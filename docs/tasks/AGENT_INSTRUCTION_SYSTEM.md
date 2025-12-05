# Agent Instruction System Implementation

> Task specification for implementing the Universal Agent Instruction Architecture with support for agent-switchable chat.

**Status**: Ready for Implementation
**Priority**: High
**Depends On**: Mode Transition UI (DONE)
**Source Document**: `docs/UNIVERSAL_AGENT_INSTRUCTION_ARCHITECTURE.md`

---

## Overview

Implement a modular prompt system that:
1. Extracts prompts from Python strings to maintainable `.md` files
2. Assembles context-aware prompts via the "Context Sandwich" architecture
3. Supports multiple selectable agents (not just The Foreman)
4. Uses XML output format for universal parsing across all LLM providers
5. Adapts prompt complexity based on model capabilities (tier-based assembly)

### Key Paradigm: Agent-Switchable Chat

Writers can select different AI agents mid-conversation (like Cursor AI):

```
Writer → [Agent Selector] → "The Foreman" (mode-aware, structural)
                         → "Character Coach" (character development specialist)
                         → "Plot Doctor" (structure/pacing specialist)
                         → "Voice Stylist" (prose/voice specialist)
                         → "Research Assistant" (NotebookLM-focused)
```

Each agent has:
- Its own identity/persona
- Specific capabilities (available actions)
- Shared access to project context (Knowledge Graph, KB, Voice Bundle)
- Shared output protocols (XML format)

---

## Phase 1: Prompt Extraction

**Goal**: Move embedded prompts to maintainable markdown files.

### Deliverables

```
backend/prompts/
├── shared/
│   ├── project_context.md      # Writers Factory context (what is this app)
│   ├── protocols.md            # XML output format (universal)
│   └── guardrails/
│       ├── voice_antipatterns.md   # Zero-tolerance patterns
│       └── continuity_rules.md     # Continuity checking rules
├── agents/
│   ├── foreman/
│   │   ├── identity.md         # Core Foreman persona
│   │   ├── process_map.md      # All modes overview
│   │   └── modes/
│   │       ├── architect.md
│   │       ├── voice_calibration.md
│   │       ├── director.md
│   │       └── editor.md
│   ├── character_coach/
│   │   └── identity.md
│   ├── plot_doctor/
│   │   └── identity.md
│   ├── voice_stylist/
│   │   └── identity.md
│   └── research_assistant/
│       └── identity.md
└── agents.yaml                 # Agent registry configuration
```

### Tasks

- [ ] **1.1** Create `backend/prompts/` directory structure
- [ ] **1.2** Extract `ARCHITECT_SYSTEM_PROMPT` from `foreman.py` → `prompts/agents/foreman/modes/architect.md`
- [ ] **1.3** Extract `VOICE_CALIBRATION_SYSTEM_PROMPT` → `prompts/agents/foreman/modes/voice_calibration.md`
- [ ] **1.4** Extract `DIRECTOR_SYSTEM_PROMPT` → `prompts/agents/foreman/modes/director.md`
- [ ] **1.5** Create `prompts/agents/foreman/modes/editor.md` (currently missing in codebase)
- [ ] **1.6** Factor out common Foreman identity → `prompts/agents/foreman/identity.md`
- [ ] **1.7** Create `prompts/agents/foreman/process_map.md` (mode overview)
- [ ] **1.8** Create `prompts/shared/protocols.md` (XML output format)
- [ ] **1.9** Create `prompts/shared/project_context.md` (Writers Factory intro)
- [ ] **1.10** Create `prompts/shared/guardrails/voice_antipatterns.md`
- [ ] **1.11** Create `prompts/shared/guardrails/continuity_rules.md`
- [ ] **1.12** Create `prompts/agents.yaml` with agent registry

### Validation

- [ ] All prompt files load without errors
- [ ] Combined character count matches or exceeds original embedded prompts
- [ ] No hardcoded prompts remain in `foreman.py` (only file references)

