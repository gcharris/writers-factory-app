"""
Model Orchestrator Service - Phase 3E

Intelligent model selection based on quality tiers, budgets, and task requirements.
Provides automatic model assignment to optimize for quality, cost, or balance.
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
    get_model_capabilities,
    get_models_with_strength
)

logger = logging.getLogger(__name__)


@dataclass
class SelectionCriteria:
    """Criteria for model selection."""
    task_type: str
    quality_tier: str  # "budget" | "balanced" | "premium"
    monthly_budget: Optional[float] = None  # USD per month
    current_month_spend: float = 0.0
    prefer_local: bool = False


class ModelOrchestrator:
    """Intelligent model selection based on quality tiers and budgets."""

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

        # Filter candidates by task strength
        candidates = [
            model for model in self.registry
            if required_strength in model.strengths
        ]

        if not candidates:
            # No models with this strength, use any semantic reasoning model
            logger.warning(f"No models found with strength {required_strength.value}, falling back to SEMANTIC_REASONING")
            candidates = get_models_with_strength(TaskStrength.SEMANTIC_REASONING)

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
        else:
            # Default to balanced
            logger.warning(f"Unknown quality tier '{criteria.quality_tier}', using balanced")
            selected = self._select_balanced(candidates, criteria)

        logger.debug(f"📊 Selected {selected} for {criteria.task_type} ({criteria.quality_tier} tier)")
        return selected

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

    def estimate_monthly_cost(
        self,
        quality_tier: str,
        estimated_monthly_usage: Dict[str, int]
    ) -> Dict[str, float]:
        """Estimate monthly cost for a quality tier.

        Args:
            quality_tier: "budget" | "balanced" | "premium"
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
                "premium": "claude-3-5-sonnet-20241022"
            }
        """
        recommendations = {}
        for tier in ["budget", "balanced", "premium"]:
            criteria = SelectionCriteria(task_type=task_type, quality_tier=tier)
            recommendations[tier] = self.select_model(criteria)
        return recommendations


# Global orchestrator instance
orchestrator = ModelOrchestrator()
