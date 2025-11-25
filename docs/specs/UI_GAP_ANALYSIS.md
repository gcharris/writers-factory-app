# UI Implementation - Comprehensive Gap Analysis

**Date**: November 25, 2025
**Status**: Pre-Implementation Audit
**Purpose**: Identify all backend features requiring UI components

---

## Executive Summary

**Current State**: The UI_IMPLEMENTATION_PLAN.md focuses on **infrastructure** (4-panel layout, Studio cards, basic AI Intelligence) but is **missing 60+ UI components** needed to activate all backend services.

**Backend Reality**: 88 API endpoints across 12 major categories, requiring comprehensive UI coverage for:
- Story Bible creation workflow (Architect mode)
- Voice calibration tournament (25 variants)
- Director mode scene creation (16 endpoints)
- Graph health checks (7 categories)
- Complete settings configuration (11 categories)
- Session/metabolism management
- Knowledge graph visualization

**Gap Severity**: **HIGH** - The current plan would result in a beautiful panel system with no way to access most features.

---

## Complete Backend Inventory

### Category 1: Story Bible System (ARCHITECT Mode)
**Backend Endpoints** (7):
- `GET /story-bible/status` - Validation status
- `POST /story-bible/scaffold` - Create scaffolding
- `GET /story-bible/protagonist` - Parsed protagonist data
- `GET /story-bible/beat-sheet` - Parsed beat sheet
- `POST /story-bible/ensure-structure` - Directory creation
- `GET /story-bible/can-execute` - Phase 3 readiness
- `POST /story-bible/smart-scaffold` - AI-powered generation

**UI Components Required** (MISSING):
1. **StoryBibleWizard.svelte** - Main creation interface
   - Template progress tracker (4 templates with status icons)
   - NotebookLM notebook registration modal
   - Multi-notebook role assignment (World/Voice/Craft dropdowns)
   - Template validation status display
   - "Continue to Voice Calibration" gating logic

2. **TemplateEditor.svelte** - In-context template editing
   - Protagonist: Fatal Flaw, The Lie, Arc fields with validation
   - Beat Sheet: 15-beat checklist with percentage targets
   - Theme: Central theme + statement fields
   - World Rules: Fundamental constraints editor

3. **NotebookRegistration.svelte** - Multi-notebook orchestration
   - Add notebook button → NotebookLM auth flow
   - Notebook list with role assignments (dropdown: World/Voice/Craft)
   - Test query button per notebook
   - Export to Project Notebook trigger

**Current Plan Coverage**: ❌ NOT MENTIONED

---

### Category 2: Voice Calibration (VOICE_CALIBRATION Mode)
**Backend Endpoints** (7):
- `GET /voice-calibration/agents` - Available agents
- `POST /voice-calibration/tournament/start` - Launch tournament
- `GET /voice-calibration/tournament/{id}/status` - Tournament status
- `GET /voice-calibration/tournament/{id}/variants` - Get 25 variants
- `POST /voice-calibration/tournament/{id}/select` - Select winner
- `POST /voice-calibration/generate-bundle/{project_id}` - Create Voice Bundle
- `GET /voice-calibration/{project_id}` - Get calibration data

**UI Components Required** (MISSING):
1. **VoiceTournamentLauncher.svelte** - Tournament setup
   - Test text input (200-500 words)
   - Agent selection checkboxes (Claude, GPT-4o, Gemini, Grok, DeepSeek)
   - Strategy selection (5 strategies: ACTION, CHARACTER, DIALOGUE, ATMOSPHERIC, BALANCED)
   - "Launch Tournament" button with loading state

2. **VoiceVariantGrid.svelte** - 25-variant display
   - 5×5 grid layout (agents × strategies)
   - Card per variant with:
     - Agent name + strategy badge
     - Preview (first 150 words)
     - "Select as Winner" button
     - "Add to Reference" checkbox
   - Side-by-side comparison mode (2-3 variants)
   - Filter by agent or strategy

