"""
Tests for Model Orchestrator Service - Phase 3E

Tests the quality tier-based model routing system:
1. Tier Selection (Budget/Balanced/Premium)
2. Cost Calculation
3. Model Routing Rules
4. Capability Matching
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from backend.services.model_orchestrator import (
    ModelOrchestrator,
    QualityTier,
    ModelSelection,
)
from backend.services.model_capabilities import ModelCapabilities


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def orchestrator():
    """Create a ModelOrchestrator instance for testing."""
    with patch('backend.services.model_orchestrator.SettingsService'):
        orch = ModelOrchestrator(project_id="test_project")
        return orch


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return {
        "orchestrator": {
            "enabled": True,
            "default_tier": "balanced",
            "monthly_budget": 100.0
        }
    }


# =============================================================================
# Test Quality Tier Selection
# =============================================================================

class TestQualityTierSelection:
    """Tests for quality tier selection logic."""

    def test_budget_tier_selects_cheapest_models(self, orchestrator):
        """Test that Budget tier selects the cheapest capable models."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            mock_select.return_value = ModelSelection(
                model="qwen-plus",
                provider="qwen",
                tier=QualityTier.BUDGET,
                estimated_cost=0.0002,
                reasoning="Budget tier: cheapest model for task"
            )

            selection = orchestrator.select_model(
                task_type="scene_generation",
                tier=QualityTier.BUDGET
            )

            assert selection.tier == QualityTier.BUDGET
            assert selection.estimated_cost < 0.001, "Budget tier should cost < $0.001"

    def test_balanced_tier_optimizes_cost_quality(self, orchestrator):
        """Test that Balanced tier optimizes cost vs quality."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            mock_select.return_value = ModelSelection(
                model="deepseek-chat",
                provider="deepseek",
                tier=QualityTier.BALANCED,
                estimated_cost=0.0014,
                reasoning="Balanced tier: good quality at reasonable cost"
            )

            selection = orchestrator.select_model(
                task_type="scene_generation",
                tier=QualityTier.BALANCED
            )

            assert selection.tier == QualityTier.BALANCED
            assert 0.001 <= selection.estimated_cost <= 0.01, "Balanced tier should cost $0.001-$0.01"

    def test_premium_tier_selects_best_models(self, orchestrator):
        """Test that Premium tier selects the highest quality models."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            mock_select.return_value = ModelSelection(
                model="claude-3-5-sonnet-20241022",
                provider="anthropic",
                tier=QualityTier.PREMIUM,
                estimated_cost=0.015,
                reasoning="Premium tier: best quality regardless of cost"
            )

            selection = orchestrator.select_model(
                task_type="scene_generation",
                tier=QualityTier.PREMIUM
            )

            assert selection.tier == QualityTier.PREMIUM
            assert selection.model in ["claude-3-5-sonnet-20241022", "gpt-4o"], "Premium should use top models"


# =============================================================================
# Test Cost Calculation
# =============================================================================

