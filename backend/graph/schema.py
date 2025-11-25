from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    node_type = Column(String)  # e.g., 'scene', 'character', 'location', 'event'
    name = Column(String)
    description = Column(String)
    content = Column(String) # Textual content if applicable. Can be used for Scene text, Character bio, etc.

    # Backrefs for edges (relationships)
    outgoing_edges = relationship("Edge", back_populates="source_node", foreign_keys="[Edge.source_id]")
    incoming_edges = relationship("Edge", back_populates="target_node", foreign_keys="[Edge.target_id]")

    scene_metadata = relationship("SceneMetadata", back_populates="node", uselist=False)

    def __repr__(self):
        return f"<Node(id={self.id}, type='{self.node_type}', name='{self.name}')>"


class Edge(Base):
    __tablename__ = 'edges'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('nodes.id'))
    target_id = Column(Integer, ForeignKey('nodes.id'))
    relation_type = Column(String)  # e.g., 'related_to', 'part_of', 'occurs_in'

    source_node = relationship("Node", back_populates="outgoing_edges", foreign_keys=[source_id])
    target_node = relationship("Node", back_populates="incoming_edges", foreign_keys=[target_id])

    def __repr__(self):
        return f"<Edge(id={self.id}, source={self.source_id}, target={self.target_id}, type='{self.relation_type}')>"



class SceneMetadata(Base):
    __tablename__ = 'scene_metadata'

    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    draft_number = Column(Integer, default=0)
    last_edited = Column(DateTime, default=datetime.utcnow)
    is_locked = Column(Boolean, default=False)

    # Scoring dimensions from the spec.
    voice_authenticity = Column(Float)
    pacing_tension = Column(Float)
    dialogue_naturalness = Column(Float)
    show_dont_tell = Column(Float)
    character_development = Column(Float)
    graph_consistency = Column(Float)

    node = relationship("Node", back_populates="scene_metadata")


    def __repr__(self):
        return f"<SceneMetadata(node_id={self.node_id}, draft={self.draft_number}, locked={self.is_locked})>"


# --- Phase 3D: Graph Health Service Tables ---

class Chapter(Base):
    """
    Chapter tracking for pacing analysis and beat progress validation.

    Phase 3D Strategic Decisions:
    - Auto-trigger health checks after chapter assembly (Decision 3)
    - Store historical reports for longitudinal analysis (Decision 4)
    """
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True)
    chapter_id = Column(String, unique=True, nullable=False, index=True)  # e.g., "chapter_2.5"
    act = Column(Integer, nullable=False)
    title = Column(String)
    total_word_count = Column(Integer, default=0)
    avg_tension = Column(Float)  # Average tension across scenes
    completion_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    health_score = Column(Integer)  # Set by Graph Health Service
    project_id = Column(String, index=True)

    # Relationships
    scenes = relationship("Scene", back_populates="chapter")
    health_reports = relationship("HealthReportHistory", back_populates="chapter")

    def __repr__(self):
        return f"<Chapter(id='{self.chapter_id}', act={self.act}, health_score={self.health_score})>"


class Scene(Base):
    """
    Individual scene tracking for tension analysis and timeline consistency.

    Phase 3D: Used for:
    - Pacing plateau detection (tension_score over multiple scenes)
    - Timeline consistency checks (location, timestamp, characters)
    - Flaw challenge monitoring
    """
    __tablename__ = 'scenes'

    id = Column(Integer, primary_key=True)
    scene_id = Column(String, unique=True, nullable=False, index=True)  # e.g., "scene_2.5.1"
    chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=False)
    beat_id = Column(Integer, ForeignKey('beats.id'))

    tension_score = Column(Float)  # 0-10 scale
    word_count = Column(Integer, default=0)
    completion_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    analysis_score = Column(Float)  # From Scene Analyzer (Phase 3B)

    # Timeline consistency tracking
    pov_character = Column(String)
    location = Column(String)
    timestamp = Column(String)  # In-story timeline (e.g., "story_day_5_14:30")

    project_id = Column(String, index=True)

    # Relationships
    chapter = relationship("Chapter", back_populates="scenes")
    beat = relationship("Beat", back_populates="scenes")
    flaw_challenges = relationship("FlawChallenge", back_populates="scene")

    def __repr__(self):
        return f"<Scene(id='{self.scene_id}', tension={self.tension_score}, beat={self.beat_id})>"