3. **VoiceBundlePreview.svelte** - Generated bundle display
   - Shows Gold Standard reference
   - Shows Anti-Patterns list
   - Shows Phase Evolution guidance
   - "Export to NotebookLM Project Notebook" button

**Current Plan Coverage**: ✅ Mentioned in Studio Panel as "Voice Tournament" card, but NO detail on variant display/selection UI

---

### Category 3: Director Mode (DIRECTOR Mode)
**Backend Endpoints** (16):

#### 3A: Scaffold Generation (3 endpoints)
- `POST /director/scaffold/draft-summary` - Stage 1 draft
- `POST /director/scaffold/enrich` - NotebookLM enrichment
- `POST /director/scaffold/generate` - Stage 2 full scaffold

**Missing UI**:
1. **ScaffoldGenerator.svelte** - 2-stage flow UI
   - Stage 1: Draft summary display with enrichment suggestions
   - Enrichment modal: Select notebook + customize query
   - Stage 2: Full scaffold preview (Chapter Overview, Strategic Context, Success Criteria, Continuity)
   - "Use This Scaffold" button → pass to Scene Writer

#### 3B: Scene Writing (4 endpoints)
- `POST /director/scene/structure-variants` - Generate 5 structures
- `POST /director/scene/generate-variants` - Generate 15+ prose variants
- `POST /director/scene/create-hybrid` - Merge best elements
- `POST /director/scene/quick-generate` - Single-model fast draft

**Missing UI**:
2. **SceneStructureSelector.svelte** - Layout selection
   - 5 structure cards (different chapter opening strategies)
   - Preview: "Opens with dialogue" vs "Opens with action"
   - Select one → pass to variant generation

3. **SceneVariantTournament.svelte** - 15+ variant display
   - 3 models × 5 strategies = 15 variants (default)
   - Grid layout with score badges
   - Sort by score / agent / strategy
   - Expand variant → full text + detailed score breakdown
   - "Select Winner" or "Create Hybrid" buttons

4. **HybridSceneCreator.svelte** - Merge UI
   - Select 2-3 variants to merge
   - Specify what to take from each: "Opening from Variant A, dialogue from Variant B"
   - LLM generates hybrid
   - Preview → accept/reject

#### 3C: Scene Analysis (4 endpoints)
- `POST /director/scene/analyze` - Full 5-category score
- `POST /director/scene/compare` - Compare multiple variants
- `POST /director/scene/detect-patterns` - Anti-pattern detection only
- `POST /director/scene/analyze-metaphors` - Metaphor analysis only

**Missing UI**:
5. **SceneScorecard.svelte** - Detailed score display
   - 5-category breakdown (Voice 30, Character 20, Metaphor 20, Anti-Pattern 15, Phase 15)
   - Visual progress bars per category
   - Drill-down: Click category → see specific violations
   - Grade badge (A, A-, B+, etc.)
   - Comparison mode: Side-by-side scores for 2+ scenes

6. **AntiPatternDetector.svelte** - Violation list
   - Table: Pattern | Line Number | Severity | Fix Suggestion
   - Filter by severity (zero-tolerance vs formulaic)
   - "Ignore This Instance" button (one-time override)

7. **MetaphorAnalyzer.svelte** - Domain visualization
   - Pie chart: Domain distribution (Gambling 35%, Violence 25%, etc.)
   - Saturation warnings (red if > threshold)
   - Simile count with tolerance indicator
   - Domain list with examples from text

#### 3D: Scene Enhancement (4 endpoints)
- `POST /director/scene/enhance` - Auto-select enhancement mode
- `POST /director/scene/action-prompt` - Generate surgical fixes
- `POST /director/scene/apply-fixes` - Apply action prompt
- `POST /director/scene/six-pass` - Full 6-pass enhancement

