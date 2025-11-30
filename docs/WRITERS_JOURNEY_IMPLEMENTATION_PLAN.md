# Writers Journey Implementation Plan

> From Minimal Testing to Full Experience
> **Version**: 1.0
> **Created**: November 30, 2025
> **Purpose**: Complete the "Auditor's HUD" - the visual verification layer required to fulfill the Software 3.0 promise

---

## Executive Summary

Writers Factory has achieved **100% backend completion** for the generation side of the AI workflow. However, the **verification side** - the visual tools that allow the human writer to audit AI output efficiently - remains incomplete (~20%).

This document outlines a two-track implementation plan:
- **Track A: Minimal Testing Path** (8 hours) - Enable basic Writer's Journey testing
- **Track B: Full Experience Path** (40 hours) - Complete the Iron Man HUD

The philosophy is clear: *"The success of the application depends on making the generation-verification loop go as fast as possible."* Without visual auditing tools, the writer is flying blind.

---

## Table of Contents

1. [Current State Assessment](#current-state-assessment)
2. [Track A: Minimal Testing Path](#track-a-minimal-testing-path)
3. [Track B: Full Experience Path](#track-b-full-experience-path)
4. [Implementation Details](#implementation-details)
5. [Testing Checkpoints](#testing-checkpoints)
6. [Dependencies & Prerequisites](#dependencies--prerequisites)

---

## Current State Assessment

### What Works (Generation Layer)
| Component | Status | Notes |
|-----------|--------|-------|
| Foreman Agent | ✅ Complete | All 4 modes, 8 task types |
| Story Bible Service | ✅ Complete | Parsing, validation, status |
| Voice Calibration Service | ✅ Complete | Tournament, bundle generation |
| Scene Writer Service | ✅ Complete | Structure variants, scene tournament |
| Scene Analyzer Service | ✅ Complete | 100-point scoring, 5 categories |
| Scene Enhancement Service | ✅ Complete | Action prompts, 6-pass enhancement |
| Graph Health Service | ✅ Complete | 7 health checks implemented |
| Knowledge Graph | ✅ Complete | 68 nodes, 319 edges |
| Session Persistence | ✅ Complete | SQLite-backed |
| Settings Service | ✅ Complete | 3-tier resolution |

### What's Missing (Verification Layer)
| Component | Status | Impact |
|-----------|--------|--------|
| FileTree File Loading | ❌ Broken | Writers can't open files |
| Score Display UI | ❌ Missing | Can't see 100-point breakdown |
| Variant Comparison Grid | ❌ Missing | Can't compare tournament outputs |
| Anti-Pattern Highlighting | ❌ Missing | Can't see violations in text |
| Story Bible Status Panel | ❌ Missing | Can't see ARCHITECT progress |
| Voice Tournament UI | ❌ Missing | Can't run voice calibration |
| Mode Indicator | ❌ Missing | Can't see current Foreman mode |
| Health Dashboard | ⚠️ Partial | Basic exists, needs polish |
| Keyboard Shortcuts | ❌ Missing | None implemented |

---

## Track A: Minimal Testing Path

**Goal**: Enable basic end-to-end Writer's Journey testing
**Estimated Time**: 8 hours
**Outcome**: Can test all 4 phases with basic visual feedback

### A.1: FileTree File Loading (3 hours)

**Problem**: Clicking files in FileTree doesn't load content into editor.

**Root Cause**: Tauri FS plugin integration incomplete.

**Implementation**:
```
Location: frontend/src/lib/components/FileTree/FileTree.svelte
Dependencies: @tauri-apps/plugin-fs

Tasks:
1. Import Tauri FS plugin readTextFile
2. Add click handler to file nodes
3. Read file content on click
4. Update currentFile store
5. Emit content to Editor component
6. Handle errors gracefully (file not found, permissions)
```

**Acceptance Criteria**:
- [ ] Click .md file → content appears in Editor
- [ ] Click .yaml file → content appears in Editor
- [ ] Error toast if file unreadable
- [ ] Loading indicator during read

**Files to Modify**:
- `frontend/src/lib/components/FileTree/FileTree.svelte`
- `frontend/src/lib/components/FileTree/FileTreeNode.svelte`
- `frontend/src/lib/stores.js` (add currentFileContent store)

---

### A.2: Score Display Component (2 hours)

**Problem**: After scene generation/analysis, scores exist but aren't visible.

**Implementation**:
```
Location: frontend/src/lib/components/Director/ScoreDisplay.svelte (NEW)

Tasks:
1. Create ScoreDisplay.svelte component
2. Accept SceneAnalysisResult as prop
3. Display total score with letter grade
4. Show 5-category breakdown with bars
5. List violations with severity indicators
6. Show recommended enhancement mode
```

**Component Structure**:
```svelte
<script>
  export let analysis; // SceneAnalysisResult from API
</script>

<div class="score-display">
  <div class="total-score">
    <span class="grade">{analysis.grade}</span>
    <span class="points">{analysis.total_score}/100</span>
  </div>

  <div class="category-breakdown">
    {#each Object.entries(analysis.categories) as [name, cat]}
      <div class="category">
        <span class="name">{formatName(name)}</span>
        <div class="bar" style="width: {cat.score/cat.max_score * 100}%"></div>
        <span class="score">{cat.score}/{cat.max_score}</span>
      </div>
    {/each}
  </div>

  {#if analysis.violations.length > 0}
    <div class="violations">
      <h4>Issues Found ({analysis.violations.length})</h4>
      {#each analysis.violations as v}
        <div class="violation {v.pattern_type}">
          <span class="penalty">-{v.penalty}</span>
          <span class="text">{v.matched_text}</span>
        </div>
      {/each}
    </div>
  {/if}

  <div class="recommendation">
    Mode: {analysis.recommended_mode}
  </div>
</div>
```

**Acceptance Criteria**:
- [ ] Shows letter grade prominently (A, B+, etc.)
- [ ] 5 category bars with percentages
- [ ] Violations list with penalty amounts
- [ ] Color coding (green >85, yellow 70-84, red <70)

**Files to Create/Modify**:
- `frontend/src/lib/components/Director/ScoreDisplay.svelte` (NEW)
- `frontend/src/lib/components/Director/index.js` (export)

---

### A.3: Mode Indicator (1 hour)

**Problem**: Writer doesn't know which Foreman mode they're in.

**Implementation**:
```
Location: frontend/src/lib/components/StatusBar/ModeIndicator.svelte (NEW)

Tasks:
1. Create ModeIndicator component
2. Subscribe to foremanStatus store
3. Display current mode with icon
4. Show mode-specific color
5. Tooltip with mode description
```

**Mode Colors**:
```javascript
const MODE_COLORS = {
  architect: '#3B82F6',      // Blue - building structure
  voice_calibration: '#8B5CF6', // Purple - finding voice
  director: '#10B981',       // Green - creating
  editor: '#F59E0B'          // Amber - polishing
};
```

**Component**:
```svelte
<script>
  import { foremanStatus } from '$lib/stores.js';

  const MODE_INFO = {
    architect: { icon: '🏗️', label: 'ARCHITECT', desc: 'Building Story Bible' },
    voice_calibration: { icon: '🎭', label: 'VOICE', desc: 'Calibrating Voice' },
    director: { icon: '🎬', label: 'DIRECTOR', desc: 'Drafting Scenes' },
    editor: { icon: '✨', label: 'EDITOR', desc: 'Polish & Revision' }
  };
</script>

<div class="mode-indicator" style="--mode-color: {MODE_COLORS[$foremanStatus?.mode]}">
  <span class="icon">{MODE_INFO[$foremanStatus?.mode]?.icon}</span>
  <span class="label">{MODE_INFO[$foremanStatus?.mode]?.label}</span>
</div>
```

**Acceptance Criteria**:
- [ ] Shows current mode name
- [ ] Color matches mode
- [ ] Updates when mode changes
- [ ] Tooltip explains mode

**Files to Create/Modify**:
- `frontend/src/lib/components/StatusBar/ModeIndicator.svelte` (NEW)
- `frontend/src/lib/components/StatusBar/StatusBar.svelte` (add indicator)

---

### A.4: Basic Chat Enhancement (2 hours)

**Problem**: Chat doesn't show Foreman actions or structured responses well.

**Implementation**:
```
Location: frontend/src/lib/components/Chat/ChatMessage.svelte

Tasks:
1. Detect action objects in Foreman responses
2. Render actions with special styling
3. Show save_decision actions clearly
4. Display query_notebook actions
5. Highlight mode transitions
```

**Action Rendering**:
```svelte
{#if message.action}
  <div class="foreman-action">
    {#if message.action.action === 'save_decision'}
      <div class="decision-saved">
        <span class="icon">💾</span>
        <span class="category">{message.action.category}</span>
        <span class="key">{message.action.key}</span>
        <span class="value">{message.action.value}</span>
      </div>
    {:else if message.action.action === 'advance_to_voice_calibration'}
      <div class="mode-transition">
        <span class="icon">🎭</span>
        Story Bible Complete! Advancing to Voice Calibration...
      </div>
    {:else if message.action.action === 'query_notebook'}
      <div class="notebook-query">
        <span class="icon">📓</span>
        Querying NotebookLM: {message.action.query}
      </div>
    {/if}
  </div>
{/if}
```

**Acceptance Criteria**:
- [ ] Foreman actions render distinctly
- [ ] save_decision shows category/key/value
- [ ] Mode transitions are prominent
- [ ] NotebookLM queries visible

**Files to Modify**:
- `frontend/src/lib/components/Chat/ChatMessage.svelte`
- `frontend/src/lib/components/Chat/ChatMessage.css` (styles)

---

## Track B: Full Experience Path

**Goal**: Complete the Iron Man HUD for full auditor capability
**Estimated Time**: 40 hours
**Outcome**: Full visual verification layer as designed in planning documents

### B.1: Story Bible Status Panel (4 hours)

**Purpose**: Visual checklist showing ARCHITECT mode progress.

**Location**: `frontend/src/lib/components/StoryBible/StoryBibleStatus.svelte`

**Features**:
- Collapsible panel in right sidebar
- 4 required artifacts with checkmarks
- Per-artifact detail expansion
- Completion percentage
- "Ready to Advance" indicator when complete
- Links to open each artifact file

**API Integration**:
```typescript
// GET /story-bible/status
interface StoryBibleStatus {
  phase2_complete: boolean;
  completion_score: number;
  protagonist: {
    is_valid: boolean;
    has_fatal_flaw: boolean;
    has_the_lie: boolean;
    has_arc: boolean;
  };
  beat_sheet: {
    is_valid: boolean;
    beats_defined: number;
    has_midpoint_type: boolean;
  };
  theme: {
    is_valid: boolean;
    has_central_theme: boolean;
    has_statement: boolean;
  };
  world_rules: {
    is_valid: boolean;
    rule_count: number;
  };
}
```

**UI Mockup**:
```
┌─────────────────────────────────────┐
│ 📖 STORY BIBLE                 75%  │
├─────────────────────────────────────┤
│ ✅ Protagonist.md                   │
│    ├─ ✅ Fatal Flaw                 │
│    ├─ ✅ The Lie                    │
│    └─ ✅ Character Arc              │
│                                     │
│ ⚠️ Beat_Sheet.md            10/15   │
│    ├─ ✅ Beats 1-10                 │
│    ├─ ❌ Beats 11-15                │
│    └─ ❌ Midpoint Type              │
│                                     │
│ ✅ Theme.md                         │
│    ├─ ✅ Central Theme              │
│    └─ ✅ Theme Statement            │
│                                     │
│ ❌ World_Rules.md                   │
│    └─ ❌ No rules defined           │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Complete Story Bible to unlock │ │
│ │ Voice Calibration Mode         │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Real-time status from API
- [ ] Click artifact → opens file
- [ ] Visual progress indicator
- [ ] Gate message when incomplete
- [ ] Celebration animation when complete

---

### B.2: Voice Tournament UI (8 hours)

**Purpose**: Run voice calibration tournaments visually.

**Location**: `frontend/src/lib/components/Voice/` (new directory)

**Components**:
1. `VoiceTournamentWizard.svelte` - Multi-step wizard
2. `AgentSelector.svelte` - Pick 3-5 agents
3. `TestPassageEditor.svelte` - Write/edit test passage
4. `VariantGrid.svelte` - Display all variants
5. `VariantCard.svelte` - Single variant with selection
6. `VoiceNotesEditor.svelte` - Add voice notes
7. `BundlePreview.svelte` - Preview generated bundle

**Wizard Flow**:
```
Step 1: Test Passage Design
┌─────────────────────────────────────────────────────┐
│ 🎭 Voice Calibration Tournament                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Write a key scene (~500 words) that exercises:      │
│ • Dialogue                                          │
│ • Action                                            │
│ • Interiority (internal thoughts)                   │
│ • World details                                     │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ [Monaco Editor with test passage]               │ │
│ │                                                 │ │
│ │                                                 │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│                        [Next: Select Agents →]      │
└─────────────────────────────────────────────────────┘

Step 2: Agent Selection
┌─────────────────────────────────────────────────────┐
│ Select 3-5 Agents for Tournament                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│ │ Claude   │ │ GPT-4o   │ │ DeepSeek │             │
│ │ Sonnet   │ │          │ │          │             │
│ │ [✓]      │ │ [✓]      │ │ [✓]      │             │
│ │ Voice,   │ │ Polish,  │ │ Cost-    │             │
│ │ Nuance   │ │ Structure│ │ effective│             │
│ └──────────┘ └──────────┘ └──────────┘             │
│                                                     │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│ │ Grok     │ │ Mistral  │ │ Qwen     │             │
│ │          │ │ (local)  │ │          │             │
│ │ [ ]      │ │ [ ]      │ │ [ ]      │             │
│ │ Unconv-  │ │ Free,    │ │ Fast,    │             │
│ │ entional │ │ Decent   │ │ Capable  │             │
│ └──────────┘ └──────────┘ └──────────┘             │
│                                                     │
│ Selected: 3 agents × 5 strategies = 15 variants     │
│                                                     │
│        [← Back]              [Run Tournament →]     │
└─────────────────────────────────────────────────────┘

Step 3: Variant Review
┌─────────────────────────────────────────────────────┐
│ Tournament Results: 15 Variants Generated           │
├─────────────────────────────────────────────────────┤
│ Filter: [All ▼] [Claude ▼] [ACTION ▼]               │
│                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│ │ Claude #1   │ │ Claude #2   │ │ Claude #3   │    │
│ │ ACTION      │ │ CHARACTER   │ │ DIALOGUE    │    │
│ │ ─────────── │ │ ─────────── │ │ ─────────── │    │
│ │ "She moved  │ │ "The weight │ │ "You're not │    │
│ │ through..." │ │ of years..."│ │ listening." │    │
│ │             │ │             │ │             │    │
│ │ [Preview]   │ │ [Preview]   │ │ [Select ★]  │    │
│ └─────────────┘ └─────────────┘ └─────────────┘    │
│                                                     │
│ ... (12 more variants)                              │
│                                                     │
│        [← Back]              [Confirm Selection →]  │
└─────────────────────────────────────────────────────┘

Step 4: Voice Notes
┌─────────────────────────────────────────────────────┐
│ Why does this voice work?                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Selected: Claude Sonnet #3 (DIALOGUE strategy)      │
│                                                     │
│ What specifically resonates?                        │
│ ┌─────────────────────────────────────────────────┐ │
│ │ - Sparse, deliberate dialogue                   │ │
│ │ - Heavy interiority between lines               │ │
│ │ - Metaphors drawn from nature/weather           │ │
│ │ - Short sentences for tension                   │ │
│ │ - No adverbs in dialogue tags                   │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│        [← Back]              [Generate Bundle →]    │
└─────────────────────────────────────────────────────┘

Step 5: Bundle Generated
┌─────────────────────────────────────────────────────┐
│ ✨ Voice Bundle Generated!                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Created files:                                      │
│ ✅ Voice-Gold-Standard.md                           │
│ ✅ Voice-Anti-Pattern-Sheet.md                      │
│ ✅ Phase-Evolution-Guide.md                         │
│ ✅ voice_settings.yaml                              │
│                                                     │
│ This bundle will be injected into every scene       │
│ generation call to maintain voice consistency.      │
│                                                     │
│                    [Enter Director Mode →]          │
└─────────────────────────────────────────────────────┘
```

**API Endpoints Used**:
- `GET /tournament/agents` - Available agents
- `POST /tournament/run` - Execute tournament
- `POST /tournament/select-winner` - Save selection
- `POST /voice-calibration/generate-bundle` - Create bundle

**Acceptance Criteria**:
- [ ] Multi-step wizard flow
- [ ] Agent selection with descriptions
- [ ] Tournament progress indicator
- [ ] All variants displayed in grid
- [ ] Full variant preview modal
- [ ] Selection persists
- [ ] Voice notes saved
- [ ] Bundle files created and visible

---

### B.3: Variant Comparison Grid (6 hours)

**Purpose**: Side-by-side comparison of scene tournament variants.

**Location**: `frontend/src/lib/components/Director/VariantGrid.svelte`

**Features**:
- Grid layout (3 columns default)
- Sort by: Score, Model, Strategy
- Filter by: Model, Strategy, Score range
- Expand to full preview
- Side-by-side comparison mode (2 variants)
- Hybrid selection (combine parts from multiple)

**UI Mockup**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Scene 4.1 Tournament Results                    15 variants     │
├─────────────────────────────────────────────────────────────────┤
│ Sort: [Score ▼]  Filter: [All Models ▼] [All Strategies ▼]      │
│                                                                 │
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │
│ │ Claude #2     │ │ GPT-4o #1     │ │ Claude #4     │          │
│ │ CHARACTER     │ │ BALANCED      │ │ BRAINSTORM    │          │
│ │ ══════════════│ │ ══════════════│ │ ══════════════│          │
│ │ Score: 91 A-  │ │ Score: 88 A-  │ │ Score: 87 A-  │          │
│ │               │ │               │ │               │          │
│ │ "The morning  │ │ "Rain traced  │ │ "What if she  │          │
│ │ light caught  │ │ paths down    │ │ had never     │          │
│ │ the edge of..." │ the window..." │ │ left the..."  │          │
│ │               │ │               │ │               │          │
│ │ [Expand]      │ │ [Expand]      │ │ [Expand]      │          │
│ │ [Compare]     │ │ [Compare]     │ │ [Compare]     │          │
│ │ [Select ★]    │ │ [Select ★]    │ │ [Select ★]    │          │
│ └───────────────┘ └───────────────┘ └───────────────┘          │
│                                                                 │
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │
│ │ DeepSeek #3   │ │ GPT-4o #5     │ │ DeepSeek #1   │          │
│ │ DIALOGUE      │ │ ACTION        │ │ CHARACTER     │          │
│ │ ══════════════│ │ ══════════════│ │ ══════════════│          │
│ │ Score: 84 B+  │ │ Score: 82 B+  │ │ Score: 81 B+  │          │
│ │ ...           │ │ ...           │ │ ...           │          │
│ └───────────────┘ └───────────────┘ └───────────────┘          │
│                                                                 │
│ ... (9 more variants)                                           │
│                                                                 │
│ Selected: Claude #2 (91 A-)        [Proceed to Enhancement →]   │
└─────────────────────────────────────────────────────────────────┘
```

**Comparison Mode**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Comparing: Claude #2 vs GPT-4o #1                    [× Close]  │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────┐ ┌─────────────────────────┐        │
│ │ Claude #2 - CHARACTER   │ │ GPT-4o #1 - BALANCED    │        │
│ │ Score: 91 A-            │ │ Score: 88 A-            │        │
│ ├─────────────────────────┤ ├─────────────────────────┤        │
│ │ Voice: 28/30            │ │ Voice: 26/30            │        │
│ │ Character: 19/20        │ │ Character: 18/20        │        │
│ │ Metaphor: 18/20         │ │ Metaphor: 19/20         │        │
│ │ Anti-Pattern: 14/15     │ │ Anti-Pattern: 13/15     │        │
│ │ Phase: 12/15            │ │ Phase: 12/15            │        │
│ ├─────────────────────────┤ ├─────────────────────────┤        │
│ │ The morning light       │ │ Rain traced paths down  │        │
│ │ caught the edge of      │ │ the window as she       │        │
│ │ her resolve, thin as    │ │ considered the letter   │        │
│ │ paper, ready to tear... │ │ in her hands...         │        │
│ │                         │ │                         │        │
│ │ [Full text...]          │ │ [Full text...]          │        │
│ └─────────────────────────┘ └─────────────────────────┘        │
│                                                                 │
│     [Select Left]    [Create Hybrid]    [Select Right]          │
└─────────────────────────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Grid displays all variants
- [ ] Sorting works (score, model, strategy)
- [ ] Filtering works
- [ ] Expand shows full content
- [ ] Compare mode works
- [ ] Selection saves to backend
- [ ] Proceeds to enhancement

---

### B.4: Anti-Pattern Highlighting (4 hours)

**Purpose**: Visual markers in editor showing detected anti-patterns.

**Location**: `frontend/src/lib/components/Editor/AntiPatternMarker.svelte`

**Integration**: Monaco Editor decorations API

**Features**:
- Underline violations in red/yellow
- Hover tooltip with violation details
- Gutter icons for line-level issues
- Summary panel with all violations
- Quick-fix suggestions

**Monaco Integration**:
```typescript
// Add decorations for violations
function addViolationDecorations(editor: monaco.editor.IStandaloneCodeEditor, violations: PatternViolation[]) {
  const decorations = violations.map(v => ({
    range: new monaco.Range(v.line_number, 1, v.line_number, 1000),
    options: {
      isWholeLine: false,
      className: v.pattern_type === 'zero_tolerance' ? 'violation-severe' : 'violation-warning',
      glyphMarginClassName: 'violation-glyph',
      hoverMessage: {
        value: `**${v.pattern_name}** (-${v.penalty} pts)\n\n${v.description}\n\n\`${v.matched_text}\``
      }
    }
  }));

  editor.deltaDecorations([], decorations);
}
```

**CSS Classes**:
```css
.violation-severe {
  background-color: rgba(239, 68, 68, 0.2);
  border-bottom: 2px wavy #EF4444;
}

