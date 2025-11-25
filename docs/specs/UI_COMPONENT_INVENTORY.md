# Writers Factory - Complete UI Component Inventory

**Version**: 2.0
**Date**: November 25, 2025
**Purpose**: Comprehensive list of ALL UI components required to activate backend features

---

## Organization Strategy

Components are organized by:
1. **Panel Location** (Binder, Canvas, Foreman, Studio, Modals)
2. **Foreman Mode** (ARCHITECT, VOICE_CALIBRATION, DIRECTOR, EDITOR)
3. **Backend Service** (What API endpoints it activates)

---

## Panel 1: BINDER (File Navigation)

### Core Components
1. **PanelBinder.svelte** - Main container (~150 lines)
   - **Backend**: `GET /files/{path}`
   - **Features**: File tree, context menus, drag-drop
   - **Dependencies**: None
   - **Priority**: P0 (Infrastructure)

2. **FileTreeNode.svelte** - Recursive tree node (~80 lines)
   - Expand/collapse folders
   - File type icons
   - Context menu on right-click

3. **FileContextMenu.svelte** - Actions menu (~60 lines)
   - New File/Folder
   - Rename, Delete
   - Open in External Editor

### Story Bible-Specific
4. **StoryBibleBadges.svelte** - Template status indicators (~40 lines)
   - Shows template completion status in file tree
   - Icons: ✓ Complete, ◐ In Progress, □ Not Started, ❌ Invalid
   - **Backend**: `GET /story-bible/status`

---

## Panel 2: CANVAS (Editor)

### Core Components
5. **PanelCanvas.svelte** - Editor container (~120 lines)
   - **Backend**: `GET /files/{path}`, `PUT /files/{path}`
   - Monaco Editor wrapper
   - Breadcrumbs (Project > Chapter 1 > Scene 1.1.md)
   - **Priority**: P0 (Infrastructure)

6. **MonacoWrapper.svelte** - Editor integration (~100 lines)
   - Syntax highlighting (Markdown)
   - Auto-save with debounce
   - Word count display

7. **BreadcrumbNav.svelte** - File path navigation (~50 lines)
   - Clickable path segments
   - Shows current file context

---

## Panel 3: FOREMAN (AI Chat + Knowledge Graph)

### Core Container
8. **PanelForeman.svelte** - Split container (~150 lines)
   - Top half: Chat interface
   - Bottom half: Knowledge graph
   - Draggable split handle
   - **Priority**: P0 (Infrastructure)

### Foreman Chat Components
9. **ForemanChat.svelte** - Chat interface (~200 lines)
   - **Backend**: `POST /foreman/chat`, `GET /foreman/status`
   - Message history display
   - Input field with send button
   - Streaming response support
   - **Priority**: P0 (Core feature)

10. **ForemanMessage.svelte** - Single message bubble (~80 lines)
    - User vs Foreman styling
    - Markdown rendering
    - Copy button
    - Timestamp

11. **ForemanModeIndicator.svelte** - Mode badge (~60 lines)
    - Shows current mode: ARCHITECT / VOICE_CALIBRATION / DIRECTOR / EDITOR
    - Color-coded per mode
    - Click → show mode details modal
    - **Backend**: `GET /foreman/mode`
    - **Priority**: P1

12. **WorkOrderTracker.svelte** - Template progress (~120 lines)
    - **Backend**: `GET /foreman/status`
    - 4 templates with status icons
    - Completion percentage bar
    - Missing fields per template
    - Mode transition buttons
    - **Priority**: P1 (Critical for ARCHITECT mode)

13. **ForemanActionButtons.svelte** - Quick actions (~80 lines)
    - "Reset Foreman" button
    - "Flush KB to Graph" button
    - "Advance to Next Mode" button (gated)
    - **Backend**: `POST /foreman/reset`, `POST /foreman/flush-kb`, `POST /foreman/mode/*`

### Knowledge Graph Components
14. **LiveGraph.svelte** - D3.js force-directed graph (~250 lines)
    - **Backend**: `GET /graph/view`
    - Force simulation
    - Node click → select
    - Zoom/pan controls
    - **Priority**: P1

15. **GraphControls.svelte** - Graph toolbar (~80 lines)
    - Zoom in/out buttons
    - Reset view
    - Node type filters (Character, Location, Theme, etc.)
    - Search nodes by name

