# Writers Factory - Complete UI Implementation Plan v3.0

**Date**: November 25, 2025
**Status**: Production Ready
**Supersedes**: UI_IMPLEMENTATION_PLAN_V2.md

---

## Executive Summary

This document provides a **complete** UI implementation plan covering all 87 components required to make the Writers Factory backend features accessible to users. It consolidates:
- Original infrastructure plan (4-panel layout, design system)
- Complete component inventory from gap analysis
- **4-track parallel development strategy** (added Track 0: Design System)
- Phased rollout following Foreman workflow modes
- **Direct implementation approach** (Figma optional for complex components only)

**Key Metrics**:
- **Total Components**: 87
- **Backend API Coverage**: 88 endpoints across 13 categories
- **Current Coverage**: 21% (8 components exist)
- **Missing Coverage**: 79% (69 components to build)

**Critical Insight**: Settings Panel (specifically SettingsAgents.svelte for API keys) is a P0 blocker that prevents access to 80% of backend features.

**Design Decision**: Direct implementation using detailed UX_DESIGN_PROMPTS.md specs. Figma reserved only for complex spatial layouts (Voice Tournament 5×5 grid, BeatSheet Editor).

---

## Implementation Approach: Figma vs. Direct

### Direct Implementation (DEFAULT)

The UX_DESIGN_PROMPTS.md contains detailed specifications with:
- Exact pixel dimensions (240px binder, 320px foreman, etc.)
- Complete color palette (hex codes for all states)
- Typography scale (sizes, weights, line heights)
- Component states (default, hover, active, disabled, focus)
- Spacing system (4px base grid)

**Use direct implementation for:**
- Settings panels (forms + tabs - patterns exist)
- 4-panel layout (flex layout - pattern exists)
- Studio panel (card grid - `.agent-card` pattern exists)
- Status bar, toasts, loading states (standard patterns)
- Menu bar (standard desktop pattern)
- Chat interfaces (existing ChatSidebar pattern)

### Figma Validation (OPTIONAL)

**Use Figma only when visual validation would prevent rework:**

| Component | Reason for Figma |
|-----------|------------------|
| VoiceVariantGrid (5×5) | Complex 25-cell grid needs spatial validation |
| BeatSheetEditor | 15-beat table with drag-drop reordering |
| SceneHybridCreator | Multi-section merge UI is novel |
| GraphVisualization | Force-directed layout needs visual tuning |

**Figma workflow:**
1. Feed specific prompt from UX_DESIGN_PROMPTS.md to Figma AI
2. Generate mockup
3. Validate layout decisions
4. Implement based on mockup + specs

### Existing Patterns to Reuse

From the 8 existing components (~2,050 lines):

| Pattern | Source Component | Reuse For |
|---------|------------------|-----------|
| Card with status | AgentPanel.svelte | Studio cards, Story Bible progress |
| Chat bubbles | ChatSidebar.svelte | Foreman chat, any chat UI |
| Tab switcher | TabbedPanel.svelte | Settings tabs, mode tabs |
| File tree | FileTree.svelte | Binder panel |
| Status indicators | AgentPanel.svelte | Health indicators, progress dots |
| Form inputs | NotebookPanel.svelte | Settings forms, wizards |
| Loading states | Multiple | All async operations |

---

## Design System: Cyber-Noir Theme

### Current State vs. Target

The existing 8 components use a **light theme with purple accent**. The target is a **dark Cyber-Noir theme** per UX_DESIGN_PROMPTS.md.

| Aspect | Current | Cyber-Noir Target |
|--------|---------|-------------------|
| Mode | Light theme | Dark theme |
| Background | `#f8fafc` | `#0f1419` |
| Panel BG | `#ffffff` | `#1a2027` |
| Card BG | `#f3f4f6` | `#242d38` |
| Text Primary | `#111827` | `#e6edf3` |
| Text Secondary | `#6b7280` | `#8b949e` |
| Accent | `#8b5cf6` (purple) | `#d4a574` (gold) / `#58a6ff` (cyan) |
| Borders | `#e5e7eb` | `#2d3a47` |

### Design Tokens (CSS Variables)

All components will use CSS custom properties defined in `frontend/src/app.css`:

```css
:root {
  /* Backgrounds */
  --bg-primary: #0f1419;
  --bg-secondary: #1a2027;
  --bg-tertiary: #242d38;
  --bg-elevated: #2d3640;

  /* Text */
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;

  /* Accents */
  --accent-gold: #d4a574;
  --accent-cyan: #58a6ff;
  --accent-gold-hover: #e0b585;
  --accent-cyan-hover: #79b8ff;

  /* Semantic */
  --success: #3fb950;
  --warning: #d29922;
  --error: #f85149;

  /* Borders */
  --border: #2d3a47;
  --border-subtle: #21262d;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);

  /* Spacing (4px base) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-full: 9999px;

  /* Typography */
  --font-ui: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'IBM Plex Mono', monospace;
  --font-prose: 'Merriweather', Georgia, serif;
}
```

---

## Strategic Approach: 4-Track Parallel Development

### Track 0: Design System (PREREQUISITE)

**Goal**: Establish Cyber-Noir foundation before building new components

**Tasks**:
1. Create `frontend/src/app.css` with design tokens
2. Import tokens in `frontend/src/app.html`
3. Migrate 8 existing components to use CSS variables
4. Validate dark theme renders correctly

**Components to Migrate**:
| Component | Lines | Effort |
|-----------|-------|--------|
| ChatSidebar.svelte | 549 | 1h |
| HealthDashboard.svelte | 495 | 1h |
| NotebookPanel.svelte | 384 | 45min |
| AgentPanel.svelte | 209 | 30min |
| FileTree.svelte | 187 | 30min |
| TabbedPanel.svelte | 79 | 15min |
| Editor.svelte | 55 | 15min |
| +page.svelte | 92 | 15min |

