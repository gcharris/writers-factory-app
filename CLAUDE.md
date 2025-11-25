# CLAUDE.md - Writers Factory Desktop App

> AI assistant guide for understanding and developing the Writers Factory codebase.

## Project Overview

Writers Factory is a **professional novel-writing IDE** built as a desktop-first application using **Tauri + SvelteKit (frontend)** and **Python FastAPI (backend)**. It enforces a structured creative methodology called the **Narrative Protocol** while providing AI-powered assistance for the complete novel-writing workflow.

**Core Philosophy**: "Structure Before Freedom" - Writers must complete Story Bible artifacts before accessing drafting features.

---

## Quick Reference

### Tech Stack
- **Frontend**: SvelteKit 5, TypeScript, Tauri v2, Monaco Editor
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, NetworkX
- **AI Services**: Multi-model (Claude, GPT-4o, Gemini, Grok, DeepSeek, Mistral, Qwen), Ollama (local)
- **Storage**: SQLite (sessions, settings), JSON (knowledge graph)

### Key Ports
- Frontend Dev Server: `http://localhost:1420`
- Backend API: `http://localhost:8000`
- Ollama: `http://localhost:11434`

### Essential Commands

```bash
# Backend
cd backend
pip install -r ../requirements.txt
uvicorn api:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Run with Tauri (desktop app)
cd frontend
npm run tauri dev

# Test pipeline (standalone)
python run_pipeline.py
```

---

## Repository Structure

```
writers-factory-app/
├── backend/                    # Python FastAPI backend
│   ├── api.py                  # Main FastAPI app (~110KB, 88+ endpoints)
│   ├── ingestor.py             # Markdown → Knowledge Graph
│   ├── agents/
│   │   ├── foreman.py          # THE FOREMAN - Ollama-powered creative partner (~76KB)
│   │   ├── orchestrator.py     # SceneTournament, DraftCritic
│   │   ├── registry.py         # AgentRegistry (loads agents.yaml)
│   │   ├── specialists/
│   │   │   └── scaffold.py     # SmartScaffoldAgent
│   │   └── wizard/             # Project setup wizard
│   ├── bridges/
│   │   └── gemini_cli.py       # Gemini API bridge
│   ├── graph/
│   │   ├── graph_service.py    # KnowledgeGraphService
│   │   ├── schema.py           # SQLAlchemy models (Node, Edge)
│   │   └── ner_extractor.py    # Entity extraction
│   ├── services/               # Core business logic
│   │   ├── consolidator_service.py    # "The Liver" - digests sessions
│   │   ├── foreman_kb_service.py      # Foreman Knowledge Base
│   │   ├── graph_health_service.py    # LLM-powered health checks
│   │   ├── llm_service.py             # LLM abstraction layer
│   │   ├── model_capabilities.py      # Model capability matrix
│   │   ├── model_orchestrator.py      # Quality tier routing
│   │   ├── notebooklm_service.py      # NotebookLM MCP client
│   │   ├── scene_analyzer_service.py  # 5-category scene analysis
│   │   ├── scene_enhancement_service.py
│   │   ├── scene_writer_service.py    # Multi-model scene generation
│   │   ├── session_service.py         # Chat persistence
│   │   ├── settings_service.py        # SQLite-backed settings
│   │   ├── story_bible_service.py     # Story Bible parsing
│   │   └── voice_calibration_service.py
│   ├── workflows/
│   │   ├── base.py             # Workflow base classes
│   │   └── smart_scaffold.py   # AI scaffolding workflow
│   ├── templates/              # Story structure templates
│   └── external/               # External MCP servers
│       ├── notebooklm-mcp/     # NotebookLM integration
│       └── khengyun-mcp/       # Additional MCP tools
├── frontend/                   # SvelteKit + Tauri frontend
│   ├── src/
│   │   ├── routes/
│   │   │   └── +page.svelte    # Main 3-panel layout
│   │   └── lib/
│   │       ├── api_client.ts   # TypeScript API client
│   │       ├── stores.js       # Svelte stores
│   │       └── components/     # UI components
│   │           ├── AgentPanel.svelte
│   │           ├── ChatSidebar.svelte
│   │           ├── Editor.svelte
│   │           ├── FileTree.svelte
│   │           ├── HealthDashboard.svelte
│   │           ├── NotebookPanel.svelte
│   │           └── TabbedPanel.svelte
│   └── src-tauri/              # Tauri Rust backend
│       └── tauri.conf.json
├── content/                    # User manuscript & Story Bible
│   ├── Characters/             # Character profiles
│   ├── Story Bible/            # Structural artifacts
│   │   ├── Structure/          # Beat Sheet, Scene Strategy
│   │   └── Themes_and_Philosophy/
│   └── World Bible/            # World rules
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # Master architecture doc
│   ├── API_REFERENCE.md        # API endpoint reference
│   ├── BACKEND_SERVICES.md     # Service documentation
│   ├── WORKFLOWS.md            # Workflow infrastructure
│   └── claude-skills/          # Claude-specific skills
├── agents.yaml                 # AI agent configurations
├── requirements.txt            # Python dependencies
└── run_pipeline.py             # Standalone pipeline test
```

