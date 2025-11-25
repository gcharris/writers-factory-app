# Writers Factory

**AI-Augmented Novel Writing Desktop Application**

Writers Factory is a desktop-first application that transforms novel writing through intelligent AI collaboration. Built on Tauri + SvelteKit + FastAPI, it provides a complete IDE for long-form fiction with voice consistency, structural validation, and multi-model AI orchestration.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

---

## 🎯 What It Does

Writers Factory helps novelists:
- **Discover Your Voice** through AI agent tournaments (5 models × 5 strategies = 25 variants)
- **Write Scene-by-Scene** with Director Mode (scaffold → structure → draft → enhance → validate)
- **Maintain Consistency** via Story Bible (15-beat structure, character arcs, world rules)
- **Validate Structure** with Graph Health checks (pacing, theme, timeline, character arcs)
- **Choose Quality Tiers** from Budget (free local) to Premium (best cloud AI)

**Built with the Explants novel** (120K words, cyber-noir) as the reference implementation.

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Rust** (for Tauri) - [Install rustup](https://rustup.rs/)
- **Ollama** (for local AI) - [Install Ollama](https://ollama.ai/)

### Installation

```bash
# Clone repository
git clone https://github.com/gcharris/writers-factory-app.git
cd writers-factory-app

# Install Ollama model for local processing
ollama pull llama3.2

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Configure API keys (optional - enables cloud features)
cp .env.example .env
# Edit .env with your API keys (OpenAI, Anthropic, DeepSeek, Qwen)
```

### Running the App

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run tauri dev  # Desktop app
# OR
npm run dev        # Browser (http://localhost:1420)
```

---

## 🏗️ Architecture

### Tech Stack
- **Frontend**: SvelteKit + Tauri (desktop) with Monaco Editor
- **Backend**: FastAPI + Python with SQLite
- **AI**: Multi-provider (Anthropic, OpenAI, DeepSeek, Qwen, Ollama)
- **Knowledge**: NotebookLM integration via MCP
- **Graph**: NetworkX + SQLite for manuscript structure

### 4-Panel IDE Layout
```
┌─────────────┬──────────────────┬─────────────┬─────────────┐
│   Studio    │      Canvas      │   Foreman   │    Graph    │
│   (280px)   │      (flex)      │   (320px)   │   (240px)   │
│             │                  │             │             │
│ • Actions   │ • Monaco Editor  │ • Chat      │ • Health    │
│ • Modes     │ • File Tree      │ • Memory    │ • Structure │
│ • Settings  │ • Manuscript     │ • KB        │ • Metrics   │
└─────────────┴──────────────────┴─────────────┴─────────────┘
```

### Key Services
- **The Foreman** - Ollama-powered creative partner (8 task types, intelligent routing)
- **Director Mode** - 4 services for scene creation (Analyzer, Scaffold, Writer, Enhancement)
- **Voice Calibration** - Tournament-based voice discovery with Gold Standard generation
- **Graph Health** - 7 structural checks (pacing, timeline, theme, character arcs)
- **Model Orchestrator** - 3 quality tiers with automatic model selection

---

## 📚 Core Workflows

### 1. ARCHITECT Mode: Story Bible Creation
Build your novel's foundation:
- **15-Beat Structure** (Save the Cat! methodology)
- **Character Profiles** (Fatal Flaw, The Lie, transformation arc)
- **World Rules** (consistent physics, geography, magic systems)
- **Thematic Questions** (6 core questions guiding the narrative)

### 2. VOICE_CALIBRATION Mode: Voice Discovery
Find your narrative voice through AI tournaments:
- **Multi-Agent Competition** - 5+ models compete on test passage
- **5 Strategy Variants** - ACTION, CHARACTER, DIALOGUE, ATMOSPHERIC, BALANCED
- **Voice Reference Bundle** - Gold Standard + Anti-Patterns + Phase Evolution
- **Automatic Integration** - Voice travels with every Director Mode call

### 3. DIRECTOR Mode: Scene-by-Scene Writing
Write with AI collaboration and quality validation:

**Workflow**: Scaffold → Structure → Draft → Enhance → Validate

**Scaffold Generator**:
- 2-stage flow: Draft Summary → Optional NotebookLM enrichment → Full Scaffold
- Pulls from Story Bible, KB decisions, previous scene continuity

**Scene Writer**:
- Structure variants (5 different approaches before writing prose)
- Tournament mode (3 models × 5 strategies = 15 scenes)
- Voice Bundle injection (maintains consistency)
- Auto-scoring (100-point rubric with 5 categories)

**Scene Enhancement**:
- **Action Prompt (85+)**: Surgical OLD → NEW fixes
- **6-Pass Enhancement (70-84)**: Full ritual (Sensory, Verb, Metaphor, Voice, Italics, Auth)
- **Rewrite (<70)**: Return to Scene Writer

**Scene Analyzer**:
- 5-category rubric: Voice (30), Character (20), Metaphor (20), Anti-Pattern (15), Phase (15)
- Zero-tolerance violation detection
- Metaphor domain saturation analysis

### 4. Graph Health: Structural Validation
Macro-level quality checks across chapters:
- **Pacing Failure Detection** - Tension plateau analysis
- **Beat Progress Validation** - 15-beat structure compliance
- **Timeline Consistency** - Character locations, world rules, dropped threads
- **Fatal Flaw Challenges** - Character arc tracking
- **Cast Function Verification** - Character purpose analysis
- **Symbolic Layering** - Symbol recurrence and evolution
- **Theme Resonance** - Thematic alignment scoring

---

## 🎛️ Configuration

### Quality Tiers

Choose your cost/quality balance:

| Tier | Models | Cost/Month | Use Case |
|------|--------|------------|----------|
| **Budget** | Ollama (local) | $0 | Experimenting, drafting |
| **Balanced** | DeepSeek + Qwen | $0.50-1 | Most writers (recommended) |
| **Premium** | Claude + GPT-4o | $3-5 | Final drafts, critical scenes |

### API Keys (Optional)

Configure in Settings Panel or `.env`:
```bash
# Cloud AI (enables Premium/Balanced tiers)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
QWEN_API_KEY=sk-...

# NotebookLM (enables research integration)
NOTEBOOKLM_PROJECT_ID=your-project-id
```

**Without API keys**: Full functionality with local Ollama (Budget tier only)

### Settings System

3-tier resolution:
1. **Project Settings** - Stored in `voice_settings.yaml` per project
2. **Global Settings** - User preferences in SQLite
3. **Default Settings** - System defaults in `settings.yaml`

11 configurable categories: Voice, Director, Enhancement, Health, Orchestrator, NotebookLM, Graph, Foreman, Session, Export, Advanced

---

## 🧪 Testing

Comprehensive backend test coverage:

```bash
cd backend
pytest tests/ -v

# Run specific test suites
pytest tests/test_scene_analyzer_service.py -v
pytest tests/test_scaffold_generator_service.py -v
pytest tests/test_scene_enhancement_service.py -v
pytest tests/test_voice_calibration_service.py -v
```

**Coverage**: 4 of 19 services tested (21%), 2,090 lines of tests

See [docs/TESTING.md](docs/TESTING.md) for detailed testing documentation.

---

## 📖 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and UI/UX strategy
- **[04_roadmap.md](docs/04_roadmap.md)** - Development roadmap and phase tracking
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - All 98 REST API endpoints
- **[BACKEND_SERVICES.md](docs/BACKEND_SERVICES.md)** - Service layer documentation
- **[TESTING.md](docs/TESTING.md)** - Testing strategy and coverage
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Developer contribution guide
- **[DOCS_INDEX.md](docs/DOCS_INDEX.md)** - Complete documentation index

**Total Documentation**: 58+ files (~400K words)

---

## 🚀 Development Status

### ✅ Completed Phases

- **Phase 1**: Foundation (Tauri + Svelte + FastAPI, Graph Engine, Basic UI)
- **Phase 2**: NotebookLM Integration (MCP bridge, research queries)
- **Phase 2B**: Voice Calibration (Tournament system, Voice Bundle generation)
- **Phase 3**: The Foreman (Ollama-powered partner, KB service, session persistence)
- **Phase 3B**: Director Mode (4 services, 16 API endpoints, complete scene workflow)
- **Phase 3C**: Settings-Driven (Dynamic configuration, 3-tier resolution)
- **Phase 3D**: Graph Health (7 health checks, LLM-powered analysis)
- **Phase 3E**: Model Orchestration (3 quality tiers, automatic model selection)
- **Phase 5 Track 1**: Critical UI (11 components, Settings Panel unblocked)

### 🚧 In Progress

- **Phase 5 Track 3**: Feature UI (87 components total, following Foreman modes)
  - Week 2: ARCHITECT Mode UI (7 components)
  - Week 3: VOICE_CALIBRATION Mode UI (6 components)
  - Week 4: DIRECTOR Mode UI (16 components)
  - Week 5: Graph Health UI (4 components)
  - Week 6: Settings Polish (remaining components)

### 📋 Planned

- **Phase 4**: Multi-Model Tournament (Consensus detection, dispute flagging)
- **Phase 6**: Polish & Release (Packaging, optimizations, plugins, documentation)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

**Key Areas Needing Help**:
- Frontend UI components (Phase 5)
- Backend test coverage (13 services remaining)
- Documentation improvements
- Bug reports and feature requests

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **The Explants** - 120K word cyber-noir novel used as reference implementation
- **Save the Cat!** - Blake Snyder's 15-beat structure
- **NotebookLM** - Google's research tool (MCP integration)
- **Ollama** - Local LLM infrastructure
- **Anthropic, OpenAI, DeepSeek, Qwen** - Cloud AI providers

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/gcharris/writers-factory-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gcharris/writers-factory-app/discussions)
- **Documentation**: [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md)

---

**Built with ❤️ for novelists who want AI collaboration without losing their voice.**