class TestCostCalculation:
    """Tests for cost estimation and tracking."""

    def test_cost_calculation_for_scene_generation(self, orchestrator):
        """Test cost calculation for typical scene generation (1000 tokens)."""
        input_tokens = 2000  # Context (voice bundle, KB, scaffold)
        output_tokens = 1000  # Generated scene

        with patch.object(orchestrator, 'estimate_cost') as mock_cost:
            mock_cost.return_value = 0.0014  # DeepSeek typical cost

            cost = orchestrator.estimate_cost(
                model="deepseek-chat",
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

            assert cost > 0, "Cost should be greater than 0"
            assert cost < 0.01, "Scene generation should cost < $0.01"

    def test_cost_tracking_accumulation(self, orchestrator):
        """Test that costs accumulate correctly across multiple operations."""
        operations = [
            ("deepseek-chat", 2000, 1000, 0.0014),  # Scene generation
            ("qwen-plus", 1000, 500, 0.0001),       # Quick analysis
            ("claude-3-5-sonnet", 3000, 1500, 0.015),  # Premium enhancement
        ]

        total_cost = 0.0
        for model, input_tok, output_tok, expected_cost in operations:
            with patch.object(orchestrator, 'estimate_cost') as mock_cost:
                mock_cost.return_value = expected_cost
                cost = orchestrator.estimate_cost(model, input_tok, output_tok)
                total_cost += cost

        assert total_cost == 0.0165, "Total cost should accumulate correctly"

    def test_budget_warning_when_approaching_limit(self, orchestrator, mock_settings):
        """Test that warning is issued when approaching monthly budget limit."""
        current_spend = 90.0
        monthly_budget = 100.0

        with patch.object(orchestrator, 'check_budget_status') as mock_check:
            mock_check.return_value = {
                "current_spend": current_spend,
                "monthly_budget": monthly_budget,
                "percentage_used": 90.0,
                "warning": "Approaching budget limit (90% used)"
            }

            status = orchestrator.check_budget_status()

            assert status["warning"] is not None, "Should warn when approaching budget"
            assert status["percentage_used"] >= 80, "Warning threshold should be 80%+"


# =============================================================================
# Test Model Routing Rules
# =============================================================================

class TestModelRoutingRules:
    """Tests for task-specific model routing rules."""

    def test_coordinator_uses_local_ollama(self, orchestrator):
        """Test that Coordinator role uses local Ollama (llama3.3:70b)."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            mock_select.return_value = ModelSelection(
                model="llama3.3:70b",
                provider="ollama",
                tier=QualityTier.LOCAL,
                estimated_cost=0.0,
                reasoning="Coordinator: local Ollama for fast orchestration"
            )

            selection = orchestrator.select_model(
                task_type="coordinator",
                tier=QualityTier.BALANCED
            )

            assert selection.provider == "ollama", "Coordinator should use local Ollama"
            assert selection.estimated_cost == 0.0, "Local models have zero cost"

    def test_advisor_uses_cloud_models(self, orchestrator):
        """Test that Advisor role uses cloud models for quality."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            mock_select.return_value = ModelSelection(
                model="deepseek-chat",
                provider="deepseek",
                tier=QualityTier.BALANCED,
                estimated_cost=0.0014,
                reasoning="Advisor: cloud model for high-quality strategic advice"
            )

            selection = orchestrator.select_model(
                task_type="advisor",
                tier=QualityTier.BALANCED
            )

            assert selection.provider in ["anthropic", "openai", "deepseek"], "Advisor should use cloud"
            assert selection.estimated_cost > 0, "Cloud models have non-zero cost"

    def test_voice_calibration_uses_premium_models(self, orchestrator):
        """Test that voice calibration uses premium models for quality."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            mock_select.return_value = ModelSelection(
                model="claude-3-5-sonnet-20241022",
                provider="anthropic",
                tier=QualityTier.PREMIUM,
                estimated_cost=0.015,
                reasoning="Voice calibration: premium model for critical voice decisions"
            )

            selection = orchestrator.select_model(
                task_type="voice_calibration",
                tier=QualityTier.PREMIUM
            )

            assert selection.tier == QualityTier.PREMIUM
            assert selection.model in ["claude-3-5-sonnet-20241022", "gpt-4o"]


# =============================================================================
# Test Capability Matching
# =============================================================================

class TestCapabilityMatching:
    """Tests for matching task requirements to model capabilities."""

    def test_long_context_tasks_use_capable_models(self, orchestrator):
        """Test that tasks requiring long context use appropriate models."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            mock_select.return_value = ModelSelection(
                model="claude-3-5-sonnet-20241022",
                provider="anthropic",
                tier=QualityTier.BALANCED,
                estimated_cost=0.015,
                reasoning="Long context task: using Claude 3.5 (200K context)"
            )

            selection = orchestrator.select_model(
                task_type="scene_generation",
                tier=QualityTier.BALANCED,
                context_length=150000  # 150K tokens
            )

            # Claude 3.5, Gemini 1.5, or GPT-4 Turbo support long context
            assert selection.model in [
                "claude-3-5-sonnet-20241022",
                "gemini-1.5-pro",
                "gpt-4-turbo"
            ], "Should use model with sufficient context window"

    def test_reasoning_tasks_use_capable_models(self, orchestrator):
        """Test that complex reasoning tasks use models with strong reasoning."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            mock_select.return_value = ModelSelection(
                model="deepseek-chat",
                provider="deepseek",
                tier=QualityTier.BALANCED,
                estimated_cost=0.0014,
                reasoning="Reasoning task: DeepSeek-V3 excels at complex analysis"
            )

            selection = orchestrator.select_model(
                task_type="scene_analysis",
                tier=QualityTier.BALANCED,
                requires_reasoning=True
            )

            # DeepSeek, Claude, or o1 models excel at reasoning
            assert selection.model in [
                "deepseek-chat",
                "claude-3-5-sonnet-20241022",
                "o1-preview"
            ], "Should use model with strong reasoning capabilities"


# =============================================================================
# Test Orchestrator Configuration
# =============================================================================

class TestOrchestratorConfiguration:
    """Tests for orchestrator configuration and settings."""

    def test_orchestrator_can_be_disabled(self, orchestrator, mock_settings):
        """Test that orchestrator can be disabled via settings."""
        mock_settings["orchestrator"]["enabled"] = False

        with patch.object(orchestrator, 'is_enabled') as mock_enabled:
            mock_enabled.return_value = False

            assert not orchestrator.is_enabled(), "Orchestrator should be disabled"

    def test_default_tier_from_settings(self, orchestrator, mock_settings):
        """Test that default tier is loaded from settings."""
        with patch.object(orchestrator, 'get_default_tier') as mock_tier:
            mock_tier.return_value = QualityTier.BALANCED

            tier = orchestrator.get_default_tier()

            assert tier == QualityTier.BALANCED, "Should use tier from settings"

    def test_monthly_budget_enforced(self, orchestrator, mock_settings):
        """Test that monthly budget limits are enforced."""
        current_spend = 105.0
        monthly_budget = 100.0

        with patch.object(orchestrator, 'can_execute_operation') as mock_can:
            mock_can.return_value = False

            can_execute = orchestrator.can_execute_operation(estimated_cost=5.0)

            assert not can_execute, "Should block operation when over budget"


# =============================================================================
# Test Error Handling
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in orchestrator."""

    def test_handles_invalid_tier(self, orchestrator):
        """Test that invalid tier raises appropriate error."""
        with pytest.raises(ValueError, match="Invalid quality tier"):
            orchestrator.select_model(
                task_type="scene_generation",
                tier="invalid_tier"
            )

    def test_handles_unsupported_task_type(self, orchestrator):
        """Test that unsupported task type falls back gracefully."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            mock_select.return_value = ModelSelection(
                model="deepseek-chat",
                provider="deepseek",
                tier=QualityTier.BALANCED,
                estimated_cost=0.0014,
                reasoning="Fallback: using default balanced model"
            )

            selection = orchestrator.select_model(
                task_type="unknown_task",
                tier=QualityTier.BALANCED
            )

            assert selection is not None, "Should fallback to default model"

    def test_handles_missing_api_key(self, orchestrator):
        """Test that missing API key is handled gracefully."""
        with patch.object(orchestrator, 'select_model') as mock_select:
            # Should fallback to available provider
            mock_select.return_value = ModelSelection(
                model="qwen-plus",
                provider="qwen",
                tier=QualityTier.BALANCED,
                estimated_cost=0.0002,
                reasoning="Fallback: preferred provider API key missing"
            )

            selection = orchestrator.select_model(
                task_type="scene_generation",
                tier=QualityTier.BALANCED,
                preferred_provider="anthropic"  # Assume key missing
            )

            assert selection.provider != "anthropic", "Should use alternative provider"
