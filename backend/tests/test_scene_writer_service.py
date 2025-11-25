"""
Tests for Scene Writer Service - Phase 3B Director Mode

Tests the multi-model scene generation workflow:
1. Structure Variants - 5 different chapter layout approaches
2. Scene Variants - Tournament generation (3 models × 5 strategies = 15 variants)
3. Scoring - Automatic scoring via SceneAnalyzerService
4. Hybrid Creation - Combine best elements from multiple variants

Key Principle: Creative exploration before commitment.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import time

from backend.services.scene_writer_service import (
    SceneWriterService,
    WritingStrategy,
    StructureVariant,
    SceneVariant,
    StructureGenerationResult,
    SceneGenerationResult,
    HybridRequest,
)
from backend.services.scaffold_generator_service import Scaffold
from backend.services.scene_analyzer_service import SceneAnalysisResult


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_scaffold():
    """Create a mock scaffold for scene generation."""
    return Scaffold(
        beat_number=3,
        beat_name="Catalyst",
        scaffold_content="""
        ## Chapter 3: The Catalyst

        **Strategic Context**: Mickey confronts evidence of quantum surveillance network

        **Success Criteria**:
        - Establish quantum threat
        - Show Mickey's addiction tell
        - End with cliffhanger decision

        **Continuity**: Reference Area 51 security clearance from Ch.2
        """,
        enrichment_data={"location": "Area 52 briefing room", "time": "2:00 AM"},
    )


@pytest.fixture
def mock_voice_bundle():
    """Create a mock voice bundle."""
    return {
        "gold_standard": "Q5 port hummed with residual charge...",
        "anti_patterns": ["with [adjective] precision", "like [simile]"],
        "principles": ["Embedded philosophy", "Process-over-noun"],
        "metaphor_domains": ["gambling", "surveillance", "performance"],
    }


@pytest.fixture
def mock_story_bible():
    """Create a mock story bible context."""
    return {
        "protagonist": "Mickey Bardot",
        "fatal_flaw": "Addiction to control through prediction",
        "the_lie": "Perfect knowledge prevents loss",
        "genre": "Cyber-noir techno-thriller",
        "theme": "Illusion of certainty in uncertain world",
    }


@pytest.fixture
def writer_service():
    """Create a SceneWriterService instance for testing."""
    with patch('backend.services.scene_writer_service.LLMService'), \
         patch('backend.services.scene_writer_service.get_scene_analyzer_service'):
        service = SceneWriterService()
        return service


@pytest.fixture
def mock_structure_variants():
    """Create mock structure variants."""
    return [
        StructureVariant(
            variant_id="A",
            beat_count=3,
            scene_sequence=["Opening tension", "Evidence reveal", "Cliffhanger"],
            strategic_rationale="Fast pacing, action-focused",
            pacing="fast",
            focus="action"
        ),
        StructureVariant(
            variant_id="B",
            beat_count=5,
            scene_sequence=["Setup", "Inner conflict", "Evidence", "Reaction", "Decision"],
            strategic_rationale="Character-driven, psychological depth",
            pacing="medium",
            focus="character"
        ),
        StructureVariant(
            variant_id="C",
            beat_count=4,
            scene_sequence=["Dialogue opener", "Verbal sparring", "Truth bomb", "Exit"],
            strategic_rationale="Conversation-centered tension",
            pacing="medium",
            focus="dialogue"
        ),
    ]


@pytest.fixture
def mock_scene_content():
    """Create mock scene content."""
    return """
The Q5 port at the base of Mickey's skull hummed with residual charge from overnight
surveillance duty. Area 52's fluorescent buzz cut through his consciousness—quantum
fatigue manifesting as analog pain.

Ken entered carrying two items: a manila folder and a tablet displaying satellite imagery.

"Beautiful morning," Ken said, settling into the chair across from Mickey's platform.
He opened the folder first, spreading photographs across the metal table.