16. **NodeDetailsPanel.svelte** - Selected node info (~100 lines)
    - Shows entity name, type, properties
    - Related nodes list
    - "View in Editor" button (if applicable)
    - **Priority**: P2

17. **GraphConflictIndicator.svelte** - Conflict badge (~50 lines)
    - **Backend**: `GET /graph/conflicts`
    - Badge count: "3 conflicts"
    - Click → open conflict resolver modal
    - **Priority**: P2

---

## Panel 4: STUDIO (Tool Cards)

### Core Container
18. **PanelStudio.svelte** - Card grid (~150 lines)
    - 2-column card layout
    - Responsive (1 col on narrow screens)
    - Scroll container
    - **Priority**: P0 (Infrastructure)

19. **StudioCard.svelte** - Reusable card component (~120 lines)
    - Props: title, description, icon, status, action
    - States: Ready, Active, Warning, Error, Disabled
    - Click handler
    - Status badge
    - **Priority**: P0 (Infrastructure)

### Story Bible Tools (ARCHITECT Mode)
20. **StoryBibleCard.svelte** - Story Bible launcher (~60 lines)
    - Shows completion status
    - Click → open Story Bible wizard
    - **Backend**: `GET /story-bible/status`
    - **Priority**: P1

### Voice Calibration Tools (VOICE_CALIBRATION Mode)
21. **VoiceTournamentCard.svelte** - Tournament launcher (~80 lines)
    - Shows agent availability
    - Click → open tournament launcher
    - **Backend**: `GET /voice-calibration/agents`
    - **Priority**: P1

### Director Mode Tools (DIRECTOR Mode)
22. **ScaffoldCard.svelte** - Scaffold generator launcher (~60 lines)
    - Click → open scaffold generator
    - **Priority**: P1

23. **SceneWriterCard.svelte** - Scene writer launcher (~60 lines)
    - Click → open scene variant tournament
    - **Priority**: P1

24. **EnhancementCard.svelte** - Enhancement pipeline (~60 lines)
    - Shows current scene score
    - Recommended enhancement mode
    - Click → open enhancement UI
    - **Priority**: P1

### Universal Tools
25. **HealthCheckCard.svelte** - Health check launcher (~80 lines)
    - **Backend**: `GET /health/status`
    - Shows last check summary
    - Warning/error count badges
    - Click → open health dashboard
    - **Priority**: P1

26. **MetabolismCard.svelte** - Consolidation launcher (~80 lines)
    - **Backend**: `GET /session/{id}/uncommitted`
    - Shows uncommitted event count
    - Click → trigger consolidation
    - **Priority**: P1

27. **AIIntelligenceCard.svelte** - Orchestrator quick view (~100 lines)
    - Shows current quality tier
    - Monthly spend indicator
    - Click → open Settings > Orchestrator
    - **Backend**: `GET /orchestrator/current-spend`
    - **Priority**: P1 (Phase 3E integration)

28. **SettingsCard.svelte** - Settings launcher (~60 lines)
    - Click → open settings modal
    - **Priority**: P1

---

## Modals & Overlays

### Story Bible Workflow (ARCHITECT Mode)
29. **StoryBibleWizard.svelte** - Main creation interface (~300 lines)
    - **Backend**: All `/story-bible/*` endpoints
    - Template progress tracker
    - NotebookLM integration
    - Step-by-step flow
    - **Priority**: P1

30. **NotebookRegistration.svelte** - Notebook setup (~150 lines)
    - **Backend**: `POST /foreman/notebook`, `GET /notebooklm/notebooks`
    - Add notebook button → auth flow
    - Role assignment dropdowns (World/Voice/Craft)
    - Test query per notebook
    - **Priority**: P1

31. **TemplateEditor.svelte** - In-context editing (~200 lines)
    - Protagonist: Fatal Flaw, The Lie, Arc fields
    - Beat Sheet: 15-beat checklist
    - Theme: Central theme + statement
    - Validation feedback
    - **Priority**: P2

### Voice Calibration Workflow (VOICE_CALIBRATION Mode)
32. **VoiceTournamentLauncher.svelte** - Tournament setup (~180 lines)
    - **Backend**: `POST /voice-calibration/tournament/start`
    - Test text input area
    - Agent selection (checkboxes)
    - Strategy selection (5 strategies)
    - Launch button with loading state
    - **Priority**: P1

