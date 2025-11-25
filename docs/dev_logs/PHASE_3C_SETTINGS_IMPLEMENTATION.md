# Phase 3C: Settings-Driven Director Mode Implementation

**Date**: November 24, 2025
**Status**: Planned - Ready for Implementation
**Priority**: P0 - Critical (Blocks Universal Framework Goal)
**Estimated Effort**: 10-13 hours

---

## Executive Summary

Phase 3C implements settings-driven configuration for Director Mode, transforming hard-coded Explants-era patterns into a universal framework that works for any writer's style.

### Problem Statement

The current Director Mode implementation has **hard-coded scoring rules** that worked brilliantly for the Explants project (Mickey Bardot voice) but prevent Writers Factory from being a general-purpose tool:

| Hard-Coded Rule | Problem | Example |
|-----------------|---------|---------|
| Similes penalized (-1 each) | Some writers love similes | Literary fiction often uses similes deliberately |
| First-person italics = -2 penalty | Only matters for 3rd person | 1st person POV can use italics freely |
| Domain saturation = 30% | Too restrictive for expertise-driven characters | A doctor protagonist should use medical metaphors heavily |
| "despite the" = -1 penalty | Common in literary prose | Many accomplished writers use this transition |
| 6-pass enhancement always | Too aggressive for some writers | Conservative writers want minimal changes |

### Solution

Implement a **3-tier settings system**:

1. **Global Defaults** - Sensible starting values (current hard-coded values)
2. **Voice Bundle Settings** - Per-project configuration during Voice Calibration
3. **Runtime Resolution** - `SettingsService` resolves: Project → Global → Default

---

## Agent Feedback & Validation

### External Agent Review

An independent agent reviewed the implementation plan and provided the following assessment:

> "The agent's suggested plan is **highly detailed, technically sound, and perfectly aligns** with the requirements outlined for generalizing the Scene Analyzer and Enhancement pipeline to move away from hard-coded constraints."

### Key Validation Points

1. ✅ **Generalizing the Scoring Rubric** - `SettingsService.get_scoring_weights()` replaces hard-coded `DEFAULT_WEIGHTS`
2. ✅ **Dynamic Anti-Pattern Detection** - Two-pass system (project-specific + universal AI patterns)
3. ✅ **Generalizing Metaphor Discipline** - Dynamic thresholds for saturation and simile tolerance
4. ✅ **Dynamic Enhancement Triggering** - Configurable thresholds for Action Prompt, 6-Pass, Rewrite modes

### Review Summary

> "The suggested plan is strong because it establishes a clear architecture before refactoring existing code... The total estimated effort is ~10-13 hours."

---

## Architecture

### Settings Resolution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   Settings Resolution                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Check Voice Bundle (voice_settings.yaml)                │
│     ├─ Project-specific configuration                       │
│     └─ Generated during Voice Calibration                   │
│                                                              │
│  2. Check Global Settings (sessions.db)                     │
│     ├─ User's preferred defaults                            │
│     └─ Persists across all projects                         │
│                                                              │
│  3. Fall back to Hard-Coded Defaults                        │
│     ├─ Explants-era values                                  │
│     └─ Guaranteed to work                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

```sql
-- Global settings (in sessions.db)
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,  -- JSON serialized
    category TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Per-project overrides
CREATE TABLE project_settings (
    project_id TEXT,
    key TEXT,
    value TEXT,  -- JSON serialized
    PRIMARY KEY (project_id, key)
);
```

---

## Implementation Tasks

### Task 1: Create Settings Service ⭐ P0 CRITICAL
**Effort**: 2-3 hours
**Blocks**: All other tasks

Create `backend/services/settings_service.py`:

```python
class SettingsService:
    """
    Manages global and per-project settings.

    Resolution order:
    1. Project-specific override (in Voice Bundle)
    2. Global setting (in settings table)
    3. Default value (hard-coded)
    """

    def __init__(self, db_path: str = "workspace/sessions.db"):
        self.db_path = db_path
        self._ensure_tables()

    def get_scoring_weights(self, project_id: Optional[str] = None) -> Dict[str, int]:
        """Get scoring category weights (must sum to 100)."""
        weights = self._resolve("scoring_weights", project_id)
        # Validate sum = 100
        total = sum(weights.values())
        if total != 100:
            raise ValueError(f"Scoring weights must sum to 100, got {total}")
        return weights

    def get_anti_patterns(self, project_id: Optional[str] = None) -> Dict:
        """Get anti-pattern configuration."""
        return self._resolve("anti_patterns", project_id)

    def get_metaphor_settings(self, project_id: Optional[str] = None) -> Dict:
        """Get metaphor discipline settings."""
        return self._resolve("metaphor_settings", project_id)

    def get_enhancement_thresholds(self, project_id: Optional[str] = None) -> Dict:
        """Get enhancement mode thresholds."""
        return self._resolve("enhancement_thresholds", project_id)

    def _resolve(self, key: str, project_id: Optional[str]) -> Any:
        """Resolve setting with 3-tier priority."""
        # 1. Check Voice Bundle (if project_id provided)
        if project_id:
            voice_bundle_value = self._get_from_voice_bundle(project_id, key)
            if voice_bundle_value is not None:
                return voice_bundle_value

        # 2. Check Global Settings
        global_value = self._get_from_db(key)
        if global_value is not None:
            return global_value

        # 3. Fall back to defaults
        return self._get_default(key)
```

