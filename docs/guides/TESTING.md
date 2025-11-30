# Testing Guide

**Writers Factory Testing Strategy and Coverage**

This document describes the testing approach, current coverage, and guidelines for writing tests in Writers Factory.

---

## 📊 Test Coverage Status

### Backend Tests

**Current Coverage**: 4 of 19 services tested (21%)
**Total Test Lines**: 2,090 lines across 4 test files
**Framework**: pytest with AsyncMock

| Service | Test File | Lines | Tests | Status |
|---------|-----------|-------|-------|--------|
| GraphHealthService | test_graph_health_service.py | - | - | ✅ Tested |
| SceneAnalyzerService | test_scene_analyzer_service.py | 400 | 25+ | ✅ Tested |
| ModelOrchestrator | test_model_orchestrator.py | 350 | 20+ | ✅ Tested |
| ScaffoldGeneratorService | test_scaffold_generator_service.py | 593 | 20+ | ✅ Tested |
| SceneEnhancementService | test_scene_enhancement_service.py | 954 | 35+ | ✅ Tested |
| VoiceCalibrationService | test_voice_calibration_service.py | 736 | 30+ | ✅ Tested |

### Untested Services (13 remaining)

Priority for next testing phase:
1. **SceneWriterService** - Critical for Director Mode scene generation
2. **StructureVariantService** - 5 structural approaches before writing
3. **SettingsService** - Foundation of dynamic configuration
4. **ForemanKBService** - Knowledge base operations
5. **NotebookLMService** - Research integration
6. **LLMService** - Multi-provider AI integration
7. **ConsolidatorService** - KB to graph promotion
8. **GraphService** - Core graph operations
9. **FileService** - File system operations
10. **SessionService** - Session management
11. **ExportService** - Export functionality
12. **TournamentService** - Multi-model tournaments
13. **AgentRegistryService** - Agent management

### Frontend Tests

**Status**: No frontend tests yet
**Planned**: Component tests with Vitest + Testing Library

---

## 🧪 Running Tests

### Quick Start

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=backend/services --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
start htmlcov/index.html  # Windows
```

### Run Specific Test Suites

```bash
# Scene Analyzer tests
pytest tests/test_scene_analyzer_service.py -v

# Scaffold Generator tests
pytest tests/test_scaffold_generator_service.py -v

# Scene Enhancement tests
pytest tests/test_scene_enhancement_service.py -v

# Voice Calibration tests
pytest tests/test_voice_calibration_service.py -v
```

### Run Specific Test Classes

```bash
# Test only voice authenticity scoring
pytest tests/test_scene_analyzer_service.py::TestVoiceAuthenticity -v

# Test only 6-pass enhancement mode
pytest tests/test_scene_enhancement_service.py::TestSixPassMode -v

