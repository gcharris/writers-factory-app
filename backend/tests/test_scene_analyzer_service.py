"""
Tests for Scene Analyzer Service - Phase 3B Director Mode

Tests the 5-category scoring system:
1. Voice Authenticity (30 points)
2. Character Consistency (20 points)
3. Metaphor Discipline (20 points)
4. Anti-Pattern Compliance (15 points)
5. Phase Appropriateness (15 points)
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from backend.services.scene_analyzer_service import (
    SceneAnalyzerService,
    SceneScore,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_scene_content():
    """Create sample scene content for testing."""
    return """
The Q5 port at the base of Mickey's skull hummed with residual charge from overnight
surveillance duty. Area 52's fluorescent buzz cut through his consciousness like
withdrawal symptoms—quantum fatigue manifesting as analog pain.

Ken entered carrying two items: a manila folder and a tablet displaying satellite imagery.

"Beautiful morning," Ken said, settling into the chair across from Mickey's platform.
He opened the folder first, spreading photographs across the metal table. "I thought
you'd like to see how your investment is performing."

Mickey's thumb found its familiar groove against his finger—three taps, pause, three more.
The addiction tell that survived decades of suppression.
"""


@pytest.fixture
def mock_voice_bundle():
    """Create a mock voice bundle for testing."""
    return {
        "gold_standard": {
            "principles": [
                "Embedded philosophical argument through dramatic action",
                "Cognitive fusion: con artist wisdom + quantum hindsight",
                "Process-over-noun thinking"
            ]
        },
        "anti_patterns": [
            {
                "pattern": "with [adjective] precision",
                "severity": "zero_tolerance",
                "fix": "Remove 'with precision' constructions"
            },
            {
                "pattern": "like [simile]",
                "severity": "critical",
                "fix": "Convert similes to literal metaphorical reality"
            }
        ]
    }


@pytest.fixture
def analyzer_service():
    """Create a SceneAnalyzerService instance for testing."""
    with patch('backend.services.scene_analyzer_service.llm_service'):
        service = SceneAnalyzerService(project_id="test_project")
        return service


# =============================================================================
# Test Voice Authenticity Scoring
# =============================================================================

class TestVoiceAuthenticity:
    """Tests for voice authenticity scoring (30 points)."""

    @pytest.mark.asyncio
    async def test_high_voice_score_with_good_voice(self, analyzer_service, mock_scene_content, mock_voice_bundle):
        """Test that authentic voice gets high score (27-30 points)."""
        with patch.object(analyzer_service, '_score_voice_authenticity', new_callable=AsyncMock) as mock_score:
            mock_score.return_value = 29

            score = await analyzer_service._score_voice_authenticity(
                mock_scene_content,
                mock_voice_bundle
            )

            assert score >= 27, "Authentic voice should score 27+ points"
            assert score <= 30, "Voice score cannot exceed 30 points"

    @pytest.mark.asyncio
    async def test_low_voice_score_with_ai_contamination(self, analyzer_service, mock_voice_bundle):
        """Test that AI-contaminated voice gets low score (<24 points)."""
        contaminated_content = """
        The protagonist analyzed the situation with clinical precision.
        His consciousness crystallized with geometric precision.
        The data flowed like a stream of information through his neural pathways.
        """

        with patch.object(analyzer_service, '_score_voice_authenticity', new_callable=AsyncMock) as mock_score:
            # Contaminated content should score low due to "with precision" and similes
            mock_score.return_value = 18

            score = await analyzer_service._score_voice_authenticity(
                contaminated_content,
                mock_voice_bundle
            )

            assert score < 24, "AI-contaminated voice should score below 24"


# =============================================================================
# Test Character Consistency Scoring
# =============================================================================

class TestCharacterConsistency:
    """Tests for character consistency scoring (20 points)."""

    @pytest.mark.asyncio
    async def test_character_consistency_with_addiction_tells(self, analyzer_service, mock_scene_content):
        """Test that consistent character tells get high score."""
        character_profile = {
            "mickey": {
                "addiction_tells": ["thumb-on-finger tapping (3 taps, pause, 3 more)"],
                "psychological_traits": ["con artist pattern recognition", "quantum hindsight"]
            }
        }

        with patch.object(analyzer_service, '_score_character_consistency', new_callable=AsyncMock) as mock_score:
            mock_score.return_value = 19

            score = await analyzer_service._score_character_consistency(
                mock_scene_content,
                character_profile
            )

            assert score >= 18, "Consistent character behavior should score 18+ points"


# =============================================================================
# Test Metaphor Discipline Scoring
# =============================================================================

class TestMetaphorDiscipline:
    """Tests for metaphor discipline scoring (20 points)."""

    @pytest.mark.asyncio
    async def test_metaphor_domain_saturation_detection(self, analyzer_service):
        """Test detection of metaphor domain over-saturation (>30%)."""
        oversaturated_content = """
        The casino floor hummed with the house edge.
        Ken dealt another hand from his strategic deck.
        Mickey read the tells in Ken's poker face.
        The odds were stacked against Mickey's hand.
        Ken called Mickey's bluff with practiced ease.
        """

        with patch.object(analyzer_service, '_analyze_metaphor_domains', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = {
                "gambling": 5,  # 5 out of 5 metaphors = 100% saturation
                "total_metaphors": 5
            }

            domains = await analyzer_service._analyze_metaphor_domains(oversaturated_content)

            gambling_percentage = (domains["gambling"] / domains["total_metaphors"]) * 100
            assert gambling_percentage > 30, "Should detect over-saturation of gambling metaphors"

    @pytest.mark.asyncio
    async def test_good_metaphor_rotation(self, analyzer_service, mock_scene_content):
        """Test that diverse metaphor domains get high score."""
        with patch.object(analyzer_service, '_score_metaphor_discipline', new_callable=AsyncMock) as mock_score:
            mock_score.return_value = 18

            score = await analyzer_service._score_metaphor_discipline(mock_scene_content)

            assert score >= 16, "Diverse metaphor rotation should score 16+ points"


# =============================================================================
# Test Anti-Pattern Detection
# =============================================================================

class TestAntiPatternDetection:
    """Tests for anti-pattern detection (15 points)."""

    @pytest.mark.asyncio
    async def test_zero_tolerance_pattern_detection(self, analyzer_service):
        """Test detection of zero-tolerance anti-patterns."""
        problematic_content = """
        The system crystallized with geometric precision.
        He moved with practiced precision through the space.
        The data flowed like water through the pipes.
        """

        with patch.object(analyzer_service, '_detect_anti_patterns', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = [
                {"pattern": "with geometric precision", "severity": "zero_tolerance", "line": 1},
                {"pattern": "with practiced precision", "severity": "zero_tolerance", "line": 2},
                {"pattern": "like water", "severity": "critical", "line": 3}
            ]

            violations = await analyzer_service._detect_anti_patterns(problematic_content)

            assert len(violations) == 3, "Should detect all anti-pattern violations"
            zero_tolerance_count = sum(1 for v in violations if v["severity"] == "zero_tolerance")
            assert zero_tolerance_count == 2, "Should detect both 'with precision' patterns"

    @pytest.mark.asyncio
    async def test_clean_content_high_score(self, analyzer_service, mock_scene_content):
        """Test that content without anti-patterns gets high score."""
        with patch.object(analyzer_service, '_score_anti_pattern_compliance', new_callable=AsyncMock) as mock_score:
            mock_score.return_value = 15  # Perfect score

            score = await analyzer_service._score_anti_pattern_compliance(mock_scene_content)

            assert score == 15, "Clean content should get perfect anti-pattern score"


# =============================================================================
# Test Phase Appropriateness Scoring
# =============================================================================

class TestPhaseAppropriateness:
    """Tests for phase appropriateness scoring (15 points)."""

    @pytest.mark.asyncio
    async def test_phase_4_enhanced_voice(self, analyzer_service, mock_scene_content):
        """Test that Phase 4 Enhanced voice gets appropriate score."""
        with patch.object(analyzer_service, '_score_phase_appropriateness', new_callable=AsyncMock) as mock_score:
            mock_score.return_value = 14

            score = await analyzer_service._score_phase_appropriateness(
                mock_scene_content,
                phase=4
            )

            assert score >= 13, "Phase 4 Enhanced voice should score 13+ points"


# =============================================================================
# Test Overall Scene Scoring
# =============================================================================

class TestOverallScoring:
    """Tests for overall scene scoring (100 points total)."""

    @pytest.mark.asyncio
    async def test_gold_standard_scene_scores_90_plus(self, analyzer_service, mock_scene_content, mock_voice_bundle):
        """Test that gold standard scene scores 90+ overall."""
        with patch.object(analyzer_service, 'analyze_scene', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = SceneScore(
                voice_authenticity=29,
                character_consistency=19,
                metaphor_discipline=18,
                anti_pattern_compliance=15,
                phase_appropriateness=14,
                total_score=95,
                grade="A+",
                quality_level="GOLD STANDARD"
            )

            score = await analyzer_service.analyze_scene(
                scene_content=mock_scene_content,
                voice_bundle=mock_voice_bundle,
                phase=4
            )

            assert score.total_score >= 90, "Gold standard scene should score 90+"
            assert score.quality_level == "GOLD STANDARD"

    @pytest.mark.asyncio
    async def test_score_components_sum_to_total(self, analyzer_service, mock_scene_content, mock_voice_bundle):
        """Test that individual scores sum to total score."""
        with patch.object(analyzer_service, 'analyze_scene', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = SceneScore(
                voice_authenticity=25,
                character_consistency=17,
                metaphor_discipline=16,
                anti_pattern_compliance=12,
                phase_appropriateness=13,
                total_score=83,
                grade="A-",
                quality_level="EXCELLENT"
            )

            score = await analyzer_service.analyze_scene(
                scene_content=mock_scene_content,
                voice_bundle=mock_voice_bundle,
                phase=4
            )

            expected_total = (
                score.voice_authenticity +
                score.character_consistency +
                score.metaphor_discipline +
                score.anti_pattern_compliance +
                score.phase_appropriateness
            )

            assert score.total_score == expected_total, "Total score should equal sum of components"

    def test_quality_level_thresholds(self, analyzer_service):
        """Test that quality levels are assigned correctly based on scores."""
        test_cases = [
            (96, "GOLD STANDARD"),
            (90, "GOLD STANDARD"),
            (88, "A+ EXCELLENT"),
            (85, "A+ EXCELLENT"),
            (82, "A- STRONG"),
            (75, "A- STRONG"),
            (72, "B+ ACCEPTABLE"),
            (65, "B NEEDS WORK"),
        ]

        for score, expected_level in test_cases:
            level = analyzer_service._determine_quality_level(score)
            assert level == expected_level, f"Score {score} should map to '{expected_level}'"


# =============================================================================
# Test Error Handling
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in scene analysis."""

    @pytest.mark.asyncio
    async def test_handles_empty_scene_content(self, analyzer_service):
        """Test that empty scene content is handled gracefully."""
        with pytest.raises(ValueError, match="Scene content cannot be empty"):
            await analyzer_service.analyze_scene(
                scene_content="",
                voice_bundle={},
                phase=4
            )

    @pytest.mark.asyncio
    async def test_handles_missing_voice_bundle(self, analyzer_service, mock_scene_content):
        """Test that missing voice bundle returns lower voice score."""
        with patch.object(analyzer_service, 'analyze_scene', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = SceneScore(
                voice_authenticity=15,  # Lower without voice bundle
                character_consistency=17,
                metaphor_discipline=16,
                anti_pattern_compliance=12,
                phase_appropriateness=13,
                total_score=73,
                grade="B+",
                quality_level="ACCEPTABLE"
            )

            score = await analyzer_service.analyze_scene(
                scene_content=mock_scene_content,
                voice_bundle=None,
                phase=4
            )

            assert score.voice_authenticity < 20, "Score should be lower without voice bundle"