**Total Track 0 Effort**: 5-6 hours

**Outcome**: All existing components use Cyber-Noir theme. New components inherit automatically.

---

### Track 1: Critical UI - START AFTER TRACK 0

**Goal**: Unblock backend features and enable basic cloud functionality

**Why Week 1**:
- Settings Panel depends only on `/settings/*` API (stable since Phase 3C)
- Does NOT require Phase 3D/4 backend completion
- Unblocks all cloud features immediately (Voice Calibration, Director Mode, Model Orchestrator)
- Enables production testing while remaining UI is built

**Components** (18 hours total):

| Component | Effort | Priority | Purpose | Dependencies |
|-----------|--------|----------|---------|--------------|
| **SettingsAgents.svelte** | 3h | P0 | API key configuration (OpenAI, Anthropic, DeepSeek, Qwen) | `/settings/*` API |
| **SettingsOrchestrator.svelte** | 3h | P0 | Quality tier selection (Budget/Balanced/Premium), cost estimation | `/orchestrator/*` API |
| **MainLayout.svelte** | 6h | P0 | 4-panel IDE layout (Studio \| Graph \| Foreman \| Chat) with resize/collapse | Panel components |
| **ForemanChatPanel.svelte** | 4h | P0 | Enhanced chat interface with mode awareness, model routing display | `/foreman/chat` API |
| **StudioPanel.svelte** | 2h | P0 | Mode-aware cards (ARCHITECT, VOICE, DIRECTOR) with quick actions | Mode components |

**Deliverables**:
- Writers can configure API keys → unlock cloud features
- Writers can select quality tier → enable Budget/Balanced/Premium orchestration
- Writers can chat with Foreman → basic workflow guidance
- Writers can navigate modes → see available actions per mode

**Test Criteria**:
- Can enter API keys and save to settings.yaml
- Can select quality tier and see cost estimation
- Can chat with Foreman and see model routing (📋 local, 🧠 cloud)
- Can switch Foreman modes (ARCHITECT → VOICE → DIRECTOR)

---

### Track 2: Backend Completion (Parallel with Track 1)

**Goal**: Finish remaining backend features while UI Track 1 is in development

**Work Items**:
1. Complete Phase 3D remaining health checks (Pacing, Beat Progress, Symbolic Layering)
2. Extend Knowledge Graph schema (SCENE, CHAPTER, BEAT nodes)
3. Implement 7 Graph Health API endpoints
4. (Optional) Phase 4 Multi-Model Tournament

**Independence**: This work does NOT block Track 1 UI development. Both tracks run concurrently.

**Impact**: Track 2 completion enables Track 3 Graph Health UI (Week 5), but does not block Weeks 1-4 UI work.

---

### Track 3: Feature UI (Weeks 2-6) - FOLLOWS FOREMAN MODES

**Goal**: Complete all 87 UI components following the natural writer's workflow

**Strategy**: Phased rollout mirrors Foreman modes (ARCHITECT → VOICE_CALIBRATION → DIRECTOR → EDITOR) so writers can use each mode as it's completed.

---

## Track 3 Detailed Breakdown

### Week 2: ARCHITECT Mode UI (7 components, 40 hours)

**Goal**: Enable Story Bible creation workflow

**Components**:

| Component | Lines | Effort | Priority | Purpose | API Dependencies |
|-----------|-------|--------|----------|---------|------------------|
| **StoryBibleWizard.svelte** | 800 | 12h | P1 | Multi-step guided creation (Mindset → Audience → Premise → Theme → Voice → Characters → Beat Sheet) | `/story-bible/scaffold`, `/story-bible/status` |
| **BeatSheetEditor.svelte** | 600 | 10h | P1 | 15-beat structure editor with Save the Cat! templates, beat validation, percentage calculator | `/story-bible/beats`, `/story-bible/validate` |
| **CharacterArcBuilder.svelte** | 500 | 8h | P1 | Fatal Flaw, The Lie, True Character vs Characterization, arc progression | `/story-bible/characters` |
| **ThemeDefinition.svelte** | 300 | 5h | P1 | Theme statement, central question, thematic symbols, beats where theme appears | `/story-bible/theme` |
| **NotebookLMSelector.svelte** | 200 | 3h | P2 | Multi-notebook registration (World, Voice, Craft), role assignment | `/notebooklm/register`, `/notebooklm/list` |
| **StoryBibleProgress.svelte** | 100 | 1h | P2 | Progress tracker (5 foundation docs, beat sheet, protagonist, cast) | `/story-bible/status` |
| **StoryBibleExport.svelte** | 100 | 1h | P2 | Export to NotebookLM_Export/ for Project Notebook safety net | `/story-bible/export` |

**Workflow**:
1. Writer opens Writers Factory → sees "Create Story Bible" card in Studio Panel
2. Clicks card → StoryBibleWizard modal opens
3. Works through multi-step wizard: Mindset → Audience → Premise → Theme → Voice
4. Registers NotebookLM notebooks (World, Voice, Craft) if available
5. Builds protagonist (Fatal Flaw, The Lie, arc) using CharacterArcBuilder
6. Defines 15-beat structure using BeatSheetEditor with templates
7. Foreman validates completeness → transitions to VOICE_CALIBRATION mode

**Test Criteria**:
- Can complete all 7 Story Bible sections
- Can register 3+ NotebookLM notebooks
- Can create protagonist with Fatal Flaw + The Lie
- Can define 15-beat structure with midpoint and All Is Lost
- Foreman transitions to VOICE_CALIBRATION when Story Bible complete