# Test only tournament execution
pytest tests/test_voice_calibration_service.py::TestTournamentExecution -v
```

### Run Tests with Output

```bash
# Show print statements
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf
```

---

## 📝 Test Structure

### Directory Layout

```
backend/tests/
├── __init__.py
├── test_graph_health_service.py      # Graph health checks
├── test_scene_analyzer_service.py    # Scene scoring (5 categories)
├── test_model_orchestrator.py        # Model selection & tiers
├── test_scaffold_generator_service.py # Scaffold generation (2-stage)
├── test_scene_enhancement_service.py # Enhancement pipeline (2 modes)
└── test_voice_calibration_service.py # Voice tournaments & bundles
```

### Test File Anatomy

Each test file follows this pattern:

```python
"""
Tests for [Service Name] - Phase 3B Director Mode

Brief description of what's being tested.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

# Import service and related classes
from backend.services.example_service import (
    ExampleService,
    DataClass1,
    DataClass2,
)

# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def example_service():
    """Create service instance for testing."""
    with patch('backend.services.example_service.dependency'):
        return ExampleService(project_id="test_project")

@pytest.fixture
def mock_data():
    """Create mock data for testing."""
    return {...}

# =============================================================================
# Test Classes (Organized by Feature)
# =============================================================================

class TestFeature1:
    """Tests for Feature 1."""

    @pytest.mark.asyncio
    async def test_scenario_1(self, example_service, mock_data):
        """Test that scenario 1 works correctly."""
        # Arrange
        # Act
        # Assert
```

---

## 🎯 Testing Principles

### 1. Test Organization

**Group by Feature, Not by Method**:
```python
# Good
class TestVoiceAuthenticity:
    """Tests for voice authenticity scoring (30 points)."""

    async def test_high_voice_score_with_good_voice(...)
    async def test_low_voice_score_with_ai_contamination(...)

# Bad
class TestSceneAnalyzerMethods:
    async def test_score_voice_authenticity(...)
    async def test_score_character_consistency(...)
```

### 2. Test Naming

**Use descriptive test names that explain the scenario**:
```python
# Good
async def test_action_prompt_mode_for_high_score(...)
async def test_six_pass_mode_for_medium_score(...)
async def test_rewrite_mode_for_low_score(...)

# Bad
async def test_mode_selection(...)
async def test_enhancement(...)
```

### 3. Fixture Usage

**Create reusable fixtures for common test data**:
```python
@pytest.fixture
def mock_scene_content():
    """Create sample scene content for testing."""
    return """
    The Q5 port at the base of Mickey's skull hummed...
    """

@pytest.fixture
def mock_voice_bundle():
    """Create a mock voice bundle for testing."""
    return {
        "gold_standard": "...",
        "anti_patterns": [...],
        "principles": [...],
    }
```

### 4. Async Testing

**Use AsyncMock for async service methods**:
```python
@pytest.mark.asyncio
async def test_async_method(self, service):
    with patch.object(service, 'async_method', new_callable=AsyncMock) as mock:
        mock.return_value = "expected_result"

        result = await service.async_method()

        assert result == "expected_result"
        assert mock.called
```

### 5. Mocking Dependencies

**Patch external dependencies to isolate unit tests**:
```python
def test_service_initialization():
    with patch('backend.services.example_service.LLMService'), \
         patch('backend.services.example_service.get_kb_service'):
        service = ExampleService(project_id="test")
        assert service is not None
```

---

## 📚 Test Examples by Service

### Scene Analyzer Service

**What it tests**: 5-category scoring system (100 points total)

```python
class TestVoiceAuthenticity:
    """Tests for voice authenticity scoring (30 points)."""

    @pytest.mark.asyncio
    async def test_high_voice_score_with_good_voice(
        self, analyzer_service, mock_scene_content, mock_voice_bundle
    ):
        """Test that authentic voice gets high score (27-30 points)."""
        with patch.object(
            analyzer_service,
            '_score_voice_authenticity',
            new_callable=AsyncMock
        ) as mock_score:
            mock_score.return_value = 29

            score = await analyzer_service._score_voice_authenticity(
                mock_scene_content,
                mock_voice_bundle
            )

            assert score >= 27
            assert score <= 30
```

**Key Tests**:
- Voice authenticity (30 pts): Detects AI contamination
- Character consistency (20 pts): Validates addiction tells, behavior patterns
- Metaphor discipline (20 pts): Detects domain saturation (>30%)
- Anti-pattern compliance (15 pts): Zero-tolerance violations
- Phase appropriateness (15 pts): Phase 4 Enhanced voice validation

### Scaffold Generator Service

**What it tests**: 2-stage scaffold workflow

```python
class TestDraftSummaryGeneration:
    """Tests for Stage 1 - Draft Summary with enrichment suggestions."""

    @pytest.mark.asyncio
    async def test_generates_draft_summary_successfully(
        self, scaffold_service, mock_beat_info, mock_character_context
    ):
        """Test that draft summary is generated with basic context."""
        with patch.object(
            scaffold_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = "Draft summary content"

            result = await scaffold_service.generate_draft_summary(
                beat_info=mock_beat_info,
                character_context=mock_character_context,
                project_id="test_project"
            )

            assert result is not None
            assert "Draft summary content" in result.summary
```

**Key Tests**:
- Draft summary generation with basic context
- Full scaffold with NotebookLM enrichment
- KB context injection from graph
- Continuity tracking (must-callback entries)
- Beat connection logic

### Scene Enhancement Service

**What it tests**: 2-mode enhancement pipeline

```python
class TestActionPromptMode:
    """Tests for Action Prompt mode (surgical fixes for high-scoring scenes)."""

    @pytest.mark.asyncio
    async def test_generates_action_prompt_with_fixes(
        self, enhancement_service, mock_scene_content, mock_analysis
    ):
        """Test that action prompt generates surgical fixes from violations."""
        action_prompt = await enhancement_service._generate_action_prompt(
            scene_id="test_scene",
            scene_content=mock_scene_content,
            analysis=mock_analysis,
            voice_bundle=mock_voice_bundle,
        )

        assert len(action_prompt.fixes) > 0
        assert action_prompt.expected_score_improvement > 0
        assert any("simile" in f.description.lower() for f in action_prompt.fixes)
```

**Key Tests**:
- Mode selection based on score thresholds (85+, 70-84, <70)
- Action Prompt: Surgical OLD → NEW fixes
- 6-Pass Enhancement: All 6 passes execute correctly
- Dynamic threshold loading from Settings Service
- Error handling and graceful degradation

### Voice Calibration Service

**What it tests**: Tournament-based voice discovery

```python
class TestTournamentExecution:
    """Tests for tournament creation and variant generation."""

    @pytest.mark.asyncio
    async def test_tournament_generates_variants_from_all_agents(
        self, calibration_service, mock_test_prompt
    ):
        """Test that tournament generates 5 variants from each agent."""
        calibration_service.llm_service.generate_response = AsyncMock(
            return_value=mock_winning_variant
        )

        result = TournamentResult(
            tournament_id="test_tournament",
            project_id="test_project",
            test_prompt=mock_test_prompt,
            test_context="Test context",
            status=TournamentStatus.RUNNING,
            selected_agents=['claude-sonnet-4', 'gpt-4o'],
        )

        await calibration_service._run_tournament(result, 5, "Test voice")

        # Should have 2 agents × 5 variants = 10 variants
        assert len(result.variants) == 10
        assert result.status == TournamentStatus.AWAITING_SELECTION
```

**Key Tests**:
- Agent configuration and API key validation
- Tournament execution (5 agents × 5 strategies = 25 variants)
- Winner selection and VoiceCalibrationDocument generation
- Voice Bundle file generation (Gold Standard, Anti-Patterns, Phase Evolution)
- KB storage with multiple keys
- Graceful handling of agent failures

---

## 🔧 Testing Utilities

### Common Mocking Patterns

**Mock LLM Service**:
```python
with patch.object(service.llm_service, 'generate_response', new_callable=AsyncMock) as mock_llm:
    mock_llm.return_value = "Expected LLM response"
    # Your test code
```

**Mock KB Service**:
```python
with patch.object(service.kb_service, 'get', new_callable=AsyncMock) as mock_kb:
    mock_kb.return_value = json.dumps({"key": "value"})
    # Your test code
```

**Mock Settings Service**:
```python
with patch('backend.services.example_service.settings_service.get') as mock_settings:
    mock_settings.return_value = 85  # Custom threshold
    # Your test code
```

### Assertion Helpers

**Check score ranges**:
```python
assert 27 <= score <= 30, "Authentic voice should score 27-30 points"
```

**Check list contents**:
```python
assert len(variants) == expected_count
assert all(isinstance(v, VoiceVariant) for v in variants)
```

**Check dictionary contents**:
```python
assert "key" in result
assert result["key"] == expected_value
```

---

## 📈 Continuous Integration

### GitHub Actions (Planned)

```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=backend/services
```

---

## 🎯 Testing Goals

### Short-Term (Next 2 Weeks)
- [ ] Test SceneWriterService (critical for Director Mode)
- [ ] Test StructureVariantService (5 structural approaches)
- [ ] Test SettingsService (configuration foundation)
- [ ] Add frontend component tests (Vitest)

### Medium-Term (Next Month)
- [ ] Achieve 50% backend service coverage (10 of 19 services)
- [ ] Add integration tests for complete workflows
- [ ] Set up CI/CD pipeline with automated testing
- [ ] Add E2E tests for critical user journeys

### Long-Term (Next Quarter)
- [ ] Achieve 80% backend service coverage
- [ ] Full frontend component coverage
- [ ] Performance testing (load tests for tournaments)
- [ ] Security testing (API key handling, file access)

---

## 📝 Contributing Tests

### Guidelines for New Tests

1. **Follow existing patterns** - Look at existing test files for structure
2. **Use descriptive names** - Test names should explain the scenario
3. **Create fixtures** - Reuse mock data across tests
4. **Mock external dependencies** - Isolate units under test
5. **Test edge cases** - Not just happy paths
6. **Add docstrings** - Explain what each test validates
7. **Keep tests focused** - One assertion per test when possible
8. **Use async patterns correctly** - @pytest.mark.asyncio + AsyncMock

### Pull Request Requirements

- [ ] All new code has corresponding tests
- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] Coverage doesn't decrease
- [ ] Tests follow naming conventions
- [ ] Fixtures are properly defined
- [ ] Async patterns used correctly

---

## 📚 Resources

**Testing Frameworks**:
- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

**Best Practices**:
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Testing Async Code](https://realpython.com/pytest-python-testing/)

**Writers Factory Testing**:
- [BACKEND_TESTING.md](BACKEND_TESTING.md) - Detailed backend test documentation
- [CONTRIBUTING.md](../reference/CONTRIBUTING.md) - Contribution guidelines

---

**Last Updated**: November 25, 2025
**Test Coverage**: 21% (4 of 19 services)
**Total Test Lines**: 2,090 lines