33. **VoiceVariantGrid.svelte** - 25-variant display (~300 lines)
    - **Backend**: `GET /voice-calibration/tournament/{id}/variants`
    - 5×5 grid layout (agents × strategies)
    - Variant preview cards
    - Side-by-side comparison mode
    - Filter/sort controls
    - **Priority**: P1

34. **VoiceVariantCard.svelte** - Single variant (~120 lines)
    - Agent name + strategy badge
    - Preview text (first 150 words)
    - "Select Winner" button
    - "Add to Reference" checkbox
    - Expand for full text

35. **VoiceSelectionModal.svelte** - Winner selection (~150 lines)
    - **Backend**: `POST /voice-calibration/tournament/{id}/select`
    - Confirm winning variant
    - Optional: Select multiple as references
    - Generate Voice Bundle button
    - **Priority**: P1

36. **VoiceBundlePreview.svelte** - Bundle viewer (~150 lines)
    - **Backend**: `GET /voice-calibration/{project_id}`
    - Shows Gold Standard reference
    - Shows Anti-Patterns list
    - Shows Phase Evolution guidance
    - Export to NotebookLM button
    - **Priority**: P2

### Director Mode Workflow (DIRECTOR Mode)
37. **ScaffoldGenerator.svelte** - 2-stage scaffold flow (~350 lines)
    - **Backend**: 3 scaffold endpoints
    - Stage 1: Draft summary + enrichment suggestions
    - Enrichment modal: Notebook selector + query
    - Stage 2: Full scaffold preview
    - "Use Scaffold" button → pass to Scene Writer
    - **Priority**: P1

38. **EnrichmentSuggestions.svelte** - Context-aware prompts (~120 lines)
    - **Backend**: Returns from draft-summary
    - Suggested queries list
    - Click suggestion → auto-fill query
    - Skip enrichment option

39. **SceneStructureSelector.svelte** - Layout selection (~180 lines)
    - **Backend**: `POST /director/scene/structure-variants`
    - 5 structure cards
    - Preview: "Opens with dialogue" vs "Opens with action"
    - Select one → pass to variant generation
    - **Priority**: P1

40. **SceneVariantTournament.svelte** - 15+ variant display (~400 lines)
    - **Backend**: `POST /director/scene/generate-variants`
    - 3 models × 5 strategies = 15 variants
    - Grid with score badges
    - Sort: Score / Agent / Strategy
    - Expand → full text + score breakdown
    - "Select Winner" or "Create Hybrid"
    - **Priority**: P1 (Core Director Mode feature)

41. **SceneVariantCard.svelte** - Single variant (~150 lines)
    - Model + strategy badges
    - Score badge (color-coded by grade)
    - Preview (first 300 words)
    - Expand for full text
    - "Select" / "Add to Hybrid" buttons

42. **HybridSceneCreator.svelte** - Merge UI (~250 lines)
    - **Backend**: `POST /director/scene/create-hybrid`
    - Select 2-3 variants to merge
    - Specify merge instructions: "Opening from A, dialogue from B"
    - LLM generates hybrid
    - Preview → accept/reject
    - **Priority**: P2

43. **SceneScorecard.svelte** - Detailed scoring display (~200 lines)
    - **Backend**: `POST /director/scene/analyze`
    - 5-category breakdown (Voice 30, Character 20, etc.)
    - Visual progress bars per category
    - Drill-down: Click → see violations
    - Grade badge (A, A-, B+, etc.)
    - **Priority**: P1

44. **ScoreComparison.svelte** - Multi-scene comparison (~180 lines)
    - **Backend**: `POST /director/scene/compare`
    - Side-by-side scores for 2-4 scenes
    - Highlight differences
    - "Pick Best" button
    - **Priority**: P2

45. **AntiPatternDetector.svelte** - Violation display (~150 lines)
    - **Backend**: `POST /director/scene/detect-patterns`
    - Table: Pattern | Line | Severity | Fix
    - Filter by severity
    - "Ignore This" button (one-time)
    - **Priority**: P2

46. **MetaphorAnalyzer.svelte** - Domain visualization (~180 lines)
    - **Backend**: `POST /director/scene/analyze-metaphors`
    - Pie chart: Domain distribution
    - Saturation warnings (red if > threshold)
    - Simile count indicator
    - Domain examples from text
    - **Priority**: P2

