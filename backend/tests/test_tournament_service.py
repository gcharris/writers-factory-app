"""
Unit tests for Tournament Service - Phase 4 Multi-Model Tournament System

Tests the tournament lifecycle, variant generation, scoring, consensus
detection, and hybrid creation.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from backend.models.tournament import (
    Tournament,
    TournamentConfig,
    TournamentRound,
    TournamentStatus,
    TournamentType,
    Variant,
    VariantStrategy,
    ScoreBreakdown,
    AgentConfig,
    ConsensusReport,
    RankedResults,
    HybridSceneConfig,
)
from backend.services.tournament_service import TournamentService


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    mock = AsyncMock()
    mock.generate_response = AsyncMock(return_value="This is a test scene variant with compelling prose.")
    return mock


@pytest.fixture
def mock_orchestrator():
    """Mock model orchestrator."""
    mock = MagicMock()
    mock.select_model = MagicMock(return_value="claude-3-5-sonnet-20241022")
    return mock


@pytest.fixture
def mock_scene_analyzer():
    """Mock scene analyzer service."""
    mock = AsyncMock()

    # Create a mock analysis result
    mock_category = MagicMock()
    mock_category.score = 25

    mock_result = MagicMock()
    mock_result.total_score = 85
    mock_result.grade = "A-"
    mock_result.categories = {
        "voice_authenticity": mock_category,
        "character_consistency": mock_category,
        "metaphor_discipline": mock_category,
        "anti_pattern_compliance": mock_category,
        "phase_appropriateness": mock_category,
    }
    mock_result.violations = []
    mock_result.action_prompt = None

    mock.analyze_scene = AsyncMock(return_value=mock_result)
    return mock


@pytest.fixture
def tournament_service(mock_llm_service, mock_orchestrator, mock_scene_analyzer):
    """Create tournament service with mocked dependencies."""
    return TournamentService(
        llm_service=mock_llm_service,
        orchestrator=mock_orchestrator,
        scene_analyzer=mock_scene_analyzer,
    )


@pytest.fixture
def sample_agents():
    """Sample agent configurations for testing."""
    return [
        AgentConfig(
            agent_id="claude",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            quality_tier="premium",
            enabled=True,
        ),
        AgentConfig(
            agent_id="gpt4",
            provider="openai",
            model="gpt-4o",
            quality_tier="premium",
            enabled=True,
        ),
        AgentConfig(
            agent_id="deepseek",
            provider="deepseek",
            model="deepseek-chat",
            quality_tier="budget",
            enabled=True,
        ),
    ]


@pytest.fixture
def sample_config(sample_agents):
    """Sample tournament configuration."""
    return TournamentConfig(
        tournament_type=TournamentType.SCENE_VARIANT,
        project_id="test_project",
        agents=sample_agents,
        strategies=[VariantStrategy.ACTION, VariantStrategy.CHARACTER, VariantStrategy.BALANCED],
        source_material="Test source material for the scene.",
        source_context="A tense confrontation in a dimly lit room.",
        max_variants_per_agent=3,
        parallel_execution=True,
        auto_score=True,
    )


# =============================================================================
# Model Tests
# =============================================================================

class TestTournamentModels:
    """Test data model classes."""

    def test_variant_strategy_description(self):
        """Test variant strategy descriptions."""
        assert "Fast pacing" in VariantStrategy.ACTION.description
        assert "internal landscape" in VariantStrategy.CHARACTER.description
        assert "Mix of elements" in VariantStrategy.BALANCED.description

    def test_tournament_config_to_dict(self, sample_config):
        """Test tournament config serialization."""
        config_dict = sample_config.to_dict()

        assert config_dict["tournament_type"] == "scene_variant"
        assert config_dict["project_id"] == "test_project"
        assert len(config_dict["agents"]) == 3
        assert len(config_dict["strategies"]) == 3

    def test_score_breakdown_creation(self):
        """Test score breakdown creation."""
        score = ScoreBreakdown(
            total_score=85,
            grade="A-",
            voice_authenticity=25,
            character_consistency=18,
            metaphor_discipline=17,
            anti_pattern_compliance=13,
            phase_appropriateness=12,
        )

        assert score.total_score == 85
        assert score.grade == "A-"

        score_dict = score.to_dict()
        assert "total_score" in score_dict
        assert "grade" in score_dict

    def test_variant_word_count(self):
        """Test variant word count property."""
        variant = Variant(
            id="test_variant_001",
            agent_id="claude",
            strategy=VariantStrategy.ACTION,
            content="This is a test scene with exactly ten words here.",
        )

        assert variant.word_count == 10

    def test_tournament_round_get_ranked(self):
        """Test tournament round ranking."""
        variants = [
            Variant(
                id="v1",
                agent_id="claude",
                strategy=VariantStrategy.ACTION,
                content="Variant 1",
                scores=ScoreBreakdown(total_score=75),
            ),
            Variant(
                id="v2",
                agent_id="gpt4",
                strategy=VariantStrategy.CHARACTER,
                content="Variant 2",
                scores=ScoreBreakdown(total_score=92),
            ),
            Variant(
                id="v3",
                agent_id="deepseek",
                strategy=VariantStrategy.BALANCED,
                content="Variant 3",
                scores=ScoreBreakdown(total_score=80),
            ),
        ]

        round_ = TournamentRound(round_number=1, variants=variants)
        ranked = round_.get_ranked_variants()

        assert ranked[0].id == "v2"  # Highest score
        assert ranked[1].id == "v3"
        assert ranked[2].id == "v1"  # Lowest score


# =============================================================================
# Service Tests
# =============================================================================

class TestTournamentService:
    """Test TournamentService methods."""

    def test_create_tournament(self, tournament_service, sample_config):
        """Test tournament creation."""
        tournament = tournament_service.create_tournament(sample_config)

        assert tournament.id.startswith("tournament_test_project_")
        assert tournament.tournament_type == TournamentType.SCENE_VARIANT
        assert tournament.status == TournamentStatus.PENDING
        assert tournament.project_id == "test_project"

    def test_get_tournament(self, tournament_service, sample_config):
        """Test tournament retrieval."""
        created = tournament_service.create_tournament(sample_config)
        retrieved = tournament_service.get_tournament(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_nonexistent_tournament(self, tournament_service):
        """Test retrieving non-existent tournament."""
        result = tournament_service.get_tournament("nonexistent_id")
        assert result is None

    def test_list_tournaments(self, tournament_service, sample_config):
        """Test listing tournaments."""
        # Create multiple tournaments
        t1 = tournament_service.create_tournament(sample_config)

        sample_config.project_id = "other_project"
        t2 = tournament_service.create_tournament(sample_config)

        # List all
        all_tournaments = tournament_service.list_tournaments()
        assert len(all_tournaments) == 2

        # Filter by project
        filtered = tournament_service.list_tournaments(project_id="test_project")
        assert len(filtered) == 1
        assert filtered[0].project_id == "test_project"

    @pytest.mark.asyncio
    async def test_run_round(self, tournament_service, sample_config):
        """Test running a tournament round."""
        tournament = tournament_service.create_tournament(sample_config)
        round_result = await tournament_service.run_round(tournament.id)

        # Should generate 9 variants (3 agents × 3 strategies)
        assert round_result.variant_count == 9
        assert round_result.round_number == 1
        assert round_result.consensus_score >= 0

        # Tournament should be awaiting selection
        assert tournament.status == TournamentStatus.AWAITING_SELECTION

    @pytest.mark.asyncio
    async def test_run_round_nonexistent_tournament(self, tournament_service):
        """Test running round on non-existent tournament."""
        with pytest.raises(ValueError, match="not found"):
            await tournament_service.run_round("nonexistent_id")

    def test_aggregate_scores(self, tournament_service):
        """Test score aggregation."""
        variants = [
            Variant(
                id="v1",
                agent_id="claude",
                strategy=VariantStrategy.ACTION,
                content="Variant 1",
                scores=ScoreBreakdown(total_score=75, grade="B"),
            ),
            Variant(
                id="v2",
                agent_id="gpt4",
                strategy=VariantStrategy.CHARACTER,
                content="Variant 2",
                scores=ScoreBreakdown(total_score=92, grade="A"),
            ),
            Variant(
                id="v3",
                agent_id="deepseek",
                strategy=VariantStrategy.BALANCED,
                content="Variant 3",
                scores=ScoreBreakdown(total_score=80, grade="B+"),
            ),
        ]

        results = tournament_service.aggregate_scores(variants)

        assert isinstance(results, RankedResults)
        assert len(results.ranked_variants) == 3
        assert results.ranked_variants[0]["variant_id"] == "v2"  # Highest
        assert results.average_score == pytest.approx(82.33, rel=0.01)
        assert results.median_score == 80

    def test_detect_consensus_high_agreement(self, tournament_service):
        """Test consensus detection with high agreement."""
        # All variants have similar scores
        variants = [
            Variant(
                id="v1",
                agent_id="claude",
                strategy=VariantStrategy.ACTION,
                content="Variant 1",
                scores=ScoreBreakdown(
                    total_score=85,
                    voice_authenticity=25,
                    character_consistency=18,
                    metaphor_discipline=17,
                    anti_pattern_compliance=13,
                    phase_appropriateness=12,
                ),
            ),
            Variant(
                id="v2",
                agent_id="gpt4",
                strategy=VariantStrategy.CHARACTER,
                content="Variant 2",
                scores=ScoreBreakdown(
                    total_score=87,
                    voice_authenticity=26,
                    character_consistency=18,
                    metaphor_discipline=18,
                    anti_pattern_compliance=13,
                    phase_appropriateness=12,
                ),
            ),
            Variant(
                id="v3",
                agent_id="deepseek",
                strategy=VariantStrategy.BALANCED,
                content="Variant 3",
                scores=ScoreBreakdown(
                    total_score=83,
                    voice_authenticity=24,
                    character_consistency=17,
                    metaphor_discipline=17,
                    anti_pattern_compliance=13,
                    phase_appropriateness=12,
                ),
            ),
        ]

        consensus = tournament_service.detect_consensus(variants)

        assert isinstance(consensus, ConsensusReport)
        assert consensus.overall_consensus >= 90  # High consensus (low spread)
        assert len(consensus.high_agreement_sections) > 0

    def test_detect_consensus_low_agreement(self, tournament_service):
        """Test consensus detection with low agreement."""
        # Variants have very different scores
        variants = [
            Variant(
                id="v1",
                agent_id="claude",
                strategy=VariantStrategy.ACTION,
                content="Variant 1",
                scores=ScoreBreakdown(
                    total_score=95,
                    voice_authenticity=28,
                    character_consistency=19,
                    metaphor_discipline=18,
                    anti_pattern_compliance=15,
                    phase_appropriateness=15,
                ),
            ),
            Variant(
                id="v2",
                agent_id="gpt4",
                strategy=VariantStrategy.CHARACTER,
                content="Variant 2",
                scores=ScoreBreakdown(
                    total_score=60,
                    voice_authenticity=18,
                    character_consistency=12,
                    metaphor_discipline=10,
                    anti_pattern_compliance=10,
                    phase_appropriateness=10,
                ),
            ),
        ]

        consensus = tournament_service.detect_consensus(variants)

        assert consensus.overall_consensus <= 70  # Low consensus (high spread)
        assert "review" in consensus.recommendation.lower() or "hybrid" in consensus.recommendation.lower()

    def test_select_winner(self, tournament_service, sample_config):
        """Test selecting tournament winner."""
        tournament = tournament_service.create_tournament(sample_config)

        # Add a mock variant
        variant = Variant(
            id="test_winner",
            agent_id="claude",
            strategy=VariantStrategy.ACTION,
            content="Winning variant content",
            scores=ScoreBreakdown(total_score=95, grade="A"),
        )
        round_ = TournamentRound(round_number=1, variants=[variant])
        tournament.rounds.append(round_)
        tournament.status = TournamentStatus.AWAITING_SELECTION

        # Select winner
        updated = tournament_service.select_winner(tournament.id, "test_winner")

        assert updated.winner_variant_id == "test_winner"
        assert updated.status == TournamentStatus.COMPLETE
        assert updated.completed_at is not None

    def test_select_winner_invalid_variant(self, tournament_service, sample_config):
        """Test selecting non-existent variant as winner."""
        tournament = tournament_service.create_tournament(sample_config)
        tournament.rounds.append(TournamentRound(round_number=1, variants=[]))
        tournament.status = TournamentStatus.AWAITING_SELECTION

        with pytest.raises(ValueError, match="not found"):
            tournament_service.select_winner(tournament.id, "nonexistent_variant")

    @pytest.mark.asyncio
    async def test_create_hybrid(self, tournament_service, sample_config):
        """Test hybrid scene creation."""
        tournament = tournament_service.create_tournament(sample_config)

        # Add variants
        variants = [
            Variant(
                id="v1",
                agent_id="claude",
                strategy=VariantStrategy.ACTION,
                content="Action-packed variant with exciting prose.",
                scores=ScoreBreakdown(total_score=85),
            ),
            Variant(
                id="v2",
                agent_id="gpt4",
                strategy=VariantStrategy.CHARACTER,
                content="Character-focused variant with deep psychology.",
                scores=ScoreBreakdown(total_score=88),
            ),
        ]
        round_ = TournamentRound(round_number=1, variants=variants)
        tournament.rounds.append(round_)

        config = HybridSceneConfig(
            tournament_id=tournament.id,
            selected_variant_ids=["v1", "v2"],
            merge_strategy="paragraph",
            target_word_count=600,
        )

        hybrid_content = await tournament_service.create_hybrid(config)

        assert hybrid_content is not None
        assert len(hybrid_content) > 0

        # Verify variants are marked as selected
        assert variants[0].selected_for_hybrid
        assert variants[1].selected_for_hybrid

    @pytest.mark.asyncio
    async def test_create_hybrid_insufficient_variants(self, tournament_service, sample_config):
        """Test hybrid creation with insufficient variants."""
        tournament = tournament_service.create_tournament(sample_config)

        # Add only one variant
        variant = Variant(
            id="v1",
            agent_id="claude",
            strategy=VariantStrategy.ACTION,
            content="Single variant",
        )
        round_ = TournamentRound(round_number=1, variants=[variant])
        tournament.rounds.append(round_)

        config = HybridSceneConfig(
            tournament_id=tournament.id,
            selected_variant_ids=["v1"],  # Only one variant
        )

        with pytest.raises(ValueError, match="at least 2"):
            await tournament_service.create_hybrid(config)


# =============================================================================
# Integration Tests
# =============================================================================

class TestTournamentIntegration:
    """Integration tests for full tournament workflow."""

    @pytest.mark.asyncio
    async def test_full_tournament_workflow(self, tournament_service, sample_config):
        """Test complete tournament workflow from creation to winner selection."""
        # 1. Create tournament
        tournament = tournament_service.create_tournament(sample_config)
        assert tournament.status == TournamentStatus.PENDING

        # 2. Run round
        round_result = await tournament_service.run_round(tournament.id)
        assert round_result.variant_count > 0
        assert tournament.status == TournamentStatus.AWAITING_SELECTION

        # 3. Get results
        results = tournament_service.get_tournament_results(tournament.id)
        assert "ranked_results" in results
        assert "consensus_report" in results

        # 4. Get top variant
        top_variant_id = results["ranked_results"]["ranked_variants"][0]["variant_id"]

        # 5. Select winner
        tournament_service.select_winner(tournament.id, top_variant_id)
        assert tournament.status == TournamentStatus.COMPLETE
        assert tournament.winner_variant_id == top_variant_id

    @pytest.mark.asyncio
    async def test_tournament_cost_tracking(self, tournament_service, sample_config):
        """Test that tournament tracks costs."""
        tournament = tournament_service.create_tournament(sample_config)
        await tournament_service.run_round(tournament.id)

        # Cost should be tracked (may be 0 with mocked service)
        assert tournament.total_cost_usd >= 0
        assert tournament.total_tokens_input >= 0
        assert tournament.total_tokens_output >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
