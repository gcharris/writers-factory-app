# Writers Factory Technical Documentation

> Complete technical documentation for the Writers Factory desktop application.

---

## Quick Links

| Document | Description |
|----------|-------------|
| [API Reference](API_REFERENCE.md) | All REST API endpoints |
| [Backend Services](BACKEND_SERVICES.md) | Service layer documentation |
| [Workflows](WORKFLOWS.md) | Workflow infrastructure guide |
| [Architecture](ARCHITECTURE.md) | System architecture & roadmap |
| [The Foreman Spec](specs/STORY_BIBLE_ARCHITECT.md) | Intelligent creative partner design |

---

## Architecture Overview

```
writers-factory-app/
├── frontend/                    # Tauri + React UI
│   └── src/
│       ├── components/          # React components
│       └── services/            # API client
├── backend/                     # FastAPI backend
│   ├── api.py                   # Main API (~850 lines)
│   ├── services/                # Business logic
│   ├── workflows/               # Multi-step workflows
│   ├── graph/                   # Knowledge graph
│   └── agents/                  # AI agents
├── content/                     # Story Bible & manuscripts
│   ├── Characters/
│   ├── Story Bible/
│   └── World Bible/
└── docs/                        # Documentation
```

---

## Core Concepts

### The Narrative Protocol

Writers Factory implements the **Narrative Protocol** - a structured approach to novel writing:

1. **Phase 1: NotebookLM Preparation** - Upload research to Google NotebookLM
2. **Phase 2: Story Bible System** - Generate structured artifacts (enforced before drafting)
3. **Phase 3: Execution** - Draft scenes with AI assistance
4. **Phase 4: Archive** - Finalize and store completed scenes

### Key Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| `Protagonist.md` | `content/Characters/` | Character with Fatal Flaw & The Lie |
| `Beat_Sheet.md` | `content/Story Bible/Structure/` | 15-beat Save the Cat! structure |
| `Scene_Strategy.md` | `content/Story Bible/Structure/` | Scene-level planning |
| `04_Theme.md` | `content/Story Bible/Themes_and_Philosophy/` | Theme documentation |
| `Rules.md` | `content/World Bible/` | World-building rules |

### Level 2 Health Checks

Before proceeding to Phase 3 (Execution), the system validates:

- [ ] Protagonist file exists
- [ ] Protagonist has Fatal Flaw defined
- [ ] Protagonist has The Lie defined
- [ ] Beat Sheet exists
- [ ] Beat Sheet is complete (all 15 beats)

Check status: `GET /story-bible/can-execute`

---

## API Reference Summary

### Endpoint Groups

| Group | Base Path | Description |
|-------|-----------|-------------|
| System | `/agents`, `/manager` | Agent listing, health checks |
| **Foreman** | `/foreman/*` | Intelligent creative partner |
| Files | `/files/{path}` | Read/write files |
| Graph | `/graph/*` | Knowledge graph operations |
| Sessions | `/session/*` | Chat session management |
| Consolidator | `/graph/consolidate` | "The Liver" - session digestion |
| Health | `/health/status` | Combined dashboard data |
| NotebookLM | `/notebooklm/*` | External research queries |
| Story Bible | `/story-bible/*` | Phase 2 system |

### Key Endpoints

```
# The Foreman (Intelligent Creative Partner)
POST /foreman/start               # Initialize project with protagonist
POST /foreman/chat                # Chat with Foreman (Ollama-powered)
POST /foreman/notebook            # Register NotebookLM notebook
GET  /foreman/status              # Get work order status
POST /foreman/reset               # Reset for new project

# Story Bible System
GET  /story-bible/status          # Level 2 Health Checks
POST /story-bible/scaffold        # Create templates
POST /story-bible/smart-scaffold  # AI-powered generation
GET  /story-bible/can-execute     # Phase 3 gate
GET  /health/status               # Dashboard data
POST /graph/ingest                # Ingest content to graph
POST /notebooklm/query            # Query NotebookLM
```

[Full API Reference →](API_REFERENCE.md)

---

## Backend Services Summary

### Core Services

