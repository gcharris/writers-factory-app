"""
Tests for SquadService - Squad Preset Management and Model Selection

The Squad system simplifies model configuration into three choices:
1. Local Squad - Free, offline, privacy-focused
2. Hybrid Squad - Best value, course default (RECOMMENDED)
3. Pro Squad - Premium quality, BYOK

Test Coverage:
- Squad preset loading
- Squad availability checking (hardware + API keys)
- Squad application (Foreman, health checks, tournament defaults)
- Tournament model management (get, set, clear custom)
- Cost estimation
- Voice-based recommendations
- Genre-based recommendations
- Model availability detection
"""

import pytest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from backend.services.squad_service import (
    SquadService,
    SquadRequirements,
    SquadCostEstimate,
)

# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_settings_service():
    """Mock SettingsService."""
    settings = Mock()
    settings.get = Mock(return_value=None)
    settings.set = Mock()
    return settings


@pytest.fixture
def mock_hardware_service():
    """Mock HardwareService."""
    hardware = Mock()
    hardware.detect = Mock(return_value=Mock(to_dict=Mock(return_value={
        "ram_gb": 16,
        "available_ram_gb": 8,
        "cpu_cores": 8,
        "gpu_available": True,
        "gpu_name": "Apple Silicon",
        "gpu_vram_gb": 16,
        "ollama_installed": True,
        "ollama_version": "0.12.10",
        "ollama_models": ["mistral:7b", "llama3.2:3b"],
        "recommended_max_params": "12b",
        "platform": "darwin"
    })))
    hardware.is_ollama_running = Mock(return_value=True)
    return hardware


@pytest.fixture
def squad_presets_json(tmp_path):
    """Create temporary squad_presets.json for testing."""
    presets = {
        "version": "1.0",
        "presets": {
            "local": {
                "id": "local",
                "name": "Local Squad",
                "icon": "🏠",
                "tier": "free",
                "recommended": False,
                "requirements": {
                    "ollama_required": True,
                    "min_ram_gb": 8,
                    "api_keys": []
                },
                "optional_api_keys": [],
                "default_models": {
                    "foreman_strategic": "mistral:7b",
                    "foreman_coordinator": "mistral:7b",
                    "tournament": ["mistral:7b", "llama3.2:3b"],
                    "health_checks": {
                        "default": "mistral:7b"
                    }
                },
                "cost_estimate": {
                    "weekly_usd": 0,
                    "monthly_usd": 0
                }
            },
            "hybrid": {
                "id": "hybrid",
                "name": "Hybrid Squad",
                "icon": "💎",
                "tier": "budget",
                "recommended": True,
                "requirements": {
                    "ollama_required": True,
                    "min_ram_gb": 8,
                    "api_keys": ["DEEPSEEK_API_KEY"]
                },
                "optional_api_keys": ["QWEN_API_KEY", "ZHIPU_API_KEY"],
                "default_models": {
                    "foreman_strategic": "deepseek-chat",
                    "foreman_coordinator": "mistral:7b",
                    "tournament": ["deepseek-chat", "qwen-plus", "zhipu-glm4"],
                    "health_checks": {
                        "default": "mistral:7b",
                        "timeline_consistency": "deepseek-chat"
                    }
                },
                "cost_estimate": {
                    "weekly_usd": 0.50,
                    "monthly_usd": 2.00
                }
            },
            "pro": {
                "id": "pro",
                "name": "Pro Squad",
                "icon": "🚀",
                "tier": "premium",
                "recommended": False,
                "requirements": {
                    "ollama_required": False,
                    "min_ram_gb": 4,
                    "api_keys": ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
                },
                "optional_api_keys": ["XAI_API_KEY"],
                "default_models": {
                    "foreman_strategic": "claude-3-7-sonnet-20250219",
                    "foreman_coordinator": "deepseek-chat",
                    "tournament": ["claude-3-7-sonnet-20250219", "gpt-4o"],
                    "health_checks": {
                        "default": "claude-3-7-sonnet-20250219"
                    }
                },
                "cost_estimate": {
                    "weekly_usd": 3.50,
                    "monthly_usd": 15.00
                }
            }
        },
        "model_tiers": {
            "free": ["mistral:7b", "llama3.2:3b"],
            "budget": ["deepseek-chat", "qwen-plus", "zhipu-glm4"],
            "premium": ["claude-3-7-sonnet-20250219", "gpt-4o", "grok-2"]
        },
        "model_metadata": {
            "mistral:7b": {
                "name": "Mistral 7B",
                "provider": "ollama",
                "cost_per_1m_input": 0,
                "cost_per_1m_output": 0
            },
            "deepseek-chat": {
                "name": "DeepSeek V3",
                "provider": "deepseek",
                "cost_per_1m_input": 0.14,
                "cost_per_1m_output": 0.28
            },
            "claude-3-7-sonnet-20250219": {
                "name": "Claude 3.7 Sonnet",
                "provider": "anthropic",
                "cost_per_1m_input": 3.00,
                "cost_per_1m_output": 15.00
            },
            "gpt-4o": {
                "name": "GPT-4o",
                "provider": "openai",
                "cost_per_1m_input": 2.50,
                "cost_per_1m_output": 10.00
            }
        }
    }

    presets_file = tmp_path / "squad_presets.json"
    with open(presets_file, 'w') as f:
        json.dump(presets, f)

    return str(presets_file)