---

## Phase 2: PromptAssembler Service

**Goal**: Create the service that assembles the Context Sandwich.

### Deliverables

```
backend/services/prompt_assembler.py   # Main assembler service
backend/services/response_parser.py    # XML response parser
```

### Data Structures

```python
@dataclass
class AssemblyConfig:
    """Configuration for prompt assembly."""
    agent_id: str              # "foreman", "character_coach", etc.
    model_id: str              # "gpt-4o", "claude-sonnet-4-5", etc.
    mode: Optional[str]        # For mode-aware agents: "architect", etc.
    max_kb_entries: int = 10
    max_conversation_turns: int = 10
    include_voice_bundle: bool = True

@dataclass
class AssembledPrompt:
    """Result of prompt assembly."""
    system_prompt: str         # Complete system prompt
    tier: str                  # "full", "medium", "minimal"
    token_estimate: int        # Estimated token count
    included_sections: List[str]  # What was included
```

### Tasks

- [ ] **2.1** Create `backend/services/prompt_assembler.py` with:
  - [ ] `PromptAssembler` class
  - [ ] `_load_prompt(filename)` - load with caching
  - [ ] `_generate_session_state()` - create XML state
  - [ ] `assemble()` - main assembly method
  - [ ] `get_prompt_tier()` - determine tier from model
  - [ ] `assemble_for_tier()` - tier-specific assembly
- [ ] **2.2** Create `backend/services/response_parser.py` with:
  - [ ] `ParsedResponse` dataclass
  - [ ] `parse_agent_response()` - extract XML tags
  - [ ] `parse_action_content()` - parse action parameters
  - [ ] `parse_with_fallback()` - graceful degradation
- [ ] **2.3** Add model capability matrix to `model_capabilities.py`:
  - [ ] `xml_reliability` field per model
  - [ ] `instruction_following` field per model
  - [ ] `tier` field (full/medium/minimal)
- [ ] **2.4** Create unit tests for assembler
- [ ] **2.5** Create unit tests for parser

### Validation

- [ ] Assembler correctly loads all prompt files
- [ ] Session state XML is well-formed
- [ ] Tier-based assembly produces different output sizes
- [ ] Parser correctly extracts `<thinking>`, `<message>`, `<action>` tags
- [ ] Parser handles malformed responses gracefully

---

## Phase 3: Session State Generation

**Goal**: Generate dynamic XML state injected into every prompt.

### Session State Schema

```xml
<session_state>
  <current_agent>foreman</current_agent>
  <current_mode>ARCHITECT</current_mode>
  <completion_pct>45</completion_pct>

  <project>
    <title>The Last Starship</title>
    <protagonist>Elena Vance</protagonist>
    <genre>Sci-Fi Noir</genre>
  </project>

  <active_context>
    <file>Characters/Elena_Vance.md</file>
    <beat>Midpoint (Beat 9/15)</beat>
  </active_context>

  <work_order>
    <template name="Protagonist" status="in_progress" missing="arc_resolution"/>
    <template name="Beat Sheet" status="not_started"/>
    <template name="Theme" status="complete"/>
    <template name="World Rules" status="not_started"/>
  </work_order>

  <voice_context loaded="true">
    <voice_summary>First-person, present tense. Short punchy sentences...</voice_summary>
  </voice_context>

  <knowledge_context>
    <entry category="character" key="elena_fatal_flaw">
      Inability to trust, stemming from father's abandonment
    </entry>
  </knowledge_context>

  <agent_memory>
    <preference>Writer prefers British spellings</preference>
    <correction>Elena lost her gun in Ch3</correction>
  </agent_memory>
</session_state>
```

### Tasks

