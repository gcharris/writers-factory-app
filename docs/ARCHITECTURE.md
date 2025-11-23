# Writers Factory - Desktop App Architecture

**Version**: 2.0 (Consolidated)
**Date**: November 22, 2025
**Status**: Foundation Complete, Writers Group Ready

---

## Executive Summary

Writers Factory is a **professional novel-writing IDE** that enforces a structured creative methodology while providing AI-powered assistance. It is designed for a **group of writers** who follow the **Narrative Protocol** methodology.

This document supersedes the Gemini architect's incremental approach and defines the complete system architecture based on:
- `NARRATIVE PROTOCOL.md` - The creative methodology
- `VISION_AND_ROADMAP.md` - The hierarchical structure vision
- `writers-factory-core` - The existing tooling and workflows
- Current `writers-factory-app` implementation

---

## Core Philosophy

### 1. Structure Before Freedom
Writers must complete the **Preparation Phase** (Story Bible artifacts) before accessing the **Execution Phase** (drafting). The system enforces this.

### 2. Hierarchy is Sacred
```
Novel Project
├── Story Bible (MANDATORY)
│   ├── 01_Mindset.md
│   ├── 02_Audience.md
│   ├── 03_Premise.md
│   ├── 04_Theme.md
│   ├── 05_Voice.md
│   ├── Characters/
│   │   ├── Protagonist.md (Fatal Flaw, The Lie, True Character)
│   │   └── Cast.md (by function)
│   ├── Structure/
│   │   ├── Beat_Sheet.md (15 beats)
│   │   └── Scene_Strategy.md (Goal/Conflict/Outcome per scene)
│   └── World/
│       └── Rules.md
├── Manuscript
│   ├── Act 1/
│   │   ├── Chapter 1/
│   │   │   ├── Scene 1.1.md
│   │   │   └── Scene 1.2.md
│   │   └── Chapter 2/
│   └── Act 2/
└── Knowledge Graph (auto-generated)
```

### 3. The Living Brain
The Knowledge Graph is not static. It **evolves** with the manuscript through:
- **Ingestion**: Parse Story Bible → Build initial graph
- **Metabolism**: Chat sessions → Consolidator → Graph updates
- **Archivist**: Scene finalization → Update character arcs, world rules, plot status

### 4. Invisible Complexity
Users never see "Cognee", "Ollama", or "Knowledge Graph". They see:
- "Project Knowledge" (local graph)
- "NotebookLM" (external research)
- "Agents" (AI assistants)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DESKTOP APP (Tauri + Svelte)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  File Tree   │  │   Editor     │  │     Right Sidebar        │  │
│  │  (Hierarchy) │  │   (Monaco)   │  │  • Agent Panel           │  │
│  │              │  │              │  │  • NotebookLM / Health   │  │
│  │              │  │              │  │  • Chat Manager          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PYTHON BACKEND (FastAPI)                      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    KNOWLEDGE ROUTER                            │ │
│  │  • Auto-routes queries to best source                          │ │
│  │  • Query Classification (Character/Plot/World/Technique)       │ │
│  │  • Hybrid queries when needed                                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│         │                    │                    │                  │
│         ▼                    ▼                    ▼                  │
│  ┌────────────┐      ┌────────────┐      ┌────────────────────┐    │
│  │ Knowledge  │      │ NotebookLM │      │    Agent Pool      │    │
│  │   Graph    │      │   (MCP)    │      │ Claude/GPT/Gemini  │    │
│  │  (Local)   │      │ (External) │      │ Grok/DeepSeek      │    │
│  └────────────┘      └────────────┘      └────────────────────┘    │
│         │                                                           │
│         ▼                                                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    METABOLISM SYSTEM                           │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │ │
│  │  │ SessionMgr   │→│ Consolidator │→│  Knowledge Graph  │    │ │
│  │  │ (Workbench)  │  │  (Liver)     │  │  (Living Brain)   │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘    │ │
│  │         ↑                                      │               │ │
│  │         │              ┌──────────────────────┘               │ │
│  │         │              ▼                                       │ │
│  │  ┌──────────────┐  ┌──────────────┐                          │ │
│  │  │   Archivist  │←│ Health Checks │                          │ │
│  │  │ (Scene Done) │  │  (Narrative) │                          │ │
│  │  └──────────────┘  └──────────────┘                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    STORAGE LAYER                               │ │
│  │  • sessions.db (SQLite) - Chat history                        │ │
│  │  • knowledge_graph.json - Entities & relationships            │ │
│  │  • graph_conflicts.json - Unresolved contradictions           │ │
│  │  • Content files (markdown) - Manuscript & Story Bible        │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        LOCAL LLM (Ollama)                           │
│                        Llama 3.2 (3B) - Entity Extraction           │
│                        Zero Cost, Privacy First                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Story Bible Schema

