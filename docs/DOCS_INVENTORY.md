# Documentation Inventory & Organization Plan

**Created**: November 25, 2025
**Purpose**: Comprehensive audit of /docs folder to clarify what's current vs archival

---

## 📁 Current Structure

```
/docs
├── /archive (7 files) - Old architecture versions
├── /claude skills original (13+ folders) - Reference Claude skills
├── /dev_logs (20 files) - Implementation logs and completion summaries
├── /specs (17 files) - Technical specifications and plans
└── Root files (14 .md files) - Core documentation
```

---

## ✅ ROOT LEVEL FILES (14 files) - Current & Active

### Critical Active Documentation
1. **ARCHITECTURE.md** (21K, Nov 23) - ✅ **CURRENT** - Main architecture specification
2. **04_roadmap.md** (9.1K, Nov 24) - ✅ **CURRENT** - Phase tracking and roadmap
3. **BACKEND_SERVICES.md** (20K, Nov 23) - ✅ **CURRENT** - Complete backend service documentation
4. **API_REFERENCE.md** (15K, Nov 23) - ✅ **CURRENT** - API endpoint reference
5. **WORKFLOWS.md** (15K, Nov 23) - ✅ **CURRENT** - User workflows and Foreman modes
6. **DOCS_INDEX.md** (8.7K, Nov 23) - ✅ **CURRENT** - Documentation index

### Configuration & Model Documentation
7. **CONFIGURABLE_MODEL_ASSIGNMENTS.md** (12K, Nov 24) - ✅ **CURRENT** - Phase 3E model configuration guide
8. **PHASE_3E_QUICK_START.md** (7.1K, Nov 24) - ✅ **CURRENT** - Phase 3E quick start guide

### Supplementary Active Documentation
9. **NARRATIVE PROTOCOL.md** (4.0K, Nov 21) - ✅ **CURRENT** - Writing quality standards
10. **manifesto.md** (5.0K, Nov 22) - ✅ **CURRENT** - Project philosophy and goals
11. **index.md** (4.5K, Nov 22) - ✅ **CURRENT** - Documentation homepage

### UX Planning
12. **UX_ROADMAP.md** (5.1K, Nov 22) - ⚠️ **OUTDATED** - Superseded by UI_IMPLEMENTATION_PLAN.md (Nov 25)

### Reference Documents (Less Critical)
13. **AI Self-Review Document for Creative Prose.md** (6.6K, Nov 23) - 📚 **REFERENCE** - Quality checklist
14. **Guidance for Scene-Level Agent Refinement.md** (5.5K, Nov 24) - 📚 **REFERENCE** - Agent tuning guidance

### Files to Archive
15. **Architecture for Macro-Level Analysis (Graph Health Service).md** (5.7K, Nov 24) - ♻️ **ARCHIVE** - Draft superseded by Phase 3D implementation
16. **CNAME** (18B) - ⚠️ **DELETE** - Appears to be accidental include (GitHub Pages?)

---

## ✅ /dev_logs FOLDER (20 files) - Implementation Logs

### Phase 3E: Model Orchestrator (Most Recent - Nov 24-25)
1. **PHASE_3_ORCHESTRATOR_COMPLETION.md** (13K, Nov 25) - ✅ **CURRENT** - Phase 3 (Orchestrator) completion summary
2. **PHASE_3_ORCHESTRATOR_IMPLEMENTATION_COMPLETE.md** (7.8K, Nov 25) - ✅ **CURRENT** - Phase 3 implementation details
3. **PHASE_3E_COMPLETION_SUMMARY.md** (15K, Nov 24) - ✅ **CURRENT** - Phase 3E (Phases 1-2) completion summary
4. **PHASE_3E_INTELLIGENT_FOREMAN_IMPLEMENTATION.md** (13K, Nov 24) - ✅ **CURRENT** - Phase 3E implementation details
5. **PHASE_3E_NEXT_STEPS.md** (17K, Nov 24) - ✅ **CURRENT** - Phase 3E next steps and Phase 3-4 planning
6. **PHASE_3E_PHASES_3_4_IMPLEMENTATION_PLAN.md** (39K, Nov 24) - ✅ **CURRENT** - Complete Phase 3-4 implementation plan

