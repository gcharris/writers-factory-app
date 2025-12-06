# Phase 4: Promotion Workflow

> Move reviewed Research Notes into the canonical Story Bible with intelligent transformation.

## Concept

Research Notes live in `workspace/research/` - they're drafts, works-in-progress.

Story Bible documents live in `content/` - they're canonical, the source of truth.

**Promotion** = Moving vetted research into the Story Bible **with intelligent transformation**.

### Critical Insight

Promotion is NOT just file copy. Each category requires specific field extraction:

| From Category | To Story Bible | Fields to Extract |
|---------------|----------------|-------------------|
| `characters/` | `Protagonist.md`, `Cast.md` | Fatal Flaw, The Lie, Arc, Relationships |
| `world/` | `Rules.md`, `Locations.md` | Hard Rules, Locations, Secrets |
| `theme/` | `Theme.md` | Central Question, Thesis, Counter-thesis, Symbols |
| `plot/` | `Beat_Sheet.md` | 15 Beats, Midpoint Type |
| `voice/` | Voice Calibration Bundle | Triggers voice training, not file copy |

---

## Structure Check (Critical Pre-Requisite)

Before promotion, verify the Research Note contains the required structure for its category.

### Required Fields by Category

```python
REQUIRED_FIELDS = {
    "characters": {
        "protagonist": ["fatal_flaw", "the_lie", "arc_start", "arc_resolution"],
        "antagonist": ["motivation", "goal", "conflict_with_protagonist"],
        "supporting": ["role", "relationship_to_protagonist"]
    },
    "world": {
        "rules": ["hard_rules"],  # At least one Hard Rule
        "locations": ["name", "significance"]
    },
    "theme": {
        "core": ["central_question", "thesis", "counter_thesis"]
    },
    "plot": {
        "beats": ["catalyst", "midpoint", "all_is_lost", "finale"],
        "structure": ["midpoint_type"]  # false_victory or false_defeat
    },
    "voice": {
        # Voice has no structure requirement - triggers calibration instead
    }
}
```

### Structure Check Logic

```python
async def check_promotable(file_path: str, category: str) -> PromotionStatus:
    """
    Check if file can be promoted to Story Bible.

    Requirements:
    1. Stage 2 content (not raw Stage 1)
    2. No unresolved BREAKING conflicts
    3. Contains required fields for category
    """
    content = read_file(file_path)
    metadata = parse_frontmatter(file_path)

    blockers = []
    warnings = []

    # Check 1: Stage Check
    if metadata.get("stage") == "1":
        blockers.append("Content is Stage 1 (raw). Run Distillation Prompt first.")

    # Check 2: Conflict Check
    conflicts = metadata.get("conflicts", [])
    breaking = [c for c in conflicts if c.get("severity") == "breaking"]
    if breaking:
        blockers.append(f"{len(breaking)} BREAKING conflicts must be resolved first.")

    significant = [c for c in conflicts if c.get("severity") == "significant"]
    if significant:
        warnings.append(f"{len(significant)} SIGNIFICANT conflicts recommended to resolve.")

    # Check 3: Structure Check
    required = REQUIRED_FIELDS.get(category, {})
    missing = check_missing_fields(content, required)
    if missing:
        blockers.append(f"Missing required fields: {', '.join(missing)}")

    return PromotionStatus(
        can_promote=len(blockers) == 0,
        blockers=blockers,
        warnings=warnings
    )
```

---

## Intelligent Transformation by Category

Promotion extracts structured data and updates the correct Story Bible document.

### Characters → Protagonist.md / Cast.md

```python
async def promote_character(source_path: str) -> PromotionResult:
    """
    Extract character data and update Story Bible.

    1. Determine character type (protagonist, antagonist, supporting)
    2. Extract required fields
    3. Update or create appropriate Story Bible file
    """
    content = read_file(source_path)

    # Use LLM to extract structured data
    extracted = await llm_service.extract_character_fields(
        content,
        fields=["fatal_flaw", "the_lie", "true_character", "arc_start",
                "arc_midpoint", "arc_resolution", "relationships"]
    )

    if extracted.is_protagonist:
        # Update Protagonist.md with extracted fields
        await update_protagonist_md(extracted)
        return PromotionResult(
            success=True,
            target="content/Characters/Protagonist.md",
            fields_updated=extracted.fields
        )
    else:
        # Add to Cast.md
        await append_to_cast_md(extracted)
        return PromotionResult(
            success=True,
            target="content/Characters/Cast.md",
            fields_updated=extracted.fields
        )
```

### World → Rules.md / Locations.md