class Beat(Base):
    """
    15-beat structure tracking for beat progress validation.

    Phase 3D Check A2: Beat Progress Validation
    - Ensures story structure matches planned beats
    - Warns if beats deviate >5% from target manuscript position
    """
    __tablename__ = 'beats'

    id = Column(Integer, primary_key=True)
    beat_id = Column(String, unique=True, nullable=False, index=True)  # e.g., "beat_7"
    number = Column(Integer, nullable=False)  # 1-15
    name = Column(String, nullable=False)  # e.g., "Midpoint", "All Is Lost"
    target_percentage = Column(Float, nullable=False)  # e.g., 50.0 for Midpoint
    actual_percentage = Column(Float)  # Calculated from word count
    status = Column(String, default='pending')  # pending | complete
    deviation = Column(Float)  # Percentage points off target
    project_id = Column(String, index=True)

    # Relationships
    scenes = relationship("Scene", back_populates="beat")
    theme_resonance_scores = relationship("ThemeResonanceOverride", back_populates="beat")

    def __repr__(self):
        return f"<Beat(id='{self.beat_id}', name='{self.name}', deviation={self.deviation}%)>"


class FlawChallenge(Base):
    """
    Fatal Flaw challenge tracking for character arc health.

    Phase 3D Check B1: Fatal Flaw Challenge Monitoring
    - Tracks when protagonist's Fatal Flaw is tested
    - Warns if gap exceeds threshold (default: 10 scenes)
    """
    __tablename__ = 'flaw_challenges'

    id = Column(Integer, primary_key=True)
    flaw_challenge_id = Column(String, unique=True, nullable=False)
    scene_id = Column(Integer, ForeignKey('scenes.id'), nullable=False)
    chapter_id = Column(String)

    character_id = Column(String, nullable=False)  # e.g., "protagonist"
    challenge_type = Column(String)  # direct | indirect | failure
    outcome = Column(String)  # character_passed | character_failed | character_avoided
    scenes_since_last = Column(Integer, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    project_id = Column(String, index=True)

    # Relationships
    scene = relationship("Scene", back_populates="flaw_challenges")

    def __repr__(self):
        return f"<FlawChallenge(character='{self.character_id}', type='{self.challenge_type}', outcome='{self.outcome}')>"


class ThemeResonanceOverride(Base):
    """
    Manual writer overrides for theme resonance scores.

    Phase 3D Strategic Decision 2: Hybrid LLM + Manual Override
    - LLM auto-scores theme resonance at critical beats
    - Writers can override scores when LLM misses subtle intent
    - Future health checks respect manual overrides
    """
    __tablename__ = 'theme_resonance_overrides'

    id = Column(Integer, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    beat_id = Column(Integer, ForeignKey('beats.id'), nullable=False)
    theme_id = Column(String, nullable=False)

    manual_score = Column(Float, nullable=False)  # 0-10 scale (writer's override)
    llm_score = Column(Float)  # Original LLM auto-score
    reason = Column(Text)  # Writer's explanation
    overridden_by = Column(String, default='writer')
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    beat = relationship("Beat", back_populates="theme_resonance_scores")

    def __repr__(self):
        return f"<ThemeResonanceOverride(beat='{self.beat_id}', theme='{self.theme_id}', manual={self.manual_score}, llm={self.llm_score})>"


class HealthReportHistory(Base):
    """
    Historical health report storage for longitudinal analysis.

    Phase 3D Strategic Decision 4: SQLite Persistence
    - Stores all health reports with 365-day retention
    - Enables trend analysis: "Is pacing improving over time?"
    - Supports A/B testing and writer learning
    """
    __tablename__ = 'health_report_history'

    id = Column(Integer, primary_key=True)
    report_id = Column(String, unique=True, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)

    scope = Column(String, nullable=False)  # chapter | act | manuscript
    chapter_id = Column(Integer, ForeignKey('chapters.id'))
    act_number = Column(Integer)

    overall_score = Column(Integer, default=100)  # 0-100
    warnings = Column(JSON)  # JSON array of warning objects
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    chapter = relationship("Chapter", back_populates="health_reports")

    def __repr__(self):
        return f"<HealthReport(id='{self.report_id}', scope='{self.scope}', score={self.overall_score})>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "report_id": self.report_id,
            "project_id": self.project_id,
            "scope": self.scope,
            "chapter_id": self.chapter_id,
            "act_number": self.act_number,
            "overall_score": self.overall_score,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