47. **EnhancementPipeline.svelte** - Enhancement workflow (~350 lines)
    - **Backend**: All 4 `/director/scene/enhance*` endpoints
    - Mode auto-selection based on score
    - **Action Prompt (85+)**: OLD → NEW fixes with checkboxes
    - **6-Pass (70-84)**: Progress indicator (Pass 1/6: Sensory Anchoring...)
    - **Rewrite (<70)**: "Score too low" message
    - Before/after diff view
    - Accept/reject buttons
    - **Priority**: P1

---

## Panel 3: FOREMAN (Chat + Graph)

### Already Covered Above
- Components 9-17 (ForemanChat, LiveGraph, WorkOrderTracker, etc.)

### Additional Mode-Specific UI
48. **ArchitectModeUI.svelte** - ARCHITECT mode context (~150 lines)
    - Embedded in Foreman panel when mode = ARCHITECT
    - Shows template checklist
    - Notebook registration inline
    - Quick links to templates
    - **Priority**: P1

49. **VoiceCalibrationModeUI.svelte** - VOICE_CALIBRATION context (~120 lines)
    - Shows tournament status
    - Variant selection progress
    - Voice Bundle generation status
    - **Priority**: P1

50. **DirectorModeUI.svelte** - DIRECTOR mode context (~150 lines)
    - Shows current scene being drafted
    - Quick access to scaffold/variants/enhancement
    - Beat progress indicator
    - **Priority**: P1

---

## Panel 4: STUDIO (Tool Cards)

### Already Covered Above
- Components 20-28 (Studio cards)

---

## Modal Components (Overlays)

### Settings System (Phase 3C/5)
51. **SettingsPanel.svelte** - Main settings modal (~250 lines)
    - **Backend**: All 8 `/settings/*` endpoints
    - Sidebar navigation (11 categories)
    - Main content area
    - Apply/Reset buttons
    - **Priority**: P1 (Critical - API keys blocking!)

52. **SettingsAgents.svelte** - API keys + agents (~200 lines)
    - API key inputs (masked): OpenAI, Anthropic, Google, DeepSeek, Mistral, XAI, Qwen, Kimi, Zhipu, Tencent
    - "Test Connection" button per key
    - Agent status indicators (Ready/Missing Key/Error)
    - Foreman model dropdown
    - Tournament agent checkboxes
    - **Backend**: `GET /settings/category/agents`
    - **Priority**: P0 (BLOCKING - No cloud features work without API keys!)

53. **SettingsScoring.svelte** - Rubric weights (~180 lines)
    - Preset dropdown (Literary Fiction, Thriller, Romance, Balanced)
    - 5 linked sliders (Voice, Character, Metaphor, Anti-Pattern, Phase)
    - Auto-adjust logic (sum = 100)
    - Live total display
    - **Backend**: `GET /settings/category/scoring`
    - **Priority**: P1

54. **SettingsVoice.svelte** - Voice strictness (~150 lines)
    - 3 dropdowns: Authenticity, Purpose, Fusion (Low/Medium/High)
    - Explanation tooltips per strictness level
    - **Backend**: `GET /settings/category/scoring`
    - **Priority**: P2

55. **SettingsMetaphor.svelte** - Metaphor discipline (~150 lines)
    - Domain saturation slider (20-50%)
    - Primary domain allowance slider (25-45%)
    - Simile tolerance slider (0-5)
    - Minimum domains slider (2-6)
    - **Backend**: `GET /settings/category/scoring`
    - **Priority**: P2

56. **SettingsAntiPatterns.svelte** - Pattern management (~200 lines)
    - System patterns list with ignore toggles
    - Custom patterns section
    - "Add Pattern" button → modal (pattern + severity)
    - Severity overrides dropdown
    - **Backend**: `GET /settings/category/scoring`
    - **Priority**: P2

57. **SettingsEnhancement.svelte** - Enhancement thresholds (~150 lines)
    - 4 threshold sliders (Auto-Enhance, Action Prompt, 6-Pass, Rewrite)
    - Aggressiveness dropdown (Conservative/Medium/Aggressive)
    - **Backend**: `GET /settings/category/enhancement`
    - **Priority**: P2