---

## The Foreman (Core AI Agent)

The Foreman is the central AI partner, powered by Ollama (Llama 3.2). It operates in three modes:

| Mode | Stage | Purpose |
|------|-------|---------|
| `ARCHITECT` | Conception | Build Story Bible, query NotebookLM, challenge structure |
| `VOICE_CALIBRATION` | Voice | Run tournaments, calibrate author voice |
| `DIRECTOR` | Execution | Draft scenes, inject context, maintain beat awareness |
| `EDITOR` | Polish | Check voice consistency, pacing, continuity |

### Foreman API Endpoints
```
POST /foreman/start          - Initialize new project
POST /foreman/chat           - Chat with Foreman
POST /foreman/notebook       - Register NotebookLM notebook
GET  /foreman/status         - Get current state
POST /foreman/flush-kb       - Flush pending KB entries
POST /foreman/reset          - Reset for new project
```

---

## Key Concepts

### 1. Story Bible System (Narrative Protocol)
Required artifacts before drafting:
- **Protagonist.md**: Fatal Flaw, The Lie, Arc (start/midpoint/resolution)
- **Beat_Sheet.md**: 15-beat structure (Save the Cat! format)
- **Theme.md**: Central theme and thesis
- **World Rules.md**: Fundamental world-building rules

### 2. Knowledge Graph ("The Living Brain")
- NetworkX-based entity graph stored in `knowledge_graph.json`
- Auto-populated from Story Bible and manuscript
- Updated by "The Consolidator" from chat sessions

### 3. Multi-Model Architecture
- 8+ AI models available (defined in `agents.yaml`)
- Model Orchestrator routes by quality tier: Budget/Balanced/Premium
- Ollama (Llama 3.2) for local, zero-cost tasks

### 4. Director Mode Pipeline
```
Scaffold → Structure Variants → Scene Generation → Enhancement → Analysis
```

---

## API Categories (88+ Endpoints)

| Category | Base Path | Description |
|----------|-----------|-------------|
| System | `/agents`, `/manager` | Agent listing, health checks |
| Foreman | `/foreman/*` | Creative partner interactions |
| Files | `/files/*` | File read/write |
| Graph | `/graph/*` | Knowledge graph operations |
| Sessions | `/session/*` | Chat session management |
| Consolidator | `/graph/consolidate/*` | Session → Graph digestion |
| Health | `/health/*` | System and narrative health |
| NotebookLM | `/notebooklm/*` | External research integration |
| Story Bible | `/story-bible/*` | Structure validation |
| Director | `/director/*` | Scene creation pipeline |
| Voice | `/voice-calibration/*` | Voice tournament system |
| Settings | `/settings/*` | Configuration management |
| Orchestrator | `/orchestrator/*` | Model routing |

---

## Development Workflow

### Backend Development
1. Create/modify services in `backend/services/`
2. Add Pydantic models for request/response in `backend/api.py`
3. Register endpoints in `backend/api.py`
4. Document in `docs/API_REFERENCE.md`

### Frontend Development
1. Components go in `frontend/src/lib/components/`
2. API calls through `frontend/src/lib/api_client.ts`
3. State management via Svelte stores in `stores.js`

### Adding a New AI Agent
1. Add configuration to `agents.yaml`
2. Ensure API key env var in `.env` (see `env_template.txt`)
3. Agent auto-loads via `AgentRegistry`

---

## Coding Standards

### Python
- Use type hints throughout
- Pydantic models for all data exchange
- Async/await for I/O operations
- Services follow single-responsibility principle

### TypeScript/Svelte
- Strict TypeScript (see `tsconfig.json`)
- Interface definitions in `api_client.ts`
- Component-based architecture

