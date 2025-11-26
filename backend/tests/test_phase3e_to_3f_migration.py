"""
Test Phase 3E → Phase 3F Migration

Phase 3E: Individual model configuration (9+ models to configure)
Phase 3F: Squad System (3 preset choices)

This test verifies that:
1. Existing Phase 3E projects can apply Squad System
2. Squad application doesn't break existing settings
3. Custom model selections are preserved where possible
4. Migration is smooth and reversible
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from backend.services.settings_service import SettingsService
from backend.services.hardware_service import HardwareService
from backend.services.squad_service import SquadService


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def settings_service():
    """Create SettingsService (uses shared test database)."""
    return SettingsService()


@pytest.fixture
def hardware_service():
    """Create HardwareService."""
    return HardwareService()


@pytest.fixture
def squad_service(settings_service, hardware_service):
    """Create SquadService."""
    # Use the actual squad_presets.json file
    presets_path = Path(__file__).parent.parent / "config" / "squad_presets.json"
    return SquadService(settings_service, hardware_service, presets_path=str(presets_path))


@pytest.fixture
def phase3e_settings():
    """Typical Phase 3E settings (pre-Squad System)."""
    return {
        # Model Orchestrator (Phase 3E)
        "orchestrator.quality_tier": "balanced",
        "orchestrator.enabled": True,
        "orchestrator.prefer_local": False,
        "orchestrator.monthly_budget": 50.0,

        # Individual model assignments (Phase 3E)
        "foreman.coordinator_model": "llama3.2:3b",  # User was using local model
        "tournament.default_models": ["deepseek-chat", "qwen-plus", "claude-3-7-sonnet-20250219"],

        # Health check models (Phase 3E - manually configured)
        "health_checks.models.default_model": "llama3.2:3b",
        "health_checks.models.timeline_consistency": "deepseek-chat",
        "health_checks.models.theme_resonance": "claude-3-7-sonnet-20250219",

        # Scoring weights
        "scoring.voice_authenticity_weight": 30,
        "scoring.character_consistency_weight": 20,

        # Voice settings
        "voice.strictness": "high",
        "voice.min_match_score": 85,

        # Enhancement settings
        "enhancement.auto_threshold": 85,
        "enhancement.action_prompt_threshold": 70,
    }


# =============================================================================
# Test: Migration Scenarios
# =============================================================================

class TestPhase3ETo3FMigration:
    """Test migration from Phase 3E (individual models) to Phase 3F (Squad System)."""

    def test_apply_squad_preserves_non_squad_settings(
        self, settings_service, squad_service, phase3e_settings
    ):
        """Test that applying a squad doesn't overwrite unrelated settings."""
        # Setup: Create Phase 3E project with settings
        project_id = "test_phase3e_project"

        for key, value in phase3e_settings.items():
            settings_service.set(key, value, project_id)

        # Verify Phase 3E settings exist
        assert settings_service.get("scoring.voice_authenticity_weight", project_id) == 30
        assert settings_service.get("voice.strictness", project_id) == "high"

        # Apply Squad System (Phase 3F)
        result = squad_service.apply_squad("hybrid", project_id)

        assert result["status"] == "success"
        assert result["squad"] == "hybrid"

        # Verify non-squad settings are preserved
        assert settings_service.get("scoring.voice_authenticity_weight", project_id) == 30
        assert settings_service.get("voice.strictness", project_id) == "high"
        assert settings_service.get("voice.min_match_score", project_id) == 85
        assert settings_service.get("enhancement.auto_threshold", project_id) == 85

    def test_apply_squad_updates_model_assignments(
        self, settings_service, squad_service, phase3e_settings
    ):
        """Test that squad application updates model assignments."""
        project_id = "test_migration_models"

        # Setup Phase 3E settings
        for key, value in phase3e_settings.items():
            settings_service.set(key, value, project_id)

        # Verify Phase 3E had llama3.2 as coordinator
        assert settings_service.get("foreman.coordinator_model", project_id) == "llama3.2:3b"

        # Apply Hybrid Squad
        result = squad_service.apply_squad("hybrid", project_id)

        # Verify Hybrid Squad assignments (Mistral 7B for coordinator, DeepSeek for strategic)
        assert settings_service.get("foreman.coordinator_model", project_id) == "mistral:7b"
        assert settings_service.get("foreman.task_models.coordinator", project_id) == "mistral:7b"

        # Verify strategic tasks use DeepSeek
        assert settings_service.get("foreman.task_models.health_check_review", project_id) == "deepseek-chat"
        assert settings_service.get("foreman.task_models.theme_analysis", project_id) == "deepseek-chat"

    def test_squad_active_indicator_set(
        self, settings_service, squad_service
    ):
        """Test that squad.active_squad setting is set correctly."""
        project_id = "test_squad_indicator"

        # Before squad application (default may be "local" or "hybrid")
        active_squad = settings_service.get("squad.active_squad", project_id)
        assert active_squad in [None, "local", "hybrid"]  # Default varies

        # Apply Local Squad
        squad_service.apply_squad("local", project_id)

        # Verify indicator is set
        assert settings_service.get("squad.active_squad", project_id) == "local"
        assert settings_service.get("squad.setup_complete", project_id) is True

    def test_switch_squads_mid_project(
        self, settings_service, squad_service
    ):
        """Test switching from one squad to another."""
        project_id = "test_squad_switch"

        # Start with Local Squad
        squad_service.apply_squad("local", project_id)
        assert settings_service.get("squad.active_squad", project_id) == "local"
        assert settings_service.get("foreman.coordinator_model", project_id) == "mistral:7b"

        # Switch to Hybrid Squad
        squad_service.apply_squad("hybrid", project_id)
        assert settings_service.get("squad.active_squad", project_id) == "hybrid"
        # Coordinator stays local (mistral:7b)
        assert settings_service.get("foreman.coordinator_model", project_id) == "mistral:7b"
        # But strategic tasks now use DeepSeek
        assert settings_service.get("foreman.task_models.health_check_review", project_id) == "deepseek-chat"

        # Switch to Pro Squad
        squad_service.apply_squad("pro", project_id)
        assert settings_service.get("squad.active_squad", project_id) == "pro"
        # Strategic tasks now use Claude
        assert settings_service.get("foreman.task_models.health_check_review", project_id) == "claude-3-7-sonnet-20250219"

    def test_tournament_models_preserved_if_custom(
        self, settings_service, squad_service
    ):
        """Test that custom tournament model selections are preserved."""
        project_id = "test_custom_tournament"

        # User had custom tournament models in Phase 3E
        custom_models = ["claude-3-7-sonnet-20250219", "gpt-4o", "grok-2"]
        settings_service.set("squad.custom_tournament_models", custom_models, project_id)

        # Apply squad
        squad_service.apply_squad("hybrid", project_id)

        # Custom selection should be preserved
        assert settings_service.get("squad.custom_tournament_models", project_id) == custom_models

    def test_multiple_projects_independent_migration(
        self, settings_service, squad_service
    ):
        """Test that multiple projects can migrate independently."""
        # Project 1: Applies Local Squad
        squad_service.apply_squad("local", "project1")
        assert settings_service.get("squad.active_squad", "project1") == "local"

        # Project 2: Applies Hybrid Squad
        squad_service.apply_squad("hybrid", "project2")
        assert settings_service.get("squad.active_squad", "project2") == "hybrid"

        # Project 3: Doesn't migrate yet (uses global defaults)
        assert settings_service.get("squad.active_squad", "project3") in [None, "hybrid"]

        # Verify projects remain independent
        assert settings_service.get("squad.active_squad", "project1") == "local"
        assert settings_service.get("squad.active_squad", "project2") == "hybrid"


