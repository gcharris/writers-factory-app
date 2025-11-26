# Implementation Roadmap (V4.2 Updated)

## Phase 1: The Foundation (✅ Done)
**Goal:** Core App Infrastructure.
1.  **Setup:** Tauri + Svelte + Python Backend.
2.  **Graph Engine:** NetworkX + SQLite implemented.
3.  **UI:** Editor, Graph Panel, Agent Panel built.
4.  **Tournament:** Basic drafting logic functional.

## Phase 2: The Oracle (✅ Done)
**Goal:** NotebookLM Integration.
1.  **MCP:** Bridge connected via `notebooklm-mcp`.
2.  **Integration:** App can query research notebooks.
3.  **Verification:** Proven to work with live Google NotebookLM accounts.

## Phase 2B: Voice Calibration (✅ Done)
**Goal:** Tournament-based voice discovery before scene writing.
1.  **Agent Registry:** Dynamic scanning of available API keys to determine which agents are ready.
2.  **Voice Tournament:** Multi-agent competition with 5-variant multiplier (ACTION, CHARACTER, DIALOGUE, ATMOSPHERIC, BALANCED strategies).
3.  **Voice Reference Bundle:** Generated markdown files (Gold-Standard, Anti-Patterns, Phase-Evolution) that travel with every scene writing call.
4.  **Foreman Mode Transitions:** ARCHITECT → VOICE_CALIBRATION → DIRECTOR with validation guards.

## Phase 3: The Metabolism (✅ Done)
**Goal:** Stateful Session & Memory Digestion.
1.  **The Foreman:** Ollama-powered intelligent creative partner with work order tracking.
2.  **Foreman KB:** SQLite-backed knowledge base for crystallized decisions.
3.  **Consolidator Service:** Promotes KB entries to Knowledge Graph with category mapping.
4.  **Session Persistence:** Conversation history survives restarts.

## Phase 3B: Director Mode (✅ Backend Complete)
**Goal:** Scene-by-scene drafting with voice consistency.

### Service 1: Scene Analyzer ✅
*Foundation service - scoring framework everything else depends on*
- **5-Category Rubric:** Voice Authenticity (30), Character Consistency (20), Metaphor Discipline (20), Anti-Pattern Compliance (15), Phase Appropriateness (15)
- **Vanilla Tests:** Authenticity, Purpose, Fusion tests reference Voice Bundle (not hard-coded)
- **Automated Detection:** Regex patterns for zero-tolerance violations, domain saturation
- **Grade Thresholds:** A (92+), A- (85+), B+ (80+) → determines enhancement mode
- **API:** `/director/scene/analyze`, `/director/scene/compare`, `/director/scene/detect-patterns`, `/director/scene/analyze-metaphors`

### Service 2: Scaffold Generator ✅
*Strategic context assembly from KB and Story Bible*
- **Two-Stage Flow:** Draft Summary → Optional Enrichment → Full Scaffold
- **Gold Standard Structure:** Chapter Overview, Strategic Context, Success Criteria, Continuity Checklist
- **KB Integration:** Pulls decisions, constraints, previous scene events
- **NotebookLM Queries:** Optionally enriches with research notebook data
- **API:** `/director/scaffold/draft-summary`, `/director/scaffold/enrich`, `/director/scaffold/generate`

### Service 3: Scene Writer ✅
*Multi-model drafting with Voice Bundle injection*
- **Structure Variants:** 5 different chapter layouts before writing prose
- **Voice Bundle Context:** Gold Standard + Anti-Patterns + Phase Evolution injected every call
- **Tournament Mode:** 3+ models compete (Claude, GPT-4o, DeepSeek), 5 strategies each
- **5 Writing Strategies:** ACTION, CHARACTER, DIALOGUE, ATMOSPHERIC, BALANCED
- **Auto-Scoring:** All variants scored by Scene Analyzer, ranked
- **API:** `/director/scene/structure-variants`, `/director/scene/generate-variants`, `/director/scene/create-hybrid`, `/director/scene/quick-generate`

### Service 4: Scene Enhancement ✅
*Two modes based on score threshold*
- **Action Prompt (85+):** Surgical OLD → NEW fixes from violations
- **6-Pass Enhancement (70-84):** Sensory Anchoring → Verb Promotion → Metaphor Rotation → Voice Embed → Italics Gate → Voice Authentication
- **Rewrite (<70):** Returns "rewrite_needed" status
- **API:** `/director/scene/enhance`, `/director/scene/action-prompt`, `/director/scene/apply-fixes`, `/director/scene/six-pass`

