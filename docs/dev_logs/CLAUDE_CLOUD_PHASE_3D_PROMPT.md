# Claude Code Cloud - Phase 3D Backend Completion Prompt

**Agent**: Claude Code Cloud (Opus 4.5)
**Task**: Complete Phase 3D Graph Health Service backend implementation
**Branch**: `phase-3d-completion` (create new branch from `main`)
**Parallel Work**: Local IDE is working on Track 1 Critical UI (frontend)
**Expected Duration**: 12-15 hours of focused backend work
**Deliverable**: Complete Phase 3D implementation ready to merge

---

## Context: What You're Completing

You are completing Phase 3D of the Writers Factory project - a professional novel-writing IDE with AI-powered assistance. Phase 3D adds **macro-level structural validation** (Graph Health Service) that validates manuscript structure at chapter/act/manuscript level.

**Current State** (as of commit `ffd474d`):
- ✅ 4 of 7 health checks implemented with cloud-native LLM analysis
- ✅ LLM query routing infrastructure (9+ providers)
- ✅ Settings configuration complete
- ❌ 3 remaining health checks (Pacing, Beat Progress, Symbolic Layering)
- ❌ Knowledge Graph schema extension (SCENE, CHAPTER, BEAT nodes)
- ❌ 7 API endpoints

**Your Mission**: Complete the remaining 3 health checks, extend the Knowledge Graph schema, and implement 7 API endpoints to finish Phase 3D.

---

## Architecture Overview

