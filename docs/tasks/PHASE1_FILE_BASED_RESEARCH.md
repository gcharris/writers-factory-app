# Phase 1: File-Based Research (MVP)

> Save NotebookLM extractions as editable markdown files instead of SQLite entries.

## Current State

```
NotebookLM Query → API Response → SQLite KB Entry → (invisible to user)
```

## Target State

```
NotebookLM Query → API Response → Markdown file in workspace/research/{category}/
                               → Visible in File Tree
                               → Editable in Main Editor
                               → "Copy to Chat" action available
```

---

## The 5 Core Categories (STRICT)

Research files MUST be saved into exactly one of these 5 categories, matching the 5 Core Notebooks:

```
workspace/research/
├── characters/   # From CHARACTER Core Notebook
├── world/        # From WORLD Core Notebook
├── theme/        # From THEME Core Notebook
├── plot/         # From PLOT Core Notebook
└── voice/        # From VOICE Core Notebook
```

### Why These 5?

| Category | Source Notebook | Maps to Story Bible |
|----------|-----------------|---------------------|
| `characters/` | Character Notebook | `Protagonist.md`, `Cast.md` |
| `world/` | World Notebook | `Rules.md`, `Locations.md` |
| `theme/` | Theme Notebook | `Theme.md` |
| `plot/` | Plot Notebook | `Beat_Sheet.md` |
| `voice/` | Voice Notebook | Voice Calibration Bundle |

### Category Enforcement

- UI dropdown shows ONLY these 5 categories (no "Other" or "Misc")
- Backend validates category is one of: `characters`, `world`, `theme`, `plot`, `voice`
- Invalid categories are rejected with helpful error message

---

## Implementation Tasks

### 1. Create Directory Structure

**On first save**, create:
```
workspace/
└── research/
    ├── characters/
    ├── world/
    ├── theme/
    ├── plot/
    └── voice/
```

**File**: `backend/api.py` or new `backend/services/workspace_service.py`

```python
VALID_RESEARCH_CATEGORIES = ["characters", "world", "theme", "plot", "voice"]

def ensure_research_directories(workspace_path: str):
    """Create the 5 Core research directories."""
    research_path = os.path.join(workspace_path, "workspace", "research")
    for category in VALID_RESEARCH_CATEGORIES:
        os.makedirs(os.path.join(research_path, category), exist_ok=True)
```

### 2. Modify Save Endpoint

**Current endpoint**: `POST /notebooklm/save-to-kb`

**Changes**:
- Validate category is in `VALID_RESEARCH_CATEGORIES`
- Still save to SQLite for backward compatibility
- ALSO save as markdown file to `workspace/research/{category}/{key}.md`

**File format**:
```markdown
---
source: NotebookLM
notebook_name: "Character Research"
notebook_id: ce3c54ad-fc95-44ba-a88a-19573bd6aac2
extracted: 2024-12-06T11:07:08
category: characters
key: protagonist_profile
status: draft
stage: 2  # Indicates this came from a Core Notebook (Stage 2)
---

# Protagonist Profile - Umar

[Extraction content here]

---
## User Notes

[Space for author annotations]
```

### 3. Update UI Category Selector

**File**: `frontend/src/lib/components/NotebookLMPanel.svelte`

Replace any generic category input with a strict dropdown:

```svelte
<select bind:value={selectedCategory}>
    <option value="characters">Characters (Fatal Flaw, Arc, Cast)</option>
    <option value="world">World (Hard Rules, Locations)</option>
    <option value="theme">Theme (Central Question, Symbols)</option>
    <option value="plot">Plot (15 Beats, Structure)</option>
    <option value="voice">Voice (Style Targets, Anti-patterns)</option>
</select>
```

### 4. Update File Tree

**File**: `frontend/src/lib/components/FileTree.svelte`

- Show `workspace/research/` directory in tree
- Use icons to distinguish the 5 categories:
  - 👤 characters/
  - 🌍 world/
  - 💭 theme/
  - 📊 plot/
  - ✍️ voice/

### 5. Add "Copy to Chat" Button