---

### Week 3: VOICE_CALIBRATION Mode UI (6 components, 45 hours)

**Goal**: Enable voice tournament and Voice Bundle generation

**Components**:

| Component | Lines | Effort | Priority | Purpose | API Dependencies |
|-----------|-------|--------|----------|---------|------------------|
| **VoiceTournamentLauncher.svelte** | 400 | 6h | P1 | Configure tournament: select 3+ agents, choose 5 strategies (ACTION, CHARACTER, DIALOGUE, ATMOSPHERIC, BALANCED), set source scenes | `/voice-calibration/agents`, `/voice-calibration/tournament/start` |
| **VoiceVariantGrid.svelte** | 600 | 10h | P1 | Display 15-25 variants (3 models × 5 strategies) in grid, highlight scores, show strategy icons | `/voice-calibration/tournament/results` |
| **VoiceComparisonView.svelte** | 500 | 8h | P1 | Side-by-side comparison of 2-4 variants with diff highlighting, score breakdown | `/voice-calibration/tournament/compare` |
| **VoiceVariantSelector.svelte** | 300 | 5h | P1 | Select winning variant(s), create hybrid from multiple variants, mark for Voice Bundle | `/voice-calibration/tournament/select` |
| **VoiceBundleGenerator.svelte** | 400 | 6h | P1 | Generate Gold Standard, Anti-Patterns, Phase Evolution from selected variants, preview YAML | `/voice-calibration/bundle/generate` |
| **VoiceEvolutionChart.svelte** | 300 | 5h | P2 | Visualize voice changes across 4 phases (Early, Mid, Late, Final) with example sentences | `/voice-calibration/bundle/evolution` |

**Workflow**:
1. Foreman prompts: "Story Bible complete. Run Voice Calibration?"
2. Writer clicks "Launch Voice Tournament" in Studio Panel
3. VoiceTournamentLauncher opens → selects 3 agents (Claude, GPT-4o, DeepSeek), chooses source scenes
4. Tournament runs (backend) → 15 variants generated (3 models × 5 strategies)
5. VoiceVariantGrid displays results with scores
6. Writer reviews variants using VoiceComparisonView
7. Selects winners or creates hybrid → VoiceBundleGenerator creates Gold Standard, Anti-Patterns, Phase Evolution
8. Foreman generates Voice Bundle YAML → transitions to DIRECTOR mode

**Test Criteria**:
- Can launch tournament with 3+ agents
- Can see 15-25 variants in grid with scores
- Can compare 2-4 variants side-by-side
- Can select winner or create hybrid
- Can generate Voice Bundle (Gold Standard, Anti-Patterns, Phase Evolution)
- Foreman transitions to DIRECTOR mode when Voice Bundle complete

---

### Week 4: DIRECTOR Mode UI (16 components, 100 hours)

**Goal**: Enable scene-by-scene drafting with full pipeline (Scaffold → Structure → Write → Enhance)

**Components**:

| Component | Lines | Effort | Priority | Purpose | API Dependencies |
|-----------|-------|--------|----------|---------|------------------|
| **ScaffoldGenerator.svelte** | 600 | 10h | P1 | 2-stage scaffold flow: Draft Summary → Enrich (optional) → Generate Full Scaffold. Shows KB context, NotebookLM queries | `/director/scaffold/draft-summary`, `/director/scaffold/enrich`, `/director/scaffold/generate` |
| **StructureVariantSelector.svelte** | 400 | 6h | P1 | Choose from 5 chapter structure variants before writing prose. Shows beat connection, arc purpose | `/director/scene/structure-variants` |
| **SceneVariantGrid.svelte** | 800 | 12h | P1 | Tournament results grid: 15 variants (3 models × 5 strategies) with scores, strategy icons, Voice Authentication pass/fail | `/director/scene/generate-variants` |
| **SceneComparison.svelte** | 500 | 8h | P1 | Side-by-side comparison of 2-4 scene variants with diff highlighting, score breakdown by category (Voice 30, Character 20, Metaphor 20, Anti-Pattern 15, Phase 15) | `/director/scene/compare` |
| **SceneHybridCreator.svelte** | 400 | 6h | P1 | Create hybrid from multiple variants: select opening from Variant A, middle from Variant B, closing from Variant C | `/director/scene/create-hybrid` |
| **EnhancementPanel.svelte** | 600 | 10h | P1 | Enhancement mode selector: Action Prompt (85+), 6-Pass (70-84), Rewrite (<70). Shows threshold, reasoning | `/director/scene/enhance`, `/director/scene/action-prompt`, `/director/scene/six-pass` |
| **ActionPromptView.svelte** | 300 | 5h | P1 | Display surgical OLD → NEW fixes with rationale. Writer can accept/reject fixes individually | `/director/scene/action-prompt` |
| **SixPassEnhancement.svelte** | 500 | 8h | P1 | 6-pass enhancement with progress tracking: Sensory Anchoring → Verb Promotion → Metaphor Rotation → Voice Embed → Italics Gate → Voice Authentication | `/director/scene/six-pass` |
| **SceneScoreBreakdown.svelte** | 400 | 6h | P2 | Detailed score breakdown: Voice Authenticity (30), Character Consistency (20), Metaphor Discipline (20), Anti-Pattern Compliance (15), Phase Appropriateness (15) | `/director/scene/analyze` |
| **MetaphorAnalyzer.svelte** | 300 | 5h | P2 | Metaphor domain analysis: identify domains, check saturation (30% default), suggest rotation | `/director/scene/analyze-metaphors` |
| **AntiPatternDetector.svelte** | 300 | 5h | P2 | Detect zero-tolerance violations: "despite the", -ly adverbs, similes, passive voice, overused words | `/director/scene/detect-patterns` |
| **QuickSceneGenerator.svelte** | 400 | 6h | P2 | Fast single-model scene generation without tournament (for rough drafts) | `/director/scene/quick-generate` |
| **SceneVersionHistory.svelte** | 300 | 5h | P2 | Version history with rollback: Original → Enhanced → Hybrid → Final | N/A (future feature) |
| **ScaffoldEnrichmentPreview.svelte** | 200 | 3h | P2 | Preview NotebookLM enrichment results before committing to scaffold | `/director/scaffold/enrich` |
| **SceneExport.svelte** | 200 | 3h | P2 | Export scene to markdown, docx, or clipboard | N/A (file operation) |
| **BeatProgressTracker.svelte** | 200 | 3h | P2 | Show current beat, percentage through manuscript, next beat target | `/story-bible/beats`, `/health/beat-progress` |

