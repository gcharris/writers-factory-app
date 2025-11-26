"""
Squad Service - Manages squad presets and intelligent model selection.

The Squad system simplifies model configuration into three choices:
1. Local Squad - Free, offline, privacy-focused
2. Hybrid Squad - Best value, course default
3. Pro Squad - Premium quality, BYOK

This service handles:
- Loading and validating squad presets
- Detecting available squads based on hardware + API keys
- Applying squad configuration to project settings
- Tournament model recommendations
- Smart recommendations from voice tournament results
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class SquadRequirements:
    """Requirements to use a squad."""
    ollama_required: bool
    min_ram_gb: int
    api_keys: List[str]
    optional_api_keys: List[str]


@dataclass
class SquadCostEstimate:
    """Cost estimates for a squad."""
    weekly_usd: float
    monthly_usd: float


class SquadService:
    """
    Manages squad presets and intelligent model selection.

    Usage:
        squad_service = SquadService(settings_service, hardware_service)

        # Get available squads
        squads = squad_service.get_available_squads()

        # Apply a squad
        squad_service.apply_squad("hybrid")

        # Get tournament models
        models = squad_service.get_tournament_models()
    """

    def __init__(
        self,
        settings_service: Any,
        hardware_service: Any,
        presets_path: str = None
    ):
        """
        Initialize Squad Service.

        Args:
            settings_service: SettingsService instance for reading/writing settings
            hardware_service: HardwareService instance for hardware detection
            presets_path: Path to squad_presets.json (auto-detected if None)
        """
        self.settings = settings_service
        self.hardware = hardware_service

        # Find presets file
        if presets_path is None:
            # Try common locations
            possible_paths = [
                Path(__file__).parent.parent / "config" / "squad_presets.json",
                Path("backend/config/squad_presets.json"),
                Path("config/squad_presets.json"),
            ]
            for path in possible_paths:
                if path.exists():
                    presets_path = str(path)
                    break

        if presets_path is None:
            raise FileNotFoundError("Could not find squad_presets.json")

        self.presets_path = presets_path
        self._presets = None  # Lazy load
        self._model_tiers = None
        self._model_metadata = None

    @property
    def presets(self) -> Dict:
        """Lazy load presets from JSON."""
        if self._presets is None:
            self._load_presets()
        return self._presets

    @property
    def model_tiers(self) -> Dict[str, List[str]]:
        """Model tier classifications."""
        if self._model_tiers is None:
            self._load_presets()
        return self._model_tiers

    @property
    def model_metadata(self) -> Dict[str, Dict]:
        """Model metadata (names, costs, descriptions)."""
        if self._model_metadata is None:
            self._load_presets()
        return self._model_metadata

    def _load_presets(self):
        """Load squad presets from JSON configuration."""
        with open(self.presets_path, 'r') as f:
            data = json.load(f)

        self._presets = data.get("presets", {})
        self._model_tiers = data.get("model_tiers", {})
        self._model_metadata = data.get("model_metadata", {})

        logger.info(f"Loaded {len(self._presets)} squad presets")

    def get_available_squads(
        self,
        hardware_info: Dict = None,
        check_api_keys: bool = True
    ) -> List[Dict]:
        """
        Returns squads the user can run based on hardware and API keys.

        Args:
            hardware_info: Pre-fetched hardware info (or fetches if None)
            check_api_keys: Whether to validate API key availability

        Returns:
            List of squad presets with availability status
        """
        if hardware_info is None:
            hardware_info = self.hardware.detect().to_dict()

        available = []
        for squad_id, preset in self.presets.items():
            availability = self._check_squad_availability(
                preset, hardware_info, check_api_keys
            )
            squad_data = {
                **preset,
                "available": availability["available"],
                "missing_requirements": availability["missing"],
                "warnings": availability["warnings"],
                "available_tournament_models": self._get_available_tournament_models(
                    preset, check_api_keys
                )
            }
            available.append(squad_data)

        # Sort: available first, then by tier (budget before premium)
        tier_order = {"free": 0, "budget": 1, "premium": 2}
        available.sort(key=lambda s: (
            0 if s["available"] else 1,
            tier_order.get(s["tier"], 99)
        ))

        return available

    def _check_squad_availability(
        self,
        preset: Dict,
        hardware: Dict,
        check_keys: bool
    ) -> Dict:
        """
        Check if a squad can be used.

        Returns dict with 'available', 'missing', and 'warnings' keys.
        """
        missing = []
        warnings = []

        reqs = preset.get("requirements", {})

        # Check Ollama requirement
        if reqs.get("ollama_required") and not hardware.get("ollama_installed"):
            missing.append("Ollama not installed")

        # Check RAM requirement
        min_ram = reqs.get("min_ram_gb", 0)
        if hardware.get("ram_gb", 0) < min_ram:
            missing.append(f"Requires {min_ram}GB RAM (you have {hardware.get('ram_gb', 0)}GB)")

        # Check required API keys
        if check_keys:
            for key_name in reqs.get("api_keys", []):
                if not os.environ.get(key_name):
                    missing.append(f"Missing {key_name}")

        # Check optional API keys (warnings only)
        for key_name in preset.get("optional_api_keys", []):
            if not os.environ.get(key_name):
                # Make warning more helpful
                provider = key_name.replace("_API_KEY", "").replace("_", " ").title()
                warnings.append(f"{provider} not configured (optional)")

        return {
            "available": len(missing) == 0,
            "missing": missing,
            "warnings": warnings
        }

    def _get_available_tournament_models(
        self,
        preset: Dict,
        check_keys: bool
    ) -> List[str]:
        """Get which tournament models from a preset are actually available."""
        default_models = preset.get("default_models", {}).get("tournament", [])
        if not check_keys:
            return default_models

        available = []
        for model_id in default_models:
            if self._is_model_available(model_id):
                available.append(model_id)

        return available

    def apply_squad(
        self,
        squad_id: str,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Apply a squad's configuration to settings.

        This updates:
        - Foreman task models
        - Health check models
        - Tournament defaults
        - Squad metadata

        Args:
            squad_id: "local" | "hybrid" | "pro"
            project_id: Optional project-specific override

        Returns:
            Applied configuration summary
        """
        preset = self.presets.get(squad_id)
        if not preset:
            raise ValueError(f"Unknown squad: {squad_id}")

        # Update squad settings
        self.settings.set("squad.active_squad", squad_id, project_id)
        self.settings.set("squad.setup_complete", True, project_id)

        # Get model configuration
        models = preset.get("default_models", {})

        # Apply Foreman coordinator model
        coordinator = models.get("foreman_coordinator", "mistral:7b")
        self.settings.set("foreman.coordinator_model", coordinator, project_id)
        self.settings.set("foreman.task_models.coordinator", coordinator, project_id)

        # Apply strategic task models
        strategic_model = models.get("foreman_strategic", "deepseek-chat")
        strategic_tasks = [
            "health_check_review",
            "voice_calibration_guidance",
            "beat_structure_advice",
            "conflict_resolution",
            "scaffold_enrichment_decisions",
            "theme_analysis",
            "structural_planning"
        ]
        for task in strategic_tasks:
            self.settings.set(
                f"foreman.task_models.{task}",
                strategic_model,
                project_id
            )

        # Apply health check models
        health_models = models.get("health_checks", {})
        for check_type, model in health_models.items():
            if check_type == "default":
                self.settings.set(
                    "health_checks.models.default_model",
                    model,
                    project_id
                )
            else:
                self.settings.set(
                    f"health_checks.models.{check_type}",
                    model,
                    project_id
                )

        # Store tournament defaults (but don't lock them - user can customize)
        tournament_models = models.get("tournament", [])
        # Only store as defaults, not as custom selection
        # Custom selection is only set when user explicitly chooses models

        logger.info(f"Applied {squad_id} squad configuration")

        return {
            "squad": squad_id,
            "applied_models": {
                "foreman_strategic": strategic_model,
                "foreman_coordinator": coordinator,
                "tournament_defaults": tournament_models,
                "health_checks": health_models
            },
            "status": "success"
        }

    def get_active_squad(self, project_id: Optional[str] = None) -> str:
        """Get the currently active squad ID."""
        return self.settings.get("squad.active_squad", project_id) or "hybrid"

    def get_tournament_models(
        self,
        project_id: Optional[str] = None,
        include_unavailable: bool = False
    ) -> List[Dict]:
        """
        Get models available for tournament selection.

        Returns list of models with tier, availability, cost, and selection status.

        Args:
            project_id: For project-specific settings
            include_unavailable: Include models without API keys

        Returns:
            List of model dicts with metadata
        """
        # Get active squad
        squad_id = self.get_active_squad(project_id)
        preset = self.presets.get(squad_id, {})

        # Check for custom selection
        custom = self.settings.get("squad.custom_tournament_models", project_id)
        if custom:
            default_selected = set(custom)
        else:
            default_selected = set(
                preset.get("default_models", {}).get("tournament", [])
            )

        # Build model list with metadata
        all_models = []

        for tier, models in self.model_tiers.items():
            for model_id in models:
                metadata = self.model_metadata.get(model_id, {})
                is_available = self._is_model_available(model_id)

                if not include_unavailable and not is_available:
                    continue

                all_models.append({
                    "id": model_id,
                    "name": metadata.get("name", model_id),
                    "tier": tier,
                    "provider": metadata.get("provider", "unknown"),
                    "available": is_available,
                    "selected": model_id in default_selected,
                    "cost_per_1m_input": metadata.get("cost_per_1m_input", 0),
                    "cost_per_1m_output": metadata.get("cost_per_1m_output", 0),
                    "description": metadata.get("description", "")
                })

        # Sort by tier then name
        tier_order = {"free": 0, "budget": 1, "premium": 2}
        all_models.sort(key=lambda m: (tier_order.get(m["tier"], 99), m["name"]))

        return all_models

    def set_tournament_models(
        self,
        models: List[str],
        project_id: Optional[str] = None
    ):
        """
        Set custom tournament model selection.

        Args:
            models: List of model IDs to use in tournaments
            project_id: For project-specific override
        """
        self.settings.set("squad.custom_tournament_models", models, project_id)
        logger.info(f"Set custom tournament models: {models}")

    def clear_custom_tournament_models(self, project_id: Optional[str] = None):
        """Clear custom selection and revert to squad defaults."""
        self.settings.set("squad.custom_tournament_models", None, project_id)

    def _is_model_available(self, model_id: str) -> bool:
        """
        Check if a model is available (API key present or local).

        Args:
            model_id: Model identifier

        Returns:
            True if model can be used
        """
        # Local models: check if Ollama is running
        local_prefixes = ("mistral:", "llama", "phi", "neural-chat", "solar", "mixtral")
        if model_id.startswith(local_prefixes):
            return self.hardware.is_ollama_running()

        # Cloud models: check for API keys
        key_mapping = {
            "deepseek-chat": "DEEPSEEK_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "qwen-plus": "QWEN_API_KEY",
            "qwen": "QWEN_API_KEY",
            "zhipu-glm4": "ZHIPU_API_KEY",
            "zhipu": "ZHIPU_API_KEY",
            "glm": "ZHIPU_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "gpt": "OPENAI_API_KEY",
            "grok": "XAI_API_KEY",
            "mistral-large": "MISTRAL_API_KEY",
        }

        for prefix, key_name in key_mapping.items():
            if prefix in model_id.lower():
                return bool(os.environ.get(key_name))

        # Unknown model - assume unavailable
        return False

    def estimate_tournament_cost(
        self,
        selected_models: List[str],
        num_strategies: int = 5,
        avg_tokens_per_variant: int = 2000
    ) -> Dict:
        """
        Estimate cost for a tournament run.

        Args:
            selected_models: Models to include in tournament
            num_strategies: Number of writing strategies (default 5)
            avg_tokens_per_variant: Average tokens per generated variant

        Returns:
            Cost estimate with breakdown
        """
        total_cost = 0.0
        breakdown = []

        for model_id in selected_models:
            metadata = self.model_metadata.get(model_id, {})

            # Cost per 1M tokens
            input_cost = metadata.get("cost_per_1m_input", 0)
            output_cost = metadata.get("cost_per_1m_output", 0)

            # Estimate: input is prompt (~500 tokens), output is variant (~2000 tokens)
            input_tokens = 500 * num_strategies
            output_tokens = avg_tokens_per_variant * num_strategies

            model_cost = (
                (input_tokens / 1_000_000) * input_cost +
                (output_tokens / 1_000_000) * output_cost
            )

            total_cost += model_cost
            breakdown.append({
                "model": model_id,
                "model_name": metadata.get("name", model_id),
                "variants": num_strategies,
                "cost": round(model_cost, 6)
            })

        return {
            "total_cost": round(total_cost, 4),
            "breakdown": breakdown,
            "total_variants": len(selected_models) * num_strategies,
            "assumptions": {
                "input_tokens_per_variant": 500,
                "output_tokens_per_variant": avg_tokens_per_variant,
                "strategies": num_strategies
            }
        }

    def generate_voice_recommendation(
        self,
        tournament_results: List[Dict],
        current_squad: str,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Analyze voice tournament results and recommend a squad.

        This provides intelligent guidance based on which models
        best matched the author's target voice.

        Args:
            tournament_results: List of {model, score, strategy} from voice tournament
            current_squad: User's current squad selection

        Returns:
            Recommendation with reasoning
        """
        if not tournament_results:
            return {
                "recommended_squad": current_squad,
                "reason": "No tournament data available",
                "top_model": None,
                "top_score": None
            }

        # Find top performer
        sorted_results = sorted(
            tournament_results,
            key=lambda x: x.get("score", 0),
            reverse=True
        )
        top = sorted_results[0]
        top_model = top.get("model")
        top_score = top.get("score", 0)

        # Determine which tier the top model belongs to
        top_tier = None
        for tier, models in self.model_tiers.items():
            if top_model in models:
                top_tier = tier
                break

        # Find best budget model for comparison
        budget_best = None
        budget_score = 0
        for result in sorted_results:
            model = result.get("model")
            if model in self.model_tiers.get("budget", []):
                budget_best = model
                budget_score = result.get("score", 0)
                break

        # Generate recommendation
        recommendation = {
            "top_model": top_model,
            "top_model_name": self.model_metadata.get(top_model, {}).get("name", top_model),
            "top_score": top_score,
            "top_tier": top_tier,
            "current_squad": current_squad,
            "budget_alternative": budget_best,
            "budget_score": budget_score
        }

        # Decision logic
        if top_tier == "premium" and top_score >= 85:
            # Premium model won decisively
            recommendation["recommended_squad"] = "pro"
            recommendation["reason"] = (
                f"Your voice achieved {top_score}% match with {recommendation['top_model_name']}. "
                f"This premium model captures nuances that significantly benefit your style. "
                f"Pro Squad recommended for best results."
            )
            if budget_best and budget_score >= top_score - 10:
                recommendation["alternative"] = (
                    f"However, {self.model_metadata.get(budget_best, {}).get('name', budget_best)} "
                    f"scored {budget_score}% - only {top_score - budget_score}% behind. "
                    f"Hybrid Squad offers excellent value if budget is a concern."
                )
        elif top_tier == "budget" or (top_tier == "premium" and top_score < 80):
            # Budget model won or premium didn't win decisively
            recommendation["recommended_squad"] = "hybrid"
            recommendation["reason"] = (
                f"Budget models performed excellently for your voice style. "
                f"{recommendation['top_model_name']} achieved {top_score}% match. "
                f"Hybrid Squad provides optimal quality at minimal cost."
            )
        elif top_tier == "free":
            # Local model performed best
            recommendation["recommended_squad"] = "local"
            recommendation["reason"] = (
                f"Local model {recommendation['top_model_name']} matched your voice well ({top_score}%). "
                f"For privacy and zero cost, Local Squad is a great choice. "
                f"Consider Hybrid Squad for more variety in tournaments."
            )
        else:
            # Default to current
            recommendation["recommended_squad"] = current_squad
            recommendation["reason"] = "Your current squad configuration is well-suited to your voice."

        # Save recommendation to settings
        self.settings.set("squad.voice_recommendation", recommendation, project_id)

        return recommendation

    def get_squad_for_genre(self, genre: str) -> Dict:
        """
        Get squad recommendation based on genre.

        Different genres may benefit from different model strengths.

        Args:
            genre: Genre name (e.g., "cyberpunk", "romance", "literary")

        Returns:
            Recommendation dict with squad and reasoning
        """
        genre_lower = genre.lower()

        # Genre-specific recommendations
        genre_recommendations = {
            "cyberpunk": {
                "squad": "pro",
                "reason": "Cyberpunk benefits from Grok's unconventional voice and Claude's noir sensibilities",
                "key_models": ["grok-2", "claude-3-7-sonnet-20250219"]
            },
            "scifi": {
                "squad": "hybrid",
                "reason": "Science fiction works well with DeepSeek's systematic thinking",
                "key_models": ["deepseek-chat", "qwen-plus"]
            },
            "fantasy": {
                "squad": "hybrid",
                "reason": "Fantasy world-building pairs well with Qwen's cultural depth",
                "key_models": ["qwen-plus", "deepseek-chat"]
            },
            "romance": {
                "squad": "hybrid",
                "reason": "Romance benefits from emotional nuance - budget models handle this well",
                "key_models": ["deepseek-chat", "gemini-2.0-flash-exp"]
            },
            "literary": {
                "squad": "pro",
                "reason": "Literary fiction requires Claude's sophisticated prose and GPT-4o's thematic depth",
                "key_models": ["claude-3-7-sonnet-20250219", "gpt-4o"]
            },
            "thriller": {
                "squad": "hybrid",
                "reason": "Thrillers need tight pacing - DeepSeek excels at structure",
                "key_models": ["deepseek-chat", "zhipu-glm4"]
            },
            "mystery": {
                "squad": "hybrid",
                "reason": "Mystery plotting benefits from strategic reasoning",
                "key_models": ["zhipu-glm4", "deepseek-chat"]
            },
            "horror": {
                "squad": "pro",
                "reason": "Horror atmosphere benefits from premium model creativity",
                "key_models": ["claude-3-7-sonnet-20250219", "grok-2"]
            }
        }

        # Find matching recommendation
        for key, rec in genre_recommendations.items():
            if key in genre_lower:
                return rec

        # Default recommendation
        return {
            "squad": "hybrid",
            "reason": "Hybrid Squad offers excellent general-purpose performance",
            "key_models": ["deepseek-chat", "qwen-plus"]
        }


# Lazy initialization - will be properly initialized when settings and hardware services are available
squad_service = None


def get_squad_service(settings_service, hardware_service) -> SquadService:
    """Get or create the squad service singleton."""
    global squad_service
    if squad_service is None:
        squad_service = SquadService(settings_service, hardware_service)
    return squad_service