**Default Values** (Match current hard-coded values):

```python
DEFAULTS = {
    "scoring_weights": {
        "voice_authenticity": 30,
        "character_consistency": 20,
        "metaphor_discipline": 20,
        "anti_pattern_compliance": 15,
        "phase_appropriateness": 15,
    },
    "anti_patterns": {
        "zero_tolerance": {
            "first_person_italics": {"enabled": True, "penalty": -2},
            "with_precision": {"enabled": True, "penalty": -2},
            "computer_psychology": {"enabled": True, "penalty": -2},
            "with_obvious_adjective": {"enabled": True, "penalty": -2},
        },
        "formulaic": {
            "adverb_verb": {"enabled": True, "penalty": -1},
            "despite_the": {"enabled": True, "penalty": -1},
            "atmosphere_seemed": {"enabled": True, "penalty": -1},
            "suddenly": {"enabled": True, "penalty": -1},
        },
    },
    "metaphor_settings": {
        "saturation_threshold": 30,
        "simile_tolerance": 0,
        "penalize_similes": True,
        "min_domains_for_diversity": 3,
    },
    "enhancement_thresholds": {
        "action_prompt_threshold": 85,
        "six_pass_threshold": 70,
        "rewrite_threshold": 60,
        "italics_limit": 1,
        "sensory_anchors_per_section": 3,
        "aggressiveness": "medium",
    },
}
```

---

### Task 2: Update Voice Calibration to Generate Settings File ⭐ P0 CRITICAL
**Effort**: 1-2 hours
**Depends on**: Task 1

Modify `voice_calibration_service.py` (line 580, `generate_voice_bundle()`):

**Add new output file**: `voice_settings.yaml`

```yaml
# Auto-generated during Voice Calibration
# Writers can edit this file to customize scoring for this project
project_id: "my_novel"
version: "1.0"

scoring_weights:
  voice_authenticity: 30
  character_consistency: 20
  metaphor_discipline: 20
  anti_pattern_compliance: 15
  phase_appropriateness: 15

anti_patterns:
  zero_tolerance:
    first_person_italics:
      enabled: true        # Disable for 1st person POV
      penalty: -2
    with_precision:
      enabled: true
      penalty: -2
    computer_psychology:
      enabled: true
      penalty: -2
    with_obvious_adjective:
      enabled: true
      penalty: -2

  formulaic:
    adverb_verb:
      enabled: true
      penalty: -1
    despite_the:
      enabled: false       # EXAMPLE: Writer override
      penalty: 0
    atmosphere_seemed:
      enabled: true
      penalty: -1
    suddenly:
      enabled: true
      penalty: -1

  custom: []  # Writers can add custom patterns

metaphor_settings:
  saturation_threshold: 30      # 20-50% range
  simile_tolerance: 0           # 0-10 allowed
  penalize_similes: true        # false = similes allowed
  min_domains_for_diversity: 3

enhancement:
  action_prompt_threshold: 85
  six_pass_threshold: 70
  rewrite_threshold: 60
  italics_limit: 1              # 0-5 allowed
  sensory_anchors_per_section: 3
  aggressiveness: "medium"      # conservative|medium|aggressive
```

---

### Task 3: Refactor Scene Analyzer Service ⭐ P1 HIGH
**Effort**: 3-4 hours
**Depends on**: Tasks 1, 2

**File**: `backend/services/scene_analyzer_service.py`

#### Change 1: Remove hard-coded weights (lines 36-42)

```python
# BEFORE (hard-coded)
DEFAULT_WEIGHTS = {
    "voice_authenticity": 30,
    ...
}

# AFTER (dynamic)
def __init__(self, llm_service=None, settings_service=None):
    self.llm_service = llm_service or LLMService()
    self.settings_service = settings_service or get_settings_service()
    # Weights loaded per-call based on project_id
```