- [ ] **3.1** Create `SessionStateGenerator` class in `prompt_assembler.py`
- [ ] **3.2** Implement project info extraction
- [ ] **3.3** Implement work order status formatting
- [ ] **3.4** Implement voice bundle injection (summary for small models)
- [ ] **3.5** Implement knowledge context injection from Foreman KB
- [ ] **3.6** Implement agent memory section (preferences, corrections)
- [ ] **3.7** Implement active scaffold injection (for DIRECTOR mode)
- [ ] **3.8** Create mode-specific state variants (omit irrelevant sections)
- [ ] **3.9** Create size-constrained variants (full/medium/minimal)

### Validation

- [ ] State XML validates against schema
- [ ] Mode-specific variants include correct sections
- [ ] Size variants respect token budgets
- [ ] KB entries retrieved via `get_context_for_foreman()`

---

## Phase 4: Agent Registry

**Goal**: Define selectable agents with their capabilities.

### agents.yaml Schema

```yaml
agents:
  foreman:
    name: "The Foreman"
    description: "Your structural editor and creative partner"
    icon: "🏗️"
    has_modes: true
    modes: [architect, voice_calibration, director, editor]
    default_mode: architect
    identity_file: "agents/foreman/identity.md"
    process_map_file: "agents/foreman/process_map.md"
    capabilities:
      - query_notebook
      - save_decision
      - write_template
      - update_status
      - start_tournament
      - generate_scaffold
      - write_scene
      - run_health_check
    recommended_models:
      premium: ["claude-sonnet-4-5", "gpt-4o"]
      balanced: ["claude-sonnet-4-5", "deepseek-chat"]
      budget: ["mistral:7b", "llama3.2:3b"]

  character_coach:
    name: "Character Coach"
    description: "Deep dive into character psychology and development"
    icon: "🎭"
    has_modes: false
    identity_file: "agents/character_coach/identity.md"
    capabilities:
      - query_notebook
      - save_decision
    focus_areas:
      - fatal_flaw
      - character_arc
      - relationships
      - backstory
    recommended_models:
      premium: ["claude-sonnet-4-5"]
      balanced: ["gpt-4o"]

  plot_doctor:
    name: "Plot Doctor"
    description: "Structure, pacing, and beat sheet expertise"
    icon: "📊"
    has_modes: false
    identity_file: "agents/plot_doctor/identity.md"
    capabilities:
      - query_notebook
      - save_decision
      - run_health_check
    focus_areas:
      - beat_sheet
      - pacing
      - tension_curves
      - act_structure

  voice_stylist:
    name: "Voice Stylist"
    description: "Prose quality, voice consistency, and style refinement"
    icon: "✨"
    has_modes: false
    identity_file: "agents/voice_stylist/identity.md"
    capabilities:
      - save_decision
    focus_areas:
      - prose_quality
      - voice_consistency
      - anti_patterns
      - sentence_rhythm

  research_assistant:
    name: "Research Assistant"
    description: "Query your NotebookLM notebooks for research"
    icon: "📚"
    has_modes: false
    identity_file: "agents/research_assistant/identity.md"
    capabilities:
      - query_notebook
    focus_areas:
      - world_building
      - research_synthesis
      - fact_checking
```

### Tasks

- [ ] **4.1** Create `prompts/agents.yaml` with full schema
- [ ] **4.2** Update `backend/agents/registry.py` to load agents.yaml
- [ ] **4.3** Create `AgentConfig` dataclass for runtime agent info
- [ ] **4.4** Create agent identity files:
  - [ ] `prompts/agents/character_coach/identity.md`
  - [ ] `prompts/agents/plot_doctor/identity.md`
  - [ ] `prompts/agents/voice_stylist/identity.md`
  - [ ] `prompts/agents/research_assistant/identity.md`
- [ ] **4.5** Add `/agents/available` endpoint to list selectable agents
- [ ] **4.6** Add `/agents/{agent_id}/info` endpoint for agent details

### Validation

- [ ] All agents load from YAML
- [ ] Agent capabilities map to existing services
- [ ] Identity files exist for all agents
- [ ] API endpoints return correct agent info

