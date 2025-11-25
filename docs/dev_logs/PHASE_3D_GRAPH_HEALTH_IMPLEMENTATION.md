# Phase 3D: Graph Health Service Implementation

**Date**: November 24, 2025
**Status**: ✅ Settings Updated → 🚧 In Progress (Schema Extension)
**Priority**: P1 - High (Completes Director Mode Quality Loop)
**Estimated Effort**: 12-15 hours
**Depends On**: ✅ Phase 3C (Settings Service - Complete)

---

## 🎯 Strategic Decisions (Final Architecture)

**Context**: Given no resource or time limitations and access to capable AI agents, these decisions prioritize **maximum accuracy, deep structural integrity, and longitudinal analysis**.

### Decision 1: Timeline Consistency - Full LLM Semantic Analysis ✅

**Choice**: Implement full LLM-powered semantic analysis (not simplified regex checks)

**Rationale**:
- Timeline conflicts are nuanced: "Character arrives at sunset" vs. "It's still noon" requires understanding context
- Dropped threads detection needs semantic reasoning: "The missing documents" mentioned in Ch. 2 should be resolved
- World rules consistency requires natural language understanding

**Implementation**:
- Use Ollama LLM to analyze scene pairs for semantic conflicts
- Confidence threshold: 0.7 (configurable via settings)
- Check character locations, world rules, dropped threads
- Store conflict details with semantic explanation

```python
async def _check_timeline_semantic(self, scenes: List[Scene]) -> List[HealthWarning]:
    """Full LLM-powered semantic timeline analysis."""
    # Build context from previous scenes
    # Query LLM: "Does this scene contradict established timeline/world rules?"
    # Return warnings with confidence scores
```

---

### Decision 2: Theme Resonance - Hybrid LLM + Manual Override ✅

**Choice**: Automated LLM scoring with manual writer override capability

**Rationale**:
- Thematic success is subjective - LLM provides baseline scoring
- Writers may have subtle thematic intent the LLM misses
- Continuous feedback > purely manual scoring
- Override system respects writer autonomy while maintaining automation benefits

**Implementation**:
- Default: LLM auto-scores theme resonance at critical beats (0-10 scale)
- Writers can override scores via `/health/theme/override` endpoint
- Overrides stored in `ThemeResonanceOverride` table
- Health checks respect manual overrides over LLM scores

```python
# In check_theme_resonance():
resonance = self._get_theme_score(beat_id, theme_id)
# First checks ThemeResonanceOverride table
# Falls back to LLM auto-score if no override exists
```

---

### Decision 3: Check Frequency - Auto-Trigger After Every Chapter ✅

**Choice**: Automatically run health checks after each chapter assembly (customizable via Foreman proactiveness)

**Rationale**:
- Early detection prevents compound structural errors
- Cheaper to fix issues immediately vs. rewriting 10 chapters later
- Foreman proactiveness setting provides escape hatch for writers who prefer passive mode
- Background execution doesn't interrupt workflow

**Implementation**:
- Auto-trigger: `on_chapter_complete()` hook in Foreman
- Respects `foreman.proactiveness` setting:
  - **High**: Show all warnings, block on critical errors
  - **Medium** (default): Show warnings, allow continue with acknowledgment
  - **Low**: Silent mode, store reports but don't interrupt
- Reports always stored for historical analysis

---

### Decision 4: Report Storage - SQLite Persistence for Longitudinal Analysis ✅

**Choice**: Store all health reports in SQLite with 365-day retention

**Rationale**:
- Enables trend analysis: "Chapter pacing improving over time?"
- Supports A/B testing: "Did tighter flaw challenge frequency improve character arc?"
- Historical data valuable for writer learning
- Minimal storage cost (reports are small JSON documents)

**Implementation**:
- New table: `HealthReportHistory` with indexed timestamps
- Retention policy: 365 days (configurable)
- Automatic cleanup on startup
- New API endpoints: `/health/trends/{metric}` for longitudinal queries

```python
# Example trend query:
GET /health/trends/pacing_plateaus?start_date=2025-01-01&end_date=2025-11-24
# Returns: [
#   {"chapter_id": "1.2", "plateaus_detected": 1, "timestamp": "2025-05-10"},
#   {"chapter_id": "2.3", "plateaus_detected": 0, "timestamp": "2025-08-15"}
# ]
```

