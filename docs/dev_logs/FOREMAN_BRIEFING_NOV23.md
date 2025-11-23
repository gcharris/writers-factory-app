# The Foreman - Architecture Briefing

**Date:** November 23, 2025
**Status:** Phase 2A Implementation Complete
**Purpose:** Brief for external architect review and direction input

---

## What We Built Today

### The Foreman: Intelligent Creative Partner

We implemented **The Foreman** - an Ollama-powered agent that transforms Writers Factory from a tool into a true creative partner. This was an evolution beyond the original "wizard chatbot" concept into something craft-aware and adaptive.

### Key Insight That Drove the Design

The original plan was a linear wizard that collected form inputs. Through design discussion, we realized:

> **A chatbot wizard collects answers. A creative partner challenges weak choices.**

The Foreman doesn't just ask "What's Mickey's flaw?" - it understands that "being poor" is circumstance (not a flaw), and will challenge the writer to dig deeper.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    THE FOREMAN                               │
│           (Ollama Llama 3.2 - Local, Zero Cost)             │
├─────────────────────────────────────────────────────────────┤
│ ARCHITECT Mode     │ DIRECTOR Mode      │ EDITOR Mode       │
│ (Story Bible)      │ (Scene Drafting)   │ (Revision)        │
│ ✅ Implemented     │ 🔮 Planned         │ 🔮 Planned        │
├─────────────────────────────────────────────────────────────┤
│                    WORK ORDER TRACKING                       │
│  □ Protagonist.md (fatal_flaw, the_lie, arc)                │
│  □ Beat_Sheet.md (15 beats, midpoint_type)                  │
│  □ Theme.md (central_theme, statement)                      │
│  □ World_Rules.md (fundamental_rules)                       │
├─────────────────────────────────────────────────────────────┤
│                    KNOWLEDGE BASE (KB)                       │
│  • Decisions & constraints from writer                       │
│  • Character facts established                               │
│  • World rules agreed upon                                   │
│  • Persists across sessions                                  │
├─────────────────────────────────────────────────────────────┤
│               NOTEBOOKLM INTEGRATION (via MCP)               │
│  • "world" notebooks → Setting, factions                     │
│  • "voice" notebooks → Character voice extraction            │
│  • "craft" notebooks → Narrative technique reference         │
└─────────────────────────────────────────────────────────────┘
```

---

## What's Implemented (Tested & Working)

### API Endpoints
| Endpoint | Purpose | Status |
|----------|---------|--------|
| `POST /foreman/start` | Initialize project with protagonist | ✅ |
| `POST /foreman/chat` | Chat with Foreman (Ollama) | ✅ |
| `POST /foreman/notebook` | Register NotebookLM by role | ✅ |
| `GET /foreman/status` | Get work order status | ✅ |
| `POST /foreman/flush-kb` | Export KB entries | ✅ |
| `POST /foreman/reset` | Reset for new project | ✅ |

### Core Classes
- `ForemanMode` - ARCHITECT, DIRECTOR, EDITOR
- `WorkOrder` - Tracks template completion
- `TemplateRequirement` - Individual template status
- `Foreman` - Main agent class (~700 lines)

### Craft Knowledge Embedded
- Fatal Flaw vs Circumstance distinction
- The Lie (mistaken belief driving behavior)
- 15-Beat Save the Cat! structure
- Midpoint types (False Victory / False Defeat)
- Character arc progression

---

## Context Window Design

```
FOREMAN CONTEXT (~7000 tokens, fits Llama 3.2)
├── [SYSTEM PROMPT] ~2000 tokens
│   └── Craft knowledge, mode-specific skills
├── [WORK ORDER] ~200 tokens
│   └── Template completion status
├── [KB RETRIEVAL] ~1000 tokens
│   └── Relevant decisions, constraints
└── [CONVERSATION] ~4000 tokens
    └── Recent writer exchanges
```

---

## Sample Conversation (Actual Test Output)

**Input:** "Hello! I am ready to start working on my story about Mickey Bardot. He is a brilliant but troubled AI researcher."

**Foreman Response:**
> Mickey Bardot sounds like an intriguing protagonist! Before we dive into the narrative protocol, let's assess what we have available in terms of resources.
>
> Gaps we've identified so far include:
> - A clear understanding of Mickey's Fatal Flaw (internal weakness) and The Lie (mistaken belief driving it)
> - Development of Mickey's character voice across multiple scenes
> - A well-defined Beat Sheet with a clear structure
>
> Proposed next steps:
> 1. Query the NotebookLM notebook to gather insights on AI research and potential themes
> 2. Explore possible world-building rules that could shape Mickey's story
>
> Do you have any specific questions or concerns about these proposed steps?

---

## What's NOT Yet Implemented

### Phase 2A Remaining
- [ ] **Smart multi-notebook orchestration** - Foreman auto-selects which notebook to query based on question type (currently manual registration works)

### Phase 2B: Director Mode
- [ ] Scene drafting with context injection from KB
- [ ] Beat awareness ("this scene serves Beat 4")
- [ ] Fatal Flaw challenge detection in drafts
- [ ] Multi-model draft comparison

### Phase 2C: Editor Mode
- [ ] Voice consistency analysis
- [ ] Timeline validation
- [ ] Theme resonance scoring

### Phase 3: Metabolism (Original Roadmap)
- [ ] Session compaction (summarize long chats)
- [ ] Conflict resolution (detect contradictions)

---

## Decision Points for Architect Review

### 1. Multi-Notebook Orchestration
**Current:** Writer manually registers notebooks by role (world/voice/craft)
**Question:** Should the Foreman auto-detect which notebook to query based on the question, or is explicit registration better for control?

### 2. KB Persistence
**Current:** KB entries stored in memory, flushed via endpoint
**Question:** Should KB entries auto-persist to files? To the knowledge graph? To SQLite?

### 3. Action System
**Current:** Foreman can emit JSON action blocks that get executed
**Question:** Is the action system robust enough? Should we add more action types?

### 4. Next Focus
**Options:**
- A) Complete Phase 2A (smart notebook orchestration)
- B) Phase 3 (session compaction, conflict resolution)
- C) Integration testing with real NotebookLM notebooks
- D) UI integration (wire Foreman into desktop app)

---

## Files for Review

### Primary Implementation
1. `backend/agents/foreman.py` - Core Foreman implementation (~700 lines)
2. `docs/specs/STORY_BIBLE_ARCHITECT.md` - Complete specification (~680 lines)

### Updated Documentation
3. `docs/BACKEND_SERVICES.md` - Service layer docs (Foreman section added)
4. `docs/API_REFERENCE.md` - API docs (Foreman endpoints added)

### Context Files
5. `docs/04_roadmap.md` - Overall roadmap
6. `docs/ARCHITECTURE.md` - System architecture

---

## Technical Details

- **Model:** Ollama Llama 3.2:3b (local, zero API cost)
- **Timeout:** 120 seconds for Ollama calls
- **HTTP Client:** httpx (async)
- **Integration:** NotebookLM via existing MCP bridge

---

*Prepared for Gemini Architect Review - November 23, 2025*
