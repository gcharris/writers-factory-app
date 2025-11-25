# Writers Factory - UI Implementation Plan

**Version**: 1.0
**Date**: November 25, 2025
**Status**: Planning Phase
**Target**: Complete 4-Panel "Cyber-Noir" IDE Interface

---

## Executive Summary

This document outlines the complete implementation plan for the Writers Factory UI, transforming it from the current primitive 3-panel design into a professional, collapsible 4-panel IDE with:

- **Flexible panel system** with drag-to-resize and collapsibility
- **Studio panel** with card-based tool interface
- **Split Foreman panel** (Chat + Live Knowledge Graph)
- **Focus Mode** for distraction-free writing
- **AI Intelligence integration** (Phase 3E Model Orchestrator)

**Design Philosophy**: "Professional IDE meets Cyber-Noir aesthetic" - VS Code power with NotebookLM's Studio concept, optimized for novelists.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Panel System Design](#panel-system-design)
3. [Technology Stack](#technology-stack)
4. [Implementation Phases](#implementation-phases)
5. [Component Specifications](#component-specifications)
6. [Visual Design System](#visual-design-system)
7. [State Management](#state-management)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [Responsive Behavior](#responsive-behavior)
10. [Testing Strategy](#testing-strategy)

---

## 1. Architecture Overview

### 1.1 High-Level Structure

```
┌──────────────────────────────────────────────────────────────┐
│ Writers Factory Menu Bar                                     │
│ File  Edit  Selection  View  AI  Go  Run  Terminal  Window  │
└──────────────────────────────────────────────────────────────┘
┌─────────┬──────────────┬─────────────┬──────────┐
│ BINDER  │   CANVAS     │  FOREMAN    │ STUDIO   │  Main Panels
│ 250px   │   FLEX       │   400px     │  280px   │
│         │              │             │          │
│ File    │  Monaco      │  Chat       │  Tools   │
│ Tree    │  Editor      │  ─────────  │  (Cards) │
│         │              │  Graph      │          │
│         │              │             │          │
│ ⌘B      │  Always      │  ⌘J         │  ⌘K      │
│ Toggle  │  Visible     │  Toggle +   │  Toggle  │
│         │              │  Split      │          │
└─────────┴──────────────┴─────────────┴──────────┘
┌──────────────────────────────────────────────────────────────┐
│ Status Bar: Graph Nodes: 1,240 | Uncommitted: 3 | Model: ...│
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Panel Responsibilities

| Panel | Width | Collapsible | Primary Function | Key Components |
|-------|-------|-------------|------------------|----------------|
| **Binder** | 200-300px | Yes (⌘B) | File navigation | TreeView, ContextMenus |
| **Canvas** | Flex (min 600px) | No | Writing/editing | Monaco Editor, Breadcrumbs |
| **Foreman** | 400px | Yes (⌘J) | AI chat + graph | ChatStream, ForceGraph |
| **Studio** | 280px | Yes (⌘K) | Tool launcher | ToolCards, ActionButtons |

### 1.3 View Modes

```typescript
enum ViewMode {
  FULL_IDE = "full",        // All 4 panels visible
  FOCUS = "focus",          // Canvas only (⌘⇧F)
  WRITING = "writing",      // Binder + Canvas
  DIRECTOR = "director"     // Canvas + Foreman + Studio
}
```

---

## 2. Panel System Design

### 2.1 Core Layout Component

**File**: `frontend/src/lib/layouts/MainLayout.svelte`

**Responsibilities**:
- Manage 4-panel grid with flexible widths
- Handle panel visibility state
- Persist panel widths to localStorage
- Provide drag-to-resize functionality
- Implement view mode switching

**Props**:
```typescript
interface MainLayoutProps {
  initialMode?: ViewMode;
  minCanvasWidth?: number; // Default: 600px
  persistKey?: string;     // localStorage key
}
```

**State**:
```typescript
interface LayoutState {
  viewMode: ViewMode;
  panels: {
    binder: { visible: boolean; width: number };
    canvas: { width: number };
    foreman: { visible: boolean; width: number; split: boolean };
    studio: { visible: boolean; width: number };
  };
}
```

### 2.2 Resizable Panel Implementation

**Library**: `svelte-splitpanes` or custom implementation

**Key Features**:
- Drag handles between panels
- Min/max width constraints
- Smooth resize with debounced persistence
- Visual feedback on drag (highlight drag area)

**Example**:
```svelte
<Splitpanes horizontal>
  <Pane minSize={15} maxSize={30}>
    <PanelBinder />
  </Pane>
  <Pane minSize={40}>
    <PanelCanvas />
  </Pane>
  <Pane minSize={20} maxSize={40}>
    <PanelForeman />
  </Pane>
  <Pane minSize={15} maxSize={25}>
    <PanelStudio />
  </Pane>
</Splitpanes>
```

### 2.3 Panel Collapse/Expand

**Behavior**:
- Click toggle button (⌘B/⌘J/⌘K) → panel slides out/in
- Animation: 200ms ease-out
- When collapsed: 0px width (not hidden, allows animation)
- Canvas automatically flexes to fill space

**Toggle Buttons Location**:
- Binder: Top-right corner of Binder panel
- Foreman: Top-right corner of Foreman panel
- Studio: Top-right corner of Studio panel

---

## 3. Technology Stack

### 3.1 Core Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| **Svelte** | 4.x | Component framework |
| **SvelteKit** | 2.x | App framework, routing |
| **TypeScript** | 5.x | Type safety |
| **Vite** | 5.x | Build tool |

### 3.2 UI Libraries

| Library | Purpose | Notes |
|---------|---------|-------|
| **svelte-splitpanes** | Panel resizing | Or custom implementation |
| **Monaco Editor** | Code/text editor | Already integrated |
| **D3.js** | Force-directed graph | For Live Graph |
| **Lucide Svelte** | Icons | Consistent icon system |
| **TailwindCSS** | Styling | Cyber-Noir theme |

### 3.3 State Management

| Tool | Purpose |
|------|---------|
| **Svelte Stores** | Global UI state (panel visibility, widths) |
| **Context API** | Panel-specific state |
| **localStorage** | Persist panel preferences |

### 3.4 Development Tools

| Tool | Purpose |
|------|---------|
| **Storybook** | Component development/testing |
| **Playwright** | E2E testing |
| **Vitest** | Unit testing |

---

## 4. Implementation Phases

### Phase 1: Panel Infrastructure (Week 1)
**Goal**: Working 4-panel layout with resize/collapse

**Tasks**:
1. ✅ Create `MainLayout.svelte` with 4-panel grid
2. ✅ Implement panel resize with drag handles
3. ✅ Add collapse/expand animations
4. ✅ Persist panel widths to localStorage
5. ✅ Add keyboard shortcuts (⌘B, ⌘J, ⌘K, ⌘⇧F)
6. ✅ Create view mode switcher

**Deliverables**:
- `MainLayout.svelte` (~200 lines)
- `PanelBinder.svelte` (placeholder)
- `PanelCanvas.svelte` (Monaco wrapper)
- `PanelForeman.svelte` (placeholder)
- `PanelStudio.svelte` (placeholder)

**Success Criteria**:
- Can resize all panels with mouse
- Panels collapse/expand smoothly
- Preferences persist across reloads
- Focus Mode works (Canvas only)

---

### Phase 2: Studio Panel (Week 1-2)
**Goal**: Card-based tool interface with AI Intelligence

**Tasks**:
1. ✅ Create `StudioCard.svelte` component
2. ✅ Implement card grid layout (2 columns)
3. ✅ Add existing tools:
   - Voice Tournament
   - Scaffold Generator
   - Health Check
   - Metabolism
4. ✅ Add AI Intelligence card
5. ✅ Implement card states (Ready, Active, Warning, Error)
6. ✅ Add click handlers to open tools/settings

**Deliverables**:
- `PanelStudio.svelte` (~150 lines)
- `StudioCard.svelte` (~100 lines)
- `AIIntelligenceCard.svelte` (~80 lines)

**Success Criteria**:
- Cards display with correct status/icons
- Clicking cards triggers appropriate actions
- AI Intelligence card shows live cost data
- Responsive grid (2 cols on desktop, 1 col on narrow)

---

### Phase 3: AI Intelligence Integration (Week 2)
**Goal**: Full Model Orchestrator UI

**Tasks**:
1. ✅ Create `SettingsOrchestrator.svelte` modal
2. ✅ Add quality tier selector (3 cards)
3. ✅ Implement cost estimator widget
4. ✅ Add monthly budget input
5. ✅ Create model assignments preview
6. ✅ Wire up to Phase 3E backend endpoints
7. ✅ Add menu bar "AI" menu

**Deliverables**:
- `SettingsOrchestrator.svelte` (~200 lines)
- `CostEstimator.svelte` (~100 lines)
- `QualityTierCard.svelte` (~80 lines)
- Menu bar integration

**Success Criteria**:
- Tier selection updates backend immediately
- Cost estimator displays real-time spend
- Model recommendations update on tier change
- Menu bar "AI" menu shows current tier

---

### Phase 4: Foreman Split Panel (Week 2-3)
**Goal**: Chat + Live Graph split

**Tasks**:
1. ✅ Create split-pane within Foreman panel
2. ✅ Implement chat interface (top half)
3. ✅ Implement force-directed graph (bottom half)
4. ✅ Add drag handle between chat/graph
5. ✅ Connect graph to knowledge base
6. ✅ Add node selection → details display

**Deliverables**:
- `PanelForeman.svelte` with split (~150 lines)
- `ForemanChat.svelte` (~120 lines)
- `LiveGraph.svelte` (~200 lines, D3.js)
- `NodeDetails.svelte` (~80 lines)

**Success Criteria**:
- Chat displays Foreman messages correctly
- Graph visualizes knowledge nodes/edges
- Drag handle resizes chat vs graph ratio
- Clicking node shows details panel

---

### Phase 5: Polish & Testing (Week 3)
**Goal**: Production-ready UI

**Tasks**:
1. ✅ Implement Cyber-Noir theme (dark + cyan/gold)
2. ✅ Add animations (panel slide, card hover, etc.)
3. ✅ Optimize performance (debounce resizes, virtual scrolling)
4. ✅ Add loading states for all async operations
5. ✅ Write unit tests for components
6. ✅ E2E tests for critical flows
7. ✅ Accessibility audit (keyboard nav, screen readers)

**Deliverables**:
- Complete theme system
- Animation library
- Test suite (>80% coverage)
- Accessibility improvements

**Success Criteria**:
- No jank when resizing panels
- All interactive elements keyboard accessible
- Lighthouse score >90
- Zero console errors

---

## 5. Component Specifications

### 5.1 MainLayout.svelte

**File**: `frontend/src/lib/layouts/MainLayout.svelte`

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import PanelBinder from './panels/PanelBinder.svelte';
  import PanelCanvas from './panels/PanelCanvas.svelte';
  import PanelForeman from './panels/PanelForeman.svelte';
  import PanelStudio from './panels/PanelStudio.svelte';

  // View mode state
  let viewMode: ViewMode = ViewMode.FULL_IDE;

  // Panel visibility
  let binderVisible = true;
  let foremanVisible = true;
  let studioVisible = true;

  // Panel widths (percentages)
  let binderWidth = 15;
  let foremanWidth = 25;
  let studioWidth = 18;

  // Computed canvas width
  $: canvasWidth = 100 -
    (binderVisible ? binderWidth : 0) -
    (foremanVisible ? foremanWidth : 0) -
    (studioVisible ? studioWidth : 0);

  // Keyboard shortcuts
  function handleKeyPress(e: KeyboardEvent) {
    if (e.metaKey || e.ctrlKey) {
      switch(e.key) {
        case 'b': toggleBinder(); break;
        case 'j': toggleForeman(); break;
        case 'k': toggleStudio(); break;
        case 'F': if (e.shiftKey) toggleFocusMode(); break;
      }
    }
  }

  function toggleBinder() {
    binderVisible = !binderVisible;
    persistState();
  }

  function toggleForeman() {
    foremanVisible = !foremanVisible;
    persistState();
  }

  function toggleStudio() {
    studioVisible = !studioVisible;
    persistState();
  }

  function toggleFocusMode() {
    if (viewMode === ViewMode.FOCUS) {
      viewMode = ViewMode.FULL_IDE;
      binderVisible = true;
      foremanVisible = true;
      studioVisible = true;
    } else {
      viewMode = ViewMode.FOCUS;
      binderVisible = false;
      foremanVisible = false;
      studioVisible = false;
    }
    persistState();
  }

  function persistState() {
    localStorage.setItem('wf-layout', JSON.stringify({
      viewMode,
      binderVisible,
      foremanVisible,
      studioVisible,
      binderWidth,
      foremanWidth,
      studioWidth
    }));
  }

  function loadState() {
    const saved = localStorage.getItem('wf-layout');
    if (saved) {
      const state = JSON.parse(saved);
      viewMode = state.viewMode ?? ViewMode.FULL_IDE;
      binderVisible = state.binderVisible ?? true;
      foremanVisible = state.foremanVisible ?? true;
      studioVisible = state.studioVisible ?? true;
      binderWidth = state.binderWidth ?? 15;
      foremanWidth = state.foremanWidth ?? 25;
      studioWidth = state.studioWidth ?? 18;
    }
  }

  onMount(() => {
    loadState();
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  });
</script>

<div class="main-layout">
  <!-- Implementation here -->
</div>

<style>
  .main-layout {
    display: flex;
    height: 100vh;
    background: var(--bg-primary);
  }
  /* ... more styles */
</style>
```

**Key Methods**:
- `toggleBinder()` / `toggleForeman()` / `toggleStudio()`: Toggle panel visibility
- `toggleFocusMode()`: Hide all panels except Canvas
- `persistState()`: Save layout to localStorage
- `loadState()`: Restore layout from localStorage
- `handleKeyPress()`: Process keyboard shortcuts

---

### 5.2 StudioCard.svelte

**File**: `frontend/src/lib/components/studio/StudioCard.svelte`

```typescript
export interface StudioCardProps {
  title: string;           // "Voice Tournament"
  icon: string;            // "🎤" or lucide icon name
  status: string;          // "Ready", "Active", "3 Conflicts", etc.
  variant?: CardVariant;   // "default" | "success" | "warning" | "error" | "active"
  subtitle?: string;       // "$0.47 / $2.00"
  progress?: number;       // 0-100 for progress bar
  action?: string;         // "Run", "Stop", "Configure"
  disabled?: boolean;
  onClick?: () => void;
}

enum CardVariant {
  DEFAULT = "default",
  SUCCESS = "success",
  WARNING = "warning",
  ERROR = "error",
  ACTIVE = "active"
}
```

**Visual States**:
- **Default**: Slate gray background, cyan border on hover
- **Success**: Subtle green glow
- **Warning**: Orange/gold border + icon
- **Error**: Red border + error icon
- **Active**: Pulsing cyan glow, animated border

**Example**:
```svelte
<StudioCard
  title="AI Intelligence"
  icon="🎯"
  status="Balanced"
  subtitle="$0.47 / $2.00"
  progress={24}
  action="Configure"
  variant="success"
  on:click={openAISettings}
/>
```

---

### 5.3 SettingsOrchestrator.svelte

**File**: `frontend/src/lib/components/settings/SettingsOrchestrator.svelte`

**Layout**:
```
┌──────────────────────────────────────────────┐
│  AI Intelligence & Model Orchestration       │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────┐ ┌────────┐ ┌────────┐          │
│  │ BUDGET │ │BALANCED│ │PREMIUM │          │
│  │  Free  │ │  Best  │ │Highest │          │
│  │  $0/mo │ │ Value  │ │Quality │          │
│  │        │ │ $0.50  │ │ $3-5   │          │
│  └────────┘ └────────┘ └────────┘          │
│       ○         ●          ○                │
│                                              │
│  Monthly Budget:  [$2.00____________]       │
│                                              │
│  Current Spend:                              │
│  ┌────────────────────────────────┐         │
│  │ $0.47 / $2.00                 │         │
│  │ ██████████░░░░░░░░░░ 24%      │         │
│  │ $1.53 remaining                │         │
│  └────────────────────────────────┘         │
│                                              │
│  ☐ Prefer local models when similar         │
│                                              │
│  📋 Model Assignments (preview):             │
│  ┌────────────────────────────────┐         │
│  │ • Health Checks → llama3.2     │         │
│  │ • Theme Analysis → deepseek    │         │
│  │ • Coordination → mistral       │         │
│  └────────────────────────────────┘         │
│                                              │
│              [Cancel]  [Save]                │
└──────────────────────────────────────────────┘
```

**Data Flow**:
1. On mount: Fetch current settings (`GET /settings/category/orchestrator`)
2. On tier change: Update preview (`POST /orchestrator/estimate-cost`)
3. On save: Update backend (`POST /settings`)
4. On budget change: Validate and update cost estimator

---

### 5.4 LiveGraph.svelte

**File**: `frontend/src/lib/components/foreman/LiveGraph.svelte`

**Technology**: D3.js force-directed graph

**Features**:
- **Nodes**: Characters (cyan), Locations (gold), Items (white)
- **Edges**: Relationship lines with labels
- **Interactions**:
  - Click node → Show NodeDetails panel
  - Hover node → Highlight connected nodes
  - Drag node → Reposition (affects physics)
  - Zoom/pan with mouse wheel/drag

**Data Structure**:
```typescript
interface GraphNode {
  id: string;
  type: 'character' | 'location' | 'item';
  label: string;
  properties: Record<string, any>;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
  label: string;
}
```

**API Integration**:
- Fetch graph data: `GET /graph/view`
- Updates on metabolism: WebSocket or polling

---

## 6. Visual Design System

### 6.1 Color Palette (Cyber-Noir)

```css
:root {
  /* Base colors */
  --bg-primary: #0a0e14;        /* Deep black-blue */
  --bg-secondary: #141b24;      /* Slightly lighter */
  --bg-tertiary: #1e2936;       /* Panel backgrounds */

  /* Accents */
  --accent-cyan: #00d4ff;       /* Primary accent */
  --accent-gold: #f2a83b;       /* Warning/Director Mode */
  --accent-green: #4ade80;      /* Success */
  --accent-red: #ef4444;        /* Error */

  /* Text */
  --text-primary: #e6edf3;      /* High contrast */
  --text-secondary: #8b949e;    /* Muted */
  --text-tertiary: #57606a;     /* Very muted */

  /* Borders */
  --border-default: #30363d;
  --border-active: var(--accent-cyan);
  --border-warning: var(--accent-gold);
}
```

### 6.2 Typography

```css
:root {
  /* Headings */
  --font-heading: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Body (Editor) */
  --font-body: 'Charter', 'Georgia', serif;  /* Readable serif for prose */

  /* Sizes */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
}
```

### 6.3 Component Styles

**Studio Card**:
```css
.studio-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s ease;
}

.studio-card:hover {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.3);
  transform: translateY(-2px);
}

.studio-card.active {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 24px rgba(0, 212, 255, 0.5);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 24px rgba(0, 212, 255, 0.5); }
  50% { box-shadow: 0 0 32px rgba(0, 212, 255, 0.7); }
}
```

**Panel Drag Handle**:
```css
.drag-handle {
  width: 4px;
  background: var(--border-default);
  cursor: col-resize;
  transition: background 0.2s;
}

.drag-handle:hover,
.drag-handle:active {
  background: var(--accent-cyan);
}
```

---

## 7. State Management

### 7.1 Global UI State (Svelte Store)

**File**: `frontend/src/lib/stores/uiStore.ts`

```typescript
import { writable } from 'svelte/store';

interface UIState {
  layout: {
    viewMode: ViewMode;
    panels: {
      binder: { visible: boolean; width: number };
      foreman: { visible: boolean; width: number; split: boolean };
      studio: { visible: boolean; width: number };
    };
  };
  activeModal: string | null;
  sidebarExpanded: boolean;
}

const defaultState: UIState = {
  layout: {
    viewMode: ViewMode.FULL_IDE,
    panels: {
      binder: { visible: true, width: 250 },
      foreman: { visible: true, width: 400, split: true },
      studio: { visible: true, width: 280 }
    }
  },
  activeModal: null,
  sidebarExpanded: true
};

export const uiStore = writable<UIState>(defaultState);

// Helper actions
export const ui = {
  toggleBinder: () => uiStore.update(s => ({
    ...s,
    layout: {
      ...s.layout,
      panels: {
        ...s.layout.panels,
        binder: { ...s.layout.panels.binder, visible: !s.layout.panels.binder.visible }
      }
    }
  })),
  // ... more helpers
};
```

### 7.2 Orchestrator Settings State

**File**: `frontend/src/lib/stores/orchestratorStore.ts`

```typescript
import { writable, derived } from 'svelte/store';
import { api } from '$lib/api';

interface OrchestratorState {
  enabled: boolean;
  qualityTier: 'budget' | 'balanced' | 'premium';
  monthlyBudget: number | null;
  currentSpend: number;
  currentMonth: string | null;
  preferLocal: boolean;
}

export const orchestratorStore = writable<OrchestratorState>({
  enabled: false,
  qualityTier: 'balanced',
  monthlyBudget: null,
  currentSpend: 0,
  currentMonth: null,
  preferLocal: false
});

// Derived: Budget remaining
export const budgetRemaining = derived(
  orchestratorStore,
  $store => {
    if ($store.monthlyBudget === null) return null;
    return $store.monthlyBudget - $store.currentSpend;
  }
);

// Derived: Budget warning (>80%)
export const budgetWarning = derived(
  [orchestratorStore, budgetRemaining],
  ([$store, $remaining]) => {
    if ($store.monthlyBudget === null || $remaining === null) return false;
    return ($remaining / $store.monthlyBudget) <= 0.2; // <20% remaining
  }
);

// Actions
export const orchestrator = {
  async load() {
    const data = await api.get('/settings/category/orchestrator');
    orchestratorStore.set(data.settings);
  },

  async setTier(tier: 'budget' | 'balanced' | 'premium') {
    await api.post('/settings', {
      key: 'orchestrator.quality_tier',
      value: tier
    });
    orchestratorStore.update(s => ({ ...s, qualityTier: tier }));
  },

  // ... more actions
};
```

---

## 8. Keyboard Shortcuts

### 8.1 Global Shortcuts

| Shortcut | Action | Scope |
|----------|--------|-------|
| `⌘B` / `Ctrl+B` | Toggle Binder panel | Global |
| `⌘J` / `Ctrl+J` | Toggle Foreman panel | Global |
| `⌘K` / `Ctrl+K` | Toggle Studio panel | Global |
| `⌘⇧F` / `Ctrl+Shift+F` | Toggle Focus Mode | Global |
| `⌘,` / `Ctrl+,` | Open Settings | Global |
| `⌘⇧P` / `Ctrl+Shift+P` | Command Palette | Global |

### 8.2 Panel-Specific Shortcuts

| Shortcut | Action | Scope |
|----------|--------|-------|
| `⌘⇧E` | Focus Binder (Explorer) | Binder |
| `⌘1` | Focus Canvas | Canvas |
| `⌘2` | Focus Foreman | Foreman |
| `⌘3` | Focus Studio | Studio |

### 8.3 Implementation

```typescript
// Global keyboard handler
function handleGlobalKeyPress(e: KeyboardEvent) {
  const isMod = e.metaKey || e.ctrlKey;
  const isShift = e.shiftKey;

  if (isMod) {
    switch(e.key) {
      case 'b': ui.toggleBinder(); break;
      case 'j': ui.toggleForeman(); break;
      case 'k': ui.toggleStudio(); break;
      case 'F': if (isShift) ui.toggleFocusMode(); break;
      case ',': openSettings(); break;
      case 'P': if (isShift) openCommandPalette(); break;
    }
  }
}
```

---

## 9. Responsive Behavior

### 9.1 Breakpoints

```css
/* Desktop (default) */
@media (min-width: 1280px) {
  /* 4-panel layout */
}

/* Laptop (medium) */
@media (min-width: 1024px) and (max-width: 1279px) {
  /* Auto-collapse Binder by default */
  /* Reduce Studio width to 250px */
}

/* Tablet (small) - NOT PRIMARY TARGET */
@media (max-width: 1023px) {
  /* Show warning: "Writers Factory requires desktop browser" */
}
```

### 9.2 Minimum Requirements

- **Minimum Screen Width**: 1024px
- **Recommended**: 1440px or larger
- **Target**: Desktop/laptop writers, not mobile

---

## 10. Testing Strategy

### 10.1 Unit Tests (Vitest)

**Components to Test**:
- `StudioCard.svelte`: Props, states, click handlers
- `CostEstimator.svelte`: Budget calculations, warnings
- `QualityTierCard.svelte`: Selection logic

**Example**:
```typescript
import { render } from '@testing-library/svelte';
import StudioCard from '$lib/components/studio/StudioCard.svelte';

test('StudioCard renders with correct status', () => {
  const { getByText } = render(StudioCard, {
    props: {
      title: 'Test Tool',
      status: 'Ready',
      icon: '🎯'
    }
  });
  expect(getByText('Ready')).toBeInTheDocument();
});
```

### 10.2 Integration Tests

**Scenarios**:
1. Panel resize → persist to localStorage
2. Toggle panel → updates layout correctly
3. Change tier → updates cost estimator
4. Save settings → backend receives correct data

### 10.3 E2E Tests (Playwright)

**Critical Flows**:
1. **Full IDE Mode** → Toggle panels → Verify layout
2. **Focus Mode** → Enter/exit → Verify Canvas only visible
3. **AI Settings** → Change tier → Save → Verify backend updated
4. **Studio Cards** → Click Health Check → Verify modal opens

---

## Success Metrics

### Phase 1 (Panel Infrastructure)
- ✅ All panels resize smoothly (no jank)
- ✅ Collapse/expand animations < 200ms
- ✅ Panel preferences persist across reloads
- ✅ Keyboard shortcuts work 100% of time

### Phase 2 (Studio Panel)
- ✅ Cards render correctly with all variants
- ✅ Status updates reflect backend state
- ✅ Click handlers trigger correct actions
- ✅ Grid responsive (2 cols → 1 col on narrow)

### Phase 3 (AI Intelligence)
- ✅ Tier selection updates immediately
- ✅ Cost estimator accurate within $0.01
- ✅ Model recommendations update < 500ms
- ✅ Menu bar shows current tier

### Phase 4 (Foreman Split)
- ✅ Chat messages display correctly
- ✅ Graph renders all nodes/edges
- ✅ Drag handle resizes smoothly
- ✅ Node selection shows details

### Phase 5 (Polish)
- ✅ No console errors/warnings
- ✅ Lighthouse score > 90
- ✅ All interactions keyboard accessible
- ✅ Test coverage > 80%

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Panel resize performance | High | Debounce resize events, use CSS transforms |
| D3.js graph performance | Medium | Limit nodes to 200, implement virtualization |
| State sync issues | High | Use single source of truth (backend), optimistic updates |
| Browser compatibility | Low | Target modern Chrome/Firefox/Safari only |

### UX Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Too many panels → cluttered | Medium | Implement Focus Mode, smart defaults |
| Keyboard shortcuts conflict | Low | Use standard VS Code shortcuts |
| Learning curve | Medium | Add onboarding tooltips, documentation |

---

## Future Enhancements (Post-MVP)

1. **Customizable Layouts**: Save/load custom panel arrangements
2. **Panel Tabs**: Multiple tabs within Foreman (Chat, Graph, Logs)
3. **Minimap**: Code minimap in Canvas (like VS Code)
4. **Themes**: Multiple color schemes (Cyber-Noir, Light Mode, etc.)
5. **Command Palette**: Fuzzy search for all actions
6. **Drag-to-Dock**: Drag cards from Studio to create floating windows

---

## Appendix

### A. File Structure

```
frontend/src/
├── lib/
│   ├── layouts/
│   │   └── MainLayout.svelte          # 4-panel system
│   ├── components/
│   │   ├── panels/
│   │   │   ├── PanelBinder.svelte
│   │   │   ├── PanelCanvas.svelte
│   │   │   ├── PanelForeman.svelte
│   │   │   └── PanelStudio.svelte
│   │   ├── studio/
│   │   │   ├── StudioCard.svelte
│   │   │   ├── AIIntelligenceCard.svelte
│   │   │   └── ToolGrid.svelte
│   │   ├── settings/
│   │   │   ├── SettingsOrchestrator.svelte
│   │   │   ├── CostEstimator.svelte
│   │   │   └── QualityTierCard.svelte
│   │   └── foreman/
│   │       ├── ForemanChat.svelte
│   │       ├── LiveGraph.svelte
│   │       └── NodeDetails.svelte
│   ├── stores/
│   │   ├── uiStore.ts
│   │   ├── orchestratorStore.ts
│   │   └── graphStore.ts
│   └── styles/
│       ├── theme.css                  # Cyber-Noir colors
│       └── animations.css
└── routes/
    └── +page.svelte                   # Main app entry
```

### B. Dependencies

```json
{
  "dependencies": {
    "svelte": "^4.2.0",
    "@sveltejs/kit": "^2.0.0",
    "svelte-splitpanes": "^0.8.0",
    "d3": "^7.8.0",
    "d3-force": "^3.0.0",
    "lucide-svelte": "^0.300.0",
    "@monaco-editor/loader": "^1.4.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0",
    "@testing-library/svelte": "^4.0.0",
    "tailwindcss": "^3.4.0"
  }
}
```

### C. References

- **UX Design Prompts**: `docs/specs/UX_DESIGN_PROMPTS.md`
- **Phase 3E Plan**: `docs/dev_logs/PHASE_3E_PHASES_3_4_IMPLEMENTATION_PLAN.md`
- **Settings Panel Spec**: `docs/specs/SETTINGS_PANEL_IMPLEMENTATION_PLAN.md`
- **Phase 3 Completion**: `docs/dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md`

---

**Document Version**: 1.0
**Last Updated**: November 25, 2025
**Status**: Ready for Implementation ✅

**Next Steps**:
1. Review and approve this plan
2. Set up frontend project structure
3. Begin Phase 1: Panel Infrastructure
4. Weekly progress reviews

---

*This is the complete technical blueprint for the Writers Factory UI. All specifications are production-ready and can be handed to any frontend developer for implementation.*