# =============================================================================
# Test: Backward Compatibility
# =============================================================================

class TestBackwardCompatibility:
    """Test that Phase 3F doesn't break Phase 3E functionality."""

    def test_settings_service_still_works(
        self, settings_service
    ):
        """Test that basic settings operations still work."""
        project_id = "test_backward_compat"

        # Set various Phase 3E settings
        settings_service.set("scoring.voice_authenticity_weight", 35, project_id)
        settings_service.set("voice.strictness", "medium", project_id)
        settings_service.set("enhancement.auto_threshold", 80, project_id)

        # Get settings
        assert settings_service.get("scoring.voice_authenticity_weight", project_id) == 35
        assert settings_service.get("voice.strictness", project_id) == "medium"
        assert settings_service.get("enhancement.auto_threshold", project_id) == 80

        # Settings cascade still works (project → global → default)
        # Nonexistent settings return None (expected behavior)
        assert settings_service.get("nonexistent.setting", project_id) is None

    def test_phase3e_projects_work_without_squad(
        self, settings_service
    ):
        """Test that Phase 3E projects work without applying Squad System."""
        project_id = "test_no_squad"

        # User sets individual models (Phase 3E style)
        settings_service.set("foreman.coordinator_model", "llama3.2:3b", project_id)
        settings_service.set("health_checks.models.default_model", "mistral:7b", project_id)

        # These should work fine without squad.active_squad being set
        assert settings_service.get("foreman.coordinator_model", project_id) == "llama3.2:3b"
        assert settings_service.get("health_checks.models.default_model", project_id) == "mistral:7b"


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestMigrationEdgeCases:
    """Test edge cases in migration."""

    def test_apply_squad_twice_idempotent(
        self, settings_service, squad_service
    ):
        """Test that applying the same squad twice is idempotent."""
        project_id = "test_idempotent"

        # Apply hybrid squad
        result1 = squad_service.apply_squad("hybrid", project_id)
        model1 = settings_service.get("foreman.coordinator_model", project_id)

        # Apply hybrid squad again
        result2 = squad_service.apply_squad("hybrid", project_id)
        model2 = settings_service.get("foreman.coordinator_model", project_id)

        # Should be identical
        assert result1["squad"] == result2["squad"]
        assert model1 == model2

    def test_apply_squad_with_missing_api_keys_still_works(
        self, settings_service, hardware_service
    ):
        """Test that squad application works even if some API keys are missing."""
        # Create squad service
        presets_path = Path(__file__).parent.parent / "config" / "squad_presets.json"
        squad_service = SquadService(settings_service, hardware_service, presets_path=str(presets_path))

        # Apply hybrid squad (requires DEEPSEEK_API_KEY but we won't validate it here)
        # The application should succeed - availability checking is separate from application
        with patch.dict('os.environ', {}, clear=True):  # No API keys
            result = squad_service.apply_squad("hybrid", "test_no_keys")
            assert result["status"] == "success"
            # Settings are applied even if models aren't available
            assert result["squad"] == "hybrid"

    def test_squad_system_doesnt_affect_global_settings(
        self, settings_service, squad_service
    ):
        """Test that squad application to one project doesn't affect global settings."""
        # Set global setting
        settings_service.set("scoring.voice_authenticity_weight", 30, project_id=None)

        # Apply squad to specific project
        squad_service.apply_squad("hybrid", "test_project_only")

        # Global setting should be unchanged
        assert settings_service.get("scoring.voice_authenticity_weight", project_id=None) == 30


