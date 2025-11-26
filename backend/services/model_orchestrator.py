"""
Model Orchestrator Service - Phase 3E.2

Intelligent model selection based on quality tiers, budgets, task requirements,
content maturity requirements, and language preferences.

Extended with:
- Content-aware routing (mature content → unfiltered models)
- Language-aware routing (French fiction → Mistral, Chinese → DeepSeek/Qwen)
- Creative style matching (literary → Claude, edgy → Grok)
"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

from backend.services.model_capabilities import (
    ModelCapabilities,
    MODEL_REGISTRY,
    TASK_STRENGTH_MAP,
    TaskStrength,
    ContentFilter,
    CreativeStyle,
    get_model_capabilities,
    get_models_with_strength,
    get_models_by_content_filter,
    get_models_for_language,
    get_models_by_style,
    get_best_model_for_content
)

logger = logging.getLogger(__name__)


@dataclass
class SelectionCriteria:
    """Criteria for model selection."""
    task_type: str
    quality_tier: str  # "budget" | "balanced" | "premium" | "opus"
    monthly_budget: Optional[float] = None  # USD per month
    current_month_spend: float = 0.0
    prefer_local: bool = False

    # === Extended Content-Aware Selection ===
    content_type: Optional[str] = None  # "dark_themes", "romance_explicit", etc.
    target_language: str = "en"  # ISO 639-1 code
    creative_style: Optional[str] = None  # "literary", "edgy", "commercial", etc.


class ModelOrchestrator:
    """Intelligent model selection based on quality tiers, content, and language."""

    def __init__(self):
        self.registry = MODEL_REGISTRY
        self.available_providers = self._detect_available_providers()
        logger.info(f"🎯 Model Orchestrator initialized. Available providers: {list(self.available_providers.keys())}")

    def _detect_available_providers(self) -> Dict[str, bool]:
        """Detect which cloud providers have API keys configured."""
        providers = {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "deepseek": bool(os.getenv("DEEPSEEK_API_KEY")),
            "qwen": bool(os.getenv("QWEN_API_KEY")),
            "kimi": bool(os.getenv("KIMI_API_KEY")),
            "zhipu": bool(os.getenv("ZHIPU_API_KEY")),
            "tencent": bool(os.getenv("TENCENT_API_KEY")),
            "mistral": bool(os.getenv("MISTRAL_API_KEY")),
            "xai": bool(os.getenv("XAI_API_KEY")),
            "google": bool(os.getenv("GEMINI_API_KEY")),
            "yandex": bool(os.getenv("YANDEX_API_KEY")),
        }

        # Log available providers
        available = [p for p, avail in providers.items() if avail]
        if available:
            logger.info(f"✓ Cloud providers available: {', '.join(available)}")
        else:
            logger.info("ℹ️ No cloud provider API keys detected, using local models only")

        return providers

    def select_model(self, criteria: SelectionCriteria) -> str:
        """Select optimal model based on criteria.

        Args:
            criteria: SelectionCriteria with task type, quality tier, budget, etc.

        Returns:
            model_id (str): The selected model ID
        """
        # Get required task strength
        required_strength = TASK_STRENGTH_MAP.get(criteria.task_type)
        if not required_strength:
            # Unknown task type, default to coordination
            required_strength = TaskStrength.COORDINATION
            logger.debug(f"Unknown task type '{criteria.task_type}', using COORDINATION strength")

        # Start with all models that have the required strength
        candidates = [
            model for model in self.registry
            if required_strength in model.strengths
        ]

        if not candidates:
            # No models with this strength, use any semantic reasoning model
            logger.warning(f"No models found with strength {required_strength.value}, falling back to SEMANTIC_REASONING")
            candidates = get_models_with_strength(TaskStrength.SEMANTIC_REASONING)

        # === Content-Aware Filtering ===
        if criteria.content_type:
            content_filtered = self._filter_by_content_type(candidates, criteria.content_type)
            if content_filtered:
                candidates = content_filtered
                logger.debug(f"📝 Filtered by content type '{criteria.content_type}': {len(candidates)} candidates")

        # === Language-Aware Filtering ===
        if criteria.target_language and criteria.target_language != "en":
            lang_filtered = self._filter_by_language(candidates, criteria.target_language)
            if lang_filtered:
                candidates = lang_filtered
                logger.debug(f"🌍 Filtered by language '{criteria.target_language}': {len(candidates)} candidates")

        # === Creative Style Filtering ===
        if criteria.creative_style:
            style_filtered = self._filter_by_style(candidates, criteria.creative_style)
            if style_filtered:
                candidates = style_filtered
                logger.debug(f"🎨 Filtered by style '{criteria.creative_style}': {len(candidates)} candidates")

        # Filter by API key availability
        candidates = [
            model for model in candidates
            if (model.local_only or
                not model.requires_api_key or
                self.available_providers.get(model.provider, False))
        ]

        if not candidates:
            logger.warning("No available models found, falling back to mistral")
            return "mistral"

        # Apply quality tier selection
        if criteria.quality_tier == "budget":
            selected = self._select_budget(candidates, criteria)
        elif criteria.quality_tier == "balanced":
            selected = self._select_balanced(candidates, criteria)
        elif criteria.quality_tier == "premium":
            selected = self._select_premium(candidates, criteria)
        elif criteria.quality_tier == "opus":
            selected = self._select_opus(candidates, criteria)
        else:
            # Default to balanced
            logger.warning(f"Unknown quality tier '{criteria.quality_tier}', using balanced")
            selected = self._select_balanced(candidates, criteria)

        logger.debug(f"📊 Selected {selected} for {criteria.task_type} ({criteria.quality_tier} tier)")
        return selected

    def _filter_by_content_type(
        self,
        candidates: List[ModelCapabilities],
        content_type: str
    ) -> List[ModelCapabilities]:
        """Filter models by content type requirements."""
        # Map content types to required filter levels
        content_filter_requirements = {
            "romance_explicit": ContentFilter.UNFILTERED,
            "violence_graphic": ContentFilter.UNFILTERED,
            "dark_themes": ContentFilter.PERMISSIVE,
            "mature_content": ContentFilter.PERMISSIVE,
            "thriller": ContentFilter.PERMISSIVE,
            "horror": ContentFilter.PERMISSIVE,
            "literary_fiction": ContentFilter.MODERATE,
            "general_fiction": ContentFilter.MODERATE,
            "young_adult": ContentFilter.STRICT,
            "children": ContentFilter.STRICT,
        }

        required_filter = content_filter_requirements.get(content_type, ContentFilter.MODERATE)

        # Filter models that meet the content filter requirement
        filter_order = [ContentFilter.STRICT, ContentFilter.MODERATE, ContentFilter.PERMISSIVE, ContentFilter.UNFILTERED]
        min_index = filter_order.index(required_filter)

        return [
            model for model in candidates
            if filter_order.index(model.content_filter) >= min_index
        ]

    def _filter_by_language(
        self,
        candidates: List[ModelCapabilities],
        language_code: str
    ) -> List[ModelCapabilities]:
        """Filter models by language support quality."""
        # Return models that support the language with good quality
        return [
            model for model in candidates
            if language_code in model.primary_languages and model.multilingual_quality >= 7
        ]

    def _filter_by_style(
        self,
        candidates: List[ModelCapabilities],
        style: str
    ) -> List[ModelCapabilities]:
        """Filter models by creative style."""
        try:
            creative_style = CreativeStyle(style)
            return [
                model for model in candidates
                if creative_style in model.creative_styles
            ]
        except ValueError:
            # Unknown style, don't filter
            logger.warning(f"Unknown creative style '{style}', skipping style filter")
            return candidates

    def _select_budget(self, candidates: List[ModelCapabilities], criteria: SelectionCriteria) -> str:
        """Select cheapest model that meets minimum quality (score >= 6)."""
        # Filter by minimum quality
        candidates = [m for m in candidates if m.quality_score >= 6]

        if not candidates:
            logger.warning("No budget candidates with quality >= 6, falling back to mistral")
            return "mistral"

        # Prefer local models (free)
        local_models = [m for m in candidates if m.local_only]
        if local_models:
            # Pick highest quality local model
            best_local = max(local_models, key=lambda m: m.quality_score)
            logger.debug(f"💰 Budget tier: selected free local model {best_local.model_id}")
            return best_local.model_id

        # Otherwise pick cheapest cloud model
        cheapest = min(candidates, key=lambda m: m.cost_per_1m_input)
        logger.debug(f"💰 Budget tier: selected cheapest cloud model {cheapest.model_id} (${cheapest.cost_per_1m_input}/1M)")
        return cheapest.model_id

    def _select_balanced(self, candidates: List[ModelCapabilities], criteria: SelectionCriteria) -> str:
        """Select model with best quality-to-cost ratio."""
        if not candidates:
            return "mistral"

        # Check monthly budget constraint
        if criteria.monthly_budget is not None:
            remaining_budget = criteria.monthly_budget - criteria.current_month_spend
            if remaining_budget <= 0:
                # Budget exhausted, use free local model
                logger.warning(f"⚠️ Monthly budget exhausted (${criteria.current_month_spend}/${criteria.monthly_budget}), using local model")
                local_models = [m for m in candidates if m.local_only]
                if local_models:
                    best_local = max(local_models, key=lambda m: m.quality_score)
                    return best_local.model_id
                return "mistral"

        # Calculate quality per dollar (higher is better)
        def value_score(model: ModelCapabilities) -> float:
            if model.local_only:
                return 1000.0  # Local models have infinite value

            # Estimate average cost (input + output weighted)
            avg_cost = (model.cost_per_1m_input * 0.7 + model.cost_per_1m_output * 0.3)
            if avg_cost == 0:
                return 1000.0

            return model.quality_score / avg_cost

        # Prefer local if criteria says so and quality is similar
        if criteria.prefer_local:
            local_models = [m for m in candidates if m.local_only]
            cloud_models = [m for m in candidates if not m.local_only]

            if local_models and cloud_models:
                best_local = max(local_models, key=lambda m: m.quality_score)
                best_cloud = max(cloud_models, key=value_score)

                # If local quality is within 1 point of cloud, prefer local
                if best_local.quality_score >= best_cloud.quality_score - 1:
                    logger.debug(f"⚖️ Balanced tier: prefer_local enabled, using {best_local.model_id}")
                    return best_local.model_id

        best = max(candidates, key=value_score)
        logger.debug(f"⚖️ Balanced tier: selected {best.model_id} (quality {best.quality_score}, value score {value_score(best):.2f})")
        return best.model_id

    def _select_premium(self, candidates: List[ModelCapabilities], criteria: SelectionCriteria) -> str:
        """Select highest quality model regardless of cost."""
        if not candidates:
            return "mistral"

        # Filter to cloud models if available (usually higher quality)
        cloud_models = [m for m in candidates if not m.local_only]
        if cloud_models:
            best = max(cloud_models, key=lambda m: m.quality_score)
            logger.debug(f"💎 Premium tier: selected {best.model_id} (quality {best.quality_score})")
            return best.model_id

        # Otherwise pick best local model
        best_local = max(candidates, key=lambda m: m.quality_score)
        logger.debug(f"💎 Premium tier: no cloud models available, using best local {best_local.model_id}")
        return best_local.model_id

    def _select_opus(self, candidates: List[ModelCapabilities], criteria: SelectionCriteria) -> str:
        """Select absolute highest quality model (Opus tier)."""
        if not candidates:
            return "mistral"

        # Try to find Opus-tier models first
        opus_models = [m for m in candidates if "opus" in m.model_id.lower()]
        if opus_models:
            best = max(opus_models, key=lambda m: m.quality_score)
            logger.debug(f"🏆 Opus tier: selected {best.model_id} (quality {best.quality_score})")
            return best.model_id

        # Fall back to premium selection
        return self._select_premium(candidates, criteria)

    def select_model_for_content(
        self,
        task_type: str,
        content_type: str,
        language: str = "en",
        quality_tier: str = "balanced"
    ) -> str:
        """Convenience method for content-aware model selection.

        Args:
            task_type: Task type (e.g., "scene_generation")
            content_type: Content type (e.g., "dark_themes", "romance_explicit")
            language: Target language (ISO 639-1 code)
            quality_tier: Quality tier

        Returns:
            model_id (str): Selected model
        """
        criteria = SelectionCriteria(
            task_type=task_type,
            quality_tier=quality_tier,
            content_type=content_type,
            target_language=language
        )
        return self.select_model(criteria)

    def get_best_models_for_language(self, language_code: str) -> Dict[str, str]:
        """Get recommended models for a specific language.

        Args:
            language_code: ISO 639-1 code (e.g., "fr", "ru", "zh")

        Returns:
            Dict with model recommendations by use case
        """
        recommendations = {
            "strategic": None,
            "creative": None,
            "dialogue": None,
            "analysis": None
        }

        # Language-specific recommendations
        if language_code == "fr":
            # French - Mistral is best
            recommendations = {
                "strategic": "mistral-large-latest",
                "creative": "mistral-large-latest",
                "dialogue": "claude-3-7-sonnet-20250219",
                "analysis": "gpt-4o"
            }
        elif language_code == "ru":
            # Russian - YandexGPT 5.1 Pro is best for native cultural fluency, Qwen 3 for open alternative
            recommendations = {
                "strategic": "qwen-max",  # Qwen 3 excellent for Russian analysis
                "creative": "yandexgpt-5.1-pro",  # Best Russian prose quality
                "dialogue": "yandexgpt-5.1-pro",  # Native Russian dialogue
                "analysis": "gpt-4o"      # Strong general analysis
            }
        elif language_code == "zh":
            # Chinese
            recommendations = {
                "strategic": "deepseek-chat",
                "creative": "moonshot-v1-128k",
                "dialogue": "qwen-plus",
                "analysis": "deepseek-chat"
            }
        elif language_code == "de":
            # German
            recommendations = {
                "strategic": "mistral-large-latest",
                "creative": "claude-3-7-sonnet-20250219",
                "dialogue": "gpt-4o",
                "analysis": "gpt-4o"
            }
        elif language_code == "es":
            # Spanish
            recommendations = {
                "strategic": "gpt-4o",
                "creative": "claude-3-7-sonnet-20250219",
                "dialogue": "gpt-4o",
                "analysis": "gpt-4o"
            }
        else:
            # Default English
            recommendations = {
                "strategic": "deepseek-chat",
                "creative": "claude-3-7-sonnet-20250219",
                "dialogue": "gpt-4o",
                "analysis": "deepseek-chat"
            }

        # Filter by availability
        for use_case, model_id in recommendations.items():
            if model_id:
                model = get_model_capabilities(model_id)
                if model and not self._is_model_available(model):
                    # Fall back to first available model for the language
                    available = get_models_for_language(language_code, min_quality=7)
                    available = [m for m in available if self._is_model_available(m)]
                    if available:
                        recommendations[use_case] = available[0].model_id
                    else:
                        recommendations[use_case] = "mistral"  # Ultimate fallback

        return recommendations

    def _is_model_available(self, model: ModelCapabilities) -> bool:
        """Check if a model is available (has API key or is local)."""
        if model.local_only:
            return True
        if not model.requires_api_key:
            return True
        return self.available_providers.get(model.provider, False)

    def estimate_monthly_cost(
        self,
        quality_tier: str,
        estimated_monthly_usage: Dict[str, int]
    ) -> Dict[str, float]:
        """Estimate monthly cost for a quality tier.

        Args:
            quality_tier: "budget" | "balanced" | "premium" | "opus"
            estimated_monthly_usage: Dict mapping task_type to number of calls per month

        Returns:
            Dict with cost breakdown:
            {
                "total_cost": 5.50,
                "by_task": {"health_check_review": 2.30, "theme_analysis": 1.20, ...},
                "by_model": {"deepseek-chat": 3.50, "gpt-4o": 2.00}
            }
        """
        cost_by_task = {}
        cost_by_model = {}

        for task_type, num_calls in estimated_monthly_usage.items():
            # Select model for this task
            criteria = SelectionCriteria(
                task_type=task_type,
                quality_tier=quality_tier
            )
            model_id = self.select_model(criteria)

            # Get model capabilities
            model = get_model_capabilities(model_id)
            if not model:
                continue

            # Estimate tokens per call (conservative estimates)
            avg_input_tokens = 2000  # System prompt + user message
            avg_output_tokens = 500

            # Calculate cost
            task_cost = (
                (avg_input_tokens / 1_000_000) * model.cost_per_1m_input * num_calls +
                (avg_output_tokens / 1_000_000) * model.cost_per_1m_output * num_calls
            )

            cost_by_task[task_type] = round(task_cost, 2)
            cost_by_model[model_id] = cost_by_model.get(model_id, 0) + task_cost

        return {
            "total_cost": round(sum(cost_by_task.values()), 2),
            "by_task": cost_by_task,
            "by_model": {k: round(v, 2) for k, v in cost_by_model.items()}
        }

    def get_model_recommendations(self, task_type: str) -> Dict[str, str]:
        """Get recommended models for a task across all quality tiers.

        Args:
            task_type: Task type (e.g., "health_check_review")

        Returns:
            {
                "budget": "mistral",
                "balanced": "deepseek-chat",
                "premium": "claude-3-7-sonnet-20250219",
                "opus": "claude-3-opus-20240229"
            }
        """
        recommendations = {}
        for tier in ["budget", "balanced", "premium", "opus"]:
            criteria = SelectionCriteria(task_type=task_type, quality_tier=tier)
            recommendations[tier] = self.select_model(criteria)
        return recommendations

    def get_unfiltered_models(self) -> List[str]:
        """Get list of models suitable for mature/unfiltered content.

        Returns:
            List of model IDs with unfiltered or permissive content handling
        """
        unfiltered = get_models_by_content_filter(ContentFilter.UNFILTERED)
        permissive = get_models_by_content_filter(ContentFilter.PERMISSIVE)

        # Combine and filter by availability
        all_models = {m.model_id for m in unfiltered + permissive}
        available = [
            model_id for model_id in all_models
            if self._is_model_available(get_model_capabilities(model_id))
        ]

        return sorted(available)


# Global orchestrator instance
orchestrator = ModelOrchestrator()