---

## Phase 5: Foreman Integration

**Goal**: Update Foreman to use PromptAssembler instead of embedded strings.

### Tasks

- [ ] **5.1** Update `foreman.py` to import `PromptAssembler`
- [ ] **5.2** Replace `_get_system_prompt()` with assembler call
- [ ] **5.3** Update `chat()` method to use assembled prompts
- [ ] **5.4** Update `_query_openai()` to use assembled system prompt
- [ ] **5.5** Add response parsing via `ResponseParser`
- [ ] **5.6** Implement action execution from parsed actions
- [ ] **5.7** Remove embedded `ARCHITECT_SYSTEM_PROMPT`, etc. constants
- [ ] **5.8** Add agent selection support (default to "foreman")
- [ ] **5.9** Update `/foreman/chat` endpoint to accept `agent_id` parameter

### Validation

- [ ] Foreman chat works with assembled prompts
- [ ] Mode switching still works
- [ ] Actions execute correctly from XML responses
- [ ] Graceful fallback for malformed responses
- [ ] No regression in existing functionality

---

## Phase 6: Frontend - Agent Selector

**Goal**: Allow writers to select different agents in the chat interface.

### UI Design

```
┌─────────────────────────────────────────┐
│ FOREMAN PANEL                           │
├─────────────────────────────────────────┤
│ [Agent Selector Dropdown]               │
│  ┌─────────────────────────────┐        │
│  │ 🏗️ The Foreman         ✓   │        │
│  │ 🎭 Character Coach          │        │
│  │ 📊 Plot Doctor              │        │
│  │ ✨ Voice Stylist            │        │
│  │ 📚 Research Assistant       │        │
│  └─────────────────────────────┘        │
├─────────────────────────────────────────┤
│ [Chat Messages...]                      │
│                                         │
├─────────────────────────────────────────┤
│ [Input] [Send]                          │
└─────────────────────────────────────────┘
```

### Tasks

- [ ] **6.1** Add `selectedAgent` store to `stores.js`
- [ ] **6.2** Create `AgentSelector.svelte` component
- [ ] **6.3** Integrate selector into `ChatSidebar.svelte` or `ForemanPanel`
- [ ] **6.4** Update chat submission to include `agent_id`
- [ ] **6.5** Show current agent in StatusBar (alongside mode)
- [ ] **6.6** Persist agent selection in session
- [ ] **6.7** Style agent selector with agent icons and descriptions
- [ ] **6.8** Add keyboard shortcut for agent switching (Cmd+1-5)

### Validation

- [ ] Agent selector shows all available agents
- [ ] Selecting agent changes chat behavior
- [ ] Current agent visible in UI
- [ ] Agent selection persists across page refresh

---

## Phase 7: Action System

**Goal**: Connect parsed XML actions to backend services.

### Action → Service Mapping

| Action Type | Service | Method |
|-------------|---------|--------|
| `query_notebook` | `notebooklm_service` | `query_notebook()` |
| `save_decision` | `foreman_kb_service` | `save_decision()` |
| `write_template` | `story_bible_service` | `write_template()` |
| `update_status` | `foreman.work_order` | Direct update |
| `start_tournament` | `voice_calibration_service` | `start_tournament()` |
| `select_winner` | `voice_calibration_service` | `select_winner()` |
| `generate_bundle` | `voice_calibration_service` | `generate_bundle()` |
| `generate_scaffold` | `scaffold_generator_service` | `generate_scaffold()` |
| `write_scene` | `scene_writer_service` | `generate_variants()` |
| `analyze_scene` | `scene_analyzer_service` | `analyze_scene()` |
| `enhance_scene` | `scene_enhancement_service` | `enhance()` |
| `run_health_check` | `graph_health_service` | `run_check()` |

### Tasks