---

## Executive Summary

Phase 3D implements the **Graph Health Service** - a macro-level analysis system that validates narrative structure, character arcs, and thematic consistency at the chapter/act/manuscript level.

### The Quality Pyramid

```
┌─────────────────────────────────────────────────────────┐
│          TIER 3: Manuscript Health                      │
│          (Graph Health Service)                         │
│          • Full manuscript structural integrity         │
│          • Thematic coherence across volumes            │
│          • Character arc completion validation          │
├─────────────────────────────────────────────────────────┤
│          TIER 2: Chapter/Act Health                     │
│          (Graph Health Service)                         │
│          • Pacing across chapters                       │
│          • Beat progress validation                     │
│          • Timeline consistency                         │
├─────────────────────────────────────────────────────────┤
│          TIER 1: Scene-Level Quality                    │
│          (Scene Analyzer - Phase 3B)                    │
│          • Voice authenticity                           │
│          • Anti-pattern compliance                      │
│          • Metaphor discipline                          │
└─────────────────────────────────────────────────────────┘
```

**Analogy**: If Scene Analyzer is the **line editor**, Graph Health Service is the **structural engineer** checking blueprints against construction.

---

## Problem Statement

### What Scene Analyzer Doesn't Catch

The current Scene Analyzer (Phase 3B) validates individual scenes but **cannot detect**:

| Issue | Example | Why Scene Analyzer Misses It |
|-------|---------|------------------------------|
| **Pacing Plateaus** | 3 consecutive low-tension chapters | Needs cross-chapter context |
| **Dropped Threads** | Setup in Ch. 2 never resolved | Single scene can't detect absence |
| **Character Absences** | Supporting character disappears for 10 chapters | No character appearance tracking |
| **Beat Deviation** | Act 2 finishes at 45% instead of 50% | Requires manuscript-level % calculation |
| **Flaw Challenge Gaps** | Protagonist's Fatal Flaw untested for 5 chapters | Needs arc tracking over time |
| **Timeline Conflicts** | Character in two places at once | Requires world state history |
| **Theme Drift** | Central theme absent from critical structural beats | Needs beat-to-theme mapping |

### Solution: Asynchronous Macro Analysis

Run comprehensive health checks **after chapter assembly** or on-demand for full manuscript.

---

## Architecture

### Two-Tier Analysis Strategy

#### Tier 1: Immediate (Existing - Scene Analyzer)
- **When**: After each scene generation
- **Scope**: Single scene
- **Focus**: Voice, anti-patterns, metaphor discipline
- **Speed**: Real-time (<5 seconds)

#### Tier 2: Asynchronous (New - Graph Health Service)
- **When**: After chapter assembly OR manual trigger
- **Scope**: Chapter, Act, or Full Manuscript
- **Focus**: Structure, pacing, character arcs, theme
- **Speed**: Background job (30 seconds - 5 minutes)

### Service Integration

```
┌────────────────────────────────────────────────────────────────┐
│                     Graph Health Service                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Triggers:                                                      │
│  ├─ Chapter Assembly Complete (automatic)                      │
│  ├─ Act Complete (automatic)                                   │
│  └─ Manual Health Check (writer-initiated)                     │
│                                                                 │
│  Checks:                                                        │
│  ├─ Structural Integrity                                       │
│  │   ├─ Pacing Failure Detection                              │
│  │   ├─ Beat Progress Validation                              │
│  │   └─ Plot/Timeline Consistency                             │
│  │                                                              │
│  ├─ Character Arc Health                                       │
│  │   ├─ Fatal Flaw Challenge Monitoring                       │
│  │   └─ Cast Function Verification                            │
│  │                                                              │
│  └─ Thematic Health                                            │
│      ├─ Symbolic Layering                                      │
│      └─ Theme Resonance Score                                  │
│                                                                 │
│  Output:                                                        │
│  └─ Health Report (JSON + Markdown)                           │
│      ├─ Overall Health Score (0-100)                          │
│      ├─ Warnings (by category)                                │
│      ├─ Recommendations                                        │
│      └─ Visualization data                                     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Required Graph Schema Extensions

The current Knowledge Graph needs new node types and properties to support macro analysis.

### New Node Types

#### Phase 3D Core Nodes

```python
# 1. SCENE nodes (tracking individual scenes)
{
    "id": "scene_2.5.1",  # volume.chapter.scene
    "type": "SCENE",
    "chapter_id": "chapter_2.5",
    "beat": "beat_7",  # Which of 15 beats
    "tension_score": 7,  # 0-10 scale
    "word_count": 1200,
    "completion_date": "2025-11-24T10:30:00Z",
    "analysis_score": 92,  # From Scene Analyzer
    "pov_character": "protagonist",
    "location": "location_downtown_office",
    "timestamp": "story_day_5_14:30"  # In-story timeline
}