### Protagonist.md (Required Fields)

```markdown
# [Character Name]

## True Character vs Characterization
- **Characterization** (Surface): How they appear to others
- **True Character** (Core): Who they really are under pressure
- **Core Contradiction**: The tension between these two

## Fatal Flaw
The internal weakness that blocks their success.
> Example: "Fear of abandonment leads to controlling behavior"

## The Lie
The mistaken belief driving the flaw.
> Example: "If I let people get close, they'll leave me"

## Arc
- **Starting State**: Where they begin
- **Midpoint Shift**: What challenges the Lie
- **Resolution**: How they change (or fail to)

## Relationships
- [Character]: [Function in protagonist's arc]
```

### Beat_Sheet.md (15-Beat Structure)

```markdown
# Beat Sheet - [Novel Title]

## Act 1: Setup (Beats 1-5)
1. **Opening Image** (1%): [Scene/visual that captures starting state]
2. **Theme Stated** (5%): [Where theme is hinted]
3. **Setup** (1-10%): [Protagonist's ordinary world]
4. **Catalyst** (10%): [Inciting incident]
5. **Debate** (10-20%): [Protagonist's hesitation]

## Act 2A: Fun & Games (Beats 6-9)
6. **Break into Two** (20%): [Protagonist commits]
7. **B Story** (22%): [Subplot/love interest begins]
8. **Fun & Games** (20-50%): [Promise of the premise]
9. **Midpoint** (50%): [False victory/defeat, stakes raise]

## Act 2B: Bad Guys Close In (Beats 10-12)
10. **Bad Guys Close In** (50-75%): [Opposition tightens]
11. **All Is Lost** (75%): [Lowest point, whiff of death]
12. **Dark Night of the Soul** (75-80%): [Protagonist despairs]

## Act 3: Resolution (Beats 13-15)
13. **Break into Three** (80%): [Solution discovered]
14. **Finale** (80-99%): [Final confrontation]
15. **Final Image** (99-100%): [Mirror of opening, showing change]

## Current Progress
- **Active Beat**: [Number]
- **Last Scene Written**: [Act.Chapter.Scene]
```

### Scene_Strategy.md

```markdown
# Scene Strategy

## Scene [Act].[Chapter].[Scene]: [Title]

### Goal
What does the POV character want in this scene?

### Conflict
What stands in their way?

### Outcome
- [ ] Yes - They get what they want
- [ ] No - They don't get it
- [ ] Yes, But - They get it with complications
- [ ] No, And - They don't get it, plus things get worse

### Beat Connection
Which of the 15 beats does this scene serve?

### Character Arc Progress
Does this scene challenge the Fatal Flaw / The Lie?
```

---

## Health Checks (Narrative-Aware)

### Level 1: Graph Health (Current Implementation)
- Node/edge counts
- Orphan nodes (no connections)
- Conflict detection (contradictory facts)

### Level 2: Story Bible Completeness
- [ ] All 5 foundational docs exist
- [ ] Protagonist has Fatal Flaw defined
- [ ] Beat Sheet has all 15 beats
- [ ] Scene Strategy exists for drafted scenes

### Level 3: Narrative Health
- **Beat Progress**: Which beat are we on? Are scenes advancing the structure?
- **Flaw Challenge**: Has the Fatal Flaw been tested recently?
- **Cast Function**: Are supporting characters appearing per their defined function?
- **Theme Resonance**: Do recent scenes connect to 04_Theme.md?

### Level 4: Archivist Checks (Post-Scene)
- Did the character learn something? → Update arc progress
- Did new world facts emerge? → Update World/Rules.md
- Did the plot deviate from Beat Sheet? → Flag for review

---

## Workflows (5-Stage Pipeline)

### Stage 1: Creation (Story Bible)

**Powered by the Story Bible Architect** - See [specs/STORY_BIBLE_ARCHITECT.md](specs/STORY_BIBLE_ARCHITECT.md)

