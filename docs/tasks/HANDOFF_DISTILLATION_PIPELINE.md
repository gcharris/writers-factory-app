# Handoff: Implement Distillation Pipeline

> For Claude Code Desktop agent working in a git worktree

## Your Mission

Implement the **Distillation Pipeline** feature set as specified in `docs/tasks/WORKSPACE_FILE_SYSTEM.md` and its phase specs.

## Before You Start

```bash
git fetch origin
git pull origin main
```

Read these specs IN ORDER:
1. `docs/tasks/WORKSPACE_FILE_SYSTEM.md` - Master spec with full context
2. `docs/tasks/PHASE0_FOREMAN_KNOWLEDGE.md` - Start here (blocker for others)
3. `docs/tasks/PHASE1_FILE_BASED_RESEARCH.md` - Core file system
4. `docs/tasks/PHASE2_CONFLICT_DETECTION.md` - Quality gates
5. `docs/tasks/PHASE4_PROMOTION_WORKFLOW.md` - Intelligent extraction
6. `docs/tasks/PHASE5_DOCUMENTATION.md` - User-facing docs

Also read:
- `docs/course_information/5 Core Notebooks.md` - The pedagogical foundation
- `docs/course_information/The Distillation Pipeline.md` - The educational concept

---

## Implementation Order

### Phase 0: Foreman Knowledge (HIGH - Do First)

**File to modify**: `backend/agents/foreman.py`

**Task**: Add ~1000 tokens of product knowledge to Foreman's system prompt including:
- Distillation Pipeline (Stage 1 → Stage 2 → Stage 3)
- 5 Core Notebooks requirement
- Distillation Prompts library
- Graceful failure behavior (offer prompts when extraction fails)

**Find**: The base system prompt (likely `FOREMAN_BASE_PROMPT` or in `_build_system_prompt()`)

**Add**: The entire "WRITERS FACTORY PRODUCT KNOWLEDGE" block from the Phase 0 spec

**Test**:
```bash
# Start backend
cd backend && uvicorn api:app --reload --port 8000

# Test via API
curl -X POST http://localhost:8000/foreman/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a notebook?"}'
# Should mention "NotebookLM notebook", not hallucinate

curl -X POST http://localhost:8000/foreman/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many notebooks do I need?"}'
# Should say "5 Core Notebooks"
```

---

### Phase 1: File-Based Research (HIGH - Core Feature)

**Files to create/modify**:
- `backend/services/workspace_service.py` (new)
- `backend/api.py` (modify save endpoint)
- `frontend/src/lib/components/NotebookLMPanel.svelte` (modify)
- `frontend/src/lib/components/FileTree.svelte` (modify)

**Key Implementation**:

1. **Create workspace service**:
```python
# backend/services/workspace_service.py
import os
from pathlib import Path

VALID_RESEARCH_CATEGORIES = ["characters", "world", "theme", "plot", "voice"]

class WorkspaceService:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)

    def ensure_research_directories(self):
        """Create the 5 Core research directories."""
        research_path = self.workspace_root / "workspace" / "research"
        for category in VALID_RESEARCH_CATEGORIES:
            (research_path / category).mkdir(parents=True, exist_ok=True)

    def validate_category(self, category: str) -> bool:
        return category in VALID_RESEARCH_CATEGORIES

    def save_research_note(self, category: str, key: str, content: str, metadata: dict) -> Path:
        if not self.validate_category(category):
            raise ValueError(f"Invalid category '{category}'. Must be one of: {VALID_RESEARCH_CATEGORIES}")

        self.ensure_research_directories()
        file_path = self.workspace_root / "workspace" / "research" / category / f"{key}.md"

        # Build markdown with YAML frontmatter
        frontmatter = f"""---
source: NotebookLM
notebook_name: "{metadata.get('notebook_name', '')}"
notebook_id: {metadata.get('notebook_id', '')}
extracted: {metadata.get('extracted', '')}
category: {category}
key: {key}
status: draft
stage: 2
---

"""
        file_path.write_text(frontmatter + content + "\n\n---\n## User Notes\n\n")
        return file_path
```

2. **Modify save endpoint** in `backend/api.py`:
- Find `POST /notebooklm/save-to-kb`
- Add category validation
- Call workspace service to save file
- Keep SQLite save for backwards compatibility

3. **Update frontend category selector** in `NotebookLMPanel.svelte`:
```svelte
<select bind:value={selectedCategory}>
    <option value="characters">Characters (Fatal Flaw, Arc, Cast)</option>
    <option value="world">World (Hard Rules, Locations)</option>
    <option value="theme">Theme (Central Question, Symbols)</option>
    <option value="plot">Plot (15 Beats, Structure)</option>
    <option value="voice">Voice (Style Targets, Anti-patterns)</option>
</select>
```