# 2. CHAPTER nodes
{
    "id": "chapter_2.5",
    "type": "CHAPTER",
    "act": 2,
    "title": "The Revelation",
    "scenes": ["scene_2.5.1", "scene_2.5.2", "scene_2.5.3"],
    "total_word_count": 3800,
    "avg_tension": 6.5,
    "completion_date": "2025-11-24T15:00:00Z",
    "health_score": null,  # Set by Graph Health Service
    "warnings": []
}

# 3. BEAT nodes (15-beat structure)
{
    "id": "beat_7",
    "type": "BEAT",
    "number": 7,
    "name": "Midpoint",
    "target_percentage": 50,  # Should occur at 50% of manuscript
    "actual_percentage": 48,  # Calculated from word count
    "scenes": ["scene_2.5.3"],  # Scenes implementing this beat
    "status": "complete",
    "deviation": -2  # % points off target
}

# 4. TENSION_TRACK nodes (for pacing analysis)
{
    "id": "tension_track_act2",
    "type": "TENSION_TRACK",
    "act": 2,
    "chapters": ["chapter_2.1", "chapter_2.2", "chapter_2.3", "chapter_2.4", "chapter_2.5"],
    "tension_scores": [5, 6, 6, 6, 7],  # Avg per chapter
    "plateau_detected": true,  # 3+ consecutive similar scores
    "plateau_chapters": ["chapter_2.2", "chapter_2.3", "chapter_2.4"]
}

# 5. FLAW_CHALLENGE nodes (tracking Fatal Flaw tests)
{
    "id": "flaw_challenge_1",
    "type": "FLAW_CHALLENGE",
    "scene_id": "scene_1.3.2",
    "chapter_id": "chapter_1.3",
    "challenge_type": "direct",  # direct | indirect | failure
    "outcome": "character_failed",
    "scenes_since_last": 0,
    "chapters_since_last": 0
}

# 6. SYMBOL nodes (thematic tracking)
{
    "id": "symbol_broken_mirror",
    "type": "SYMBOL",
    "name": "Broken Mirror",
    "theme_id": "theme_identity_fragmentation",
    "first_appearance": "scene_1.2.1",
    "recurrences": [
        {"scene": "scene_1.5.2", "meaning": "denial"},
        {"scene": "scene_2.8.1", "meaning": "acceptance"},
        {"scene": "scene_3.12.2", "meaning": "integration"}
    ],
    "evolution_detected": true
}
```

#### Phase 3D Historical Tracking Tables (Strategic Decision 4)

```python
# 7. HealthReportHistory table (SQLite persistence for longitudinal analysis)
{
    "id": "health_report_123",
    "type": "HEALTH_REPORT",
    "scope": "chapter",  # chapter | act | manuscript
    "chapter_id": "chapter_2.5",
    "act_number": null,
    "overall_score": 87,
    "warnings": [
        {
            "type": "PACING_PLATEAU",
            "severity": "warning",
            "message": "Flat pacing detected...",
            "recommendation": "Escalate tension"
        }
    ],
    "timestamp": "2025-11-24T15:30:00Z",
    "project_id": "explants_project"
}