```python
async def promote_world(source_path: str) -> PromotionResult:
    """
    Extract world data and update Rules.md and/or Locations.md.

    Separates Hard Rules from Soft Lore.
    """
    content = read_file(source_path)

    extracted = await llm_service.extract_world_fields(
        content,
        fields=["hard_rules", "soft_lore", "locations", "factions", "secrets"]
    )

    results = []

    # Hard Rules → Rules.md
    if extracted.hard_rules:
        await merge_hard_rules(extracted.hard_rules)
        results.append(("content/World Bible/Rules.md", extracted.hard_rules))

    # Locations → Locations.md
    if extracted.locations:
        await merge_locations(extracted.locations)
        results.append(("content/World Bible/Locations.md", extracted.locations))

    return PromotionResult(
        success=True,
        targets=[r[0] for r in results],
        data_merged=results
    )
```

### Theme → Theme.md

```python
async def promote_theme(source_path: str) -> PromotionResult:
    """
    Extract theme data and update Theme.md structure.
    """
    content = read_file(source_path)

    extracted = await llm_service.extract_theme_fields(
        content,
        fields=["central_question", "thesis", "counter_thesis",
                "symbols", "protagonist_embodiment"]
    )

    # Update Theme.md with structured sections
    await update_theme_md(extracted)

    return PromotionResult(
        success=True,
        target="content/Story Bible/Themes_and_Philosophy/Theme.md",
        fields_updated=extracted.fields
    )
```

### Plot → Beat_Sheet.md

```python
async def promote_plot(source_path: str) -> PromotionResult:
    """
    Extract plot beats and update Beat_Sheet.md.

    Maps to the 15-beat Save the Cat structure.
    """
    content = read_file(source_path)

    extracted = await llm_service.extract_plot_beats(
        content,
        beats=[
            "opening_image", "theme_stated", "setup", "catalyst", "debate",
            "break_into_two", "b_story", "fun_and_games", "midpoint",
            "bad_guys_close_in", "all_is_lost", "dark_night_of_soul",
            "break_into_three", "finale", "final_image"
        ],
        metadata=["midpoint_type"]  # false_victory or false_defeat
    )

    # Update specific beats in Beat_Sheet.md (not just append)
    await update_beat_sheet(extracted)

    return PromotionResult(
        success=True,
        target="content/Story Bible/Structure/Beat_Sheet.md",
        beats_updated=extracted.beats,
        midpoint_type=extracted.midpoint_type
    )
```

### Voice → Trigger Calibration (Special Case)

```python
async def promote_voice(source_path: str) -> PromotionResult:
    """
    Voice promotion doesn't create a file - it triggers Voice Calibration.

    1. Extract style patterns from content
    2. Feed to Voice Calibration service
    3. Generate Voice Bundle files
    """
    content = read_file(source_path)

    # Don't just save - trigger the full calibration process
    calibration_result = await voice_calibration_service.calibrate_from_samples(
        samples=content,
        extract_patterns=True
    )

    if calibration_result.success:
        return PromotionResult(
            success=True,
            target="Voice Calibration Bundle",
            action="triggered_calibration",
            bundle_files=calibration_result.generated_files
        )
    else:
        return PromotionResult(
            success=False,
            error="Voice calibration failed. Need more distinctive samples."
        )
```

---

## Implementation Tasks

### 1. Promotion Service

**New file**: `backend/services/promotion_service.py`

```python
class PromotionService:
    async def check_promotable(self, file_path: str) -> PromotionStatus:
        """Check if file can be promoted."""
        category = extract_category_from_path(file_path)
        return await self._check_requirements(file_path, category)

    async def promote(self, source_path: str) -> PromotionResult:
        """
        Promote research to Story Bible with intelligent transformation.
        """
        # Get category from path
        category = extract_category_from_path(source_path)

        # Dispatch to category-specific handler
        handlers = {
            "characters": self._promote_character,
            "world": self._promote_world,
            "theme": self._promote_theme,
            "plot": self._promote_plot,
            "voice": self._promote_voice
        }

        handler = handlers.get(category)
        if not handler:
            raise ValueError(f"Unknown category: {category}")

        # Run promotion
        result = await handler(source_path)

        # Mark source as promoted
        if result.success:
            await self._mark_promoted(source_path, result.target)

        return result
```

### 2. Extraction Prompts

Add prompts for field extraction to `backend/prompts/`:

**Character Extraction Prompt**:
```
Extract structured character data from this research note.

CONTENT:
{content}

Extract these fields (return null if not found):
- character_type: "protagonist" | "antagonist" | "supporting"
- fatal_flaw: The character's internal weakness (NOT circumstance)
- the_lie: The mistaken belief driving the flaw
- true_character: Who they become after the arc
- arc_start: Their state at the beginning
- arc_midpoint: The crisis/turning point
- arc_resolution: Their state at the end
- relationships: List of key relationships

Return as JSON.
```

