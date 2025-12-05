"""
Narrative Ontology for GraphRAG.

Defines narrative-specific edge types based on story physics.
These capture the dramatic relationships that drive plot.

Part of GraphRAG Phase 3 - Narrative Extraction.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict


class NarrativeEdgeType(Enum):
    """
    Core narrative edge types based on story physics.

    These capture the dramatic relationships that drive plot.
    """
    # Goal-Obstacle-Conflict Triad
    MOTIVATES = "MOTIVATES"      # Goal → Character (what drives them)
    HINDERS = "HINDERS"          # Obstacle → Goal (what blocks progress)
    CAUSES = "CAUSES"            # Event → Event (causality chain)

    # Character Dynamics
    CHALLENGES = "CHALLENGES"    # Scene → Fatal Flaw (when flaw is tested)
    KNOWS = "KNOWS"              # Character → Fact (knowledge state)
    CONTRADICTS = "CONTRADICTS"  # Fact → Fact (conflicts in story logic)

    # Narrative Threading
    FORESHADOWS = "FORESHADOWS"  # Scene → Future Event (setup)
    CALLBACKS = "CALLBACKS"      # Scene → Past Event (payoff)

    # Existing types (for compatibility with basic extraction)
    LOCATED_IN = "LOCATED_IN"
    OWNS = "OWNS"
    PART_OF = "PART_OF"
    HAS_TRAIT = "HAS_TRAIT"
    LOVES = "LOVES"
    HATES = "HATES"
    ALLIES_WITH = "ALLIES_WITH"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    REVEALS = "REVEALS"

    # Escape hatch for custom types
    CUSTOM = "CUSTOM"


@dataclass
class NarrativeEdge:
    """Enhanced edge with narrative metadata."""
    source: str
    target: str
    edge_type: NarrativeEdgeType
    description: Optional[str] = None
    weight: float = 1.0  # For tension calculations
    scene_id: Optional[str] = None  # Where relationship established
    is_active: bool = True  # Can be "resolved" (obstacle overcome)
    custom_type: Optional[str] = None  # If edge_type is CUSTOM

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.edge_type.value,
            "description": self.description,
            "weight": self.weight,
            "scene_id": self.scene_id,
            "is_active": self.is_active,
            "custom_type": self.custom_type
        }


# Default edge types (can be toggled in settings)
DEFAULT_EDGE_TYPES: Dict[NarrativeEdgeType, bool] = {
    # Core narrative types - enabled by default
    NarrativeEdgeType.MOTIVATES: True,
    NarrativeEdgeType.HINDERS: True,
    NarrativeEdgeType.CHALLENGES: True,
    NarrativeEdgeType.CAUSES: True,
    NarrativeEdgeType.FORESHADOWS: True,
    NarrativeEdgeType.CALLBACKS: True,
    NarrativeEdgeType.KNOWS: True,

    # Experimental - off by default (can create noise)
    NarrativeEdgeType.CONTRADICTS: False,

    # Basic relationship types - enabled by default
    NarrativeEdgeType.LOCATED_IN: True,
    NarrativeEdgeType.OWNS: True,
    NarrativeEdgeType.PART_OF: True,
    NarrativeEdgeType.HAS_TRAIT: True,
    NarrativeEdgeType.LOVES: True,
    NarrativeEdgeType.HATES: True,
    NarrativeEdgeType.ALLIES_WITH: True,
    NarrativeEdgeType.CONFLICTS_WITH: True,
    NarrativeEdgeType.REVEALS: True,
}


# Edge type descriptions for UI/API
EDGE_TYPE_DESCRIPTIONS: Dict[str, str] = {
    "MOTIVATES": "What drives a character toward their goal",
    "HINDERS": "What blocks or impedes a goal",
    "CAUSES": "One event leading to another (causality)",
    "CHALLENGES": "Scene or event that tests a character's weakness/flaw",
    "KNOWS": "Character possesses knowledge of a fact",
    "CONTRADICTS": "Two facts that conflict with each other",
    "FORESHADOWS": "Sets up or hints at future events",
    "CALLBACKS": "References or resolves earlier events/setups",
    "LOCATED_IN": "Entity is in a place",
    "OWNS": "Possession or ownership",
    "PART_OF": "Hierarchical membership",
    "HAS_TRAIT": "Character or entity has a property",
    "LOVES": "Positive emotional bond",
    "HATES": "Negative emotional bond",
    "ALLIES_WITH": "Cooperative relationship",
    "CONFLICTS_WITH": "Adversarial relationship",
    "REVEALS": "Information disclosure",
    "CUSTOM": "User-defined relationship type",
}


def get_enabled_edge_types() -> List[NarrativeEdgeType]:
    """
    Get list of enabled edge types from settings.

    Falls back to defaults if settings service unavailable.
    """
    try:
        from backend.services.settings_service import settings_service

        enabled = []
        for edge_type, default in DEFAULT_EDGE_TYPES.items():
            key = f"graph.edge_types.{edge_type.value}"
            if settings_service.get(key, default):
                enabled.append(edge_type)

        return enabled
    except Exception:
        # Fall back to defaults
        return [t for t, enabled in DEFAULT_EDGE_TYPES.items() if enabled]


def get_all_edge_types() -> List[Dict]:
    """
    Get all edge types with their status and descriptions.

    Returns list of dicts suitable for API response.
    """
    enabled = get_enabled_edge_types()

    return [
        {
            "name": edge_type.value,
            "enabled": edge_type in enabled,
            "default": DEFAULT_EDGE_TYPES.get(edge_type, True),
            "description": EDGE_TYPE_DESCRIPTIONS.get(edge_type.value, ""),
        }
        for edge_type in NarrativeEdgeType
        if edge_type != NarrativeEdgeType.CUSTOM
    ]


def parse_edge_type(type_str: str) -> NarrativeEdgeType:
    """
    Parse a string to NarrativeEdgeType, with fallback to CUSTOM.

    Args:
        type_str: Edge type string from LLM extraction

    Returns:
        NarrativeEdgeType enum value
    """
    normalized = type_str.upper().strip()

    try:
        return NarrativeEdgeType[normalized]
    except KeyError:
        # Handle common variations
        variations = {
            "RELATED_TO": NarrativeEdgeType.PART_OF,
            "BELONGS_TO": NarrativeEdgeType.PART_OF,
            "LIVES_IN": NarrativeEdgeType.LOCATED_IN,
            "IN": NarrativeEdgeType.LOCATED_IN,
            "HAS": NarrativeEdgeType.OWNS,
            "POSSESSES": NarrativeEdgeType.OWNS,
            "FRIEND": NarrativeEdgeType.ALLIES_WITH,
            "ENEMY": NarrativeEdgeType.CONFLICTS_WITH,
            "LEADS_TO": NarrativeEdgeType.CAUSES,
            "TRIGGERS": NarrativeEdgeType.CAUSES,
            "SETUP": NarrativeEdgeType.FORESHADOWS,
            "PAYOFF": NarrativeEdgeType.CALLBACKS,
            "TESTS": NarrativeEdgeType.CHALLENGES,
            "BLOCKS": NarrativeEdgeType.HINDERS,
            "PREVENTS": NarrativeEdgeType.HINDERS,
            "DRIVES": NarrativeEdgeType.MOTIVATES,
        }

        if normalized in variations:
            return variations[normalized]

        return NarrativeEdgeType.CUSTOM
