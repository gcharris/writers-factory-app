# Task: Implement Foreman Work Orders UI

**Status**: ⚪ Not Started
**Priority**: Medium
**Estimated Effort**: ~18 hours
**Assigned To**: TBD
**Created**: 2025-11-27

---

## Overview

Implement a comprehensive Work Orders UI system to visualize and manage the Foreman's active and completed work orders. This provides writers with transparency into what the Foreman is working on, progress tracking, and historical context for completed work.

---

## Background

The Foreman backend already tracks work orders internally during ARCHITECT, VOICE_CALIBRATION, and DIRECTOR modes. Each mode has specific work order types:

- **ARCHITECT Mode**: 15-beat Story Bible completion tracking
- **VOICE_CALIBRATION Mode**: Tournament variant generation, voice reference bundle creation
- **DIRECTOR Mode**: Scaffold generation, scene structure variants, scene writing variants, enhancement passes

Currently, this information exists in the backend but has no frontend visualization. Writers need to see:
- What work orders are in progress
- What's been completed
- Progress on multi-step work orders
- Historical context for completed work

---

## Components to Create

### 1. WorkOrderList.svelte (~350 lines)
**Location**: `frontend/src/lib/components/WorkOrderList.svelte`

**Purpose**: Main container showing active and recently completed work orders

**Features**:
- Tab view: "Active" (in_progress), "Completed" (completed), "All"
- Sort options: Recent first, Oldest first, By mode
- Filter by mode: ARCHITECT, VOICE_CALIBRATION, DIRECTOR, ALL
- Empty states for each tab
- Auto-refresh when new work orders arrive
- Click work order → expand to show WorkOrderCard

**Props**:
```typescript
export let sessionId: string;  // Current Foreman session
export let mode: 'active' | 'completed' | 'all' = 'active';
```

**API Integration**:
```javascript
// GET /foreman/work-orders?session_id={sessionId}&status={status}
async function fetchWorkOrders(status = null) {
  const params = new URLSearchParams({ session_id: sessionId });
  if (status) params.append('status', status);

  const response = await fetch(`http://localhost:8000/foreman/work-orders?${params}`);
  return response.json();
}
```

**Layout**:
```
┌─────────────────────────────────────┐
│ WORK ORDERS                         │
│ [Active] [Completed] [All]          │
│ Sort: [Recent ▼]  Filter: [All ▼]   │
├─────────────────────────────────────┤
│ ▶ Beat 1: Opening Image             │
│   Status: In Progress • 45% done    │
│   Started: 2h ago                   │
├─────────────────────────────────────┤
│ ✓ Voice Calibration Tournament      │
│   Status: Completed • 3h ago        │
│   5 variants generated              │
└─────────────────────────────────────┘
```

**Styling**: Cyber-noir theme with cyan accent for active work orders

---

### 2. WorkOrderCard.svelte (~280 lines)
**Location**: `frontend/src/lib/components/WorkOrderCard.svelte`

**Purpose**: Display detailed information for a single work order

**Features**:
- Expandable/collapsible card
- Mode badge (ARCHITECT, VOICE_CALIBRATION, DIRECTOR)
- Status indicator (pending, in_progress, completed, failed)
- Progress bar for multi-step work orders
- Timestamp (relative time: "2h ago")
- Task breakdown list (sub-tasks if available)
- Result summary (for completed work orders)
- Error message (for failed work orders)
- Click → navigate to related content (e.g., beat in Story Bible, variant in Studio)

**Props**:
```typescript
export let workOrder: {
  id: string;
  session_id: string;
  mode: 'ARCHITECT' | 'VOICE_CALIBRATION' | 'DIRECTOR';
  title: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;  // 0-100
  created_at: string;  // ISO timestamp
  completed_at: string | null;
  tasks: Array<{
    name: string;
    status: string;
    result?: any;
  }>;
  metadata?: any;
  error?: string;
};
export let expanded: boolean = false;
```

**Layout (Expanded)**:
```
┌─────────────────────────────────────────────────┐
│ ▼ Beat 1: Opening Image          [ARCHITECT]   │
│   Status: In Progress • 45% done               │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45%    │
│   Started: 2h ago                              │
│                                                │
│   Tasks:                                       │
│   ✓ Extract world details from NotebookLM     │
│   ✓ Generate protagonist introduction         │
│   ⏳ Create opening scene setup                │
│   ⚪ Establish narrative voice                 │
│                                                │
│   → View in Story Bible                        │
└─────────────────────────────────────────────────┘
```

**Styling**:
- Mode badges: ARCHITECT (gold), VOICE_CALIBRATION (purple), DIRECTOR (cyan)
- Status colors: pending (gray), in_progress (cyan), completed (green), failed (red)
- Progress bar with animated gradient

---

### 3. WorkOrderProgress.svelte (~190 lines)
**Location**: `frontend/src/lib/components/WorkOrderProgress.svelte`

**Purpose**: Visual progress tracker for multi-step work orders

**Features**:
- Step-by-step progress visualization
- Current step highlighted
- Completed steps with checkmarks
- Pending steps grayed out
- Estimated time remaining (if available)
- Substep breakdown for current step
- Real-time updates via WebSocket (future enhancement)

**Props**:
```typescript
export let workOrder: WorkOrder;
export let compact: boolean = false;  // Compact view for WorkOrderCard
```

**Layout (Full View)**:
```
┌─────────────────────────────────────────────────┐
│ Voice Calibration Tournament                   │
│                                                │
│ ✓ Step 1: Generate 5 strategy variants         │
│   • Hemingway Sparse (287 words)               │
│   • Metaphor-Dense (412 words)                 │
│   • Dialogue-Heavy (356 words)                 │
│   • Action-Oriented (298 words)                │
│   • Lyrical Prose (445 words)                  │
│                                                │
│ ⏳ Step 2: Analyze voice consistency            │
│   • Scoring variant 3 of 5...                  │
│                                                │
│ ⚪ Step 3: Generate voice reference bundle      │
│                                                │
│ Progress: 60% • ~5 min remaining               │
└─────────────────────────────────────────────────┘
```

**Compact View** (for WorkOrderCard):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60%
Step 2 of 3: Analyzing variants...
```