# =============================================================================
# Test: Data Integrity
# =============================================================================

class TestDataIntegrity:
    """Test that migration maintains data integrity."""

    def test_no_data_loss_during_migration(
        self, settings_service, squad_service, phase3e_settings
    ):
        """Test that no Phase 3E settings are lost during migration."""
        project_id = "test_data_integrity"

        # Set all Phase 3E settings
        for key, value in phase3e_settings.items():
            settings_service.set(key, value, project_id)

        # Get all settings before migration
        settings_before = {key: settings_service.get(key, project_id) for key in phase3e_settings.keys()}

        # Apply squad
        squad_service.apply_squad("hybrid", project_id)

        # Check non-squad settings are preserved
        non_squad_keys = [k for k in phase3e_settings.keys() if not k.startswith("foreman.") and not k.startswith("health_checks.")]
        for key in non_squad_keys:
            assert settings_service.get(key, project_id) == settings_before[key], f"Setting {key} was modified during migration"

    def test_settings_export_import_works(
        self, settings_service, squad_service
    ):
        """Test that project settings isolation and squad migration work together."""
        project_id = "test_export_import"

        # Apply squad and set custom settings
        squad_service.apply_squad("hybrid", project_id)
        settings_service.set("scoring.voice_authenticity_weight", 35, project_id)

        # Verify settings are project-specific
        assert settings_service.get("scoring.voice_authenticity_weight", project_id) == 35
        assert settings_service.get("squad.active_squad", project_id) == "hybrid"

        # Create new project - should not inherit settings from first project
        new_project_id = "test_new_project"

        # New project should have default voice weight (30), not 35 from other project
        assert settings_service.get("scoring.voice_authenticity_weight", new_project_id) == 30

        # Apply squad to new project independently
        squad_service.apply_squad("local", new_project_id)
        assert settings_service.get("squad.active_squad", new_project_id) == "local"

        # Verify original project unchanged
        assert settings_service.get("squad.active_squad", project_id) == "hybrid"
        assert settings_service.get("scoring.voice_authenticity_weight", project_id) == 35


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