Mickey's thumb found its familiar groove against his finger—three taps, pause, three more.
The addiction tell that survived decades of suppression.
"""


# =============================================================================
# Test Structure Variant Generation
# =============================================================================

class TestStructureVariantGeneration:
    """Tests for generating structure variants (chapter layout options)."""

    @pytest.mark.asyncio
    async def test_generates_five_structure_variants(
        self, writer_service, mock_scaffold, mock_story_bible
    ):
        """Test that 5 structure variants are generated."""
        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            # Mock LLM to return structure variant JSON
            mock_llm.return_value = """
            {
                "variant_id": "A",
                "beat_count": 3,
                "scene_sequence": ["Opening", "Development", "Climax"],
                "strategic_rationale": "Fast pacing",
                "pacing": "fast",
                "focus": "action"
            }
            """

            result = await writer_service.generate_structure_variants(
                scaffold=mock_scaffold,
                story_bible=mock_story_bible,
                beat_name="Catalyst"
            )

            assert isinstance(result, StructureGenerationResult)
            assert len(result.variants) >= 3  # At least 3 variants
            assert result.scene_id is not None
            assert result.beat_description is not None

    @pytest.mark.asyncio
    async def test_structure_variants_have_different_approaches(
        self, writer_service, mock_scaffold, mock_story_bible
    ):
        """Test that structure variants represent different approaches."""
        with patch.object(
            writer_service,
            'generate_structure_variants',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = StructureGenerationResult(
                scene_id="test_scene",
                beat_description="Catalyst beat",
                variants=[
                    StructureVariant("A", 3, ["Fast", "Action"], "Quick", "fast", "action"),
                    StructureVariant("B", 5, ["Slow", "Character"], "Deep", "slow", "character"),
                    StructureVariant("C", 4, ["Medium", "Dialogue"], "Balanced", "medium", "dialogue"),
                ],
                recommendation="Variant A for fast pacing"
            )

            result = await writer_service.generate_structure_variants(
                scaffold=mock_scaffold,
                story_bible=mock_story_bible,
                beat_name="Catalyst"
            )

            # Variants should have different pacing
            pacing_values = {v.pacing for v in result.variants}
            assert len(pacing_values) > 1, "Should have varied pacing"

            # Variants should have different focus
            focus_values = {v.focus for v in result.variants}
            assert len(focus_values) > 1, "Should have varied focus"

    @pytest.mark.asyncio
    async def test_structure_variant_includes_strategic_rationale(
        self, writer_service, mock_scaffold, mock_story_bible
    ):
        """Test that each variant includes strategic rationale."""
        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = """
            {
                "variant_id": "A",
                "beat_count": 3,
                "scene_sequence": ["Opening", "Build", "Payoff"],
                "strategic_rationale": "Maximize tension through compression",
                "pacing": "fast",
                "focus": "action"
            }
            """

            result = await writer_service.generate_structure_variants(
                scaffold=mock_scaffold,
                story_bible=mock_story_bible,
                beat_name="Catalyst"
            )

            for variant in result.variants:
                assert variant.strategic_rationale is not None
                assert len(variant.strategic_rationale) > 0


# =============================================================================
# Test Scene Variant Generation (Tournament)
# =============================================================================

class TestSceneVariantGeneration:
    """Tests for multi-model scene variant generation."""

    @pytest.mark.asyncio
    async def test_generates_variants_from_multiple_models(
        self, writer_service, mock_scaffold, mock_voice_bundle, mock_story_bible
    ):
        """Test that variants are generated from all tournament models."""
        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = mock_scene_content

            # Default tournament has 3 models
            result = await writer_service.generate_scene_variants(
                scaffold=mock_scaffold,
                structure_choice="A",
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible,
                strategies=[WritingStrategy.ACTION, WritingStrategy.CHARACTER]
            )

            # 3 models × 2 strategies = 6 variants
            assert len(result.variants) == 6
            assert result.total_variants == 6

            # Verify models used
            model_names = {v.model_name for v in result.variants}
            assert len(model_names) == 3, "Should use 3 different models"

    @pytest.mark.asyncio
    async def test_applies_all_five_writing_strategies(
        self, writer_service, mock_scaffold, mock_voice_bundle, mock_story_bible
    ):
        """Test that all 5 writing strategies are applied."""
        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = mock_scene_content

            result = await writer_service.generate_scene_variants(
                scaffold=mock_scaffold,
                structure_choice="A",
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible,
                strategies=list(WritingStrategy)  # All 5 strategies
            )

            # Should have variants for each strategy
            strategies_used = {v.strategy for v in result.variants}
            assert WritingStrategy.ACTION in strategies_used
            assert WritingStrategy.CHARACTER in strategies_used
            assert WritingStrategy.DIALOGUE in strategies_used
            assert WritingStrategy.BRAINSTORMING in strategies_used
            assert WritingStrategy.BALANCED in strategies_used

    @pytest.mark.asyncio
    async def test_voice_bundle_injected_into_generation(
        self, writer_service, mock_scaffold, mock_voice_bundle, mock_story_bible
    ):
        """Test that Voice Bundle is injected into scene generation prompt."""
        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = mock_scene_content

            await writer_service.generate_scene_variants(
                scaffold=mock_scaffold,
                structure_choice="A",
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible,
                strategies=[WritingStrategy.ACTION]
            )

            # Check that voice bundle elements appear in LLM prompt
            call_args = mock_llm.call_args
            prompt = call_args[1]['prompt']

            # Voice Bundle should be referenced in prompt
            assert 'gold_standard' in str(prompt).lower() or 'voice' in str(prompt).lower()

    @pytest.mark.asyncio
    async def test_tracks_generation_time(
        self, writer_service, mock_scaffold, mock_voice_bundle, mock_story_bible
    ):
        """Test that generation time is tracked for each variant."""
        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate 100ms generation
                return mock_scene_content

            mock_llm.side_effect = slow_response

            result = await writer_service.generate_scene_variants(
                scaffold=mock_scaffold,
                structure_choice="A",
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible,
                strategies=[WritingStrategy.ACTION]
            )

            for variant in result.variants:
                assert variant.generation_time > 0
                assert variant.generation_time >= 0.1  # At least 100ms

    @pytest.mark.asyncio
    async def test_handles_model_failure_gracefully(
        self, writer_service, mock_scaffold, mock_voice_bundle, mock_story_bible
    ):
        """Test that service continues if one model fails."""
        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            # First model succeeds, second fails, third succeeds
            mock_llm.side_effect = [
                mock_scene_content,
                Exception("API error"),
                mock_scene_content,
            ]

            result = await writer_service.generate_scene_variants(
                scaffold=mock_scaffold,
                structure_choice="A",
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible,
                strategies=[WritingStrategy.ACTION]  # 1 strategy × 3 models
            )

            # Should have 2 successful variants (not 3)
            assert len(result.variants) == 2


# =============================================================================
# Test Automatic Scoring
# =============================================================================

class TestAutomaticScoring:
    """Tests for automatic variant scoring."""

    @pytest.mark.asyncio
    async def test_scores_all_variants_automatically(
        self, writer_service, mock_voice_bundle, mock_story_bible
    ):
        """Test that all variants are automatically scored."""
        # Create mock variants
        variants = [
            SceneVariant("A", "Claude", WritingStrategy.ACTION, mock_scene_content, 150, 1.0),
            SceneVariant("B", "GPT-4o", WritingStrategy.CHARACTER, mock_scene_content, 160, 1.2),
            SceneVariant("C", "DeepSeek", WritingStrategy.DIALOGUE, mock_scene_content, 140, 0.8),
        ]

        with patch.object(
            writer_service.analyzer_service,
            'analyze_scene',
            new_callable=AsyncMock
        ) as mock_analyze:
            mock_analyze.return_value = SceneAnalysisResult(
                scene_id="test",
                total_score=85,
                grade="A",
                quality_level="EXCELLENT",
                violations=[],
                metaphor_analysis=None
            )

            scored_variants = await writer_service.score_all_variants(
                variants=variants,
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible
            )

            # All variants should have scores
            assert all(v.score is not None for v in scored_variants)
            assert all(v.grade is not None for v in scored_variants)
            assert all(v.analysis is not None for v in scored_variants)

    @pytest.mark.asyncio
    async def test_identifies_winner_by_highest_score(
        self, writer_service, mock_voice_bundle, mock_story_bible
    ):
        """Test that winner is identified by highest score."""
        variants = [
            SceneVariant("A", "Claude", WritingStrategy.ACTION, mock_scene_content, 150, 1.0),
            SceneVariant("B", "GPT-4o", WritingStrategy.CHARACTER, mock_scene_content, 160, 1.2),
            SceneVariant("C", "DeepSeek", WritingStrategy.DIALOGUE, mock_scene_content, 140, 0.8),
        ]

        with patch.object(
            writer_service.analyzer_service,
            'analyze_scene',
            new_callable=AsyncMock
        ) as mock_analyze:
            # Return different scores for each variant
            mock_analyze.side_effect = [
                SceneAnalysisResult("A", 85, "A", "EXCELLENT", [], None),
                SceneAnalysisResult("B", 92, "A+", "GOLD STANDARD", [], None),  # Winner
                SceneAnalysisResult("C", 78, "B+", "ACCEPTABLE", [], None),
            ]

            scored_variants = await writer_service.score_all_variants(
                variants=variants,
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible
            )

            # Variant B should have highest score
            winner = max(scored_variants, key=lambda v: v.score)
            assert winner.variant_id == "B"
            assert winner.score == 92


# =============================================================================
# Test Hybrid Creation
# =============================================================================

class TestHybridCreation:
    """Tests for creating hybrid scenes from multiple variants."""

    @pytest.mark.asyncio
    async def test_creates_hybrid_from_multiple_variants(
        self, writer_service, mock_voice_bundle, mock_story_bible
    ):
        """Test that hybrid scene is created from multiple source variants."""
        # Create source variants
        variants = [
            SceneVariant("A", "Claude", WritingStrategy.ACTION, "Opening paragraph A...", 100, 1.0),
            SceneVariant("B", "GPT-4o", WritingStrategy.CHARACTER, "Middle paragraph B...", 100, 1.0),
            SceneVariant("C", "DeepSeek", WritingStrategy.DIALOGUE, "Closing paragraph C...", 100, 1.0),
        ]

        hybrid_request = HybridRequest(
            scene_id="test_hybrid",
            sources=[
                {"variant_id": "A", "section": "opening"},
                {"variant_id": "B", "section": "middle"},
                {"variant_id": "C", "section": "closing"},
            ],
            instructions="Combine opening from A, middle from B, closing from C"
        )

        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = "Hybrid scene combining best elements..."

            hybrid_variant = await writer_service.create_hybrid(
                hybrid_request=hybrid_request,
                source_variants=variants,
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible
            )

            assert hybrid_variant is not None
            assert "Hybrid" in hybrid_variant.variant_id
            assert hybrid_variant.model_name == "Hybrid"
            assert len(hybrid_variant.content) > 0

    @pytest.mark.asyncio
    async def test_hybrid_includes_source_tracking(
        self, writer_service, mock_voice_bundle, mock_story_bible
    ):
        """Test that hybrid tracks its source variants."""
        variants = [
            SceneVariant("A", "Claude", WritingStrategy.ACTION, "Content A", 100, 1.0),
            SceneVariant("B", "GPT-4o", WritingStrategy.CHARACTER, "Content B", 100, 1.0),
        ]

        hybrid_request = HybridRequest(
            scene_id="test_hybrid",
            sources=[
                {"variant_id": "A", "section": "opening"},
                {"variant_id": "B", "section": "closing"},
            ],
            instructions="Merge A and B"
        )

        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = "Hybrid content"

            hybrid = await writer_service.create_hybrid(
                hybrid_request=hybrid_request,
                source_variants=variants,
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible
            )

            # Hybrid variant_id should reference sources
            assert "A" in hybrid.variant_id or "B" in hybrid.variant_id or "Hybrid" in hybrid.variant_id


# =============================================================================
# Test Integration Scenarios
# =============================================================================

class TestIntegrationScenarios:
    """Tests for complete scene generation workflows."""

    @pytest.mark.asyncio
    async def test_complete_scene_generation_workflow(
        self, writer_service, mock_scaffold, mock_voice_bundle, mock_story_bible
    ):
        """Test complete workflow from structure to scored variants."""
        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm, \
             patch.object(
                 writer_service.analyzer_service,
                 'analyze_scene',
                 new_callable=AsyncMock
             ) as mock_analyze:

            # Mock structure generation
            mock_llm.return_value = """
            {
                "variant_id": "A",
                "beat_count": 3,
                "scene_sequence": ["Open", "Build", "Close"],
                "strategic_rationale": "Fast pacing",
                "pacing": "fast",
                "focus": "action"
            }
            """

            # Step 1: Generate structure variants
            structure_result = await writer_service.generate_structure_variants(
                scaffold=mock_scaffold,
                story_bible=mock_story_bible,
                beat_name="Catalyst"
            )

            assert len(structure_result.variants) > 0

            # Mock scene generation
            mock_llm.return_value = mock_scene_content

            # Step 2: Generate scene variants
            scene_result = await writer_service.generate_scene_variants(
                scaffold=mock_scaffold,
                structure_choice="A",
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible,
                strategies=[WritingStrategy.ACTION]
            )

            assert len(scene_result.variants) > 0

            # Mock scoring
            mock_analyze.return_value = SceneAnalysisResult(
                scene_id="test",
                total_score=88,
                grade="A",
                quality_level="EXCELLENT",
                violations=[],
                metaphor_analysis=None
            )

            # Step 3: Score all variants
            scored_variants = await writer_service.score_all_variants(
                variants=scene_result.variants,
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible
            )

            # All steps completed successfully
            assert all(v.score is not None for v in scored_variants)
            assert max(v.score for v in scored_variants) > 0


# =============================================================================
# Test Error Handling
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in scene generation."""

    @pytest.mark.asyncio
    async def test_handles_empty_scaffold_gracefully(self, writer_service):
        """Test that empty scaffold is handled gracefully."""
        with pytest.raises(ValueError, match="scaffold|required"):
            await writer_service.generate_structure_variants(
                scaffold=None,
                story_bible={},
                beat_name="Test"
            )

    @pytest.mark.asyncio
    async def test_continues_on_partial_tournament_failure(
        self, writer_service, mock_scaffold, mock_voice_bundle, mock_story_bible
    ):
        """Test that tournament continues even if some models fail."""
        with patch.object(
            writer_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            # 2 successes, 1 failure
            mock_llm.side_effect = [
                mock_scene_content,
                Exception("Model unavailable"),
                mock_scene_content,
            ]

            result = await writer_service.generate_scene_variants(
                scaffold=mock_scaffold,
                structure_choice="A",
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible,
                strategies=[WritingStrategy.ACTION]
            )

            # Should have 2 variants (not fail completely)
            assert len(result.variants) == 2
            assert result.total_variants == 2
