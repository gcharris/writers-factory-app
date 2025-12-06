# Phase 2: Conflict Detection

> Flag contradictions in research before they pollute the Knowledge Graph.

## Problem

User has two research notes:
- "Character Profile" says Umar is 45 years old
- "World Timeline" says the protagonist is in their 30s

Without conflict detection, both get ingested → Knowledge Graph has contradictions.

**Additional Problem**: If the research contains Stage 1 (raw/unstructured) data, conflict detection produces false positives because you can't compare "vibes" to "facts."

---

## Stage Check (Critical Pre-Requisite)

Before running conflict detection, check if the content is structured (Stage 2) or raw (Stage 1):

### Stage Detection Logic

```python
def is_structured_stage2_content(content: str, category: str) -> bool:
    """
    Check if content appears to be distilled Stage 2 data.

    Stage 2 content should have explicit structure markers based on category.
    """
    if category == "characters":
        # Must have Fatal Flaw OR The Lie OR character arc markers
        markers = ["fatal flaw", "the lie", "arc:", "true character"]
        return any(marker in content.lower() for marker in markers)

    elif category == "world":
        # Must have Hard Rules OR explicit world rules
        markers = ["hard rule", "cannot be broken", "world rule", "law:"]
        return any(marker in content.lower() for marker in markers)

    elif category == "theme":
        # Must have theme question OR thesis/counter-thesis
        markers = ["central question", "theme:", "thesis", "counter-thesis", "argument"]
        return any(marker in content.lower() for marker in markers)

    elif category == "plot":
        # Must have beat markers OR structure references
        markers = ["beat", "catalyst", "midpoint", "all is lost", "act 1", "act 2"]
        return any(marker in content.lower() for marker in markers)

    elif category == "voice":
        # Voice notes are less structured - always treat as Stage 2 if saved
        return True

    return False
```

### Skip Conflict Detection for Stage 1

If `is_structured_stage2_content()` returns `False`:

1. **Don't run conflict detection** - you can't compare vibes to facts
2. **Mark the file with a warning** in frontmatter: `stage: 1 (raw, needs distillation)`
3. **Show user guidance**: "This appears to be raw research. Consider running a Distillation Prompt before conflict checking."

---

## Hard Rules Priority

Conflict detection must check against World "Hard Rules" FIRST. Hard Rules are immutable - any contradiction is BREAKING severity.

### Conflict Priority Order

```python
CONFLICT_PRIORITY = [
    ("world", "hard_rules"),     # BREAKING - Hard Rules cannot be violated
    ("characters", "facts"),     # SIGNIFICANT - Ages, capabilities, relationships
    ("plot", "timeline"),        # SIGNIFICANT - Event order, causality
    ("theme", "core"),           # MINOR - Thematic consistency (can evolve)
    ("voice", None),             # SKIP - Voice is subjective, no conflicts
]
```

### Hard Rules Example

If `Rules.md` or `world/hard_rules.md` contains:
```markdown
## Hard Rules (Cannot Be Broken)
1. Magic requires blood sacrifice
2. The dead cannot return
3. Technology fails within the Enclave
```

And new research says:
```markdown
Marcus cast a spell with just a thought, no sacrifice needed.
```

This is a **BREAKING** conflict - must be resolved before proceeding.

---

## Implementation Tasks

### 1. Conflict Detection Service

**New file**: `backend/services/conflict_detection_service.py`

```python
from enum import Enum

class ConflictSeverity(Enum):
    MINOR = "minor"           # Easily reconciled, stylistic
    SIGNIFICANT = "significant"  # Needs author decision
    BREAKING = "breaking"     # Fundamentally incompatible with Hard Rules

class Conflict:
    file: str
    description: str
    severity: ConflictSeverity
    rule_violated: Optional[str]  # If Hard Rule, which one?

async def detect_conflicts(
    new_content: str,
    category: str,
    skip_stage_check: bool = False
) -> ConflictResult:
    """
    Detect conflicts with existing research.

    1. Stage Check - skip if raw Stage 1 data
    2. Hard Rules Check - any World Hard Rule violations?
    3. Category Facts Check - contradicting established facts?
    """

    # Step 1: Stage Check
    if not skip_stage_check and not is_structured_stage2_content(new_content, category):
        return ConflictResult(
            stage_warning=True,
            message="Content appears to be raw Stage 1 data. Distillation recommended.",
            conflicts=[]
        )

    conflicts = []

    # Step 2: Hard Rules Check (always, regardless of category)
    hard_rules = load_hard_rules()  # From world/hard_rules.md or Rules.md
    if hard_rules:
        rule_conflicts = await check_hard_rules_violations(new_content, hard_rules)
        for rc in rule_conflicts:
            conflicts.append(Conflict(
                file="content/World Bible/Rules.md",
                description=f"Violates Hard Rule: {rc.rule}",
                severity=ConflictSeverity.BREAKING,
                rule_violated=rc.rule
            ))

    # Step 3: Category-Specific Fact Check
    if category != "voice":  # Voice has no fact conflicts
        existing_files = load_research_files(category)
        for file in existing_files:
            result = await llm_service.analyze_contradiction(
                new_content,
                file.content,
                focus=get_focus_for_category(category)
            )
            if result.has_conflict:
                conflicts.append(Conflict(
                    file=file.path,
                    description=result.explanation,
                    severity=result.severity
                ))

    return ConflictResult(
        stage_warning=False,
        conflicts=conflicts
    )

def get_focus_for_category(category: str) -> str:
    """Return the conflict detection focus based on category."""
    focuses = {
        "characters": "ages, relationships, capabilities, physical descriptions, backstory facts",
        "world": "locations, rules, factions, timeline, technology limits",
        "theme": "central argument, thesis vs counter-thesis consistency",
        "plot": "event sequence, causality, beat placement, timeline",
        "voice": None  # Voice doesn't get fact-checked
    }
    return focuses.get(category, "factual claims")
```

