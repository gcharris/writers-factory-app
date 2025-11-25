# Settings Configuration Panel Implementation Plan

**Version**: 1.0
**Status**: Draft
**Based on**: `SETTINGS_CONFIGURATION.md`, `SETTINGS CONFIGURATION Comments.md`, `CONFIGURABLE_MODEL_ASSIGNMENTS.md`

## Overview
This document outlines the plan for implementing the **Settings Configuration Panel**, a critical UI component that allows writers to customize the Writers Factory behavior. It aggregates requirements from core specifications, model assignment configs, and advanced architectural comments.

## 1. Component Architecture

### 1.1 Core Component
**`frontend/src/lib/components/settings/SettingsPanel.svelte`**
-   **Type**: Modal or Full-Screen Overlay (configurable).
-   **Layout**: Sidebar navigation (Categories) + Main Content Area (Settings Forms).
-   **State**: Fetches settings on mount, maintains local dirty state, saves on "Apply" or auto-save.

### 1.2 Sub-Components
To maintain maintainability, each category will be a separate component:
-   `SettingsAgents.svelte`: API keys, model selection, tournament roster.
-   `SettingsScoring.svelte`: Rubric weights (linked sliders), presets.
-   `SettingsVoice.svelte`: Strictness levels, authentic/purpose/fusion tests.
-   `SettingsMetaphor.svelte`: Domain saturation, simile tolerance.
-   `SettingsAntiPatterns.svelte`: Zero-tolerance lists, custom patterns.
-   `SettingsEnhancement.svelte`: Thresholds, aggressiveness.
-   `SettingsForeman.svelte`: Behavior (proactiveness), context window.
-   `SettingsOrchestrator.svelte`: **Phase 3E** - Quality tiers, budget controls, cost estimation.
-   `SettingsTournament.svelte`: **Phase 3E** - Multi-model consensus configuration.
-   `SettingsHealth.svelte`: Graph health check thresholds (pacing, beats).
-   `SettingsAdvanced.svelte`: RAG strategy, file watching, AI safety.

### 1.3 Shared UI Elements
-   `SettingSlider.svelte`: For numerical ranges (e.g., weights, thresholds).
-   `SettingDropdown.svelte`: For discrete options (e.g., models, strictness).
-   `SettingToggle.svelte`: For boolean flags.
-   `SettingSecret.svelte`: For API keys (mask/unmask/test).
-   `CostEstimator.svelte`: **Phase 3E** - Real-time cost tracking widget (progress bar, spend display, warnings).

## 2. Detailed Category Specifications

### 2.1 Agents & Models
*Combines `SETTINGS_CONFIGURATION.md` (Cat 1) and `CONFIGURABLE_MODEL_ASSIGNMENTS.md`*
-   **API Keys**: OpenAI, Anthropic, Google, DeepSeek, Mistral, XAI.
    -   *Feature*: "Test Connection" button for each.
-   **Model Assignments**:
    -   **Foreman Model**: Dropdown (Local vs. Cloud options).
    -   **Tournament Agents**: Multi-select checkbox list.
    -   **Task-Specific Overrides** (Advanced): Accordion to set specific models for `theme_analysis`, `conflict_resolution`, etc.

### 2.2 Scoring & Rubrics
*Ref: `SETTINGS_CONFIGURATION.md` (Cat 2)*
-   **Presets Dropdown**: Literary Fiction, Commercial Thriller, Genre Romance, Balanced.
-   **Category Weights**: 5 Linked Sliders (Voice, Character, Metaphor, Anti-Pattern, Phase).
    -   *Logic*: Changing one adjusts others to maintain Sum=100.

### 2.3 Voice & Metaphor
*Ref: `SETTINGS_CONFIGURATION.md` (Cat 3 & 4)*
-   **Voice Strictness**: Dropdowns (Low/Medium/High) for Authenticity, Purpose, Fusion.
-   **Metaphor Discipline**:
    -   Saturation Threshold: Slider (20-50%).
    -   Simile Tolerance: Slider (0-5).
    -   Min Domains: Slider (2-6).