58. **SettingsForeman.svelte** - Foreman behavior (~150 lines)
    - Proactiveness dropdown (Low/Medium/High)
    - Challenge intensity dropdown
    - Explanation verbosity dropdown
    - Auto-KB-Writes toggle
    - **Backend**: `GET /settings/category/foreman`
    - **Priority**: P2

59. **SettingsOrchestrator.svelte** - Model orchestrator (~250 lines)
    - **Backend**: All 4 `/orchestrator/*` endpoints
    - Enable toggle
    - Quality tier selector (3 cards: Budget/Balanced/Premium)
    - Monthly budget input
    - Prefer local toggle
    - Cost estimator widget
    - Model recommendations preview
    - **Priority**: P1 (Phase 3E)
    - ✅ **Already in current plan**

60. **SettingsTournament.svelte** - Multi-model tournament (~200 lines)
    - **Backend**: Future Phase 4 (not yet implemented)
    - Enable toggle
    - Critical tasks checkboxes
    - Models per tournament slider (2-5)
    - Max per day input
    - Show all responses toggle
    - Cost warning box
    - **Priority**: P3 (Future)

61. **SettingsHealth.svelte** - Health check thresholds (~200 lines)
    - **Backend**: `GET /settings/category/health_checks`
    - Health check model dropdown
    - Pacing: Plateau window, tolerance sliders
    - Structure: Beat deviation sliders
    - Character: Flaw frequency, cast appearances
    - Theme: Symbol occurrences, resonance score
    - **Priority**: P2

62. **SettingsAdvanced.svelte** - Advanced settings (~150 lines)
    - Max conversation history slider
    - KB context limit slider
    - Voice bundle injection dropdown
    - RAG strategy dropdown (Vector/Keyword/Hybrid)
    - File watcher dropdown (Immediate/Polling)
    - **Priority**: P3

### Shared Settings Components
63. **SettingSlider.svelte** - Reusable slider (~80 lines)
    - Label, value display, range
    - Tooltip support
    - **Priority**: P0 (Shared infrastructure)

64. **SettingDropdown.svelte** - Reusable dropdown (~70 lines)
    - Label, options, tooltip
    - **Priority**: P0

65. **SettingToggle.svelte** - Reusable toggle (~60 lines)
    - Label, tooltip, on/off state
    - **Priority**: P0

66. **SettingSecret.svelte** - API key input (~100 lines)
    - Masked input (show last 4 chars)
    - Show/hide toggle
    - Test connection button
    - Status indicator
    - **Priority**: P0

67. **CostEstimator.svelte** - Real-time spend widget (~120 lines)
    - **Backend**: `GET /orchestrator/current-spend`
    - Progress bar (Green/Yellow/Red based on %)
    - Text: "$0.47 / $2.00 ($1.53 remaining)"
    - Warning indicators (80%, 100%)
    - **Priority**: P1
    - ✅ **Already in current plan**

68. **QualityTierCard.svelte** - Tier selector card (~100 lines)
    - Budget/Balanced/Premium cards
    - Shows: Cost estimate, quality range, models used
    - Selected state
    - **Priority**: P1
    - ✅ **Already in current plan**

69. **ModelRecommendationsPreview.svelte** - Model assignments (~120 lines)
    - **Backend**: `GET /orchestrator/recommendations/{task}`
    - Table: Task Type | Budget | Balanced | Premium
    - Updates dynamically on tier change
    - **Priority**: P2

### Health Check Workflow (Phase 3D)
70. **HealthReportViewer.svelte** - Full report display (~300 lines)
    - **Backend**: `GET /health/report/{id}`
    - 7 category sections (expandable)
    - Warning/error cards per issue
    - Recommendations
    - Export button (markdown/JSON)
    - **Priority**: P1

71. **HealthWarningCard.svelte** - Single warning display (~100 lines)
    - Severity badge (Warning/Error)
    - Title + description
    - Affected scenes/chapters
    - Recommendation
    - "View in Editor" link

72. **HealthTrendsChart.svelte** - Longitudinal analysis (~250 lines)
    - **Backend**: `GET /health/trends/{metric}`
    - Line charts for metrics over time
    - Date range selector
    - Metric dropdown (Pacing, Theme Scores, Flaw Frequency, etc.)
    - Export as PNG
    - **Priority**: P2