@pytest.fixture
def squad_service(mock_settings_service, mock_hardware_service, squad_presets_json):
    """Create SquadService instance for testing."""
    return SquadService(
        mock_settings_service,
        mock_hardware_service,
        presets_path=squad_presets_json
    )


# =============================================================================
# Test: Initialization and Loading
# =============================================================================

class TestInitializationAndLoading:
    """Test service initialization and preset loading."""

    def test_init_with_custom_presets_path(
        self, mock_settings_service, mock_hardware_service, squad_presets_json
    ):
        """Test initialization with custom presets path."""
        service = SquadService(
            mock_settings_service,
            mock_hardware_service,
            presets_path=squad_presets_json
        )

        assert service.presets_path == squad_presets_json
        assert service.settings == mock_settings_service
        assert service.hardware == mock_hardware_service

    def test_init_finds_presets_automatically(
        self, mock_settings_service, mock_hardware_service, squad_presets_json
    ):
        """Test that init finds presets in common locations."""
        # This test assumes squad_presets.json exists in the actual location
        with patch('pathlib.Path.exists', return_value=True):
            service = SquadService(
                mock_settings_service,
                mock_hardware_service
            )
            # Should not raise FileNotFoundError

    def test_init_raises_when_presets_not_found(
        self, mock_settings_service, mock_hardware_service
    ):
        """Test that init raises error when presets not found."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(FileNotFoundError, match="Could not find squad_presets.json"):
                SquadService(mock_settings_service, mock_hardware_service)

    def test_presets_lazy_loading(self, squad_service):
        """Test that presets are lazy-loaded."""
        # Access should trigger loading
        presets = squad_service.presets

        assert isinstance(presets, dict)
        assert "local" in presets
        assert "hybrid" in presets
        assert "pro" in presets

    def test_model_tiers_loaded(self, squad_service):
        """Test that model tiers are loaded."""
        tiers = squad_service.model_tiers

        assert "free" in tiers
        assert "budget" in tiers
        assert "premium" in tiers
        assert "mistral:7b" in tiers["free"]

    def test_model_metadata_loaded(self, squad_service):
        """Test that model metadata is loaded."""
        metadata = squad_service.model_metadata

        assert "mistral:7b" in metadata
        assert "deepseek-chat" in metadata
        assert metadata["deepseek-chat"]["name"] == "DeepSeek V3"


# =============================================================================
# Test: Squad Availability
# =============================================================================

class TestSquadAvailability:
    """Test squad availability checking."""

    def test_get_available_squads_all_available(self, squad_service):
        """Test getting available squads when all requirements met."""
        with patch.dict(os.environ, {
            "DEEPSEEK_API_KEY": "test",
            "ANTHROPIC_API_KEY": "test",
            "OPENAI_API_KEY": "test"
        }):
            squads = squad_service.get_available_squads()

            assert len(squads) == 3
            # All squads should be available
            assert all(s["available"] for s in squads)

    def test_get_available_squads_missing_ollama(
        self, mock_settings_service, mock_hardware_service, squad_presets_json
    ):
        """Test squad availability when Ollama not installed."""
        mock_hardware_service.detect.return_value.to_dict.return_value = {
            "ram_gb": 16,
            "ollama_installed": False,
            "platform": "darwin"
        }

        service = SquadService(
            mock_settings_service,
            mock_hardware_service,
            presets_path=squad_presets_json
        )

        squads = service.get_available_squads()

        # Local and Hybrid should be unavailable (require Ollama)
        local = next(s for s in squads if s["id"] == "local")
        hybrid = next(s for s in squads if s["id"] == "hybrid")
        pro = next(s for s in squads if s["id"] == "pro")

        assert local["available"] is False
        assert "Ollama not installed" in local["missing_requirements"]
        assert hybrid["available"] is False
        # Pro doesn't require Ollama

    def test_get_available_squads_missing_ram(
        self, mock_settings_service, mock_hardware_service, squad_presets_json
    ):
        """Test squad availability when insufficient RAM."""
        mock_hardware_service.detect.return_value.to_dict.return_value = {
            "ram_gb": 4,  # Local requires 8GB
            "ollama_installed": True,
            "platform": "darwin"
        }

        service = SquadService(
            mock_settings_service,
            mock_hardware_service,
            presets_path=squad_presets_json
        )

        squads = service.get_available_squads()

        local = next(s for s in squads if s["id"] == "local")
        assert local["available"] is False
        assert any("RAM" in req for req in local["missing_requirements"])

    def test_get_available_squads_missing_api_keys(self, squad_service):
        """Test squad availability when API keys missing."""
        with patch.dict(os.environ, {}, clear=True):
            squads = squad_service.get_available_squads()

            # Local should be available (no API keys needed)
            local = next(s for s in squads if s["id"] == "local")
            assert local["available"] is True

            # Hybrid should be unavailable (needs DEEPSEEK_API_KEY)
            hybrid = next(s for s in squads if s["id"] == "hybrid")
            assert hybrid["available"] is False
            assert "DEEPSEEK_API_KEY" in str(hybrid["missing_requirements"])

            # Pro should be unavailable (needs ANTHROPIC + OPENAI)
            pro = next(s for s in squads if s["id"] == "pro")
            assert pro["available"] is False

    def test_get_available_squads_optional_keys_warnings(self, squad_service):
        """Test that missing optional API keys generate warnings."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}, clear=True):
            squads = squad_service.get_available_squads()

            hybrid = next(s for s in squads if s["id"] == "hybrid")
            # Should have warnings for optional keys (Qwen, Zhipu)
            assert len(hybrid["warnings"]) > 0
            assert any("optional" in w.lower() for w in hybrid["warnings"])

    def test_get_available_squads_sorts_by_availability(self, squad_service):
        """Test that squads are sorted by availability then tier."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}, clear=True):
            squads = squad_service.get_available_squads()

            # Available squads should come first
            first_available_idx = next(
                i for i, s in enumerate(squads) if s["available"]
            )
            first_unavailable_idx = next(
                (i for i, s in enumerate(squads) if not s["available"]),
                len(squads)
            )

            assert first_available_idx < first_unavailable_idx


# =============================================================================
# Test: Squad Application
# =============================================================================

class TestSquadApplication:
    """Test applying squad configurations."""

    def test_apply_squad_hybrid(self, squad_service):
        """Test applying Hybrid Squad."""
        result = squad_service.apply_squad("hybrid")

        assert result["squad"] == "hybrid"
        assert result["status"] == "success"
        assert "foreman_strategic" in result["applied_models"]
        assert result["applied_models"]["foreman_strategic"] == "deepseek-chat"
        assert result["applied_models"]["foreman_coordinator"] == "mistral:7b"

        # Verify settings were updated
        squad_service.settings.set.assert_any_call("squad.active_squad", "hybrid", None)
        squad_service.settings.set.assert_any_call("squad.setup_complete", True, None)

    def test_apply_squad_local(self, squad_service):
        """Test applying Local Squad."""
        result = squad_service.apply_squad("local")

        assert result["squad"] == "local"
        assert result["applied_models"]["foreman_strategic"] == "mistral:7b"
        assert result["applied_models"]["foreman_coordinator"] == "mistral:7b"

    def test_apply_squad_pro(self, squad_service):
        """Test applying Pro Squad."""
        result = squad_service.apply_squad("pro")

        assert result["squad"] == "pro"
        assert result["applied_models"]["foreman_strategic"] == "claude-3-7-sonnet-20250219"

    def test_apply_squad_with_project_id(self, squad_service):
        """Test applying squad with project-specific override."""
        result = squad_service.apply_squad("hybrid", project_id="test_project")

        # Verify project_id was passed to settings.set
        squad_service.settings.set.assert_any_call(
            "squad.active_squad", "hybrid", "test_project"
        )

    def test_apply_squad_invalid_id(self, squad_service):
        """Test applying non-existent squad."""
        with pytest.raises(ValueError, match="Unknown squad"):
            squad_service.apply_squad("nonexistent")

    def test_apply_squad_updates_health_checks(self, squad_service):
        """Test that health check models are updated."""
        result = squad_service.apply_squad("hybrid")

        health_models = result["applied_models"]["health_checks"]
        assert health_models["default"] == "mistral:7b"
        assert health_models["timeline_consistency"] == "deepseek-chat"

    def test_apply_squad_updates_strategic_tasks(self, squad_service):
        """Test that strategic task models are updated."""
        squad_service.apply_squad("hybrid")

        # Check that strategic tasks were set to DeepSeek
        strategic_tasks = [
            "health_check_review",
            "voice_calibration_guidance",
            "beat_structure_advice"
        ]
        for task in strategic_tasks:
            squad_service.settings.set.assert_any_call(
                f"foreman.task_models.{task}",
                "deepseek-chat",
                None
            )


# =============================================================================
# Test: Active Squad and Tournament Models
# =============================================================================

class TestActiveSquadAndTournament:
    """Test active squad retrieval and tournament model management."""

    def test_get_active_squad_default(self, squad_service):
        """Test getting active squad when none set (defaults to hybrid)."""
        squad_service.settings.get.return_value = None

        active = squad_service.get_active_squad()

        assert active == "hybrid"

    def test_get_active_squad_set(self, squad_service):
        """Test getting active squad when previously set."""
        squad_service.settings.get.return_value = "pro"

        active = squad_service.get_active_squad()

        assert active == "pro"

    def test_get_tournament_models_default_selection(self, squad_service):
        """Test getting tournament models with squad defaults."""
        squad_service.settings.get.side_effect = lambda key, pid: {
            "squad.active_squad": "hybrid",
            "squad.custom_tournament_models": None
        }.get(key)

        with patch.object(squad_service, '_is_model_available', return_value=True):
            models = squad_service.get_tournament_models()

            # Should return all available models from all tiers
            assert len(models) > 0
            # Default hybrid models should be selected
            selected = [m for m in models if m["selected"]]
            assert len(selected) > 0

    def test_get_tournament_models_custom_selection(self, squad_service):
        """Test getting tournament models with custom selection."""
        custom_models = ["claude-3-7-sonnet-20250219", "gpt-4o"]
        squad_service.settings.get.side_effect = lambda key, pid: {
            "squad.active_squad": "pro",
            "squad.custom_tournament_models": custom_models
        }.get(key)

        with patch.object(squad_service, '_is_model_available', return_value=True):
            models = squad_service.get_tournament_models()

            # Only custom models should be selected
            selected = [m for m in models if m["selected"]]
            selected_ids = {m["id"] for m in selected}
            assert selected_ids == set(custom_models)

    def test_set_tournament_models(self, squad_service):
        """Test setting custom tournament model selection."""
        custom = ["claude-3-7-sonnet-20250219", "grok-2"]

        squad_service.set_tournament_models(custom)

        squad_service.settings.set.assert_called_once_with(
            "squad.custom_tournament_models", custom, None
        )

    def test_clear_custom_tournament_models(self, squad_service):
        """Test clearing custom selection."""
        squad_service.clear_custom_tournament_models()

        squad_service.settings.set.assert_called_once_with(
            "squad.custom_tournament_models", None, None
        )

    def test_get_tournament_models_exclude_unavailable(self, squad_service):
        """Test that unavailable models are excluded by default."""
        squad_service.settings.get.return_value = "hybrid"

        # Only local models are available
        def mock_available(model_id):
            return model_id.startswith("mistral:")

        with patch.object(squad_service, '_is_model_available', side_effect=mock_available):
            models = squad_service.get_tournament_models(include_unavailable=False)

            # Should only include available models
            assert all(m["available"] for m in models)

    def test_get_tournament_models_include_unavailable(self, squad_service):
        """Test including unavailable models."""
        squad_service.settings.get.return_value = "hybrid"

        with patch.object(squad_service, '_is_model_available', return_value=False):
            models = squad_service.get_tournament_models(include_unavailable=True)

            # Should include unavailable models
            assert any(not m["available"] for m in models)


# =============================================================================
# Test: Model Availability Detection
# =============================================================================

class TestModelAvailability:
    """Test model availability detection."""

    def test_is_model_available_local_ollama_running(self, squad_service):
        """Test local model availability when Ollama running."""
        squad_service.hardware.is_ollama_running.return_value = True

        assert squad_service._is_model_available("mistral:7b") is True
        assert squad_service._is_model_available("llama3.2:3b") is True

    def test_is_model_available_local_ollama_not_running(self, squad_service):
        """Test local model availability when Ollama not running."""
        squad_service.hardware.is_ollama_running.return_value = False

        assert squad_service._is_model_available("mistral:7b") is False

    def test_is_model_available_cloud_with_api_key(self, squad_service):
        """Test cloud model availability with API key."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}):
            assert squad_service._is_model_available("deepseek-chat") is True

    def test_is_model_available_cloud_without_api_key(self, squad_service):
        """Test cloud model availability without API key."""
        with patch.dict(os.environ, {}, clear=True):
            assert squad_service._is_model_available("deepseek-chat") is False

    def test_is_model_available_various_providers(self, squad_service):
        """Test availability detection for various providers."""
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test",
            "OPENAI_API_KEY": "test",
            "XAI_API_KEY": "test",
            "MISTRAL_API_KEY": "test"
        }):
            assert squad_service._is_model_available("claude-3-7-sonnet-20250219") is True
            assert squad_service._is_model_available("gpt-4o") is True
            assert squad_service._is_model_available("grok-2") is True
            assert squad_service._is_model_available("mistral-large-latest") is True

    def test_is_model_available_unknown_model(self, squad_service):
        """Test unknown model defaults to unavailable."""
        assert squad_service._is_model_available("unknown-model-xyz") is False


