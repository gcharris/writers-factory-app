"""
Consolidator Service - The "Liver" (Phase 3, Step 4)

This service bridges the SessionManager (raw chat logs) and the Knowledge Graph.
It "digests" uncommitted session events into structured graph data.

Architecture Role:
- Reads uncommitted events from sessions.db
- Extracts entities/relationships using local Llama 3.2
- Merges new data into knowledge_graph.json (with conflict detection)
- Marks events as committed after successful digestion

Key Features:
- File locking to prevent concurrent graph corruption
- Conflict detection (logs conflicts for manual review)
- Supports session-based or scene-based consolidation
"""

import os
import json
import fcntl
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager

import aiohttp

from backend.services.session_service import SessionService, get_session_service
from backend.services.foreman_kb_service import get_foreman_kb_service, ForemanKBService

# --- Logging ---
logger = logging.getLogger(__name__)

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"
GRAPH_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_graph.json")


# --- File Locking Context Manager ---
@contextmanager
def locked_file(filepath: str, mode: str = 'r+'):
    """
    Context manager for file operations with exclusive locking.
    Prevents concurrent modifications to the knowledge graph.
    """
    # Ensure file exists
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump({"metadata": {}, "nodes": [], "edges": []}, f)

    f = open(filepath, mode)
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
        yield f
    finally:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock
        f.close()


class ConsolidatorService:
    """
    The "Liver" - digests raw session events into knowledge graph data.

    Workflow:
    1. Fetch uncommitted events from SessionService
    2. Combine into context block
    3. Extract entities via Llama 3.2
    4. Merge into knowledge_graph.json (with conflict detection)
    5. Mark events as committed
    """

    def __init__(self):
        self.ollama_url = OLLAMA_URL
        self.model = OLLAMA_MODEL
        self.graph_path = GRAPH_PATH

    async def _query_ollama(self, prompt: str, system_prompt: str) -> Dict:
        """Direct call to Ollama Llama 3.2 in JSON mode."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1  # Low temperature for consistent extraction
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.ollama_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("message", {}).get("content", "{}")
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON Parse Error: {e}")
                            return {"nodes": [], "edges": []}
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama Error {response.status}: {error_text}")
                        return {"nodes": [], "edges": []}
        except asyncio.TimeoutError:
            logger.error("Ollama request timed out (120s)")
            return {"nodes": [], "edges": []}
        except aiohttp.ClientConnectorError:
            logger.error(f"Cannot connect to Ollama at {self.ollama_url}")
            return {"nodes": [], "edges": []}
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return {"nodes": [], "edges": []}

    async def _extract_from_chat(self, chat_context: str, source_label: str) -> Dict[str, Any]:
        """
        Extract entities and relationships from chat context.

        This uses a prompt optimized for conversational content
        (vs. the file-based ingestor which is for narrative text).
        """
        system_prompt = """You are an expert at extracting story elements from conversations.
Analyze this chat between a writer and their AI assistant about a story.

Extract ONLY entities and relationships that are FACTS about the story world.
Ignore meta-discussion, questions, or hypotheticals.

Return ONLY valid JSON with this exact structure:
{
  "nodes": [
    {"id": "ExactName", "type": "CHARACTER", "desc": "Short description"},
    {"id": "LocationName", "type": "LOCATION", "desc": "Short description"}
  ],
  "edges": [
    {"source": "id1", "target": "id2", "relation": "KNOWS", "desc": "context"}
  ]
}

Node types: CHARACTER, LOCATION, OBJECT, EVENT, ORGANIZATION, THEME, PLOT_POINT
Relation types: LOVES, HATES, KNOWS, LOCATED_IN, OWNS, PART_OF, CAUSES, CONFLICTS_WITH, REVEALS