# 8. ThemeResonanceOverride table (Manual writer overrides - Strategic Decision 2)
{
    "id": "theme_override_1",
    "project_id": "explants_project",
    "beat_id": "beat_7",
    "theme_id": "theme_identity",
    "manual_score": 9,  # Writer's override (0-10)
    "llm_score": 6,  # Original LLM auto-score
    "reason": "Subtle thematic callback that LLM missed - mirror metaphor evolution",
    "overridden_by": "writer",
    "timestamp": "2025-11-24T16:00:00Z"
}
```

### Enhanced Existing Nodes

```python
# CHARACTER nodes - add tracking
{
    "id": "protagonist",
    "type": "CHARACTER",
    "fatal_flaw": "overreliance_on_logic",
    "the_lie": "emotions_are_weakness",
    "last_appearance": "scene_2.5.1",
    "total_scenes": 42,
    "flaw_challenges": ["flaw_challenge_1", "flaw_challenge_2", "flaw_challenge_3"],
    "scenes_since_flaw_test": 5,  # WARNING if > threshold
    "character_function": "protagonist"
}

# THEME nodes - add resonance tracking
{
    "id": "theme_identity",
    "type": "THEME",
    "statement": "True identity emerges when logic and emotion integrate",
    "critical_beats": ["beat_2", "beat_7", "beat_12", "beat_15"],
    "resonance_scores": {
        "beat_2": 8,
        "beat_7": null,  # Not reached yet
        "beat_12": null,
        "beat_15": null
    }
}
```

---

## Health Checks Specification

### Category A: Structural Integrity

#### Check A1: Pacing Failure Detection

**Purpose**: Detect flat tension spots that bore readers.

**Algorithm**:
```python
def detect_pacing_plateaus(chapters: List[Chapter]) -> List[Warning]:
    warnings = []
    tension_scores = [ch.avg_tension for ch in chapters]

    # Sliding window of 3 chapters
    for i in range(len(tension_scores) - 2):
        window = tension_scores[i:i+3]

        # Check if all three are within 1 point of each other
        if max(window) - min(window) <= 1.0:
            warnings.append({
                "type": "PACING_PLATEAU",
                "severity": "warning",
                "chapters": chapters[i:i+3],
                "message": f"Flat pacing detected: Chapters {chapters[i].id} through {chapters[i+2].id} have similar tension ({window})",
                "recommendation": "Next scene should escalate tension significantly"
            })

    return warnings
```

**Data Requirements**:
- Each SCENE must have `tension_score` (0-10)
- CHAPTER tracks `avg_tension` across its scenes

**Settings Integration**:
```yaml
# voice_settings.yaml
health_checks:
  pacing:
    plateau_window: 3  # How many chapters to check
    plateau_tolerance: 1.0  # Max variation to still be "plateau"
    enabled: true
```

---

#### Check A2: Beat Progress Validation

**Purpose**: Ensure story structure matches planned beats.

**Algorithm**:
```python
def validate_beat_progress(manuscript_word_count: int, beat_sheet: List[Beat]) -> List[Warning]:
    warnings = []

    for beat in beat_sheet:
        # Calculate where this beat should occur
        target_word_count = manuscript_word_count * (beat.target_percentage / 100)

        # Calculate where it actually occurred
        actual_word_count = sum(scene.word_count for scene in beat.scenes)
        actual_percentage = (actual_word_count / manuscript_word_count) * 100

        deviation = abs(actual_percentage - beat.target_percentage)

        if deviation > 5:  # Configurable threshold
            warnings.append({
                "type": "BEAT_DEVIATION",
                "severity": "error" if deviation > 10 else "warning",
                "beat": beat.name,
                "target": f"{beat.target_percentage}%",
                "actual": f"{actual_percentage:.1f}%",
                "deviation": f"{deviation:.1f}%",
                "message": f"Beat '{beat.name}' is {deviation:.1f}% off target",
                "recommendation": "Consider restructuring to align with beat sheet"
            })

    return warnings
```

**Data Requirements**:
- BEAT nodes with `target_percentage`, `actual_percentage`, linked scenes
- Total manuscript word count

---

#### Check A3: Plot/Timeline Consistency

**Purpose**: Detect continuity errors (character in two places, contradictory world rules).

**Algorithm**:
```python
def check_timeline_consistency(scenes: List[Scene]) -> List[Warning]:
    warnings = []
    character_locations = {}  # character_id -> {timestamp: location}

    for scene in sorted(scenes, key=lambda s: s.timestamp):
        # Check each character in scene
        for character_id in scene.characters:
            location = scene.location
            timestamp = scene.timestamp

            if character_id in character_locations:
                prev_location, prev_timestamp = character_locations[character_id]

                # Check if character teleported
                if location != prev_location:
                    travel_time = parse_time_delta(timestamp, prev_timestamp)
                    if travel_time < minimum_travel_time(prev_location, location):
                        warnings.append({
                            "type": "TIMELINE_ERROR",
                            "severity": "error",
                            "character": character_id,
                            "message": f"{character_id} moved from {prev_location} to {location} in {travel_time} (too fast)",
                            "scenes": [prev_scene.id, scene.id]
                        })

            character_locations[character_id] = (location, timestamp)

    return warnings