### 2.4 Anti-Patterns
*Ref: `SETTINGS_CONFIGURATION.md` (Cat 5)*
-   **System Patterns**: List view with toggles to ignore specific patterns (e.g., "despite the").
-   **Custom Patterns**: "Add Pattern" button -> Input for pattern string + severity level.

### 2.5 Enhancement Pipeline
*Ref: `SETTINGS_CONFIGURATION.md` (Cat 6)*
-   **Thresholds**: Sliders for Auto-Enhance, Action Prompt, 6-Pass, Rewrite.
-   **Aggressiveness**: Dropdown (Conservative/Medium/Aggressive).

### 2.6 Foreman & Advanced
*Ref: `SETTINGS_CONFIGURATION.md` (Cat 8, 9) & `Comments.md`*
-   **Behavior**: Sliders/Dropdowns for Proactiveness, Challenge Intensity.
-   **Context**:
    -   Max History: Slider (10-50).
    -   KB Context Limit: Slider (500-2000 tokens).
    -   **RAG Strategy** (New): Dropdown (Vector, Keyword, Hybrid).
    -   **File Watcher** (New): Dropdown (Immediate, Polling).

### 2.7 Graph Health
*Ref: `SETTINGS_CONFIGURATION.md` (Cat 10)*
-   **Models**: Dropdown for Health Check Model.
-   **Thresholds**: Sliders for Pacing Plateau, Beat Deviation, Flaw Challenge Frequency.

### 2.8 AI Intelligence (Phase 3E)
*Ref: `PHASE_3E_PHASES_3_4_IMPLEMENTATION_PLAN.md` + `SETTINGS_CONFIGURATION.md` (Cat 8)*

Phase 3E adds intelligent model selection with budget controls and multi-model consensus for critical decisions.

#### Model Orchestrator (Phase 3)
Automatic model selection based on quality tiers and budget constraints.

**UI Elements:**
-   **Enable Toggle**: Turn on/off automatic model selection
    -   When OFF: Manual task_models configuration used (existing behavior)
    -   When ON: Orchestrator overrides manual assignments
-   **Quality Tier Dropdown**: Budget / Balanced / Premium
    -   **Budget**: Free local models only (~$0/month)
    -   **Balanced**: Best quality per dollar (~$0.50-1/month, DeepSeek + local)
    -   **Premium**: Optimal model per task (~$3-5/month, Claude + GPT-4o + DeepSeek)
-   **Monthly Budget Input**: Number input (optional, USD, range: $0-100)
    -   Placeholder: "No limit"
    -   Shows red border when spending approaches limit (≥80%)
    -   Null/empty = unlimited budget
-   **Prefer Local Toggle**: Boolean preference for local models when quality similar
    -   Tooltip: "Use free Ollama models when quality difference is < 1 point"
-   **Cost Estimator Widget** (real-time display):
    -   **Progress Bar**: Visual representation of spend vs. budget
        -   Green (0-79%), Yellow (80-99%), Red (100%+)
    -   **Text Display**: "$0.47 / $2.00 ($1.53 remaining)"
    -   **Warning Indicators**:
        -   80%: "⚠️ Approaching budget limit"
        -   100%: "🚫 Budget exceeded - using free local models"
    -   Auto-updates when tier/budget changes
-   **Recommendations Preview** (expandable section):
    -   Shows which models will be selected for key tasks
    -   Example: "Health Check Review → deepseek-chat"
    -   Updates dynamically when tier changes

**UI Component**: `SettingsOrchestrator.svelte` (~200 lines)

**Data Integration:**
-   `GET /orchestrator/capabilities` - Fetch model registry (costs, strengths, quality scores)
-   `POST /orchestrator/estimate-cost` - Get cost projection for quality tier + typical usage
-   `GET /orchestrator/current-spend` - Current month's spending + budget remaining
-   `GET /orchestrator/recommendations/{task_type}` - Get recommended models per tier

