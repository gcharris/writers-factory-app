# Work Orders UI - Implementation Specification

## Context

Work Orders are background tasks that run asynchronously (voice tournaments, scene generation, health checks, etc.). The UI needs to show progress, allow cancellation, and provide history access.

**Current Status**: 3 components exist (1,309 lines), but need verification and potential improvements.

---

## 📦 Existing Components (Need Verification)

### 1. StatusBar.svelte (429 lines)
**Location**: `frontend/src/lib/components/chat/StatusBar.svelte`

**Purpose**: Bottom bar showing active task progress or idle state

**Features (from code review)**:
- Active task display with progress (e.g., "Generating voice variants... 3/5")
- Idle state with completed count
- "View history" link
- Task icons by type: 🎤 (voice), ✍️ (scene), 📖 (story bible), 🩺 (health), 🧠 (consolidation)
- Status colors: Running (cyan), Completed (green), Failed (red), Pending (yellow)

**Integration**:
- Imported in `ForemanPanel.svelte` (line 26)
- Imported in `MainLayout.svelte` (line 33)

**Needs Screenshot**: Where does this appear? Is it working correctly?

---

### 2. WorkOrderHistory.svelte (470 lines)
**Location**: `frontend/src/lib/components/chat/WorkOrderHistory.svelte`

**Purpose**: Modal showing historical work orders

**Features (from code review)**:
- Filter by status: All, Completed, Failed, Cancelled
- Statistics (total, completed, failed, cancelled counts)
- Formatted dates (relative: "2h ago", "3 days ago")
- Clear old entries functionality
- Task icons and status colors

**Integration**:
- Imported in `ForemanPanel.svelte` (line 27)

**Needs Screenshot**: Can you open this modal? What does it look like?

---

### 3. WorkOrderTracker.svelte (410 lines)
**Location**: `frontend/src/lib/components/WorkOrderTracker.svelte`

**Purpose**: Unknown - needs investigation

**Integration**:
- Imported in `ArchitectModeUI.svelte` (line 23)

**Question**: What is this component for? Is it a duplicate of StatusBar?

---

## 🔍 Investigation Needed (Waiting for Screenshots)

### Questions to Answer:

1. **Where do Work Orders appear?**
   - Bottom of Foreman panel?
   - Separate panel?
   - Toast notifications?

2. **What's working vs. broken?**
   - Can you see active tasks running?
   - Does progress update in real-time?
   - Can you cancel tasks?
   - Can you open history modal?

3. **What's missing?**
   - Visual design issues?
   - Missing functionality?
   - Confusing UX?

4. **Backend integration**:
   - Are work orders actually being created when you run tournaments/scene generation?
   - Do they show in the UI?
   - Do they persist across restarts?

---

## 🎯 Expected User Experience (Based on Spec)

### Active Task State:
```
┌─────────────────────────────────────────────────────────┐
│ ⏳ Generating voice variants... 3/5                     │
│ [progress bar: 60%]                                     │
│ [Cancel] [Details ▼]                                    │
└─────────────────────────────────────────────────────────┘
```

### Idle State:
```
┌─────────────────────────────────────────────────────────┐
│ ✓ 3 tasks completed today     [View history →]         │
└─────────────────────────────────────────────────────────┘
```

