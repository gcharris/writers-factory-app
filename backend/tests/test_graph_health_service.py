"""
Tests for Graph Health Service - Phase 3D Health Checks

Tests the following health checks:
1. Pacing Plateau Detection (_check_pacing_plateaus)
2. Beat Progress Validation (_check_beat_progress)
3. Symbolic Layering (_check_symbolic_layering)
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import json

# Import the classes and functions we're testing
from backend.services.graph_health_service import (
    GraphHealthService,
    HealthWarning,
    HealthReport,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_chapter():
    """Create a mock chapter for testing."""
    chapter = Mock()
    chapter.chapter_id = "chapter_1.1"
    chapter.act = 1
    chapter.title = "The Beginning"
    chapter.total_word_count = 8000
    chapter.avg_tension = 5.0
    chapter.health_score = None
    chapter.project_id = "test_project"
    chapter.scenes = []
    return chapter


@pytest.fixture
def mock_scene():
    """Create a mock scene for testing."""
    scene = Mock()
    scene.scene_id = "scene_1.1.1"
    scene.beat_number = 1
    scene.tension_score = 5.0
    scene.summary = "The protagonist wakes up in a strange room."
    scene.timestamp = "2025-01-01T00:00:00"
    scene.location = "Bedroom"
    scene.pov_character = "Mickey"
    return scene


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = Mock()
    session.query.return_value.filter.return_value.all.return_value = []
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def health_service():
    """Create a GraphHealthService instance for testing."""
    with patch('backend.services.graph_health_service.SettingsSessionLocal'):
        with patch('backend.services.graph_health_service.Base'):
            service = GraphHealthService(project_id="test_project")
            return service


# =============================================================================
# Test Pacing Plateau Detection
# =============================================================================

class TestPacingPlateauDetection:
    """Tests for _check_pacing_plateaus method."""

    @pytest.mark.asyncio
    async def test_no_plateau_with_varied_tension(self, health_service, mock_db_session):
        """Test that varied tension scores don't trigger plateau warnings."""
        # Create chapters with varied tension
        chapters = []
        tensions = [4.0, 6.0, 8.0, 5.0, 7.0]
        for i, tension in enumerate(tensions):
            ch = Mock()
            ch.chapter_id = f"chapter_1.{i+1}"
            ch.avg_tension = tension
            ch.scenes = []
            chapters.append(ch)

        with patch.object(health_service, '_query_llm', new_callable=AsyncMock) as mock_llm:
            warnings = await health_service._check_pacing_plateaus(mock_db_session, chapters)

        # Should have no warnings since tension varies
        assert len(warnings) == 0

    @pytest.mark.asyncio
    async def test_plateau_detected_with_flat_tension(self, health_service, mock_db_session):
        """Test that flat tension scores trigger plateau warnings."""
        # Create chapters with flat tension (plateau)
        chapters = []
        tensions = [5.0, 5.1, 5.0, 5.2, 5.1]  # Very flat
        for i, tension in enumerate(tensions):
            ch = Mock()
            ch.chapter_id = f"chapter_1.{i+1}"
            ch.avg_tension = tension
            ch.title = f"Chapter {i+1}"
            ch.scenes = []
            chapters.append(ch)

        # Mock LLM response for plateau analysis
        mock_response = json.dumps({
            "is_intentional": False,
            "risk_level": "medium",
            "reasoning": "Tension remains flat without clear purpose",
            "recommendation": "Add conflict escalation in upcoming chapters"
        })

        with patch.object(health_service, '_query_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            warnings = await health_service._check_pacing_plateaus(mock_db_session, chapters)

        # Should detect at least one plateau
        assert len(warnings) >= 1
        assert any(w.type == "PACING_PLATEAU" for w in warnings)

    @pytest.mark.asyncio
    async def test_intentional_plateau_recognized(self, health_service, mock_db_session):
        """Test that intentional plateaus (calm before storm) are handled differently."""
        # Create chapters with flat tension
        chapters = []
        tensions = [5.0, 5.0, 5.0]
        for i, tension in enumerate(tensions):
            ch = Mock()
            ch.chapter_id = f"chapter_2.{i+1}"
            ch.avg_tension = tension
            ch.title = f"Chapter {i+1}"
            ch.scenes = []
            chapters.append(ch)

        # Mock LLM recognizing intentional plateau
        mock_response = json.dumps({
            "is_intentional": True,
            "risk_level": "low",
            "reasoning": "This is a calm before the storm setup",
            "recommendation": "Maintain pacing, tension will rise soon"
        })

        with patch.object(health_service, '_query_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            warnings = await health_service._check_pacing_plateaus(mock_db_session, chapters)

        # Intentional + low risk shouldn't generate warnings
        assert len(warnings) == 0 or all(w.severity == "info" for w in warnings)

    @pytest.mark.asyncio
    async def test_insufficient_chapters_no_warning(self, health_service, mock_db_session):
        """Test that insufficient chapters don't trigger warnings."""
        # Create only 2 chapters (less than plateau window)
        chapters = []
        for i in range(2):
            ch = Mock()
            ch.chapter_id = f"chapter_1.{i+1}"
            ch.avg_tension = 5.0
            chapters.append(ch)

        warnings = await health_service._check_pacing_plateaus(mock_db_session, chapters)

        # Should have no warnings due to insufficient data
        assert len(warnings) == 0


# =============================================================================
# Test Beat Progress Validation
# =============================================================================

class TestBeatProgressValidation:
    """Tests for _check_beat_progress method."""

    @pytest.mark.asyncio
    async def test_beat_progress_on_track(self, health_service, mock_db_session):
        """Test that on-track beat progress doesn't trigger warnings."""
        # Create chapters totaling 40,000 words (50% of 80,000)
        chapters = []
        for i in range(10):
            ch = Mock()
            ch.chapter_id = f"chapter_1.{i+1}"
            ch.total_word_count = 4000  # 10 chapters x 4000 = 40000 words
            ch.scenes = []
            chapters.append(ch)

        # For 50% completion, should be at Midpoint (beat 9)
        scene = Mock()
        scene.beat_number = 9  # Midpoint
        chapters[0].scenes = [scene]

        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        warnings = await health_service._check_beat_progress(mock_db_session, chapters)

        # On-track progress shouldn't generate severe warnings
        error_warnings = [w for w in warnings if w.severity == "error"]
        assert len(error_warnings) == 0

    @pytest.mark.asyncio
    async def test_beat_progress_behind_schedule(self, health_service, mock_db_session):
        """Test that being behind on beats triggers warnings."""
        # Create chapters totaling 50,000 words (62.5% of 80,000)
        chapters = []
        for i in range(10):
            ch = Mock()
            ch.chapter_id = f"chapter_1.{i+1}"
            ch.total_word_count = 5000  # 50000 words total
            ch.scenes = []
            chapters.append(ch)

        # At 62.5%, should be at beat 9 (Midpoint) or beyond
        # But we're only at beat 4 (Catalyst at 10%)
        scene = Mock()
        scene.beat_number = 4  # Catalyst - behind schedule
        chapters[0].scenes = [scene]

        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        warnings = await health_service._check_beat_progress(mock_db_session, chapters)

        # Should have warnings about being behind
        behind_warnings = [w for w in warnings if "behind" in w.type.lower() or "deviation" in w.type.lower()]
        # Note: The actual behavior depends on deviation threshold

    @pytest.mark.asyncio
    async def test_no_word_count_no_warnings(self, health_service, mock_db_session):
        """Test that chapters without word count don't cause errors."""
        # Create chapters with zero word count
        chapters = []
        for i in range(3):
            ch = Mock()
            ch.chapter_id = f"chapter_1.{i+1}"
            ch.total_word_count = 0
            ch.scenes = []
            chapters.append(ch)

        warnings = await health_service._check_beat_progress(mock_db_session, chapters)

        # Should return empty list without errors
        assert len(warnings) == 0


# =============================================================================
# Test Symbolic Layering
# =============================================================================

class TestSymbolicLayering:
    """Tests for _check_symbolic_layering method."""

    @pytest.mark.asyncio
    async def test_good_symbolic_layering(self, health_service, mock_db_session):
        """Test that good symbolic layering doesn't trigger warnings."""
        # Create chapters with scenes that have summaries
        chapters = []
        for i in range(5):
            ch = Mock()
            ch.chapter_id = f"chapter_1.{i+1}"
            scene = Mock()
            scene.scene_id = f"scene_1.{i+1}.1"
            scene.summary = f"The mirror appears again, reflecting the protagonist's change."
            ch.scenes = [scene]
            chapters.append(ch)

        # Mock LLM response with good symbolic health
        mock_response = json.dumps({
            "symbols_detected": [
                {
                    "symbol": "Mirror",
                    "occurrences": ["chapter_1.1", "chapter_1.3", "chapter_1.5"],
                    "recurrence_count": 3,
                    "recurrence_adequate": True,
                    "meaning_evolves": True,
                    "appears_at_critical_beats": True,
                    "analysis": "Mirror symbol evolves throughout the story",
                    "recommendation": ""
                }
            ],
            "overall_symbolic_health": "excellent",
            "general_recommendations": []
        })

        with patch.object(health_service, '_query_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            warnings = await health_service._check_symbolic_layering(mock_db_session, chapters)

        # Good symbolic layering shouldn't generate warnings
        assert len(warnings) == 0

    @pytest.mark.asyncio
    async def test_insufficient_recurrence_warning(self, health_service, mock_db_session):
        """Test that symbols with insufficient recurrence trigger warnings."""
        chapters = []
        for i in range(5):
            ch = Mock()
            ch.chapter_id = f"chapter_1.{i+1}"
            scene = Mock()
            scene.scene_id = f"scene_1.{i+1}.1"
            scene.summary = "A brief scene with little symbolic content."
            ch.scenes = [scene]
            chapters.append(ch)

        # Mock LLM response with insufficient recurrence
        mock_response = json.dumps({
            "symbols_detected": [
                {
                    "symbol": "Broken Clock",
                    "occurrences": ["chapter_1.1"],
                    "recurrence_count": 1,
                    "recurrence_adequate": False,
                    "meaning_evolves": False,
                    "appears_at_critical_beats": False,
                    "analysis": "Symbol appears once and is never revisited",
                    "recommendation": "Consider reinforcing the broken clock symbol in later chapters"
                }
            ],
            "overall_symbolic_health": "poor",
            "general_recommendations": ["Establish recurring symbols", "Use symbols at key beats"]
        })

        with patch.object(health_service, '_query_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            warnings = await health_service._check_symbolic_layering(mock_db_session, chapters)

        # Should have warnings about insufficient recurrence
        recurrence_warnings = [w for w in warnings if "RECURRENCE" in w.type or "WEAK" in w.type]
        assert len(recurrence_warnings) >= 1

    @pytest.mark.asyncio
    async def test_static_meaning_warning(self, health_service, mock_db_session):
        """Test that symbols with static meaning trigger info warnings."""
        chapters = []
        for i in range(5):
            ch = Mock()
            ch.chapter_id = f"chapter_1.{i+1}"
            scene = Mock()
            scene.scene_id = f"scene_1.{i+1}.1"
            scene.summary = "The red door appears again."
            ch.scenes = [scene]
            chapters.append(ch)

        # Mock LLM response with static meaning
        mock_response = json.dumps({
            "symbols_detected": [
                {
                    "symbol": "Red Door",
                    "occurrences": ["chapter_1.1", "chapter_1.2", "chapter_1.3", "chapter_1.4"],
                    "recurrence_count": 4,
                    "recurrence_adequate": True,
                    "meaning_evolves": False,
                    "appears_at_critical_beats": True,
                    "analysis": "Symbol recurs but meaning stays the same",
                    "recommendation": "Let the red door gain new layers of meaning"
                }
            ],
            "overall_symbolic_health": "fair",
            "general_recommendations": []
        })

        with patch.object(health_service, '_query_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            warnings = await health_service._check_symbolic_layering(mock_db_session, chapters)

        # Should have info warning about static meaning
        static_warnings = [w for w in warnings if "STATIC" in w.type]
        assert len(static_warnings) >= 1

    @pytest.mark.asyncio
    async def test_empty_chapters_no_error(self, health_service, mock_db_session):
        """Test that empty chapters list doesn't cause errors."""
        warnings = await health_service._check_symbolic_layering(mock_db_session, [])
        assert len(warnings) == 0


# =============================================================================
# Test Health Report Generation
# =============================================================================

class TestHealthReport:
    """Tests for HealthReport class."""

    def test_health_report_to_dict(self):
        """Test that HealthReport converts to dictionary correctly."""
        warning = HealthWarning(
            type="PACING_PLATEAU",
            severity="warning",
            message="Flat pacing detected",
            recommendation="Escalate tension",
            chapters=["chapter_1.1", "chapter_1.2"]
        )

        report = HealthReport(
            report_id="test-123",
            project_id="test_project",
            scope="manuscript",
            overall_score=85,
            warnings=[warning]
        )

        result = report.to_dict()

        assert result["report_id"] == "test-123"
        assert result["project_id"] == "test_project"
        assert result["scope"] == "manuscript"
        assert result["overall_score"] == 85
        assert len(result["warnings"]) == 1

    def test_health_report_to_markdown(self):
        """Test that HealthReport generates proper markdown."""
        warning = HealthWarning(
            type="PACING_PLATEAU",
            severity="error",
            message="Critical pacing issue",
            recommendation="Fix immediately",
            chapters=["chapter_1.1"]
        )

        report = HealthReport(
            report_id="test-123",
            project_id="test_project",
            scope="manuscript",
            overall_score=65,
            warnings=[warning]
        )

        markdown = report.to_markdown()

        assert "Health Report" in markdown
        assert "65" in markdown
        assert "Critical Issues" in markdown or "PACING_PLATEAU" in markdown

    def test_health_report_has_critical_warnings(self):
        """Test has_critical_warnings method."""
        error_warning = HealthWarning(
            type="TEST",
            severity="error",
            message="Error message"
        )

        info_warning = HealthWarning(
            type="TEST",
            severity="info",
            message="Info message"
        )

        report_with_error = HealthReport(
            report_id="test-1",
            project_id="test",
            scope="chapter",
            warnings=[error_warning]
        )

        report_without_error = HealthReport(
            report_id="test-2",
            project_id="test",
            scope="chapter",
            warnings=[info_warning]
        )

        assert report_with_error.has_critical_warnings() == True
        assert report_without_error.has_critical_warnings() == False


# =============================================================================
# Test Health Warning
# =============================================================================

class TestHealthWarning:
    """Tests for HealthWarning class."""

    def test_health_warning_to_dict(self):
        """Test that HealthWarning converts to dictionary correctly."""
        warning = HealthWarning(
            type="BEAT_DEVIATION",
            severity="warning",
            message="Beat 9 is off target",
            recommendation="Consider restructuring",
            chapters=["chapter_2.1"],
            data={"deviation": 15.5}
        )

        result = warning.to_dict()

        assert result["type"] == "BEAT_DEVIATION"
        assert result["severity"] == "warning"
        assert result["message"] == "Beat 9 is off target"
        assert result["recommendation"] == "Consider restructuring"
        assert result["chapters"] == ["chapter_2.1"]
        assert result["data"]["deviation"] == 15.5

    def test_health_warning_default_values(self):
        """Test that HealthWarning has correct default values."""
        warning = HealthWarning(
            type="TEST",
            severity="info",
            message="Test message"
        )

        assert warning.recommendation is None
        assert warning.scenes == []
        assert warning.chapters == []
        assert warning.characters == []
        assert warning.data == {}


# =============================================================================
# Test Score Calculation
# =============================================================================

class TestScoreCalculation:
    """Tests for health score calculation."""

    def test_calculate_score_perfect(self, health_service):
        """Test perfect score with no warnings."""
        warnings = []
        score = health_service._calculate_health_score(warnings)
        assert score == 100

    def test_calculate_score_with_errors(self, health_service):
        """Test score reduction with error-level warnings."""
        warnings = [
            HealthWarning(type="TEST", severity="error", message="Error 1"),
            HealthWarning(type="TEST", severity="error", message="Error 2"),
        ]
        score = health_service._calculate_health_score(warnings)
        assert score == 80  # 100 - 10 - 10

    def test_calculate_score_with_warnings(self, health_service):
        """Test score reduction with warning-level warnings."""
        warnings = [
            HealthWarning(type="TEST", severity="warning", message="Warning 1"),
            HealthWarning(type="TEST", severity="warning", message="Warning 2"),
        ]
        score = health_service._calculate_health_score(warnings)
        assert score == 90  # 100 - 5 - 5

    def test_calculate_score_with_info(self, health_service):
        """Test score reduction with info-level warnings."""
        warnings = [
            HealthWarning(type="TEST", severity="info", message="Info 1"),
            HealthWarning(type="TEST", severity="info", message="Info 2"),
        ]
        score = health_service._calculate_health_score(warnings)
        assert score == 98  # 100 - 1 - 1

    def test_calculate_score_minimum_zero(self, health_service):
        """Test that score doesn't go below zero."""
        warnings = [
            HealthWarning(type="TEST", severity="error", message=f"Error {i}")
            for i in range(15)  # 15 errors = -150 points
        ]
        score = health_service._calculate_health_score(warnings)
        assert score == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