### Phase 3D: Graph Health Service (Nov 24)
7. **PHASE_3D_GRAPH_HEALTH_IMPLEMENTATION.md** (36K, Nov 24) - ✅ **CURRENT** - Phase 3D implementation log

### Phase 3C: Settings Implementation (Nov 24)
8. **PHASE_3C_SETTINGS_IMPLEMENTATION.md** (19K, Nov 24) - ✅ **CURRENT** - Phase 3C implementation log

### Phase 2B: Voice Calibration (Nov 23)
9. **PHASE_2B_VOICE_CALIBRATION_NOV23.md** (7.9K, Nov 23) - ✅ **CURRENT** - Phase 2B implementation log

### Agent Handoff & Session Documentation (Nov 22-23)
10. **AGENT_HANDOFF_WISDOM.md** (5.9K, Nov 23) - ✅ **CURRENT** - Lessons from agent sessions
11. **FOREMAN_BRIEFING_NOV23.md** (7.8K, Nov 23) - ✅ **CURRENT** - Foreman architecture briefing
12. **GEMINI_ARCHITECT_REVIEW_NOV23.md** (4.5K, Nov 23) - ✅ **CURRENT** - Gemini review session
13. **ARCHITECT_HANDOFF_VOICE_UI.md** (3.8K, Nov 23) - ✅ **CURRENT** - Architect to Voice UI handoff
14. **FINAL_HANDOFF_NOV22.md** (2.3K, Nov 22) - ✅ **CURRENT** - Phase 3B handoff notes

### NotebookLM Integration (Nov 21-22)
15. **NOTEBOOKLM_INTEGRATION_RESEARCH.md** (4.1K, Nov 21) - ✅ **CURRENT** - NotebookLM integration research
16. **NOTEBOOKLM_FIX_NOV22.md** (5.4K, Nov 22) - ✅ **CURRENT** - NotebookLM fix documentation
17. **AGENT_PROMPT_NOTEBOOKLM_FIX.md** (2.2K, Nov 22) - ✅ **CURRENT** - Agent prompt for NotebookLM fix

### Other Implementation Logs (Nov 21-24)
18. **Complete Inventory of All Stylistic Checks.md** (7.3K, Nov 24) - ✅ **CURRENT** - Complete stylistic check inventory
19. **TROUBLESHOOTING_REPORT_NOV22.md** (2.1K, Nov 22) - ✅ **CURRENT** - Troubleshooting session notes
20. **MANAGER_INSTALLATION_PLAN.md** (2.3K, Nov 21) - ✅ **CURRENT** - Installation plan

**Status**: All dev_logs are current and should be retained. These are historical records of implementation sessions.

---

## ✅ /specs FOLDER (17 files) - Technical Specifications

### UI/UX Specifications (Most Recent - Nov 25)
1. **UI_IMPLEMENTATION_PLAN.md** (30K, Nov 25) - ✅ **CURRENT** - Original UI implementation plan (infrastructure focus)
2. **UI_GAP_ANALYSIS.md** (21K, Nov 25) - ✅ **CURRENT** - Comprehensive backend vs UI coverage analysis
3. **UI_COMPONENT_INVENTORY.md** (30K, Nov 25) - ✅ **CURRENT** - Complete 87-component inventory with 8-phase plan
4. **UX_DESIGN_PROMPTS.md** (11K, Nov 24) - ✅ **CURRENT** - UX design prompts and guidelines

### Settings & Configuration (Nov 24-25)
5. **SETTINGS_CONFIGURATION.md** (20K, Nov 24) - ✅ **CURRENT** - Complete settings specification (11 categories)
6. **SETTINGS_PANEL_IMPLEMENTATION_PLAN.md** (10K, Nov 25) - ✅ **CURRENT** - Settings Panel UI specification
7. **SETTINGS CONFIGURATION Comments.md** (6.8K, Nov 24) - ♻️ **ARCHIVE** - Draft comments, superseded by main spec

