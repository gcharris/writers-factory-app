# UI Simplification Task

**Status**: ✅ COMPLETE
**Priority**: HIGH
**Created**: 2025-11-28
**Completed**: 2025-11-28

---

## Overview

Simplify the Writers Factory UI to match IDE conventions (VS Code, Cursor). Remove redundant elements, fix broken functionality, and improve usability.

---

## Tasks

### 1. Fix FileTree Folder Expansion (CRITICAL)
**File:** `frontend/src/lib/components/FileTree.svelte`, `TreeNode.svelte`

**Problem:** Clicking folder names (Characters, Story Bible, World Bible) does nothing.

**Solution:** Debug the Svelte reactivity issue. The `expandedFolders` object must trigger re-renders when folders are toggled.

**Test:** Click any folder → it should expand/collapse.

---

### 2. Chat Works Without Project (CRITICAL)
**File:** `backend/agents/foreman.py`

**Status:** PARTIALLY DONE - basic casual mode added, but needs Writers Factory knowledge.

**Problem:** New users get "No active project" error when trying to chat.

**Solution:** Already implemented casual chat mode. Now enhance the system prompt with Writers Factory knowledge (see Task 3).

---

### 3. Chat Assistant Knows Writers Factory
**File:** `backend/agents/foreman.py` (line ~616, the NO PROJECT MODE system prompt)

**Current prompt:** Generic writing assistant

**New prompt should include:**
- What Writers Factory is (professional novel-writing IDE)
- The Narrative Protocol methodology ("Structure Before Freedom")
- Story Bible requirements: Protagonist (Fatal Flaw, The Lie, Arc), Beat Sheet (15 beats), Theme, World Rules
- The four modes: ARCHITECT → VOICE_CALIBRATION → DIRECTOR → EDITOR
- How to start: "Use the Story Bible Wizard to set up your project"
- Encouragement to explore the app and ask questions

---

### 4. Remove "THE FOREMAN" Header
**File:** `frontend/src/lib/components/MainLayout.svelte`

**Problem:** Redundant header above chat panel says "THE FOREMAN"

**Solution:** Delete the entire `panel-header` div for the foreman panel (around lines 192-221).

---

### 5. Simplify Chat Panel Top Section
**File:** `frontend/src/lib/components/ForemanPanel.svelte`

**Remove:**
- "Muse • Ready" header section at top
- All icons currently at top (Notebook, Studio, Graph, Settings icons)

**Add:**
- `+` button (new chat) - top right
- Clock/history icon (view chat history) - top right

**Keep:**
- Agent name "Muse" at bottom next to input box only

---

### 6. Simplify Binder to "EXPLORER" Style
**Files:** `frontend/src/lib/components/MainLayout.svelte`, `FileTree.svelte`

**Current (two redundant headers):**
```
┌─────────────────────────────┐
│ < BINDER              [icon]│
├─────────────────────────────┤
│ BINDER                      │
│ content                [📁] │
├─────────────────────────────┤
│ > Characters                │
```

**New (single clean header):**
```
┌─────────────────────────────┐
│ EXPLORER              [📁]  │
├─────────────────────────────┤
│ ▼ /content                  │
│   > Characters              │
│   > Story Bible             │
```

**Changes:**
- Rename "BINDER" to "EXPLORER"
- Remove duplicate header sections
- Keep only: title + folder open icon
- Remove `<` collapse button from here (moved to toolbar - see Task 9)
- Show `/content` as root folder name in tree (with leading slash)

---

### 7. Editor Shows Filename Only
**File:** `frontend/src/lib/components/Editor.svelte`

**Current:** `/content/1.21.3 Return from Q-Space 2.md`

**New:** `1.21.3 Return from Q-Space 2.md`

**Solution:** Extract just the filename from the path, not the full path.

---

### 8. Remove Editor Expand Button
**File:** `frontend/src/lib/components/Editor.svelte` or `MainLayout.svelte`

**Problem:** The expand button (bottom right of editor, looks like `⤢`) leads to fullscreen mode where clicking X closes the entire app.

**Solution:** Remove this button entirely.

---

### 9. Move Panel Toggle Buttons to Toolbar
**File:** `frontend/src/lib/components/MainLayout.svelte`

**Remove:**
- `<` button from left panel header
- `>` button from right panel header

**Add to main toolbar (top bar with "Writers Factory"):**
- `[◧]` icon - Toggle left panel (Explorer)
- `[◨]` icon - Toggle right panel (Chat)

**Position:** After "Writers Factory" title, before window controls

**Example:**
```
┌─────────────────────────────────────────────────────────────┐
│ ✏️ Writers Factory     [◧] [◨]                    [─][□][✕] │
└─────────────────────────────────────────────────────────────┘
```

---

### 10. Multi-Project Support (Future - Document Only)
**DO NOT IMPLEMENT YET** - Just document this for future reference.

**Concept:**
- On first launch: No project folder, user must create or open one
- Creating new project creates: `ProjectName/content/Characters/`, `Story Bible/`, `World Bible/`
- Explorer root shows project folder, not hardcoded "content"

---

## Files to Modify

| File | Tasks |
|------|-------|
| `MainLayout.svelte` | 4, 6, 8, 9 |
| `ForemanPanel.svelte` | 5 |
| `FileTree.svelte` | 1, 6 |
| `TreeNode.svelte` | 1 |
| `Editor.svelte` | 7, 8 |
| `foreman.py` | 2, 3 |

---

## Testing Checklist

After implementation, verify:

- [x] Click folder in Explorer → expands/collapses
- [x] Send chat message without project → get helpful response about Writers Factory
- [x] No "THE FOREMAN" header visible
- [x] No "Muse • Ready" at top of chat (only at bottom by input)
- [x] Chat has `+` and history buttons at top
- [x] Explorer has single clean header (no duplicate BINDER)
- [x] Editor shows filename only (not full path)
- [x] No expand button in editor
- [x] Panel toggle buttons in main toolbar work
- [x] No `<` `>` buttons on panel headers

---

## Commands

```bash
# Start backend
cd /Users/gch2024/Documents/Documents\ -\ Mac\ Mini/writers-factory-app
uvicorn backend.api:app --reload --port 8000

# Start frontend (in separate terminal)
cd /Users/gch2024/Documents/Documents\ -\ Mac\ Mini/writers-factory-app/frontend
npm run tauri dev

# Type check
npm run check
```

---

## Notes for Claude Agent

- Run `npm run check` before considering work complete
- Test each change in the running Tauri app
- Commit frequently with clear messages
- Report branch name and commit hash when done

---

*Document created: 2025-11-28*
