"""
Foreman Knowledge Base Service - Persistent Decision Storage

This service manages the Foreman's Knowledge Base - crystallized decisions
from creative conversations that persist across sessions.

Architecture Role (per Gemini Architect Review):
- SQLite for immediate writes (survives crashes)
- Consolidator later promotes "hard facts" to knowledge_graph.json
- Keeps the graph clean by separating "soft" decisions from "hard" facts

Flow:
1. Foreman learns a fact -> Writes to foreman_kb (SQLite)
2. Consolidator wakes up -> Reads foreman_kb -> Updates knowledge_graph.json
3. Foreman reads knowledge_graph.json for context in future chats
"""

import os
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- Logging ---
logger = logging.getLogger(__name__)

# --- Database Setup ---
# Use the same sessions.db as SessionService (per Gemini's recommendation)
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)
KB_DB_PATH = os.path.join(WORKSPACE_DIR, "sessions.db")
KB_DB_URL = f"sqlite:///{KB_DB_PATH}"

# SQLAlchemy setup
engine = create_engine(KB_DB_URL, echo=False)
KBSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Models ---
class ForemanKBEntry(Base):
    """
    A crystallized decision from a Foreman conversation.

    This is NOT raw conversation - it's the extracted decision/fact
    that emerged from conversation and should persist.

    Categories:
    - character: Character traits, flaws, arcs
    - world: World-building rules, settings
    - structure: Beat sheet decisions, plot points
    - constraint: Creative constraints agreed upon
    - preference: Writer preferences (soft facts)
    """
    __tablename__ = "foreman_kb"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(255), nullable=False, index=True)  # Links to project
    category = Column(String(50), nullable=False, index=True)  # character, world, structure, etc.
    key = Column(String(255), nullable=False)  # e.g., "mickey_fatal_flaw"
    value = Column(Text, nullable=False)  # The actual decision/fact
    source = Column(String(255), nullable=True)  # Where this came from
    is_promoted = Column(Boolean, default=False, index=True)  # Promoted to graph?
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_project_category', 'project_id', 'category'),
        Index('idx_project_promoted', 'project_id', 'is_promoted'),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "category": self.category,
            "key": self.key,
            "value": self.value,
            "source": self.source,
            "is_promoted": self.is_promoted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Create tables
Base.metadata.create_all(bind=engine)
logger.info(f"Foreman KB table initialized in: {KB_DB_PATH}")