### File Naming
- Python: `snake_case.py`
- TypeScript/Svelte: `PascalCase.svelte`, `camelCase.ts`
- Markdown docs: `SCREAMING_SNAKE_CASE.md`

---

## Environment Setup

Copy `env_template.txt` to `.env` and configure:

```bash
# Essential (at least one required for cloud features)
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...

# Optional cloud models
XAI_API_KEY=...           # Grok
DEEPSEEK_API_KEY=...
QWEN_API_KEY=...          # Alibaba
MISTRAL_API_KEY=...

# Local (Ollama - no key needed)
OLLAMA_API_KEY=local
```

---

## Current Development Status

### Backend: Feature-Complete
- Story Bible System (Phase 2)
- Voice Calibration (Phase 2B)
- Director Mode (Phase 3B) - 4 services, 16 endpoints
- Settings Service (Phase 3C)
- Graph Health Service (Phase 3D) - 4/7 checks
- Model Orchestrator (Phase 3E.3)
- Foreman (Phase 3E.1) - 8 task types

### Frontend: In Progress (~20% coverage)
- Basic Monaco editor, file tree, chat panel
- Missing: Settings Panel, Story Bible UI, Director Mode UI
- **Critical Blocker**: Settings Panel needed for cloud features

### Next Steps
1. **Track 1 (Critical UI)**: SettingsAgents.svelte, MainLayout.svelte
2. **Track 2 (Backend)**: Complete Phase 3D health checks
3. **Track 3 (Feature UI)**: ARCHITECT, VOICE, DIRECTOR mode UIs

---

## Common Tasks

### Run the Full Stack
```bash
# Terminal 1: Backend
cd backend && uvicorn api:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Ollama (if not running)
ollama serve
```

### Ingest Content to Graph
```bash
curl -X POST http://localhost:8000/graph/ingest
```

### Start a Foreman Session
```bash
curl -X POST http://localhost:8000/foreman/start \
  -H "Content-Type: application/json" \
  -d '{"project_title": "My Novel", "protagonist_name": "Alice"}'
```

### Check Story Bible Status
```bash
curl http://localhost:8000/story-bible/status
```

---

## Important Files to Know

| File | Purpose |
|------|---------|
| `backend/api.py` | All API endpoints (~110KB) |
| `backend/agents/foreman.py` | Core creative AI (~76KB) |
| `backend/services/graph_health_service.py` | LLM-powered analysis (~66KB) |
| `agents.yaml` | AI model configurations |
| `docs/ARCHITECTURE.md` | Master architecture reference |
| `frontend/src/lib/api_client.ts` | TypeScript API client |

---

## Documentation Index

- **Architecture**: `docs/ARCHITECTURE.md`
- **API Reference**: `docs/API_REFERENCE.md`
- **Backend Services**: `docs/BACKEND_SERVICES.md`
- **Workflows**: `docs/WORKFLOWS.md`
- **Roadmap**: `docs/04_roadmap.md`
- **Narrative Protocol**: `docs/NARRATIVE PROTOCOL.md`
- **Model Config**: `docs/CONFIGURABLE_MODEL_ASSIGNMENTS.md`

---

## Testing

### Backend
```bash
# Test graph ingestion (2 files only)
curl -X POST "http://localhost:8000/graph/ingest/test"

# Run pipeline test
python run_pipeline.py
```

### Frontend
```bash
cd frontend
npm run check          # Type checking
npm run check:watch    # Watch mode
```

---

## Troubleshooting

### Ollama Not Responding
```bash
ollama list                    # Check models
ollama pull llama3.2:3b        # Pull required model
ollama serve                   # Start server
```

### Backend Import Errors
Ensure you're running from project root and Python path is set:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Frontend CORS Issues
Check that backend CORS allows frontend origin in `api.py`:
```python
allow_origins=["http://localhost:1420", "http://127.0.0.1:1420"]
```

---

## Notes for AI Assistants

1. **The Graph is Truth**: NetworkX/SQLite graph is source of truth, not text files
2. **Hybrid AI Strategy**: Cloud models for reasoning, Ollama for utility/NER tasks
3. **Invisible Complexity**: Users see "Project Knowledge", not "Cognee" or "Knowledge Graph"
4. **Phase Enforcement**: Story Bible must be complete before enabling Director Mode
5. **Backend-First Development**: Backend is mature; UI is the bottleneck
6. **Multi-Provider Support**: 9+ LLM providers with configurable routing

---

*Last updated: November 2025 | Version: 2.1*
