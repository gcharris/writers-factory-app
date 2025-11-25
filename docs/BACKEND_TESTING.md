# Backend Testing Documentation

**Detailed Test Documentation for Writers Factory Backend Services**

This document provides in-depth testing information specific to backend services, including test patterns, mocking strategies, and service-specific testing guidelines.

---

## 📊 Current Test Coverage

### Tested Services (4 of 19)

| Service | Test File | Lines | Tests | Coverage |
|---------|-----------|-------|-------|----------|
| GraphHealthService | test_graph_health_service.py | ~200 | 15+ | ✅ High |
| SceneAnalyzerService | test_scene_analyzer_service.py | 400 | 25+ | ✅ Comprehensive |
| ModelOrchestrator | test_model_orchestrator.py | 350 | 20+ | ✅ Complete |
| ScaffoldGeneratorService | test_scaffold_generator_service.py | 593 | 20+ | ✅ Comprehensive |
| SceneEnhancementService | test_scene_enhancement_service.py | 954 | 35+ | ✅ Comprehensive |
| VoiceCalibrationService | test_voice_calibration_service.py | 736 | 30+ | ✅ Comprehensive |

**Total**: 2,090 lines of tests, 145+ test cases

---

## 🎯 Service-Specific Testing Guides

### Scene Analyzer Service

**What it tests**: 5-category 100-point scoring system

**Key Test Areas**:
1. **Voice Authenticity (30 pts)**: AI contamination detection
2. **Character Consistency (20 pts)**: Behavioral pattern validation
3. **Metaphor Discipline (20 pts)**: Domain saturation detection (>30%)
4. **Anti-Pattern Compliance (15 pts)**: Zero-tolerance violations
5. **Phase Appropriateness (15 pts)**: Voice evolution through acts

**Example Test**:
```python
@pytest.mark.asyncio
async def test_detects_ai_contamination(self, analyzer_service, mock_voice_bundle):
    """Test that AI-contaminated text gets low voice score."""
    contaminated_content = """
    The protagonist analyzed the situation with clinical precision.
    His consciousness crystallized with geometric precision.
    """

    score = await analyzer_service._score_voice_authenticity(
        contaminated_content,
        mock_voice_bundle
    )

    assert score < 24, "AI patterns should reduce voice score"
```

**Mocking Strategy**:
- Mock LLM service for scoring operations
- Mock voice bundle for consistency tests
- Use real regex patterns for anti-pattern detection

---

### Scaffold Generator Service

**What it tests**: 2-stage scaffold workflow

**Key Test Areas**:
1. **Draft Summary Generation**: Quick preview with enrichment suggestions
2. **Full Scaffold Generation**: Complete scaffold with NotebookLM enrichment
3. **KB Context Injection**: Pull decisions, constraints from graph
4. **Beat Connection Logic**: Link scaffolds to 15-beat structure
5. **Continuity Tracking**: Must-callback entries from previous scenes

**Example Test**:
```python
@pytest.mark.asyncio
async def test_notebooklm_enrichment_integration(self, scaffold_service):
    """Test that NotebookLM enrichment adds research context."""
    # Mock NotebookLM query
    scaffold_service.notebooklm_service.query = AsyncMock(
        return_value="Research: Vegas is 160 miles from Area 51"
    )

    result = await scaffold_service.generate_full_scaffold(
        beat_info=mock_beat,
        enrich_with_notebooklm=True,
        queries=["Distance from Vegas to Area 51"]
    )

    assert "160 miles" in result.scaffold_content
    assert result.enrichment_used is True
```

**Mocking Strategy**:
- Mock NotebookLM service for enrichment queries
- Mock KB service for context retrieval
- Mock LLM service for scaffold generation

---

### Scene Enhancement Service

**What it tests**: 2-mode enhancement pipeline

**Key Test Areas**:
1. **Mode Selection**: Threshold-based routing (85+, 70-84, <70)
2. **Action Prompt Mode**: Surgical OLD → NEW fixes
3. **6-Pass Enhancement**: All 6 passes execute correctly
4. **Dynamic Thresholds**: Settings Service integration
5. **Error Handling**: Graceful degradation on LLM failures