### Implementation Status
- ✅ All 4 backend services implemented
- ✅ 16 API endpoints available
- ✅ Foreman orchestration integration (7 action handlers)
- ✅ LLM scoring reliability fixes (JSON parsing, prompt improvements)
- 🔲 Frontend UI (Phase 5)

See: [DIRECTOR_MODE_SPECIFICATION.md](specs/DIRECTOR_MODE_SPECIFICATION.md) for full technical details

## Phase 3C: Settings-Driven Director Mode (✅ Complete)
**Goal:** Transform hard-coded Explants patterns into universal framework.
**Priority:** P0 Critical - Enables any writer's style
**Effort:** 10-13 hours

### Problem
Current Director Mode has hard-coded rules from Explants project (Mickey Bardot voice):
- Similes penalized → But some writers love similes
- Domain saturation = 30% → Too restrictive for expertise-driven characters
- "despite the" = violation → Common in literary fiction
- 6-pass always → Some writers want conservative enhancement

### Solution: 3-Tier Settings System
1. **Settings Service** - SQLite-backed with project → global → default resolution
2. **Voice Bundle YAML** - Auto-generated `voice_settings.yaml` during Voice Calibration
3. **Dynamic Services** - Scene Analyzer and Enhancement load settings at runtime

### Tasks
1. ✅ **Settings Service** - 3-tier resolution, validation
2. ✅ **Voice Calibration Integration** - Generate `voice_settings.yaml`
3. ✅ **Scene Analyzer Refactor** - Dynamic weights, patterns, thresholds
4. ✅ **Scene Enhancement Refactor** - Dynamic enhancement thresholds
5. ✅ **VoiceBundleContext Update** - Load structured settings

**See**: [PHASE_3C_SETTINGS_IMPLEMENTATION.md](dev_logs/PHASE_3C_SETTINGS_IMPLEMENTATION.md)

## Phase 3D: Graph Health Service (✅ Complete)
**Goal:** Macro-level structural validation at chapter/act/manuscript level.
**Priority:** P1 High - Completes Director Mode quality loop
**Effort:** 12-15 hours
**Depends On:** ✅ Phase 3C (Settings Service - Complete)
**Status:** All 7 health checks implemented with cloud-native LLM analysis

### Strategic Decisions
**Full LLM-Powered Analysis** - Maximum accuracy with no resource limitations:
1. **Timeline Consistency** - Full semantic analysis for character locations, world rules, dropped threads
2. **Theme Resonance** - Hybrid automated LLM scoring + manual writer override capability
3. **Check Frequency** - Auto-trigger after every chapter assembly (customizable via Foreman proactiveness)
4. **Report Storage** - SQLite persistence for historical tracking and longitudinal analysis (365-day retention)

### Two-Tier Quality System
1. **Tier 1 (Immediate)** - Scene Analyzer validates individual scenes
2. **Tier 2 (Async)** - Graph Health Service validates structure across chapters

### Health Check Categories
**A. Structural Integrity**
- ✅ Pacing Failure Detection (tension plateau analysis with LLM intent detection)
- ✅ Beat Progress Validation (15-beat Save the Cat! structure compliance)
- ✅ Plot/Timeline Consistency (world rules + character locations) - LLM-powered

**B. Character Arc Health**
- ✅ Fatal Flaw Challenge Monitoring (dual-mode: explicit + LLM fallback)
- ✅ Cast Function Verification (LLM character analysis)

**C. Thematic Health**
- ✅ Symbolic Layering (symbol recurrence + meaning evolution with LLM analysis)
- ✅ Theme Resonance Score (hybrid LLM + manual override)

### Implementation Status
✅ **All 7 Health Checks** - Pacing, Beat Progress, Symbolic, Timeline, Theme, Flaw, Cast Function
✅ **Settings Configuration** - Timeline, theme, and reporting settings
✅ **LLM Query Routing** - 9+ provider support with graceful Ollama fallback
✅ **Configurable Models** - 7 health check models in settings.yaml
✅ **Knowledge Graph Schema** - SCENE, CHAPTER, BEAT nodes in schema.py
✅ **API Endpoints** - 7 endpoints implemented:
  - `POST /health/check` - Run health checks
  - `GET /health/report/{id}` - Get detailed report
  - `GET /health/reports` - List all reports (paginated)
  - `GET /health/trends/{metric}` - Historical trends
  - `POST /health/theme/override` - Manual theme override
  - `GET /health/theme/overrides` - List overrides
  - `GET /health/export/{id}` - Export as JSON/markdown
