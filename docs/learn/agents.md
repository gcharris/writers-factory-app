---
layout: default
title: Agent Instructions

---


# Agent Instruction System: The Brain of Writers Factory

> **"It's not what the AI knows. It's who it thinks it is."**

The most sophisticated AI model in the world is useless if it doesn't understand its role. The Agent Instruction System is how we transform a generic language model into a specialized creative writing partner.

---

## The Problem We Solved

### The Identity Crisis

When you chat with an AI, you're talking to a blank slate. It doesn't know:
- Who it is (a structural editor? a prose stylist? a research assistant?)
- What phase you're in (worldbuilding? drafting? polishing?)
- What it's allowed to do (query notebooks? write scenes? run tournaments?)
- What voice to use (professional? casual? craft-focused?)

Every message requires you to re-explain the context. It's like having a new employee who forgets their job description every morning.

### The Payload Problem

Even worse, different AI models have different capabilities:
- **Claude Opus 4.5** can handle 200K tokens of context and follows complex instructions perfectly
- **Mistral 7B** running locally has 32K tokens and needs simpler prompts
- **Llama 3.2:3b** has minimal context and struggles with XML formatting

One-size-fits-all prompts fail. You need prompts that adapt to the model.

---

## The Solution: Context Sandwich Architecture

We created a layered prompt assembly system that builds the perfect context for every message. Think of it as a sandwich:

```
┌─────────────────────────────────────────┐
│  1. IDENTITY LAYER                      │  ← "Who am I?"
│     Agent persona, core philosophy      │
├─────────────────────────────────────────┤
│  2. PROCESS MAP                         │  ← "Where are we?"
│     Current mode, available modes       │
├─────────────────────────────────────────┤
│  3. MODE-SPECIFIC RULES                 │  ← "What do I do here?"
│     ARCHITECT / VOICE / DIRECTOR / EDITOR│
├─────────────────────────────────────────┤
│  4. SESSION STATE                       │  ← "What's happening now?"
│     Project, work order, KB entries     │
├─────────────────────────────────────────┤
│  5. PROTOCOLS                           │  ← "How do I respond?"
│     XML output format, action syntax    │
├─────────────────────────────────────────┤
│  6. CONVERSATION HISTORY                │  ← "What did we discuss?"
│     Recent messages for continuity      │
├─────────────────────────────────────────┤
│  7. USER MESSAGE                        │  ← "What are you asking?"
│     The writer's current request        │
└─────────────────────────────────────────┘
```

This isn't just organization. It's **engineering**. Each layer serves a purpose, and the system assembles them dynamically based on:
- Which **agent** is selected
- Which **mode** is active
- Which **model** is being used
- How much **context space** is available

---

## Meet The Agents

Writers Factory isn't one AI - it's a **team** of specialists. Writers can switch between them mid-conversation, just like consulting different experts.

### The Foreman (Mode-Aware)

```
🏗️ "Your structural editor and creative partner through all phases"
```

The Foreman is the primary agent. Unlike specialists, it has **four distinct modes**:

| Mode | Phase | Focus |
|------|-------|-------|
| **ARCHITECT** | Conception | Build Story Bible, challenge structure |
| **VOICE** | Voice Calibration | Run tournaments, establish style |
| **DIRECTOR** | Execution | Draft scenes, manage beat progression |
| **EDITOR** | Polish | Check consistency, refine prose |

The Foreman doesn't just chat - it **acts**. It can:
- Query NotebookLM for research
- Save decisions to the Knowledge Base
- Write templates to the Story Bible
- Start voice tournaments
- Generate scene scaffolds
- Run health checks on the manuscript

### Character Coach 🎭

```
"Deep dive into character psychology, motivation, and arc"
```

When you need to explore a character's fatal flaw, understand their backstory, or work out relationship dynamics, switch to the Character Coach. They speak in the language of character craft:

- Fatal flaw and "the lie"
- Character arc (wound → want → need → transformation)
- Relationship dynamics
- Voice authenticity

