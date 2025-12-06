"""
Workspace Service - File-based research management

Manages the workspace/research/ directory structure with 5 Core categories
aligned with the Distillation Pipeline.

Phase 1 of WORKSPACE_FILE_SYSTEM.md
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import re

# The 5 Core Categories (matching 5 Core Notebooks)
VALID_RESEARCH_CATEGORIES = ["characters", "world", "theme", "plot", "voice"]

# Category descriptions for UI
CATEGORY_DESCRIPTIONS = {
    "characters": "Characters (Fatal Flaw, Arc, Cast)",
    "world": "World (Hard Rules, Locations)",
    "theme": "Theme (Central Question, Symbols)",
    "plot": "Plot (15 Beats, Structure)",
    "voice": "Voice (Style Targets, Anti-patterns)",
}

# Category icons for File Tree
CATEGORY_ICONS = {
    "characters": "👤",
    "world": "🌍",
    "theme": "💭",
    "plot": "📊",
    "voice": "✍️",
}


class WorkspaceService:
    """
    Manages file-based research storage with 5 Core categories.

    Directory structure:
        workspace/
        └── research/
            ├── characters/
            ├── world/
            ├── theme/
            ├── plot/
            └── voice/
    """

    def __init__(self, workspace_root: str = None):
        """
        Initialize WorkspaceService.

        Args:
            workspace_root: Base path for workspace. Defaults to current working directory.
        """
        if workspace_root is None:
            workspace_root = os.getcwd()
        self.workspace_root = Path(workspace_root)
        self.research_path = self.workspace_root / "workspace" / "research"

    def ensure_research_directories(self) -> List[Path]:
        """
        Create the 5 Core research directories if they don't exist.

        Returns:
            List of created directory paths
        """
        created = []
        for category in VALID_RESEARCH_CATEGORIES:
            category_path = self.research_path / category
            if not category_path.exists():
                category_path.mkdir(parents=True, exist_ok=True)
                created.append(category_path)
        return created

    def validate_category(self, category: str) -> bool:
        """
        Check if category is one of the 5 valid categories.

        Args:
            category: Category to validate

        Returns:
            True if valid, False otherwise
        """
        return category.lower() in VALID_RESEARCH_CATEGORIES

    def get_category_error_message(self, invalid_category: str) -> str:
        """
        Generate a helpful error message for invalid categories.

        Args:
            invalid_category: The invalid category that was provided

        Returns:
            Helpful error message with suggestions
        """
        suggestions = {
            "misc": "Choose the most relevant category: characters, world, theme, plot, or voice",
            "other": "Choose the most relevant category: characters, world, theme, plot, or voice",
            "craft": "Use 'voice' for style and craft references",
            "style": "Use 'voice' for style and craft references",
            "setting": "Use 'world' for locations and settings",
            "locations": "Use 'world' for locations and settings",
            "structure": "Use 'plot' for story structure and beats",
            "beats": "Use 'plot' for story structure and beats",
            "protagonist": "Use 'characters' for protagonist and all characters",
            "antagonist": "Use 'characters' for antagonist and all characters",
            "philosophy": "Use 'theme' for philosophical and thematic content",
        }

        suggestion = suggestions.get(invalid_category.lower(), "")
        base_msg = f"Invalid category '{invalid_category}'. Must be one of: {', '.join(VALID_RESEARCH_CATEGORIES)}"

        if suggestion:
            return f"{base_msg}. {suggestion}"
        return base_msg

    def sanitize_filename(self, key: str) -> str:
        """
        Convert a key into a safe filename.

        Args:
            key: The key/name to sanitize

        Returns:
            Safe filename (without extension)
        """
        # Replace spaces with underscores
        safe = key.replace(" ", "_")
        # Remove or replace invalid characters
        safe = re.sub(r'[<>:"/\\|?*]', '', safe)
        # Remove leading/trailing whitespace and dots
        safe = safe.strip(". ")
        # Ensure not empty
        if not safe:
            safe = "unnamed"
        # Limit length
        if len(safe) > 100:
            safe = safe[:100]
        return safe.lower()

    def save_research_note(
        self,
        category: str,
        key: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Save a research note as a markdown file.

        Args:
            category: One of the 5 valid categories
            key: Name/key for the file
            content: The extracted content
            metadata: Optional metadata (notebook_name, notebook_id, etc.)

        Returns:
            Dict with success status and file_path

        Raises:
            ValueError: If category is invalid
        """
        # Validate category
        category = category.lower()
        if not self.validate_category(category):
            raise ValueError(self.get_category_error_message(category))

        # Ensure directories exist
        self.ensure_research_directories()

        # Sanitize filename
        filename = self.sanitize_filename(key)
        file_path = self.research_path / category / f"{filename}.md"

        # Build metadata dict
        if metadata is None:
            metadata = {}

        # Build YAML frontmatter
        now = datetime.now(timezone.utc).isoformat()
        frontmatter_lines = [
            "---",
            "source: NotebookLM",
            f'notebook_name: "{metadata.get("notebook_name", "")}"',
            f"notebook_id: {metadata.get('notebook_id', '')}",
            f"extracted: {metadata.get('extracted', now)}",
            f"category: {category}",
            f"key: {key}",
            "status: draft",
            "stage: 2  # Stage 2 = Distilled from Core Notebook",
            "---",
            "",
        ]

        # Build file content
        title = key.replace("_", " ").title()
        file_content = "\n".join(frontmatter_lines)
        file_content += f"# {title}\n\n"
        file_content += content.strip()
        file_content += "\n\n---\n## User Notes\n\n[Add your annotations here]\n"

        # Write file
        file_path.write_text(file_content, encoding="utf-8")

        return {
            "success": True,
            "file_path": str(file_path.relative_to(self.workspace_root)),
            "absolute_path": str(file_path),
            "category": category,
            "key": key,
        }

    def list_research_files(self) -> Dict[str, List[str]]:
        """
        List all research files organized by category.

        Returns:
            Dict mapping category to list of filenames
        """
        result = {}
        for category in VALID_RESEARCH_CATEGORIES:
            category_path = self.research_path / category
            if category_path.exists():
                files = [f.name for f in category_path.glob("*.md")]
                result[category] = sorted(files)
            else:
                result[category] = []
        return result

    def read_research_file(self, category: str, filename: str) -> Dict:
        """
        Read a research file's content and metadata.

        Args:
            category: The category folder
            filename: The filename (with or without .md)

        Returns:
            Dict with content and metadata
        """
        category = category.lower()
        if not self.validate_category(category):
            raise ValueError(self.get_category_error_message(category))

        # Ensure .md extension
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        file_path = self.research_path / category / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Research file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")

        # Parse frontmatter if present
        metadata = {}
        body = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                # Parse YAML frontmatter
                frontmatter = parts[1].strip()
                body = parts[2].strip()

                for line in frontmatter.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        metadata[key] = value

        return {
            "content": body,
            "metadata": metadata,
            "file_path": str(file_path.relative_to(self.workspace_root)),
        }

    def get_categories(self) -> List[Dict]:
        """
        Get list of categories with descriptions and icons.

        Returns:
            List of category info dicts
        """
        return [
            {
                "id": cat,
                "name": CATEGORY_DESCRIPTIONS[cat],
                "icon": CATEGORY_ICONS[cat],
            }
            for cat in VALID_RESEARCH_CATEGORIES
        ]


# Singleton instance
_workspace_service: Optional[WorkspaceService] = None


def get_workspace_service(workspace_root: str = None) -> WorkspaceService:
    """
    Get the workspace service singleton.

    Args:
        workspace_root: Optional workspace root path

    Returns:
        WorkspaceService instance
    """
    global _workspace_service
    if _workspace_service is None or workspace_root is not None:
        _workspace_service = WorkspaceService(workspace_root)
    return _workspace_service