### 3. Promotion UI

**File**: `frontend/src/lib/components/PromotionModal.svelte`

Flow:
1. User clicks "Promote to Story Bible" on a Research Note
2. System runs Structure Check
3. If blockers → show what's missing, offer Distillation Prompt
4. If warnings → show but allow proceed
5. If clear → show preview of what will be updated
6. User confirms → execute promotion

### 4. Update Knowledge Graph

After promotion:
```python
async def _post_promotion_tasks(self, source_path: str, result: PromotionResult):
    """Tasks to run after successful promotion."""

    # Re-ingest the updated Story Bible file
    await graph_service.ingest_file(result.target)

    # Update entity relationships
    await graph_service.refresh_relationships(result.target)

    # Mark research source as promoted (keep for reference)
    await self._mark_promoted(source_path, result.target)
```

---

## API Endpoints

```python
# Check if file can be promoted
GET /promotion/check?path=workspace/research/characters/protagonist.md
Response: {
    "can_promote": false,
    "blockers": ["Missing required field: fatal_flaw"],
    "warnings": [],
    "category": "characters",
    "target": "content/Characters/Protagonist.md"
}

# Preview promotion (what will change)
GET /promotion/preview?path=workspace/research/characters/protagonist.md
Response: {
    "category": "characters",
    "extracted_fields": {
        "fatal_flaw": "Need for control",
        "the_lie": "I can't trust anyone"
    },
    "target_file": "content/Characters/Protagonist.md",
    "merge_strategy": "update_fields"  # vs "append" vs "replace"
}

# Execute promotion
POST /promotion/execute
Request: {
    "source": "workspace/research/characters/protagonist.md",
    "confirm_warnings": true  # Acknowledge SIGNIFICANT conflicts
}
Response: {
    "success": true,
    "target": "content/Characters/Protagonist.md",
    "fields_updated": ["fatal_flaw", "the_lie", "arc_start"],
    "graph_updated": true
}
```

---

## Research Note Status After Promotion

```yaml
---
source: NotebookLM
category: characters
status: promoted
stage: 2
promoted_to: content/Characters/Protagonist.md
promoted_date: 2024-12-06
promoted_fields:
  - fatal_flaw
  - the_lie
  - arc_start
---
```

File stays in workspace/research/ for reference but is marked as promoted.

---

## Testing

### Structure Check Tests
1. Try to promote character note without Fatal Flaw → Expect: Blocked
2. Try to promote plot note without Midpoint → Expect: Blocked
3. Try to promote Stage 1 content → Expect: Blocked with Distillation Prompt

### Category-Specific Promotion Tests
1. Promote character with all fields → Verify Protagonist.md updated correctly
2. Promote world with Hard Rules → Verify Rules.md merged (not replaced)
3. Promote plot beats → Verify Beat_Sheet.md beats updated individually
4. Promote voice samples → Verify Voice Calibration triggered

### Merge Strategy Tests
1. Promote when Protagonist.md already has some fields → Verify merge, not replace
2. Promote conflicting data → Verify handled (should be caught by Phase 2)

---

## Acceptance Criteria

- [ ] Structure Check validates required fields before promotion
- [ ] Category-specific extraction prompts implemented
- [ ] Characters promote to Protagonist.md with field extraction
- [ ] World separates Hard Rules from Soft Lore
- [ ] Theme extracts Central Question, Thesis, Counter-thesis
- [ ] Plot updates specific beats in Beat_Sheet.md
- [ ] Voice triggers calibration instead of file copy
- [ ] Knowledge Graph updated after promotion
- [ ] Source file marked as promoted (not deleted)
- [ ] Preview shows what will change before confirmation

---

## Dependencies

- **Phase 1** (file-based research with 5 categories)
- **Phase 2** (conflict detection - for prerequisite check)

---

## Handoff

When complete:
```bash
git add backend/services/promotion_service.py backend/prompts/ frontend/
git commit -m "feat: Intelligent promotion with category-specific transformation

- Structure Check validates required fields before promotion
- Characters extract Fatal Flaw, The Lie, Arc → Protagonist.md
- World separates Hard Rules → Rules.md
- Plot extracts 15 beats → Beat_Sheet.md
- Voice triggers calibration (not file copy)
- Knowledge Graph updated after promotion

Closes Phase 4 of WORKSPACE_FILE_SYSTEM.md"
git push -u origin <branch-name>
```

Report: branch name, commit hash, test results

---

*Parent spec: [WORKSPACE_FILE_SYSTEM.md](./WORKSPACE_FILE_SYSTEM.md)*
*Priority: MEDIUM - Workflow completion*