73. **ThemeOverrideModal.svelte** - Manual theme scoring (~150 lines)
    - **Backend**: `POST /health/theme/override`, `GET /health/theme/overrides`
    - Beat selector
    - Current LLM score display
    - Manual score input (0-10)
    - Explanation text area
    - Save button
    - **Priority**: P3

74. **HealthCheckTrigger.svelte** - On-demand check (~100 lines)
    - **Backend**: `POST /health/check`
    - Scope selector: Scene / Chapter / Act / Manuscript
    - Target selector (e.g., "Chapter 5")
    - Run button with progress indicator
    - **Priority**: P2

### Graph Management
75. **GraphConflictResolver.svelte** - Conflict resolution (~250 lines)
    - **Backend**: `GET /graph/conflicts`
    - Conflict list: "Character age: 25 vs 30"
    - Source references per conflict
    - Resolution buttons: "Use First" / "Use Second" / "Manual Edit"
    - Bulk resolution
    - **Priority**: P2

76. **GraphIngestModal.svelte** - Manual re-ingestion (~120 lines)
    - **Backend**: `POST /graph/ingest`
    - File/folder selector
    - Progress indicator
    - Success/failure notifications
    - **Priority**: P3

### Session Management
77. **SessionSwitcher.svelte** - Session selector (~120 lines)
    - **Backend**: `GET /sessions/active`, `POST /session/new`
    - Dropdown: Active sessions
    - "New Session" button
    - Session stats preview
    - **Priority**: P2

78. **SessionHistoryBrowser.svelte** - History viewer (~200 lines)
    - **Backend**: `GET /session/{id}/history`
    - Searchable message list
    - Timestamp + speaker
    - Export session button
    - **Priority**: P3

79. **UncommittedEventsIndicator.svelte** - Metabolism reminder (~80 lines)
    - **Backend**: `GET /session/{id}/uncommitted`
    - Badge count: "3 uncommitted"
    - Click → trigger consolidation
    - Auto-hide when count = 0
    - **Priority**: P2

80. **ConsolidationProgress.svelte** - Consolidation flow (~150 lines)
    - **Backend**: `POST /metabolism/consolidate-kb`
    - Shows KB entries being processed
    - Progress bar: "Processing 5/12 entries"
    - Success/failure per entry
    - **Priority**: P2

### NotebookLM Integration
81. **NotebookLMConfig.svelte** - Configuration panel (~200 lines)
    - **Backend**: All 7 `/notebooklm/*` endpoints
    - Connection status indicator
    - "Authenticate" button → auth flow
    - Configured notebooks list
    - "Add Notebook" button
    - Test query interface
    - **Priority**: P1

82. **NotebookQueryModal.svelte** - Query interface (~180 lines)
    - Notebook selector dropdown
    - Query text input
    - Submit → display answer
    - Query history
    - **Priority**: P2

83. **NotebookAuthFlow.svelte** - Google auth (~120 lines)
    - **Backend**: `GET /notebooklm/auth`
    - Trigger auth flow
    - Loading state
    - Success/failure feedback
    - **Priority**: P1

### Miscellaneous
84. **MenuBar.svelte** - Application menu bar (~150 lines)
    - Writers Factory menus: File, Edit, Selection, View, AI, Go, Run, Terminal, Window
    - AI menu: Model Orchestrator submenu (current tier display)
    - **Priority**: P1

85. **StatusBar.svelte** - Bottom status bar (~100 lines)
    - Graph stats: "Nodes: 1,240"
    - Uncommitted events: "Uncommitted: 3"
    - Current model indicator
    - Mode indicator
    - **Priority**: P2

86. **LoadingOverlay.svelte** - Global loading state (~60 lines)
    - Full-screen overlay for long operations
    - Progress spinner
    - Status message
    - **Priority**: P2

87. **ToastNotifications.svelte** - Success/error toasts (~100 lines)
    - Auto-dismiss notifications
    - Success (green), Error (red), Info (blue), Warning (yellow)
    - Action buttons (e.g., "View Report")
    - **Priority**: P1

---

## Component Count Summary