**Missing UI**:
8. **EnhancementPipeline.svelte** - Enhancement workflow
   - Score display → recommended enhancement mode
   - Action Prompt mode (85+): Shows OLD → NEW fixes, checkboxes to apply
   - 6-Pass mode (70-84): Progress indicator (Pass 1/6: Sensory Anchoring...)
   - Rewrite mode (<70): "Score too low, rewrite recommended" message
   - Before/after diff view
   - "Accept Changes" / "Reject" buttons

**Current Plan Coverage**: ❌ Director Mode completely absent from current plan

---

### Category 4: Graph Health Checks (Phase 3D)
**Backend Endpoints** (7):
- `POST /health/check` - Run health check
- `GET /health/report/{report_id}` - Retrieve report
- `POST /health/export` - Export as markdown/JSON
- `GET /health/trends/{metric}` - Historical trends
- `POST /health/theme/override` - Manual theme score
- `GET /health/theme/overrides` - List overrides
- `GET /health/status` - Combined dashboard status

**UI Components Required** (PARTIALLY MISSING):
1. **HealthDashboard.svelte** - Overview panel (EXISTS but needs expansion)
   - Current: Shows basic graph stats + conflicts
   - **Missing**:
     - 7 health check cards (Timeline, Theme, Flaw, Cast, Pacing, Beats, Symbols)
     - Severity indicators (✓ Pass, ⚠️ Warning, ❌ Error)
     - "Run Health Check" button (on-demand trigger)
     - Last check timestamp

2. **HealthReportViewer.svelte** - Detailed report display (MISSING)
   - Full report with all 7 categories
   - Warning/error list with line numbers
   - Recommendations per issue
   - Export button (markdown/JSON)
   - Historical comparison ("Better than last check?")

3. **HealthTrendsChart.svelte** - Longitudinal analysis (MISSING)
   - Line charts for: Pacing trends, Theme scores over time, Flaw challenge frequency
   - Date range selector
   - Metric selector dropdown
   - Export chart as PNG

4. **ThemeOverrideModal.svelte** - Manual score override (MISSING)
   - Beat selector + current LLM score
   - Manual score input (0-10)
   - Explanation text area
   - "Override" button

**Current Plan Coverage**: ⚠️ Mentioned "HealthDashboard" but missing 3 critical sub-components

---

### Category 5: Settings Configuration (Phase 3C/5)
**Backend Endpoints** (8):
- `GET /settings/{key}` - Get single setting
- `POST /settings` - Set value
- `DELETE /settings/{key}` - Reset to default
- `GET /settings/category/{category}` - Get category
- `GET /settings/project/{project_id}/overrides` - Project overrides
- `GET /settings/export` - Export YAML
- `POST /settings/import` - Import YAML
- `GET /settings/defaults` - Get all defaults

**UI Components Required** (COMPLETELY MISSING):
**Main Component**: `SettingsPanel.svelte` - Modal with sidebar navigation

**11 Sub-Components** (per SETTINGS_PANEL_IMPLEMENTATION_PLAN.md):
1. **SettingsAgents.svelte** - API keys + model selection
2. **SettingsScoring.svelte** - Rubric weights with linked sliders
3. **SettingsVoice.svelte** - Voice strictness levels
4. **SettingsMetaphor.svelte** - Metaphor discipline thresholds
5. **SettingsAntiPatterns.svelte** - Zero-tolerance patterns + custom
6. **SettingsEnhancement.svelte** - Enhancement thresholds
7. **SettingsForeman.svelte** - Foreman behavior
8. **SettingsOrchestrator.svelte** - Model orchestrator (Phase 3E)
9. **SettingsTournament.svelte** - Multi-model tournament config
10. **SettingsHealth.svelte** - Health check thresholds
11. **SettingsAdvanced.svelte** - RAG strategy, file watching

**Shared Sub-Components** (5):
- `SettingSlider.svelte` - Numerical ranges
- `SettingDropdown.svelte` - Discrete options
- `SettingToggle.svelte` - Boolean flags
- `SettingSecret.svelte` - API keys (mask/unmask/test)
- `CostEstimator.svelte` - Real-time spend widget

