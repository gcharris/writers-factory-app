# Writers Factory - Documentation Index

**Version**: 2.0 (Reorganized)
**Last Updated**: November 25, 2025
**Total Documentation**: 58+ files (~400K words)

---

## 📚 Quick Start

**New to Writers Factory?** Start here:
1. [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and UI/UX strategy
2. [04_roadmap.md](04_roadmap.md) - Development roadmap and phase tracking
3. [PHASE_3E_QUICK_START.md](PHASE_3E_QUICK_START.md) - Quick start guide for Phase 3E Model Orchestrator

**Want to implement UI?** Start here:
1. [specs/UI_IMPLEMENTATION_PLAN_V2.md](specs/UI_IMPLEMENTATION_PLAN_V2.md) - Complete UI implementation plan (87 components)
2. [specs/UI_GAP_ANALYSIS.md](specs/UI_GAP_ANALYSIS.md) - Backend vs UI coverage analysis
3. [specs/UI_COMPONENT_INVENTORY.md](specs/UI_COMPONENT_INVENTORY.md) - Complete component inventory

**Want to understand backend?** Start here:
1. [BACKEND_SERVICES.md](BACKEND_SERVICES.md) - Service layer documentation
2. [API_REFERENCE.md](API_REFERENCE.md) - All 88 REST API endpoints
3. [specs/DIRECTOR_MODE_SPECIFICATION.md](specs/DIRECTOR_MODE_SPECIFICATION.md) - Director Mode complete specification

---

## 📁 Documentation Structure

```
/docs
├── /archive              - Historical documentation (9 files)
│   ├── /drafts          - Abandoned drafts
│   └── /superseded      - Replaced by newer versions
├── /claude-skills        - Reference Claude skills (13+ folders)
├── /dev_logs            - Implementation logs (20 files)
├── /specs               - Technical specifications (16 files)
└── ROOT FILES           - Core documentation (14 files)
```

Each folder now has a **README.md** explaining its purpose and organization. See folder READMEs for details:
- [archive/README.md](archive/README.md)
- [claude-skills/README.md](claude-skills/README.md)
- [dev_logs/README.md](dev_logs/README.md)
- [specs/README.md](specs/README.md)

---

## 🗂️ Core Documentation (Root Level)

### Architecture & Planning
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 21K | Main architecture specification with UI/UX strategy | ✅ Current (v2.1) |
| [04_roadmap.md](04_roadmap.md) | 9K | Phase tracking and 3-track parallel development | ✅ Current |
| [WORKFLOWS.md](WORKFLOWS.md) | 15K | User workflows and Foreman modes | ✅ Current |

### Backend Documentation
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [BACKEND_SERVICES.md](BACKEND_SERVICES.md) | 20K | Complete backend service documentation | ✅ Current |
| [API_REFERENCE.md](API_REFERENCE.md) | 15K | API endpoint reference (88 endpoints) | ✅ Current |

### Configuration & Setup
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [CONFIGURABLE_MODEL_ASSIGNMENTS.md](CONFIGURABLE_MODEL_ASSIGNMENTS.md) | 12K | Phase 3E model configuration guide | ✅ Current |
| [PHASE_3E_QUICK_START.md](PHASE_3E_QUICK_START.md) | 7K | Phase 3E quick start guide | ✅ Current |

### Philosophy & Standards
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [NARRATIVE PROTOCOL.md](NARRATIVE%20PROTOCOL.md) | 4K | Writing quality standards | ✅ Current |
| [manifesto.md](manifesto.md) | 5K | Project philosophy and goals | ✅ Current |
| [index.md](index.md) | 5K | Documentation homepage | ✅ Current |

### Reference Documents
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [AI Self-Review Document for Creative Prose.md](AI%20Self-Review%20Document%20for%20Creative%20Prose.md) | 7K | Quality checklist | 📚 Reference |
| [Guidance for Scene-Level Agent Refinement.md](Guidance%20for%20Scene-Level%20Agent%20Refinement.md) | 6K | Agent tuning guidance | 📚 Reference |
| [DOCS_INVENTORY.md](DOCS_INVENTORY.md) | - | Complete documentation inventory | ✅ Current |
| [DOCS_INDEX.md](DOCS_INDEX.md) | - | This file | ✅ Current |

---

## 📋 Technical Specifications (/specs)

### UI/UX Specifications (November 25, 2025)
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [UI_IMPLEMENTATION_PLAN_V2.md](specs/UI_IMPLEMENTATION_PLAN_V2.md) | ~30K | **Complete UI plan with all 87 components** | ✅ **CURRENT** |
| [UI_GAP_ANALYSIS.md](specs/UI_GAP_ANALYSIS.md) | 21K | Backend vs UI coverage analysis | ✅ Current |
| [UI_COMPONENT_INVENTORY.md](specs/UI_COMPONENT_INVENTORY.md) | 30K | All 87 components with priorities | ✅ Current |
| [UI_IMPLEMENTATION_PLAN.md](specs/UI_IMPLEMENTATION_PLAN.md) | 30K | Original infrastructure plan | 📚 Reference (superseded by V2) |
| [UX_DESIGN_PROMPTS.md](specs/UX_DESIGN_PROMPTS.md) | 11K | UX design prompts and guidelines | ✅ Current |

### Settings & Configuration (November 24-25, 2025)
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [SETTINGS_CONFIGURATION.md](specs/SETTINGS_CONFIGURATION.md) | 20K | Complete settings spec (11 categories) | ✅ Current (v1.1) |
| [SETTINGS_PANEL_IMPLEMENTATION_PLAN.md](specs/SETTINGS_PANEL_IMPLEMENTATION_PLAN.md) | 10K | Settings Panel UI specification | ✅ Current |

### Director Mode (November 23-24, 2025)
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [DIRECTOR_MODE_SPECIFICATION.md](specs/DIRECTOR_MODE_SPECIFICATION.md) | 63K | **Complete Director Mode spec (v2.0)** | ✅ **CURRENT** |
| [DIRECTOR_MODE_API_REFERENCE.md](specs/DIRECTOR_MODE_API_REFERENCE.md) | 16K | Director Mode API reference | ✅ Current |
| [DIRECTOR_MODE.md](specs/DIRECTOR_MODE.md) | 20K | Director Mode overview | ✅ Current |

### Story Bible (November 22-23, 2025)
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [STORY_BIBLE_ARCHITECT.md](specs/STORY_BIBLE_ARCHITECT.md) | 27K | Story Bible (ARCHITECT mode) specification | ✅ Current |

### Graph Health (November 24, 2025)
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [Phase 3D Graph Health Service - Complete Implementation Plan.md](specs/Phase%203D%20Graph%20Health%20Service%20-%20Complete%20Implementation%20Plan.md) | 43K | Phase 3D implementation plan | 🚧 In Progress |

### Quality & Scoring (November 23, 2025)
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [SCORING_RUBRICS.md](specs/SCORING_RUBRICS.md) | 18K | Complete scoring rubric specification | ✅ Current |

### Infrastructure (November 22, 2025)
| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| [RAG_IMPLEMENTATION.md](specs/RAG_IMPLEMENTATION.md) | 28K | RAG system implementation plan | ✅ Current |
| [FILE_SYNC.md](specs/FILE_SYNC.md) | 16K | File synchronization specification | ✅ Current |
| [SECURITY.md](specs/SECURITY.md) | 19K | Security considerations | ✅ Current |

**Total Specifications**: 16 files (~350K words)

See [specs/README.md](specs/README.md) for detailed organization and reading guide.

---

## 📝 Development Logs (/dev_logs)

Implementation logs organized chronologically by phase. See [dev_logs/README.md](dev_logs/README.md) for complete organization.

### Phase 3E: Intelligent Model Orchestration (Nov 24-25, 2025)
| Document | Size | Purpose |
|----------|------|---------|
| [PHASE_3_ORCHESTRATOR_COMPLETION.md](dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md) | 13K | Phase 3 (Orchestrator) completion summary |
| [PHASE_3_ORCHESTRATOR_IMPLEMENTATION_COMPLETE.md](dev_logs/PHASE_3_ORCHESTRATOR_IMPLEMENTATION_COMPLETE.md) | 8K | Phase 3 implementation details |
| [PHASE_3E_COMPLETION_SUMMARY.md](dev_logs/PHASE_3E_COMPLETION_SUMMARY.md) | 15K | Phase 3E (Phases 1-2) completion |
| [PHASE_3E_INTELLIGENT_FOREMAN_IMPLEMENTATION.md](dev_logs/PHASE_3E_INTELLIGENT_FOREMAN_IMPLEMENTATION.md) | 13K | Phase 3E implementation details |
| [PHASE_3E_NEXT_STEPS.md](dev_logs/PHASE_3E_NEXT_STEPS.md) | 17K | Phase 3E next steps |
| [PHASE_3E_PHASES_3_4_IMPLEMENTATION_PLAN.md](dev_logs/PHASE_3E_PHASES_3_4_IMPLEMENTATION_PLAN.md) | 39K | Complete Phase 3-4 plan |

### Phase 3D: Graph Health (Nov 24, 2025)
| Document | Size | Purpose |
|----------|------|---------|
| [PHASE_3D_GRAPH_HEALTH_IMPLEMENTATION.md](dev_logs/PHASE_3D_GRAPH_HEALTH_IMPLEMENTATION.md) | 36K | Phase 3D implementation log |

### Phase 3C: Settings (Nov 24, 2025)
| Document | Size | Purpose |
|----------|------|---------|
| [PHASE_3C_SETTINGS_IMPLEMENTATION.md](dev_logs/PHASE_3C_SETTINGS_IMPLEMENTATION.md) | 19K | Settings service implementation |

### Phase 2B: Voice Calibration (Nov 23, 2025)
| Document | Size | Purpose |
|----------|------|---------|
| [PHASE_2B_VOICE_CALIBRATION_NOV23.md](dev_logs/PHASE_2B_VOICE_CALIBRATION_NOV23.md) | 8K | Voice calibration implementation |

### Agent Handoff & Sessions (Nov 22-23, 2025)
| Document | Size | Purpose |
|----------|------|---------|
| [AGENT_HANDOFF_WISDOM.md](dev_logs/AGENT_HANDOFF_WISDOM.md) | 6K | Agent handoff lessons learned |
| [FOREMAN_BRIEFING_NOV23.md](dev_logs/FOREMAN_BRIEFING_NOV23.md) | 8K | Foreman architecture briefing |
| [GEMINI_ARCHITECT_REVIEW_NOV23.md](dev_logs/GEMINI_ARCHITECT_REVIEW_NOV23.md) | 5K | Gemini review session |
| [ARCHITECT_HANDOFF_VOICE_UI.md](dev_logs/ARCHITECT_HANDOFF_VOICE_UI.md) | 4K | Architect to Voice UI handoff |
| [FINAL_HANDOFF_NOV22.md](dev_logs/FINAL_HANDOFF_NOV22.md) | 2K | Phase 3B handoff notes |

### NotebookLM Integration (Nov 21-22, 2025)
| Document | Size | Purpose |
|----------|------|---------|
| [NOTEBOOKLM_INTEGRATION_RESEARCH.md](dev_logs/NOTEBOOKLM_INTEGRATION_RESEARCH.md) | 4K | NotebookLM integration research |
| [NOTEBOOKLM_FIX_NOV22.md](dev_logs/NOTEBOOKLM_FIX_NOV22.md) | 5K | NotebookLM fix documentation |
| [AGENT_PROMPT_NOTEBOOKLM_FIX.md](dev_logs/AGENT_PROMPT_NOTEBOOKLM_FIX.md) | 2K | Agent prompt for fix |

### Other Logs
| Document | Size | Purpose |
|----------|------|---------|
| [Complete Inventory of All Stylistic Checks.md](dev_logs/Complete%20Inventory%20of%20All%20Stylistic%20Checks.md) | 7K | Stylistic check inventory |
| [TROUBLESHOOTING_REPORT_NOV22.md](dev_logs/TROUBLESHOOTING_REPORT_NOV22.md) | 2K | Troubleshooting session |
| [MANAGER_INSTALLATION_PLAN.md](dev_logs/MANAGER_INSTALLATION_PLAN.md) | 2K | Installation plan |

**Total Dev Logs**: 20 files (~200K words)

---

## 📚 Reference Materials (/claude-skills)

Original Claude skills from Explants project that served as reference for Director Mode implementation.

**Status**: Reference Only - Not Active Code

See [claude-skills/README.md](claude-skills/README.md) for complete details.

### Skills Included
1. **explants-scene-writer/** - Scene writing (Mickey Bardot voice)
2. **explants-scene-analyzer-scorer/** - Scene analysis (5-category rubric)
3. **explants-scene-enhancement/** - Scene enhancement (Action Prompt, 6-Pass)
4. **explants-smart-scaffold-generator/** - Scaffold generation
5. **explants-scene-multiplier/** - Scene multiplier (5 strategies)
6. **mickey-bardot-character-identity/** - Character identity
7. **Gemini Gem files/** - Gemini reference files
8. **Sample transcripts and documentation**

**Mapping to Writers Factory**:
| Claude Skill | Writers Factory Service | Status |
|--------------|-------------------------|--------|
| explants-scene-analyzer-scorer | SceneAnalyzerService | ✅ Implemented |
| explants-smart-scaffold-generator | ScaffoldGeneratorService | ✅ Implemented |
| explants-mickey-scene-writer | SceneWriterService | ✅ Implemented |
| explants-scene-enhancement | SceneEnhancementService | ✅ Implemented |
| explants-scene-multiplier | SceneWriterService (tournament) | ✅ Implemented |

---

## 🗄️ Archived Documentation (/archive)

Historical documentation that has been superseded or is no longer actively maintained.

See [archive/README.md](archive/README.md) for archival policy.

### Architecture Versions (/archive)
- MASTER_ARCHITECTURE V2.0.md → V4.1.md
- Master Architecture V4.1 Review & Next Steps.md
- 01_architecture.md, 02_scene_pipeline.md, 03_data_schema.md
- Writers Factory Desktop App - Technical Specification.md

### Superseded Specifications (/archive/superseded)
- Technical specifications and requirements for Story Bible System.md (→ STORY_BIBLE_ARCHITECT.md)
- UX_ROADMAP.md (→ UI_IMPLEMENTATION_PLAN_V2.md)

### Drafts (/archive/drafts)
- Architecture for Macro-Level Analysis (Graph Health Service).md
- SETTINGS CONFIGURATION Comments.md

**Total Archived**: 9+ files

---

## 🔍 Finding What You Need

### By Topic

**UI/UX Implementation**:
- [specs/UI_IMPLEMENTATION_PLAN_V2.md](specs/UI_IMPLEMENTATION_PLAN_V2.md) - Complete plan
- [specs/UI_GAP_ANALYSIS.md](specs/UI_GAP_ANALYSIS.md) - Coverage analysis
- [specs/UI_COMPONENT_INVENTORY.md](specs/UI_COMPONENT_INVENTORY.md) - All components
- [specs/SETTINGS_PANEL_IMPLEMENTATION_PLAN.md](specs/SETTINGS_PANEL_IMPLEMENTATION_PLAN.md) - Settings UI

**Backend Services**:
- [BACKEND_SERVICES.md](BACKEND_SERVICES.md) - Service layer docs
- [API_REFERENCE.md](API_REFERENCE.md) - API endpoints
- [specs/DIRECTOR_MODE_SPECIFICATION.md](specs/DIRECTOR_MODE_SPECIFICATION.md) - Director Mode
- [specs/STORY_BIBLE_ARCHITECT.md](specs/STORY_BIBLE_ARCHITECT.md) - Story Bible

**Configuration & Settings**:
- [specs/SETTINGS_CONFIGURATION.md](specs/SETTINGS_CONFIGURATION.md) - 11 settings categories
- [CONFIGURABLE_MODEL_ASSIGNMENTS.md](CONFIGURABLE_MODEL_ASSIGNMENTS.md) - Model configuration
- [PHASE_3E_QUICK_START.md](PHASE_3E_QUICK_START.md) - Phase 3E quick start

**Architecture & Planning**:
- [ARCHITECTURE.md](ARCHITECTURE.md) - Main architecture (includes UI/UX strategy)
- [04_roadmap.md](04_roadmap.md) - Roadmap and phase tracking
- [WORKFLOWS.md](WORKFLOWS.md) - User workflows

**Implementation History**:
- [dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md](dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md) - Latest phase
- [dev_logs/PHASE_3E_COMPLETION_SUMMARY.md](dev_logs/PHASE_3E_COMPLETION_SUMMARY.md) - Phase 3E summary
- [dev_logs/](dev_logs/) - All implementation logs

### By Development Phase

**Phase 1** (Complete): Foundation
- [ARCHITECTURE.md](ARCHITECTURE.md) sections: Phase 1

**Phase 2** (Complete): Story Bible System
- [specs/STORY_BIBLE_ARCHITECT.md](specs/STORY_BIBLE_ARCHITECT.md)
- [dev_logs/PHASE_2B_VOICE_CALIBRATION_NOV23.md](dev_logs/PHASE_2B_VOICE_CALIBRATION_NOV23.md)

**Phase 3B** (Complete): Director Mode
- [specs/DIRECTOR_MODE_SPECIFICATION.md](specs/DIRECTOR_MODE_SPECIFICATION.md)
- [specs/DIRECTOR_MODE_API_REFERENCE.md](specs/DIRECTOR_MODE_API_REFERENCE.md)

**Phase 3C** (Complete): Settings-Driven
- [specs/SETTINGS_CONFIGURATION.md](specs/SETTINGS_CONFIGURATION.md)
- [dev_logs/PHASE_3C_SETTINGS_IMPLEMENTATION.md](dev_logs/PHASE_3C_SETTINGS_IMPLEMENTATION.md)

**Phase 3D** (In Progress): Graph Health
- [specs/Phase 3D Graph Health Service - Complete Implementation Plan.md](specs/Phase%203D%20Graph%20Health%20Service%20-%20Complete%20Implementation%20Plan.md)
- [dev_logs/PHASE_3D_GRAPH_HEALTH_IMPLEMENTATION.md](dev_logs/PHASE_3D_GRAPH_HEALTH_IMPLEMENTATION.md)

**Phase 3E** (Complete): Model Orchestration
- [dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md](dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md)
- [dev_logs/PHASE_3E_COMPLETION_SUMMARY.md](dev_logs/PHASE_3E_COMPLETION_SUMMARY.md)
- [CONFIGURABLE_MODEL_ASSIGNMENTS.md](CONFIGURABLE_MODEL_ASSIGNMENTS.md)

**Phase 4** (Planned): Multi-Model Tournament
- [dev_logs/PHASE_3E_PHASES_3_4_IMPLEMENTATION_PLAN.md](dev_logs/PHASE_3E_PHASES_3_4_IMPLEMENTATION_PLAN.md)

**Phase 5** (In Progress): UI/UX Implementation
- [specs/UI_IMPLEMENTATION_PLAN_V2.md](specs/UI_IMPLEMENTATION_PLAN_V2.md)
- [ARCHITECTURE.md](ARCHITECTURE.md) section: UI/UX Implementation Strategy

**Phase 6** (Planned): Polish & Release
- [04_roadmap.md](04_roadmap.md) section: Phase 6

---

## 📊 Documentation Statistics

**Total Files**: 58+ markdown files
- **Root Level**: 14 files
- **Specifications**: 16 files (~350K words)
- **Development Logs**: 20 files (~200K words)
- **Reference Materials**: 13+ folders
- **Archived**: 9+ files

**Total Word Count**: ~400K words

**Documentation Coverage**:
- ✅ **Architecture**: Complete
- ✅ **Backend Services**: Complete (88 API endpoints documented)
- ✅ **UI/UX Strategy**: Complete (87 components planned)
- ✅ **Phase 3E (Model Orchestrator)**: Complete
- 🚧 **Phase 3D (Graph Health)**: In Progress (4/7 checks)
- 📋 **Phase 4 (Tournament)**: Planned
- 🚧 **Phase 5 (UI)**: In Progress (Track 1 starting)

---

## 🚀 Current Development Status

**Active Phase**: Phase 5 (UI/UX Implementation) - Track 1 Critical UI
**Parallel Work**: Phase 3D (Graph Health) - 3 remaining checks

**Next Steps**:
1. ✅ Documentation reorganization (Complete)
2. ⏳ Push to GitHub
3. ⏳ Start Track 1 UI Implementation (Week 1):
   - SettingsAgents.svelte (API keys)
   - SettingsOrchestrator.svelte (Quality tiers)
   - MainLayout.svelte (4-panel IDE)
   - ForemanChatPanel.svelte (Enhanced chat)
   - StudioPanel.svelte (Mode cards)

**Recommended Reading Order for New Contributors**:
1. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the system
2. [04_roadmap.md](04_roadmap.md) - See where we are
3. [specs/UI_IMPLEMENTATION_PLAN_V2.md](specs/UI_IMPLEMENTATION_PLAN_V2.md) - Understand UI work ahead
4. [BACKEND_SERVICES.md](BACKEND_SERVICES.md) - Understand backend APIs
5. [dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md](dev_logs/PHASE_3_ORCHESTRATOR_COMPLETION.md) - Latest completed work

---

**Last Updated**: November 25, 2025
**Version**: 2.0 (Reorganized)
**Maintained By**: Writers Factory Development Team
