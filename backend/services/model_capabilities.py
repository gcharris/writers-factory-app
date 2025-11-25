"""
Model Capabilities Registry - Phase 3E

Defines the capabilities, costs, and strengths of all available AI models
to enable intelligent model selection by the orchestrator.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class TaskStrength(Enum):
    """Task categories that models excel at."""
    NARRATIVE_CONTINUITY = "narrative_continuity"      # Timeline consistency
    THEMATIC_ANALYSIS = "thematic_analysis"           # Theme resonance
    CHARACTER_PSYCHOLOGY = "character_psychology"      # Flaw challenges
    STRUCTURAL_PLANNING = "structural_planning"        # Beat structure
    COORDINATION = "coordination"                      # Simple coordination
    SEMANTIC_REASONING = "semantic_reasoning"          # General reasoning
    CREATIVE_WRITING = "creative_writing"             # Scene generation


@dataclass
class ModelCapabilities:
    """Complete capabilities profile for a model."""
    model_id: str
    provider: str
    display_name: str

    # Performance characteristics
    strengths: List[TaskStrength]
    quality_score: int  # 0-10 (10 = best quality)
    speed: str  # "very_fast" | "fast" | "medium" | "slow"

    # Cost (per 1M tokens)
    cost_per_1m_input: float
    cost_per_1m_output: float

    # Availability
    requires_api_key: bool
    local_only: bool
    api_key_env_var: Optional[str] = None


# Model registry with complete capability profiles
MODEL_REGISTRY: List[ModelCapabilities] = [
    # === Local Models (Free) ===
    ModelCapabilities(
        model_id="mistral",
        provider="ollama",
        display_name="Mistral 7B (Local)",
        strengths=[TaskStrength.COORDINATION, TaskStrength.STRUCTURAL_PLANNING],
        quality_score=6,
        speed="very_fast",
        cost_per_1m_input=0.0,
        cost_per_1m_output=0.0,
        requires_api_key=False,
        local_only=True
    ),

    ModelCapabilities(
        model_id="llama3.2",
        provider="ollama",
        display_name="Llama 3.2 (Local)",
        strengths=[TaskStrength.COORDINATION, TaskStrength.SEMANTIC_REASONING],
        quality_score=6,
        speed="fast",
        cost_per_1m_input=0.0,
        cost_per_1m_output=0.0,
        requires_api_key=False,
        local_only=True
    ),

    # === Budget Cloud Models ===
    ModelCapabilities(
        model_id="deepseek-chat",
        provider="deepseek",
        display_name="DeepSeek V3",
        strengths=[
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CHARACTER_PSYCHOLOGY,
            TaskStrength.THEMATIC_ANALYSIS,
            TaskStrength.STRUCTURAL_PLANNING
        ],
        quality_score=9,  # Excellent reasoning at low cost
        speed="medium",
        cost_per_1m_input=0.27,  # $0.27 per 1M input tokens
        cost_per_1m_output=1.10,  # $1.10 per 1M output tokens
        requires_api_key=True,
        local_only=False,
        api_key_env_var="DEEPSEEK_API_KEY"
    ),

    ModelCapabilities(
        model_id="qwen-plus",
        provider="qwen",
        display_name="Qwen Plus",
        strengths=[TaskStrength.COORDINATION, TaskStrength.SEMANTIC_REASONING],
        quality_score=7,
        speed="fast",
        cost_per_1m_input=0.40,
        cost_per_1m_output=1.20,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="QWEN_API_KEY"
    ),

    ModelCapabilities(
        model_id="qwen-turbo",
        provider="qwen",
        display_name="Qwen Turbo",
        strengths=[TaskStrength.COORDINATION],
        quality_score=6,
        speed="very_fast",
        cost_per_1m_input=0.30,
        cost_per_1m_output=0.60,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="QWEN_API_KEY"
    ),

    ModelCapabilities(
        model_id="gpt-4o-mini",
        provider="openai",
        display_name="GPT-4o Mini",
        strengths=[TaskStrength.COORDINATION, TaskStrength.SEMANTIC_REASONING],
        quality_score=8,
        speed="very_fast",
        cost_per_1m_input=0.15,
        cost_per_1m_output=0.60,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="OPENAI_API_KEY"
    ),

    # === Premium Cloud Models ===
    ModelCapabilities(
        model_id="claude-3-5-sonnet-20241022",
        provider="anthropic",
        display_name="Claude 3.5 Sonnet",
        strengths=[
            TaskStrength.NARRATIVE_CONTINUITY,
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.THEMATIC_ANALYSIS
        ],
        quality_score=10,  # Best at narrative reasoning
        speed="medium",
        cost_per_1m_input=3.00,
        cost_per_1m_output=15.00,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="ANTHROPIC_API_KEY"
    ),

    ModelCapabilities(
        model_id="gpt-4o",
        provider="openai",
        display_name="GPT-4o",
        strengths=[
            TaskStrength.THEMATIC_ANALYSIS,
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.STRUCTURAL_PLANNING
        ],
        quality_score=10,  # Best at thematic analysis
        speed="fast",
        cost_per_1m_input=2.50,
        cost_per_1m_output=10.00,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="OPENAI_API_KEY"
    ),
]


# Task type to strength mapping
TASK_STRENGTH_MAP: Dict[str, TaskStrength] = {
    # Foreman tasks
    "coordinator": TaskStrength.COORDINATION,
    "health_check_review": TaskStrength.SEMANTIC_REASONING,
    "voice_calibration_guidance": TaskStrength.SEMANTIC_REASONING,
    "beat_structure_advice": TaskStrength.STRUCTURAL_PLANNING,
    "conflict_resolution": TaskStrength.SEMANTIC_REASONING,
    "scaffold_enrichment_decisions": TaskStrength.SEMANTIC_REASONING,
    "theme_analysis": TaskStrength.THEMATIC_ANALYSIS,
    "structural_planning": TaskStrength.STRUCTURAL_PLANNING,

    # Health check tasks
    "timeline_consistency": TaskStrength.NARRATIVE_CONTINUITY,
    "theme_resonance": TaskStrength.THEMATIC_ANALYSIS,
    "flaw_challenges": TaskStrength.CHARACTER_PSYCHOLOGY,
    "cast_function": TaskStrength.SEMANTIC_REASONING,
    "pacing_analysis": TaskStrength.STRUCTURAL_PLANNING,
    "beat_progress": TaskStrength.STRUCTURAL_PLANNING,
    "symbolic_layering": TaskStrength.THEMATIC_ANALYSIS,
}


def get_model_capabilities(model_id: str) -> Optional[ModelCapabilities]:
    """Get capabilities for a specific model.

    Args:
        model_id: Model identifier (e.g., "deepseek-chat", "gpt-4o")

    Returns:
        ModelCapabilities object or None if not found
    """
    for model in MODEL_REGISTRY:
        if model.model_id == model_id:
            return model
    return None


def get_models_with_strength(strength: TaskStrength) -> List[ModelCapabilities]:
    """Get all models that excel at a specific task strength.

    Args:
        strength: TaskStrength enum value

    Returns:
        List of ModelCapabilities that have this strength
    """
    return [model for model in MODEL_REGISTRY if strength in model.strengths]


def get_all_models() -> List[ModelCapabilities]:
    """Get complete model registry.

    Returns:
        List of all available models
    """
    return MODEL_REGISTRY.copy()
