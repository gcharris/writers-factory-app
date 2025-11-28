# Task: Assistant Panel Redesign (Muse/Scribe)

**Status**: ✅ COMPLETE
**Priority**: High
**Estimated Effort**: ~24 hours
**Created**: 2025-11-27
**Completed**: 2025-11-28
**Supersedes**: `IMPLEMENT_FOREMAN_WORK_ORDERS_UI.md`

---

## Completion Summary

**All 4 phases implemented:**

| Phase | Description | Status | Commit |
|-------|-------------|--------|--------|
| Phase 1 | Core Chat Liberation | ✅ Complete | `0b8b542` |
| Phase 2 | Enhanced Input Bar | ✅ Complete | `0b8b542` |
| Phase 3 | Stage Auto-Detection | ✅ Complete | `08b5808` |
| Phase 4 | Status Bar | ✅ Complete | `0b8b542` |

**Components created:**
- `chat/AgentDropdown.svelte`
- `chat/StageDropdown.svelte`
- `chat/MentionPicker.svelte`
- `chat/AttachButton.svelte`
- `chat/ContextBadge.svelte`
- `chat/StatusBar.svelte`
- `chat/InputBar.svelte`
- `chat/ChatMessage.svelte`

**Backend endpoints added:**
- `GET /foreman/stage` - Auto-detect writing stage
- `POST /foreman/stage` - Manual stage override
- `DELETE /foreman/stage` - Reset to auto-detection
- `GET /mentions/search` - Search Knowledge Graph for @mentions
- `POST /foreman/chat` - Updated to accept context array

---

## Executive Summary

Redesign the right panel chat interface to be IDE-style (like VS Code Copilot or Cursor AI) rather than a gated workflow. The assistant should be immediately accessible without requiring project initialization, with smart context awareness and configurable naming.

---

## Core Philosophy Changes

| Current Approach | New Approach |
|------------------|--------------|
| "Start New Project" gate blocks chat | Chat immediately available |
| "Foreman" branding (factory hierarchy) | "Muse" or "Scribe" (creative partnership) |
| Modes exposed to user (ARCHITECT, VOICE, etc.) | Stages shown as progress indicator |
| Work orders as primary feature | Work orders as background status |
| Mandatory project context | Optional, toggleable context |

---

## Naming Convention

### User-Facing
- **Default name**: "Muse" (configurable in Settings)
- **Preset options**: Muse, Scribe, Quill, Ghost, Companion
- **Custom option**: User can enter any name (e.g., "Little Jackie")
- **Display**: Name appears in panel header and responses

### Internal (Code/Backend)
- **Keep existing**: `foreman.py`, `ForemanPanel.svelte`, `/foreman/*` endpoints
- **No backend renaming** - too much refactoring for minimal benefit
- **UI layer translates**: `$assistantName` store used for display

### Implementation
```javascript
// stores.js
export const assistantName = writable('Muse');

// In components, always use:
<h2>{$assistantName}</h2>  // Shows "Muse" or user's custom name
```

---

## Panel Layout

### Header
```
┌─────────────────────────────────────────────────────────┐
│ [Muse]                    [Studio] [Graph] [Sessions] [⚙]│
└─────────────────────────────────────────────────────────┘
```

- **Assistant name** (left): Configurable, shows current name
- **Header buttons** (right): Studio Tools, Knowledge Graph, Sessions, Settings

### Chat Area
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  User: Help me develop my protagonist's arc             │
│                                                         │
│  Muse: I'd love to help! Based on your Story Bible...   │
│                                                         │
│  [Messages scroll here]                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

- Standard chat interface
- No "Start New Project" form blocking access
- Messages styled per role (user, assistant, system)

### Input Bar (VS Code/Cursor Style)
```
┌─────────────────────────────────────────────────────────┐
│ [Agent ▼] [Stage ▼]                                     │
├─────────────────────────────────────────────────────────┤
│ [@] [📎] [📄 Chapter3.md ✕]  [ Type message...   ] [⏎] │
└─────────────────────────────────────────────────────────┘
```

#### Components:

| Element | Description |
|---------|-------------|
| **Agent Dropdown** | Select from Squad-configured agents |
| **Stage Dropdown** | Shows current writing stage (checkmarks) |
| **@ Button** | Opens mention picker for project files/characters |
| **📎 Button** | Attach external file (from Downloads, etc.) |
| **Context Badge** | Shows attached file, click ✕ to remove |
| **Input Field** | Message text |
| **Send Button** | Submit message |

---

## Component Specifications

### 1. Agent Dropdown

**Purpose**: Select which AI agent to route the message to

**Data Source**: Squad-configured agents from Settings

**UI**:
```
┌──────────────────────────┐
│ ▼ Muse (Default)         │
├──────────────────────────┤
│ ● Muse                   │  ← Currently selected
│ ○ Scene Writer           │
│ ○ Voice Analyst          │
│ ○ Story Architect        │
├──────────────────────────┤
│ ⚙ Configure agents...    │  ← Opens Settings > Squads
└──────────────────────────┘
```

**Behavior**:
- Shows only agents configured in user's Squad
- Footer link: "Configure agents..." opens Settings modal
- Selection persists for session (not permanently)
- Default resets to primary assistant on new session

**Props**:
```typescript
export let selectedAgent: string = 'default';
export let availableAgents: Array<{id: string, name: string, description: string}>;
```

---

### 2. Stage Dropdown

**Purpose**: Show and optionally change current writing stage

**Stages** (from Narrative Protocol):
1. **Conception** - Story Bible, world-building, structure
2. **Voice** - Calibration, tournaments, voice reference
3. **Execution** - Drafting scenes, writing
4. **Polish** - Editing, refinement, continuity

**UI**:
```
┌──────────────────────────┐
│ ▼ Voice (Current)        │
├──────────────────────────┤
│ ✓ Conception             │  ← Completed
│ ● Voice                  │  ← Current stage
│ ○ Execution              │  ← Not started
│ ○ Polish                 │  ← Not started
├──────────────────────────┤
│ Current stage auto-      │
│ detected. Click to       │
│ change focus.            │
└──────────────────────────┘
```

**Behavior**:
- **Checkmarks** (✓) for completed stages
- **Filled circle** (●) for current stage
- **Empty circle** (○) for future stages
- **Auto-detection**: System determines stage from Story Bible completion, existing drafts, etc.
- **Manual override**: Clicking a stage changes assistant focus
- **Confirmation**: "Switch focus to [Stage]?" (optional, can be disabled)
- **Non-destructive**: Changing stage doesn't delete work, just shifts conversation focus

**Backend Integration**:
```javascript
// GET /foreman/stage
// Returns: { current: "voice", completed: ["conception"], progress: { conception: 100, voice: 45, execution: 0, polish: 0 } }
```

---

### 3. Mention System (@)

**Purpose**: Reference project files, characters, locations inline

**Trigger**: Type `@` or click @ button

**UI**:
```
┌──────────────────────────┐
│ @ Search files...        │
├──────────────────────────┤
│ CHARACTERS               │
│   @Maya                  │
│   @Dr. Chen              │
│   @The Stranger          │
├──────────────────────────┤
│ FILES                    │
│   @Protagonist.md        │
│   @Beat_Sheet.md         │
│   @Chapter3.md           │
├──────────────────────────┤
│ LOCATIONS                │
│   @The Lab               │
│   @Downtown              │
└──────────────────────────┘
```

**Data Sources**:
- **Characters**: From Knowledge Graph (node_type: CHARACTER)
- **Files**: From content directory (Story Bible, chapters)
- **Locations**: From Knowledge Graph (node_type: LOCATION)
- **Themes**: From Knowledge Graph (node_type: THEME)

**Behavior**:
- Fuzzy search as user types
- Categories collapse/expand
- Selected mention inserted as `@[Name]` in input
- Backend resolves mention to actual content when sending

---

### 4. Attach Button (📎)

**Purpose**: Upload external files not in the project

**Use Cases**:
- Reference article from Downloads folder
- Image for visual reference
- PDF research document
- Any file outside the content directory

