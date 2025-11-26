## Detailed Test Prompt for IntelligenceDirector

Here's a comprehensive prompt you can use to have Claude test the Director Mode system:

~~~markdown
# INTELLIGENCE DIRECTOR (Director Mode) COMPREHENSIVE TEST SUITE

You are testing the Director Mode system of the Writers Factory application. This is a 4-service pipeline for AI-assisted scene creation with voice consistency enforcement.

## TEST ENVIRONMENT SETUP
- Backend: Python FastAPI at http://localhost:8000
- All 4 services must be initialized before testing
- Requires: A project with completed Voice Calibration (Voice Bundle generated)

---

## PHASE 1: SCAFFOLD GENERATOR TESTS

### Test 1.1: Draft Summary Generation
**Endpoint:** `POST /director/scaffold/draft-summary`
```json
{
  "project_id": "{{project_id}}",
  "scene_id": "ch1_scene1",
  "chapter_number": 1,
  "scene_number": 1,
  "beat_number": 1,
  "target_word_count": 2500
}
~~~

**Expected Output:**

- `DraftSummary` with scene context, character goals, enrichment suggestions
- At least 2 enrichment opportunities flagged
- Phase-appropriate voice complexity indicator

### Test 1.2: Enrichment Data Fetch

**Endpoint:** `POST /director/scaffold/enrich`

```json
{
  "draft_summary_id": "{{from_test_1.1}}",
  "enrichment_ids": ["notebooklm_character_voice", "notebooklm_setting_details"]
}
```

**Expected:** EnrichmentData with NotebookLM-sourced context

### Test 1.3: Full Scaffold Generation

**Endpoint:** `POST /director/scaffold/generate` **Expected Scaffold Fields:**

-  `scene_id`, `chapter_number`, `scene_number`
-  `target_word_count` (2500 ± 10%)
-  `phase` (1-4 based on story progress)
-  `voice_requirements` (from Voice Bundle)
-  `quality_threshold` (default 85)
-  `character_goals` (array, minimum 2)
-  `callbacks` (references to prior scenes if applicable)

------

## PHASE 2: SCENE WRITER TESTS

### Test 2.1: Structure Variant Generation

**Endpoint:** `POST /director/scene/structure-variants`

```json
{
  "scaffold_id": "{{from_phase_1}}",
  "variant_count": 5
}
```

**Expected:** 5 StructureVariant objects (A-E) with:

- Distinct beat counts (3-7 range)
- Different pacing profiles (rapid/measured/contemplative)
- Unique strategic rationales

### Test 2.2: Multi-Model Tournament

**Endpoint:** `POST /director/scene/generate-variants`

```json
{
  "scaffold_id": "{{scaffold_id}}",
  "structure_variant_id": "A",
  "strategies": ["ACTION", "CHARACTER", "DIALOGUE", "ATMOSPHERIC", "BALANCED"],
  "models": ["claude-sonnet-4-20250514", "gpt-4o", "deepseek-chat"]
}
```

**Expected:** 15 SceneVariant objects (3 models × 5 strategies) **Verify:**

-  Each variant has unique `variant_id`
-  `generation_time` recorded
-  `word_count` within ±20% of target
-  Different `strategy` per variant

### Test 2.3: Quick Generate (Single Model)

**Endpoint:** `POST /director/scene/quick-generate` **Verify:** Single scene output in < 30 seconds

------

## PHASE 3: SCENE ANALYZER TESTS

### Test 3.1: Full 5-Category Analysis

**Endpoint:** `POST /director/scene/analyze`

```json
{
  "scene_id": "{{scene_id}}",
  "content": "{{scene_content}}",
  "voice_bundle_path": "{{voice_bundle_path}}"
}
```

**Expected SceneAnalysisResult:**

```json
{
  "total_score": 0-100,
  "grade": "A|B|C|D|F",
  "categories": {
    "voice_authenticity": {"score": 0-30, "tests": {...}},
    "character_consistency": {"score": 0-20, "tests": {...}},
    "metaphor_discipline": {"score": 0-20, "metrics": {...}},
    "anti_pattern_compliance": {"score": 0-15, "violations": [...]},
    "phase_appropriateness": {"score": 0-15, "assessment": {...}}
  },
  "enhancement_needed": true|false,
  "recommended_mode": "ACTION_PROMPT|SIX_PASS|REWRITE"
}
```

### Test 3.2: Anti-Pattern Detection (Real-Time)

**Endpoint:** `POST /director/scene/detect-patterns` **Test with known violations:**

```
"She thought to herself that..."  → first_person_italics
"He moved with precision."        → with_precision
"Suddenly, the door opened."      → suddenly
```

**Expected:** Array of PatternViolation with line numbers

### Test 3.3: Metaphor Domain Analysis

**Endpoint:** `POST /director/scene/analyze-metaphors` **Expected MetaphorAnalysis:**

-  `total_metaphors` count
-  `domains` breakdown (MECHANICAL, ORGANIC, etc.)
-  `domain_percentages` (none > 30% saturation threshold)
-  `simile_count` (should be ≤ 2)
-  `saturated_domains` flagged if > 30%

### Test 3.4: Scoring Boundary Tests

**Test scenes designed to score at edges:**

- Perfect voice (28-30/30): Match gold standard exactly
- Zero tolerance violation (-2): Include "with precision"
- Simile overload: 5+ similes in 500 words
- Domain saturation: 40% mechanical metaphors

------

## PHASE 4: SCENE ENHANCEMENT TESTS

### Test 4.1: Auto-Mode Selection

**Endpoint:** `POST /director/scene/enhance`

| Input Score | Expected Mode | Behavior               |
| :---------- | :------------ | :--------------------- |
| ≥ 85        | ACTION_PROMPT | Surgical OLD→NEW fixes |
| 70-84       | SIX_PASS      | Full 6-pass ritual     |
| < 70        | REWRITE       | Return to Scene Writer |

### Test 4.2: Action Prompt Generation

**Endpoint:** `POST /director/scene/action-prompt` **Expected:** Array of Fix objects:

```json
[
  {
    "fix_id": "uuid",
    "category": "anti_pattern|voice|metaphor",
    "old_text": "She moved with precision.",
    "new_text": "She moved like a scalpel through flesh.",
    "line_number": 47,
    "rationale": "Replace zero-tolerance pattern"
  }
]
```

### Test 4.3: Apply Fixes

**Endpoint:** `POST /director/scene/apply-fixes`

```json
{
  "scene_id": "{{scene_id}}",
  "fix_ids": ["fix_1", "fix_2"]
}
```

**Verify:**

-  Content updated with NEW text
-  Score improved after re-analysis
-  Version history updated

### Test 4.4: 6-Pass Enhancement

**Endpoint:** `POST /director/scene/six-pass` **Monitor Progress:**

1. Pass 1: Voice alignment
2. Pass 2: Anti-pattern removal
3. Pass 3: Metaphor rebalancing
4. Pass 4: Character consistency
5. Pass 5: Phase calibration
6. Pass 6: Final polish

**Expected:** Progressive score improvement, final ≥ 85

------

## PHASE 5: INTEGRATION TESTS

### Test 5.1: Full Pipeline (Happy Path)

1. Generate scaffold for scene
2. Create 5 structure variants
3. Run tournament (15 variants)
4. Analyze top 3 variants
5. Select winner
6. Enhance to 85+
7. Verify KB persistence

### Test 5.2: Mode Transition

**Endpoint:** `POST /foreman/mode/director` **Prerequisite:** Voice Bundle must exist **Expected:** Mode changes from VOICE_CALIBRATION → DIRECTOR

### Test 5.3: Settings Override

```python
# Test 3-tier resolution
settings_service.set_global("scoring.voice_authenticity_weight", 25)
settings_service.set_project(project_id, "scoring.voice_authenticity_weight", 35)
# Expect project-level (35) to win
```

------

## PHASE 6: EDGE CASE & ERROR HANDLING

### Test 6.1: Missing Voice Bundle

- Call `/director/scene/analyze` without Voice Bundle
- **Expected:** 400 error with clear message

### Test 6.2: Invalid Phase

- Set scene to Phase 5 (only 1-4 valid)
- **Expected:** Validation error

### Test 6.3: Empty Scene Content

- Analyze empty string
- **Expected:** Graceful failure, not crash

### Test 6.4: Concurrent Writes

- Submit 3 enhancement requests simultaneously
- **Expected:** Proper queuing/locking

------

## SUCCESS CRITERIA

✅ All 5 scoring categories return valid 0-max scores ✅ Anti-pattern detection catches zero-tolerance patterns ✅ Metaphor saturation flagged at > 30% ✅ Enhancement improves score by at least 10 points ✅ 6-pass completes all passes without error ✅ Settings 3-tier resolution works correctly ✅ KB persists scene completion status ✅ No unhandled exceptions in any test

```
---

## Recommendation

Based on the complexity assessment:

1. **If you want to tweak existing behavior** (weights, thresholds, models) → Use the Settings Service. Zero code changes needed.

2. **If you want to add new anti-patterns or metaphor domains** → Moderate effort, isolated to the Analyzer service.

3. **If you want to restructure the scoring rubric** (add/remove categories) → Significant refactor affecting tests, frontend, and all 4 services.

Would you like me to:
1. Save this test prompt to a file in the project?
2. Create a test runner script that executes these tests automatically?
3. Design a Settings UI mockup for the easy-to-modify configurations?
```