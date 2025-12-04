"""
Manuscript Service for Working → Manuscript Workflow.

Manages the two-stage file workflow:
1. Working/ - Active drafts, editable, not yet canonical
2. Manuscript/ - Canonical scenes, triggers graph extraction

Part of GraphRAG Phase 1 - Foundation.
"""

import os
import json
import shutil
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class WorkingFileMeta:
    """Metadata for a file in the Working directory."""
    filename: str
    created_at: str
    modified_at: str
    word_count: int
    promoted: bool = False
    promoted_to: Optional[str] = None
    promoted_at: Optional[str] = None


@dataclass
class ManuscriptFileMeta:
    """Metadata for a file in the Manuscript directory."""
    path: str
    source_file: str
    promoted_at: str
    extracted: bool = False
    extracted_at: Optional[str] = None
    word_count: int = 0


class ManuscriptService:
    """
    Manages the Working → Manuscript file workflow.

    Working/ contains active drafts that the writer edits freely.
    Manuscript/ contains canonical scenes that are indexed in the knowledge graph.

    When a file is "promoted" from Working to Manuscript:
    1. File is copied (not moved) to Manuscript with organized structure
    2. Graph extraction is triggered to index the content
    3. Metadata is updated in both directories
    """

    def __init__(self, content_root: Optional[str] = None):
        """
        Initialize the ManuscriptService.

        Args:
            content_root: Root directory for content. Defaults to project's content/ folder.
        """
        if content_root:
            self.content_root = content_root
        else:
            # Go up from backend/services/ to project root, then to content/
            self.content_root = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "content"
            )

        self.working_dir = os.path.join(self.content_root, "Working")
        self.manuscript_dir = os.path.join(self.content_root, "Manuscript")
        self.working_meta_path = os.path.join(self.working_dir, ".working_meta.json")
        self.manuscript_meta_path = os.path.join(self.manuscript_dir, ".manuscript_meta.json")

        # Ensure directories exist
        self._ensure_directories()

        logger.info(f"ManuscriptService initialized: {self.content_root}")

    def _ensure_directories(self) -> None:
        """Create Working/ and Manuscript/ directories if they don't exist."""
        os.makedirs(self.working_dir, exist_ok=True)
        os.makedirs(self.manuscript_dir, exist_ok=True)

        # Initialize metadata files if they don't exist
        if not os.path.exists(self.working_meta_path):
            self._save_working_meta({})
        if not os.path.exists(self.manuscript_meta_path):
            self._save_manuscript_meta({})

    def _load_working_meta(self) -> Dict[str, Any]:
        """Load working directory metadata."""
        try:
            with open(self.working_meta_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_working_meta(self, meta: Dict[str, Any]) -> None:
        """Save working directory metadata."""
        with open(self.working_meta_path, 'w') as f:
            json.dump(meta, f, indent=2)

    def _load_manuscript_meta(self) -> Dict[str, Any]:
        """Load manuscript directory metadata."""
        try:
            with open(self.manuscript_meta_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_manuscript_meta(self, meta: Dict[str, Any]) -> None:
        """Save manuscript directory metadata."""
        with open(self.manuscript_meta_path, 'w') as f:
            json.dump(meta, f, indent=2)

    def _count_words(self, filepath: str) -> int:
        """Count words in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                return len(content.split())
        except Exception:
            return 0

    def get_working_files(self) -> List[Dict[str, Any]]:
        """
        List all files in Working/ directory with metadata.

        Returns:
            List of file info dicts with name, metadata, and status
        """
        if not os.path.exists(self.working_dir):
            return []

        meta = self._load_working_meta()
        files = []

        for filename in os.listdir(self.working_dir):
            # Skip hidden files and metadata
            if filename.startswith('.'):
                continue

            filepath = os.path.join(self.working_dir, filename)
            if not os.path.isfile(filepath):
                continue

            # Get file stats
            stat = os.stat(filepath)
            modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            created_at = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat()

            # Merge with stored metadata
            stored_meta = meta.get(filename, {})

            files.append({
                "filename": filename,
                "path": filepath,
                "created_at": stored_meta.get("created_at", created_at),
                "modified_at": modified_at,
                "word_count": self._count_words(filepath),
                "promoted": stored_meta.get("promoted", False),
                "promoted_to": stored_meta.get("promoted_to"),
                "promoted_at": stored_meta.get("promoted_at"),
            })

        # Sort by modification time, newest first
        files.sort(key=lambda x: x["modified_at"], reverse=True)
        return files

    def get_manuscript_structure(self) -> Dict[str, Any]:
        """
        Get hierarchical manuscript structure for file tree display.

        Returns:
            Nested dict representing directory structure:
            {
                "name": "Manuscript",
                "type": "directory",
                "children": [
                    {
                        "name": "Act_1",
                        "type": "directory",
                        "children": [...]
                    },
                    ...
                ]
            }
        """
        def build_tree(path: str, name: str) -> Dict[str, Any]:
            """Recursively build directory tree."""
            node = {
                "name": name,
                "path": path,
            }

            if os.path.isdir(path):
                node["type"] = "directory"
                children = []

                try:
                    for item in sorted(os.listdir(path)):
                        # Skip hidden files
                        if item.startswith('.'):
                            continue

                        item_path = os.path.join(path, item)
                        children.append(build_tree(item_path, item))
                except PermissionError:
                    pass

                node["children"] = children
            else:
                node["type"] = "file"
                node["word_count"] = self._count_words(path)

                # Add extraction status from metadata
                meta = self._load_manuscript_meta()
                rel_path = os.path.relpath(path, self.manuscript_dir)
                file_meta = meta.get(rel_path, {})
                node["extracted"] = file_meta.get("extracted", False)
                node["extracted_at"] = file_meta.get("extracted_at")

            return node

        if not os.path.exists(self.manuscript_dir):
            return {"name": "Manuscript", "type": "directory", "children": [], "path": self.manuscript_dir}

        return build_tree(self.manuscript_dir, "Manuscript")

    async def promote_to_manuscript(
        self,
        working_file: str,
        target_path: str,
        trigger_extraction: bool = True
    ) -> Dict[str, Any]:
        """
        Promote a working file to the manuscript.

        Args:
            working_file: Filename in Working/ directory (e.g., "Chapter_04_Scene_02.md")
            target_path: Target path within Manuscript/ (e.g., "Act_2/Chapter_04/Scene_02.md")
            trigger_extraction: Whether to trigger graph extraction after promotion

        Returns:
            Result dict with status and metadata
        """
        source_path = os.path.join(self.working_dir, working_file)

        # Validate source exists
        if not os.path.exists(source_path):
            return {
                "status": "error",
                "error": f"Working file not found: {working_file}",
            }

        # Build target path
        full_target_path = os.path.join(self.manuscript_dir, target_path)
        target_dir = os.path.dirname(full_target_path)

        # Create target directory structure
        os.makedirs(target_dir, exist_ok=True)

        # Copy file (preserve working copy)
        now = datetime.now(timezone.utc).isoformat()
        try:
            shutil.copy2(source_path, full_target_path)
            logger.info(f"Promoted {working_file} -> {target_path}")
        except Exception as e:
            logger.error(f"Failed to copy file: {e}")
            return {
                "status": "error",
                "error": f"Failed to copy file: {str(e)}",
            }

        # Update working metadata
        working_meta = self._load_working_meta()
        working_meta[working_file] = {
            "promoted": True,
            "promoted_to": target_path,
            "promoted_at": now,
        }
        self._save_working_meta(working_meta)

        # Update manuscript metadata
        manuscript_meta = self._load_manuscript_meta()
        manuscript_meta[target_path] = {
            "source_file": working_file,
            "promoted_at": now,
            "extracted": False,
            "word_count": self._count_words(full_target_path),
        }
        self._save_manuscript_meta(manuscript_meta)

        # Trigger graph extraction
        extraction_result = None
        if trigger_extraction:
            try:
                extraction_result = await self._trigger_extraction(full_target_path)

                # Update extraction status
                if extraction_result.get("status") == "success":
                    manuscript_meta[target_path]["extracted"] = True
                    manuscript_meta[target_path]["extracted_at"] = datetime.now(timezone.utc).isoformat()
                    manuscript_meta[target_path]["nodes_extracted"] = extraction_result.get("nodes_extracted", 0)
                    manuscript_meta[target_path]["edges_extracted"] = extraction_result.get("edges_extracted", 0)
                    self._save_manuscript_meta(manuscript_meta)

            except Exception as e:
                logger.error(f"Extraction failed (file still promoted): {e}")
                extraction_result = {"status": "error", "error": str(e)}

        return {
            "status": "success",
            "source": working_file,
            "target": target_path,
            "promoted_at": now,
            "word_count": self._count_words(full_target_path),
            "extraction": extraction_result,
        }

    async def _trigger_extraction(self, filepath: str) -> Dict[str, Any]:
        """
        Trigger graph extraction for a single file.

        Uses the GraphIngestor to extract entities from the promoted file.
        """
        try:
            # Import here to avoid circular imports
            from backend.ingestor import GraphIngestor

            # Read file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                return {
                    "status": "skipped",
                    "reason": "empty_file",
                }

            # Create ingestor and extract from this single file
            ingestor = GraphIngestor()
            filename = os.path.basename(filepath)

            # Extract entities from the text
            extracted = await ingestor.extract_graph_from_text(content, filename)

            nodes = extracted.get("nodes", [])
            edges = extracted.get("edges", [])

            if not nodes and not edges:
                return {
                    "status": "success",
                    "nodes_extracted": 0,
                    "edges_extracted": 0,
                    "message": "No entities found in file",
                }

            # Merge into the knowledge graph
            # Load existing graph
            graph_path = ingestor.output_path
            if os.path.exists(graph_path):
                with open(graph_path, 'r') as f:
                    graph = json.load(f)
            else:
                graph = {"metadata": {}, "nodes": [], "edges": []}

            # Merge nodes (by ID)
            existing_ids = {n.get("id") for n in graph.get("nodes", [])}
            new_nodes = [n for n in nodes if n.get("id") not in existing_ids]
            graph["nodes"] = graph.get("nodes", []) + new_nodes

            # Merge edges (by source-target-relation)
            def edge_key(e):
                return (e.get("source"), e.get("target"), e.get("relation"))

            existing_edges = {edge_key(e) for e in graph.get("edges", [])}
            new_edges = [e for e in edges if edge_key(e) not in existing_edges]
            graph["edges"] = graph.get("edges", []) + new_edges

            # Update metadata
            graph["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
            graph["metadata"]["last_extraction_source"] = filepath

            # Save
            with open(graph_path, 'w') as f:
                json.dump(graph, f, indent=2)

            logger.info(f"Extracted {len(new_nodes)} nodes, {len(new_edges)} edges from {filename}")

            return {
                "status": "success",
                "nodes_extracted": len(new_nodes),
                "edges_extracted": len(new_edges),
                "total_nodes": len(graph["nodes"]),
                "total_edges": len(graph["edges"]),
            }

        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    def get_promotion_status(self, working_file: str) -> Optional[Dict[str, Any]]:
        """
        Check if a working file has been promoted.

        Args:
            working_file: Filename to check

        Returns:
            Promotion metadata if promoted, None otherwise
        """
        meta = self._load_working_meta()
        return meta.get(working_file)

    def get_extraction_status(self, manuscript_path: str) -> Optional[Dict[str, Any]]:
        """
        Check extraction status for a manuscript file.

        Args:
            manuscript_path: Path relative to Manuscript/ directory

        Returns:
            Extraction metadata if exists, None otherwise
        """
        meta = self._load_manuscript_meta()
        return meta.get(manuscript_path)


# Singleton instance
_manuscript_service: Optional[ManuscriptService] = None


def get_manuscript_service(content_root: Optional[str] = None) -> ManuscriptService:
    """
    Get or create the singleton ManuscriptService instance.

    Args:
        content_root: Optional content root override

    Returns:
        ManuscriptService instance
    """
    global _manuscript_service

    if _manuscript_service is None:
        _manuscript_service = ManuscriptService(content_root)

    return _manuscript_service


def reset_manuscript_service() -> None:
    """Reset the singleton instance (useful for testing)."""
    global _manuscript_service
    _manuscript_service = None