```

**Data Requirements**:
- SCENE nodes with `location`, `timestamp`, `characters`
- LOCATION nodes with distances/travel times
- WORLD_RULES for physical constraints

---

### Category B: Character Arc Health

#### Check B1: Fatal Flaw Challenge Monitoring

**Purpose**: Ensure protagonist's Fatal Flaw is tested regularly.

**Algorithm**:
```python
def check_flaw_challenge_frequency(protagonist: Character, scenes: List[Scene]) -> List[Warning]:
    warnings = []
    threshold = get_setting("health_checks.character.flaw_challenge_frequency", 10)

    if protagonist.scenes_since_flaw_test > threshold:
        warnings.append({
            "type": "FLAW_CHALLENGE_GAP",
            "severity": "warning",
            "character": protagonist.id,
            "scenes_since_test": protagonist.scenes_since_flaw_test,
            "message": f"Protagonist's Fatal Flaw ({protagonist.fatal_flaw}) hasn't been challenged in {protagonist.scenes_since_flaw_test} scenes",
            "recommendation": "Create a scene where protagonist must confront their flaw"
        })

    return warnings
```

**Data Requirements**:
- CHARACTER node with `fatal_flaw`, `scenes_since_flaw_test`
- FLAW_CHALLENGE nodes tracking when flaw was tested

**Settings Integration**:
```yaml
health_checks:
  character:
    flaw_challenge_frequency: 10  # Max scenes before warning
```

---

#### Check B2: Cast Function Verification

**Purpose**: Ensure supporting characters serve their narrative function.

**Algorithm**:
```python
def verify_cast_function(cast: List[Character], scenes: List[Scene]) -> List[Warning]:
    warnings = []

    for character in cast:
        if character.function == "none":
            continue

        # Check appearance frequency
        appearances = [s for s in scenes if character.id in s.characters]

        if len(appearances) == 0:
            warnings.append({
                "type": "UNUSED_CHARACTER",
                "severity": "info",
                "character": character.id,
                "function": character.function,
                "message": f"{character.id} ({character.function}) has not appeared in any scenes"
            })
        elif len(appearances) < 3:
            warnings.append({
                "type": "UNDERUTILIZED_CHARACTER",
                "severity": "info",
                "character": character.id,
                "appearances": len(appearances),
                "message": f"{character.id} appears in only {len(appearances)} scenes - may be underutilized"
            })

    return warnings
```

---

### Category C: Thematic Health

#### Check C1: Symbolic Layering

**Purpose**: Track symbol recurrence and meaning evolution.

**Algorithm**:
```python
def analyze_symbolic_layering(symbols: List[Symbol]) -> List[Warning]:
    warnings = []

    for symbol in symbols:
        # Check recurrence
        if len(symbol.recurrences) < 3:
            warnings.append({
                "type": "WEAK_SYMBOL",
                "severity": "info",
                "symbol": symbol.name,
                "occurrences": len(symbol.recurrences),
                "message": f"Symbol '{symbol.name}' appears only {len(symbol.recurrences)} times - may not be significant enough"
            })

        # Check evolution
        meanings = [r["meaning"] for r in symbol.recurrences]
        if len(set(meanings)) == 1:
            warnings.append({
                "type": "STATIC_SYMBOL",
                "severity": "warning",
                "symbol": symbol.name,
                "message": f"Symbol '{symbol.name}' has static meaning ('{meanings[0]}') - should evolve with character"
            })

    return warnings
