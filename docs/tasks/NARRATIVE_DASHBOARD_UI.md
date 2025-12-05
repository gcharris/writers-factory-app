# Narrative Dashboard UI: Tension & Pacing Indicators

**Status**: Ready for Implementation
**Priority**: High - Visual payoff for GraphRAG backend work
**Depends On**: GraphRAG Phase 5 (complete on `nifty-antonelli`)
**Estimated Effort**: 3-4 hours

---

## Goal

Create visual dashboard components that display GraphRAG analysis to writers:
1. **Tension Indicator** - Real-time narrative tension score with visual feedback
2. **Pacing Dashboard** - Action/setup/resolution ratios with recommendations

These components turn the new GraphRAG analysis endpoints into visible, actionable writer feedback.

---

## API Endpoints Available

Both endpoints are already implemented and tested:

### Tension Endpoint
```bash
GET /graph/analysis/tension
```

Response:
```json
{
  "tension_score": 0.45,
  "level": "medium",
  "indicators": {
    "active_obstacles": 3,
    "unresolved_foreshadowing": 2,
    "contradictions": 0,
    "flaw_challenges": 1,
    "active_conflicts": 2
  },
  "total_edges": 45,
  "recommendation": "Balanced tension level"
}
```

### Pacing Endpoint
```bash
GET /graph/analysis/pacing
```

Response:
```json
{
  "pacing": "balanced",
  "edge_counts": {
    "action": 12,
    "setup": 18,
    "resolution": 5,
    "other": 10
  },
  "ratios": {
    "action_ratio": 0.267,
    "setup_ratio": 0.400,
    "resolution_ratio": 0.111
  },
  "recommendation": "Balanced pacing across narrative elements"
}
```

---

## Deliverables

### 1. TensionIndicator.svelte

**Location**: `frontend/src/lib/components/TensionIndicator.svelte`

**Features**:
- Circular or bar gauge showing tension score (0-1)
- Color gradient: green (low) → yellow (medium) → red (high)
- Tooltip showing breakdown of indicators
- Pulsing animation when tension is high
- Click to expand detailed view

**Visual Design**:
```
┌─────────────────────────┐
│  NARRATIVE TENSION      │
│  ┌───────────────────┐  │
│  │ ████████░░░░ 0.65 │  │ ← Color-coded bar
│  └───────────────────┘  │
│  Level: MEDIUM          │
│  ─────────────────────  │
│  ⚔ 3 obstacles          │ ← Indicators (collapsed by default)
│  🔮 2 foreshadows       │
│  ⚡ 1 flaw challenge    │
│  ─────────────────────  │
│  💡 Balanced tension    │ ← Recommendation
└─────────────────────────┘
```

**Props**:
```typescript
export let autoRefresh: boolean = true;
export let refreshInterval: number = 30000; // 30s
export let compact: boolean = false; // For sidebar mode
```

### 2. PacingDashboard.svelte

**Location**: `frontend/src/lib/components/PacingDashboard.svelte`

**Features**:
- Stacked bar or pie chart showing action/setup/resolution ratios
- Color coding: action (red), setup (blue), resolution (green)
- Pacing type label (fast/slow/balanced/concluding)
- Recommendation text
- Historical trend (if we track over time - optional)

**Visual Design**:
```
┌─────────────────────────────────┐
│  PACING ANALYSIS                │
│  ┌─────────────────────────────┐│
│  │████████████░░░░░░░░░░░░░░░░ ││ ← Action (27%)
│  │████████████████████░░░░░░░░ ││ ← Setup (40%)
│  │████░░░░░░░░░░░░░░░░░░░░░░░░ ││ ← Resolution (11%)
│  └─────────────────────────────┘│
│                                 │
│  Type: BALANCED                 │
│  ─────────────────────────────  │
│  💡 Balanced pacing across      │
│     narrative elements          │
└─────────────────────────────────┘
```

**Props**:
```typescript
export let autoRefresh: boolean = true;
export let refreshInterval: number = 30000;
export let showLegend: boolean = true;
```

### 3. NarrativeDashboard.svelte (Optional Wrapper)

**Location**: `frontend/src/lib/components/NarrativeDashboard.svelte`