---

### 4. WorkOrderHistory.svelte (~180 lines)
**Location**: `frontend/src/lib/components/WorkOrderHistory.svelte`

**Purpose**: Show completed work orders for the entire project (all sessions)

**Features**:
- Timeline view of all completed work orders
- Group by date: Today, Yesterday, Last 7 days, Last 30 days, Older
- Search by title or mode
- Filter by mode or date range
- Export to JSON/Markdown
- Click work order → view details in modal
- Statistics: Total completed, success rate, average completion time

**Props**:
```typescript
export let projectId: string;  // Optional - defaults to current project
export let limit: number = 50;  // Max work orders to show
```

**API Integration**:
```javascript
// GET /foreman/work-orders/history?project_id={projectId}&limit={limit}
async function fetchHistory() {
  const params = new URLSearchParams({ limit: String(limit) });
  if (projectId) params.append('project_id', projectId);

  const response = await fetch(`http://localhost:8000/foreman/work-orders/history?${params}`);
  return response.json();
}
```

**Layout**:
```
┌─────────────────────────────────────────────────┐
│ WORK ORDER HISTORY                             │
│ Search: [____________]  Export: [JSON ▼]       │
│                                                │
│ Today (3 work orders)                          │
│ ├─ 14:32 • Beat 5: Midpoint ✓                  │
│ ├─ 12:15 • Scene Enhancement (6-Pass) ✓        │
│ └─ 09:41 • Scaffold Generation ✓               │
│                                                │
│ Yesterday (5 work orders)                      │
│ ├─ 18:20 • Voice Calibration Tournament ✓      │
│ ├─ 16:45 • Beat 4: Catalyst ✓                  │
│ └─ ... (show more)                             │
│                                                │
│ Stats: 127 total • 98% success • Avg 8.5 min   │
└─────────────────────────────────────────────────┘
```

---

## Backend API Endpoints

### Required Endpoints (To Be Implemented)

#### 1. GET /foreman/work-orders
**Purpose**: List active/completed work orders for current session

**Query Parameters**:
- `session_id` (required): Foreman session ID
- `status` (optional): "pending", "in_progress", "completed", "failed", "all"
- `mode` (optional): "ARCHITECT", "VOICE_CALIBRATION", "DIRECTOR"

**Response**:
```json
{
  "work_orders": [
    {
      "id": "wo_1732682745_beat_1",
      "session_id": "session_1732682400",
      "mode": "ARCHITECT",
      "title": "Beat 1: Opening Image",
      "status": "in_progress",
      "progress": 45,
      "created_at": "2025-11-27T10:32:25Z",
      "completed_at": null,
      "tasks": [
        {
          "name": "Extract world details from NotebookLM",
          "status": "completed",
          "result": {
            "sources": 3,
            "characters": ["Maya", "Dr. Chen"]
          }
        },
        {
          "name": "Generate protagonist introduction",
          "status": "completed"
        },
        {
          "name": "Create opening scene setup",
          "status": "in_progress"
        },
        {
          "name": "Establish narrative voice",
          "status": "pending"
        }
      ],
      "metadata": {
        "beat_number": 1,
        "target_word_count": 500
      }
    }
  ]
}
```

#### 2. GET /foreman/work-orders/{work_order_id}
**Purpose**: Get detailed information about a specific work order

**Response**: Single work order object (same structure as above)

#### 3. GET /foreman/work-orders/history
**Purpose**: Get completed work orders across all sessions

**Query Parameters**:
- `project_id` (optional): Filter by project
- `limit` (optional): Max work orders (default: 50)
- `offset` (optional): Pagination offset
- `mode` (optional): Filter by mode
- `start_date` (optional): ISO timestamp
- `end_date` (optional): ISO timestamp

**Response**:
```json
{
  "work_orders": [...],
  "total": 127,
  "offset": 0,
  "limit": 50,
  "stats": {
    "total_completed": 127,
    "total_failed": 3,
    "success_rate": 0.977,
    "average_completion_time_seconds": 510
  }
}
```

#### 4. POST /foreman/work-orders/{work_order_id}/cancel
**Purpose**: Cancel an in-progress work order

**Response**:
```json
{
  "work_order_id": "wo_1732682745_beat_1",
  "status": "cancelled"
}
```

---

## Integration Points

### 1. ForemanPanel.svelte
**Location**: `frontend/src/lib/components/ForemanPanel.svelte`

**Changes Needed**:
- Add "Work Orders" button to header (6th button)
- Open WorkOrderList modal on click
- Badge showing active work order count

**Code**:
```svelte
<script>
  import { activeWorkOrderCount } from '$lib/stores';

  function openWorkOrders() {
    activeModal.set('work-orders');
  }