✅ **Tests** - Unit tests for all health checks

**See**:
- [PHASE_3D_GRAPH_HEALTH_IMPLEMENTATION.md](dev_logs/PHASE_3D_GRAPH_HEALTH_IMPLEMENTATION.md)
- [PHASE_3D_COMPLETION_CLOUD.md](dev_logs/PHASE_3D_COMPLETION_CLOUD.md)

## Phase 3E: Intelligent Model Orchestration (✅ Complete)
**Goal:** Transform single-model local system into intelligent multi-model orchestrator.
**Priority:** P0 Critical - Unlocks cloud AI features
**Effort:** ~6 hours (2 hours per sub-phase)
**Status:** ✅ Complete (Phases 1-3 implemented)

### Phase 3E.1: Dual-Model Foreman ✅
**Intelligent task routing between fast local (coordination) and powerful cloud (strategic reasoning)**

**Implementation:**
- ✅ 8 task types with automatic classification (coordinator, health_check_review, voice_calibration_guidance, etc.)
- ✅ Multi-provider cloud support (OpenAI, Anthropic, DeepSeek, Qwen)
- ✅ Fully configurable model assignments (all in settings.yaml, zero hardcoded)
- ✅ Graceful fallback to local Ollama models when API keys missing

**Files:** [backend/agents/foreman.py](../backend/agents/foreman.py) (~300 lines added)

### Phase 3E.2: Cloud-Native Health Checks ✅
**Upgraded 4 placeholder health checks to use cloud AI with configurable assignments**

**Implementation:**
- ✅ Timeline Consistency - Full LLM semantic analysis (claude-3-5-sonnet)
- ✅ Theme Resonance - Hybrid LLM + manual override (gpt-4o)
- ✅ Flaw Challenges - Dual-mode explicit + LLM fallback (deepseek-chat)
- ✅ Cast Function - LLM character analysis (qwen-plus)
- ✅ LLM query routing infrastructure (9+ providers)
- ✅ 7 configurable health check models

**Files:** [backend/services/graph_health_service.py](../backend/services/graph_health_service.py) (~500 lines added)

### Phase 3E.3: Model Orchestrator ✅
**Automatic model selection with quality tiers - one setting replaces 15 manual assignments**

**Implementation:**
- ✅ Model capabilities matrix (8 models with quality scores, costs, strengths)
- ✅ 3 quality tiers: Budget ($0/month), Balanced ($0.50-1/month), Premium ($3-5/month)
- ✅ API key detection with automatic fallback to local
- ✅ Budget enforcement and cost estimation
- ✅ 4 API endpoints: `/orchestrator/capabilities`, `/estimate-cost`, `/recommendations/{task}`, `/current-spend`
- ✅ Foreman integration with orchestrator toggle

**Files:**
- [backend/services/model_capabilities.py](../backend/services/model_capabilities.py) (~230 lines)
- [backend/services/model_orchestrator.py](../backend/services/model_orchestrator.py) (~300 lines)

**Cost Impact:** $0 (Budget tier) to $5/month (Premium tier). Most writers: ~$0.50/month (Balanced).

**See:**
- [PHASE_3E_COMPLETION_SUMMARY.md](dev_logs/PHASE_3E_COMPLETION_SUMMARY.md) - Phases 1-2
- [PHASE_3_ORCHESTRATOR_COMPLETION.md](dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md) - Phase 3
- [CONFIGURABLE_MODEL_ASSIGNMENTS.md](../CONFIGURABLE_MODEL_ASSIGNMENTS.md) - Configuration guide

## Phase 4: Multi-Model Tournament (Planned)
**Goal:** Consensus detection for critical decisions.
**Priority:** P2 Optional - 90% value delivered by Phase 3E
**Effort:** 8-10 hours

### Features (Planned)
1. **Critical Decision Detection** - Automatically identify high-stakes tasks
2. **Parallel Querying** - Query 3+ models simultaneously
3. **Consensus Detection** - High confidence when models agree
4. **Dispute Flagging** - Flag for human review when models disagree

**Note:** Phase 3E already delivers Budget/Balanced/Premium quality tiers and automatic model selection. Phase 4 adds tournament-style multi-model querying for critical decisions only.