#### Change 2: Remove hard-coded patterns (lines 45-90)

```python
# BEFORE (hard-coded constants)
ZERO_TOLERANCE_PATTERNS = {...}
FORMULAIC_PATTERNS = {...}

# AFTER (dynamic loading)
def _load_patterns(self, project_id: Optional[str]) -> Tuple[Dict, Dict]:
    """Load patterns from settings, fall back to defaults."""
    patterns = self.settings_service.get_anti_patterns(project_id)

    # Filter by enabled status
    zero_tolerance = {
        name: config for name, config in patterns['zero_tolerance'].items()
        if config['enabled']
    }
    formulaic = {
        name: config for name, config in patterns['formulaic'].items()
        if config['enabled']
    }

    return zero_tolerance, formulaic
```

#### Change 3: Dynamic saturation threshold (line 473)

```python
# BEFORE (hard-coded)
saturation_threshold = 30.0

# AFTER (dynamic)
metaphor_settings = self.settings_service.get_metaphor_settings(project_id)
saturation_threshold = float(metaphor_settings['saturation_threshold'])
```

#### Change 4: Dynamic simile scoring (lines 564-575)

```python
# BEFORE (hard-coded simile penalties)
if analysis.simile_count == 0:
    simile_score = 5
elif analysis.simile_count <= 2:
    simile_score = 3

# AFTER (dynamic tolerance)
simile_tolerance = metaphor_settings['simile_tolerance']
if analysis.simile_count <= simile_tolerance:
    simile_score = 5  # Within tolerance
elif analysis.simile_count <= simile_tolerance + 2:
    simile_score = 3  # Slightly over
elif analysis.simile_count <= simile_tolerance + 4:
    simile_score = 1  # Multiple over
else:
    simile_score = 0  # Simile-heavy
```

---

### Task 4: Refactor Scene Enhancement Service ⭐ P1 HIGH
**Effort**: 2-3 hours
**Depends on**: Tasks 1, 2

**File**: `backend/services/scene_enhancement_service.py`

#### Change 1: Inject SettingsService (lines 47-48)

```python
# BEFORE (hard-coded thresholds)
ACTION_PROMPT_THRESHOLD = 85
SIX_PASS_THRESHOLD = 70

# AFTER (dynamic)
def __init__(self, llm_service=None, analyzer_service=None, settings_service=None):
    self.llm_service = llm_service or LLMService()
    self.analyzer_service = analyzer_service or get_scene_analyzer_service()
    self.settings_service = settings_service or get_settings_service()
```

#### Change 2: Dynamic threshold check (line 274)

```python
# BEFORE (hard-coded)
if score >= ACTION_PROMPT_THRESHOLD:
    return EnhancementMode.ACTION_PROMPT
elif score >= SIX_PASS_THRESHOLD:
    return EnhancementMode.SIX_PASS

# AFTER (dynamic)
thresholds = self.settings_service.get_enhancement_thresholds(project_id)
if score >= thresholds['action_prompt_threshold']:
    return EnhancementMode.ACTION_PROMPT
elif score >= thresholds['six_pass_threshold']:
    return EnhancementMode.SIX_PASS
else:
    return EnhancementMode.REWRITE
```

#### Change 3: Dynamic limits in passes (lines 715, 791)

```python
# Pass 3: Metaphor Rotation - BEFORE
max_domain_pct = 30  # Hard-coded

# Pass 3: Metaphor Rotation - AFTER
metaphor_settings = self.settings_service.get_metaphor_settings(project_id)
max_domain_pct = metaphor_settings['saturation_threshold']

# Pass 5: Italics Gate - BEFORE
TARGET: 0-1 maximum

# Pass 5: Italics Gate - AFTER
thresholds = self.settings_service.get_enhancement_thresholds(project_id)
italics_limit = thresholds['italics_limit']
```

---

### Task 5: Update VoiceBundleContext 🔵 P2 MEDIUM
**Effort**: 1 hour
**Depends on**: Task 2

**File**: `backend/services/scene_analyzer_service.py` (lines 197-236)