**Current Plan Coverage**: ⚠️ Only mentions SettingsOrchestrator.svelte in Phase 3, missing all other 10 sub-components

---

### Category 6: Model Orchestrator (Phase 3E - Phase 3)
**Backend Endpoints** (4):
- `GET /orchestrator/capabilities` - Model registry
- `POST /orchestrator/estimate-cost` - Cost estimation
- `GET /orchestrator/recommendations/{task_type}` - Tier recommendations
- `GET /orchestrator/current-spend` - Current spend

**UI Components Required**:
1. **SettingsOrchestrator.svelte** (~200 lines) - ✅ IN PLAN
2. **CostEstimator.svelte** (~100 lines) - ✅ IN PLAN
3. **QualityTierCard.svelte** (~80 lines) - ✅ IN PLAN
4. **ModelRecommendationsPreview.svelte** (MISSING)
   - Table: Task Type | Budget | Balanced | Premium
   - Shows which model selected for each tier
   - Updates dynamically on tier change

**Current Plan Coverage**: ✅ GOOD (but missing recommendations preview)

---

### Category 7: Foreman Chat Interface
**Backend Endpoints** (9):
- `POST /foreman/start` - Initialize project
- `POST /foreman/chat` - Chat message
- `POST /foreman/notebook` - Register notebook
- `GET /foreman/status` - Get status
- `POST /foreman/flush-kb` - Flush KB
- `POST /foreman/reset` - Reset
- `GET /foreman/mode` - Get mode
- `POST /foreman/mode/voice-calibration` - Advance to Voice Calibration
- `POST /foreman/mode/director` - Advance to Director

**UI Components Required** (PARTIALLY MISSING):
1. **ForemanChat.svelte** - ✅ IN PLAN (Phase 4)
2. **ForemanModeIndicator.svelte** (MISSING)
   - Shows current mode: ARCHITECT / VOICE_CALIBRATION / DIRECTOR / EDITOR
   - Mode-specific UI context (e.g., in ARCHITECT mode, show template progress)
3. **WorkOrderTracker.svelte** (MISSING)
   - Template checklist with status icons (□ Not Started, ◐ In Progress, ✓ Complete)
   - Completion percentage progress bar
   - Mode transition buttons ("Ready for Voice Calibration")

**Current Plan Coverage**: ⚠️ Chat interface planned, but mode-specific UI missing

---

### Category 8: Knowledge Graph
**Backend Endpoints** (6):
- `POST /graph/ingest` - Ingest content
- `POST /graph/ingest/test` - Test ingestor
- `GET /graph/view` - View graph data
- `POST /graph/consolidate/{session_id}` - Consolidate session
- `POST /graph/consolidate` - Consolidate all
- `GET /graph/conflicts` - View conflicts

**UI Components Required** (PARTIALLY MISSING):
1. **LiveGraph.svelte** - ✅ IN PLAN (Phase 4, D3.js force-directed graph)
2. **GraphConflictResolver.svelte** (MISSING)
   - Conflict list: "Character age: 25 vs 30"
   - Source references per conflict
   - Resolution buttons: "Use First" / "Use Second" / "Manual Edit"
   - Bulk resolution tools
3. **GraphIngestTrigger.svelte** (MISSING)
   - "Re-ingest Story Bible" button
   - Progress indicator during ingestion
   - Success/failure toast notifications
4. **NodeDetailsPanel.svelte** (MISSING)
   - Clicked node → show full entity data
   - Related nodes/edges
   - Edit node data (advanced)

**Current Plan Coverage**: ⚠️ Graph visualization planned, but conflict resolution + node details missing

---

### Category 9: Session Management
**Backend Endpoints** (7):
- `POST /session/new` - Create session
- `POST /session/{session_id}/message` - Log message
- `GET /session/{session_id}/history` - Get history
- `GET /session/{session_id}/stats` - Get stats
- `GET /sessions/active` - List active
- `GET /session/{session_id}/uncommitted` - Uncommitted events
- `POST /session/commit` - Mark committed

