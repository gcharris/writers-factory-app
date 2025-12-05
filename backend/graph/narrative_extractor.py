"""
Narrative Extractor for GraphRAG.

LLM-based extraction with narrative-aware prompts.
Uses Ollama (llama3.2:3b) for intelligent extraction with
context about known entities and story structure.

Part of GraphRAG Phase 3 - Narrative Extraction.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, TYPE_CHECKING

import aiohttp

from .narrative_ontology import (
    NarrativeEdgeType,
    get_enabled_edge_types,
    parse_edge_type,
    NarrativeEdge
)
from .schema import Node, Edge

if TYPE_CHECKING:
    from .graph_service import KnowledgeGraphService

logger = logging.getLogger(__name__)


# Narrative-aware extraction prompt
NARRATIVE_EXTRACTION_PROMPT = """You are analyzing a scene from a novel to extract narrative structure.

SCENE CONTENT:
{scene_content}

EXISTING CHARACTERS: {known_characters}
EXISTING LOCATIONS: {known_locations}
CURRENT BEAT: {current_beat}

Extract the following from this scene:

1. NEW ENTITIES (only if not already known):
   - Characters introduced
   - Locations mentioned
   - Objects of significance
   - Events that occur

2. NARRATIVE RELATIONSHIPS:
   For each relationship, identify:
   - Source entity
   - Relationship type (from: {enabled_types})
   - Target entity
   - Brief description

Focus especially on:
- What MOTIVATES characters in this scene?
- What HINDERS their goals?
- Is the protagonist's fatal flaw being CHALLENGED?
- What does this scene FORESHADOW for later?
- What earlier events does it CALLBACK to?

Return as JSON:
{{
  "entities": [
    {{"id": "entity_name", "type": "CHARACTER|LOCATION|OBJECT|EVENT", "description": "..."}}
  ],
  "relationships": [
    {{"source": "...", "type": "MOTIVATES|HINDERS|...", "target": "...", "description": "..."}}
  ],
  "flaw_challenge": {{
    "challenged": true/false,
    "description": "How the flaw was challenged (if applicable)"
  }},
  "beat_alignment": {{
    "aligned": true/false,
    "expected_beat": "{current_beat}",
    "actual_function": "What this scene actually accomplishes"
  }}
}}