# =============================================================================
# Test: Cost Estimation
# =============================================================================

class TestCostEstimation:
    """Test tournament cost estimation."""

    def test_estimate_tournament_cost_single_model(self, squad_service):
        """Test cost estimate for single model."""
        estimate = squad_service.estimate_tournament_cost(
            selected_models=["deepseek-chat"],
            num_strategies=3,
            avg_tokens_per_variant=2000
        )

        assert estimate["total_variants"] == 3  # 1 model × 3 strategies
        assert estimate["total_cost"] > 0
        assert len(estimate["breakdown"]) == 1
        assert estimate["breakdown"][0]["model"] == "deepseek-chat"

    def test_estimate_tournament_cost_multiple_models(self, squad_service):
        """Test cost estimate for multiple models."""
        estimate = squad_service.estimate_tournament_cost(
            selected_models=["deepseek-chat", "claude-3-7-sonnet-20250219"],
            num_strategies=5,
            avg_tokens_per_variant=2000
        )

        assert estimate["total_variants"] == 10  # 2 models × 5 strategies
        assert len(estimate["breakdown"]) == 2
        # Claude should be more expensive than DeepSeek
        claude_cost = next(b["cost"] for b in estimate["breakdown"] if "claude" in b["model"])
        deepseek_cost = next(b["cost"] for b in estimate["breakdown"] if "deepseek" in b["model"])
        assert claude_cost > deepseek_cost

    def test_estimate_tournament_cost_local_model(self, squad_service):
        """Test cost estimate for local model (should be $0)."""
        estimate = squad_service.estimate_tournament_cost(
            selected_models=["mistral:7b"],
            num_strategies=5
        )

        assert estimate["total_cost"] == 0
        assert estimate["breakdown"][0]["cost"] == 0

    def test_estimate_tournament_cost_mixed_models(self, squad_service):
        """Test cost estimate for mix of local and cloud models."""
        estimate = squad_service.estimate_tournament_cost(
            selected_models=["mistral:7b", "deepseek-chat"],
            num_strategies=3
        )

        # Total cost should only be from DeepSeek
        assert estimate["total_cost"] > 0
        local_cost = next(b["cost"] for b in estimate["breakdown"] if b["model"] == "mistral:7b")
        assert local_cost == 0