**Workflow**:
1. Foreman prompts: "Voice Bundle ready. Create your first scene?"
2. Writer clicks "Create Scene" in Studio Panel
3. ScaffoldGenerator opens → writer drafts summary, optionally enriches from NotebookLM, generates full scaffold
4. StructureVariantSelector shows 5 chapter structures → writer chooses one
5. Tournament runs (backend) → 15 scene variants generated
6. SceneVariantGrid displays results → writer compares using SceneComparison
7. Writer selects winner or creates hybrid using SceneHybridCreator
8. EnhancementPanel determines mode: Action Prompt (85+) or 6-Pass (70-84)
9. Writer applies fixes → final scene ready
10. Foreman ingests scene → updates Knowledge Graph → prompts for next scene

**Test Criteria**:
- Can generate scaffold with KB context + NotebookLM enrichment
- Can see 5 structure variants and select one
- Can run tournament and see 15 scene variants
- Can compare variants side-by-side with score breakdown
- Can create hybrid from multiple variants
- Can apply Action Prompt fixes (85+) or 6-Pass enhancement (70-84)
- Can see metaphor domains and anti-pattern violations
- Foreman updates Knowledge Graph after scene finalization

---

### Week 5: Graph Health UI (4 components, 50 hours)

**Goal**: Enable macro-level structural validation and health monitoring

**Components**:

| Component | Lines | Effort | Priority | Purpose | API Dependencies |
|-----------|-------|--------|----------|---------|------------------|
| **HealthDashboard.svelte** | 800 | 15h | P1 | Main health dashboard with 7 check categories: Pacing, Beat Progress, Timeline, Flaw Challenges, Cast Function, Symbolic Layering, Theme Resonance. Shows scores, warnings, trends | `/health/check`, `/health/report/{id}` |
| **HealthReportViewer.svelte** | 600 | 10h | P1 | Detailed health report with warnings by severity (ERROR, WARNING, INFO), remediation suggestions, affected scenes | `/health/report/{id}` |
| **TrendChart.svelte** | 500 | 8h | P2 | Historical trend charts for 7 health metrics over time (daily/weekly/monthly), export to CSV | `/health/trends/{metric}` |
| **ThemeResonanceOverride.svelte** | 400 | 6h | P2 | Manual override for theme resonance scores: writer sets custom score + explanation, LLM auto-scores when no override | `/health/theme/override` |

**Additional Components** (from original plan, already counted):
- HealthCheckConfig.svelte (3h, P2) - Configure health check thresholds and auto-trigger settings
- ConflictResolutionPanel.svelte (5h, P2) - Resolve timeline conflicts, world rule violations
- BeatDeviationAlert.svelte (3h, P2) - Alert when scenes deviate from beat targets

**Total**: 7 components, 50 hours

**Workflow**:
1. Foreman auto-runs health checks after chapter assembly (configurable)
2. Writer sees health score in Graph Panel (green/yellow/red indicator)
3. Clicks health indicator → HealthDashboard opens
4. Reviews 7 check categories → clicks category to see detailed report
5. HealthReportViewer shows warnings with severity, remediation suggestions
6. Writer can override theme resonance scores manually using ThemeResonanceOverride
7. TrendChart shows health history over time
8. Writer resolves conflicts using ConflictResolutionPanel

**Test Criteria**:
- Can see overall health score in Graph Panel
- Can open HealthDashboard and see 7 check categories
- Can view detailed warnings with remediation suggestions
- Can override theme resonance scores with explanation
- Can see historical trends for health metrics
- Can resolve timeline conflicts and world rule violations

---

### Week 6: Settings + Polish (14 components, 52 hours)

**Goal**: Complete Settings Panel and polish existing UI

**Settings Sub-Components** (8 components, 25 hours):

| Component | Lines | Effort | Priority | Purpose | API Dependencies |
|-----------|-------|--------|----------|---------|------------------|
| **SettingsScoring.svelte** | 300 | 4h | P2 | Configure rubric weights: Voice (30), Character (20), Metaphor (20), Anti-Pattern (15), Phase (15) | `/settings/category/scoring` |
| **SettingsVoice.svelte** | 300 | 4h | P2 | Voice strictness levels (Conservative, Balanced, Experimental), authenticity thresholds | `/settings/category/voice` |
| **SettingsMetaphor.svelte** | 300 | 4h | P2 | Metaphor discipline: domain saturation threshold (30% default), domain whitelist | `/settings/category/metaphor` |
| **SettingsAntiPatterns.svelte** | 400 | 5h | P2 | Anti-pattern management: enable/disable patterns, add custom patterns, zero-tolerance list | `/settings/category/anti_patterns` |
| **SettingsEnhancement.svelte** | 300 | 4h | P2 | Enhancement thresholds: Action Prompt (85+ default), 6-Pass (70-84), Rewrite (<70) | `/settings/category/enhancement` |
| **SettingsForeman.svelte** | 200 | 2h | P2 | Foreman behavior: proactiveness level (Low/Medium/High), auto-health-check frequency | `/settings/category/foreman` |
| **SettingsHealth.svelte** | 300 | 4h | P2 | Health check thresholds: pacing plateau (3 chapters default), flaw challenge gap (10 chapters), cast absence (8 chapters) | `/settings/category/health_checks` |
| **SettingsAdvanced.svelte** | 300 | 4h | P2 | Advanced settings: RAG chunk size, file watching enabled, context window limits | `/settings/category/advanced` |