.violation-warning {
  background-color: rgba(245, 158, 11, 0.2);
  border-bottom: 2px wavy #F59E0B;
}

.violation-glyph {
  background: url('warning-icon.svg') center center no-repeat;
}
```

**Acceptance Criteria**:
- [ ] Violations highlighted in editor
- [ ] Hover shows details
- [ ] Gutter icons for lines
- [ ] Zero-tolerance vs formulaic distinction
- [ ] Summary panel lists all

---

### B.5: Health Dashboard (6 hours)

**Purpose**: Visual manuscript health monitoring.

**Location**: `frontend/src/lib/components/Health/HealthDashboard.svelte`

**Components**:
1. `HealthDashboard.svelte` - Main container
2. `HealthScore.svelte` - Overall score gauge
3. `PacingChart.svelte` - Tension over chapters
4. `BeatProgress.svelte` - 15-beat tracking
5. `FlawTracker.svelte` - Fatal flaw challenges
6. `ThreadTracker.svelte` - Dropped thread detection
7. `SymbolResonance.svelte` - Theme/symbol tracking

**Dashboard Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ 📊 MANUSCRIPT HEALTH                           Overall: 82/100  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ PACING ANALYSIS                                             │ │
│ │                                                             │ │
│ │ Tension  ▲                                                  │ │
│ │    10 ─  │     ╱╲         ╱╲                                │ │
│ │     8 ─  │   ╱    ╲     ╱    ╲    ╱                         │ │
│ │     6 ─  │  ╱      ╲   ╱      ╲  ╱                          │ │
│ │     4 ─  │ ╱        ╲ ╱        ╲╱                           │ │
│ │     2 ─  │╱          ╳                                      │ │
│ │     0 ─  └───────────────────────────────────────►          │ │
│ │          Ch1  Ch2  Ch3  Ch4  Ch5  Ch6  Ch7  Ch8             │ │
│ │                                                             │ │
│ │ ⚠️ Pacing Plateau detected: Chapters 4-6 (flat tension)     │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌───────────────────────┐ ┌───────────────────────┐            │
│ │ BEAT PROGRESS         │ │ FATAL FLAW TRACKER    │            │
│ │ ═══════════════════   │ │ ═══════════════════   │            │
│ │ ✅ 1. Opening Image   │ │ Last challenged: Ch 3 │            │
│ │ ✅ 2. Theme Stated    │ │ Scenes since: 8       │            │
│ │ ✅ 3. Setup           │ │ ⚠️ Due for test       │            │
│ │ ✅ 4. Catalyst        │ │                       │            │
│ │ ✅ 5. Debate          │ │ Challenges:           │            │
│ │ ✅ 6. Break into Two  │ │ Ch 1: Introduced      │            │
│ │ 🔄 7. B Story (now)   │ │ Ch 2: Tested (failed) │            │
│ │ ⬜ 8. Fun & Games     │ │ Ch 3: Tested (resisted)│           │
│ │ ⬜ 9. Midpoint        │ │                       │            │
│ │ ⬜ 10-15...           │ │                       │            │
│ │                       │ │                       │            │
│ │ Progress: 46% ████░░░ │ │ Status: NEEDS TEST    │            │
│ └───────────────────────┘ └───────────────────────┘            │
│                                                                 │
│ ┌───────────────────────┐ ┌───────────────────────┐            │
│ │ DROPPED THREADS       │ │ THEME RESONANCE       │            │
│ │ ═══════════════════   │ │ ═══════════════════   │            │
│ │ ⚠️ 2 potential drops  │ │ Central: "Cost of    │            │
│ │                       │ │ vengeance"            │            │
│ │ 1. "The letter from   │ │                       │            │
│ │    Marcus" (Ch 2)     │ │ Resonance at beats:   │            │
│ │    - Not referenced   │ │ ✅ Catalyst: 8/10     │            │
│ │      in 4 chapters    │ │ ✅ Midpoint: 9/10     │            │
│ │                       │ │ ⬜ All Is Lost: TBD   │            │
│ │ 2. "The broken watch" │ │ ⬜ Finale: TBD        │            │
│ │    (Ch 3)             │ │                       │            │
│ │    - Symbol unused    │ │ Overall: 8.5/10      │            │
│ └───────────────────────┘ └───────────────────────┘            │
│                                                                 │
│                              [Run Full Health Check] [Export]   │
└─────────────────────────────────────────────────────────────────┘
```