**See:** [PHASE_3E_PHASES_3_4_IMPLEMENTATION_PLAN.md](dev_logs/PHASE_3E_PHASES_3_4_IMPLEMENTATION_PLAN.md)

## Phase 5: UI/UX Implementation (🚧 40% Complete)
**Goal:** Production-ready user interface with complete feature coverage.
**Priority:** P0 Critical - Makes backend features accessible
**Strategy:** 3-Track Parallel Development
**Status:** Track 1 Complete, Track 3 Phases 1-3 Complete

### Critical Insight: Settings Panel is a Blocker, Not Polish
**Problem:** 80% of backend features (40+ hours of development) require cloud API keys to function:
- Voice Calibration tournaments (3 models minimum)
- Director Mode scene generation (Claude, GPT-4o, DeepSeek)
- Model Orchestrator activation (Budget/Balanced/Premium tiers)
- Graph Health with optimal models (Claude for timeline, GPT-4o for themes)

**Without SettingsAgents.svelte (API key configuration):** Writers cannot access any cloud features.

**ROI:** 6-8 hours of Settings UI work unlocks ~40 hours of backend functionality.

### 3-Track Parallel Development Strategy

#### Track 1: Critical UI ✅ COMPLETE
**Goal:** Unblock backend features and enable basic functionality

**Components (11 components, 1,750 lines):**
1. ✅ **SettingsAgents.svelte** - API key configuration (BLOCKER REMOVAL)
2. ✅ **SettingsOrchestrator.svelte** - Quality tier selection (Budget/Balanced/Premium)
3. ✅ **MainLayout.svelte** - 4-panel IDE layout (Studio, Graph, Foreman, Chat)
4. ✅ **ForemanChatPanel.svelte** - Chat interface for Foreman
5. ✅ **StudioPanel.svelte** - Studio cards and mode selection
6. ✅ **GraphPanel.svelte** - Knowledge Graph visualization
7. ✅ **AgentRegistryPanel.svelte** - Available agents display
8. ✅ **NotebookRegistration.svelte** - NotebookLM integration
9. ✅ **StoryBibleEditor.svelte** - 15-beat structure editor
10. ✅ **VoiceReferenceView.svelte** - Voice Bundle display
11. ✅ **ProjectSelector.svelte** - Project management

**Impact:** All cloud features now accessible. Model Orchestrator active.

#### Track 2: Backend Completion ✅ COMPLETE
**Goal:** Finish Phase 3D and Phase 4 (optional)

**Completed:**
- ✅ Phase 3D: All 7 health checks (Pacing, Beat Progress, Symbolic Layering, Timeline, Theme, Flaw, Cast)
- ✅ Phase 3D: Knowledge Graph schema extension (SCENE, CHAPTER, BEAT nodes)
- ✅ Phase 3D: 7 API endpoints
- ✅ Phase 3E: Model Orchestrator (Budget/Balanced/Premium tiers)
- 🔲 Phase 4: Multi-model tournament (optional, deferred)

**Status:** Backend feature-complete for Phase 5 UI work.

#### Track 3: Feature UI (Weeks 2-6) - FOLLOWS FOREMAN MODES ✅ 95% Complete

**Phased Approach:**
1. ✅ **Phase 1 (ARCHITECT Mode UI):** Story Bible creation (3 components, 890 lines)
   - StoryBibleEditor.svelte (467 lines)
   - StoryBibleSidebar.svelte (235 lines)
   - BeatCard.svelte (188 lines)

2. ✅ **Phase 2 (VOICE_CALIBRATION Mode UI):** Tournament interface (6 components, 1,250 lines)
   - VoiceTournamentPanel.svelte (347 lines)
   - VoiceVariantCard.svelte (289 lines)
   - StrategyComparison.svelte (221 lines)
   - VoiceReferenceView.svelte (185 lines)
   - VoiceGoldStandard.svelte (142 lines)
   - VoiceAntiPatterns.svelte (66 lines)

3. ✅ **Phase 3 (DIRECTOR Mode UI):** Scene creation (8 components, 6,751 lines)
   - ScaffoldGenerator.svelte (1,231 lines) - Two-stage scaffold flow
   - ActionPromptView.svelte (830 lines) - Surgical OLD → NEW fixes
   - SixPassEnhancement.svelte (781 lines) - 6-pass progress tracker
   - SceneScoreBreakdown.svelte (765 lines) - 100-point rubric details
   - SceneVariantGrid.svelte (733 lines) - Tournament results display
   - StructureVariantSelector.svelte (712 lines) - 5 structural layouts
   - EnhancementPanel.svelte (645 lines) - Enhancement mode selector
   - SceneComparison.svelte (552 lines) - Side-by-side variant comparison
   - **API Client:** +457 lines (15+ Director Mode methods)
   - **State Management:** +45 lines (stores.js)