The Story Bible Architect is an **intelligent Ollama-powered agent** (not a form-filling wizard) that:
- Assesses writer's NotebookLM library (multiple notebooks as "consultants")
- Identifies gaps against Narrative Protocol requirements
- Proposes paths: query notebooks, brainstorm, or create new sources
- Challenges weak structural choices with craft expertise
- Synthesizes across sources into proper templates

**Multi-Notebook Architecture:**
```
Writer's NotebookLM Library
├── WORLD NOTEBOOKS (setting, rules, factions)
├── CHARACTER/VOICE NOTEBOOKS (voice samples, real people)
├── CRAFT REFERENCE NOTEBOOKS (favorite novels, films, technique)
└── PROJECT NOTEBOOK (synthesized Story Bible - created at end)
```

**Creative Workflow:**
1. **Notebook Assessment** - Inventory resources, assign roles (world/voice/craft)
2. **Intelligent Gap Analysis** - "I have KAI's situation but not his interior"
3. **Craft-Informed Challenges** - "That's circumstance, not flaw"
4. **Cross-Notebook Synthesis** - Connect insights across sources
5. **Template Generation** - Structure into Story Bible files (via Ollama)
6. **Export for Safety Net** - Copy to `NotebookLM_Export/` for Project Notebook

**Key Distinction:**
- NotebookLM = Research oracle (query multiple specialized notebooks)
- Ollama = Story architect (structures, validates, challenges with craft knowledge)

The Project Notebook (created at end) serves as a **safety net** - if the writer wants to chat directly with NotebookLM about their story, all structured context is available there.

### Stage 2: Writing
- Scene generation with context injection
- Multi-model comparison
- Beat Sheet awareness ("This scene serves Beat 8: Fun & Games")

### Stage 3: Enhancing
- Voice consistency checks
- Metaphor discipline
- Anti-pattern detection

### Stage 4: Analyzing
- Timeline validation
- Character voice consistency
- Pacing analysis

### Stage 5: Scoring
- Quality metrics per scene
- Aggregate manuscript health
- Readiness assessment

---

## Agent Pool (from writers-factory-core)

### Available Agents
| Agent | Provider | Strengths |
|-------|----------|-----------|
| Claude Sonnet 4.5 | Anthropic | Voice, nuance, philosophical depth |
| GPT-4o | OpenAI | Polish, structure, consistency |
| Gemini Pro | Google | Speed, world-building |
| Grok | xAI | Unconventional takes, humor |
| DeepSeek | DeepSeek | Cost-effective drafts |

### Tools from Core (to port)
- **Voice Consistency Tester** - Score scenes on 5 dimensions
- **Scene Multiplier** - Generate 5 variations
- **Scene Enhancement** - Surgical fixes with voice preservation
- **Smart Scaffold Generator** - Outline → Gold Standard scaffold

---

## Knowledge Router

### Query Classification
```
User: "Who is Mickey Bardot?"
→ CHARACTER_LOOKUP → Local Knowledge Graph

User: "How do I write compressed prose?"
→ WRITING_TECHNIQUE → NotebookLM (if configured)

User: "How should I write Mickey's voice in this scene?"
→ HYBRID → Both sources, merged results
```

### Invisible to Users
- Users ask questions naturally
- System routes automatically
- Results show "Source: Project Knowledge" or "Source: NotebookLM"

---

## File Structure (Desktop App)

```
writers-factory-app/
├── backend/
│   ├── api.py                    # FastAPI endpoints
│   ├── ingestor.py               # Story Bible → Graph
│   ├── knowledge_graph.json      # The Living Brain
│   └── services/
│       ├── session_service.py    # Chat persistence
│       ├── consolidator_service.py # Chat → Graph
│       ├── health_service.py     # Narrative checks (TODO)
│       ├── archivist_service.py  # Scene finalization (TODO)
│       └── knowledge_router.py   # Query routing (TODO)
├── frontend/
│   └── src/
│       ├── routes/+page.svelte   # Main layout
│       └── lib/components/
│           ├── FileTree.svelte
│           ├── Editor.svelte
│           ├── AgentPanel.svelte
│           ├── ChatSidebar.svelte
│           ├── TabbedPanel.svelte
│           ├── NotebookPanel.svelte
│           └── HealthDashboard.svelte
├── content/                       # User's manuscript
│   ├── Story Bible/              # (to be created)
│   ├── Characters/
│   ├── World Bible/
│   └── [Scene files]
├── workspace/
│   └── sessions.db               # Chat history
└── docs/
    ├── ARCHITECTURE.md           # This document
    ├── NARRATIVE PROTOCOL.md     # The methodology
    └── UX_ROADMAP.md             # UI evolution plan
```