### Director Mode (Nov 23-24)
8. **DIRECTOR_MODE_SPECIFICATION.md** (63K, Nov 24) - ✅ **CURRENT** - Complete Director Mode specification (v2.0)
9. **DIRECTOR_MODE_API_REFERENCE.md** (16K, Nov 23) - ✅ **CURRENT** - Director Mode API reference
10. **DIRECTOR_MODE.md** (20K, Nov 23) - ✅ **CURRENT** - Director Mode overview

### Story Bible & Architecture (Nov 22-24)
11. **STORY_BIBLE_ARCHITECT.md** (27K, Nov 23) - ✅ **CURRENT** - Story Bible (ARCHITECT mode) specification
12. **Technical specifications and requirements for Story Bible System.md** (9.4K, Nov 22) - ♻️ **ARCHIVE** - Draft superseded by STORY_BIBLE_ARCHITECT.md

### Graph Health Service (Nov 24)
13. **Phase 3D Graph Health Service - Complete Implementation Plan.md** (43K, Nov 24) - ✅ **CURRENT** - Phase 3D complete implementation plan

### Scoring & Quality (Nov 23)
14. **SCORING_RUBRICS.md** (18K, Nov 23) - ✅ **CURRENT** - Complete scoring rubric specification

### Infrastructure & Backend (Nov 22)
15. **RAG_IMPLEMENTATION.md** (28K, Nov 22) - ✅ **CURRENT** - RAG system implementation plan
16. **FILE_SYNC.md** (16K, Nov 22) - ✅ **CURRENT** - File sync specification
17. **SECURITY.md** (19K, Nov 22) - ✅ **CURRENT** - Security considerations and implementation

**Status**: 14 current, 2 archival candidates

---

## ♻️ /archive FOLDER (7 files) - Historical Architecture Versions

1. **MASTER_ARCHITECTURE V2.0.md** - ✅ **ARCHIVED** - Old architecture version
2. **MASTER_ARCHITECTURE V3.0.md** - ✅ **ARCHIVED** - Old architecture version
3. **Master Architecture V4.0.md** - ✅ **ARCHIVED** - Old architecture version
4. **Master Architecture V4.1.md** - ✅ **ARCHIVED** - Old architecture version
5. **Master Architecture V4.1 Review & Next Steps.md** - ✅ **ARCHIVED** - Old architecture review
6. **01_architecture.md** - ✅ **ARCHIVED** - Old architecture version
7. **02_scene_pipeline.md** - ✅ **ARCHIVED** - Old pipeline spec
8. **03_data_schema.md** - ✅ **ARCHIVED** - Old schema spec
9. **Writers Factory Desktop App - Technical Specification.md** - ✅ **ARCHIVED** - Old technical spec

**Status**: All properly archived.

---

## 📚 /claude skills original FOLDER (13+ folders) - Reference Skills

This folder contains the original Claude skills that were used as reference for implementing the Director Mode services:

1. **explants-scene-writer/** - Scene writing skill (Mickey Bardot voice)
2. **explants-scene-analyzer-scorer/** - Scene analysis and scoring skill
3. **explants-scene-enhancement/** - Scene enhancement skill
4. **explants-smart-scaffold-generator/** - Scaffold generation skill
5. **explants-scene-multiplier/** - Scene multiplier skill
6. **mickey-bardot-character-identity/** - Mickey character identity skill
7. **Gemini Gem files/** - Gemini reference files for Mickey
8. **SKILLS_AUDIT_SUMMARY.md** - Skills audit summary
9. **Sample Explants Chapter:scene generation.md** - Sample chapter generation
10. **COMPLETE_CHAPTER_CREATION_PIPELINE.md** - Complete pipeline documentation
11. **Mickey Gemini Gem Instructions.md** - Gemini instructions

**Status**: All are reference materials. Should be retained but clearly marked as "Reference Only - Not Active Code".

---

## 📋 Proposed Reorganization

### Option 1: Current Structure (Recommended)
Keep the current 4-folder structure but clarify with README files:

```
/docs
├── /archive         - Historical architecture versions
├── /claude-skills   - Rename from "claude skills original" (remove spaces)
├── /dev_logs        - Implementation logs (chronological)
├── /specs           - Technical specifications (by feature)
└── ROOT FILES       - Core documentation only
```

### Option 2: Expanded Structure
Create more granular organization:

```
/docs
├── /archive
│   ├── /architecture-versions
│   └── /deprecated-specs
├── /backend
│   ├── /api-reference
│   ├── /services
│   └── /architecture
├── /frontend
│   ├── /ui-specs
│   ├── /ux-design
│   └── /components
├── /implementation-logs
│   ├── /phase-2
│   ├── /phase-3
│   └── /handoffs
├── /reference
│   └── /claude-skills-original
└── /guides
    ├── /quick-starts
    └── /configuration
```

**Recommendation**: **Option 1** - The current structure is clean and works well. Just needs:
1. Rename "claude skills original" to "claude-skills" (remove spaces)
2. Add README.md to each subfolder explaining its purpose
3. Move 3 archival candidates from /specs and root to /archive
4. Update DOCS_INDEX.md with clear organization

---

## 🗂️ Files to Archive (6 candidates)

### From Root
1. **Architecture for Macro-Level Analysis (Graph Health Service).md** → archive/drafts/
2. **UX_ROADMAP.md** → archive/superseded/ (replaced by UI_IMPLEMENTATION_PLAN.md)
3. **CNAME** → DELETE (accidental include)

### From /specs
4. **SETTINGS CONFIGURATION Comments.md** → archive/drafts/ (superseded by main spec)
5. **Technical specifications and requirements for Story Bible System.md** → archive/superseded/ (replaced by STORY_BIBLE_ARCHITECT.md)

---

## 📊 Summary Statistics

**Total Documentation**: 58+ markdown files
- **Root Level**: 14 files (12 current, 2 archival)
- **/dev_logs**: 20 files (all current, historical records)
- **/specs**: 17 files (14 current, 2 archival, 1 reference)
- **/archive**: 9 files (all properly archived)
- **/claude-skills**: 13+ folders (all reference materials)

**Current & Active**: 46 files (~79%)
**Archival Candidates**: 6 files (~10%)
**Already Archived**: 9 files (~16%)

---

## ✅ Recommended Actions

### Immediate (Before GitHub Push)
1. ✅ Create this inventory document (DOCS_INVENTORY.md)
2. ⏳ Rename "claude skills original" → "claude-skills" (remove spaces)
3. ⏳ Create archive/drafts/ and archive/superseded/ subfolders
4. ⏳ Move 6 archival candidates to appropriate archive locations
5. ⏳ Delete CNAME file (accidental include)
6. ⏳ Add README.md to each main subfolder:
   - /archive/README.md - Explain archival policy
   - /claude-skills/README.md - "Reference materials only, not active code"
   - /dev_logs/README.md - "Chronological implementation logs"
   - /specs/README.md - "Technical specifications by feature area"

### After Organization
7. ⏳ Update DOCS_INDEX.md with new organization
8. ⏳ Update ARCHITECTURE.md with UI/UX strategy (per user request)
9. ⏳ Update 04_roadmap.md with 3-track parallel development plan (per user request)
10. ⏳ Create UI_IMPLEMENTATION_PLAN_V2.md or update existing with complete 87-component coverage

### Future Maintenance
11. 📅 Add "Last Updated" dates to all specs
12. 📅 Create CHANGELOG.md for major documentation updates
13. 📅 Consider using tags/versioning for major architecture changes

---

## 🎯 Current Priority: Documentation Updates

Per user request, the immediate priority is:
1. ✅ Understand documentation organization (this inventory)
2. ⏳ Update 04_roadmap.md with 3-track parallel development
3. ⏳ Update ARCHITECTURE.md with UI/UX strategy
4. ⏳ Update or create comprehensive UI implementation plan
5. ⏳ Organize /docs folder structure
6. ⏳ Push everything to GitHub

---

**Status**: Inventory complete. Ready to proceed with documentation updates and reorganization.

*Created: November 25, 2025*
*Purpose: Clarify documentation organization before GitHub push*