**UI Components Required** (MISSING):
1. **SessionSwitcher.svelte** - Session management
   - Dropdown: Active sessions list
   - "New Session" button
   - Current session indicator in status bar
2. **SessionHistory.svelte** - Chat history browser
   - Searchable message list
   - Timestamp + speaker (user/foreman/agent)
   - Export session button
3. **UncommittedEventsIndicator.svelte** - Metabolism reminder
   - Badge count: "3 uncommitted"
   - Click → trigger consolidation
   - Auto-hide when count = 0

**Current Plan Coverage**: ❌ NOT MENTIONED

---

### Category 10: Metabolism (Consolidator)
**Backend Endpoints** (2):
- `POST /metabolism/consolidate-kb` - Consolidate all
- `POST /metabolism/consolidate-kb/{project_id}` - Consolidate project

**UI Components Required** (PARTIALLY MISSING):
1. **MetabolismCard.svelte** - ✅ Mentioned in Studio Panel
2. **ConsolidationProgress.svelte** (MISSING)
   - Shows KB entries being processed
   - Progress bar: "Processing 5/12 entries"
   - Success/failure indicators
3. **KBEntriesViewer.svelte** (MISSING)
   - List of Foreman KB entries awaiting consolidation
   - Preview content
   - Manual approval before consolidation (optional)

**Current Plan Coverage**: ⚠️ Card exists, but no detail on consolidation flow UI

---

### Category 11: NotebookLM Integration
**Backend Endpoints** (7):
- `GET /notebooklm/status` - Connection status
- `GET /notebooklm/auth` - Trigger auth
- `GET /notebooklm/notebooks` - List configured
- `POST /notebooklm/query` - Query notebook
- `POST /notebooklm/character-profile` - Extract character
- `POST /notebooklm/world-building` - Extract world details
- `POST /notebooklm/context` - Get context for entity

**UI Components Required** (MISSING):
1. **NotebookLMConfig.svelte** - Configuration panel
   - Connection status indicator
   - "Authenticate with Google" button → auth flow
   - List of configured notebooks (ID, name, role)
   - "Add Notebook" button
   - Test query per notebook

2. **NotebookQueryModal.svelte** - Query interface
   - Notebook selector dropdown
   - Query text input
   - Submit button → display answer
   - History of recent queries

3. **NotebookEnrichmentSuggestions.svelte** - Context-aware prompts
   - Shows suggested queries based on current context
   - Example: "Query World notebook about the gambling den"
   - Click suggestion → auto-fill query modal

**Current Plan Coverage**: ❌ NOT MENTIONED

---

### Category 12: File Management
**Backend Endpoints** (2):
- `GET /files/{filepath:path}` - Read file
- `PUT /files/{filepath:path}` - Save file

**UI Components Required**:
1. **PanelBinder.svelte** - ✅ IN PLAN (file tree)
2. **PanelCanvas.svelte** - ✅ IN PLAN (Monaco editor)

**Current Plan Coverage**: ✅ COMPLETE

---

### Category 13: Legacy/Tournament
**Backend Endpoints** (3):
- `GET /agents` - List agents
- `GET /manager/status` - Manager status
- `POST /tournament/run` - Run tournament

**UI Components Required**:
- Likely legacy, may not need dedicated UI (superseded by Voice Calibration)

---

## Gap Summary Table