*Capabilities: query_notebook, save_decision*

### Plot Doctor 📊

```
"Structure, pacing, beat sheet, and story mechanics"
```

The Plot Doctor thinks in terms of structure. They'll analyze your beat sheet, identify pacing issues, and ensure your turning points land. They can even run health checks on your plot:

- Beat sheet analysis
- Tension curve mapping
- Act structure
- Promise/payoff tracking

*Capabilities: query_notebook, save_decision, run_health_check*

### Voice Stylist ✨

```
"Prose quality, voice consistency, and style refinement"
```

The Voice Stylist obsesses over how words sound on the page. They catch anti-patterns, analyze sentence rhythm, and ensure your voice stays consistent:

- Sentence rhythm analysis
- Anti-pattern detection (clichés, filter words)
- Voice consistency checking
- POV discipline

*Capabilities: save_decision*

### Research Assistant 📚

```
"Query your NotebookLM notebooks for research"
```

When you need information from your research notebooks - historical details, technical facts, character interview transcripts - the Research Assistant retrieves and synthesizes it:

- Notebook queries
- Research synthesis
- Fact-checking
- Source attribution

*Capabilities: query_notebook*

---

## The XML Protocol

Every agent speaks the same language - a structured XML format that separates thinking from communication from action:

```xml
<thinking>
Let me analyze the writer's request. They're asking about
their protagonist's motivation, but I notice the fatal flaw
hasn't been established yet. I should address this gap.
</thinking>

<message>
Before we dive into Marcus's motivation, I notice we haven't
established his fatal flaw. In Save the Cat! terms, this is
the internal obstacle that will challenge him throughout the
story. What wounds him? What lie does he believe about himself?
</message>

<action type="save_decision">
  <category>character</category>
  <key>marcus_motivation_gap</key>
  <value>Needs fatal flaw before motivation can be grounded</value>
</action>
```

This structure enables:
- **Transparency**: Writers can see the agent's reasoning (thinking)
- **Clean output**: The message is the user-facing response
- **Automation**: Actions execute automatically (save to KB, query notebooks, etc.)

### Why XML? Why Not JSON?

We tested both. Findings:
- Claude models follow XML format with 100% reliability
- GPT-4o handles XML at 90%+ reliability
- JSON tends to break with nested content and prose
- XML tags are visually distinct from prose, reducing confusion

For models that struggle with XML (like Gemini, which prefers JSON), we add extra reinforcement in the prompt.

---

## Tier-Based Assembly

Not all models are created equal. We adapt prompts based on capability:

### Full Tier (Claude, GPT-4o, Gemini)
- **128K+ context window**
- Complete 7-layer sandwich
- All guardrails and protocols
- Full voice bundle injection
- Up to 15 KB entries

### Medium Tier (DeepSeek, Mistral 7B)
- **32K-128K context window**
- Summarized process map
- Core protocols only
- Condensed voice bundle
- Up to 8 KB entries

### Minimal Tier (Llama 3.2:3b)
- **<32K context window**
- Identity and mode only (no process map)
- Compressed identity
- Minimal protocols
- Up to 3 KB entries

The assembly happens automatically based on the `prompt_tier` field in our model capability matrix.

---

## Soft Guardrails: Advise, Don't Block

Traditional software uses **hard guardrails**: "You can't do that." We use **soft guardrails**: "You probably shouldn't do that, but you're the writer."

For example, when a writer tries to enter Director Mode before completing their Story Bible:

```xml
<message>
I notice we're trying to jump into scene drafting, but your Story
Bible isn't complete yet. You're missing:

- Protagonist: arc_resolution not defined
- Beat Sheet: not started

I'd recommend we nail down Marcus's transformation before we start
writing scenes. That way, every scene can push him toward that arc.

But you're the writer. If you want to discovery-draft and come back
to structure later, I can support that approach too.

What would you prefer?
</message>
```

This respects writer autonomy while providing craft-aware guidance.

---

## The Implementation

### File Structure

