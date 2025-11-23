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
- 🔲 Frontend UI (Phase 5)
- 🔲 Foreman orchestration integration

See: [DIRECTOR_MODE_SPECIFICATION.md](specs/DIRECTOR_MODE_SPECIFICATION.md) for full technical details

## Phase 4: The Immune System (Planned)
**Goal:** Story Health & Versioning.
1.  **Health Service:** Automated checks for Dropped Threads, Timeline Errors, and Character Absences.
2.  **Version Control:** Graph snapshotting ("Time Travel") and Branching ("What If" scenarios).
3.  **Procedural Memory:** Vectorizing user preferences with **Consolidation Logic** (Merge/Update/Create strategies to prevent bloat).

## Phase 5: Polish & Release
1.  **Packaging:** Build `.dmg` / `.exe` installers.
2.  **Optimizations:** Lazy loading for large graphs.
3.  **Plugins:** External agent registry.
4.  **Settings UI:** Configurable scoring weights, thresholds, and agent preferences.
    - See: [SETTINGS_CONFIGURATION.md](specs/SETTINGS_CONFIGURATION.md)