**API Endpoints**:
- `GET /health/dashboard` - All health metrics
- `POST /health/check` - Run specific check
- `GET /health/trends` - Historical data

**Acceptance Criteria**:
- [ ] Pacing chart renders
- [ ] Beat progress accurate
- [ ] Flaw tracker shows last challenge
- [ ] Thread detection works
- [ ] Symbol/theme resonance shown
- [ ] Warnings highlighted
- [ ] Export to markdown

---

### B.6: Keyboard Shortcuts (4 hours)

**Purpose**: Implement documented shortcuts for power users.

**Location**: `frontend/src/lib/shortcuts.ts` (NEW)

**Shortcuts to Implement**:
| Shortcut | Action | Priority |
|----------|--------|----------|
| `Cmd+K` | Open command palette | HIGH |
| `Cmd+S` | Save current file | HIGH |
| `Cmd+Shift+S` | Save all | MEDIUM |
| `Cmd+\` | Toggle right sidebar | HIGH |
| `Cmd+B` | Toggle left sidebar (file tree) | HIGH |
| `Cmd+J` | Toggle bottom panel (chat) | HIGH |
| `Escape` | Close any modal/palette | HIGH |
| `Cmd+Shift+A` | Ask agent about selection | HIGH |
| `Cmd+Shift+G` | Look up in Knowledge Graph | MEDIUM |
| `Cmd+Enter` | Send chat message | HIGH |
| `Cmd+/` | Toggle comment in editor | LOW |

**Implementation**:
```typescript
// frontend/src/lib/shortcuts.ts
import { writable } from 'svelte/store';