4. ✅ **Phase 4 (Graph Health UI):** Dashboard and reports (4 components, ~107KB) - COMPLETE
   - GraphHealthDashboard.svelte (29KB) - 7 health check categories with run/view
   - HealthReportDetail.svelte (30KB) - Detailed report with grouped warnings
   - HealthTrends.svelte (21KB) - SVG trend charts with date picker
   - ThemeOverridePanel.svelte (25KB) - Manual theme score overrides

5. ✅ **Phase 5 (Settings + Polish):** All 9 settings tabs implemented - COMPLETE
   - SettingsSquad.svelte - Squad selection and tournament models (NEW - Nov 2025)
   - SettingsAgents.svelte - API key configuration
   - SettingsOrchestrator.svelte - Quality tier selection
   - SettingsScoring.svelte - Scene scoring weights
   - SettingsVoice.svelte - Voice calibration settings
   - SettingsEnhancement.svelte - Enhancement thresholds
   - SettingsForeman.svelte - Foreman behavior
   - SettingsHealth.svelte - Health check configuration
   - SettingsAdvanced.svelte - Context window, expert mode

### UI Component Coverage
**Total Components Required:** 87
**Completed:** 55+ components (~63%)
**In Progress:** 0 components
**Remaining:** ~32 components (37%)

**Completed by Category:**
- ✅ **Critical UI (Track 1):** 11/11 components (100%)
- ✅ **ARCHITECT Mode:** 3/3 components (100%)
- ✅ **VOICE_CALIBRATION Mode:** 6/6 components (100%)
- ✅ **DIRECTOR Mode:** 8/8 components (100%)
- ✅ **Graph Health UI:** 4/4 components (100%)
- ✅ **Settings Panels:** 9/9 components (100%)
- ✅ **Squad System UI:** 3/3 components (100%) - NEW Nov 2025

**Remaining by Category:**
- 🔲 **NotebookLM Integration:** 0/3 components (0%)
- 🔲 **Knowledge Graph Advanced:** 0/5 components (0%)
- 🔲 **Session Management:** 0/3 components (0%)
- 🔲 **Foreman Work Orders:** 0/4 components (0%)
- 🔲 **Polish & UX:** 0/6 components (0%)

### Documentation
- **Phase 3-5 Completion Summary:** [PHASE_3_5_COMPLETION_SUMMARY.md](dev_logs/PHASE_3_5_COMPLETION_SUMMARY.md)
- **Complete UI Gap Analysis:** [UI_GAP_ANALYSIS.md](specs/UI_GAP_ANALYSIS.md)
- **Complete Component Inventory:** [UI_COMPONENT_INVENTORY.md](specs/UI_COMPONENT_INVENTORY.md)
- **Original Infrastructure Plan:** [UI_IMPLEMENTATION_PLAN.md](specs/UI_IMPLEMENTATION_PLAN.md)
- **Settings Panel Specification:** [SETTINGS_PANEL_IMPLEMENTATION_PLAN.md](specs/SETTINGS_PANEL_IMPLEMENTATION_PLAN.md)
- **Settings Configuration:** [SETTINGS_CONFIGURATION.md](specs/SETTINGS_CONFIGURATION.md)

### Effort Estimates
- ✅ **Track 1 (Critical UI):** 18 hours (COMPLETE)
- ✅ **Track 3 Phases 1-5:** ~90 hours (COMPLETE - All Foreman modes + Health + Settings)
- ✅ **Squad System UI:** ~10 hours (COMPLETE - Nov 2025)
- 🔲 **Remaining UI Components:** ~80 hours (NotebookLM, KG Advanced, Session, Foreman Work Orders, Polish)
- **Total Remaining:** ~80 hours (~2 weeks)

**Current Priority:** NotebookLM Integration - 3 components, ~15 hours

## Phase 6: Polish & Release
1.  **Packaging:** Build `.dmg` / `.exe` installers.
2.  **Optimizations:** Lazy loading for large graphs.
3.  **Plugins:** External agent registry.
4.  **Documentation:** User guides and quick start tutorials.
5.  **Testing:** End-to-end workflow validation.