| Category | Components | Priority Breakdown | Current Plan Coverage |
|----------|------------|-------------------|---------------------|
| **Infrastructure** | 8 | P0: 8 | ✅ 100% |
| **Story Bible (ARCHITECT)** | 4 | P1: 3, P2: 1 | ❌ 0% |
| **Voice Calibration** | 6 | P1: 4, P2: 2 | 🔴 17% (1/6) |
| **Director Mode** | 11 | P1: 6, P2: 5 | ❌ 0% |
| **Health Checks** | 6 | P1: 2, P2: 3, P3: 1 | 🔴 17% (1/6) |
| **Settings** | 19 | P0: 4, P1: 4, P2: 8, P3: 3 | 🔴 16% (3/19) |
| **Graph Management** | 6 | P1: 1, P2: 3, P3: 2 | 🔴 17% (1/6) |
| **Session/Metabolism** | 5 | P2: 4, P3: 1 | ❌ 0% |
| **NotebookLM** | 4 | P1: 2, P2: 2 | ❌ 0% |
| **Shared/Universal** | 8 | P1: 3, P2: 5 | 🔴 25% (2/8) |

**Total Components**: 87
**Currently Planned**: ~18 (21%)
**Missing**: 69 (79%)

---

## Priority Breakdown

### P0 - Infrastructure (MUST HAVE - Week 1)
**Count**: 12 components
**Coverage**: ✅ 100% (all in current plan)
- MainLayout, 4 panel containers
- StudioCard, Shared setting components
- **Status**: Well covered

### P1 - Core Features (MUST HAVE - Weeks 2-4)
**Count**: 31 components
**Coverage**: 🔴 19% (6/31)
**Missing**:
- Story Bible wizard + templates
- Voice tournament launcher + variant grid
- Director mode: Scaffold generator, scene variants, enhancement pipeline
- Settings panel + 4 critical sub-components (Agents, Scoring, Orchestrator, Health)
- NotebookLM config + auth

### P2 - Enhanced Features (SHOULD HAVE - Weeks 5-6)
**Count**: 31 components
**Coverage**: 🔴 3% (1/31)
**Missing**: Almost everything

### P3 - Nice to Have (Weeks 7+)
**Count**: 13 components
**Coverage**: ❌ 0%

---

## Critical Blockers

### Blocker 1: API Keys (SettingsAgents.svelte)
**Severity**: **CRITICAL**
**Impact**: Without API key configuration UI, writers cannot:
- Use cloud models (Claude, GPT-4o, DeepSeek)
- Run voice calibration tournaments
- Access Director Mode scene generation
- Enable Model Orchestrator

**Required**: SettingsAgents.svelte MUST be in Phase 1 or 2 (not Phase 5!)

### Blocker 2: Story Bible Creation (StoryBibleWizard)
**Severity**: **HIGH**
**Impact**: Without Story Bible UI, writers cannot:
- Create Protagonist, Beat Sheet, Theme, World Rules
- Progress past ARCHITECT mode
- Access Voice Calibration or Director Mode

**Required**: Must be implemented before Voice Calibration UI

### Blocker 3: Voice Calibration (VoiceTournamentLauncher + VoiceVariantGrid)
**Severity**: **HIGH**
**Impact**: Without variant display/selection UI, writers cannot:
- Select winning voice variant
- Generate Voice Reference Bundle
- Progress to Director Mode

**Required**: Must be implemented before Director Mode UI

### Blocker 4: Director Mode Scene Creation (SceneVariantTournament + EnhancementPipeline)
**Severity**: **HIGH**
**Impact**: Without scene creation UI, writers cannot:
- Generate scene variants
- Score and compare variants
- Enhance scenes
- Actually write their novel!

**Required**: Core value proposition of the app

---

## Dependency Graph