export const shortcuts = {
  'cmd+k': () => commandPalette.open(),
  'cmd+s': () => saveCurrentFile(),
  'cmd+shift+s': () => saveAllFiles(),
  'cmd+\\': () => toggleRightSidebar(),
  'cmd+b': () => toggleLeftSidebar(),
  'cmd+j': () => toggleBottomPanel(),
  'escape': () => closeActiveModal(),
  'cmd+shift+a': () => askAgentAboutSelection(),
  'cmd+shift+g': () => lookupInGraph(),
  'cmd+enter': () => sendChatMessage(),
};

export function initShortcuts() {
  document.addEventListener('keydown', (e) => {
    const key = buildKeyString(e);
    if (shortcuts[key]) {
      e.preventDefault();
      shortcuts[key]();
    }
  });
}

function buildKeyString(e: KeyboardEvent): string {
  const parts = [];
  if (e.metaKey || e.ctrlKey) parts.push('cmd');
  if (e.shiftKey) parts.push('shift');
  if (e.altKey) parts.push('alt');
  parts.push(e.key.toLowerCase());
  return parts.join('+');
}
```

**Acceptance Criteria**:
- [ ] All HIGH priority shortcuts work
- [ ] No conflicts with browser defaults
- [ ] Visual feedback on shortcut use
- [ ] Shortcut hints in tooltips
- [ ] Help modal lists all shortcuts

---

### B.7: Work Orders UI (8 hours)

**Purpose**: Visual interface for Foreman task tracking.

**Location**: `frontend/src/lib/components/WorkOrders/`

**Components**:
1. `WorkOrderPanel.svelte` - Main panel
2. `WorkOrderCard.svelte` - Individual task card
3. `TaskTimeline.svelte` - Visual progress timeline
4. `TemplateStatus.svelte` - Story Bible template completion

**Features**:
- Current task prominently displayed
- Completed tasks with checkmarks
- Pending tasks grayed out
- Template completion tracking
- Time estimates (optional)
- Conversation link to relevant chat

**UI Mockup**:
```
┌─────────────────────────────────────────────────────────────────┐
│ 📋 WORK ORDER: "The Midnight Garden"                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Current Mode: ARCHITECT                      Progress: 65%      │
│ ══════════════════════════════════════════════░░░░░░░░░░░░░░░░ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🔄 CURRENT TASK                                             │ │
│ │ ─────────────────────────────────────────────────────────── │ │
│ │ Define Beat Sheet - Midpoint Type                           │ │
│ │                                                             │ │
│ │ The Foreman needs to know: Will your midpoint be a         │ │
│ │ FALSE VICTORY (things seem good, then collapse) or a       │ │
│ │ FALSE DEFEAT (things seem hopeless, then turn around)?     │ │
│ │                                                             │ │
│ │                                    [Continue in Chat →]     │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ✅ COMPLETED                                                    │
│ ├─ ✅ Protagonist: Fatal Flaw defined                          │
│ ├─ ✅ Protagonist: The Lie defined                             │
│ ├─ ✅ Protagonist: Arc mapped                                  │
│ ├─ ✅ Theme: Central theme defined                             │
│ ├─ ✅ Theme: Theme statement written                           │
│ ├─ ✅ Beat Sheet: Beats 1-9 defined                            │
│ └─ ✅ World Rules: 3 rules defined                             │
│                                                                 │
│ ⬜ PENDING                                                      │
│ ├─ ⬜ Beat Sheet: Beats 10-15                                   │
│ ├─ ⬜ Beat Sheet: Midpoint type selection                       │
│ └─ ⬜ Cast: Supporting characters                               │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Template Status                                             │ │
│ │ ┌────────────┬────────────┬────────────┬────────────┐      │ │
│ │ │ Protagonist│ Beat Sheet │   Theme    │World Rules │      │ │
│ │ │    ✅      │    🔄      │    ✅      │    ✅      │      │ │
│ │ │  100%      │   60%      │   100%     │   100%     │      │ │
│ │ └────────────┴────────────┴────────────┴────────────┘      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**API Integration**:
```typescript
// GET /foreman/status
interface ForemanStatus {
  mode: 'architect' | 'voice_calibration' | 'director' | 'editor';
  work_order: {
    project_title: string;
    protagonist_name: string;
    templates_completed: string[];
    templates_pending: string[];
    current_task: string;
    current_task_description: string;
  };
  kb_entries: number;
  conversation_length: number;
}
```