```

---

#### Check C2: Theme Resonance Score

**Purpose**: Verify theme appears at critical structural beats.

**Algorithm**:
```python
def check_theme_resonance(theme: Theme, beats: List[Beat]) -> List[Warning]:
    warnings = []

    for critical_beat in theme.critical_beats:
        beat = next((b for b in beats if b.id == critical_beat), None)

        if not beat or beat.status != "complete":
            continue

        # Check if theme appeared in scenes for this beat
        resonance = theme.resonance_scores.get(critical_beat)

        if resonance is None:
            warnings.append({
                "type": "MISSING_THEME",
                "severity": "error",
                "beat": beat.name,
                "theme": theme.statement,
                "message": f"Theme is absent from critical beat '{beat.name}'",
                "recommendation": "Revise scenes to incorporate thematic elements"
            })
        elif resonance < 6:
            warnings.append({
                "type": "WEAK_THEME",
                "severity": "warning",
                "beat": beat.name,
                "resonance": resonance,
                "message": f"Theme resonance at '{beat.name}' is weak ({resonance}/10)"
            })

    return warnings
```

---

## Implementation Tasks

### Task 0: Update Settings Configuration ✅ COMPLETE
**Effort**: 1 hour
**Status**: ✅ Done

**Files Modified**:
- `backend/services/settings_service.py`

**Completed Actions**:
1. ✅ Added `health_checks.timeline` section with semantic analysis settings
2. ✅ Added `health_checks.theme.auto_score` and `allow_manual_override` flags
3. ✅ Added `health_checks.reporting` section for historical storage
4. ✅ Added validation rules for new settings

---

### Task 1: Extend Knowledge Graph Schema ⭐ P0 CRITICAL
**Effort**: 3-4 hours
**Status**: 🔲 Next Up

**Files to Modify**:
- `backend/graph/schema.py` or `backend/services/knowledge_graph.py`
- Schema definitions for new node types

**Actions**:
1. Add SCENE, CHAPTER, BEAT, TENSION_TRACK, FLAW_CHALLENGE, SYMBOL node types
2. Add HealthReportHistory and ThemeResonanceOverride tables (SQLite)
3. Add properties to existing CHARACTER and THEME nodes
4. Create migration script for existing graphs
5. Write validators for new node types

---

### Task 2: Create Graph Health Service ⭐ P0 CRITICAL
**Effort**: 5-6 hours (increased for LLM semantic analysis)
**Status**: 🔲 Pending

**New File**: `backend/services/graph_health_service.py`

**Enhanced Implementation with Strategic Decisions**:
- ✅ **Decision 1**: Full LLM semantic analysis for timeline consistency
- ✅ **Decision 2**: Hybrid LLM + manual override for theme resonance
- ✅ **Decision 4**: SQLite persistence for historical reports

```python
class GraphHealthService:
    """
    Asynchronous macro-level analysis of manuscript structure and health.

    Runs after chapter assembly or on-demand for full manuscript.
    """

    def __init__(self, knowledge_graph, settings_service):
        self.graph = knowledge_graph
        self.settings = settings_service

    async def run_chapter_health_check(self, chapter_id: str) -> HealthReport:
        """Run all checks for a single chapter."""
        chapter = self.graph.get_node(chapter_id)
        warnings = []

        # Structural checks
        warnings.extend(self._check_beat_progress([chapter]))
        warnings.extend(self._check_timeline_consistency(chapter.scenes))

        # Character checks
        warnings.extend(self._check_flaw_challenges(chapter))
        warnings.extend(self._check_cast_function(chapter))

        # Thematic checks
        warnings.extend(self._check_theme_resonance(chapter))

        return HealthReport(
            scope="chapter",
            chapter_id=chapter_id,
            overall_score=self._calculate_health_score(warnings),
            warnings=warnings,
            timestamp=datetime.now(timezone.utc)
        )

    async def run_act_health_check(self, act_number: int) -> HealthReport:
        """Run all checks for an entire act."""
        chapters = self.graph.get_chapters_by_act(act_number)
        warnings = []

        # Pacing analysis (requires multi-chapter context)
        warnings.extend(self._check_pacing_plateaus(chapters))

        # All other checks
        for chapter in chapters:
            chapter_warnings = await self.run_chapter_health_check(chapter.id)
            warnings.extend(chapter_warnings.warnings)

        return HealthReport(
            scope="act",
            act_number=act_number,
            overall_score=self._calculate_health_score(warnings),
            warnings=warnings,
            timestamp=datetime.now(timezone.utc)
        )

    async def run_full_manuscript_check(self) -> HealthReport:
        """Run all checks across entire manuscript."""
        # ... comprehensive analysis ...