| Service | File | Purpose |
|---------|------|---------|
| **The Foreman** | `agents/foreman.py` | Ollama-powered intelligent creative partner |
| `StoryBibleService` | `services/story_bible_service.py` | Story Bible parsing & validation |
| `NotebookLMMCPClient` | `services/notebooklm_service.py` | NotebookLM integration |
| `SessionService` | `services/session_service.py` | Chat persistence |
| `ConsolidatorService` | `services/consolidator_service.py` | Graph digestion |
| `KnowledgeGraphService` | `graph/graph_service.py` | Entity storage |
| `GraphIngestor` | `ingestor.py` | File → Graph ingestion |

### Key Data Classes

```python
# From agents/foreman.py
ForemanMode         # ARCHITECT, DIRECTOR, EDITOR
WorkOrder           # Project tracking with template completion
TemplateRequirement # Individual template status

# From story_bible_service.py
ProtagonistData     # Character profile with Fatal Flaw, The Lie, Arc
BeatData            # Single beat (1-15)
BeatSheetData       # Complete 15-beat structure
StoryBibleStatus    # Level 2 Health Check results
```

[Full Services Documentation →](BACKEND_SERVICES.md)

---

## Workflows Summary

### Workflow Infrastructure

Base classes in `backend/workflows/base.py`:

- `WorkflowStep` - Single step with timing and status
- `WorkflowResult` - Execution result container
- `Workflow` - Abstract base class

### Implemented Workflows

| Workflow | Purpose | Steps |
|----------|---------|-------|
| `SmartScaffoldWorkflow` | AI Scaffolding Agent | Query protagonist → Query beats → Query themes → Query world → Synthesize → Validate |

### Usage

```python
from backend.workflows.smart_scaffold import SmartScaffoldWorkflow

workflow = SmartScaffoldWorkflow(nlm_client, story_bible_service)
result = await workflow.run(
    notebook_id="abc123",
    project_title="Big Brain",
    protagonist_name="Mickey Bardot"
)
```

[Full Workflows Documentation →](WORKFLOWS.md)

---

## Technical Specifications

Located in `docs/specs/`:

| Spec | Description |
|------|-------------|
| [FILE_SYNC.md](specs/FILE_SYNC.md) | File watching & incremental ingestion |
| [SECURITY.md](specs/SECURITY.md) | Security considerations |
| [RAG_IMPLEMENTATION.md](specs/RAG_IMPLEMENTATION.md) | Context retrieval design |
| [SCORING_RUBRICS.md](specs/SCORING_RUBRICS.md) | Draft evaluation criteria |

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ (for NotebookLM MCP server)
- Ollama with `llama3.2` model (for local LLM)

### Quick Start

```bash
# Backend
cd writers-factory-app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables

Create `backend/.env`:

```env
OPENAI_API_KEY=sk-...          # For GPT-4 agents
ANTHROPIC_API_KEY=sk-ant-...   # For Claude agents (optional)
GOOGLE_API_KEY=...             # For Gemini (optional)
```

---

## File Index

### Documentation Files

```
docs/
├── index.md                    # Course syllabus
├── DOCS_INDEX.md              # This file
├── manifesto.md               # Philosophy
├── ARCHITECTURE.md            # System architecture
├── API_REFERENCE.md           # API documentation
├── BACKEND_SERVICES.md        # Services documentation
├── WORKFLOWS.md               # Workflow documentation
├── UX_ROADMAP.md              # UI/UX plans
├── 01_architecture.md         # Original arch doc
├── 02_scene_pipeline.md       # Scene pipeline doc
├── 03_data_schema.md          # Data schema doc
├── 04_roadmap.md              # Development roadmap
├── specs/
│   ├── FILE_SYNC.md
│   ├── SECURITY.md
│   ├── RAG_IMPLEMENTATION.md
│   └── SCORING_RUBRICS.md
├── dev_logs/                  # Development logs
└── archive/                   # Old versions
```

### Key Source Files

```
backend/
├── api.py                     # 950+ lines, 45+ endpoints
├── agents/
│   └── foreman.py             # 700+ lines, THE FOREMAN (Ollama-powered)
├── services/
│   └── story_bible_service.py # 1100+ lines, Phase 2 implementation
├── workflows/
│   ├── base.py                # 209 lines, workflow infrastructure
│   └── smart_scaffold.py      # 476 lines, AI scaffolding agent
└── ingestor.py                # Graph ingestion from files
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | Nov 2024 | Initial Phase 2 implementation |

---

*Writers Factory v0.1 - Technical Documentation*