# =============================================================================
# Test: Voice-Based Recommendations
# =============================================================================

class TestVoiceRecommendations:
    """Test voice tournament result analysis and recommendations."""

    def test_generate_voice_recommendation_premium_wins(self, squad_service):
        """Test recommendation when premium model wins decisively."""
        tournament_results = [
            {"model": "claude-3-7-sonnet-20250219", "score": 88, "strategy": "noir"},
            {"model": "deepseek-chat", "score": 75, "strategy": "sparse"},
            {"model": "mistral:7b", "score": 70, "strategy": "lyrical"}
        ]

        rec = squad_service.generate_voice_recommendation(
            tournament_results, "hybrid"
        )

        assert rec["recommended_squad"] == "pro"
        assert rec["top_model"] == "claude-3-7-sonnet-20250219"
        assert rec["top_score"] == 88
        assert rec["top_tier"] == "premium"
        assert "Pro Squad" in rec["reason"]

    def test_generate_voice_recommendation_budget_wins(self, squad_service):
        """Test recommendation when budget model wins."""
        tournament_results = [
            {"model": "deepseek-chat", "score": 85, "strategy": "sparse"},
            {"model": "claude-3-7-sonnet-20250219", "score": 82, "strategy": "noir"},
            {"model": "mistral:7b", "score": 75, "strategy": "lyrical"}
        ]

        rec = squad_service.generate_voice_recommendation(
            tournament_results, "local"
        )

        assert rec["recommended_squad"] == "hybrid"
        assert rec["top_model"] == "deepseek-chat"
        assert rec["top_tier"] == "budget"
        assert "Hybrid Squad" in rec["reason"]

    def test_generate_voice_recommendation_local_wins(self, squad_service):
        """Test recommendation when local model wins."""
        tournament_results = [
            {"model": "mistral:7b", "score": 82, "strategy": "lyrical"},
            {"model": "deepseek-chat", "score": 78, "strategy": "sparse"}
        ]

        rec = squad_service.generate_voice_recommendation(
            tournament_results, "hybrid"
        )

        assert rec["recommended_squad"] == "local"
        assert rec["top_tier"] == "free"
        assert "Local Squad" in rec["reason"]

    def test_generate_voice_recommendation_premium_weak(self, squad_service):
        """Test recommendation when premium model wins but weakly."""
        tournament_results = [
            {"model": "claude-3-7-sonnet-20250219", "score": 78, "strategy": "noir"},
            {"model": "deepseek-chat", "score": 76, "strategy": "sparse"}
        ]

        rec = squad_service.generate_voice_recommendation(
            tournament_results, "hybrid"
        )

        # Should recommend Hybrid since premium didn't win decisively
        assert rec["recommended_squad"] == "hybrid"

    def test_generate_voice_recommendation_no_data(self, squad_service):
        """Test recommendation with no tournament data."""
        rec = squad_service.generate_voice_recommendation(
            [], "hybrid"
        )

        assert rec["recommended_squad"] == "hybrid"  # Keep current
        assert rec["top_model"] is None
        assert "No tournament data" in rec["reason"]

    def test_generate_voice_recommendation_saves_to_settings(self, squad_service):
        """Test that recommendation is saved to settings."""
        tournament_results = [
            {"model": "deepseek-chat", "score": 85, "strategy": "sparse"}
        ]

        rec = squad_service.generate_voice_recommendation(
            tournament_results, "hybrid", project_id="test_project"
        )

        squad_service.settings.set.assert_called_with(
            "squad.voice_recommendation", rec, "test_project"
        )