Be precise. Only extract what is explicitly present or strongly implied."""


class NarrativeExtractor:
    """
    Extracts narrative structure from scenes.

    Uses LLM (Ollama Llama 3.2) for intelligent extraction
    with narrative-aware prompts.
    """

    def __init__(
        self,
        graph_service: Optional['KnowledgeGraphService'] = None,
        ollama_url: str = "http://localhost:11434/api/chat",
        model: str = "llama3.2:3b"
    ):
        """
        Initialize the NarrativeExtractor.

        Args:
            graph_service: KnowledgeGraphService for accessing existing entities
            ollama_url: Ollama API endpoint
            model: Ollama model to use for extraction
        """
        self.graph = graph_service
        self.ollama_url = ollama_url
        self.model = model
        logger.info(f"NarrativeExtractor initialized (model={model})")

    async def _query_ollama(self, prompt: str) -> str:
        """Query Ollama for extraction."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.1}  # Low temp for consistent extraction
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
                        return result.get("message", {}).get("content", "{}")
                    else:
                        logger.error(f"Ollama error: {response.status}")
                        return "{}"
        except aiohttp.ClientConnectorError:
            logger.error(f"Cannot connect to Ollama at {self.ollama_url}")
            return "{}"
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            return "{}"

    def _get_known_entities(self, entity_type: str) -> List[str]:
        """Get known entities of a type from the graph."""
        if not self.graph:
            return []

        try:
            nodes = self.graph.get_nodes_by_type(entity_type)
            return [n.name for n in nodes] if nodes else []
        except Exception as e:
            logger.debug(f"Could not fetch {entity_type} entities: {e}")
            return []

    async def extract_from_scene(
        self,
        scene_content: str,
        scene_id: str,
        current_beat: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Extract narrative elements from a scene.

        Args:
            scene_content: The scene text
            scene_id: Identifier for the scene
            current_beat: Expected beat alignment (e.g., "Midpoint")

        Returns:
            Structured extraction result with entities, relationships, and metadata
        """
        # Gather existing context
        known_characters = self._get_known_entities("CHARACTER")
        known_locations = self._get_known_entities("LOCATION")
        enabled_types = [t.value for t in get_enabled_edge_types()]

        prompt = NARRATIVE_EXTRACTION_PROMPT.format(
            scene_content=scene_content[:6000],  # Truncate for context window
            known_characters=", ".join(known_characters) or "None yet",
            known_locations=", ".join(known_locations) or "None yet",
            current_beat=current_beat,
            enabled_types=", ".join(enabled_types)
        )

        logger.info(f"Extracting narrative from scene '{scene_id}'...")
        response = await self._query_ollama(prompt)

        try:
            result = json.loads(response)
            result["scene_id"] = scene_id
            result["extracted_at"] = datetime.now(timezone.utc).isoformat()
            logger.info(
                f"Extracted {len(result.get('entities', []))} entities, "
                f"{len(result.get('relationships', []))} relationships"
            )
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction result: {e}")
            logger.debug(f"Raw response: {response[:500]}")
            return {
                "error": "Extraction failed",
                "raw": response[:500],
                "scene_id": scene_id
            }

    async def merge_to_graph(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge extraction results into the knowledge graph.

        Args:
            extraction: Result from extract_from_scene()

        Returns:
            Merge statistics (nodes_created, edges_created, conflicts)
        """
        if not self.graph:
            return {"error": "No graph service configured"}

        stats = {
            "nodes_created": 0,
            "edges_created": 0,
            "conflicts": [],
            "flaw_challenged": False
        }

        scene_id = extraction.get("scene_id", "unknown")

        # Track flaw challenge
        flaw_info = extraction.get("flaw_challenge", {})
        if flaw_info.get("challenged"):
            stats["flaw_challenged"] = True
            stats["flaw_challenge_description"] = flaw_info.get("description", "")

        # Create new entities
        for entity in extraction.get("entities", []):
            entity_id = entity.get("id", "").strip()
            if not entity_id:
                continue

            existing = self.graph.find_node_by_name(entity_id)
            if not existing:
                try:
                    node = Node(
                        name=entity_id,
                        node_type=entity.get("type", "UNKNOWN").upper(),
                        description=entity.get("description"),
                        content=f"Introduced in scene: {scene_id}"
                    )
                    self.graph.add_node(node)
                    stats["nodes_created"] += 1
                    logger.debug(f"Created node: {entity_id}")
                except Exception as e:
                    logger.error(f"Failed to create node {entity_id}: {e}")

        # Create relationships
        for rel in extraction.get("relationships", []):
            rel_type_str = rel.get("type", "CUSTOM")
            edge_type = parse_edge_type(rel_type_str)

            # Flag contradictions for review instead of adding
            if edge_type == NarrativeEdgeType.CONTRADICTS:
                stats["conflicts"].append({
                    "type": "CONTRADICTION",
                    "source": rel.get("source"),
                    "target": rel.get("target"),
                    "description": rel.get("description"),
                    "scene_id": scene_id
                })
                logger.warning(f"Flagged contradiction: {rel.get('source')} <-> {rel.get('target')}")
                continue

            source_node = self.graph.find_node_by_name(rel.get("source", ""))
            target_node = self.graph.find_node_by_name(rel.get("target", ""))

            if source_node and target_node:
                try:
                    edge = Edge(
                        source_id=source_node.id,
                        target_id=target_node.id,
                        relation_type=edge_type.value
                    )
                    result = self.graph.add_edge(edge)
                    if result:
                        stats["edges_created"] += 1
                        logger.debug(f"Created edge: {rel.get('source')} -[{edge_type.value}]-> {rel.get('target')}")
                except Exception as e:
                    logger.error(f"Failed to create edge: {e}")
            else:
                logger.debug(
                    f"Skipped edge (missing nodes): {rel.get('source')} -> {rel.get('target')}"
                )

        logger.info(
            f"Merge complete: {stats['nodes_created']} nodes, "
            f"{stats['edges_created']} edges, {len(stats['conflicts'])} conflicts"
        )
        return stats

    async def extract_and_merge(
        self,
        scene_content: str,
        scene_id: str,
        current_beat: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Convenience method: extract and merge in one call.

        Args:
            scene_content: The scene text
            scene_id: Identifier for the scene
            current_beat: Expected beat alignment

        Returns:
            Combined extraction and merge results
        """
        extraction = await self.extract_from_scene(scene_content, scene_id, current_beat)

        if extraction.get("error"):
            return extraction

        merge_stats = await self.merge_to_graph(extraction)

        return {
            "status": "success",
            "scene_id": scene_id,
            "extraction": extraction,
            "merge_stats": merge_stats
        }


# Factory function for singleton-style access
_extractor_instance: Optional[NarrativeExtractor] = None


def get_narrative_extractor(
    graph_service: Optional['KnowledgeGraphService'] = None
) -> NarrativeExtractor:
    """
    Get or create a NarrativeExtractor instance.

    Args:
        graph_service: Optional KnowledgeGraphService to use

    Returns:
        NarrativeExtractor instance
    """
    global _extractor_instance

    if _extractor_instance is None or graph_service is not None:
        _extractor_instance = NarrativeExtractor(graph_service)

    return _extractor_instance


def reset_narrative_extractor():
    """Reset the singleton instance (useful for testing)."""
    global _extractor_instance
    _extractor_instance = None
