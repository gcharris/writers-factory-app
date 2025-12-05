"""
Settings Service - Configurable Parameters for Director Mode

This service manages a 3-tier settings resolution system:
1. Project-specific overrides (highest priority)
2. Global user settings (medium priority)
3. Default values (fallback)

Architecture:
- SQLite-backed persistence using SQLAlchemy (same pattern as ForemanKBService)
- JSON serialization for complex values (lists, dicts, etc.)
- Validation to ensure settings are within acceptable ranges
- Type-safe retrieval with fallback to defaults

Usage:
    settings_service = SettingsService()

    # Get a setting (uses 3-tier resolution)
    weight = settings_service.get("scoring.voice_authenticity_weight", project_id="proj_123")

    # Set a project-specific override
    settings_service.set("scoring.voice_authenticity_weight", 40, project_id="proj_123")

    # Set a global setting
    settings_service.set("scoring.voice_authenticity_weight", 35)

    # Reset project override (falls back to global or default)
    settings_service.reset("scoring.voice_authenticity_weight", project_id="proj_123")
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- Logging ---
logger = logging.getLogger(__name__)

# --- Database Setup ---
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)
SETTINGS_DB_PATH = os.path.join(WORKSPACE_DIR, "sessions.db")  # Share with ForemanKB
SETTINGS_DB_URL = f"sqlite:///{SETTINGS_DB_PATH}"

# SQLAlchemy setup
engine = create_engine(SETTINGS_DB_URL, echo=False)
SettingsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Models ---
class GlobalSetting(Base):
    """Global user settings (applies to all projects unless overridden)."""
    __tablename__ = "global_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=False)  # JSON serialized
    category = Column(String(50), nullable=False, index=True)  # scoring, enhancement, etc.
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "key": self.key,
            "value": json.loads(self.value),
            "category": self.category,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProjectSetting(Base):
    """Project-specific setting overrides."""
    __tablename__ = "project_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(255), nullable=False, index=True)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)  # JSON serialized
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_project_key', 'project_id', 'key', unique=True),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "key": self.key,
            "value": json.loads(self.value),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Create tables
Base.metadata.create_all(bind=engine)
logger.info(f"Settings tables initialized in: {SETTINGS_DB_PATH}")


# --- Default Settings ---
@dataclass
class DefaultSettings:
    """
    Default values for all configurable settings.

    These match the specifications in SETTINGS_CONFIGURATION.md.
    """

    # --- Scoring Rubric Weights ---
    scoring: Dict[str, Any] = field(default_factory=lambda: {
        # Category weights (must sum to 100)
        "voice_authenticity_weight": 30,
        "character_consistency_weight": 20,
        "metaphor_discipline_weight": 20,
        "anti_pattern_compliance_weight": 15,
        "phase_appropriateness_weight": 15,

        # Voice authentication strictness
        "authenticity_strictness": "medium",  # low/medium/high
        "purpose_strictness": "medium",
        "fusion_strictness": "medium",

        # Metaphor discipline settings
        "saturation_threshold": 30,  # Max % for any single domain
        "primary_allowance": 35,  # Higher limit for ONE designated primary domain
        "simile_tolerance": 2,  # How many similes allowed before penalty
        "min_domains": 3,  # Minimum different domains required
    })

    # --- Anti-Pattern Detection ---
    anti_patterns: Dict[str, Any] = field(default_factory=lambda: {
        "zero_tolerance": {
            "first_person_italics": {"enabled": True, "penalty": -2},
            "with_precision": {"enabled": True, "penalty": -2},
            "explaining_to_camera": {"enabled": True, "penalty": -2},
            "ai_explaining_character": {"enabled": True, "penalty": -2},
        },
        "formulaic": {
            "despite_the": {"enabled": True, "penalty": -1},
            "eyes_widened": {"enabled": True, "penalty": -1},
            "breath_caught": {"enabled": True, "penalty": -1},
            "pulse_quickened": {"enabled": True, "penalty": -1},
        },
        "custom": []  # User-defined patterns: [{"pattern": "suddenly", "severity": "formulaic", "reason": "..."}]
    })

    # --- Enhancement Pipeline Settings ---
    enhancement: Dict[str, Any] = field(default_factory=lambda: {
        "auto_threshold": 85,  # Score below which enhancement is suggested
        "action_prompt_threshold": 85,  # Score above which surgical fixes are used
        "six_pass_threshold": 70,  # Score below which full enhancement runs
        "rewrite_threshold": 60,  # Score below which rewrite is recommended
        "aggressiveness": "medium",  # conservative/medium/aggressive
    })

    # --- Tournament Settings ---
    tournament: Dict[str, Any] = field(default_factory=lambda: {
        "variants_per_agent": 5,
        "strategies": ["ACTION", "CHARACTER", "DIALOGUE", "BRAINSTORMING", "BALANCED"],
        "auto_score_variants": True,
        "show_losing_variants": True,
        "top_n_display": 5,
    })

    # --- Foreman Behavior ---
    foreman: Dict[str, Any] = field(default_factory=lambda: {
        "proactiveness": "medium",  # low/medium/high
        "challenge_intensity": "medium",
        "explanation_verbosity": "medium",
        "auto_kb_writes": True,

        # Phase 3E: Intelligent multi-model support
        "coordinator_model": "mistral",         # Local 7B - Fast coordination tasks

        # Task-specific model assignments (configurable per task type)
        "task_models": {
            "coordinator": "mistral",                      # Simple coordination
            "health_check_review": "deepseek-chat",        # Health check interpretation
            "voice_calibration_guidance": "deepseek-chat", # Voice tournament guidance
            "beat_structure_advice": "deepseek-chat",      # Beat structure analysis
            "conflict_resolution": "deepseek-chat",        # Timeline/character conflicts
            "scaffold_enrichment_decisions": "deepseek-chat", # Scaffold enrichment
            "theme_analysis": "deepseek-chat",             # Theme and symbolism
            "structural_planning": "deepseek-chat",        # High-level planning
        },
    })

    # --- Context Window Management ---
    context: Dict[str, Any] = field(default_factory=lambda: {
        "max_conversation_history": 20,
        "kb_context_limit": 1000,
        "voice_bundle_injection": "full",  # full/summary/minimal
        "continuity_context_depth": 3,
    })

    # --- Graph Health Checks (Phase 3D) ---
    health_checks: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "models": {
            # Default model for basic health checks
            "default_model": "llama3.2",

            # Phase 3E: Task-specific model assignments (configurable)
            "timeline_consistency": "claude-3-5-sonnet",  # Best at narrative reasoning
            "theme_resonance": "gpt-4o",                   # Excellent thematic analysis
            "flaw_challenges": "deepseek-chat",            # Deep character psychology
            "cast_function": "qwen-plus",                  # Fast, cheap, good enough
            "pacing_analysis": "mistral",                  # Local for fast iteration
            "beat_progress": "mistral",                    # Structural validation
            "symbolic_layering": "gpt-4o",                 # Pattern recognition
        },
        "pacing": {
            "plateau_window": 3,
            "plateau_tolerance": 1.0,
            "enabled": True,
        },
        "structure": {
            "beat_deviation_warning": 5,
            "beat_deviation_error": 10,
            "enabled": True,
        },
        "character": {
            "flaw_challenge_frequency": 10,
            "min_cast_appearances": 3,
            "enabled": True,
        },
        "theme": {
            "min_symbol_occurrences": 3,
            "min_resonance_score": 6,
            "auto_score": True,  # Enable automated LLM scoring
            "allow_manual_override": True,  # Writer can override scores
            "enabled": True,
        },
        "timeline": {
            "enabled": True,
            "semantic_analysis": True,  # Use full LLM semantic analysis
            "check_character_locations": True,
            "check_world_rules": True,
            "check_dropped_threads": True,
            "confidence_threshold": 0.7,  # Minimum confidence for conflict detection
        },
        "reporting": {
            "store_history": True,  # Store historical reports for trend analysis
            "retention_days": 365,  # Keep reports for 1 year
            "auto_trigger": True,  # Auto-run after chapter assembly
            "notification_mode": "foreman_proactive",  # Use Foreman proactiveness setting
        },
    })

    # --- AI Intelligence & Model Orchestration (Phase 3E) ---
    orchestrator: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,  # When True, overrides manual task_models
        "quality_tier": "balanced",  # "budget" | "balanced" | "premium"
        "monthly_budget": None,  # USD per month (None = unlimited)
        "prefer_local": False,  # Prefer local models when quality similar
        "cost_tracking_enabled": True,

        # Current month tracking (auto-updated)
        "current_month": None,  # "2025-11"
        "current_month_spend": 0.0,  # USD spent this month
    })

    # --- Multi-Model Tournament (Phase 4 - planned) ---
    tournament_consensus: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "critical_tasks": [
            "beat_structure_advice",
            "structural_planning",
            "theme_analysis"
        ],
        "num_models": 3,
        "consensus_threshold": 0.7,
        "max_tournaments_per_day": 10,
        "show_all_responses": True,
    })

    # --- Squad System (Phase 3F) ---
    squad: Dict[str, Any] = field(default_factory=lambda: {
        "active_squad": "hybrid",  # "local" | "hybrid" | "pro"
        "setup_complete": False,
        "course_mode": False,  # Not yet implemented (Phase 3G)
        "custom_tournament_models": [],  # User overrides for tournament models
    })

    # --- Knowledge Graph (GraphRAG) ---
    graph: Dict[str, Any] = field(default_factory=lambda: {
        "edge_types": {
            "MOTIVATES": True,
            "HINDERS": True,
            "CHALLENGES": True,
            "CAUSES": True,
            "FORESHADOWS": True,
            "CALLBACKS": True,
            "KNOWS": True,
            "CONTRADICTS": False,  # Experimental
        },
        "extraction_triggers": {
            "on_manuscript_promote": True,
            "before_foreman_chat": True,
            "periodic_minutes": 0,  # 0 = disabled
        },
        "verification_level": "standard",  # "minimal" | "standard" | "thorough"
        "embedding_provider": "ollama",  # "ollama" | "openai" | "cohere" | "none"
    })

    def get_flat_dict(self) -> Dict[str, Any]:
        """
        Convert nested settings to flat key-value pairs.

        Example:
            scoring.voice_authenticity_weight = 30
            anti_patterns.zero_tolerance.first_person_italics = {"enabled": True, "penalty": -2}
        """
        result = {}

        for category in ["scoring", "anti_patterns", "enhancement", "tournament", "foreman", "context", "health_checks", "orchestrator", "tournament_consensus", "squad", "graph"]:
            category_data = getattr(self, category)
            self._flatten(category_data, category, result)

        return result

    def _flatten(self, data: Any, prefix: str, result: Dict[str, Any]) -> None:
        """Recursively flatten nested dictionaries."""
        if isinstance(data, dict):
            for key, value in data.items():
                self._flatten(value, f"{prefix}.{key}", result)
        else:
            result[prefix] = data

    def get_category_dict(self, category: str) -> Dict[str, Any]:
        """Get all settings for a specific category."""
        return getattr(self, category, {})


# Singleton instance
DEFAULTS = DefaultSettings()


# --- Validation Rules ---
class SettingsValidator:
    """Validates setting values against acceptable ranges and types."""

    RULES = {
        # Scoring weights must be 0-100
        "scoring.voice_authenticity_weight": {"type": int, "min": 10, "max": 50},
        "scoring.character_consistency_weight": {"type": int, "min": 10, "max": 30},
        "scoring.metaphor_discipline_weight": {"type": int, "min": 10, "max": 30},
        "scoring.anti_pattern_compliance_weight": {"type": int, "min": 5, "max": 25},
        "scoring.phase_appropriateness_weight": {"type": int, "min": 5, "max": 25},

        # Strictness levels
        "scoring.authenticity_strictness": {"type": str, "choices": ["low", "medium", "high"]},
        "scoring.purpose_strictness": {"type": str, "choices": ["low", "medium", "high"]},
        "scoring.fusion_strictness": {"type": str, "choices": ["low", "medium", "high"]},

        # Metaphor settings
        "scoring.saturation_threshold": {"type": int, "min": 20, "max": 50},
        "scoring.primary_allowance": {"type": int, "min": 25, "max": 45},
        "scoring.simile_tolerance": {"type": int, "min": 0, "max": 5},
        "scoring.min_domains": {"type": int, "min": 2, "max": 6},

        # Enhancement thresholds
        "enhancement.auto_threshold": {"type": int, "min": 70, "max": 95},
        "enhancement.action_prompt_threshold": {"type": int, "min": 80, "max": 95},
        "enhancement.six_pass_threshold": {"type": int, "min": 60, "max": 80},
        "enhancement.rewrite_threshold": {"type": int, "min": 50, "max": 70},
        "enhancement.aggressiveness": {"type": str, "choices": ["conservative", "medium", "aggressive"]},

        # Tournament settings
        "tournament.variants_per_agent": {"type": int, "min": 3, "max": 10},
        "tournament.top_n_display": {"type": int, "min": 3, "max": 10},

        # Foreman behavior
        "foreman.proactiveness": {"type": str, "choices": ["low", "medium", "high"]},
        "foreman.challenge_intensity": {"type": str, "choices": ["low", "medium", "high"]},
        "foreman.explanation_verbosity": {"type": str, "choices": ["low", "medium", "high"]},

        # Health check models (Phase 3D)
        "health_checks.models.health_check_model": {"type": str},  # Ollama model name
        "health_checks.models.timeline_analysis_model": {"type": (str, type(None))},  # Optional override
        "health_checks.models.theme_scoring_model": {"type": (str, type(None))},  # Optional override

        # Health check thresholds
        "health_checks.pacing.plateau_window": {"type": int, "min": 2, "max": 5},
        "health_checks.pacing.plateau_tolerance": {"type": float, "min": 0.5, "max": 2.0},
        "health_checks.structure.beat_deviation_warning": {"type": int, "min": 3, "max": 10},
        "health_checks.structure.beat_deviation_error": {"type": int, "min": 8, "max": 15},
        "health_checks.character.flaw_challenge_frequency": {"type": int, "min": 5, "max": 20},
        "health_checks.character.min_cast_appearances": {"type": int, "min": 1, "max": 5},
        "health_checks.theme.min_symbol_occurrences": {"type": int, "min": 2, "max": 6},
        "health_checks.theme.min_resonance_score": {"type": int, "min": 4, "max": 8},
        "health_checks.timeline.confidence_threshold": {"type": float, "min": 0.5, "max": 0.95},
        "health_checks.reporting.retention_days": {"type": int, "min": 30, "max": 730},
        "health_checks.reporting.notification_mode": {"type": str, "choices": ["foreman_proactive", "silent", "always"]},

        # Graph settings (Phase 5)
        "graph.verification_level": {"type": str, "choices": ["minimal", "standard", "thorough"]},
        "graph.embedding_provider": {"type": str, "choices": ["ollama", "openai", "cohere", "none"]},
        "graph.extraction_triggers.periodic_minutes": {"type": int, "min": 0, "max": 60},
    }

    @classmethod
    def validate(cls, key: str, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a setting value.

        Returns:
            (is_valid, error_message)
        """
        if key not in cls.RULES:
            # No validation rule defined - allow it
            return True, None

        rule = cls.RULES[key]
        expected_type = rule["type"]

        # Type check
        if not isinstance(value, expected_type):
            return False, f"Expected {expected_type.__name__}, got {type(value).__name__}"

        # Range check (for int/float)
        if expected_type in [int, float]:
            if "min" in rule and value < rule["min"]:
                return False, f"Value {value} below minimum {rule['min']}"
            if "max" in rule and value > rule["max"]:
                return False, f"Value {value} above maximum {rule['max']}"

        # Choices check (for str)
        if "choices" in rule and value not in rule["choices"]:
            return False, f"Value '{value}' not in allowed choices: {rule['choices']}"

        return True, None