```
backend/prompts/
├── agents.yaml                    # Agent registry
├── shared/
│   ├── project_context.md        # What is Writers Factory?
│   ├── protocols.md              # XML output format
│   └── guardrails/
│       ├── voice_antipatterns.md # Zero-tolerance patterns
│       └── continuity_rules.md   # Consistency checking
└── agents/
    ├── foreman/
    │   ├── identity.md           # Core Foreman persona
    │   ├── process_map.md        # Mode overview
    │   └── modes/
    │       ├── architect.md
    │       ├── voice_calibration.md
    │       ├── director.md
    │       └── editor.md
    ├── character_coach/
    │   └── identity.md
    ├── plot_doctor/
    │   └── identity.md
    ├── voice_stylist/
    │   └── identity.md
    └── research_assistant/
        └── identity.md
```

### The Assembler

The `PromptAssembler` service reads these files and dynamically constructs prompts:

```python
config = AssemblyConfig(
    agent_id="foreman",
    model_id="claude-sonnet-4-5",
    mode="architect",
    max_kb_entries=15,
    include_voice_bundle=False,
    include_guardrails=True,
)

result = assembler.assemble(
    config=config,
    work_order=current_work_order,
    kb_entries=recent_decisions,
)

# result.system_prompt → Complete 7-layer sandwich
# result.tier → "full"
# result.token_estimate → ~12,000 tokens
# result.included_sections → ["identity", "process_map", "mode", ...]
```

### The Parser

The `ResponseParser` extracts structured data from agent responses:

```python
parsed = parse_agent_response(llm_output)

# parsed.thinking → Agent's internal reasoning
# parsed.message → User-facing response
# parsed.actions → List of actions to execute
# parsed.content_updates → File changes to apply
```

---

## What We Learned

### 1. Identity Beats Instructions

We tried giving the AI detailed instructions for every scenario. It didn't work. What worked was giving the AI a **rich identity** and letting it figure out the instructions.

The Character Coach doesn't need a list of "what to say when asked about backstory." It needs to *be* a character expert who naturally thinks in terms of wounds, wants, and needs.

### 2. Separation of Concerns

Mixing "who am I" with "what do I do" with "how do I respond" creates confused agents. The layered sandwich keeps each concern isolated and composable.

### 3. Graceful Degradation

Not every model can handle complex prompts. Rather than failing, we degrade gracefully:
- Full tier gets everything
- Medium tier gets the essentials
- Minimal tier gets just enough to function

Embedded fallback prompts ensure the system works even if the file-based prompts can't load.

### 4. Actions as First-Class Citizens

Early versions had agents describe what they wanted to do. Now they *do* it:

```xml
<!-- Old: Described action -->
<message>I'll save this decision about Marcus's flaw to our KB.</message>

<!-- New: Executes action -->
<action type="save_decision">
  <category>character</category>
  <key>marcus_fatal_flaw</key>
  <value>Inability to trust, stemming from father's abandonment</value>
</action>
```

The frontend sees the action results, not just the intent.

---

## The Result

Writers now have a team of AI specialists, each with:
- A distinct **identity** (who they are)
- Defined **capabilities** (what they can do)
- Appropriate **guardrails** (what they shouldn't do)
- Consistent **communication** (XML format)
- Adaptive **complexity** (tier-based assembly)

And the writer can switch between them with a dropdown, mid-conversation, without losing context.

> **"The AI isn't just a tool anymore. It's a collaborator with a job description."**

---

## For Developers

Want to add a new agent? Here's the pattern:

1. **Create identity file**: `backend/prompts/agents/new_agent/identity.md`
2. **Register in YAML**: Add to `backend/prompts/agents.yaml` with capabilities and focus areas
3. **The system handles the rest**: Assembly, parsing, and action execution work automatically

The Agent Instruction System is the **nervous system** of Writers Factory - invisible when it works, essential to everything.

---

*Next: [GraphRAG: The Living Brain](graphrag.md) | [Voice Calibration](voice_calibration.md) | [Director Mode](director_mode.md)*