**UI**: Standard file picker dialog

**Behavior**:
- Opens system file picker
- Selected file shown as badge in input bar
- File content sent with message (or uploaded to temp storage)
- Click ✕ on badge to remove

**Difference from @Mention**:
| @Mention | 📎 Attach |
|----------|-----------|
| References files *in* the project | Uploads files *outside* the project |
| Uses Knowledge Graph | Raw file upload |
| Lightweight (just reference) | Heavier (actual content) |

---

### 5. Context Badge

**Purpose**: Show what context is attached to the message

**UI**:
```
┌──────────────────────────────────────────┐
│ [📄 Chapter3.md ✕] [📄 research.pdf ✕]   │
└──────────────────────────────────────────┘
```

**Types**:
- **Active file**: Auto-attached from editor (if enabled)
- **Mentioned files**: From @ mentions
- **Attached files**: From 📎 uploads

**Toggle**:
- Click ✕ to remove specific context
- Global toggle: "Include open file" checkbox (in input bar or settings)

---

### 6. Status Bar (Work Orders - Deferred)

**Purpose**: Show background task progress

**UI** (when active):
```
┌─────────────────────────────────────────────────────────┐
│ ⏳ Generating voice variants... 3/5                     │
└─────────────────────────────────────────────────────────┘
```

**UI** (collapsed/idle):
```
┌─────────────────────────────────────────────────────────┐
│ [3 tasks completed today] [View history →]              │
└─────────────────────────────────────────────────────────┘
```

**Note**: This is Phase 4. Implement after core chat UX is complete.

---

## Implementation Phases

### Phase 1: Core Chat Liberation (~8 hours) ✅ COMPLETE

**Goal**: Remove gating, make chat immediately usable

**Tasks**:
1. ✅ Remove `showStartProject` logic from ForemanPanel
2. ✅ Remove project initialization requirement
3. ✅ Chat sends to `/foreman/chat` without prior `/foreman/start`
4. ✅ Backend handles "no project" gracefully (general assistant mode)
5. ✅ Add `assistantName` store with default "Muse"
6. ✅ Update header to show `$assistantName`
7. ✅ Add name to Settings panel (Preset dropdown + custom input)

**Files Modified**:
- `frontend/src/lib/components/ForemanPanel.svelte`
- `frontend/src/lib/stores.js`
- `frontend/src/lib/components/SettingsPanel.svelte`
- `backend/agents/foreman.py`
- `backend/api.py`

**Acceptance Criteria**:
- [x] App loads → Chat is immediately available
- [x] User can send message without "Start Project"
- [x] Header shows "Muse" (or configured name)
- [x] Settings allows changing assistant name

---

### Phase 2: Enhanced Input Bar (~8 hours) ✅ COMPLETE

**Goal**: VS Code/Cursor-style input with dropdowns

**Tasks**:
1. ✅ Create `AgentDropdown.svelte` component
2. ✅ Create `StageDropdown.svelte` component
3. ✅ Create `MentionPicker.svelte` component
4. ✅ Create `AttachButton.svelte` component
5. ✅ Create `ContextBadge.svelte` component
6. ✅ Integrate all into `ForemanPanel.svelte` input area
7. ✅ Add context toggle (include/exclude open file)

**Files Created**:
- `frontend/src/lib/components/chat/AgentDropdown.svelte`
- `frontend/src/lib/components/chat/StageDropdown.svelte`
- `frontend/src/lib/components/chat/MentionPicker.svelte`
- `frontend/src/lib/components/chat/AttachButton.svelte`
- `frontend/src/lib/components/chat/ContextBadge.svelte`
- `frontend/src/lib/components/chat/InputBar.svelte`
- `frontend/src/lib/components/chat/ChatMessage.svelte`

**Backend Additions** (see Phase 3):
- `GET /foreman/stage` - Returns current stage and progress
- `GET /mentions/search?q={query}` - Search mentionable entities
- `POST /foreman/chat` - Accept `context` array in payload