</script>

<button class="header-btn" on:click={openWorkOrders} title="Work Orders">
  <span class="btn-label">Work Orders</span>
  {#if $activeWorkOrderCount > 0}
    <span class="badge">{$activeWorkOrderCount}</span>
  {/if}
</button>
```

### 2. +page.svelte
**Location**: `frontend/src/routes/+page.svelte`

**Changes Needed**:
- Import WorkOrderList modal
- Add modal handler

**Code**:
```svelte
<script>
  import WorkOrderList from '$lib/components/WorkOrderList.svelte';
</script>

{#if $activeModal === 'work-orders'}
  <WorkOrderList
    sessionId={$currentSessionId}
    on:close={() => activeModal.set(null)}
  />
{/if}
```

### 3. Stores
**Location**: `frontend/src/lib/stores.js`

**New Stores**:
```javascript
import { writable, derived } from 'svelte/store';

// Active work orders for current session
export const activeWorkOrders = writable([]);

// Derived: Count of in_progress work orders
export const activeWorkOrderCount = derived(
  activeWorkOrders,
  $orders => $orders.filter(wo => wo.status === 'in_progress').length
);

// Current session ID
export const currentSessionId = writable(null);
```

---

## Backend Implementation Notes

### Work Order State Management

The backend needs to track work orders in memory and/or database:

**Option 1: SQLite Table** (Recommended)
```sql
CREATE TABLE work_orders (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    tasks_json TEXT,  -- JSON array of tasks
    metadata_json TEXT,  -- JSON object
    error TEXT,
    FOREIGN KEY (session_id) REFERENCES foreman_sessions(id)
);

CREATE INDEX idx_work_orders_session ON work_orders(session_id);
CREATE INDEX idx_work_orders_status ON work_orders(status);
```

**Option 2: In-Memory + Foreman KB** (Simpler)
Store work orders in Foreman KB with category "work_order"

### Work Order Creation Pattern

When Foreman starts a new task:
```python
async def create_work_order(
    session_id: str,
    mode: str,
    title: str,
    tasks: List[Dict[str, Any]],
    metadata: Optional[Dict] = None
) -> str:
    """Create a new work order and return its ID"""
    work_order_id = f"wo_{int(time.time())}_{slugify(title)}"

    work_order = {
        "id": work_order_id,
        "session_id": session_id,
        "mode": mode,
        "title": title,
        "status": "pending",
        "progress": 0,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "tasks": tasks,
        "metadata": metadata or {}
    }

    # Save to DB or KB
    save_work_order(work_order)

    return work_order_id
```

### Work Order Update Pattern

When Foreman completes a task:
```python
async def update_work_order(
    work_order_id: str,
    task_index: int,
    status: str,
    result: Optional[Any] = None
):
    """Update a specific task in the work order"""
    work_order = get_work_order(work_order_id)
    work_order["tasks"][task_index]["status"] = status

    if result:
        work_order["tasks"][task_index]["result"] = result

    # Calculate overall progress
    completed_tasks = sum(1 for t in work_order["tasks"] if t["status"] == "completed")
    total_tasks = len(work_order["tasks"])
    work_order["progress"] = int((completed_tasks / total_tasks) * 100)

    # Update overall status
    if all(t["status"] == "completed" for t in work_order["tasks"]):
        work_order["status"] = "completed"
        work_order["completed_at"] = datetime.utcnow().isoformat()
    elif any(t["status"] == "in_progress" for t in work_order["tasks"]):
        work_order["status"] = "in_progress"

    save_work_order(work_order)
```

---

## Example Work Orders by Mode

### ARCHITECT Mode

**Work Order**: "Complete Story Bible Beat 1"
```json
{
  "title": "Beat 1: Opening Image",
  "mode": "ARCHITECT",
  "tasks": [
    {
      "name": "Query NotebookLM for world details",
      "status": "pending"
    },
    {
      "name": "Generate protagonist introduction",
      "status": "pending"
    },
    {
      "name": "Create opening scene setup",
      "status": "pending"
    },
    {
      "name": "Establish narrative voice",
      "status": "pending"
    }
  ],
  "metadata": {
    "beat_number": 1,
    "target_word_count": 500
  }
}
```

### VOICE_CALIBRATION Mode

**Work Order**: "Voice Calibration Tournament"
```json
{
  "title": "Voice Calibration Tournament",
  "mode": "VOICE_CALIBRATION",
  "tasks": [
    {
      "name": "Generate 5 strategy variants",
      "status": "pending"
    },
    {
      "name": "Analyze voice consistency",
      "status": "pending"
    },
    {
      "name": "Generate voice reference bundle",
      "status": "pending"
    }
  ],
  "metadata": {
    "scene_id": "scene_12",
    "strategies": ["hemingway_sparse", "metaphor_dense", "dialogue_heavy", "action_oriented", "lyrical_prose"]
  }
}
```

### DIRECTOR Mode

**Work Order**: "Generate Scene Scaffold"
```json
{
  "title": "Scene Scaffold: Chapter 3 Confrontation",
  "mode": "DIRECTOR",
  "tasks": [
    {
      "name": "Generate draft summary",
      "status": "pending"
    },
    {
      "name": "Enrich with NotebookLM context",
      "status": "pending"
    },
    {
      "name": "Generate structure variants",
      "status": "pending"
    }
  ],
  "metadata": {
    "scene_id": "scene_12",
    "target_word_count": 2000
  }
}
```

**Work Order**: "Scene Enhancement (6-Pass)"
```json
{
  "title": "Scene Enhancement: Chapter 3 Confrontation",
  "mode": "DIRECTOR",
  "tasks": [
    {
      "name": "Pass 1: Voice & POV",
      "status": "pending"
    },
    {
      "name": "Pass 2: Character Truth",
      "status": "pending"
    },
    {
      "name": "Pass 3: Symbolic Layer",
      "status": "pending"
    },
    {
      "name": "Pass 4: Pacing & Structure",
      "status": "pending"
    },
    {
      "name": "Pass 5: Anti-Pattern Removal",
      "status": "pending"
    },
    {
      "name": "Pass 6: Final Polish",
      "status": "pending"
    }
  ],
  "metadata": {
    "scene_id": "scene_12",
    "enhancement_mode": "six_pass",
    "initial_score": 72
  }
}
```

---

## UI/UX Requirements

### Cyber-Noir Theme Compliance

**Colors**:
- Background: `var(--bg-secondary, #1a2027)`
- Text: `var(--text-primary, #e6edf3)`
- Accent (Active): `var(--accent-cyan, #58a6ff)`
- Accent (ARCHITECT): `var(--accent-gold, #d4a574)`
- Accent (VOICE_CALIBRATION): `var(--accent-purple, #a371f7)`
- Border: `var(--border, #2d3a47)`
- Success: `var(--success, #56d364)`
- Error: `var(--error, #f85149)`

**Typography**:
- Font: `var(--font-sans)` (system sans-serif)
- Labels: `var(--text-xs, 11px)` uppercase with letter-spacing
- Body: `var(--text-sm, 12px)`

**Spacing**:
- Padding: `var(--space-3, 12px)`
- Gap: `var(--space-2, 8px)`
- Border radius: `var(--radius-md, 6px)`

### Accessibility

- All buttons must have `title` attributes for tooltips
- Keyboard navigation support (Tab, Enter, Escape)
- Screen reader friendly (proper ARIA labels)
- High contrast for status indicators
- Focus states on all interactive elements

### Responsive Behavior

- Modal max-width: 900px
- Scroll overflow for long lists
- Sticky headers for tables/lists
- Collapsible sections for compact view

---

## Testing Requirements

### Unit Tests
- [ ] WorkOrderCard renders all status types correctly
- [ ] WorkOrderProgress calculates percentages correctly
- [ ] WorkOrderList filters by mode and status
- [ ] WorkOrderHistory groups by date correctly

### Integration Tests
- [ ] Create work order via API → appears in WorkOrderList
- [ ] Update work order progress → UI updates in real-time
- [ ] Complete work order → moves to "Completed" tab
- [ ] Cancel work order → status changes to "cancelled"

### E2E Tests
- [ ] User clicks "Work Orders" button → modal opens
- [ ] User filters by mode → only matching work orders shown
- [ ] User clicks work order → expands to show details
- [ ] User clicks "View in Story Bible" → navigates to beat

---

## Acceptance Criteria

### Functional
- [x] Backend API endpoints implemented and documented
- [ ] All 4 components created and integrated
- [ ] Work orders display in real-time as Foreman works
- [ ] Users can view active, completed, and historical work orders
- [ ] Users can filter and search work orders
- [ ] Users can navigate from work order to related content
- [ ] Error handling for failed work orders

### Visual
- [ ] Matches Figma designs (if available) or cyber-noir theme
- [ ] Smooth animations for expand/collapse
- [ ] Progress bars animate smoothly
- [ ] Status badges clearly distinguishable
- [ ] Responsive layout works on all screen sizes

### Performance
- [ ] WorkOrderList loads in < 200ms for 50 work orders
- [ ] No UI lag when updating progress
- [ ] Efficient re-renders (use Svelte reactivity properly)
- [ ] Lazy loading for WorkOrderHistory (50 items at a time)

---

## Dependencies

### NPM Packages (Already Installed)
- `svelte` (v5.x)
- `@sveltejs/kit`
- `@tauri-apps/api`

### Backend Dependencies (Already Installed)
- `fastapi`
- `sqlite3` (Python standard library)
- `pydantic`

### New Dependencies (If Needed)
None expected - all features can be built with existing packages

---

## Estimated Breakdown

| Component | Lines | Hours |
|-----------|-------|-------|
| WorkOrderList.svelte | ~350 | 5h |
| WorkOrderCard.svelte | ~280 | 4h |
| WorkOrderProgress.svelte | ~190 | 3h |
| WorkOrderHistory.svelte | ~180 | 3h |
| Backend API endpoints | ~200 | 2h |
| Integration + Testing | - | 1h |
| **Total** | **~1,200 lines** | **18h** |

---

## Related Files

### To Read Before Starting
- [ForemanPanel.svelte](../frontend/src/lib/components/ForemanPanel.svelte) - Integration point
- [stores.js](../frontend/src/lib/stores.js) - Existing stores
- [+page.svelte](../frontend/src/routes/+page.svelte) - Modal handling
- [foreman.py](../backend/agents/foreman.py) - Foreman backend logic
- [api.py](../backend/api.py) - Backend API structure

### To Create
- `frontend/src/lib/components/WorkOrderList.svelte`
- `frontend/src/lib/components/WorkOrderCard.svelte`
- `frontend/src/lib/components/WorkOrderProgress.svelte`
- `frontend/src/lib/components/WorkOrderHistory.svelte`
- Backend: Work order API endpoints in `api.py`
- Backend: Work order state management in `foreman.py`

---

## Notes

### Future Enhancements (Out of Scope)
- Real-time WebSocket updates for live progress
- Work order templates for common tasks
- Estimated time remaining predictions
- Work order dependencies (e.g., Beat 2 depends on Beat 1)
- Bulk work order creation
- Work order scheduling

### Design Decisions
- **SQLite vs In-Memory**: Recommend SQLite for persistence across sessions
- **Polling vs WebSocket**: Start with polling (fetch every 2s), add WebSocket later
- **Expandable Cards vs Modal**: Use expandable cards for better UX (no context switch)
- **Mode Badges**: Use consistent color coding with rest of app

---

## Success Metrics

After implementation, writers should be able to:
1. See what the Foreman is currently working on (active work orders)
2. Track progress on multi-step tasks (e.g., Story Bible completion)
3. Review completed work orders to understand what was done
4. Navigate from work order to related content (beat, variant, etc.)
5. Understand why a work order failed (error messages)

This transparency builds trust in the AI system and helps writers understand the creative process.

---

**Created by**: Claude Code
**Last Updated**: 2025-11-27
**Status**: Ready for implementation