**Note**: SettingsAgents.svelte (3h, P0) and SettingsOrchestrator.svelte (3h, P0) already completed in Track 1 (Week 1).

**Polish Components** (6 components, 27 hours):

| Component | Lines | Effort | Priority | Purpose | API Dependencies |
|-----------|-------|--------|----------|---------|------------------|
| **KeyboardShortcuts.svelte** | 400 | 6h | P3 | Configurable keyboard shortcuts with conflict detection | N/A (local) |
| **ThemeCustomizer.svelte** | 300 | 5h | P3 | Visual theme customization: Cyber-Noir (default), Light, Sepia, Nord, etc. | N/A (local) |
| **ExportManager.svelte** | 500 | 8h | P3 | Export manuscript to multiple formats: markdown, docx, PDF, epub | N/A (file operations) |
| **CommandPalette.svelte** | 400 | 6h | P3 | Quick command access (Cmd+K): search actions, navigate, run commands | N/A (local) |
| **TutorialOverlay.svelte** | 200 | 3h | P3 | First-time user tutorial with interactive tooltips and mode walkthroughs | N/A (local) |
| **ProjectTemplates.svelte** | 300 | 4h | P3 | Quick-start templates: Literary Fiction, Thriller, Romance, Sci-Fi with pre-filled Story Bible examples | `/story-bible/templates` |

**Total**: 14 components, 52 hours

**Workflow**:
1. Writer opens Settings Panel → sees 11 sub-component tabs
2. Configures scoring weights, voice strictness, metaphor discipline, anti-patterns
3. Sets enhancement thresholds, Foreman proactiveness, health check settings
4. Customizes keyboard shortcuts and visual theme
5. Exports manuscript to desired format
6. Uses command palette (Cmd+K) for quick navigation

**Test Criteria**:
- Can access all 11 Settings sub-components
- Can modify all configurable values and save to settings.yaml
- Can customize keyboard shortcuts without conflicts
- Can change visual theme and see updates immediately
- Can export manuscript to markdown, docx, PDF
- Can use command palette to navigate and run actions

---

## Complete Component Inventory

### By Category

**Settings Panel** (11 components):
1. SettingsAgents.svelte (P0, Week 1)
2. SettingsOrchestrator.svelte (P0, Week 1)
3. SettingsScoring.svelte (P2, Week 6)
4. SettingsVoice.svelte (P2, Week 6)
5. SettingsMetaphor.svelte (P2, Week 6)
6. SettingsAntiPatterns.svelte (P2, Week 6)
7. SettingsEnhancement.svelte (P2, Week 6)
8. SettingsForeman.svelte (P2, Week 6)
9. SettingsHealth.svelte (P2, Week 6)
10. SettingsAdvanced.svelte (P2, Week 6)
11. SettingsPanel.svelte (P0, Week 1 - container)

**Story Bible (ARCHITECT Mode)** (7 components):
1. StoryBibleWizard.svelte (P1, Week 2)
2. BeatSheetEditor.svelte (P1, Week 2)
3. CharacterArcBuilder.svelte (P1, Week 2)
4. ThemeDefinition.svelte (P1, Week 2)
5. NotebookLMSelector.svelte (P2, Week 2)
6. StoryBibleProgress.svelte (P2, Week 2)
7. StoryBibleExport.svelte (P2, Week 2)

**Voice Calibration** (6 components):
1. VoiceTournamentLauncher.svelte (P1, Week 3)
2. VoiceVariantGrid.svelte (P1, Week 3)
3. VoiceComparisonView.svelte (P1, Week 3)
4. VoiceVariantSelector.svelte (P1, Week 3)
5. VoiceBundleGenerator.svelte (P1, Week 3)
6. VoiceEvolutionChart.svelte (P2, Week 3)

**Director Mode** (16 components):
1. ScaffoldGenerator.svelte (P1, Week 4)
2. StructureVariantSelector.svelte (P1, Week 4)
3. SceneVariantGrid.svelte (P1, Week 4)
4. SceneComparison.svelte (P1, Week 4)
5. SceneHybridCreator.svelte (P1, Week 4)
6. EnhancementPanel.svelte (P1, Week 4)
7. ActionPromptView.svelte (P1, Week 4)
8. SixPassEnhancement.svelte (P1, Week 4)
9. SceneScoreBreakdown.svelte (P2, Week 4)
10. MetaphorAnalyzer.svelte (P2, Week 4)
11. AntiPatternDetector.svelte (P2, Week 4)
12. QuickSceneGenerator.svelte (P2, Week 4)
13. SceneVersionHistory.svelte (P2, Week 4)
14. ScaffoldEnrichmentPreview.svelte (P2, Week 4)
15. SceneExport.svelte (P2, Week 4)
16. BeatProgressTracker.svelte (P2, Week 4)