```

---

### Task 3: Integrate with Chapter Assembly ⭐ P1 HIGH
**Effort**: 2-3 hours

**File to Modify**: `backend/agents/foreman.py`

**Actions**:
1. Add hook at end of Chapter Assembly (Director Mode Step 4)
2. Queue Graph Health check as background task
3. Store health report in Knowledge Graph
4. Foreman reads warnings and adjusts guidance

```python
# In foreman.py, after chapter assembly
async def _handle_chapter_complete(self, chapter_id: str):
    # Mark chapter as complete
    self.kb_service.set(
        project_id=self.project_id,
        key=f"chapter_{chapter_id}_status",
        value="complete"
    )

    # Trigger Graph Health check (background)
    health_service = get_graph_health_service()
    health_report = await health_service.run_chapter_health_check(chapter_id)

    # Store report
    self.kb_service.set(
        project_id=self.project_id,
        key=f"chapter_{chapter_id}_health",
        value=json.dumps(health_report.to_dict())
    )

    # Adjust guidance based on warnings
    if health_report.has_critical_warnings():
        return self._create_challenge_message(health_report)
```

---

### Task 4: Create Health Report Data Classes 🔵 P2 MEDIUM
**Effort**: 1-2 hours

```python
@dataclass
class HealthWarning:
    type: str  # PACING_PLATEAU, BEAT_DEVIATION, etc.
    severity: str  # info | warning | error
    message: str
    recommendation: Optional[str] = None
    scenes: List[str] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthReport:
    scope: str  # chapter | act | manuscript
    chapter_id: Optional[str] = None
    act_number: Optional[int] = None
    overall_score: int = 100  # 0-100
    warnings: List[HealthWarning] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def has_critical_warnings(self) -> bool:
        return any(w.severity == "error" for w in self.warnings)

    def to_markdown(self) -> str:
        """Generate markdown health report for writer."""
        # ... format as readable report ...
```

---

### Task 5: Add API Endpoints 🔵 P2 MEDIUM
**Effort**: 2-3 hours (increased for new endpoints)
**Status**: 🔲 Pending

**File**: `backend/api.py`

**Enhanced Endpoints (includes Strategic Decisions 2 & 4)**:

```python
# Core health check endpoints
@app.post("/health/check")
async def run_health_check(request: HealthCheckRequest):
    """
    Run health check on chapter/act/manuscript.

    Body: {"scope": "chapter", "chapter_id": "2.5"}
          {"scope": "act", "act_number": 2}
          {"scope": "manuscript"}
    """
    service = get_graph_health_service()

    if request.scope == "chapter":
        report = await service.run_chapter_health_check(request.chapter_id)
    elif request.scope == "act":
        report = await service.run_act_health_check(request.act_number)
    else:
        report = await service.run_full_manuscript_check()

    return report.to_dict()

@app.get("/health/report/{report_id}")
async def get_health_report(report_id: str):
    """Get stored health report by ID."""
    # Retrieve from HealthReportHistory table
    service = get_graph_health_service()
    return service.get_report(report_id)

@app.post("/health/export")
async def export_health_report(request: ExportRequest):
    """
    Export health report as markdown or JSON.

    Body: {"report_id": "health_report_123", "format": "markdown"}
    """
    service = get_graph_health_service()
    report = service.get_report(request.report_id)

    if request.format == "markdown":
        return {"content": report.to_markdown()}
    else:
        return report.to_dict()