### 2. Integrate with Save Flow

**Modify**: `POST /notebooklm/save-to-kb`

Before saving:
1. Run Stage Check → warn if Stage 1
2. Run Hard Rules Check → block if BREAKING
3. Run category conflicts → warn if conflicts
4. Let user decide resolution

**Response format**:
```json
{
  "stage_warning": true,
  "stage_message": "This appears to be raw research. Consider distillation first.",
  "conflicts": [
    {
      "file": "content/World Bible/Rules.md",
      "description": "Violates Hard Rule: Magic requires blood sacrifice",
      "severity": "breaking",
      "rule_violated": "Magic requires blood sacrifice"
    }
  ],
  "action_required": "resolve_conflicts"
}
```

### 3. Conflict Resolution UI

**New component**: `ConflictResolutionModal.svelte`

Display:
- **Stage Warning** (if Stage 1 detected): Offer Distillation Prompt
- **BREAKING conflicts** at top with red highlight - MUST be resolved
- **SIGNIFICANT conflicts** in yellow - recommended to resolve
- **MINOR conflicts** in gray - can ignore

Actions:
- **Get Distillation Prompt** (for Stage 1 warning)
- **Keep Both** - Save anyway, author will reconcile manually
- **Prefer New** - Archive old, use new
- **Prefer Existing** - Discard new
- **Edit & Fix** - Open editor to correct the contradiction

### 4. Update Frontmatter

When saved with conflicts or warnings:

```yaml
---
source: NotebookLM
category: characters
status: draft
stage: 2  # or "1 (raw, needs distillation)"
conflicts:
  - file: content/World Bible/Rules.md
    description: Magic rule violation
    severity: breaking
    status: unresolved
---
```

### 5. Conflict Indicators in File Tree

- 🔴 Red badge: BREAKING unresolved conflicts
- 🟡 Yellow badge: SIGNIFICANT unresolved conflicts
- ⚪ Gray text: Stage 1 (raw) data needing distillation

---

## Conflict Detection Prompts

### Hard Rules Check Prompt

```
You are checking if new content violates established HARD RULES.

HARD RULES (These CANNOT be broken in this story world):
{hard_rules}

NEW CONTENT:
{new_content}

For each Hard Rule, check if the new content violates it.
A violation means the new content describes something that contradicts a Hard Rule.

Respond with:
- violations: [list of violated rules with explanations]
- severity: "breaking" if any violations, "none" if no violations
```

### Category Fact Check Prompt

```
Compare these two research excerpts for factual contradictions.

CATEGORY: {category}
FOCUS ON: {focus}

EXCERPT A (NEW):
{new_content}

EXCERPT B (EXISTING, from {file_path}):
{existing_content}

Ignore: writing style differences, level of detail, opinion vs fact, Stage 1 "vibes".
Report only FACTUAL contradictions.

Respond with:
- contradiction: true/false
- severity:
  - "minor" = stylistic or easily reconciled
  - "significant" = needs author decision
  - "breaking" = fundamentally incompatible (reserved for Hard Rule violations)
- explanation: Brief description of the conflict
```

---

## Testing

### Stage Check Tests
1. Save raw podcast transcript → Expect: Stage 1 warning, skip conflict detection
2. Save distilled character profile with Fatal Flaw → Expect: No warning, run conflicts

### Hard Rules Tests
1. Add Hard Rule: "Magic requires blood"
2. Save research saying "effortless magic" → Expect: BREAKING conflict
3. Resolve conflict → Expect: Can save after resolution

### Category Conflict Tests
1. Save character age as 45
2. Try to save character age as 30 → Expect: SIGNIFICANT conflict
3. Test all resolution options

---

## Acceptance Criteria

- [ ] Stage Check implemented - detects Stage 1 vs Stage 2 content
- [ ] Stage 1 content shows warning, skips conflict detection
- [ ] Hard Rules loaded from World Bible
- [ ] Hard Rule violations flagged as BREAKING severity
- [ ] Category-specific fact checking implemented
- [ ] Voice category skipped (no fact conflicts)
- [ ] Conflict resolution modal shows severity levels
- [ ] BREAKING conflicts require resolution before promotion
- [ ] Frontmatter tracks stage and conflicts
- [ ] File tree shows appropriate badges

---

## Dependencies

- **Phase 1 must be complete** (needs file-based research with 5 categories)
- **World Rules.md should exist** for Hard Rules checking (graceful if missing)

---

## Handoff

When complete:
```bash
git add backend/services/conflict_detection_service.py frontend/
git commit -m "feat: Conflict detection with Stage Check and Hard Rules priority

- Stage Check detects raw vs distilled content
- Hard Rules violations are BREAKING severity
- Category-specific fact checking
- Conflict resolution UI with severity levels
- Skips Voice category (no fact conflicts)

Closes Phase 2 of WORKSPACE_FILE_SYSTEM.md"
git push -u origin <branch-name>
```

Report: branch name, commit hash, test results

---

*Parent spec: [WORKSPACE_FILE_SYSTEM.md](./WORKSPACE_FILE_SYSTEM.md)*
*Priority: MEDIUM - Quality improvement*