| Category | Backend Endpoints | UI Components Planned | UI Components Missing | Coverage |
|----------|-------------------|----------------------|---------------------|----------|
| Story Bible (Architect) | 7 | 0 | 3 major | ❌ 0% |
| Voice Calibration | 7 | 1 (card only) | 3 major | 🔴 20% |
| Director Mode | 16 | 0 | 8 major | ❌ 0% |
| Graph Health | 7 | 1 (basic) | 4 major | 🔴 25% |
| Settings | 8 | 1 (orchestrator) | 10 major | 🔴 10% |
| Model Orchestrator | 4 | 3 | 1 minor | ✅ 75% |
| Foreman Chat | 9 | 1 (chat UI) | 2 major | 🔴 33% |
| Knowledge Graph | 6 | 1 (graph viz) | 3 major | 🔴 25% |
| Session Management | 7 | 0 | 3 major | ❌ 0% |
| Metabolism | 2 | 1 (card only) | 2 major | 🔴 33% |
| NotebookLM | 7 | 0 | 3 major | ❌ 0% |
| File Management | 2 | 2 | 0 | ✅ 100% |

**Overall Coverage**: ~20% (infrastructure + 2 features vs. 12 feature categories)

---

## Critical Insights

### 1. **Infrastructure vs. Features**
The current UI_IMPLEMENTATION_PLAN.md focuses on:
- ✅ 4-panel layout system (excellent infrastructure)
- ✅ Collapsibility, resizing, keyboard shortcuts (great UX)
- ✅ Model Orchestrator settings (1 feature complete)
- ❌ Missing: 11 other feature categories

### 2. **The "Studio Panel" Problem**
Current plan shows Studio Panel with cards for:
- Voice Tournament ✓
- Scaffold Generator ✓
- Health Check ✓
- Metabolism ✓
- AI Intelligence ✓

**But cards are just LAUNCHERS** - clicking a card needs to open the actual UI!

**Example**: "Voice Tournament" card exists, but:
- No UI to launch tournament
- No UI to display 25 variants
- No UI to select winner
- No UI to preview Voice Bundle

### 3. **Settings Panel Critical Gap**
The SETTINGS_PANEL_IMPLEMENTATION_PLAN.md exists with complete specs for 11 sub-components, but UI_IMPLEMENTATION_PLAN.md only mentions SettingsOrchestrator.svelte (1 of 11).

**Missing 10 settings sub-components**:
- SettingsAgents (API keys - blocking feature!)
- SettingsScoring (rubric weights)
- SettingsVoice (strictness levels)
- SettingsMetaphor (domain saturation)
- SettingsAntiPatterns (pattern management)
- SettingsEnhancement (thresholds)
- SettingsForeman (behavior)
- SettingsTournament (multi-model)
- SettingsHealth (check thresholds)
- SettingsAdvanced (RAG, file watching)

### 4. **Foreman Mode-Specific UI**
Foreman operates in 4 modes (ARCHITECT → VOICE_CALIBRATION → DIRECTOR → EDITOR), but current plan treats it as generic chat.

**Missing mode-specific context**:
- ARCHITECT: Template progress tracker, notebook registration
- VOICE_CALIBRATION: Tournament launcher, variant grid
- DIRECTOR: Scaffold generator, scene variants, enhancement pipeline
- EDITOR: (Future - not yet implemented)

---

## Recommended Action

**Update UI_IMPLEMENTATION_PLAN.md** to include:

### Section 11: Feature-Complete Component Inventory
Add comprehensive list of all 50+ UI components organized by Foreman mode and backend category.

### Update Phase Breakdown
Current phases focus on infrastructure. Add feature-specific phases:
- **Phase 3**: Story Bible & Voice Calibration UI (ARCHITECT + VOICE_CALIBRATION modes)
- **Phase 4**: Director Mode UI (Scene creation pipeline)
- **Phase 5**: Complete Settings Panel (11 sub-components)
- **Phase 6**: Graph Health + Advanced Features

### Add Component Dependency Map
Show which components depend on others:
- Example: VoiceVariantGrid requires SettingsAgents (API keys) to work
- Example: SceneEnhancement requires SettingsScoring (thresholds configured)

---

**Next Step**: Create updated UI_IMPLEMENTATION_PLAN.md v2.0 with complete component inventory and revised phase breakdown.