### History Modal:
```
┌────────────────────────────────────────────────────────────┐
│ Work Order History                              [✕ Close] │
├────────────────────────────────────────────────────────────┤
│ [All] [Completed] [Failed] [Cancelled]                    │
│                                                            │
│ ✓ Voice Tournament - Mickey Bardot      2h ago            │
│   15 variants generated                                    │
│                                                            │
│ ✓ Scene Generation - Chapter 3          4h ago            │
│   Scene created (Grade: A-)                                │
│                                                            │
│ ✗ Health Check - Timeline                Yesterday        │
│   Error: Missing beat reference                            │
│                                                            │
│                            [Clear old entries]             │
└────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Architecture

### State Management (stores.js)

**Stores**:
```javascript
workOrders         // All work orders (persistent)
activeWorkOrder    // Currently running task
showWorkOrderHistory  // Modal visibility
```

**Helper Functions**:
```javascript
createWorkOrder(type, name)
updateWorkOrder(id, updates)
startWorkOrder(workOrder)
completeWorkOrder(id, result)
failWorkOrder(id, error)
cancelWorkOrder(id)
clearOldWorkOrders()
```

**Work Order Structure**:
```javascript
{
  id: "wo_1234567890_abc123",
  type: "voice_tournament" | "scene_generation" | "story_bible" | "health_check" | "consolidation",
  name: "Voice Tournament - Mickey Bardot",
  status: "pending" | "running" | "completed" | "failed" | "cancelled",
  progress: { current: 3, total: 5 } | null,
  message: "Processing variant 3...",
  started_at: "2025-11-27T19:30:00Z",
  completed_at: "2025-11-27T19:45:00Z" | null,
  result: { /* task-specific data */ },
  error: "Error message" | null
}
```

---

## 🚧 Potential Issues to Check

### 1. Real-Time Updates
**Question**: Do work orders update in real-time?

**Current Implementation** (from StatusBar.svelte):
- Has `pollInterval` variable (suggests polling)
- Needs backend endpoint to poll for status

**Backend Requirement**:
```
GET /work-orders/active
GET /work-orders/status/{id}
```

**Action**: Verify these endpoints exist in `backend/api.py`

---

### 2. Task Lifecycle Integration

**Where are work orders created?**

Potential creation points:
1. Voice Calibration starts → Create `voice_tournament` work order
2. Scene generation starts → Create `scene_generation` work order
3. Health check starts → Create `health_check` work order
4. Graph consolidation starts → Create `consolidation` work order

**Action**: Search for `createWorkOrder()` calls to verify integration

---

### 3. Persistence

**Question**: Do work orders survive app restart?

**Current**: Uses `persistentWritable` → Should save to localStorage

**Action**: Test by:
1. Starting a task
2. Closing app
3. Reopening
4. Check if work order history shows previous task

---

## 📋 Implementation Checklist (After Screenshots)

### Phase 1: Verification (2-3 hours)
- [ ] Take screenshots of current work order UI
- [ ] Test creating a work order (run voice tournament or scene generation)
- [ ] Check if StatusBar shows active task
- [ ] Check if progress updates
- [ ] Test cancelling a task
- [ ] Open WorkOrderHistory modal
- [ ] Verify persistence (restart app)

### Phase 2: Backend Integration (3-4 hours)
- [ ] Add missing API endpoints (if needed):
  - `GET /work-orders/active`
  - `GET /work-orders/history`
  - `POST /work-orders/{id}/cancel`
- [ ] Integrate work order creation in:
  - Voice calibration flow
  - Scene generation flow
  - Health check flow
  - Consolidation flow

### Phase 3: UI Improvements (4-6 hours)
- [ ] Fix any visual issues identified in screenshots
- [ ] Add missing features:
  - Real-time progress updates
  - Cancel button functionality
  - Expandable task details
  - Toast notifications for completion
- [ ] Polish styling to match cyber-noir theme
- [ ] Add loading states and error handling

### Phase 4: Polish (2-3 hours)
- [ ] Keyboard shortcuts (Escape to close modal, etc.)
- [ ] Accessibility (ARIA labels, focus management)
- [ ] Empty states (no work orders yet)
- [ ] Animation/transitions
- [ ] Responsive design

---

## 🎨 Design Principles

**From Assistant Panel Redesign** (for consistency):

1. **Cyber-Noir Theme**:
   - Dark backgrounds (`--bg-secondary`, `--bg-tertiary`)
   - Accent colors: Cyan (running), Gold (warning), Green (success), Red (error)
   - Subtle borders and shadows

2. **Status Colors**:
   - Running: `--accent-cyan` (#58a6ff)
   - Completed: `--success` (#3fb950)
   - Failed: `--error` (#f85149)
   - Pending: `--warning` (#d29922)
   - Cancelled: `--text-muted` (#8b949e)

3. **Task Icons**:
   - Voice Tournament: 🎤
   - Scene Generation: ✍️
   - Story Bible: 📖
   - Health Check: 🩺
   - Consolidation: 🧠

---

## 📸 Screenshots Needed

Please provide screenshots showing:

1. **StatusBar in different states**:
   - Active task running with progress
   - Idle state (no active tasks)
   - Multiple tasks queued

2. **WorkOrderHistory modal**:
   - Opening the modal
   - Filtered views (All, Completed, Failed)
   - Empty state (no history)

3. **Integration points**:
   - Where StatusBar appears in ForemanPanel
   - Where StatusBar appears in MainLayout
   - WorkOrderTracker in ArchitectModeUI (if visible)

4. **Task creation**:
   - Trigger a voice tournament and show work order creation
   - Show progress updates during task

5. **Any errors or issues**:
   - What's broken?
   - What's missing?
   - What's confusing?

---

## Next Steps

1. **User provides screenshots** → I'll analyze what's working/broken
2. **I'll update this spec** with specific fixes needed
3. **Create implementation tasks** based on findings
4. **Prioritize fixes** (Critical → High → Medium → Polish)

---

*Document created: 2025-11-27*
*Status: WAITING FOR SCREENSHOTS*
*Estimated Total Effort: 11-16 hours (after verification)*