**Acceptance Criteria**:
- [x] Agent dropdown shows Squad-configured agents
- [x] Stage dropdown shows 4 stages with checkmarks
- [x] @ button opens mention picker
- [x] 📎 button opens file picker
- [x] Context badges show attached items
- [x] ✕ removes context items

---

### Phase 3: Stage Auto-Detection (~4 hours) ✅ COMPLETE

**Goal**: Automatically determine and display current writing stage

**Tasks**:
1. ✅ Create stage detection logic in backend
2. ✅ Check Story Bible completion → Conception done
3. ✅ Check voice reference existence → Voice done
4. ✅ Check draft files → Execution in progress
5. ✅ Surface stage in `/foreman/stage` endpoint
6. ✅ Stage dropdown auto-selects based on detection

**Implementation** (in `backend/api.py`):
- `GET /foreman/stage` - Auto-detect based on StoryBibleService and file checks
- `POST /foreman/stage` - Manual stage override (stored in memory)
- `DELETE /foreman/stage` - Reset to auto-detection
- `GET /mentions/search` - Search Knowledge Graph + content files
- `POST /foreman/chat` - Updated to accept `context` array

**Acceptance Criteria**:
- [x] Stage auto-detected on load
- [x] Stage updates as work progresses
- [x] Manual override still works

---

### Phase 4: Status Bar & Work Orders (~4 hours) ✅ COMPLETE

**Goal**: Background task visibility

**Tasks**:
1. ✅ Create `StatusBar.svelte` component
2. ✅ Show active work order progress
3. ✅ Show completed work count
4. "View history" link opens work order history modal (deferred - not MVP)
5. Work order history modal (deferred - not MVP)

**Files Created**:
- `frontend/src/lib/components/chat/StatusBar.svelte`

**Acceptance Criteria**:
- [x] Status bar shows when task running
- [x] Progress indicator (e.g., "3/5")
- [x] Completed count shown when idle
- [ ] History modal accessible (deferred)

---

## UI/UX Specifications

### Cyber-Noir Theme Compliance

**Colors**:
```css
--bg-primary: #0f1419;
--bg-secondary: #1a2027;
--bg-tertiary: #252d38;
--text-primary: #e6edf3;
--text-muted: #8b949e;
--accent-cyan: #58a6ff;
--accent-gold: #d4a574;
--accent-purple: #a371f7;
--border: #2d3a47;
```