**Graph Health** (7 components):
1. HealthDashboard.svelte (P1, Week 5)
2. HealthReportViewer.svelte (P1, Week 5)
3. TrendChart.svelte (P2, Week 5)
4. ThemeResonanceOverride.svelte (P2, Week 5)
5. HealthCheckConfig.svelte (P2, Week 5)
6. ConflictResolutionPanel.svelte (P2, Week 5)
7. BeatDeviationAlert.svelte (P2, Week 5)

**NotebookLM Integration** (3 components):
1. NotebookLMPanel.svelte (P2, Week 2 or Week 5)
2. NotebookLMQuery.svelte (P2, Week 2 or Week 5)
3. NotebookLMStatus.svelte (P2, Week 2 or Week 5)

**Knowledge Graph** (8 components):
1. GraphPanel.svelte (P0, Week 1 - basic exists, advanced Week 5)
2. GraphVisualization.svelte (P1, Week 5)
3. GraphSearch.svelte (P2, Week 5)
4. GraphExport.svelte (P2, Week 6)
5. GraphConflictViewer.svelte (P2, Week 5)
6. GraphEntityDetails.svelte (P2, Week 5)
7. GraphRelationshipEditor.svelte (P3, Week 6)
8. GraphVersionHistory.svelte (P3, Future)

**Session Management** (3 components):
1. SessionList.svelte (P2, Week 5)
2. SessionViewer.svelte (P2, Week 5)
3. SessionExport.svelte (P3, Week 6)

**Foreman** (6 components):
1. ForemanChatPanel.svelte (P0, Week 1)
2. WorkOrderTracker.svelte (P1, Week 2)
3. KBEntryViewer.svelte (P2, Week 5)
4. ModeStatusIndicator.svelte (P1, Week 1)
5. ModelRoutingDisplay.svelte (P1, Week 1)
6. ForemanHistory.svelte (P3, Week 6)

**Infrastructure** (18 components):
1. MainLayout.svelte (P0, Week 1)
2. StudioPanel.svelte (P0, Week 1)
3. GraphPanel.svelte (P0, Week 1)
4. ForemanPanel.svelte (P0, Week 1)
5. ChatPanel.svelte (P0, Week 1)
6. Toolbar.svelte (P0, Week 1)
7. PanelResizer.svelte (P0, Week 1)
8. PanelCollapse.svelte (P0, Week 1)
9. Modal.svelte (P0, Week 1)
10. Toast.svelte (P0, Week 1)
11. LoadingSpinner.svelte (P1, Week 1)
12. ErrorBoundary.svelte (P1, Week 1)
13. FileTree.svelte (P1, existing)
14. Monaco Editor integration (P1, existing)
15. CommandPalette.svelte (P3, Week 6)
16. KeyboardShortcuts.svelte (P3, Week 6)
17. ThemeCustomizer.svelte (P3, Week 6)
18. TutorialOverlay.svelte (P3, Week 6)

**Total**: 87 components

---

## Priority Breakdown

**P0 (Critical - Week 1)**: 12 components
- Settings Panel (2): SettingsAgents, SettingsOrchestrator
- Main Layout (5): MainLayout, StudioPanel, GraphPanel (basic), ForemanChatPanel, Toolbar
- Infrastructure (5): Modal, Toast, PanelResizer, PanelCollapse, LoadingSpinner

**P1 (High - Weeks 2-4)**: 31 components
- ARCHITECT Mode (4): StoryBibleWizard, BeatSheetEditor, CharacterArcBuilder, ThemeDefinition
- VOICE Mode (4): VoiceTournamentLauncher, VoiceVariantGrid, VoiceComparisonView, VoiceVariantSelector, VoiceBundleGenerator
- DIRECTOR Mode (8): ScaffoldGenerator, StructureVariantSelector, SceneVariantGrid, SceneComparison, SceneHybridCreator, EnhancementPanel, ActionPromptView, SixPassEnhancement
- Graph Health (2): HealthDashboard, HealthReportViewer
- Infrastructure (2): ErrorBoundary, ModeStatusIndicator

**P2 (Medium - Weeks 2-5)**: 31 components
- Settings (8): All remaining settings sub-components
- Story Bible (3): NotebookLMSelector, StoryBibleProgress, StoryBibleExport
- VOICE Mode (1): VoiceEvolutionChart
- DIRECTOR Mode (8): SceneScoreBreakdown, MetaphorAnalyzer, AntiPatternDetector, QuickSceneGenerator, SceneVersionHistory, ScaffoldEnrichmentPreview, SceneExport, BeatProgressTracker
- Graph Health (4): TrendChart, ThemeResonanceOverride, HealthCheckConfig, ConflictResolutionPanel, BeatDeviationAlert
- NotebookLM (3): All NotebookLM components
- Knowledge Graph (4): GraphVisualization, GraphSearch, GraphConflictViewer, GraphEntityDetails
- Session Management (2): SessionList, SessionViewer

**P3 (Nice-to-have - Week 6+)**: 13 components
- Polish (6): KeyboardShortcuts, ThemeCustomizer, ExportManager, CommandPalette, TutorialOverlay, ProjectTemplates
- Advanced (4): GraphExport, GraphRelationshipEditor, SessionExport, ForemanHistory
- Future (3): GraphVersionHistory, SceneVersionHistory (enhanced), etc.

---

## Effort Summary

| Week | Focus | Components | Hours | Cumulative |
|------|-------|------------|-------|------------|
| **Week 1** | Critical UI (Track 1) | 5 | 18 | 18 |
| **Week 2** | ARCHITECT Mode | 7 | 40 | 58 |
| **Week 3** | VOICE_CALIBRATION Mode | 6 | 45 | 103 |
| **Week 4** | DIRECTOR Mode | 16 | 100 | 203 |
| **Week 5** | Graph Health | 7 | 50 | 253 |
| **Week 6** | Settings + Polish | 14 | 52 | 305 |

