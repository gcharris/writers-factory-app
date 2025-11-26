"""
Model Capabilities Registry - Phase 3E.2

Defines the capabilities, costs, and strengths of all available AI models
to enable intelligent model selection by the orchestrator.

Extended with:
- Content maturity tags (unfiltered, mature_ok, etc.)
- Language specialization (multilingual support for French, Russian, etc.)
- Creative style tags (prose-first, edgy, literary, etc.)
- 13 providers: OpenAI, Anthropic, DeepSeek, Qwen, Kimi, Zhipu, Tencent, Mistral, xAI, Google, Yandex, Ollama
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class TaskStrength(Enum):
    """Task categories that models excel at."""
    NARRATIVE_CONTINUITY = "narrative_continuity"      # Timeline consistency
    THEMATIC_ANALYSIS = "thematic_analysis"            # Theme resonance
    CHARACTER_PSYCHOLOGY = "character_psychology"      # Flaw challenges
    STRUCTURAL_PLANNING = "structural_planning"        # Beat structure
    COORDINATION = "coordination"                      # Simple coordination
    SEMANTIC_REASONING = "semantic_reasoning"          # General reasoning
    CREATIVE_WRITING = "creative_writing"              # Scene generation
    DIALOGUE_GENERATION = "dialogue_generation"        # Natural dialogue
    ACTION_SEQUENCES = "action_sequences"              # Fast-paced action
    ATMOSPHERIC_PROSE = "atmospheric_prose"            # Mood and setting


class ContentFilter(Enum):
    """Content filtering level for mature content handling."""
    STRICT = "strict"          # Heavy filtering (Claude, GPT default)
    MODERATE = "moderate"      # Some flexibility
    PERMISSIVE = "permissive"  # Minimal filtering (DeepSeek, Qwen)
    UNFILTERED = "unfiltered"  # No filtering (Grok, local models)


class CreativeStyle(Enum):
    """Creative writing style specializations."""
    PROSE_FIRST = "prose_first"            # Beautiful prose priority
    PLOT_DRIVEN = "plot_driven"            # Story structure priority
    DIALOGUE_FOCUSED = "dialogue_focused"  # Natural conversation
    LITERARY = "literary"                  # Literary fiction style
    COMMERCIAL = "commercial"              # Genre/commercial style
    EDGY = "edgy"                          # Dark/unconventional themes
    EMOTIONAL = "emotional"                # Character interiority
    ANALYTICAL = "analytical"              # Logical/systematic


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

    # === Extended Capability Tags ===

    # Content handling
    content_filter: ContentFilter = ContentFilter.MODERATE

    # Creative style specializations
    creative_styles: List[CreativeStyle] = field(default_factory=list)

    # Language support (ISO 639-1 codes)
    # "en" = English, "fr" = French, "ru" = Russian, "zh" = Chinese, etc.
    primary_languages: List[str] = field(default_factory=lambda: ["en"])
    multilingual_quality: int = 5  # 0-10 for non-English writing quality

    # Best use cases (descriptive tags)
    best_for: List[str] = field(default_factory=list)

    # Context window (useful for long-form writing)
    max_context_tokens: int = 8192


# Model registry with complete capability profiles
MODEL_REGISTRY: List[ModelCapabilities] = [
    # ============================================================
    # LOCAL MODELS (Free, Privacy-Focused)
    # ============================================================
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
        local_only=True,
        content_filter=ContentFilter.UNFILTERED,
        creative_styles=[CreativeStyle.PLOT_DRIVEN],
        primary_languages=["en", "fr", "de", "es"],
        multilingual_quality=6,
        best_for=["coordination", "quick_drafts", "local_privacy"],
        max_context_tokens=32768
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
        local_only=True,
        content_filter=ContentFilter.UNFILTERED,
        creative_styles=[CreativeStyle.COMMERCIAL],
        primary_languages=["en", "es", "pt"],
        multilingual_quality=5,
        best_for=["brainstorming", "character_checks", "prototyping"],
        max_context_tokens=128000
    ),

    # ============================================================
    # BUDGET CLOUD MODELS (Cost-Effective)
    # ============================================================
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
        quality_score=9,
        speed="medium",
        cost_per_1m_input=0.27,
        cost_per_1m_output=1.10,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="DEEPSEEK_API_KEY",
        content_filter=ContentFilter.PERMISSIVE,
        creative_styles=[CreativeStyle.ANALYTICAL, CreativeStyle.PLOT_DRIVEN],
        primary_languages=["en", "zh"],
        multilingual_quality=9,  # Excellent Chinese
        best_for=["strategic_analysis", "plot_structure", "dark_themes", "mature_content"],
        max_context_tokens=64000
    ),

    ModelCapabilities(
        model_id="qwen-plus",
        provider="qwen",
        display_name="Qwen Plus",
        strengths=[
            TaskStrength.COORDINATION,
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CREATIVE_WRITING
        ],
        quality_score=7,
        speed="fast",
        cost_per_1m_input=0.40,
        cost_per_1m_output=1.20,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="QWEN_API_KEY",
        content_filter=ContentFilter.PERMISSIVE,
        creative_styles=[CreativeStyle.COMMERCIAL, CreativeStyle.DIALOGUE_FOCUSED],
        primary_languages=["en", "zh", "ar"],
        multilingual_quality=9,  # Excellent Chinese, Arabic
        best_for=["world_building", "cultural_nuance", "multilingual_fiction"],
        max_context_tokens=32000
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
        api_key_env_var="QWEN_API_KEY",
        content_filter=ContentFilter.PERMISSIVE,
        creative_styles=[CreativeStyle.COMMERCIAL],
        primary_languages=["en", "zh"],
        multilingual_quality=8,
        best_for=["fast_iteration", "draft_summaries"],
        max_context_tokens=8000
    ),

    # Qwen 3 Models (Latest generation - excellent Russian!)
    ModelCapabilities(
        model_id="qwen-max",
        provider="qwen",
        display_name="Qwen Max (Qwen 3)",
        strengths=[
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.THEMATIC_ANALYSIS,
            TaskStrength.CHARACTER_PSYCHOLOGY
        ],
        quality_score=9,
        speed="medium",
        cost_per_1m_input=1.60,
        cost_per_1m_output=6.40,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="QWEN_API_KEY",
        content_filter=ContentFilter.PERMISSIVE,
        creative_styles=[CreativeStyle.LITERARY, CreativeStyle.PROSE_FIRST, CreativeStyle.EMOTIONAL],
        primary_languages=["en", "zh", "ru", "fr", "de", "es", "ar", "ja", "ko"],
        multilingual_quality=10,  # Top-tier multilingual, excellent Russian!
        best_for=["literary_fiction", "multilingual_writing", "russian_fiction", "complex_narratives"],
        max_context_tokens=32000
    ),

    ModelCapabilities(
        model_id="qwen-turbo-latest",
        provider="qwen",
        display_name="Qwen Turbo Latest (Qwen 3)",
        strengths=[
            TaskStrength.COORDINATION,
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CREATIVE_WRITING
        ],
        quality_score=8,
        speed="very_fast",
        cost_per_1m_input=0.30,
        cost_per_1m_output=0.60,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="QWEN_API_KEY",
        content_filter=ContentFilter.PERMISSIVE,
        creative_styles=[CreativeStyle.COMMERCIAL, CreativeStyle.PLOT_DRIVEN],
        primary_languages=["en", "zh", "ru", "fr", "de", "es"],
        multilingual_quality=9,  # Strong multilingual including Russian
        best_for=["fast_drafts", "russian_dialogue", "multilingual_iteration"],
        max_context_tokens=1000000  # 1M context!
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
        api_key_env_var="OPENAI_API_KEY",
        content_filter=ContentFilter.MODERATE,
        creative_styles=[CreativeStyle.COMMERCIAL],
        primary_languages=["en", "fr", "de", "es", "ru"],
        multilingual_quality=7,
        best_for=["quick_analysis", "draft_reviews"],
        max_context_tokens=128000
    ),

    ModelCapabilities(
        model_id="gpt-3.5-turbo",
        provider="openai",
        display_name="GPT-3.5 Turbo",
        strengths=[TaskStrength.COORDINATION, TaskStrength.DIALOGUE_GENERATION],
        quality_score=7,
        speed="very_fast",
        cost_per_1m_input=0.50,
        cost_per_1m_output=1.50,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="OPENAI_API_KEY",
        content_filter=ContentFilter.MODERATE,
        creative_styles=[CreativeStyle.COMMERCIAL, CreativeStyle.DIALOGUE_FOCUSED],
        primary_languages=["en", "fr", "de", "es"],
        multilingual_quality=6,
        best_for=["conversational", "simple_creative", "fast_dialogue", "casual_tone"],
        max_context_tokens=16385
    ),

    ModelCapabilities(
        model_id="gemini-2.0-flash-exp",
        provider="google",
        display_name="Gemini 2.0 Flash",
        strengths=[
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.COORDINATION,
            TaskStrength.THEMATIC_ANALYSIS
        ],
        quality_score=8,
        speed="very_fast",
        cost_per_1m_input=0.075,
        cost_per_1m_output=0.30,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="GEMINI_API_KEY",
        content_filter=ContentFilter.MODERATE,
        creative_styles=[CreativeStyle.ANALYTICAL, CreativeStyle.COMMERCIAL],
        primary_languages=["en", "fr", "de", "es", "ja", "ko"],
        multilingual_quality=8,
        best_for=["research", "fact_checking", "long_context"],
        max_context_tokens=1000000  # 1M context!
    ),

    # === Chinese AI Models (Excellent for Multilingual) ===
    ModelCapabilities(
        model_id="moonshot-v1-128k",
        provider="kimi",
        display_name="Moonshot Kimi",
        strengths=[
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.NARRATIVE_CONTINUITY,
            TaskStrength.CREATIVE_WRITING
        ],
        quality_score=8,
        speed="medium",
        cost_per_1m_input=0.80,
        cost_per_1m_output=0.80,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="KIMI_API_KEY",
        content_filter=ContentFilter.PERMISSIVE,
        creative_styles=[CreativeStyle.LITERARY, CreativeStyle.EMOTIONAL],
        primary_languages=["en", "zh"],
        multilingual_quality=9,  # Excellent long-form Chinese
        best_for=["long_form_fiction", "character_arcs", "cultural_narratives"],
        max_context_tokens=128000
    ),

    ModelCapabilities(
        model_id="glm-4",
        provider="zhipu",
        display_name="Zhipu GLM-4",
        strengths=[
            TaskStrength.STRUCTURAL_PLANNING,
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CHARACTER_PSYCHOLOGY
        ],
        quality_score=7,
        speed="fast",
        cost_per_1m_input=0.50,
        cost_per_1m_output=0.50,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="ZHIPU_API_KEY",
        content_filter=ContentFilter.MODERATE,
        creative_styles=[CreativeStyle.PLOT_DRIVEN, CreativeStyle.ANALYTICAL],
        primary_languages=["en", "zh"],
        multilingual_quality=9,
        best_for=["plot_twists", "strategic_plotting", "structure_analysis"],
        max_context_tokens=128000
    ),

    ModelCapabilities(
        model_id="hunyuan-lite",
        provider="tencent",
        display_name="Tencent Hunyuan",
        strengths=[
            TaskStrength.COORDINATION,
            TaskStrength.DIALOGUE_GENERATION,
            TaskStrength.CREATIVE_WRITING
        ],
        quality_score=7,
        speed="fast",
        cost_per_1m_input=0.10,
        cost_per_1m_output=0.10,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="TENCENT_API_KEY",
        content_filter=ContentFilter.PERMISSIVE,
        creative_styles=[CreativeStyle.DIALOGUE_FOCUSED, CreativeStyle.COMMERCIAL],
        primary_languages=["en", "zh"],
        multilingual_quality=9,
        best_for=["dialogue", "character_voice", "casual_style"],
        max_context_tokens=32000
    ),

    # ============================================================
    # PREMIUM CLOUD MODELS (Maximum Quality)
    # ============================================================
    ModelCapabilities(
        model_id="claude-3-5-sonnet-20241022",
        provider="anthropic",
        display_name="Claude 3.5 Sonnet",
        strengths=[
            TaskStrength.NARRATIVE_CONTINUITY,
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.THEMATIC_ANALYSIS,
            TaskStrength.ATMOSPHERIC_PROSE
        ],
        quality_score=10,
        speed="medium",
        cost_per_1m_input=3.00,
        cost_per_1m_output=15.00,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="ANTHROPIC_API_KEY",
        content_filter=ContentFilter.STRICT,
        creative_styles=[CreativeStyle.PROSE_FIRST, CreativeStyle.LITERARY, CreativeStyle.EMOTIONAL],
        primary_languages=["en", "fr", "de", "es"],
        multilingual_quality=8,
        best_for=["prose_quality", "emotional_depth", "internal_monologue", "nuance"],
        max_context_tokens=200000
    ),

    ModelCapabilities(
        model_id="claude-3-7-sonnet-20250219",
        provider="anthropic",
        display_name="Claude Sonnet 4",
        strengths=[
            TaskStrength.NARRATIVE_CONTINUITY,
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.THEMATIC_ANALYSIS,
            TaskStrength.ATMOSPHERIC_PROSE,
            TaskStrength.CHARACTER_PSYCHOLOGY
        ],
        quality_score=10,
        speed="medium",
        cost_per_1m_input=3.00,
        cost_per_1m_output=15.00,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="ANTHROPIC_API_KEY",
        content_filter=ContentFilter.MODERATE,  # Slightly more flexible
        creative_styles=[CreativeStyle.PROSE_FIRST, CreativeStyle.LITERARY, CreativeStyle.EMOTIONAL],
        primary_languages=["en", "fr", "de", "es", "ru"],
        multilingual_quality=8,
        best_for=["prose_quality", "emotional_depth", "character_interiority", "literary_fiction"],
        max_context_tokens=200000
    ),

    ModelCapabilities(
        model_id="gpt-4o",
        provider="openai",
        display_name="GPT-4o",
        strengths=[
            TaskStrength.THEMATIC_ANALYSIS,
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.STRUCTURAL_PLANNING,
            TaskStrength.DIALOGUE_GENERATION
        ],
        quality_score=10,
        speed="fast",
        cost_per_1m_input=2.50,
        cost_per_1m_output=10.00,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="OPENAI_API_KEY",
        content_filter=ContentFilter.MODERATE,
        creative_styles=[CreativeStyle.COMMERCIAL, CreativeStyle.PLOT_DRIVEN, CreativeStyle.DIALOGUE_FOCUSED],
        primary_languages=["en", "fr", "de", "es", "ru", "ja"],
        multilingual_quality=8,
        best_for=["thematic_analysis", "dialogue", "structure", "genre_fiction"],
        max_context_tokens=128000
    ),

    ModelCapabilities(
        model_id="grok-2-latest",
        provider="xai",
        display_name="Grok 2",
        strengths=[
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.DIALOGUE_GENERATION,
            TaskStrength.ACTION_SEQUENCES,
            TaskStrength.CHARACTER_PSYCHOLOGY
        ],
        quality_score=9,
        speed="fast",
        cost_per_1m_input=2.00,
        cost_per_1m_output=10.00,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="XAI_API_KEY",
        content_filter=ContentFilter.UNFILTERED,  # Key differentiator!
        creative_styles=[CreativeStyle.EDGY, CreativeStyle.COMMERCIAL, CreativeStyle.DIALOGUE_FOCUSED],
        primary_languages=["en"],
        multilingual_quality=5,
        best_for=["mature_content", "dark_themes", "edgy_voice", "unconventional", "action"],
        max_context_tokens=131072
    ),

    ModelCapabilities(
        model_id="mistral-large-latest",
        provider="mistral",
        display_name="Mistral Large",
        strengths=[
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.ATMOSPHERIC_PROSE,
            TaskStrength.THEMATIC_ANALYSIS,
            TaskStrength.DIALOGUE_GENERATION
        ],
        quality_score=9,
        speed="medium",
        cost_per_1m_input=2.00,
        cost_per_1m_output=6.00,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="MISTRAL_API_KEY",
        content_filter=ContentFilter.PERMISSIVE,
        creative_styles=[CreativeStyle.LITERARY, CreativeStyle.PROSE_FIRST],
        primary_languages=["en", "fr", "de", "es", "it"],
        multilingual_quality=10,  # Best for French!
        best_for=["french_fiction", "european_style", "prose_polish", "literary_voice"],
        max_context_tokens=128000
    ),

    # ============================================================
    # RUSSIAN TIER (Russian-Native Models via Yandex AI Studio)
    # ============================================================
    ModelCapabilities(
        model_id="yandexgpt-5.1-pro",
        provider="yandex",
        display_name="YandexGPT 5.1 Pro",
        strengths=[
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.DIALOGUE_GENERATION,
            TaskStrength.ATMOSPHERIC_PROSE,
            TaskStrength.CHARACTER_PSYCHOLOGY,
            TaskStrength.NARRATIVE_CONTINUITY
        ],
        quality_score=9,
        speed="medium",
        cost_per_1m_input=1.20,  # Approximate based on Yandex pricing
        cost_per_1m_output=2.40,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="YANDEX_API_KEY",
        content_filter=ContentFilter.MODERATE,
        creative_styles=[CreativeStyle.LITERARY, CreativeStyle.EMOTIONAL, CreativeStyle.PROSE_FIRST],
        primary_languages=["ru", "en"],
        multilingual_quality=10,  # Best for Russian! Native cultural fluency
        best_for=["russian_fiction", "russian_dialogue", "russian_cultural_nuance", "slavic_literature"],
        max_context_tokens=32000
    ),

    ModelCapabilities(
        model_id="yandexgpt-5-lite",
        provider="yandex",
        display_name="YandexGPT 5 Lite",
        strengths=[
            TaskStrength.COORDINATION,
            TaskStrength.DIALOGUE_GENERATION,
            TaskStrength.CREATIVE_WRITING
        ],
        quality_score=7,
        speed="very_fast",
        cost_per_1m_input=0.20,  # Budget tier
        cost_per_1m_output=0.40,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="YANDEX_API_KEY",
        content_filter=ContentFilter.MODERATE,
        creative_styles=[CreativeStyle.COMMERCIAL, CreativeStyle.DIALOGUE_FOCUSED],
        primary_languages=["ru", "en"],
        multilingual_quality=9,  # Excellent Russian
        best_for=["russian_drafts", "fast_russian_iteration", "russian_dialogue"],
        max_context_tokens=8000
    ),

    # ============================================================
    # OPUS TIER (Maximum Quality, High Cost)
    # ============================================================
    ModelCapabilities(
        model_id="claude-3-opus-20240229",
        provider="anthropic",
        display_name="Claude 3 Opus",
        strengths=[
            TaskStrength.NARRATIVE_CONTINUITY,
            TaskStrength.SEMANTIC_REASONING,
            TaskStrength.CREATIVE_WRITING,
            TaskStrength.THEMATIC_ANALYSIS,
            TaskStrength.ATMOSPHERIC_PROSE,
            TaskStrength.CHARACTER_PSYCHOLOGY
        ],
        quality_score=10,
        speed="slow",
        cost_per_1m_input=15.00,
        cost_per_1m_output=75.00,
        requires_api_key=True,
        local_only=False,
        api_key_env_var="ANTHROPIC_API_KEY",
        content_filter=ContentFilter.STRICT,
        creative_styles=[CreativeStyle.LITERARY, CreativeStyle.PROSE_FIRST, CreativeStyle.EMOTIONAL],
        primary_languages=["en", "fr", "de", "es"],
        multilingual_quality=9,
        best_for=["literary_masterwork", "complex_themes", "nuanced_character", "prize_worthy_prose"],
        max_context_tokens=200000
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

    # Creative writing tasks
    "scene_generation": TaskStrength.CREATIVE_WRITING,
    "dialogue_writing": TaskStrength.DIALOGUE_GENERATION,
    "action_scene": TaskStrength.ACTION_SEQUENCES,
    "atmospheric_description": TaskStrength.ATMOSPHERIC_PROSE,
}


# Content type to recommended filter mapping (for dynamic routing)
CONTENT_FILTER_RECOMMENDATIONS: Dict[str, ContentFilter] = {
    "romance_explicit": ContentFilter.UNFILTERED,
    "violence_graphic": ContentFilter.UNFILTERED,
    "dark_themes": ContentFilter.PERMISSIVE,
    "thriller": ContentFilter.PERMISSIVE,
    "literary_fiction": ContentFilter.MODERATE,
    "young_adult": ContentFilter.STRICT,
    "children": ContentFilter.STRICT,
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


def get_models_by_content_filter(filter_level: ContentFilter) -> List[ModelCapabilities]:
    """Get models with specified content filter or more permissive.

    Args:
        filter_level: Minimum permissiveness required

    Returns:
        List of ModelCapabilities that meet the filter requirement
    """
    # Order from most to least restrictive
    filter_order = [ContentFilter.STRICT, ContentFilter.MODERATE, ContentFilter.PERMISSIVE, ContentFilter.UNFILTERED]
    min_index = filter_order.index(filter_level)

    return [
        model for model in MODEL_REGISTRY
        if filter_order.index(model.content_filter) >= min_index
    ]


def get_models_for_language(language_code: str, min_quality: int = 7) -> List[ModelCapabilities]:
    """Get models that support a specific language with good quality.

    Args:
        language_code: ISO 639-1 language code (e.g., "fr", "ru", "zh")
        min_quality: Minimum multilingual quality score (0-10)

    Returns:
        List of ModelCapabilities that support the language well
    """
    return [
        model for model in MODEL_REGISTRY
        if language_code in model.primary_languages and model.multilingual_quality >= min_quality
    ]


def get_models_by_style(style: CreativeStyle) -> List[ModelCapabilities]:
    """Get models that excel at a specific creative style.

    Args:
        style: CreativeStyle enum value

    Returns:
        List of ModelCapabilities that have this style
    """
    return [model for model in MODEL_REGISTRY if style in model.creative_styles]


def get_all_models() -> List[ModelCapabilities]:
    """Get complete model registry.

    Returns:
        List of all available models
    """
    return MODEL_REGISTRY.copy()


def get_best_model_for_content(
    content_type: str,
    language: str = "en",
    prefer_quality: bool = True
) -> Optional[ModelCapabilities]:
    """Get the best model for specific content requirements.

    Args:
        content_type: Type of content (e.g., "dark_themes", "romance_explicit")
        language: Target language (ISO 639-1 code)
        prefer_quality: If True, prioritize quality over cost

    Returns:
        Best matching ModelCapabilities or None
    """
    # Get recommended filter level
    filter_level = CONTENT_FILTER_RECOMMENDATIONS.get(content_type, ContentFilter.MODERATE)

    # Filter by content filter
    candidates = get_models_by_content_filter(filter_level)

    # Filter by language
    if language != "en":
        candidates = [m for m in candidates if language in m.primary_languages and m.multilingual_quality >= 7]

    if not candidates:
        return None

    # Sort by quality or cost
    if prefer_quality:
        candidates.sort(key=lambda m: m.quality_score, reverse=True)
    else:
        candidates.sort(key=lambda m: m.cost_per_1m_output)

    return candidates[0]