**Stage Colors**:
- Conception: Gold (#d4a574)
- Voice: Purple (#a371f7)
- Execution: Cyan (#58a6ff)
- Polish: Green (#3fb950)

### Dropdown Styling

```css
.dropdown {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  min-width: 180px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.dropdown-item {
  padding: 8px 12px;
  cursor: pointer;
}

.dropdown-item:hover {
  background: var(--bg-tertiary);
}

.dropdown-item.selected {
  color: var(--accent-cyan);
}
```

### Input Bar Layout

```css
.input-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--border);
  background: var(--bg-secondary);
}

.input-controls {
  display: flex;
  gap: 8px;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-field {
  flex: 1;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  color: var(--text-primary);
}
```

---

## Backend API Changes

### New Endpoints

#### GET /foreman/stage
```json
{
  "current": "voice",
  "completed": ["conception"],
  "progress": {
    "conception": 100,
    "voice": 45,
    "execution": 0,
    "polish": 0
  },
  "can_change": true
}
```

#### POST /foreman/stage
```json
// Request
{ "stage": "conception" }

// Response
{ "success": true, "message": "Focus changed to Conception stage" }
```

#### GET /mentions/search
```json
// Request: GET /mentions/search?q=may&limit=10

// Response
{
  "results": [
    { "type": "character", "name": "Maya", "id": "char_maya", "file": "Characters/Maya.md" },
    { "type": "file", "name": "Chapter 3 - May Day", "id": "file_ch3", "path": "Chapters/Chapter3.md" }
  ]
}
```

#### Modified: POST /foreman/chat
```json
// Request (updated)
{
  "message": "Help me with @Maya's arc",
  "context": [
    { "type": "file", "path": "Chapters/Chapter3.md" },
    { "type": "mention", "id": "char_maya" },
    { "type": "attachment", "content": "...", "filename": "research.pdf" }
  ],
  "agent": "default",  // or specific agent ID
  "include_open_file": true
}
```

---

## Settings Integration

### New Settings Section: "Assistant"

```
┌─────────────────────────────────────────────────────────┐
│ ASSISTANT                                               │
├─────────────────────────────────────────────────────────┤
│ Name your writing assistant                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [Muse ▼]                                            │ │
│ └─────────────────────────────────────────────────────┘ │
│ Presets: Muse, Scribe, Quill, Ghost, Companion          │
│                                                         │
│ Or enter a custom name:                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Little Jackie                                       │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ [✓] Auto-include open file as context                   │
│ [✓] Show stage indicator                                │
│ [ ] Confirm before changing stage                       │
└─────────────────────────────────────────────────────────┘
```

**Settings Keys**:
- `assistant.name`: string (default: "Muse")
- `assistant.auto_include_file`: boolean (default: true)
- `assistant.show_stage`: boolean (default: true)
- `assistant.confirm_stage_change`: boolean (default: false)

---

## Migration Notes

### From Current ForemanPanel

**Remove**:
- `showStartProject` state and UI
- `projectTitle`, `protagonistName` input fields
- `startProject()` function requirement
- Blocking logic in `onMount`

**Keep**:
- Chat message handling
- Header buttons (Studio, Graph, Sessions, Settings)
- Message styling
- Keyboard shortcuts

**Add**:
- Agent dropdown
- Stage dropdown
- Mention system
- Attach button
- Context badges
- Status bar (Phase 4)

---

## Testing Requirements

### Unit Tests
- [ ] AgentDropdown renders configured agents
- [ ] StageDropdown shows correct checkmarks
- [ ] MentionPicker searches and filters
- [ ] ContextBadge displays and removes items

### Integration Tests
- [ ] Chat works without project initialization
- [ ] Stage auto-detection reflects actual state
- [ ] Mentions resolve to correct content
- [ ] Attachments upload successfully

### E2E Tests
- [ ] New user can chat immediately on first launch
- [ ] Changing assistant name persists
- [ ] Full flow: select agent → add context → send → receive response

---

## Success Metrics

After implementation, writers should be able to:

1. **Start chatting immediately** - No project setup required
2. **See their personalized assistant name** - "Muse", "Scribe", or custom
3. **Know where they are** - Stage indicator shows progress
4. **Reference project content easily** - @ mentions work smoothly
5. **Bring in external research** - Attach files from anywhere
6. **Control context** - Toggle what's included with each message
7. **Choose specialized help** - Select from configured agents

---

## File Summary

### Files to Modify
- `frontend/src/lib/components/ForemanPanel.svelte` - Major refactor
- `frontend/src/lib/stores.js` - Add assistantName, stage stores
- `frontend/src/lib/components/SettingsPanel.svelte` - Add Assistant section
- `backend/agents/foreman.py` - Handle no-project state
- `backend/api.py` - New endpoints, modified chat endpoint

### Files to Create
- `frontend/src/lib/components/chat/AgentDropdown.svelte`
- `frontend/src/lib/components/chat/StageDropdown.svelte`
- `frontend/src/lib/components/chat/MentionPicker.svelte`
- `frontend/src/lib/components/chat/AttachButton.svelte`
- `frontend/src/lib/components/chat/ContextBadge.svelte`
- `frontend/src/lib/components/chat/StatusBar.svelte` (Phase 4)
- `frontend/src/lib/components/WorkOrderHistory.svelte` (Phase 4)

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Default assistant name? | "Muse" |
| Backend renaming? | No - keep "foreman" internally |
| Agent dropdown source? | Squad-configured agents only |
| Stage indicator behavior? | Checkmarks, auto-detect, click to change |
| Attach vs Mention? | Attach = external files, Mention = project content |
| Work orders priority? | Phase 4 - after core UX |

---

**Document Author**: Claude (Opus)
**Last Updated**: 2025-11-27
**Status**: Ready for review and implementation