Combines both indicators into a unified dashboard panel:

```svelte
<script>
  import TensionIndicator from './TensionIndicator.svelte';
  import PacingDashboard from './PacingDashboard.svelte';
</script>

<div class="narrative-dashboard">
  <TensionIndicator />
  <PacingDashboard />
</div>
```

---

## Integration Points

### Option A: Sidebar Widget
Add to the right sidebar (alongside existing panels):

```svelte
<!-- In +page.svelte or a layout component -->
<TensionIndicator compact={true} />
```

### Option B: Dedicated Tab
Add as a new tab in the TabbedPanel:

```svelte
{#if activeTab === 'narrative'}
  <NarrativeDashboard />
{/if}
```

### Option C: Status Bar
Minimal tension indicator in the status bar at bottom:

```svelte
<div class="status-bar">
  <TensionIndicator compact={true} showDetails={false} />
</div>
```

**Recommendation**: Start with Option A (sidebar) - least invasive, easy to test.

---

## Implementation Notes

### API Client Functions

Add to `frontend/src/lib/api_client.ts`:

```typescript
export async function getTension(): Promise<TensionResponse> {
  const response = await fetch(`${API_BASE}/graph/analysis/tension`);
  if (!response.ok) throw new Error('Failed to fetch tension');
  return response.json();
}

export async function getPacing(): Promise<PacingResponse> {
  const response = await fetch(`${API_BASE}/graph/analysis/pacing`);
  if (!response.ok) throw new Error('Failed to fetch pacing');
  return response.json();
}

interface TensionResponse {
  tension_score: number;
  level: 'low' | 'medium' | 'high';
  indicators: {
    active_obstacles: number;
    unresolved_foreshadowing: number;
    contradictions: number;
    flaw_challenges: number;
    active_conflicts: number;
  };
  recommendation: string;
}

interface PacingResponse {
  pacing: 'fast' | 'slow' | 'balanced' | 'concluding';
  edge_counts: {
    action: number;
    setup: number;
    resolution: number;
    other: number;
  };
  ratios: {
    action_ratio: number;
    setup_ratio: number;
    resolution_ratio: number;
  };
  recommendation: string;
}
```

### Styling Approach

Use Tailwind CSS classes consistent with existing components:
- Cards: `bg-white dark:bg-gray-800 rounded-lg shadow p-4`
- Text: `text-sm text-gray-600 dark:text-gray-300`
- Emphasis: `font-semibold text-gray-900 dark:text-white`

### Error Handling

- Show skeleton loader while fetching
- Graceful fallback if graph is empty (no tension data)
- Retry logic for transient failures

---

## Files Checklist

**Create**:
- [ ] `frontend/src/lib/components/TensionIndicator.svelte`
- [ ] `frontend/src/lib/components/PacingDashboard.svelte`
- [ ] `frontend/src/lib/components/NarrativeDashboard.svelte` (optional)

**Modify**:
- [ ] `frontend/src/lib/api_client.ts` - Add getTension(), getPacing()
- [ ] `frontend/src/routes/+page.svelte` or sidebar component - Integration

---

## Success Criteria

- [ ] Tension indicator displays score with color gradient
- [ ] Tension level (low/medium/high) is visually distinct
- [ ] Pacing ratios are displayed as visual bars/chart
- [ ] Recommendations are shown clearly
- [ ] Auto-refresh works without performance issues
- [ ] Components handle empty graph gracefully
- [ ] Compact mode works for sidebar placement
- [ ] npm run check passes

---

## Bonus: VerificationNotification Integration

While working on the dashboard, also wire up the existing `VerificationNotification.svelte`:

**File**: `frontend/src/routes/+page.svelte`

Add near the end of the component:
```svelte
<script>
  import VerificationNotification from '$lib/components/VerificationNotification.svelte';
</script>

<!-- At end of template -->
<VerificationNotification />
```

This is a quick win - the component already exists from Phase 4.

---

## Handoff

When complete, provide:
1. Screenshots of the components in action
2. Branch name and commit hash
3. Any deviations from spec
4. npm run check output

---

*Task created: December 5, 2025*
*GraphRAG backend by: nifty-antonelli branch*