**Total**: 55 new components (32 existing from infrastructure), 305 hours (~7-8 weeks)

**Note**: Week 1 effort (18 hours) is most critical as it unblocks 80% of backend features.

---

## Design System (from UI_IMPLEMENTATION_PLAN.md)

### Visual Theme: Cyber-Noir

**Color Palette**:
```css
--primary-bg: #1a1a1a;        /* Deep charcoal */
--secondary-bg: #2d2d2d;      /* Lighter charcoal */
--accent: #00d9ff;            /* Electric blue */
--accent-hover: #00b8d9;      /* Darker electric blue */
--warning: #ffb000;           /* Amber */
--error: #ff3366;             /* Hot pink */
--success: #00ff88;           /* Neon green */
--text-primary: #ffffff;      /* High-contrast white */
--text-secondary: #a0a0a0;    /* Medium gray */
--text-muted: #666666;        /* Dark gray */
--border: #404040;            /* Subtle border */
```

**Typography**:
- **Code/Editor**: JetBrains Mono (monospace, coding-optimized)
- **UI Text**: Inter (sans-serif, clean, modern)
- **Headings**: Inter Bold
- **Body**: Inter Regular (14px base)

**Component Library**:
- SvelteKit (framework)
- TailwindCSS (utility-first CSS)
- shadcn-svelte (pre-built components)
- Lucide icons (consistent, modern icon set)

**Spacing System**:
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
--space-12: 48px;
```

**Animation**:
- **Panel transitions**: 200ms ease-in-out
- **Modal fade-in**: 150ms ease-out
- **Toast slide-in**: 300ms cubic-bezier(0.4, 0, 0.2, 1)
- **Loading spinners**: 1000ms linear infinite

---

## 4-Panel IDE Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TOOLBAR                                                                    │
│  Mode: [ARCHITECT] [VOICE] [DIRECTOR] [EDITOR] | Project | Foreman | Help  │
├──────────────┬──────────────────┬──────────────┬──────────────────────────┤
│              │                  │              │                          │
│   STUDIO     │      GRAPH       │   FOREMAN    │      CHAT                │
│   PANEL      │      PANEL       │   PANEL      │      PANEL               │
│  (280px)     │     (flex-1)     │   (320px)    │     (400px)              │
│              │                  │              │                          │
│  ┌────────┐  │  ┌────────────┐  │  Work Orders │  Foreman Chat            │
│  │ Card 1 │  │  │  Knowledge │  │  ┌────────┐  │  ┌────────────────────┐  │
│  │Create  │  │  │   Graph    │  │  │Order 1 │  │  │ User: Create scene │  │
│  │Story   │  │  │  Live Viz  │  │  │Status  │  │  ├────────────────────┤  │
│  │Bible   │  │  │            │  │  └────────┘  │  │ Foreman: Scaffold? │  │
│  └────────┘  │  │            │  │              │  │ [Using claude...] │  │
│              │  │            │  │  KB Entries  │  └────────────────────┘  │
│  ┌────────┐  │  │            │  │  ┌────────┐  │                          │
│  │ Card 2 │  │  │  Health    │  │  │Entry 1 │  │  Input: [_________]     │
│  │Launch  │  │  │  Status    │  │  │Theme   │  │  [Send]                 │
│  │Voice   │  │  │  ●Green    │  │  └────────┘  │                          │
│  │Tour    │  │  │            │  │              │  Model Routing:          │
│  └────────┘  │  └────────────┘  │  Mode Status │  📋 Coordinator (local) │
│              │                  │  DIRECTOR    │  🧠 Advisor (cloud)     │
│  Collapsible │  Collapsible     │  Collapsible │  Always Visible          │
│  [<]         │  [<]             │  [<]         │                          │
└──────────────┴──────────────────┴──────────────┴──────────────────────────┘
```

**Panel Widths** (default):
- Studio: 280px (collapsible)
- Graph: flex-1 (grows/shrinks)
- Foreman: 320px (collapsible)
- Chat: 400px (always visible, min 300px)

**Resize Behavior**:
- All panels except Chat can be resized via drag handles
- Chat panel always visible (minimum 300px width)
- Panels can collapse to 40px icon bar
- Collapsed panels show mode icon + badge (e.g., "3 work orders")

**Panel Content by Foreman Mode**:

### ARCHITECT Mode
**Studio Panel**:
- "Create Story Bible" card
- "Define Beats" card
- "Build Protagonist" card
- "Register NotebookLM" card

**Graph Panel**:
- Story Bible entity graph (Protagonist, Theme, Beats)
- Completeness indicator (5/5 foundation docs)

**Foreman Panel**:
- Work Order: "Complete Story Bible"
- KB Entries: Story Bible decisions
- Mode Status: "ARCHITECT (Step 2/7)"

### VOICE_CALIBRATION Mode
**Studio Panel**:
- "Launch Voice Tournament" card
- "Review Variants" card
- "Generate Voice Bundle" card

**Graph Panel**:
- Voice entity graph (Voice characteristics, Anti-Patterns, Phase Evolution)
- Voice Bundle status

**Foreman Panel**:
- Work Order: "Select winning voice variant"
- KB Entries: Voice decisions
- Mode Status: "VOICE_CALIBRATION (Tournament running...)"

### DIRECTOR Mode
**Studio Panel**:
- "Create Scaffold" card
- "Generate Scene" card
- "Enhance Scene" card
- "View Health" card

**Graph Panel**:
- Scene entity graph (Characters, Plot events, World rules)
- Health indicator (green/yellow/red)