# =============================================================================
# Test: Genre-Based Recommendations
# =============================================================================

class TestGenreRecommendations:
    """Test genre-based squad recommendations."""

    def test_get_squad_for_genre_cyberpunk(self, squad_service):
        """Test cyberpunk genre recommendation."""
        rec = squad_service.get_squad_for_genre("cyberpunk")

        assert rec["squad"] == "pro"
        assert "Grok" in rec["reason"] or "unconventional" in rec["reason"]

    def test_get_squad_for_genre_scifi(self, squad_service):
        """Test science fiction genre recommendation."""
        rec = squad_service.get_squad_for_genre("scifi")

        assert rec["squad"] == "hybrid"
        assert "DeepSeek" in rec["reason"]

    def test_get_squad_for_genre_fantasy(self, squad_service):
        """Test fantasy genre recommendation."""
        rec = squad_service.get_squad_for_genre("fantasy")

        assert rec["squad"] == "hybrid"
        assert "Qwen" in rec["reason"]

    def test_get_squad_for_genre_literary(self, squad_service):
        """Test literary fiction recommendation."""
        rec = squad_service.get_squad_for_genre("literary")

        assert rec["squad"] == "pro"
        assert "Claude" in rec["reason"] or "GPT" in rec["reason"]

    def test_get_squad_for_genre_romance(self, squad_service):
        """Test romance genre recommendation."""
        rec = squad_service.get_squad_for_genre("romance")

        assert rec["squad"] == "hybrid"

    def test_get_squad_for_genre_case_insensitive(self, squad_service):
        """Test genre matching is case-insensitive."""
        rec1 = squad_service.get_squad_for_genre("CYBERPUNK")
        rec2 = squad_service.get_squad_for_genre("cyberpunk")

        assert rec1["squad"] == rec2["squad"]

    def test_get_squad_for_genre_unknown_defaults_hybrid(self, squad_service):
        """Test unknown genre defaults to Hybrid."""
        rec = squad_service.get_squad_for_genre("unknown_genre_xyz")

        assert rec["squad"] == "hybrid"
        assert "general-purpose" in rec["reason"].lower()


