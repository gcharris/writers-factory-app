"""
Session Manager Service - The "Workbench" (Phase 3, Step 1)

This service manages persistent chat sessions. It stores conversation history
that will later be "digested" by the Consolidator into the Knowledge Graph.

Architecture Role:
- This is the "Mouth & Stomach" of the Metabolism system
- Events are logged here first, then marked as "committed" once digested
- Supports future compaction (summarization of old turns)
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- Logging ---
logger = logging.getLogger(__name__)

# --- Database Setup ---
# Use a separate database for sessions (keeps Workbench isolated from graph.db)
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)
SESSION_DB_PATH = os.path.join(WORKSPACE_DIR, "sessions.db")
SESSION_DB_URL = f"sqlite:///{SESSION_DB_PATH}"

# SQLAlchemy setup
engine = create_engine(SESSION_DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Models ---
class SessionEvent(Base):
    """
    A single event (message) in a chat session.

    The session_id groups related messages together.
    The scene_id optionally links a session to a specific scene file.
    The is_committed flag tracks whether this event has been "digested"
    by the Consolidator into the Knowledge Graph.
    """
    __tablename__ = "session_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), nullable=False, index=True)
    scene_id = Column(String(255), nullable=True, index=True)  # Links to scene file
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)  # Approximate, for compaction logic
    is_committed = Column(Boolean, default=False, index=True)  # Digested by graph?
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_session_committed', 'session_id', 'is_committed'),
        Index('idx_scene_committed', 'scene_id', 'is_committed'),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "scene_id": self.scene_id,
            "role": self.role,
            "content": self.content,
            "token_count": self.token_count,
            "is_committed": self.is_committed,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


# Create tables
Base.metadata.create_all(bind=engine)
logger.info(f"Session database initialized at: {SESSION_DB_PATH}")


# --- Service Class ---
class SessionService:
    """
    Manages chat sessions (the "Workbench").

    This service provides:
    - Session creation and event logging
    - History retrieval for UI display
    - Uncommitted event queries for the Consolidator
    - Commit marking after digestion
    """

    def __init__(self):
        self.db: Session = SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the database session."""
        if self.db:
            self.db.close()

    # --- Session Management ---

    def create_session(self, scene_id: Optional[str] = None) -> str:
        """
        Create a new chat session.

        Args:
            scene_id: Optional scene identifier to link this session to

        Returns:
            The new session UUID
        """
        session_id = str(uuid.uuid4())
        logger.info(f"Created new session: {session_id}" + (f" (scene: {scene_id})" if scene_id else ""))

        # Optionally log a system event marking session start
        self.log_event(
            session_id=session_id,
            role="system",
            content="Session started",
            scene_id=scene_id
        )

        return session_id

    def log_event(
        self,
        session_id: str,
        role: str,
        content: str,
        scene_id: Optional[str] = None
    ) -> SessionEvent:
        """
        Log a message event to the session.

        Args:
            session_id: The session UUID
            role: One of 'user', 'assistant', 'system'
            content: The message content
            scene_id: Optional scene identifier

        Returns:
            The created SessionEvent object
        """
        # Approximate token count (rough estimate: ~4 chars per token)
        token_count = len(content) // 4

        event = SessionEvent(
            session_id=session_id,
            scene_id=scene_id,
            role=role,
            content=content,
            token_count=token_count,
            is_committed=False,
            timestamp=datetime.now(timezone.utc)
        )

        try:
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            logger.debug(f"Logged event {event.id} to session {session_id[:8]}... ({role}, {token_count} tokens)")
            return event
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to log event: {e}")
            raise

    # --- History Retrieval ---

    def get_session_history(
        self,
        session_id: str,
        limit: int = 50,
        include_committed: bool = True
    ) -> List[SessionEvent]:
        """
        Get recent events from a session.

        Args:
            session_id: The session UUID
            limit: Maximum number of events to return
            include_committed: Whether to include already-digested events

        Returns:
            List of SessionEvent objects, ordered by timestamp
        """
        try:
            query = self.db.query(SessionEvent).filter(
                SessionEvent.session_id == session_id
            )

            if not include_committed:
                query = query.filter(SessionEvent.is_committed == False)

            events = query.order_by(SessionEvent.timestamp.asc()).limit(limit).all()
            return events
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []

    def get_active_sessions(self, limit: int = 20) -> List[dict]:
        """
        Get recently active sessions.

        Returns:
            List of session summaries with id, scene_id, event_count, last_activity
        """
        try:
            from sqlalchemy import func

            # Subquery to get session stats
            results = self.db.query(
                SessionEvent.session_id,
                SessionEvent.scene_id,
                func.count(SessionEvent.id).label('event_count'),
                func.max(SessionEvent.timestamp).label('last_activity')
            ).group_by(
                SessionEvent.session_id
            ).order_by(
                func.max(SessionEvent.timestamp).desc()
            ).limit(limit).all()

            return [
                {
                    "session_id": r.session_id,
                    "scene_id": r.scene_id,
                    "event_count": r.event_count,
                    "last_activity": r.last_activity.isoformat() if r.last_activity else None
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return []

    # --- Consolidator Support ---

    def get_uncommitted_events(
        self,
        scene_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[SessionEvent]:
        """
        Get events that haven't been digested by the Consolidator yet.

        This is used by the Consolidator to find new content to process.

        Args:
            scene_id: Filter by scene (optional)
            session_id: Filter by session (optional)

        Returns:
            List of uncommitted SessionEvent objects
        """
        try:
            query = self.db.query(SessionEvent).filter(
                SessionEvent.is_committed == False,
                SessionEvent.role != 'system'  # Skip system messages
            )

            if scene_id:
                query = query.filter(SessionEvent.scene_id == scene_id)

            if session_id:
                query = query.filter(SessionEvent.session_id == session_id)

            events = query.order_by(SessionEvent.timestamp.asc()).all()
            return events
        except Exception as e:
            logger.error(f"Failed to get uncommitted events: {e}")
            return []

    def mark_as_committed(self, event_ids: List[int]) -> int:
        """
        Mark events as digested by the Consolidator.

        Args:
            event_ids: List of event IDs to mark

        Returns:
            Number of events updated
        """
        if not event_ids:
            return 0

        try:
            updated = self.db.query(SessionEvent).filter(
                SessionEvent.id.in_(event_ids)
            ).update(
                {"is_committed": True},
                synchronize_session=False
            )
            self.db.commit()
            logger.info(f"Marked {updated} events as committed")
            return updated
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to mark events as committed: {e}")
            raise

    # --- Statistics ---

    def get_session_stats(self, session_id: str) -> dict:
        """
        Get statistics for a session (useful for compaction decisions).

        Returns:
            Dict with total_events, total_tokens, uncommitted_count
        """
        try:
            from sqlalchemy import func

            stats = self.db.query(
                func.count(SessionEvent.id).label('total_events'),
                func.sum(SessionEvent.token_count).label('total_tokens'),
                func.sum(
                    (SessionEvent.is_committed == False).cast(Integer)
                ).label('uncommitted_count')
            ).filter(
                SessionEvent.session_id == session_id
            ).first()

            return {
                "session_id": session_id,
                "total_events": stats.total_events or 0,
                "total_tokens": stats.total_tokens or 0,
                "uncommitted_count": stats.uncommitted_count or 0
            }
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {
                "session_id": session_id,
                "total_events": 0,
                "total_tokens": 0,
                "uncommitted_count": 0
            }


# --- Convenience function for one-off operations ---
def get_session_service() -> SessionService:
    """
    Get a SessionService instance.

    Usage:
        with get_session_service() as service:
            session_id = service.create_session()
    """
    return SessionService()