#### Multi-Model Tournament (Phase 4)
Query multiple models in parallel for critical story decisions.

**UI Elements:**
-   **Enable Toggle**: Turn on/off tournaments for critical decisions
    -   Tooltip: "Query 3+ models for major decisions to detect consensus/disagreement"
-   **Critical Tasks Multi-Select**: Checkboxes for which task types trigger tournaments
    -   Options:
        - ☐ beat_structure_advice (Major structural decisions)
        - ☐ structural_planning (High-level planning)
        - ☐ theme_analysis (Thematic interpretation)
        - ☐ voice_calibration_guidance (Voice selection)
        - ☐ conflict_resolution (Timeline conflicts)
-   **Models per Tournament Slider**: 2-5 models (default: 3)
    -   Tooltip: "More models = higher cost ($0.02-0.05 per tournament), better consensus detection"
    -   Shows estimated cost per tournament below slider
-   **Max per Day Input**: Cost control (range: 1-50, default: 10)
    -   Displays estimated monthly cost: "~10 tournaments/day × 30 days × $0.03 = $9/month"
-   **Show All Responses Toggle**: Display all model outputs vs. just consensus
    -   Tooltip: "Show all model responses even when they agree (useful for learning)"
-   **Tournament Usage Widget** (today's usage):
    -   **Progress Bar**: "7 / 10 tournaments used"
    -   **Text**: "(3 remaining today)"
    -   Resets daily at midnight

**Cost Warning Box** (prominent yellow/red background):
```
⚠️ WARNING: Tournaments are expensive (~$0.02-0.05 per tournament)
Estimated monthly cost: ~$9.00 based on current settings
(10 tournaments/day × 30 days × $0.03 average cost)
```

**UI Components:**
-   `SettingsTournament.svelte` (~150 lines) - Tournament configuration panel
-   `CostEstimator.svelte` (~100 lines) - Reusable real-time spend widget

**Data Integration:**
-   `GET /tournament/status` - Tournament usage (today's count, remaining, max per day)
-   `POST /tournament/run` - Manual tournament trigger (for testing, not in normal UI)

#### Shared Sub-Components
-   `SettingsOrchestrator.svelte`: Model orchestrator configuration
-   `SettingsTournament.svelte`: Tournament configuration
-   `CostEstimator.svelte`: Reusable cost tracking widget (used by both)

## 3. Data Integration

### 3.1 Backend Service
-   **Endpoint**: `GET /settings` (Returns full JSON tree).
-   **Endpoint**: `POST /settings/update` (Accepts partial or full JSON).
-   **Endpoint**: `POST /settings/reset` (Resets to defaults).

### 3.2 Frontend Store
-   Create `settingsStore.ts`:
    -   `settings`: Writable store mirroring the backend JSON.
    -   `isDirty`: Derived store tracking changes.
    -   `save()`: Method to push changes to backend.

## 4. Implementation Phases

### Phase 1: Foundation
-   Create `SettingsPanel` shell.
-   Implement `settingsStore` and API connection.
-   Build `SettingsAgents` (Priority: API Keys are blockers).

### Phase 2: Core Tuning
-   Implement `SettingsScoring` (with linked sliders logic).
-   Implement `SettingsVoice` and `SettingsMetaphor`.
-   Implement `SettingsEnhancement`.

### Phase 3: Advanced & Polish
-   Implement `SettingsForeman`, `SettingsHealth`, `SettingsAdvanced`.
-   Add "Test Connection" logic for API keys.
-   Add Import/Export functionality (JSON/YAML file handling).

## 5. UX/UI Guidelines
-   **Tooltips**: Every setting must have a tooltip explaining its craft impact.
-   **Visual Feedback**: Sliders should show the numerical value.
-   **Project Overrides**: Visual indicator (e.g., blue dot or border) when a setting differs from the global default.