# NEW: Longitudinal analysis endpoints (Strategic Decision 4)
@app.get("/health/trends/{metric}")
async def get_health_trends(
    metric: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get historical trend data for a specific health metric.

    Metrics:
    - pacing_plateaus: Count of pacing plateau warnings over time
    - beat_deviations: Beat structure compliance over time
    - flaw_challenges: Fatal flaw challenge frequency over time
    - theme_resonance: Theme resonance scores over time
    - overall_health: Overall health scores over time

    Example: GET /health/trends/pacing_plateaus?start_date=2025-01-01&end_date=2025-11-24
    """
    service = get_graph_health_service()
    return service.get_trend_data(metric, start_date, end_date)

# NEW: Theme manual override endpoint (Strategic Decision 2)
@app.post("/health/theme/override")
async def override_theme_score(request: ThemeOverrideRequest):
    """
    Manually override LLM-generated theme resonance score.

    Body: {
        "beat_id": "beat_7",
        "theme_id": "theme_identity",
        "manual_score": 9,
        "reason": "Subtle callback that LLM missed"
    }
    """
    service = get_graph_health_service()
    return service.set_theme_override(
        beat_id=request.beat_id,
        theme_id=request.theme_id,
        manual_score=request.manual_score,
        reason=request.reason
    )

@app.get("/health/theme/overrides")
async def get_theme_overrides(project_id: str):
    """Get all manual theme score overrides for a project."""
    service = get_graph_health_service()
    return service.get_all_overrides(project_id)
```

---

## Triggers & Workflow

### Automatic Trigger: Chapter Assembly

```
Writer completes final scene in Chapter
         ↓
Foreman marks Chapter as COMPLETE
         ↓
[AUTOMATIC] Graph Health Service queued
         ↓
Health checks run in background (30-60 sec)
         ↓
HealthReport stored in Knowledge Graph
         ↓
Foreman reads warnings
         ↓
Foreman adjusts guidance:
   • If CRITICAL warnings → Block next chapter until fixed
   • If WARNINGS → Suggest fixes, allow continue
   • If CLEAN → Congratulate, proceed
```

### Manual Trigger: Writer-Initiated

```
Writer: "Check health of Act 2"
         ↓
API call to /health/check/act/2
         ↓
Graph Health Service runs all checks
         ↓
Return HealthReport immediately
         ↓
Frontend displays dashboard
```

---

## Settings Integration

Add to `voice_settings.yaml`:

```yaml
health_checks:
  enabled: true

  pacing:
    plateau_window: 3       # Chapters to check
    plateau_tolerance: 1.0  # Max tension variation
    enabled: true

  structure:
    beat_deviation_warning: 5    # % off target
    beat_deviation_error: 10     # % off target
    enabled: true

  character:
    flaw_challenge_frequency: 10  # Max scenes without test
    min_cast_appearances: 3       # Min for supporting chars
    enabled: true

  theme:
    min_symbol_occurrences: 3
    min_resonance_score: 6
    enabled: true
```

---

## Success Criteria

- [ ] Knowledge Graph supports new node types (SCENE, CHAPTER, BEAT, etc.)
- [ ] Graph Health Service runs all 7 check types
- [ ] Chapter assembly automatically triggers health check
- [ ] Health reports stored and retrievable
- [ ] Foreman integrates warnings into guidance
- [ ] API endpoints for manual health checks working
- [ ] Settings control check sensitivity
- [ ] Tests passing for all check algorithms

---

## Testing Strategy

### Unit Tests

1. **Check Algorithms**:
   - Pacing plateau detection with various tension patterns
   - Beat deviation with different manuscript lengths
   - Timeline consistency with complex character movements
   - Flaw challenge gap detection
   - Symbol evolution analysis

2. **Health Report**:
   - Warning prioritization
   - Score calculation
   - Markdown formatting

### Integration Tests

1. Build mock manuscript with known issues
2. Run full health check
3. Verify all expected warnings generated
4. Test Foreman response to critical warnings

---

## Phase Ordering

**Why Phase 3D comes before Phase 4**:

- Phase 4 (Immune System) includes version control and procedural memory
- Graph Health Service is **core quality assurance**, not advanced features
- Director Mode is incomplete without macro-level validation
- Settings system (Phase 3C) needed first for configurable thresholds

---

## Future Enhancements (Phase 5)

1. **Health Dashboard UI** - Visual manuscript health display
2. **Trend Analysis** - Track health scores over time
3. **Predictive Warnings** - "Based on current pacing, Act 3 may drag"
4. **Auto-Fix Suggestions** - "Add tension scene here to resolve plateau"
5. **Export Health Reports** - PDF/HTML for beta readers

---

*This document specifies the Graph Health Service implementation for Phase 3D.*
*All macro-level quality checks should reference this architecture.*