**Foreman Panel**:
- Work Orders: "Create Scene 1.1", "Enhance Scene 1.1"
- KB Entries: Scene decisions
- Mode Status: "DIRECTOR (Scene 1.1 in progress)"

---

## API Coverage

**Total Backend Endpoints**: 88 across 13 categories

**UI Coverage by Week**:

| Category | Endpoints | Week 1 | Week 2 | Week 3 | Week 4 | Week 5 | Week 6 |
|----------|-----------|--------|--------|--------|--------|--------|--------|
| **Agents** | 1 | - | - | ✓ | ✓ | ✓ | ✓ |
| **Director** | 16 | - | - | - | ✓✓✓ | ✓✓✓ | ✓✓✓ |
| **Files** | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Foreman** | 9 | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓✓ | ✓✓✓ |
| **Graph** | 6 | ✓ | ✓ | ✓ | ✓ | ✓✓✓ | ✓✓✓ |
| **Health** | 7 | - | - | - | - | ✓✓✓ | ✓✓✓ |
| **Metabolism** | 2 | - | - | - | - | ✓ | ✓ |
| **NotebookLM** | 7 | - | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓✓ |
| **Orchestrator** | 4 | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ |
| **Session** | 7 | - | - | - | - | ✓✓ | ✓✓✓ |
| **Settings** | 8 | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ |
| **Story Bible** | 7 | - | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ |
| **Voice Cal** | 7 | - | - | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ |

**Legend**: ✓ = Partial coverage, ✓✓ = Good coverage, ✓✓✓ = Complete coverage

---

## Testing Strategy

### Week 1 Testing (Critical UI)
**Test Scenarios**:
1. **API Key Configuration**:
   - Can enter OpenAI, Anthropic, DeepSeek, Qwen API keys
   - Keys saved to settings.yaml securely
   - Can verify API key validity (test connection)
   - Can delete/update API keys

2. **Model Orchestrator**:
   - Can select quality tier (Budget/Balanced/Premium)
   - Can see cost estimation for each tier
   - Can enable/disable orchestrator
   - Can set monthly budget

3. **4-Panel Layout**:
   - Panels render correctly at default widths
   - Can resize panels via drag handles
   - Can collapse/expand panels
   - Chat panel always visible
   - Layout persists on reload

4. **Foreman Chat**:
   - Can send message to Foreman
   - Receives response with model routing indicator (📋 local, 🧠 cloud)
   - Can switch Foreman modes
   - Chat history persists

### Week 2-6 Testing (Feature UI)
**Test Categories**:
1. **Functional Testing**: Every component works as specified
2. **Integration Testing**: Components communicate correctly with backend API
3. **E2E Testing**: Complete workflows (ARCHITECT → VOICE → DIRECTOR)
4. **Performance Testing**: Large Knowledge Graphs, 25-variant tournaments
5. **Accessibility Testing**: Keyboard navigation, screen reader support

**Automated Tests**:
- Playwright for E2E testing
- Vitest for component unit testing
- API integration tests with mock backend

---

## Documentation

**Related Specifications**:
- [UI_GAP_ANALYSIS.md](UI_GAP_ANALYSIS.md) - Complete backend vs UI coverage analysis (21K words)
- [UI_COMPONENT_INVENTORY.md](UI_COMPONENT_INVENTORY.md) - All 87 components with dependencies (30K words)
- [UI_IMPLEMENTATION_PLAN.md](UI_IMPLEMENTATION_PLAN.md) - Original infrastructure plan (30K words)
- [SETTINGS_PANEL_IMPLEMENTATION_PLAN.md](SETTINGS_PANEL_IMPLEMENTATION_PLAN.md) - Settings UI specification (10K words)
- [SETTINGS_CONFIGURATION.md](SETTINGS_CONFIGURATION.md) - Complete settings spec, 11 categories (20K words)
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Main architecture document with UI/UX strategy section

**Quick Reference**:
- **Roadmap**: [04_roadmap.md](../04_roadmap.md) - Phase tracking and 3-track parallel development
- **Backend Services**: [BACKEND_SERVICES.md](../BACKEND_SERVICES.md) - Complete API reference
- **Director Mode**: [DIRECTOR_MODE_SPECIFICATION.md](DIRECTOR_MODE_SPECIFICATION.md) - Full technical specification
- **Phase 3E**: [PHASE_3_ORCHESTRATOR_COMPLETION.md](../dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md) - Model Orchestrator implementation

---

## Next Steps

**Immediate Actions** (Week 1 Priority):
1. ✅ Create comprehensive UI implementation plan (this document)
2. ⏳ Update documentation (ARCHITECTURE.md, 04_roadmap.md) ✅ DONE
3. ⏳ Organize /docs folder structure
4. ⏳ Push all documentation to GitHub
5. ⏳ **START Track 1 Critical UI Implementation**:
   - SettingsAgents.svelte (3h)
   - SettingsOrchestrator.svelte (3h)
   - MainLayout.svelte (6h)
   - ForemanChatPanel.svelte (4h)
   - StudioPanel.svelte (2h)

**Week 1 Deliverable**: Writers can configure API keys, select quality tier, chat with Foreman, and navigate modes.

**Week 2-6 Deliverables**: Complete feature UI following Foreman modes (ARCHITECT → VOICE → DIRECTOR → Health).

**Success Criteria**: All 88 backend API endpoints accessible via UI, complete writer workflow from Story Bible to finished manuscript enabled.

---

**Status**: Ready for implementation
**Version**: 2.0 (Complete)
**Last Updated**: November 25, 2025
**Priority**: Start Track 1 (Week 1) immediately
