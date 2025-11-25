# Writers Factory UX Roadmap

## Current State (v0.1)
Three stacked panels in a 320px right sidebar:
- Agent Panel (top)
- NotebookLM / Metabolism tabs (middle)
- Chat Manager (bottom)

**Problems:**
- Cramped vertical space
- No room for additional features
- Context switching requires scrolling
- No keyboard-first workflow

---

## Proposed Architecture

### 1. Command Palette (Priority: High)
**Trigger:** `Cmd+K` (Mac) / `Ctrl+K` (Windows)

A spotlight-style search bar for quick actions:
```
> digest          → Run consolidation now
> ingest          → Re-scan content folder
> new session     → Start fresh chat session
> graph stats     → Show node/edge counts
> conflicts       → List unresolved conflicts
> notebook:craft  → Query craft notebook
> notebook:world  → Query world bible notebook
```

**Benefits:**
- Reduces UI clutter (actions don't need buttons)
- Keyboard-first workflow for power users
- Extensible (agents can register commands)

### 2. Panel System Redesign

#### Option A: Floating Panels
- Panels detach from sidebar
- Can be positioned anywhere
- Persist position in localStorage
- Double-click title bar to dock/undock

#### Option B: Drawer System
- Left drawer: File tree (existing)
- Right drawer: Context panel (collapses to icons)
- Bottom drawer: Chat/Terminal (like VS Code)
- Each drawer independently collapsible

#### Option C: Tab-based Workspace (Recommended)
Keep the main editor central, but use a tab bar for auxiliary views:
```
[Editor] [Graph Explorer] [Chat] [Metabolism]
```
- Only one auxiliary view visible at a time
- Editor always visible in split view
- Quick switch with `Cmd+1`, `Cmd+2`, etc.

### 3. Status Bar (Priority: High)
A thin bar at the bottom of the window:
```
┌────────────────────────────────────────────────────────────┐
│ 📊 60 nodes · 314 edges │ ⏳ 4 uncommitted │ ✓ Ollama ready │
└────────────────────────────────────────────────────────────┘
```
- Click sections to open relevant panel
- Always visible, minimal footprint
- Color-coded warnings (red if conflicts exist)

### 4. Keyboard Shortcuts

#### Global
| Shortcut | Action |
|----------|--------|
| `Cmd+K` | Open command palette |
| `Cmd+S` | Save current file |
| `Cmd+Shift+S` | Save all |
| `Cmd+\` | Toggle right sidebar |
| `Cmd+B` | Toggle left sidebar (file tree) |
| `Cmd+J` | Toggle bottom panel (chat) |
| `Escape` | Close any modal/palette |

#### Editor
| Shortcut | Action |
|----------|--------|
| `Cmd+Shift+A` | Ask agents about selection |
| `Cmd+Shift+G` | Look up selection in graph |
| `Cmd+Shift+N` | Query NotebookLM about selection |

#### Navigation
| Shortcut | Action |
|----------|--------|
| `Cmd+1` | Focus editor |
| `Cmd+2` | Focus chat |
| `Cmd+3` | Focus graph/metabolism |
| `Cmd+P` | Quick open file |

### 5. Context Menus
Right-click on selected text in editor:
- "Ask Agents..."
- "Look up in Knowledge Graph"
- "Query NotebookLM"
- "Add to World Bible"

Right-click on file in tree:
- "Open"
- "Ingest to Graph"
- "Link to Current Session"

### 6. Modal Dialogs (for infrequent workflows)
- **Conflict Resolution:** Full-screen modal showing side-by-side diffs
- **Graph Explorer:** Modal with interactive node visualization
- **Settings:** Modal with tabs for different config areas

---

## Implementation Phases

### Phase A: Foundation
1. Add status bar component
2. Implement command palette (basic)
3. Add global keyboard shortcut listener

### Phase B: Layout Flexibility
1. Make sidebar collapsible
2. Add bottom drawer for chat
3. Implement tab switching

### Phase C: Power Features
1. Context menus
2. Command palette extensions
3. Graph visualization modal

---

## Technical Notes

### Command Palette Implementation
```typescript
interface Command {
  id: string;
  label: string;
  shortcut?: string;
  action: () => void | Promise<void>;
  category?: string;
}

// Registry pattern
const commandRegistry = new Map<string, Command>();

// Components register their commands
commandRegistry.set('metabolism.digest', {
  id: 'metabolism.digest',
  label: 'Digest uncommitted events',
  shortcut: 'Cmd+Shift+D',
  action: () => digestNow(),
  category: 'Metabolism'
});
```

### Keyboard Handling
Use a central keyboard service that:
- Captures events at document level
- Checks for registered shortcuts
- Prevents default when matched
- Handles modifier keys cross-platform

### State Persistence
- Panel positions → localStorage
- Last active tab → localStorage
- Collapsed state → localStorage
- Use Svelte stores for reactivity

---

## Open Questions
- [ ] Should chat be dockable to bottom OR right? (VS Code style)
- [ ] Do we need multiple chat sessions visible simultaneously?
- [ ] Should graph explorer be inline or always modal?
- [ ] How do we handle mobile/tablet layouts?

---

## References
- VS Code panel system
- Obsidian command palette
- Linear's keyboard-first design
- Notion's slash commands
