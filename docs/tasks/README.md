# Writers Factory - Task Queue

**Created**: 2025-11-26
**Status**: Ready for delegation

This directory contains comprehensive task specifications ready for implementation by AI agents (Claude Cloud, Claude Code, Gemini 3 Pro, etc.).

## Task Overview

### 1. UI_REFACTOR_3_PANEL_LAYOUT.md
**Priority**: High
**Estimated Effort**: 3-4 hours
**Assigned To**: Claude Cloud (in separate branch)
**Status**: 🟡 In Progress

Convert the 4-panel layout to 3-panel layout:
- Remove Studio panel (280px)
- Expand Foreman panel to 400px
- Move Studio tools to dropdown menu
- Add message action buttons (Copy, Insert, Regenerate)
- Enhance chat input (@mentions, attachments, voice)
- Fix branding "Antigravity" → "Writers Factory"
- **Preserve Live Graph in Foreman panel**

**Files to Modify**:
- `frontend/src/lib/components/MainLayout.svelte`
- `frontend/src/routes/+page.svelte`
- `frontend/src/lib/components/ForemanPanel.svelte`

**Before/After**:
```
BEFORE: [BINDER 240px] [CANVAS flex] [FOREMAN 320px] [STUDIO 280px]
AFTER:  [BINDER 240px] [CANVAS flex] [FOREMAN 400px]
```

---

### 2. SIMPLIFY_FILETREE_BINDER.md
**Priority**: High
**Estimated Effort**: 1-2 hours
**Assigned To**: Unassigned
**Status**: ⚪ Pending

Remove automatic categorization and make FileTree work like VS Code:
- Remove "Story Bible", "Manuscript", "World Database" sections
- Build proper hierarchical tree structure
- Implement folder expand/collapse
- Simple click-to-open file behavior

**Files to Modify**:
- `frontend/src/lib/components/FileTree.svelte`

**Problem**: Current FileTree has confusing "smart" categorization with `organizeFiles()` function that tries to guess where files belong. Writers need to see their actual folder structure.

---

### 3. IMPLEMENT_MONACO_EDITOR.md
**Priority**: High
**Estimated Effort**: 2-3 hours
**Assigned To**: Unassigned
**Status**: ⚪ Pending

Replace plain `<textarea>` with Monaco editor configured for prose writing:
- Markdown syntax highlighting
- Serif font (Georgia, not monospace)
- Word wrap, line numbers, smooth scrolling
- Preview toggle button
- Disable code-centric features (autocomplete, minimap, folding)

**Files to Create**:
- `frontend/src/lib/components/MonacoEditor.svelte` (NEW)

**Files to Modify**:
- `frontend/src/lib/components/Editor.svelte`
- `frontend/vite.config.js` (add Monaco workers)

**Note**: `monaco-editor` is already installed in package.json (v0.54.0)

---

## Technical Context

### System Status
- **Backend**: Running on port 8000 with 11 LLM providers
- **Frontend**: Tauri app on localhost:1420
- **Branch**: `main` (Claude Cloud working in separate branch `elegant-mendeleev`)
- **Framework**: Svelte 5 + SvelteKit + Tauri 2
- **Theme**: Cyber-Noir (dark with gold/cyan/purple accents)

### Dependencies Already Installed
- `monaco-editor`: v0.54.0 ✅
- `@monaco-editor/react`: v4.7.0 (not needed for direct integration)
- `marked`: Not installed (optional for markdown preview)

### Key Files
- [MainLayout.svelte](../frontend/src/lib/components/MainLayout.svelte) - 4-panel grid layout
- [FileTree.svelte](../frontend/src/lib/components/FileTree.svelte) - File browser with categorization
- [Editor.svelte](../frontend/src/lib/components/Editor.svelte) - Plain textarea writing area
- [ForemanPanel.svelte](../frontend/src/lib/components/ForemanPanel.svelte) - AI chat + Live Graph
- [StudioPanel.svelte](../frontend/src/lib/components/StudioPanel.svelte) - Tool card grid

---

## Coordination Notes

### Task Dependencies
- **Task 1 (UI Refactor)** is independent - can be done in parallel
- **Task 2 (FileTree)** is independent - can be done in parallel
- **Task 3 (Monaco)** is independent - can be done in parallel

**All three tasks can be worked on simultaneously by different agents!**

### After Completion
When Claude Cloud finishes Task 1 in their branch:
1. They should check main branch for any updates
2. Merge their changes back to main
3. Tasks 2 and 3 can be implemented in main or any branch

### User's Preference
User said: "let's create task docs not sure who will do it either Claude code or You Claude ID E or even Gemini three pro who sits around doing nothing all day :-)"

Translation: Any available AI agent can pick up Tasks 2 and 3.

---

## Testing Strategy

Each task document includes a detailed testing checklist. After implementation:

1. **UI Refactor**: Verify 3-panel layout, Studio dropdown works, Foreman expanded, Live Graph preserved
2. **FileTree**: Verify hierarchical tree, folder expand/collapse, no categorization
3. **Monaco**: Verify markdown highlighting, serif font, preview toggle, word wrap

---

## Questions?

If any agent needs clarification on a task:
1. Read the full task specification (they're comprehensive)
2. Check the current implementation by reading the relevant files
3. Reference similar patterns in other components
4. Test current behavior in the running app

The goal: **Professional writing experience** matching the quality of Scrivener, iA Writer, and modern IDEs like Cursor AI.