# --- Service Class ---
class SettingsService:
    """
    Manages application settings with 3-tier resolution.

    Resolution order:
    1. Project-specific override (if project_id provided)
    2. Global user setting
    3. Default value
    """

    def __init__(self):
        self.defaults = DEFAULTS
        self.validator = SettingsValidator()

    def get(self, key: str, project_id: Optional[str] = None) -> Any:
        """
        Get a setting value using 3-tier resolution.

        Args:
            key: Setting key (e.g., "scoring.voice_authenticity_weight")
            project_id: Optional project ID for project-specific override

        Returns:
            The setting value
        """
        db: Session = SettingsSessionLocal()
        try:
            # 1. Check project-specific override
            if project_id:
                project_setting = db.query(ProjectSetting).filter(
                    ProjectSetting.project_id == project_id,
                    ProjectSetting.key == key
                ).first()
                if project_setting:
                    return json.loads(project_setting.value)

            # 2. Check global setting
            global_setting = db.query(GlobalSetting).filter(
                GlobalSetting.key == key
            ).first()
            if global_setting:
                return json.loads(global_setting.value)

            # 3. Fall back to default
            flat_defaults = self.defaults.get_flat_dict()
            if key in flat_defaults:
                return flat_defaults[key]

            logger.warning(f"Setting key '{key}' not found in defaults")
            return None

        finally:
            db.close()

    def set(self, key: str, value: Any, project_id: Optional[str] = None, category: str = "general") -> bool:
        """
        Set a setting value.

        Args:
            key: Setting key
            value: Setting value
            project_id: If provided, sets project-specific override; otherwise sets global
            category: Setting category (for organization)

        Returns:
            True if successful, False if validation failed
        """
        # Validate
        is_valid, error = self.validator.validate(key, value)
        if not is_valid:
            logger.error(f"Validation failed for {key}: {error}")
            return False

        db: Session = SettingsSessionLocal()
        try:
            value_json = json.dumps(value)

            if project_id:
                # Set project-specific override
                existing = db.query(ProjectSetting).filter(
                    ProjectSetting.project_id == project_id,
                    ProjectSetting.key == key
                ).first()

                if existing:
                    existing.value = value_json
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    new_setting = ProjectSetting(
                        project_id=project_id,
                        key=key,
                        value=value_json
                    )
                    db.add(new_setting)
            else:
                # Set global setting
                existing = db.query(GlobalSetting).filter(
                    GlobalSetting.key == key
                ).first()

                if existing:
                    existing.value = value_json
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    new_setting = GlobalSetting(
                        key=key,
                        value=value_json,
                        category=category
                    )
                    db.add(new_setting)

            db.commit()
            logger.info(f"Set {key} = {value} (project_id={project_id})")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to set {key}: {e}")
            return False
        finally:
            db.close()

    def reset(self, key: str, project_id: Optional[str] = None) -> bool:
        """
        Reset a setting to its default value.

        If project_id is provided, removes the project-specific override.
        If project_id is None, removes the global setting.

        Args:
            key: Setting key
            project_id: Optional project ID

        Returns:
            True if successful
        """
        db: Session = SettingsSessionLocal()
        try:
            if project_id:
                db.query(ProjectSetting).filter(
                    ProjectSetting.project_id == project_id,
                    ProjectSetting.key == key
                ).delete()
            else:
                db.query(GlobalSetting).filter(
                    GlobalSetting.key == key
                ).delete()

            db.commit()
            logger.info(f"Reset {key} (project_id={project_id})")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to reset {key}: {e}")
            return False
        finally:
            db.close()

    def get_category(self, category: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all settings for a category (e.g., "scoring", "enhancement").

        Args:
            category: Category name
            project_id: Optional project ID

        Returns:
            Dictionary of all settings in the category
        """
        category_defaults = self.defaults.get_category_dict(category)
        result = {}

        # Start with defaults
        for key, value in self._flatten_dict(category_defaults, category).items():
            result[key] = self.get(key, project_id)

        return result

    def _flatten_dict(self, data: Dict[str, Any], prefix: str) -> Dict[str, Any]:
        """Recursively flatten nested dictionaries."""
        result = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}"
            if isinstance(value, dict) and not self._is_pattern_dict(value):
                result.update(self._flatten_dict(value, full_key))
            else:
                result[full_key] = value
        return result

    def _is_pattern_dict(self, value: Dict[str, Any]) -> bool:
        """Check if a dict is a pattern definition (has 'enabled' and 'penalty' keys)."""
        return isinstance(value, dict) and "enabled" in value and "penalty" in value

    def get_all_project_overrides(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all project-specific overrides for a project.

        Args:
            project_id: Project ID

        Returns:
            List of override dictionaries
        """
        db: Session = SettingsSessionLocal()
        try:
            overrides = db.query(ProjectSetting).filter(
                ProjectSetting.project_id == project_id
            ).all()
            return [override.to_dict() for override in overrides]
        finally:
            db.close()

    def export_settings(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Export settings to a dictionary (for YAML export).

        Args:
            project_id: If provided, exports project-specific settings; otherwise global

        Returns:
            Dictionary suitable for YAML export
        """
        result = {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

        for category in ["scoring", "anti_patterns", "enhancement", "tournament", "foreman", "context", "health_checks"]:
            result[category] = self.get_category(category, project_id)

        return result

    def import_settings(self, settings_dict: Dict[str, Any], project_id: Optional[str] = None) -> bool:
        """
        Import settings from a dictionary (from YAML import).

        Args:
            settings_dict: Settings dictionary
            project_id: If provided, imports as project-specific; otherwise as global

        Returns:
            True if successful
        """
        try:
            for category in ["scoring", "anti_patterns", "enhancement", "tournament", "foreman", "context", "health_checks"]:
                if category not in settings_dict:
                    continue

                category_data = settings_dict[category]
                flat = self._flatten_dict(category_data, category)

                for key, value in flat.items():
                    self.set(key, value, project_id, category)

            logger.info(f"Imported settings (project_id={project_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False


# Singleton instance
settings_service = SettingsService()


def get_graph_settings(project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all graph-related settings.

    Convenience function for GraphRAG Phase 5.

    Args:
        project_id: Optional project ID for project-specific settings

    Returns:
        Dict with all graph settings
    """
    return settings_service.get_category("graph", project_id)