# --- Service Class ---
class ForemanKBService:
    """
    Manages the Foreman's Knowledge Base.

    This service provides:
    - Immediate persistence of decisions from Foreman conversations
    - Retrieval of decisions for context injection
    - Tracking of which entries have been promoted to the graph
    """

    def __init__(self):
        self.db: Session = KBSessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the database session."""
        if self.db:
            self.db.close()

    def save_decision(
        self,
        project_id: str,
        category: str,
        key: str,
        value: str,
        source: Optional[str] = None
    ) -> ForemanKBEntry:
        """
        Save a decision to the KB immediately.

        If a decision with the same project_id + key exists, update it.
        Otherwise, create a new entry.

        Args:
            project_id: The project this decision belongs to
            category: character, world, structure, constraint, preference
            key: Unique identifier for this decision (e.g., "mickey_fatal_flaw")
            value: The actual decision content
            source: Optional source attribution

        Returns:
            The created or updated ForemanKBEntry
        """
        # Check if entry exists
        existing = self.db.query(ForemanKBEntry).filter(
            ForemanKBEntry.project_id == project_id,
            ForemanKBEntry.key == key
        ).first()

        if existing:
            # Update existing entry
            existing.category = category
            existing.value = value
            existing.source = source
            existing.updated_at = datetime.now(timezone.utc)
            existing.is_promoted = False  # Reset promotion status on update
            self.db.commit()
            logger.info(f"Updated KB entry: {project_id}/{key}")
            return existing
        else:
            # Create new entry
            entry = ForemanKBEntry(
                project_id=project_id,
                category=category,
                key=key,
                value=value,
                source=source
            )
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
            logger.info(f"Created KB entry: {project_id}/{key}")
            return entry

    def get_decisions(
        self,
        project_id: str,
        category: Optional[str] = None,
        include_promoted: bool = True
    ) -> List[ForemanKBEntry]:
        """
        Get decisions for a project.

        Args:
            project_id: The project to get decisions for
            category: Optional filter by category
            include_promoted: Whether to include already-promoted entries

        Returns:
            List of ForemanKBEntry objects
        """
        query = self.db.query(ForemanKBEntry).filter(
            ForemanKBEntry.project_id == project_id
        )

        if category:
            query = query.filter(ForemanKBEntry.category == category)

        if not include_promoted:
            query = query.filter(ForemanKBEntry.is_promoted == False)

        return query.order_by(ForemanKBEntry.created_at.desc()).all()

    def get_unpromoted_decisions(self, project_id: str) -> List[ForemanKBEntry]:
        """Get decisions that haven't been promoted to the graph yet."""
        return self.get_decisions(project_id, include_promoted=False)

    def mark_promoted(self, entry_ids: List[int]) -> int:
        """
        Mark entries as promoted to the knowledge graph.

        Called by the Consolidator after successfully adding to graph.

        Returns:
            Number of entries marked
        """
        count = self.db.query(ForemanKBEntry).filter(
            ForemanKBEntry.id.in_(entry_ids)
        ).update(
            {"is_promoted": True},
            synchronize_session=False
        )
        self.db.commit()
        logger.info(f"Marked {count} KB entries as promoted")
        return count

    def get_context_for_foreman(self, project_id: str, limit: int = 30) -> str:
        """
        Get a formatted context string for the Foreman's prompt.

        Uses category-aware fetching to ensure foundational decisions
        are never pushed out of context by recent activity:

        - ALWAYS include ALL 'character' and 'constraint' decisions
          (Fatal Flaw, The Lie, hard rules - these are foundational)
        - Fill remaining slots with recent 'world', 'structure', 'preference'
          decisions (these evolve more frequently)

        This ensures the Foreman never "forgets" Day 1 character decisions
        even after 100+ scene-specific decisions in later chapters.
        """
        # Foundational categories - ALWAYS include all of these
        foundational_categories = ['character', 'constraint']

        # Volatile categories - include recent entries
        volatile_categories = ['world', 'structure', 'preference']

        # 1. Get ALL foundational decisions (no limit)
        foundational_entries = []
        for category in foundational_categories:
            entries = self.db.query(ForemanKBEntry).filter(
                ForemanKBEntry.project_id == project_id,
                ForemanKBEntry.category == category
            ).order_by(ForemanKBEntry.created_at.asc()).all()  # Oldest first for foundations
            foundational_entries.extend(entries)

        # 2. Calculate remaining slots for volatile decisions
        remaining_slots = max(0, limit - len(foundational_entries))

        # 3. Get recent volatile decisions
        volatile_entries = []
        if remaining_slots > 0:
            volatile_entries = self.db.query(ForemanKBEntry).filter(
                ForemanKBEntry.project_id == project_id,
                ForemanKBEntry.category.in_(volatile_categories)
            ).order_by(ForemanKBEntry.created_at.desc()).limit(remaining_slots).all()

        # 4. Combine: foundations first, then recent volatile
        all_entries = foundational_entries + volatile_entries

        if not all_entries:
            return ""

        # 5. Format for context injection
        lines = ["## Known Decisions & Facts"]

        # Group by category for readability
        if foundational_entries:
            lines.append("\n### Foundational (Always Active)")
            for entry in foundational_entries:
                lines.append(f"- [{entry.category}] {entry.key}: {entry.value}")

        if volatile_entries:
            lines.append("\n### Recent Decisions")
            for entry in volatile_entries:
                lines.append(f"- [{entry.category}] {entry.key}: {entry.value}")

        return "\n".join(lines)

    def delete_project_kb(self, project_id: str) -> int:
        """
        Delete all KB entries for a project.

        Called when resetting the Foreman for a new project.

        Returns:
            Number of entries deleted
        """
        count = self.db.query(ForemanKBEntry).filter(
            ForemanKBEntry.project_id == project_id
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} KB entries for project: {project_id}")
        return count

    def get_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics about the KB for a project."""
        total = self.db.query(ForemanKBEntry).filter(
            ForemanKBEntry.project_id == project_id
        ).count()

        promoted = self.db.query(ForemanKBEntry).filter(
            ForemanKBEntry.project_id == project_id,
            ForemanKBEntry.is_promoted == True
        ).count()

        by_category = {}
        for category in ['character', 'world', 'structure', 'constraint', 'preference']:
            by_category[category] = self.db.query(ForemanKBEntry).filter(
                ForemanKBEntry.project_id == project_id,
                ForemanKBEntry.category == category
            ).count()

        return {
            "project_id": project_id,
            "total_entries": total,
            "promoted": promoted,
            "pending": total - promoted,
            "by_category": by_category
        }


# --- Singleton Instance ---
_kb_service: Optional[ForemanKBService] = None

def get_foreman_kb_service() -> ForemanKBService:
    """Get or create the singleton ForemanKBService instance."""
    global _kb_service
    if _kb_service is None:
        _kb_service = ForemanKBService()
    return _kb_service