**6-Pass Enhancement Tests**:
```python
@pytest.mark.asyncio
async def test_six_pass_enhancement_executes_all_passes(
    self, enhancement_service, mock_scene_content
):
    """Test that all 6 passes execute in sequence."""
    # Mock each pass
    with patch.object(enhancement_service, '_pass_sensory_anchoring', new_callable=AsyncMock) as pass1, \
         patch.object(enhancement_service, '_pass_verb_promotion', new_callable=AsyncMock) as pass2, \
         patch.object(enhancement_service, '_pass_metaphor_rotation', new_callable=AsyncMock) as pass3, \
         patch.object(enhancement_service, '_pass_voice_embed', new_callable=AsyncMock) as pass4, \
         patch.object(enhancement_service, '_pass_italics_gate', new_callable=AsyncMock) as pass5, \
         patch.object(enhancement_service, '_pass_voice_authentication', new_callable=AsyncMock) as pass6:

        # Each pass returns a result and modified content
        pass1.return_value = (PassResult(1, "Sensory", 3, ["Added sensory"]), "content1")
        pass2.return_value = (PassResult(2, "Verb", 2, ["Promoted verbs"]), "content2")
        # ... etc

        result = await enhancement_service._apply_six_pass_mode(
            scene_id="test",
            scene_content=mock_scene_content,
            analysis=mock_analysis,
            voice_bundle=mock_voice_bundle,
            story_bible=mock_story_bible,
        )

        # Verify all passes were called
        assert all([pass1.called, pass2.called, pass3.called, pass4.called, pass5.called, pass6.called])
        assert len(result.passes_completed) == 6
```

**Mocking Strategy**:
- Mock each individual pass for 6-pass tests
- Mock LLM service for enhancement operations
- Mock Scene Analyzer for re-scoring

---

### Voice Calibration Service

**What it tests**: Tournament-based voice discovery

**Key Test Areas**:
1. **Agent Configuration**: API key validation, availability filtering
2. **Tournament Execution**: 5 agents × 5 strategies = 25 variants
3. **Winner Selection**: VoiceCalibrationDocument generation
4. **Voice Bundle Generation**: 3 markdown files (Gold Standard, Anti-Patterns, Phase Evolution)
5. **KB Storage**: Multiple key storage for voice components

**Example Test**:
```python
@pytest.mark.asyncio
async def test_tournament_generates_25_variants(self, calibration_service):
    """Test that tournament generates all variant combinations."""
    # Mock LLM to return variants
    calibration_service.llm_service.generate_response = AsyncMock(
        return_value="Sample variant content"
    )

    result = TournamentResult(
        tournament_id="test_tournament",
        project_id="test_project",
        test_prompt="Write opening scene",
        test_context="Context",
        status=TournamentStatus.RUNNING,
        selected_agents=['claude', 'gpt4', 'deepseek', 'gemini', 'mistral'],
    )

    await calibration_service._run_tournament(result, 5, "Test voice")

    # 5 agents × 5 strategies = 25 variants
    assert len(result.variants) == 25
    assert result.status == TournamentStatus.AWAITING_SELECTION

    # Verify all strategies represented
    strategies = {v.strategy for v in result.variants}
    assert strategies == {
        "ACTION_EMPHASIS",
        "CHARACTER_DEPTH",
        "DIALOGUE_FOCUS",
        "ATMOSPHERIC",
        "BALANCED"
    }
```

**Mocking Strategy**:
- Mock agents.yaml configuration
- Mock LLM service for variant generation
- Mock KB service for voice storage
- Mock file system for bundle generation

---

## 🔧 Common Testing Patterns

### Async Service Testing

```python
@pytest.mark.asyncio
async def test_async_method(self, service):
    """Test async service method."""
    with patch.object(service, 'dependency_method', new_callable=AsyncMock) as mock:
        mock.return_value = "expected"

        result = await service.async_method()

        assert result == "expected"
        assert mock.called
```

### LLM Service Mocking

```python
# Mock single response
service.llm_service.generate_response = AsyncMock(return_value="LLM output")

# Mock multiple responses in sequence
service.llm_service.generate_response = AsyncMock(
    side_effect=["Response 1", "Response 2", "Response 3"]
)

# Mock with error
service.llm_service.generate_response = AsyncMock(
    side_effect=Exception("API error")
)
```