# =============================================================================
# Test: Data Classes
# =============================================================================

class TestDataClasses:
    """Test data classes."""

    def test_squad_requirements_dataclass(self):
        """Test SquadRequirements dataclass."""
        req = SquadRequirements(
            ollama_required=True,
            min_ram_gb=8,
            api_keys=["DEEPSEEK_API_KEY"],
            optional_api_keys=["QWEN_API_KEY"]
        )

        assert req.ollama_required is True
        assert req.min_ram_gb == 8
        assert len(req.api_keys) == 1
        assert len(req.optional_api_keys) == 1

    def test_squad_cost_estimate_dataclass(self):
        """Test SquadCostEstimate dataclass."""
        cost = SquadCostEstimate(
            weekly_usd=0.50,
            monthly_usd=2.00
        )

        assert cost.weekly_usd == 0.50
        assert cost.monthly_usd == 2.00


# =============================================================================
# Test: Integration
# =============================================================================

class TestIntegration:
    """Test integration scenarios."""

    def test_full_squad_workflow_local_to_hybrid(
        self, mock_settings_service, mock_hardware_service, squad_presets_json
    ):
        """Test complete workflow: check availability → apply squad → get models."""
        service = SquadService(
            mock_settings_service,
            mock_hardware_service,
            presets_path=squad_presets_json
        )

        # 1. Check what's available
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}):
            squads = service.get_available_squads()
            available_ids = [s["id"] for s in squads if s["available"]]
            assert "hybrid" in available_ids

            # 2. Apply Hybrid Squad
            result = service.apply_squad("hybrid")
            assert result["status"] == "success"

            # 3. Get tournament models
            mock_settings_service.get.side_effect = lambda key, pid: {
                "squad.active_squad": "hybrid",
                "squad.custom_tournament_models": None
            }.get(key)

            with patch.object(service, '_is_model_available', return_value=True):
                models = service.get_tournament_models()
                assert len(models) > 0

    def test_full_squad_workflow_custom_tournament(
        self, mock_settings_service, mock_hardware_service, squad_presets_json
    ):
        """Test workflow with custom tournament model selection."""
        service = SquadService(
            mock_settings_service,
            mock_hardware_service,
            presets_path=squad_presets_json
        )

        # Apply squad
        service.apply_squad("pro")

        # Set custom tournament models
        custom = ["claude-3-7-sonnet-20250219", "gpt-4o"]
        service.set_tournament_models(custom, project_id="my_novel")

        # Verify setting was called
        mock_settings_service.set.assert_any_call(
            "squad.custom_tournament_models", custom, "my_novel"
        )

        # Estimate cost
        estimate = service.estimate_tournament_cost(custom, num_strategies=5)
        assert estimate["total_variants"] == 10
        assert estimate["total_cost"] > 0