```python
@dataclass
class VoiceBundleContext:
    gold_standard: str
    anti_patterns: str
    phase_evolution: str
    metaphor_domains: Dict[str, List[str]]

    # NEW: Structured settings from voice_settings.yaml
    settings: Optional[Dict[str, Any]] = None

    @classmethod
    def from_directory(cls, voice_bundle_path: Path):
        """Load voice bundle from directory."""
        gold_standard = (voice_bundle_path / "Voice-Gold-Standard.md").read_text()
        anti_patterns = (voice_bundle_path / "Voice-Anti-Pattern-Sheet.md").read_text()

        # ... existing code for phase_evolution and metaphor_domains ...

        # NEW: Load settings YAML if exists
        settings_path = voice_bundle_path / "voice_settings.yaml"
        settings = None
        if settings_path.exists():
            import yaml
            with open(settings_path) as f:
                settings = yaml.safe_load(f)

        return cls(
            gold_standard=gold_standard,
            anti_patterns=anti_patterns,
            phase_evolution=phase_evolution,
            metaphor_domains=metaphor_domains,
            settings=settings,  # NEW
        )
```

---

## Benefits

### 1. Universal Framework ✅
Any writer can configure their style without forking the codebase.

**Example**: A romance writer can:
- Increase `simile_tolerance` to 5 (similes are common in romance)
- Disable `despite_the` penalty
- Increase `character_consistency` weight to 30 (relationships matter more)

### 2. Explants Still Works ✅
Default settings match current hard-coded values = zero regression.

### 3. No UI Required Yet ✅
Writers edit `voice_settings.yaml` during Voice Calibration = functional without frontend.

### 4. Backward Compatible ✅
Projects without `voice_settings.yaml` fall back to global → defaults.

### 5. Foundation for Phase 5 ✅
Settings UI can read/write to the same SQLite schema later.

---

## Testing Strategy

### Unit Tests

1. **SettingsService**:
   - Test 3-tier resolution (project → global → default)
   - Test weight validation (sum = 100)
   - Test pattern filtering (disabled patterns excluded)

2. **Scene Analyzer**:
   - Test scoring with custom weights
   - Test anti-pattern detection with overrides
   - Test simile scoring with different tolerance levels

3. **Scene Enhancement**:
   - Test threshold-based mode selection
   - Test dynamic italics limits
   - Test aggressiveness levels

### Integration Tests

1. Generate Voice Bundle with custom settings
2. Score a scene using custom patterns
3. Enhance a scene with custom thresholds
4. Verify settings from Voice Bundle override globals

---

## Rollout Plan

### Stage 1: Infrastructure (Days 1-2)
- Implement `SettingsService` (Task 1)
- Add database tables
- Write unit tests

### Stage 2: Voice Calibration Integration (Day 3)
- Update `generate_voice_bundle()` (Task 2)
- Generate `voice_settings.yaml`
- Test YAML loading in `VoiceBundleContext` (Task 5)

### Stage 3: Scene Analyzer Refactor (Days 4-5)
- Remove hard-coded constants (Task 3)
- Implement dynamic loading
- Test with multiple configurations

### Stage 4: Scene Enhancement Refactor (Day 6)
- Update threshold logic (Task 4)
- Test enhancement mode selection
- Integration testing

### Stage 5: Documentation & Validation (Day 7)
- Update API documentation
- Create writer guide for `voice_settings.yaml`
- Run full test suite
- Verify Explants compatibility

---

## Success Criteria

- [ ] SettingsService resolves settings in correct priority order
- [ ] Voice Bundle generation creates valid `voice_settings.yaml`
- [ ] Scene Analyzer uses custom weights and patterns
- [ ] Scene Enhancement respects custom thresholds
- [ ] Explants project scores identically with default settings
- [ ] Test project with custom settings produces different scores
- [ ] All tests passing
- [ ] Documentation updated

---

## Dependencies

### Existing Services
- `foreman_kb_service.py` - Already has SQLite infrastructure
- `voice_calibration_service.py` - Will generate settings file
- `scene_analyzer_service.py` - Will consume settings
- `scene_enhancement_service.py` - Will consume settings

### New Dependencies
- `pyyaml` - Already in requirements for agents.yaml parsing

### Database
- `workspace/sessions.db` - Existing database, add new tables

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing Explants scoring | High | Default values match hard-coded constants |
| Complex refactoring introduces bugs | Medium | Comprehensive unit tests, gradual rollout |
| Writers confused by YAML editing | Low | Provide clear examples, sensible defaults |
| Settings conflicts between global/project | Low | Explicit resolution order, validation |

---

## Future Enhancements (Phase 5)

Once this foundation is in place:

1. **Settings UI Panel** - Visual editor for `voice_settings.yaml`
2. **Presets System** - One-click configurations ("Literary Fiction", "Thriller", "Romance")
3. **Export/Import** - Share settings between projects
4. **Live Preview** - See scoring changes before saving settings
5. **Settings Profiles** - Multiple configurations per user

---

*This document serves as the technical specification for Phase 3C implementation.*
*All code changes should reference this document for context and validation.*