### System Architecture
Writers Factory is a Tauri desktop app with:
- **Frontend**: SvelteKit (you won't touch this - local IDE is handling UI)
- **Backend**: FastAPI Python (your focus)
- **Knowledge Graph**: NetworkX-based graph with SQLite persistence
- **LLM Integration**: Multi-provider support (OpenAI, Anthropic, DeepSeek, Qwen, local Ollama)

### Phase 3D Architecture
```
Graph Health Service (backend/services/graph_health_service.py)
├── 7 Health Check Methods (4 complete, 3 remaining)
│   ├── ✅ check_timeline_consistency() - LLM-powered semantic analysis
│   ├── ✅ check_theme_resonance() - Hybrid LLM + manual override
│   ├── ✅ check_flaw_challenges() - Dual-mode explicit + LLM fallback
│   ├── ✅ check_cast_function() - LLM character analysis
│   ├── ❌ check_pacing_failures() - YOUR TASK
│   ├── ❌ check_beat_progress() - YOUR TASK
│   └── ❌ check_symbolic_layering() - YOUR TASK
├── Settings Integration (settings.yaml)
├── LLM Query Router (llm_query_with_provider)
└── HealthReport data structures
```

### API Endpoints (7 new endpoints to add to backend/api.py)
```python
# Health Check Execution
POST /health/check                    # Run all or specific health checks
GET  /health/report/{report_id}       # Get detailed health report

# Historical Analysis
GET  /health/trends/{metric}          # Get historical trends for a metric
GET  /health/reports                  # List all health reports

# Manual Overrides
POST /health/theme/override           # Manual theme resonance override
GET  /health/theme/overrides          # List all theme overrides

# Export
GET  /health/export/{report_id}       # Export report as JSON/markdown
```

---

## Task Breakdown

### Task 1: Implement 3 Remaining Health Checks

#### 1.1 Pacing Failure Detection
**File**: `backend/services/graph_health_service.py`

**Method Signature**:
```python
def check_pacing_failures(self, manuscript_context: Dict[str, Any]) -> List[HealthWarning]
```

**Purpose**: Detect "tension plateaus" - consecutive chapters with low/flat tension that cause reader boredom.

**Algorithm**:
1. Extract tension scores for last N chapters (configurable, default 10)
2. Detect plateaus: 3+ consecutive chapters with <5 point tension variation
3. Use LLM to analyze if plateau is intentional (calm before storm) or problematic
4. Return warnings for problematic plateaus

**LLM Prompt Template**:
```python
prompt = f"""Analyze tension plateau in manuscript:

Chapters: {chapter_summaries}
Tension Scores: {tension_scores}

A "tension plateau" has been detected: {plateau_description}

Questions:
1. Is this plateau intentional (e.g., calm before storm, character development)?
2. Does it risk reader boredom?
3. What's missing to create rising tension?

Return JSON:
{{
  "is_intentional": bool,
  "risk_level": "low|medium|high",
  "recommendation": "specific suggestion"
}}
"""
```

**Warning Severity**: ERROR if 5+ chapters plateau, WARNING if 3-4 chapters

**Settings Key**: `health_checks.pacing.plateau_threshold` (default: 3 chapters)

---

#### 1.2 Beat Progress Validation
**File**: `backend/services/graph_health_service.py`

**Method Signature**:
```python
def check_beat_progress(self, manuscript_context: Dict[str, Any]) -> List[HealthWarning]
```

**Purpose**: Validate manuscript follows 15-beat Save the Cat! structure at correct percentages.

**Algorithm**:
1. Load Beat_Sheet.md from Story Bible (15 beats with target percentages)
2. Calculate current manuscript completion percentage
3. Determine which beat should be active at current completion
4. Query Knowledge Graph for scenes tagged with beat numbers
5. Check if current scenes align with expected beat
6. Warn if ahead/behind expected beat progression

**Beat Structure Reference**:
```python
BEAT_TARGETS = {
    1: 1,      # Opening Image
    2: 5,      # Theme Stated
    3: 10,     # Setup complete
    4: 10,     # Catalyst
    5: 20,     # Debate ends
    6: 20,     # Break into Two
    7: 22,     # B Story begins
    8: 50,     # Fun & Games
    9: 50,     # Midpoint
    10: 75,    # Bad Guys Close In
    11: 75,    # All Is Lost
    12: 80,    # Dark Night of the Soul
    13: 80,    # Break into Three
    14: 99,    # Finale
    15: 100    # Final Image
}
```

**Warning Examples**:
- ERROR: "Manuscript is 60% complete but still in Beat 6 (Break into Two at 20%). You're 40 points behind."
- WARNING: "Manuscript is 25% complete and already at Beat 9 (Midpoint at 50%). Pacing too fast."

**Settings Key**: `health_checks.beat_progress.tolerance` (default: 10% deviation allowed)

---

#### 1.3 Symbolic Layering
**File**: `backend/services/graph_health_service.py`

**Method Signature**:
```python
def check_symbolic_layering(self, manuscript_context: Dict[str, Any]) -> List[HealthWarning]
```

**Purpose**: Ensure symbols recur throughout manuscript with evolving meanings (not one-off decorations).

**Algorithm**:
1. Extract symbols from Theme.md in Story Bible
2. Query Knowledge Graph for symbol mentions across scenes
3. Use LLM to analyze:
   - Symbol recurrence frequency
   - Whether meaning evolves or stays static
   - Whether symbols appear at thematically important moments
4. Warn if symbols are absent for too long or lack evolution

**LLM Prompt Template**:
```python
prompt = f"""Analyze symbolic layering in manuscript:

Defined Symbols: {symbols_from_theme_md}
Symbol Appearances:
{symbol_occurrences_by_chapter}

For each symbol:
1. Does it recur throughout the manuscript? (minimum 3 appearances)
2. Does its meaning evolve, or is it static?
3. Does it appear at thematically critical beats (Midpoint, All Is Lost, Finale)?

Return JSON for each symbol:
{{
  "symbol": "name",
  "recurrence_adequate": bool,
  "meaning_evolves": bool,
  "appears_at_critical_beats": bool,
  "recommendation": "specific suggestion"
}}
"""
```

**Warning Examples**:
- WARNING: "Symbol 'Mirror' appears only in Chapters 1-3, then vanishes. Consider reinforcing in Act 2."
- INFO: "Symbol 'Broken Clock' appears at Opening Image and Midpoint but not at Finale. Consider final callback."

**Settings Key**: `health_checks.symbolic.min_recurrences` (default: 3)

---

### Task 2: Extend Knowledge Graph Schema

**File**: `backend/graph/schema.py`

Currently the Knowledge Graph has these node types:
```python
NODE_TYPES = {
    "character": {...},
    "location": {...},
    "event": {...},
    "theme": {...},
    "object": {...},
    "relationship": {...}
}
```

**Add 3 new node types**:

#### 2.1 SCENE Node
```python
"scene": {
    "required_attributes": [
        "scene_id",        # e.g., "1.2.3" (Act.Chapter.Scene)
        "title",           # Scene title
        "pov_character",   # Who's POV
        "beat_number",     # Which of 15 beats this serves (1-15)
        "tension_score"    # 0-100 tension rating
    ],
    "optional_attributes": [
        "goal",            # Scene goal (from Scene_Strategy.md)
        "conflict",        # Scene conflict
        "outcome",         # Yes/No/Yes-But/No-And
        "word_count",      # Scene length
        "quality_score",   # Scene Analyzer score (0-100)
        "metaphor_domains" # List of metaphor domains used
    ],
    "allowed_relationships": [
        "PRECEDES",        # Scene → Scene (chronological order)
        "FOLLOWS",         # Scene → Scene (reverse)
        "FEATURES",        # Scene → Character (character appears)
        "TAKES_PLACE_IN",  # Scene → Location
        "ADVANCES",        # Scene → Beat (which beat it advances)
        "CHALLENGES"       # Scene → Flaw (tests protagonist's flaw)
    ]
}
```

#### 2.2 CHAPTER Node
```python
"chapter": {
    "required_attributes": [
        "chapter_id",      # e.g., "1.2" (Act.Chapter)
        "title",           # Chapter title
        "act_number"       # 1, 2, or 3
    ],
    "optional_attributes": [
        "scene_count",     # Number of scenes
        "word_count",      # Total chapter length
        "avg_tension",     # Average tension across scenes
        "beat_range"       # Which beats covered (e.g., "6-8")
    ],
    "allowed_relationships": [
        "CONTAINS",        # Chapter → Scene
        "PART_OF",         # Chapter → Act (which act)
        "PRECEDES",        # Chapter → Chapter
        "FOLLOWS"          # Chapter → Chapter
    ]
}
```

#### 2.3 BEAT Node
```python
"beat": {
    "required_attributes": [
        "beat_number",     # 1-15
        "beat_name",       # e.g., "Midpoint", "All Is Lost"
        "target_percent"   # Where it should occur (0-100)
    ],
    "optional_attributes": [
        "description",     # From Beat_Sheet.md
        "scenes_serving",  # List of scene_ids that serve this beat
        "actual_percent",  # Where it actually occurred
        "deviation"        # How far off from target_percent
    ],
    "allowed_relationships": [
        "SERVED_BY",       # Beat → Scene (which scenes serve this beat)
        "PRECEDES",        # Beat → Beat (beat order)
        "FOLLOWS"          # Beat → Beat
    ]
}
```

**Implementation Notes**:
- Add to `schema.py` NODE_TYPES dictionary
- Update `validate_node()` function to validate new node types
- Add helper functions: `create_scene_node()`, `create_chapter_node()`, `create_beat_node()`

---

### Task 3: Implement 7 API Endpoints

**File**: `backend/api.py`

Add these endpoints to the FastAPI app:

#### 3.1 Run Health Checks
```python
@app.post("/health/check")
async def run_health_check(
    check_type: Optional[str] = None,  # "all" or specific check name
    manuscript_path: Optional[str] = None
):
    """
    Run health checks on manuscript.

    Args:
        check_type: "all", "pacing", "beat_progress", "symbolic", etc.
        manuscript_path: Path to manuscript root (optional, uses current project)

    Returns:
        {
            "report_id": "uuid",
            "timestamp": "ISO datetime",
            "checks_run": ["pacing", "beat_progress", ...],
            "warnings": [
                {
                    "severity": "ERROR|WARNING|INFO",
                    "category": "pacing|beat_progress|symbolic|...",
                    "message": "...",
                    "affected_chapters": [...]
                }
            ],
            "overall_health": "excellent|good|fair|poor"
        }
    """
    # Implementation:
    # 1. Load manuscript context
    # 2. Run requested health checks via GraphHealthService
    # 3. Save report to SQLite (health_reports table)
    # 4. Return report with warnings
```

#### 3.2 Get Health Report
```python
@app.get("/health/report/{report_id}")
async def get_health_report(report_id: str):
    """
    Get detailed health report by ID.

    Returns full report with all warnings, recommendations, and metadata.
    """
    # Fetch from SQLite health_reports table
```

#### 3.3 Get Historical Trends
```python
@app.get("/health/trends/{metric}")
async def get_health_trends(
    metric: str,  # "pacing", "beat_progress", "symbolic", "overall"
    days: int = 30
):
    """
    Get historical trend data for a specific health metric.

    Returns:
        {
            "metric": "pacing",
            "data_points": [
                {"date": "2025-11-20", "score": 85},
                {"date": "2025-11-21", "score": 87},
                ...
            ],
            "trend": "improving|stable|declining"
        }
    """
    # Query health_reports table for last N days
    # Calculate trend direction
```

#### 3.4 List All Reports
```python
@app.get("/health/reports")
async def list_health_reports(limit: int = 20, offset: int = 0):
    """
    List all health reports with pagination.

    Returns:
        {
            "reports": [
                {
                    "report_id": "uuid",
                    "timestamp": "ISO datetime",
                    "overall_health": "good",
                    "warning_count": 3
                },
                ...
            ],
            "total": 47,
            "limit": 20,
            "offset": 0
        }
    """
    # Query health_reports table with pagination
```

#### 3.5 Theme Resonance Override
```python
@app.post("/health/theme/override")
async def override_theme_resonance(
    chapter_id: str,
    score: int,  # 0-100
    explanation: str
):
    """
    Manually override theme resonance score for a chapter.

    Writer can override LLM's theme resonance score with their own judgment.
    """
    # Save to theme_resonance_overrides table
    # Return updated health report
```

#### 3.6 List Theme Overrides
```python
@app.get("/health/theme/overrides")
async def list_theme_overrides():
    """
    List all manual theme resonance overrides.

    Returns:
        {
            "overrides": [
                {
                    "chapter_id": "1.2",
                    "llm_score": 65,
                    "manual_score": 80,
                    "explanation": "LLM missed subtle symbolism in mirror scene",
                    "timestamp": "ISO datetime"
                },
                ...
            ]
        }
    """
    # Query theme_resonance_overrides table
```

#### 3.7 Export Health Report
```python
@app.get("/health/export/{report_id}")
async def export_health_report(
    report_id: str,
    format: str = "json"  # "json" or "markdown"
):
    """
    Export health report in specified format.

    Returns:
        For JSON: Full report object
        For Markdown: Formatted markdown report ready for reading
    """
    # Fetch report from SQLite
    # Format as JSON or Markdown
    # Return as downloadable file
```

---

### Task 4: Database Schema Updates

**File**: `backend/services/graph_health_service.py` (add SQLite schema)

Add these tables to SQLite database:

```python
CREATE TABLE IF NOT EXISTS health_reports (
    report_id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    manuscript_path TEXT,
    checks_run TEXT,  -- JSON array of check names
    warnings TEXT,     -- JSON array of HealthWarning objects
    overall_health TEXT,  -- "excellent|good|fair|poor"
    metadata TEXT      -- JSON object with additional data
);

CREATE TABLE IF NOT EXISTS theme_resonance_overrides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id TEXT,
    llm_score INTEGER,
    manual_score INTEGER,
    explanation TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_reports_timestamp ON health_reports(timestamp);
CREATE INDEX idx_theme_overrides_chapter ON theme_resonance_overrides(chapter_id);
```

---

## Implementation Guidelines

### 1. Follow Existing Patterns
Review these files for coding patterns:
- `backend/services/graph_health_service.py` (4 complete health checks - follow same pattern)
- `backend/services/model_orchestrator.py` (LLM query patterns)
- `backend/api.py` (FastAPI endpoint patterns)

### 2. Settings Integration
All configurable values must come from `settings.yaml`:
```yaml
health_checks:
  pacing:
    plateau_threshold: 3              # chapters
    min_tension_variation: 5          # points
    model: "gpt-4o"

  beat_progress:
    tolerance: 10                     # percent deviation allowed
    model: "claude-3-5-sonnet"

  symbolic:
    min_recurrences: 3                # appearances
    model: "deepseek-chat"
```

Access via `SettingsService`:
```python
from backend.services.settings_service import SettingsService

settings = SettingsService()
plateau_threshold = settings.get("health_checks.pacing.plateau_threshold", default=3)
```

### 3. LLM Query Pattern
Use the existing `llm_query_with_provider()` function:
```python
from backend.services.graph_health_service import GraphHealthService

service = GraphHealthService()
result = service.llm_query_with_provider(
    prompt=your_prompt,
    provider="openai",  # or from settings
    model="gpt-4o"      # or from settings
)
```

### 4. Error Handling
- Graceful degradation if LLM API fails (return WARNING, not ERROR)
- Log all LLM queries for debugging
- Validate all inputs from API endpoints

### 5. Testing Strategy
Create test fixtures in `backend/tests/`:
```python
# test_graph_health_pacing.py
def test_pacing_plateau_detection():
    # Test with 5 consecutive chapters at tension 50-52
    # Should return ERROR warning

def test_pacing_intentional_plateau():
    # Test with LLM recognizing intentional calm before storm
    # Should return INFO or no warning
```

---

## Documentation Requirements

Create these files:

### 1. Implementation Log
**File**: `docs/dev_logs/PHASE_3D_COMPLETION_CLOUD.md`

Document:
- What you implemented
- Decisions made (e.g., LLM prompt design choices)
- Test results
- Any deviations from this spec (with rationale)

### 2. Update Roadmap
**File**: `docs/04_roadmap.md`

Change Phase 3D status from:
```markdown
## Phase 3D: Graph Health Service (🚧 In Progress)
```

To:
```markdown
## Phase 3D: Graph Health Service (✅ Complete)
```

Update implementation status section with completion checkmarks.

### 3. API Documentation Update
**File**: `docs/API_REFERENCE.md`

Add the 7 new `/health/*` endpoints with:
- Request/response formats
- Parameter descriptions
- Example usage

---

## Quality Checklist

Before creating PR, verify:

- [ ] All 3 health checks implemented and tested
- [ ] Knowledge Graph schema extended (SCENE, CHAPTER, BEAT nodes)
- [ ] All 7 API endpoints implemented
- [ ] SQLite schema updated (health_reports, theme_resonance_overrides tables)
- [ ] Settings integration complete (all configurable values from settings.yaml)
- [ ] LLM queries use `llm_query_with_provider()` with graceful fallback
- [ ] Error handling for all edge cases
- [ ] Code follows existing patterns in codebase
- [ ] Tests written for each health check
- [ ] Documentation updated (roadmap, API reference, implementation log)
- [ ] All files formatted (black, isort for Python)
- [ ] No frontend files touched (those are for local IDE Track 1)

---

## Commit Strategy

Create **one commit per major task**:

```bash
# Commit 1: Health checks
git add backend/services/graph_health_service.py
git commit -m "feat(health): Implement pacing, beat progress, and symbolic layering checks

- Pacing: Detect tension plateaus with LLM analysis
- Beat Progress: Validate 15-beat structure alignment
- Symbolic Layering: Ensure symbol recurrence and evolution

All checks configurable via settings.yaml with LLM fallback.
Tests included for each check."

# Commit 2: Schema extension
git add backend/graph/schema.py
git commit -m "feat(graph): Extend schema with SCENE, CHAPTER, BEAT nodes

- SCENE: Track scene metadata, tension, beat alignment
- CHAPTER: Track chapter structure and metrics
- BEAT: Track 15-beat Save the Cat! structure

Includes validation and helper functions."

# Commit 3: API endpoints
git add backend/api.py backend/services/graph_health_service.py
git commit -m "feat(api): Add 7 health check endpoints

Endpoints:
- POST /health/check - Run health checks
- GET /health/report/{id} - Get report
- GET /health/trends/{metric} - Historical trends
- GET /health/reports - List all reports
- POST /health/theme/override - Manual override
- GET /health/theme/overrides - List overrides
- GET /health/export/{id} - Export report

SQLite schema includes health_reports and theme_resonance_overrides tables."

# Commit 4: Documentation
git add docs/
git commit -m "docs: Phase 3D completion documentation

- PHASE_3D_COMPLETION_CLOUD.md - Implementation log
- Updated 04_roadmap.md - Mark Phase 3D complete
- Updated API_REFERENCE.md - 7 new health endpoints

Phase 3D Graph Health Service now complete."
```

---

## Final Deliverable

When complete, create PR:

**PR Title**: `feat: Complete Phase 3D Graph Health Service (Backend)`

**PR Description**:
```markdown
Completes Phase 3D Graph Health Service backend implementation with 3 remaining health checks, Knowledge Graph schema extension, and 7 API endpoints.

## Changes
- ✅ Implemented 3 health checks: Pacing, Beat Progress, Symbolic Layering
- ✅ Extended Knowledge Graph schema: SCENE, CHAPTER, BEAT nodes
- ✅ Added 7 API endpoints for health check execution and reporting
- ✅ SQLite schema: health_reports, theme_resonance_overrides tables
- ✅ Full settings integration with configurable thresholds
- ✅ LLM query routing with graceful fallback
- ✅ Tests for all health checks
- ✅ Documentation updated

## API Endpoints Added
- POST /health/check
- GET /health/report/{id}
- GET /health/trends/{metric}
- GET /health/reports
- POST /health/theme/override
- GET /health/theme/overrides
- GET /health/export/{id}

## Testing
All health checks tested with fixture manuscripts. LLM prompts validated for accuracy.

## Phase Status
Phase 3D: ✅ Complete (was 🚧 In Progress)

## Next Steps
Phase 5 Track 1 Critical UI (in progress on local IDE - no conflicts).
Phase 4 Multi-Model Tournament (optional, planned).
```

---

## Branch Management

```bash
# Create feature branch
git checkout -b phase-3d-completion

# Work on implementation
# ... make commits as outlined above ...

# Push to remote
git push origin phase-3d-completion

# Create PR on GitHub
# Do NOT merge until local IDE Track 1 is ready to integrate
```

**Important**: Local IDE is working on `/frontend` files. Your backend work won't conflict. We'll merge both branches when ready.

---

## Questions?

If you encounter issues:
1. Check existing implementation in `backend/services/graph_health_service.py` (4 complete checks)
2. Review settings patterns in `backend/services/settings_service.py`
3. Check LLM query patterns in `backend/services/model_orchestrator.py`
4. Refer to Knowledge Graph schema in `backend/graph/schema.py`

**File Locations**:
- Health checks: `backend/services/graph_health_service.py`
- Schema: `backend/graph/schema.py`
- API endpoints: `backend/api.py`
- Settings: `backend/services/settings_service.py`
- Tests: `backend/tests/`

---

**You've got this! Opus 4.5 is perfect for complex LLM integration work. Looking forward to the PR!**

🤖 *This prompt generated with Claude Code (Sonnet 4.5)*