**Files**:
- `NotebookLMPanel.svelte` - Add button on Saved Notes cards
- `FileTree.svelte` - Add hover action on files

**Behavior**:
- Copies file content (or selection) to chat input
- Formats as:
  ```
  [From: workspace/research/characters/protagonist.md]

  <content>
  ```

### 6. Open in Editor

**Already works** if File Tree shows the workspace directory. User clicks file → opens in Monaco editor → can edit → Cmd+S saves.

---

## API Changes

### Modified Endpoints

```python
# Save extraction as file (modified)
POST /notebooklm/save-to-kb
Request: {
    "content": "...",
    "category": "characters",  # MUST be one of 5 valid categories
    "key": "protagonist_profile",
    "notebook_id": "..."
}
Response: {
    "success": true,
    "file_path": "workspace/research/characters/protagonist_profile.md"
}

# Validation error response
Response (400): {
    "error": "Invalid category 'misc'. Must be one of: characters, world, theme, plot, voice"
}
```

### New Endpoints

```python
# List research files
GET /workspace/research
Response: {
    "characters": ["protagonist_profile.md", "antagonist_notes.md"],
    "world": ["hard_rules.md", "locations.md"],
    "theme": [],
    "plot": ["beat_sheet_draft.md"],
    "voice": ["style_targets.md"]
}

# Read research file
GET /workspace/research/{category}/{filename}
Response: {
    "content": "...",
    "metadata": {...}
}
```

---

## Frontend Changes

### NotebookLMPanel.svelte
- Category selector: Strict 5-option dropdown (no free text)
- "Saved Notes" tab: Add "Copy to Chat" button on each card
- "Saved Notes" tab: Add "Open in Editor" button on each card
- Group saved notes by category with headers

### FileTree.svelte
- Add `workspace/research/` to visible roots
- Category icons for visual distinction
- Hover action: "Copy to Chat"

### ForemanPanel.svelte
- Accept pasted content in chat input (already works)

---

## Testing

### Happy Path
1. Query Character notebook: "What is the protagonist's Fatal Flaw?"
2. Click "Save to Research Notes"
3. Select category: "Characters"
4. Verify file created at `workspace/research/characters/{name}.md`
5. Verify file appears in File Tree under characters/
6. Click file → opens in editor
7. Edit and save (Cmd+S)
8. Click "Copy to Chat" → content appears in chat input

### Category Validation
1. Try to save with category "misc" → Expect: Error message
2. Try to save with category "craft" → Expect: Error message (use "voice" instead)
3. Save with category "characters" → Expect: Success

### Stage Detection
1. Note saved from Core Notebook should have `stage: 2` in frontmatter
2. This signals to Phase 2/4 that it's distilled data, not raw

---

## Acceptance Criteria

- [ ] `workspace/research/` with 5 subdirectories created on first save
- [ ] Category validation rejects invalid categories
- [ ] UI shows strict 5-option dropdown (not free text)
- [ ] Extractions saved as markdown files with YAML frontmatter
- [ ] Files visible in File Tree under workspace/research/
- [ ] Files grouped by category with appropriate icons
- [ ] Files open in editor when clicked
- [ ] Edits save correctly (Cmd+S)
- [ ] "Copy to Chat" button works on saved notes
- [ ] Backward compatibility: SQLite KB still populated

---

## Dependencies

- **Phase 0 must be complete** (Foreman needs to understand the 5 Core Notebooks)

---

## Handoff

When complete:
```bash
git add backend/ frontend/src/lib/components/
git commit -m "feat: File-based research with 5 Core categories

- Research saves to workspace/research/{category}/
- Strict 5 categories: characters, world, theme, plot, voice
- Category validation rejects invalid inputs
- Files visible in File Tree, editable in Monaco
- Copy to Chat functionality added

Closes Phase 1 of WORKSPACE_FILE_SYSTEM.md"
git push -u origin <branch-name>
```

Report: branch name, commit hash, test results

---

*Parent spec: [WORKSPACE_FILE_SYSTEM.md](./WORKSPACE_FILE_SYSTEM.md)*
*Priority: HIGH - Core feature*