### KB Service Mocking

```python
# Mock get operation
service.kb_service.get = AsyncMock(
    return_value=json.dumps({"key": "value"})
)

# Mock set operation
service.kb_service.set = AsyncMock()

# Verify set was called
assert service.kb_service.set.called
call_args = service.kb_service.set.call_args
assert call_args[1]['key'] == 'expected_key'
```

### Settings Service Mocking

```python
with patch('backend.services.example_service.settings_service.get') as mock_settings:
    # Mock single setting
    mock_settings.return_value = 85

    # Or mock with side_effect for different keys
    mock_settings.side_effect = lambda key, project_id: {
        "enhancement.threshold": 85,
        "enhancement.aggressiveness": "high"
    }.get(key)

    service = ExampleService(project_id="test")
    assert service.threshold == 85
```

---

## 📋 Test Checklist

When writing tests for a new service, ensure you cover:

### Basic Functionality
- [ ] Service initialization
- [ ] Happy path scenarios
- [ ] Core method functionality
- [ ] Return value correctness

### Edge Cases
- [ ] Empty/null inputs
- [ ] Invalid inputs
- [ ] Boundary conditions
- [ ] Unexpected data types

### Error Handling
- [ ] LLM service failures
- [ ] KB service failures
- [ ] Network errors
- [ ] Validation errors
- [ ] Graceful degradation

### Integration Points
- [ ] LLM service integration
- [ ] KB service integration
- [ ] Settings service integration
- [ ] NotebookLM integration (if applicable)
- [ ] Graph service integration (if applicable)

### Configuration
- [ ] Default configuration
- [ ] Custom configuration
- [ ] Dynamic threshold loading
- [ ] Project-specific settings

---

## 🎯 Testing Best Practices

### 1. Use Descriptive Test Names

```python
# Good
async def test_action_prompt_generates_fixes_for_violations(...)

# Bad
async def test_action_prompt(...)
```

### 2. Organize Tests by Feature

```python
class TestVoiceAuthenticity:
    """All tests related to voice authenticity scoring."""
    # Test methods here

class TestCharacterConsistency:
    """All tests related to character consistency scoring."""
    # Test methods here
```

### 3. Create Reusable Fixtures

```python
@pytest.fixture
def mock_scene_content():
    """Reusable scene content for multiple tests."""
    return """Scene content here..."""

@pytest.fixture
def mock_voice_bundle():
    """Reusable voice bundle for multiple tests."""
    return {...}
```

### 4. Mock External Dependencies

```python
# Isolate unit under test
with patch('backend.services.example.external_dependency'):
    result = service.method()
```

### 5. Test One Thing Per Test

```python
# Good - Tests one specific scenario
async def test_returns_error_for_empty_input(...)

# Bad - Tests multiple scenarios
async def test_input_validation(...)
```

---

## 📈 Coverage Goals

### Current Status
- **4 of 19 services tested (21%)**
- **2,090 lines of tests**
- **145+ test cases**

### Short-Term Goals (Next 2 Weeks)
- [ ] Test SceneWriterService
- [ ] Test StructureVariantService
- [ ] Test SettingsService
- Target: **7 of 19 services (37%)**

### Medium-Term Goals (Next Month)
- [ ] Test 6 more services
- Target: **13 of 19 services (68%)**

### Long-Term Goals (Next Quarter)
- [ ] Test remaining 6 services
- [ ] Add integration tests
- Target: **19 of 19 services (100%)**

---

## 🔍 Debugging Tests

### Running Single Test

```bash
pytest tests/test_example_service.py::TestClass::test_method -v -s
```

### Show Print Statements

```bash
pytest tests/ -v -s
```

### Stop on First Failure

```bash
pytest tests/ -x
```

### Run Last Failed Tests

```bash
pytest tests/ --lf
```

### Show Detailed Failure Information

```bash
pytest tests/ -v --tb=long
```

---

## 📚 Additional Resources

- [TESTING.md](TESTING.md) - General testing guide
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Last Updated**: November 25, 2025
**Test Coverage**: 21% (4 of 19 services)
**Total Test Lines**: 2,090