Be precise. Extract only explicitly stated facts. Ignore speculation."""

        user_prompt = f"Extract story facts from this conversation:\n\n{chat_context[:6000]}"

        logger.info(f"Extracting entities from {source_label} ({len(chat_context)} chars)...")
        return await self._query_ollama(user_prompt, system_prompt)

    def _load_graph(self) -> Dict[str, Any]:
        """Load the current knowledge graph with file locking."""
        if not os.path.exists(self.graph_path):
            return {
                "metadata": {"created_at": datetime.now(timezone.utc).isoformat()},
                "nodes": [],
                "edges": []
            }

        with locked_file(self.graph_path, 'r') as f:
            return json.load(f)

    def _save_graph(self, graph: Dict[str, Any]) -> None:
        """Save the knowledge graph with file locking."""
        graph["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()

        with locked_file(self.graph_path, 'w') as f:
            json.dump(graph, f, indent=2)

    def _merge_nodes(
        self,
        existing_nodes: List[Dict],
        new_nodes: List[Dict]
    ) -> Tuple[List[Dict], int, List[Dict]]:
        """
        Merge new nodes into existing nodes.

        Returns:
            (merged_nodes, added_count, conflicts)
        """
        # Build index of existing nodes by ID
        node_index = {n.get("id"): n for n in existing_nodes}
        added = 0
        conflicts = []

        for new_node in new_nodes:
            node_id = new_node.get("id", "").strip()
            if not node_id:
                continue

            if node_id in node_index:
                # Node exists - check for conflict
                existing = node_index[node_id]
                existing_desc = existing.get("desc", "").lower()
                new_desc = new_node.get("desc", "").lower()

                # Simple conflict detection: if descriptions differ significantly
                if existing_desc and new_desc and existing_desc != new_desc:
                    # Check if they're contradictory (simple heuristic)
                    conflict_keywords = [
                        ("loves", "hates"), ("alive", "dead"), ("friend", "enemy"),
                        ("good", "evil"), ("young", "old"), ("tall", "short")
                    ]
                    is_conflict = any(
                        (k1 in existing_desc and k2 in new_desc) or
                        (k2 in existing_desc and k1 in new_desc)
                        for k1, k2 in conflict_keywords
                    )

                    if is_conflict:
                        conflicts.append({
                            "node_id": node_id,
                            "existing_desc": existing.get("desc"),
                            "new_desc": new_node.get("desc"),
                            "type": "CONTRADICTION"
                        })
                        logger.warning(f"Conflict detected for node '{node_id}'")
                        continue  # Don't update on conflict

                # Update existing node (merge descriptions if different)
                if new_desc and new_desc not in existing_desc:
                    existing["desc"] = f"{existing.get('desc', '')} | {new_node.get('desc', '')}"
            else:
                # New node - add it
                node_index[node_id] = new_node
                added += 1

        return list(node_index.values()), added, conflicts

    def _merge_edges(
        self,
        existing_edges: List[Dict],
        new_edges: List[Dict]
    ) -> Tuple[List[Dict], int]:
        """
        Merge new edges into existing edges.

        Returns:
            (merged_edges, added_count)
        """
        # Build set of existing edge signatures
        def edge_sig(e):
            return (e.get("source"), e.get("target"), e.get("relation"))

        existing_sigs = {edge_sig(e) for e in existing_edges}
        added = 0

        for new_edge in new_edges:
            sig = edge_sig(new_edge)
            if sig not in existing_sigs:
                existing_edges.append(new_edge)
                existing_sigs.add(sig)
                added += 1

        return existing_edges, added

    async def digest_session(
        self,
        session_id: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Main consolidation method - digest a session into the knowledge graph.

        Args:
            session_id: The session UUID to consolidate
            dry_run: If True, extract but don't save (for testing)

        Returns:
            Status dict with nodes_added, edges_added, conflicts, etc.
        """
        logger.info(f"Starting consolidation for session {session_id[:8]}...")

        # 1. Fetch uncommitted events
        with get_session_service() as service:
            events = service.get_uncommitted_events(session_id=session_id)

        if not events:
            logger.info("No uncommitted events found - skipping")
            return {
                "status": "skipped",
                "reason": "no_uncommitted_events",
                "session_id": session_id
            }

        event_ids = [e.id for e in events]
        logger.info(f"Found {len(events)} uncommitted events")

        # 2. Combine events into context block
        chat_context = "\n\n".join([
            f"[{e.role.upper()}]: {e.content}"
            for e in events
        ])

        # 3. Extract entities via Llama 3.2
        extracted = await self._extract_from_chat(
            chat_context,
            f"session:{session_id[:8]}"
        )

        new_nodes = extracted.get("nodes", [])
        new_edges = extracted.get("edges", [])

        logger.info(f"Extracted {len(new_nodes)} nodes, {len(new_edges)} edges")

        if not new_nodes and not new_edges:
            # Nothing extracted - still mark as committed
            if not dry_run:
                with get_session_service() as service:
                    service.mark_as_committed(event_ids)
            return {
                "status": "empty",
                "reason": "no_entities_extracted",
                "session_id": session_id,
                "events_processed": len(events)
            }

        # 4. Merge into knowledge graph
        graph = self._load_graph()

        merged_nodes, nodes_added, conflicts = self._merge_nodes(
            graph.get("nodes", []),
            new_nodes
        )
        merged_edges, edges_added = self._merge_edges(
            graph.get("edges", []),
            new_edges
        )

        graph["nodes"] = merged_nodes
        graph["edges"] = merged_edges

        # Log conflicts for manual review
        if conflicts:
            logger.warning(f"Found {len(conflicts)} conflicts - flagged for review")
            # Could store conflicts in a separate file for UI display
            conflicts_path = os.path.join(
                os.path.dirname(self.graph_path),
                "graph_conflicts.json"
            )
            existing_conflicts = []
            if os.path.exists(conflicts_path):
                with open(conflicts_path, 'r') as f:
                    existing_conflicts = json.load(f)
            existing_conflicts.extend([
                {**c, "session_id": session_id, "timestamp": datetime.now(timezone.utc).isoformat()}
                for c in conflicts
            ])
            with open(conflicts_path, 'w') as f:
                json.dump(existing_conflicts, f, indent=2)

        # 5. Save and commit
        if not dry_run:
            self._save_graph(graph)
            logger.info(f"Graph saved: {nodes_added} new nodes, {edges_added} new edges")

            with get_session_service() as service:
                service.mark_as_committed(event_ids)
            logger.info(f"Marked {len(event_ids)} events as committed")

        return {
            "status": "success",
            "session_id": session_id,
            "events_processed": len(events),
            "nodes_added": nodes_added,
            "edges_added": edges_added,
            "conflicts": len(conflicts),
            "total_nodes": len(merged_nodes),
            "total_edges": len(merged_edges),
            "dry_run": dry_run
        }

    async def digest_all_uncommitted(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Consolidate ALL uncommitted events across all sessions.

        Returns:
            Aggregate stats from all session digestions
        """
        logger.info("Starting full consolidation of all uncommitted events...")

        with get_session_service() as service:
            sessions = service.get_active_sessions(limit=100)

        total_nodes = 0
        total_edges = 0
        total_events = 0
        total_conflicts = 0
        sessions_processed = 0

        for session_info in sessions:
            session_id = session_info["session_id"]
            result = await self.digest_session(session_id, dry_run=dry_run)

            if result.get("status") == "success":
                total_nodes += result.get("nodes_added", 0)
                total_edges += result.get("edges_added", 0)
                total_events += result.get("events_processed", 0)
                total_conflicts += result.get("conflicts", 0)
                sessions_processed += 1

        return {
            "status": "success",
            "sessions_processed": sessions_processed,
            "total_events": total_events,
            "total_nodes_added": total_nodes,
            "total_edges_added": total_edges,
            "total_conflicts": total_conflicts,
            "dry_run": dry_run
        }

    # =========================================================================
    # Foreman KB Digestion (Phase 3: Living Brain Loop)
    # =========================================================================

    def _kb_category_to_node_type(self, category: str) -> str:
        """
        Map Foreman KB categories to graph node types.

        KB Categories: character, world, structure, constraint, preference
        Graph Types: CHARACTER, LOCATION, THEME, PLOT_POINT, etc.
        """
        mapping = {
            "character": "CHARACTER",
            "world": "WORLD_RULE",
            "structure": "PLOT_POINT",
            "constraint": "CONSTRAINT",
            "preference": "PREFERENCE",
        }
        return mapping.get(category, "FACT")

    def _kb_entry_to_node(self, entry) -> Dict[str, Any]:
        """
        Convert a ForemanKBEntry to a graph node.

        Unlike session digestion (which uses LLM extraction), KB entries
        are already structured - we just need to map them.
        """
        return {
            "id": entry.key,
            "type": self._kb_category_to_node_type(entry.category),
            "desc": entry.value,
            "source": entry.source or "foreman",
            "category": entry.category,
            "project_id": entry.project_id,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }

    async def digest_foreman_kb(
        self,
        project_id: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Digest unpromoted Foreman KB entries into the knowledge graph.

        This is the "Living Brain" loop described by the Gemini Architect:
        1. Foreman learns a fact → Writes to foreman_kb (SQLite)
        2. Consolidator wakes up → Reads foreman_kb → Updates knowledge_graph.json
        3. Foreman reads knowledge_graph.json for context in future chats

        Key difference from digest_session():
        - Source: foreman_kb table (crystallized decisions), not raw chat
        - Processing: Direct mapping (no LLM needed - already structured)
        - Marking: Uses is_promoted flag, not is_committed

        Args:
            project_id: The project to consolidate KB entries for
            dry_run: If True, extract but don't save (for testing)

        Returns:
            Status dict with nodes_added, entries_promoted, etc.
        """
        logger.info(f"Starting KB consolidation for project '{project_id}'...")

        # 1. Fetch unpromoted KB entries
        kb_service = get_foreman_kb_service()
        entries = kb_service.get_unpromoted_decisions(project_id)

        if not entries:
            logger.info("No unpromoted KB entries found - skipping")
            return {
                "status": "skipped",
                "reason": "no_unpromoted_entries",
                "project_id": project_id
            }

        entry_ids = [e.id for e in entries]
        logger.info(f"Found {len(entries)} unpromoted KB entries")

        # 2. Convert KB entries to graph nodes
        # (No LLM extraction needed - KB entries are already structured)
        new_nodes = [self._kb_entry_to_node(e) for e in entries]

        # 3. Create edges for character-related entries
        # Connect character facts to their protagonist
        new_edges = []
        for entry in entries:
            if entry.category == "character":
                # Create edge: Character -[HAS_TRAIT]-> Trait
                # Extract character name from key (e.g., "mickey_fatal_flaw" -> "Mickey")
                key_parts = entry.key.split("_")
                if len(key_parts) >= 2:
                    char_name = key_parts[0].title()
                    trait_type = "_".join(key_parts[1:]).upper()
                    new_edges.append({
                        "source": char_name,
                        "target": entry.key,
                        "relation": "HAS_TRAIT",
                        "desc": f"{char_name}'s {trait_type.replace('_', ' ').lower()}"
                    })

        logger.info(f"Converted to {len(new_nodes)} nodes, {len(new_edges)} edges")

        # 4. Merge into knowledge graph
        graph = self._load_graph()

        merged_nodes, nodes_added, conflicts = self._merge_nodes(
            graph.get("nodes", []),
            new_nodes
        )
        merged_edges, edges_added = self._merge_edges(
            graph.get("edges", []),
            new_edges
        )

        graph["nodes"] = merged_nodes
        graph["edges"] = merged_edges

        # Track KB source in metadata
        if "kb_consolidations" not in graph.get("metadata", {}):
            graph.setdefault("metadata", {})["kb_consolidations"] = []
        graph["metadata"]["kb_consolidations"].append({
            "project_id": project_id,
            "entries_promoted": len(entries),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # 5. Save and mark as promoted
        if not dry_run:
            self._save_graph(graph)
            logger.info(f"Graph saved: {nodes_added} new nodes, {edges_added} new edges")

            # Mark entries as promoted
            kb_service.mark_promoted(entry_ids)
            logger.info(f"Marked {len(entry_ids)} KB entries as promoted")

        return {
            "status": "success",
            "project_id": project_id,
            "entries_processed": len(entries),
            "nodes_added": nodes_added,
            "edges_added": edges_added,
            "conflicts": len(conflicts),
            "total_nodes": len(merged_nodes),
            "total_edges": len(merged_edges),
            "dry_run": dry_run
        }

    async def digest_all_foreman_kb(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Consolidate ALL unpromoted KB entries across all projects.

        Returns:
            Aggregate stats from all project digestions
        """
        logger.info("Starting full KB consolidation across all projects...")

        # Get all unique project IDs from KB
        kb_service = get_foreman_kb_service()

        # Query for distinct project IDs with unpromoted entries
        from sqlalchemy import distinct
        from backend.services.foreman_kb_service import ForemanKBEntry

        project_ids = kb_service.db.query(
            distinct(ForemanKBEntry.project_id)
        ).filter(
            ForemanKBEntry.is_promoted == False
        ).all()

        project_ids = [p[0] for p in project_ids]

        if not project_ids:
            return {
                "status": "skipped",
                "reason": "no_unpromoted_entries",
                "projects_processed": 0
            }

        total_nodes = 0
        total_edges = 0
        total_entries = 0
        total_conflicts = 0
        projects_processed = 0

        for project_id in project_ids:
            result = await self.digest_foreman_kb(project_id, dry_run=dry_run)

            if result.get("status") == "success":
                total_nodes += result.get("nodes_added", 0)
                total_edges += result.get("edges_added", 0)
                total_entries += result.get("entries_processed", 0)
                total_conflicts += result.get("conflicts", 0)
                projects_processed += 1

        return {
            "status": "success",
            "projects_processed": projects_processed,
            "total_entries": total_entries,
            "total_nodes_added": total_nodes,
            "total_edges_added": total_edges,
            "total_conflicts": total_conflicts,
            "dry_run": dry_run
        }


# --- Convenience function ---
def get_consolidator_service() -> ConsolidatorService:
    """Get a ConsolidatorService instance."""
    return ConsolidatorService()