---

### Phase 2: Conflict Detection (MEDIUM)

**Files to create**:
- `backend/services/conflict_detection_service.py` (new)

**Key Implementation**:

1. **Stage Check** - Detect if content is Stage 1 (raw) or Stage 2 (distilled):
```python
def is_structured_stage2_content(content: str, category: str) -> bool:
    markers = {
        "characters": ["fatal flaw", "the lie", "arc:", "true character"],
        "world": ["hard rule", "cannot be broken", "world rule"],
        "theme": ["central question", "thesis", "counter-thesis"],
        "plot": ["beat", "catalyst", "midpoint", "all is lost"],
        "voice": []  # Voice always treated as Stage 2
    }
    return any(m in content.lower() for m in markers.get(category, []))
```

2. **Hard Rules Check** - Load from `content/World Bible/Rules.md`, check new content for violations

3. **LLM conflict analysis** - Use existing `llm_service` to compare content

---

### Phase 4: Intelligent Promotion (MEDIUM)

**Files to create**:
- `backend/services/promotion_service.py` (new)
- `backend/prompts/extraction_prompts.py` (new)

**Key Concept**: Promotion is NOT file copy. It's intelligent extraction:

| Category | Extracts | Updates |
|----------|----------|---------|
| characters | Fatal Flaw, The Lie, Arc | `Protagonist.md` |
| world | Hard Rules, Locations | `Rules.md` |
| theme | Central Question, Thesis | `Theme.md` |
| plot | 15 Beats | `Beat_Sheet.md` |
| voice | N/A | Triggers Voice Calibration |

**Use LLM for extraction**:
```python
EXTRACT_CHARACTER_PROMPT = """
Extract structured character data from this content:
{content}

Return JSON with:
- character_type: "protagonist" | "antagonist" | "supporting"
- fatal_flaw: string or null
- the_lie: string or null
- arc_start: string or null
- arc_resolution: string or null
"""
```

---

### Phase 5: Documentation (LOW)

**Files to create**:
- `docs/DISTILLATION_PROMPTS.md`
- `docs/FIVE_CORE_NOTEBOOKS.md`

**Content**: Copy from Phase 5 spec - these are user-facing copy-paste prompts

---

## Testing Checklist

Before declaring done:

- [ ] Foreman correctly explains 5 Core Notebooks when asked
- [ ] Foreman offers Distillation Prompts when extraction fails
- [ ] Category dropdown shows exactly 5 options (no "misc")
- [ ] Files save to `workspace/research/{category}/`
- [ ] Invalid categories are rejected with helpful error
- [ ] Stage 1 content shows warning, skips conflict detection
- [ ] Hard Rule violations are BREAKING severity
- [ ] Promotion extracts structured fields (not just copies)
- [ ] `npm run check` passes in frontend
- [ ] No regressions in existing functionality

---

## Commit Strategy

Create ONE commit per phase:

```bash
# After Phase 0
git add backend/agents/foreman.py
git commit -m "feat(foreman): Add Distillation Pipeline knowledge

- Teaches Stage 1 → Stage 2 → Stage 3 pipeline
- 5 Core Notebooks requirement
- Distillation Prompts for graceful failure"

# After Phase 1
git add backend/services/workspace_service.py backend/api.py frontend/
git commit -m "feat: File-based research with 5 Core categories

- workspace/research/{category}/ structure
- Strict category validation
- YAML frontmatter with stage tracking"

# etc.
```

---

## When You're Done

```bash
git push -u origin <your-branch-name>
```

Then report back:
```
Work complete on branch `<branch-name>` (commit <hash>).
Pushed to remote.

Implemented:
- Phase 0: Foreman Distillation Knowledge ✓
- Phase 1: File-Based Research ✓
- Phase 2: Conflict Detection ✓
- Phase 4: Promotion Workflow ✓
- Phase 5: Documentation ✓

All tests pass. npm run check clean.

IDE agent: Run `git fetch && git merge <branch-name>`
```

---

## Questions? Don't Improvise

If something in the specs is unclear:
1. Read the related `docs/course_information/` files
2. Check `docs/ARCHITECTURE.md` for system context
3. If still unclear, STOP and ask rather than guessing

The specs are comprehensive. Follow them closely.

---

*Created: 2024-12-06*
*For: Claude Code Desktop in worktree*