---

## Implementation Priority

### Phase 1: COMPLETE ✓
- [x] Basic UI (File tree, Editor, Panels)
- [x] NotebookLM MCP integration
- [x] Knowledge Graph ingestor (Ollama)
- [x] Session Manager (SQLite)
- [x] Consolidator (Chat → Graph)
- [x] Health Dashboard (Metabolic)

### Phase 2: Story Bible System (IN PROGRESS)
- [x] Story Bible template scaffolding (`StoryBibleService.scaffold_story_bible()`)
- [x] Protagonist.md parser (extract Fatal Flaw, The Lie, Arc, Contradiction Score)
- [x] Beat_Sheet.md parser (15-beat validation, midpoint type detection)
- [x] Story Bible completeness validation (Level 2 Health Checks)
- [x] API endpoints (`/story-bible/*`)
- [x] Workflow infrastructure (`backend/workflows/base.py`)
- [x] Story Bible Architect specification ([specs/STORY_BIBLE_ARCHITECT.md](specs/STORY_BIBLE_ARCHITECT.md))
- [ ] **Story Bible Architect agent implementation** (Ollama-powered creative partner)
- [ ] Multi-notebook orchestration in frontend
- [ ] NotebookLM_Export directory and workflow

### Phase 3: Narrative Health
- [ ] Health checks that understand Story Bible structure
- [ ] Beat progress tracking
- [ ] Flaw challenge detection
- [ ] Cast function monitoring

### Phase 4: Archivist
- [ ] Scene finalization workflow
- [ ] Auto-update character arcs
- [ ] World rules consistency
- [ ] Plot deviation flags

### Phase 5: Advanced Workflows
- [ ] Port tools from writers-factory-core
- [ ] Multi-model scene comparison
- [ ] Voice consistency scoring
- [ ] Scene multiplier

---

## Technical Specifications

The following detailed specifications address low-level implementation requirements. Each is maintained as a separate document for clarity.

| Specification | Purpose | Document |
|---------------|---------|----------|
| **Story Bible Architect** | Ollama-powered creative partner, multi-notebook orchestration, system prompt | [specs/STORY_BIBLE_ARCHITECT.md](specs/STORY_BIBLE_ARCHITECT.md) |
| **Story Bible System** | Phase 2 technical requirements, parsers, validation | [specs/Technical specifications and requirements for Story Bible System.md](specs/Technical%20specifications%20and%20requirements%20for%20Story%20Bible%20System.md) |
| **File Synchronization** | External edit detection, graph re-ingestion triggers | [specs/FILE_SYNC.md](specs/FILE_SYNC.md) |
| **Security & Credentials** | API key storage, encryption, OS keychain integration | [specs/SECURITY.md](specs/SECURITY.md) |
| **RAG Implementation** | Chunking strategy, retrieval logic, context budgets | [specs/RAG_IMPLEMENTATION.md](specs/RAG_IMPLEMENTATION.md) |
| **Scoring Rubrics** | Critic agent prompts, quality metrics, scoring algorithms | [specs/SCORING_RUBRICS.md](specs/SCORING_RUBRICS.md) |

### Summary of Technical Requirements

**File Sync**: The Knowledge Graph is the "source of truth", but users may edit markdown files externally. The system must detect changes via file watchers and trigger re-ingestion to maintain graph consistency.

**Security**: API keys for cloud models (OpenAI, Anthropic, Google, xAI) must be stored securely using OS-native keychains, never in plaintext config files.

**RAG-Lite**: The Knowledge Router must chunk documents appropriately, retrieve relevant context, and fit within model context windows while preserving narrative coherence.

**Scoring**: Quality metrics (Voice Consistency, Metaphor Discipline, Theme Resonance, etc.) require explicit rubrics and scoring prompts for the Critic Agent.

---

## Notes for Future Sessions

1. **The Gemini architect** builds generic infrastructure. This document defines the **actual** requirements based on your methodology.

2. **writers-factory-core** has valuable tools (Voice Tester, Scene Multiplier, etc.) that should be ported, not rebuilt.

3. **The Knowledge Router** should route to local graph OR NotebookLM automatically - users never choose.

4. **Health checks** should be narrative-aware, not just graph-structure-aware. "Has the Fatal Flaw been challenged?" is more valuable than "orphan node count."

5. **The Archivist agent** is the key to making the Knowledge Graph truly "living" - it updates after every scene.