```
Phase 1: Infrastructure
  ├── MainLayout ✅
  ├── 4 Panel Containers ✅
  ├── StudioCard ✅
  └── Shared Components (Slider, Toggle, etc.) ✅

Phase 2: Settings Foundation (CRITICAL PATH)
  ├── SettingsPanel ❌
  ├── SettingsAgents ❌ ← BLOCKER for all cloud features
  ├── SettingsScoring ❌
  └── SettingsOrchestrator ✅

Phase 3: Story Bible (ARCHITECT Mode)
  ├── Depends on: SettingsAgents (API keys)
  ├── StoryBibleWizard ❌
  ├── NotebookRegistration ❌
  └── TemplateEditor ❌

Phase 4: Voice Calibration (VOICE_CALIBRATION Mode)
  ├── Depends on: Story Bible completion
  ├── VoiceTournamentLauncher ❌
  ├── VoiceVariantGrid ❌
  └── VoiceSelectionModal ❌

Phase 5: Director Mode (DIRECTOR Mode)
  ├── Depends on: Voice Calibration completion
  ├── ScaffoldGenerator ❌
  ├── SceneVariantTournament ❌
  ├── SceneScorecard ❌
  └── EnhancementPipeline ❌

Phase 6: Health Checks
  ├── Depends on: Director Mode (scenes exist)
  ├── HealthReportViewer ❌
  ├── HealthTrendsChart ❌
  └── ThemeOverrideModal ❌

Phase 7: Advanced Features
  ├── Graph conflict resolver ❌
  ├── Session management ❌
  └── Advanced settings ❌
```

---

## Recommended Revised Phase Plan

### Week 1: Infrastructure + Critical Settings
- Phase 1: 4-panel layout (as planned) ✅
- **NEW**: SettingsPanel + SettingsAgents (API keys!) ❌
- **NEW**: SettingsScoring (rubric weights) ❌
- MenuBar + StatusBar

**Deliverable**: Working IDE with API key configuration

### Week 2: Story Bible (ARCHITECT Mode)
- StoryBibleWizard
- NotebookRegistration
- TemplateEditor
- WorkOrderTracker (already planned)

**Deliverable**: Writers can create Story Bible and advance to Voice Calibration

### Week 3: Voice Calibration (VOICE_CALIBRATION Mode)
- VoiceTournamentLauncher
- VoiceVariantGrid
- VoiceSelectionModal
- VoiceBundlePreview

**Deliverable**: Writers can run voice tournament and generate Voice Bundle

### Week 4: Director Mode - Scaffold
- ScaffoldGenerator (2-stage flow)
- EnrichmentSuggestions
- SceneStructureSelector

**Deliverable**: Writers can create scaffolds for scenes

### Week 5: Director Mode - Scene Writing
- SceneVariantTournament
- SceneVariantCard
- SceneScorecard
- HybridSceneCreator

**Deliverable**: Writers can generate and score scene variants

### Week 6: Director Mode - Enhancement
- EnhancementPipeline
- AntiPatternDetector
- MetaphorAnalyzer
- ScoreComparison

**Deliverable**: Writers can enhance scenes to publication quality

### Week 7: Health Checks
- HealthReportViewer
- HealthTrendsChart
- HealthCheckTrigger
- Complete HealthDashboard

**Deliverable**: Writers can validate manuscript structure

### Week 8: Advanced Features
- Remaining settings sub-components
- Graph conflict resolution
- Session management
- NotebookLM advanced features

**Deliverable**: Full feature parity with backend

---

## Effort Estimates

| Phase | Components | Est. Lines of Code | Est. Time |
|-------|------------|-------------------|-----------|
| Week 1 | 15 | ~1,800 | 40 hours |
| Week 2 | 8 | ~1,200 | 30 hours |
| Week 3 | 6 | ~1,100 | 28 hours |
| Week 4 | 5 | ~800 | 20 hours |
| Week 5 | 7 | ~1,300 | 32 hours |
| Week 6 | 7 | ~1,200 | 30 hours |
| Week 7 | 8 | ~1,400 | 35 hours |
| Week 8 | 18 | ~2,800 | 70 hours |

**Total**: 87 components, ~11,600 lines of code, ~285 hours (7 weeks full-time)

---

## Critical Success Factors

1. **Start with Settings** - API keys must be configurable before any cloud features work
2. **Follow Foreman Modes** - Implement UI in the order writers will use it (ARCHITECT → VOICE → DIRECTOR)
3. **Build for Discovery** - Each mode's UI should guide writers to the next step
4. **Don't Skip Modals** - Studio cards are useless without the modals they open
5. **Test End-to-End** - Each week should deliver a complete workflow, not isolated components

---

**Conclusion**: The current UI_IMPLEMENTATION_PLAN.md is excellent **infrastructure** but needs **69 additional components** to activate all backend features. A revised plan with 8 phases over 7-8 weeks is recommended.

*Generated: November 25, 2025*
*Status: Pre-Implementation Audit Complete*