- [ ] **7.1** Create `backend/services/action_executor.py`
- [ ] **7.2** Implement `ActionExecutor` class with handler registry
- [ ] **7.3** Implement handlers for each action type
- [ ] **7.4** Add action validation (check agent has capability)
- [ ] **7.5** Add action result formatting
- [ ] **7.6** Integrate executor with Foreman chat flow
- [ ] **7.7** Add action logging for debugging

### Validation

- [ ] All action types execute correctly
- [ ] Invalid actions logged and skipped
- [ ] Action results returned to frontend
- [ ] Agent capability checks enforced

---

## Phase 8: Testing & Polish

**Goal**: Comprehensive testing across all models and agents.

### Tasks

- [ ] **8.1** Test with GPT-4o (full tier)
- [ ] **8.2** Test with Claude Sonnet 4.5 (full tier)
- [ ] **8.3** Test with Gemini 2.0 Flash (full tier, XML reinforcement)
- [ ] **8.4** Test with DeepSeek (medium tier)
- [ ] **8.5** Test with Mistral 7B local (medium tier)
- [ ] **8.6** Test with Llama 3.2:3b local (minimal tier)
- [ ] **8.7** Test agent switching mid-conversation
- [ ] **8.8** Test mode transitions with new system
- [ ] **8.9** Verify XML parsing across all models
- [ ] **8.10** Performance testing (prompt assembly time)
- [ ] **8.11** Update documentation

### Validation

- [ ] All models produce parseable responses
- [ ] Graceful degradation for minimal tier
- [ ] No regression in Foreman functionality
- [ ] Agent switching works smoothly
- [ ] Documentation updated

---

## Dependencies

### Existing Services (Already Built)

- `foreman_kb_service.py` - KB storage and retrieval
- `story_bible_service.py` - Template management
- `voice_calibration_service.py` - Tournament and voice bundle
- `scene_writer_service.py` - Scene generation
- `scene_analyzer_service.py` - Scene analysis
- `scaffold_generator_service.py` - Scaffold creation
- `graph_health_service.py` - Health checks
- `notebooklm_service.py` - NotebookLM queries
- `model_capabilities.py` - Model info (needs extension)
- `context_assembler.py` - GraphRAG context (can integrate)

### New Services (To Build)

- `prompt_assembler.py` - Context Sandwich assembly
- `response_parser.py` - XML response parsing
- `action_executor.py` - Action dispatch

---

## Token Budget Reference

| Component | Full Tier | Medium Tier | Minimal Tier |
|-----------|-----------|-------------|--------------|
| Identity | 500 | 500 | 200 |
| Process Map | 1000 | 400 | 0 |
| Mode Rules | 800 | 600 | 300 |
| Session State | 800 | 400 | 150 |
| Protocols | 800 | 600 | 200 |
| **Subtotal** | **3900** | **2500** | **850** |
| Conversation | 4000 | 2000 | 500 |
| User Message | 500 | 500 | 500 |
| **Total Input** | **8400** | **5000** | **1850** |
| Response Reserve | 4000 | 2000 | 1000 |
| **Total Budget** | **12400** | **7000** | **2850** |

---

## Success Criteria

1. **Maintainability**: Prompts in `.md` files, not Python strings
2. **Multi-Agent**: Writers can select from 5+ agents mid-chat
3. **Model Agnostic**: Same behavior across GPT-4o, Claude, Gemini, local models
4. **Reliable Parsing**: XML output parsed deterministically
5. **Graceful Degradation**: Small models get trimmed prompts, not failures
6. **Process Awareness**: Agents always know mode, artifacts, available actions

---

## Notes

- The Foreman remains the primary agent with mode-awareness
- Specialist agents (Character Coach, etc.) are simpler - no modes
- All agents share the same output protocols (XML format)
- All agents have access to project context (KB, Graph, Voice Bundle)
- Agent capabilities determine which actions are available
- This replaces the removed "Squad" system with a simpler, user-selectable model

---

*Created: December 2025*
*Last Updated: December 2025*