**Acceptance Criteria**:
- [ ] Current task prominent
- [ ] Completed tasks listed
- [ ] Pending tasks shown
- [ ] Template status visual
- [ ] Progress percentage
- [ ] Link to relevant chat

---

## Implementation Details

### Shared Components Needed

#### 1. ProgressBar.svelte
```svelte
<script>
  export let value = 0;
  export let max = 100;
  export let color = '#10B981';
  export let showLabel = true;
</script>

<div class="progress-container">
  <div class="progress-bar" style="width: {(value/max)*100}%; background: {color}"></div>
  {#if showLabel}
    <span class="progress-label">{Math.round((value/max)*100)}%</span>
  {/if}
</div>
```

#### 2. ScoreGauge.svelte
```svelte
<script>
  export let score = 0;
  export let grade = 'C';

  const getColor = (s) => {
    if (s >= 85) return '#10B981'; // Green
    if (s >= 70) return '#F59E0B'; // Amber
    return '#EF4444'; // Red
  };
</script>

<div class="score-gauge">
  <svg viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="45" fill="none" stroke="#E5E7EB" stroke-width="8"/>
    <circle cx="50" cy="50" r="45" fill="none" stroke={getColor(score)} stroke-width="8"
            stroke-dasharray="{score * 2.83} 283" transform="rotate(-90 50 50)"/>
  </svg>
  <div class="score-text">
    <span class="grade">{grade}</span>
    <span class="points">{score}</span>
  </div>
</div>
```

#### 3. Toast Notifications
```svelte
<!-- Already exists, ensure it supports: success, warning, error, info -->
```

### State Management Updates

#### stores.js Additions
```javascript
// Add to frontend/src/lib/stores.js

// Foreman status (polled every 5s)
export const foremanStatus = writable(null);

// Current file content
export const currentFileContent = writable('');

// Active violations in editor
export const editorViolations = writable([]);

// Tournament state
export const tournamentState = writable({
  isRunning: false,
  progress: 0,
  variants: [],
  selectedVariant: null
});

// Health check results
export const healthResults = writable(null);
```

### API Client Additions

```typescript
// Add to frontend/src/lib/api_client.ts

// Foreman
export async function getForemanStatus(): Promise<ForemanStatus> {
  return fetch(`${API_BASE}/foreman/status`).then(r => r.json());
}

// Story Bible
export async function getStoryBibleStatus(): Promise<StoryBibleStatus> {
  return fetch(`${API_BASE}/story-bible/status`).then(r => r.json());
}

// Tournament
export async function runTournament(params: TournamentParams): Promise<TournamentResult> {
  return fetch(`${API_BASE}/tournament/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  }).then(r => r.json());
}

// Scene Analysis
export async function analyzeScene(sceneContent: string): Promise<SceneAnalysisResult> {
  return fetch(`${API_BASE}/director/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: sceneContent })
  }).then(r => r.json());
}

// Health
export async function getHealthDashboard(): Promise<HealthDashboard> {
  return fetch(`${API_BASE}/health/dashboard`).then(r => r.json());
}
```

---

## Testing Checkpoints

### After Track A (Minimal)
- [ ] Can click file → loads in editor
- [ ] Can see score after scene analysis
- [ ] Can see current Foreman mode
- [ ] Can see Foreman actions in chat
- [ ] Basic end-to-end journey possible

### After Track B (Full)
- [ ] Can see Story Bible completion status
- [ ] Can run voice tournament visually
- [ ] Can compare scene variants
- [ ] Can see anti-patterns in editor
- [ ] Can view health dashboard
- [ ] Keyboard shortcuts work
- [ ] Work orders visible

### Full Journey Test Script
```
1. Launch app fresh
2. Complete onboarding (4 steps)
3. Create new project "Test Novel"
4. ARCHITECT mode:
   - Define protagonist via chat
   - See decisions saved in Work Order
   - Complete Beat Sheet
   - See Story Bible status update
   - Get gate message → advance
5. VOICE_CALIBRATION mode:
   - Write test passage
   - Select agents
   - Run tournament
   - Compare variants in grid
   - Select winner
   - See bundle generated
   - Advance to Director
6. DIRECTOR mode:
   - See draft summary
   - Generate scaffold
   - Run scene tournament
   - Compare variants
   - See scores with breakdown
   - Select winner
   - See anti-patterns highlighted
   - Run enhancement
   - See improved score
   - Run health check
7. EDITOR mode:
   - View health dashboard
   - Address flagged issues
   - Final health check
```

---

## Dependencies & Prerequisites

### Frontend Dependencies (Already Installed)
- `@tauri-apps/plugin-fs` - File system access
- `monaco-editor` - Code editor
- `chart.js` - For pacing charts (may need to add)

### Backend Prerequisites (All Complete)
- All services implemented
- All endpoints functional
- SQLite databases ready

### Environment
- Ollama running with `llama3.2:3b` and `mistral:7b`
- At least one cloud API key configured

---

## Timeline Estimate

| Track | Component | Hours | Dependencies |
|-------|-----------|-------|--------------|
| A | FileTree Loading | 3 | None |
| A | Score Display | 2 | None |
| A | Mode Indicator | 1 | None |
| A | Chat Enhancement | 2 | None |
| **A Total** | | **8** | |
| B | Story Bible Panel | 4 | Track A |
| B | Voice Tournament UI | 8 | Track A |
| B | Variant Grid | 6 | Track A |
| B | Anti-Pattern Highlighting | 4 | Score Display |
| B | Health Dashboard | 6 | Track A |
| B | Keyboard Shortcuts | 4 | Track A |
| B | Work Orders UI | 8 | Track A |
| **B Total** | | **40** | |
| **Grand Total** | | **48** | |

---

## Success Criteria

The implementation is complete when:

1. **The Writer's Journey is testable** - A writer can go from installation to polished scene
2. **Visual auditing is fast** - Scores, variants, violations visible at a glance
3. **Gates enforce methodology** - Can't skip phases
4. **The HUD is complete** - Mode, progress, health all visible
5. **Power users can fly** - Keyboard shortcuts work

---

*Document created by Claude (eloquent-raman agent) as the Writers Journey specialist.*
*Ready for implementation assignment to development agents.*
