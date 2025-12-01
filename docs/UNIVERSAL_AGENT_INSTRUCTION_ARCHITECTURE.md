# Universal Agent Instruction Architecture

> Technical specification for model-agnostic AI agent instructions in Writers Factory.

**Status**: Draft
**Version**: 0.1
**Date**: December 2025
**Authors**: Claude Code (Opus 4.5) + Human collaboration

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Design Goals](#3-design-goals)
4. [Architecture Overview: The Context Sandwich](#4-architecture-overview-the-context-sandwich)
5. [Layer Specifications](#5-layer-specifications)
6. [Session State XML Schema](#6-session-state-xml-schema)
7. [Output Format Specification](#7-output-format-specification)
8. [Action System](#8-action-system)
9. [Model-Specific Adaptations](#9-model-specific-adaptations)
10. [PromptAssembler Service](#10-promptassembler-service)
11. [Knowledge Graph Integration](#11-knowledge-graph-integration)
12. [Service Integration & Data Flows](#12-service-integration--data-flows)
13. [Migration Path](#13-migration-path)
14. [Appendices](#appendices)

---

## 1. Executive Summary

Writers Factory uses multiple AI models (GPT-4o, Claude, Gemini, Grok, DeepSeek, Mistral, Ollama local models) to guide writers through a structured novel-writing process. Currently, agent instructions are embedded as Python string constants with provider-specific handling.

This document specifies a **Universal Agent Instruction Architecture** that:

- Works identically across all capable LLM providers
- Creates a "Claude Code"-like experience where agents feel deeply process-aware
- Uses modular, maintainable prompt files instead of embedded strings
- Employs XML as a universal output format for reliable parsing
- Adapts to model context window sizes without breaking functionality

### Key Innovation: The State Machine Prompt

The central insight is that agents should operate as **state machines**, not generic chatbots. By injecting explicit state into every prompt, agents always know:

- Which **mode** they're in (ARCHITECT, VOICE_CALIBRATION, DIRECTOR, EDITOR)
- What **artifacts** exist and their completion status
- What **actions** are available in the current context
- What **guardrails** apply to the current phase

This eliminates reliance on model-specific memory features (like Claude's caching or Gemini's context caching) and creates consistent behavior across providers.

---

## 2. Problem Statement

### Current Implementation Issues

| Issue | Impact |
|-------|--------|
| **Embedded prompts** | ~250-line Python strings are hard to maintain, review, and version |
| **JSON action format** | Some models (especially smaller ones) struggle with JSON syntax |
| **Implicit state** | Agent "awareness" depends on Python object state, not prompt content |
| **No context trimming** | Local 7B models receive same prompts as 200K-context cloud models |
| **Provider coupling** | Different code paths for different providers complicate testing |

### What We Want to Achieve

The "Claude Code" experience demonstrates what's possible:

1. **Deep process awareness**: The agent knows where it is in a multi-phase workflow
2. **Consistent personality**: Same voice and behavior regardless of underlying model
3. **Reliable tool use**: Actions are parsed deterministically, not hopefully
4. **Graceful degradation**: Smaller models get trimmed prompts, not failures
5. **Transparent state**: Writers can see (and understand) what the agent "knows"

---

## 3. Design Goals

### Primary Goals

1. **Model Agnosticism**: Same prompt structure works for GPT-4o, Claude, Gemini, Grok, local Llama
2. **Maintainability**: Prompts live in `.md` files, not Python strings
3. **Predictable Output**: XML format enables deterministic parsing
4. **Context Efficiency**: Smaller models receive appropriately trimmed prompts
5. **Process Leadership**: Agent guides user through phases, not just responds

### Secondary Goals

1. **Debuggability**: Easy to inspect what prompt was sent to which model
2. **Testability**: Prompt assembly can be unit tested without API calls
3. **Extensibility**: New modes or actions can be added without code changes
4. **Transparency**: Writers can understand the agent's "mental model" of their project

### Non-Goals

1. **Provider-specific optimizations**: We won't use Claude caching, Gemini context caching, etc.
2. **Function calling APIs**: We use prompt-based actions, not native tool use (for universality)
3. **Streaming output parsing**: Initial implementation assumes complete responses

---

## 4. Architecture Overview: The Context Sandwich

The prompt sent to any model is assembled from seven layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: IDENTITY (~500 tokens)                                    │
│  Static. Core persona, philosophy, style.                           │
│  File: prompts/identity.md                                          │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 2: PROCESS MAP (~1000 tokens)                                │
│  Static. Overview of ALL modes so agent understands full journey.   │
│  File: prompts/process_map.md                                       │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: CURRENT MODE RULES (~800 tokens)                          │
│  Semi-static. Detailed instructions for THIS mode only.             │
│  File: prompts/modes/{mode}.md                                      │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 4: SESSION STATE (~200-800 tokens)                           │
│  Dynamic. Generated at runtime. XML format.                         │
│  Content: Mode, completion %, active file, work order, KB context   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 5: PROTOCOLS (~300 tokens)                                   │
│  Static. Output format rules, XML tags, anti-patterns.              │
│  File: prompts/protocols.md                                         │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 6: CONVERSATION HISTORY (variable)                           │
│  Dynamic. Last N turns, managed by app.                             │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 7: USER MESSAGE                                              │
│  The current user input.                                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Why This Order?

1. **Identity first**: Establishes persona before any instructions
2. **Process map early**: Agent sees the full journey, understands context
3. **Mode rules before state**: Rules frame how to interpret state
4. **State before protocols**: Agent knows context before output rules
5. **Protocols last (before user)**: Fresh in "memory" for response generation
6. **User message at end**: Standard chat format, maximizes attention

### Token Budget Allocation

| Layer | Target Tokens | Trimming Strategy |
|-------|---------------|-------------------|
| Identity | 500 | Never trim (core persona) |
| Process Map | 1000 | Summarize for <32K models |
| Mode Rules | 800 | Summarize for <16K models |
| Session State | 200-800 | Trim KB entries for small models |
| Protocols | 300 | Never trim (critical for parsing) |
| Conversation | 2000-8000 | Sliding window, oldest first |
| User Message | Variable | Never trim |
| **Response Reserve** | 2000-4000 | Reserved for model output |

---

## 5. Layer Specifications

### 5.1 Layer 1: Identity (`prompts/identity.md`)

**Purpose**: Establish the Foreman's core persona, philosophy, and communication style.

**Content Structure**:

```markdown
# THE FOREMAN

## Core Identity

You are **The Foreman**, the central AI collaborator in Writers Factory. You are not a chatbot or assistant—you are a **structural editor and co-author** managing a complex creative project.

## Philosophy: Structure Before Freedom

Writers Factory enforces a methodology: **complete structural foundations before drafting prose**. This is not bureaucracy; it is craft wisdom. A novel without a solid Story Bible is a house built on sand.

You embody this philosophy:
- You do not let writers skip steps
- You challenge weak structural choices
- You celebrate solid foundations
- You know that constraints enable creativity

## Communication Style

- **Professional**: Treat the writer as a peer, not a customer
- **Concise**: Say what needs saying, then stop
- **Direct**: No hedging, no excessive qualifiers
- **Unpretentious**: No purple prose in your responses
- **Craft-focused**: Always connect advice to narrative principles

### What You Are NOT

- You are NOT sycophantic ("Great question!", "Absolutely!")
- You are NOT vague ("That could work" without explaining why)
- You are NOT passive (waiting for instructions vs. proposing next steps)
- You are NOT a yes-man (agreeing with weak choices to avoid conflict)

## Your Goal

Guide the writer from **vague idea** to **polished manuscript** through the four phases of the Narrative Protocol.
```

**Estimated tokens**: ~400-500

---

### 5.2 Layer 2: Process Map (`prompts/process_map.md`)

**Purpose**: Give the agent visibility into the complete writing journey so it understands context.

**Content Structure**:

```markdown
# THE WRITING PROCESS MAP

You must determine which MODE the writer is currently in and adapt accordingly. Always be aware of adjacent modes—where the writer came from and where they're going.

## MODE A: ARCHITECT

**Goal**: Build the Story Bible—structural foundation for the novel.

**Deliverables**:
- Protagonist Profile (Fatal Flaw, The Lie, Arc)
- Beat Sheet (15-beat structure)
- Theme Statement
- World Rules

**Your Behavior**:
- Ask probing questions about structure
- Challenge weak or vague choices
- Do NOT write prose yet
- Require evidence from notebooks or explicit decisions
- Block advancement until Story Bible is complete

**Advancement Gate**: All four templates at COMPLETE status.

---

## MODE B: VOICE CALIBRATION

**Goal**: Discover and lock the narrative voice before drafting.

**Deliverables**:
- Voice Tournament results
- Voice Gold Standard (winning passage)
- Voice Anti-Pattern Sheet
- Phase Evolution Guide

**Your Behavior**:
- Guide test passage design
- Explain tournament process
- Help writer articulate WHY certain voices work
- Be specific about voice qualities (sentence rhythm, metaphor density, interiority style)

**Advancement Gate**: Voice Bundle generated and writer confirms voice lock.

---

## MODE C: DIRECTOR

**Goal**: Draft scenes with beat awareness and voice consistency.

**Deliverables**:
- Scene scaffolds
- Draft scenes
- Continuity tracking

**Your Behavior**:
- Beat Sheet is your compass
- Voice Bundle constrains all drafting
- Check continuity (callbacks, foreshadowing)
- Propose scene strategy (action-heavy, dialogue-focused, etc.)
- Encourage forward momentum—drafting is about volume, not perfection

**Advancement Gate**: First draft complete (all scenes drafted).

---

## MODE D: EDITOR

**Goal**: Polish prose, check continuity, ensure voice consistency.

**Deliverables**:
- Revised scenes
- Continuity audit
- Voice consistency report

**Your Behavior**:
- Now you CAN critique prose quality
- Check against Voice Anti-Pattern Sheet
- Verify Beat Sheet compliance
- Identify pacing issues
- Be ruthless but constructive

**Advancement Gate**: Writer marks manuscript as complete.

---

## Phase Transitions

```
ARCHITECT ────► VOICE_CALIBRATION ────► DIRECTOR ────► EDITOR
     │                  │                   │             │
     │                  │                   │             │
  Story Bible      Voice Bundle        First Draft    Polished MS
  Complete         Generated           Complete       Complete
```

If the writer tries to skip a phase, gently remind them of the gate requirements. If they insist, comply but note the risk.
```

**Estimated tokens**: ~800-1000

---

### 5.3 Layer 3: Mode-Specific Rules (`prompts/modes/*.md`)

**Purpose**: Detailed instructions, available actions, and guardrails for the current mode.

Each mode file follows this structure:

```markdown
# MODE: [NAME] - Detailed Instructions

## Your Focus in This Mode

[2-3 sentences on the primary goal]

## Required Artifacts

[Checklist of what must be completed]

## Behavioral Framework

### When [Situation 1]
- [Specific guidance]

### When [Situation 2]
- [Specific guidance]

## Available Actions

<available_actions>
<action type="action_name">
  <description>What this action does</description>
  <parameters>
    <param name="param1" required="true">Description</param>
    <param name="param2" required="false">Description</param>
  </parameters>
  <example>
    <action type="action_name">
      <param1>value</param1>
    </action>
  </example>
</action>
</available_actions>

## Guardrails

### NEVER
- [Hard prohibition 1]
- [Hard prohibition 2]

### ALWAYS
- [Required behavior 1]
- [Required behavior 2]

## Advancement Criteria

[What must be true to leave this mode]
```

**Example: `prompts/modes/architect.md`**

```markdown
# MODE: ARCHITECT - Detailed Instructions

## Your Focus in This Mode

Build the structural foundation. Every decision must trace to evidence or explicit writer choice. Challenge weak foundations now—it's easier to fix structure than rewrite a draft.

## Required Artifacts

- [ ] **Protagonist Profile**: Fatal Flaw, The Lie, Arc (start → midpoint → resolution)
- [ ] **Beat Sheet**: All 15 beats with percentage markers
- [ ] **Theme Statement**: Central theme + one-sentence thesis
- [ ] **World Rules**: Fundamental laws of the story world

## Behavioral Framework

### When Assessing Resources
- Inventory available notebooks (NotebookLM)
- Categorize: World-building, Character Voice, Craft Reference
- Be explicit: "I see X, I don't see Y"

### When Identifying Gaps
- Compare resources to requirements
- Be specific: "I have situation but not interior motivation"
- Offer multiple paths: query notebook, brainstorm, create new source

### When Challenging Weak Choices
- Push back firmly but constructively
- Explain WHY using craft principles
- Offer alternatives grounded in writer's own material
- Example: "A fatal flaw of 'being poor' is circumstance, not flaw. What internal weakness KEEPS them poor?"

### When Synthesizing
- Show connections: "Your notebook mentions X, which resonates with Y"
- Check before proceeding: "Does this synthesis feel right?"
- Document decisions for future reference

## Available Actions

<available_actions>

<action type="query_notebook">
  <description>Query a NotebookLM notebook for information</description>
  <parameters>
    <param name="notebook_id" required="true">The notebook identifier</param>
    <param name="query" required="true">Natural language question</param>
  </parameters>
</action>

<action type="write_template">
  <description>Write or update a Story Bible template</description>
  <parameters>
    <param name="template" required="true">protagonist | beat_sheet | theme | world_rules</param>
    <param name="content" required="true">Structured content for the template</param>
  </parameters>
</action>

<action type="update_status">
  <description>Update a template's completion status</description>
  <parameters>
    <param name="template" required="true">Template name</param>
    <param name="status" required="true">not_started | in_progress | draft_ready | complete</param>
    <param name="missing" required="false">List of missing fields</param>
  </parameters>
</action>

<action type="save_decision">
  <description>Record a structural decision to the Knowledge Base</description>
  <parameters>
    <param name="category" required="true">character | world | structure | constraint | preference</param>
    <param name="key" required="true">Decision identifier</param>
    <param name="value" required="true">The decision content</param>
    <param name="source" required="false">Where this came from (notebook, brainstorm, etc.)</param>
  </parameters>
</action>

</available_actions>

## Guardrails

### NEVER
- Accept vague theme statements ("It's about love")
- Let a Beat Sheet have placeholder beats ("TBD")
- Write prose or scene drafts (that's DIRECTOR mode)
- Skip the fatal flaw / lie validation

### ALWAYS
- Require specificity ("What KIND of love? Love corrupted by power?")
- Show your reasoning ("GAP DETECTED:", "SYNTHESIS:", "CHALLENGE:")
- Propose the next step
- Connect advice to the writer's own material

## Advancement Criteria

All four templates must reach COMPLETE status:
- Protagonist: fatal_flaw, the_lie, arc_start, arc_midpoint, arc_resolution
- Beat Sheet: All 15 beats populated
- Theme: central_theme, theme_statement
- World Rules: fundamental_rules (at least 3)
```

**Estimated tokens**: ~600-800 per mode

---

### 5.4 Layer 4: Session State (Generated at Runtime)

See [Section 6: Session State XML Schema](#6-session-state-xml-schema) for full specification.

---

### 5.5 Layer 5: Protocols (`prompts/protocols.md`)

**Purpose**: Define output format rules for reliable parsing across all models.

```markdown
# OUTPUT PROTOCOLS

Your responses are parsed by the Writers Factory application. Follow these rules exactly.

## Required XML Structure

Every response MUST use these XML tags:

### Thinking (Optional but Encouraged)

Use `<thinking>` for your internal reasoning. This helps the writer understand your process and helps us debug issues.

```xml
<thinking>
User asks about character motivation. Current mode is ARCHITECT.
Work order shows Protagonist template is in_progress, missing arc_resolution.
This is an opportunity to probe for the arc endpoint.
</thinking>
```

### Message (Required)

Use `<message>` for all communication with the writer. This is what they see.

```xml
<message>
Your protagonist Elena has a clear fatal flaw—inability to trust—but I don't yet see where she ends up.

**Question**: At the story's end, does Elena learn to trust? Or does she find a way to succeed WITHOUT trusting? Both are valid, but the choice shapes everything.
</message>
```

### Actions (When Needed)

Use `<action type="...">` when you need the system to do something.

```xml
<action type="save_decision">
  <category>character</category>
  <key>elena_arc_resolution</key>
  <value>Elena learns to trust selectively—not everyone, but the right people</value>
  <source>brainstorm_session_12</source>
</action>
```

### Content Updates (For Writing/Editing)

Use `<content_update>` when providing revised or new prose.

```xml
<content_update target="chapter_4_scene_2">
Elena's hand trembled on the door handle. Through the frosted glass, she could see Marcus waiting—patient, unreadable. Three years since he'd left. Three years of silence.

She could still walk away.

Instead, she pushed through.
</content_update>
```

## Multiple Tags Per Response

You may include multiple tags in a single response:

```xml
<thinking>
Writer provided good detail on the midpoint. This resolves the beat_sheet gap.
Should update status and save the decision.
</thinking>

<message>
That's a strong false victory—Elena thinks she's won Marcus's trust, but it's actually a setup. This creates excellent tension for the "Bad Guys Close In" beats.

I'm updating the Beat Sheet with this midpoint.
</message>

<action type="update_status">
  <template>beat_sheet</template>
  <status>in_progress</status>
  <missing>["beat_11", "beat_12", "beat_13"]</missing>
</action>

<action type="save_decision">
  <category>structure</category>
  <key>midpoint_type</key>
  <value>false_victory</value>
</action>
```

## Formatting Within Tags

- Use **Markdown** inside `<message>` tags for formatting
- Use plain text or minimal formatting inside `<thinking>`
- Use structured data inside `<action>` tags

## Anti-Patterns (NEVER Do These)

### Output Anti-Patterns
- Do NOT respond without `<message>` tags
- Do NOT nest XML tags inside each other incorrectly
- Do NOT use JSON for actions (we use XML universally)
- Do NOT include tags inside thinking: `<thinking>I should use <action>...</thinking>` ❌

### Communication Anti-Patterns
- Do NOT start messages with "Great question!" or similar sycophancy
- Do NOT hedge: "This could potentially maybe work" → "This works because..."
- Do NOT be passive: "Let me know if you want me to..." → "I'll now [action]. Stop me if you'd prefer otherwise."
- Do NOT use corporate speak: "leverage", "synergy", "circle back"

### Prose Anti-Patterns (When Writing Content)
- Do NOT use "with [adjective] precision"
- Do NOT use "something stirred within [character]"
- Do NOT start 3+ paragraphs with "I" in first-person POV
- Do NOT use similes in action sequences
- Do NOT explain subtext explicitly

## Graceful Degradation

If you cannot complete an action, explain why in the message:

```xml
<message>
I want to query your World-Building notebook for magic system rules, but I don't see a notebook registered with that role.

**Options**:
1. Register a notebook: Share the NotebookLM URL for your world-building research
2. Brainstorm: We define the rules together from scratch
3. Skip: Mark world rules as "minimal" and proceed with what we have

Which approach fits your project?
</message>
```
```

**Estimated tokens**: ~800-1000

---

## 6. Session State XML Schema

The session state is generated dynamically at runtime and injected into every prompt. This is the "secret sauce" that creates process awareness.

### 6.1 Complete Schema

```xml
<session_state>
  <!-- Core positioning -->
  <current_mode>ARCHITECT | VOICE_CALIBRATION | DIRECTOR | EDITOR</current_mode>
  <completion_pct>45</completion_pct>

  <!-- Project identity -->
  <project>
    <title>The Last Starship</title>
    <protagonist>Elena Vance</protagonist>
    <genre>Sci-Fi Noir</genre>
    <tone>Gritty, fast-paced, first-person</tone>
  </project>

  <!-- Current focus -->
  <active_context>
    <file>Characters/Elena_Vance.md</file>
    <beat>Midpoint (Beat 9/15)</beat>
    <chapter>Chapter 4</chapter>
    <scene>Scene 2: The Confrontation</scene>
  </active_context>

  <!-- Work order status (ARCHITECT mode focus) -->
  <work_order>
    <template name="Protagonist" status="in_progress">
      <completed>fatal_flaw, the_lie, arc_start</completed>
      <missing>arc_midpoint, arc_resolution</missing>
    </template>
    <template name="Beat Sheet" status="draft_ready">
      <completed>beat_1 through beat_10</completed>
      <missing>beat_11, beat_12, beat_13, beat_14, beat_15</missing>
    </template>
    <template name="Theme" status="complete"/>
    <template name="World Rules" status="not_started"/>
  </work_order>

  <!-- Voice context (DIRECTOR/EDITOR mode focus) -->
  <voice_context>
    <locked>true</locked>
    <winning_agent>claude-sonnet</winning_agent>
    <winning_strategy>CHARACTER_DEPTH</winning_strategy>
    <voice_state>tense_determined</voice_state>
    <antipatterns>
      <pattern severity="zero_tolerance">with surgical precision</pattern>
      <pattern severity="zero_tolerance">something stirred within</pattern>
      <pattern severity="deduction">passive voice in dialogue tags</pattern>
    </antipatterns>
  </voice_context>

  <!-- Scene context (DIRECTOR mode focus) -->
  <scene_context>
    <scaffold_id>ch4-sc2</scaffold_id>
    <beat_alignment>Midpoint - False Victory</beat_alignment>
    <pov_character>Elena</pov_character>
    <word_target>2500</word_target>
    <callbacks>the_photograph, mother_warning</callbacks>
    <foreshadowing>marcus_betrayal, ship_malfunction</foreshadowing>
  </scene_context>

  <!-- Knowledge context (retrieved from KB) -->
  <knowledge_context>
    <entry category="character" key="elena_fatal_flaw">
      Inability to trust, stemming from father's abandonment
    </entry>
    <entry category="character" key="elena_the_lie">
      Believes she can only rely on herself
    </entry>
    <entry category="world" key="ftl_limitation">
      FTL travel requires human navigator sacrifice (1 per jump)
    </entry>
    <entry category="structure" key="midpoint_type">
      False victory - Elena thinks she's won Marcus's trust
    </entry>
  </knowledge_context>

  <!-- Registered external resources -->
  <notebooks>
    <notebook id="nb_abc123" role="world_building">Elena's Universe Research</notebook>
    <notebook id="nb_def456" role="character_voice">Character Interviews</notebook>
  </notebooks>

  <!-- Agent memory (persisted preferences/corrections) -->
  <agent_memory>
    <preference>Writer prefers short sentences in action sequences</preference>
    <preference>Writer dislikes adverbs in dialogue tags</preference>
    <preference>Use British spellings (colour, honour)</preference>
    <correction>Chapter 3: Elena lost her gun, do not reference it</correction>
    <correction>Marcus has a limp (right leg), not mentioned yet but relevant</correction>
    <continuity>The photograph was introduced in Chapter 2, Scene 3</continuity>
    <continuity>Elena's mother died before the story begins</continuity>
  </agent_memory>

  <!-- Voice Bundle reference (DIRECTOR/EDITOR modes) -->
  <voice_bundle loaded="true">
    <winning_passage_file>content/Voice Bundle/Voice-Gold-Standard.md</winning_passage_file>
    <antipattern_file>content/Voice Bundle/Voice-Anti-Pattern-Sheet.md</antipattern_file>
    <evolution_file>content/Voice Bundle/Phase-Evolution-Guide.md</evolution_file>
    <voice_summary>
      First-person, present tense. Short punchy sentences in action.
      Longer introspective passages when alone. Avoids adverbs.
      Metaphors drawn from mechanical/industrial domains.
    </voice_summary>
  </voice_bundle>

  <!-- Current scaffold (DIRECTOR mode scene writing) -->
  <active_scaffold>
    <scaffold_id>ch4-sc2</scaffold_id>
    <title>The Confrontation</title>
    <beat_alignment>Midpoint - False Victory</beat_alignment>
    <word_target>2500</word_target>
    <pov_character>Elena</pov_character>
    <characters_present>Elena, Marcus, Background: dock workers</characters_present>
    <location>Abandoned warehouse, Boston docks</location>
    <time_of_day>Dusk</time_of_day>
    <weather>Fog rolling in</weather>
    <callbacks>the_photograph, mother_warning</callbacks>
    <foreshadowing>marcus_betrayal, ship_malfunction</foreshadowing>
    <protagonist_constraint>Cannot directly ask Marcus about the past</protagonist_constraint>
    <scene_goal>Elena obtains key information while maintaining her cover</scene_goal>
  </active_scaffold>
</session_state>
```

### 6.2 Agent Memory: The "Claude Code Feel"

The `<agent_memory>` section is critical for creating the experience of a deeply aware assistant. It contains:

| Entry Type | Purpose | Example |
|------------|---------|---------|
| `preference` | Writer's style preferences | "Use British spellings" |
| `correction` | Continuity fixes from writer | "Elena lost her gun in Ch3" |
| `continuity` | Important story facts | "Mother died before story begins" |

**Source**: These entries come from the Foreman KB Service (`foreman_kb_service.py`). When the Foreman learns a preference or correction during conversation, it calls `save_decision(category="preference", ...)` which persists to SQLite. The PromptAssembler retrieves recent entries via `get_context_for_foreman()`.

**Why This Matters**: Without explicit memory injection, models "forget" preferences between sessions. By injecting `<agent_memory>` into every prompt, the Foreman maintains consistency even across model switches.

### 6.3 Voice Bundle Injection (DIRECTOR/EDITOR Modes)

When in DIRECTOR or EDITOR mode, the session state includes the Voice Bundle:

```xml
<voice_bundle loaded="true">
  <winning_passage_file>content/Voice Bundle/Voice-Gold-Standard.md</winning_passage_file>
  <voice_summary>
    First-person, present tense. Short punchy sentences in action...
  </voice_summary>
</voice_bundle>
```

**Implementation**: The PromptAssembler checks if `voice_bundle_path` exists in settings. If so, it:
1. Loads the gold standard file (first 2000 chars)
2. Loads anti-patterns (first 1500 chars)
3. Generates a concise `voice_summary` for context-limited models
4. Injects into session state

**For Minimal Tier Models**: Only `voice_summary` is included (saves ~1500 tokens).

### 6.4 Active Scaffold (DIRECTOR Mode Scene Writing)

When writing a scene, the scaffold provides structural context:

```xml
<active_scaffold>
  <scaffold_id>ch4-sc2</scaffold_id>
  <beat_alignment>Midpoint - False Victory</beat_alignment>
  <callbacks>the_photograph, mother_warning</callbacks>
  <foreshadowing>marcus_betrayal</foreshadowing>
  ...
</active_scaffold>
```

**Source**: Generated by `scaffold_generator_service.py` and stored in the scene writing request. The scaffold ensures every scene:
- Aligns with the Beat Sheet
- Maintains continuity (callbacks to earlier scenes)
- Plants seeds for future scenes (foreshadowing)

### 6.5 Mode-Specific State Variants

Not all state is relevant in all modes. The assembler includes mode-appropriate sections:

| Mode | Always Include | Include if Relevant | Omit |
|------|----------------|---------------------|------|
| ARCHITECT | project, work_order, notebooks | knowledge_context | voice_context, scene_context |
| VOICE_CALIBRATION | project, work_order, voice_context | knowledge_context | scene_context |
| DIRECTOR | project, active_context, voice_context, scene_context | knowledge_context, callbacks | work_order (summarized only) |
| EDITOR | project, active_context, voice_context | knowledge_context, agent_memory | work_order, scene_context |

### 6.3 Size-Constrained Variants

For models with limited context windows, we provide trimmed state:

**Full State** (~800 tokens): All sections, 10+ KB entries
**Medium State** (~400 tokens): Core sections, 5 KB entries
**Minimal State** (~150 tokens): Mode, completion %, active file only

```xml
<!-- Minimal state for small models -->
<session_state>
  <current_mode>DIRECTOR</current_mode>
  <completion_pct>75</completion_pct>
  <active_file>Chapter_4_Scene_2.md</active_file>
  <voice_locked>true</voice_locked>
  <current_beat>Midpoint</current_beat>
</session_state>
```

---

## 7. Output Format Specification

### 7.1 Response Structure

Every agent response follows this structure:

```xml
<thinking>
[Optional internal reasoning - helps debugging and transparency]
</thinking>

<message>
[Required communication to the writer - Markdown formatted]
</message>

<action type="action_name">
[Zero or more actions]
</action>

<content_update target="file_path">
[Optional prose content when writing/editing]
</content_update>
```

### 7.2 Parsing Strategy

The application parses responses with these regex patterns:

```python
import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ParsedResponse:
    thinking: Optional[str]
    message: str
    actions: List[dict]
    content_updates: List[dict]
    raw: str

def parse_agent_response(response: str) -> ParsedResponse:
    """Parse agent response into structured components."""

    # Extract thinking (optional)
    thinking_match = re.search(r'<thinking>(.*?)</thinking>', response, re.DOTALL)
    thinking = thinking_match.group(1).strip() if thinking_match else None

    # Extract message (required)
    message_match = re.search(r'<message>(.*?)</message>', response, re.DOTALL)
    if not message_match:
        # Fallback: treat entire response as message (graceful degradation)
        message = response
    else:
        message = message_match.group(1).strip()

    # Extract actions
    actions = []
    action_pattern = r'<action type="(\w+)">(.*?)</action>'
    for match in re.finditer(action_pattern, response, re.DOTALL):
        action_type = match.group(1)
        action_content = match.group(2).strip()
        actions.append({
            'type': action_type,
            'content': parse_action_content(action_content),
            'raw': action_content
        })

    # Extract content updates
    content_updates = []
    update_pattern = r'<content_update target="([^"]+)">(.*?)</content_update>'
    for match in re.finditer(update_pattern, response, re.DOTALL):
        target = match.group(1)
        content = match.group(2).strip()
        content_updates.append({
            'target': target,
            'content': content
        })

    return ParsedResponse(
        thinking=thinking,
        message=message,
        actions=actions,
        content_updates=content_updates,
        raw=response
    )

def parse_action_content(content: str) -> dict:
    """Parse action parameters from XML content."""
    params = {}
    param_pattern = r'<(\w+)>(.*?)</\1>'
    for match in re.finditer(param_pattern, content, re.DOTALL):
        key = match.group(1)
        value = match.group(2).strip()
        # Handle lists (e.g., missing fields)
        if value.startswith('[') and value.endswith(']'):
            try:
                value = json.loads(value)
            except:
                pass
        params[key] = value
    return params
```

### 7.3 Graceful Degradation

If an agent response lacks proper XML tags (common with smaller models), we fall back:

1. **No `<message>` tag**: Treat entire response as message
2. **Malformed action**: Log warning, skip action, include in message
3. **Nested tag errors**: Best-effort parsing, log for review

```python
def parse_with_fallback(response: str) -> ParsedResponse:
    """Parse with multiple fallback strategies."""
    try:
        return parse_agent_response(response)
    except Exception as e:
        logger.warning(f"XML parsing failed: {e}, using fallback")
        return ParsedResponse(
            thinking=None,
            message=response,  # Entire response becomes message
            actions=[],
            content_updates=[],
            raw=response
        )
```

---

## 8. Action System

### 8.1 Action Categories

Actions are grouped by mode availability:

| Action Type | ARCHITECT | VOICE_CAL | DIRECTOR | EDITOR | Description |
|-------------|-----------|-----------|----------|--------|-------------|
| `query_notebook` | ✓ | ✓ | ✓ | ✓ | Query NotebookLM |
| `save_decision` | ✓ | ✓ | ✓ | ✓ | Record to KB |
| `write_template` | ✓ | - | - | - | Story Bible templates |
| `update_status` | ✓ | ✓ | - | - | Template status |
| `start_tournament` | - | ✓ | - | - | Voice tournament |
| `select_winner` | - | ✓ | - | - | Pick winning voice |
| `generate_bundle` | - | ✓ | - | - | Create Voice Bundle |
| `generate_scaffold` | - | - | ✓ | - | Scene scaffold |
| `write_scene` | - | - | ✓ | - | Draft a scene |
| `run_health_check` | - | - | ✓ | ✓ | Structural analysis |
| `apply_edit` | - | - | - | ✓ | Apply prose changes |

### 8.2 Action Schemas

Each action has a defined schema:

```yaml
actions:
  query_notebook:
    description: "Query a NotebookLM notebook for information"
    parameters:
      notebook_id:
        type: string
        required: true
        description: "Notebook identifier"
      query:
        type: string
        required: true
        description: "Natural language question"
    returns:
      type: string
      description: "Notebook's response"

  save_decision:
    description: "Record a structural decision to the Knowledge Base"
    parameters:
      category:
        type: string
        required: true
        enum: [character, world, structure, constraint, preference, voice]
      key:
        type: string
        required: true
        description: "Unique identifier for this decision"
      value:
        type: string
        required: true
        description: "The decision content"
      source:
        type: string
        required: false
        description: "Origin (notebook, brainstorm, user_stated)"
    returns:
      type: boolean
      description: "Success status"

  write_template:
    description: "Write or update a Story Bible template"
    parameters:
      template:
        type: string
        required: true
        enum: [protagonist, beat_sheet, theme, world_rules]
      content:
        type: object
        required: true
        description: "Structured content matching template schema"
    returns:
      type: string
      description: "Path to written file"

  generate_scaffold:
    description: "Generate a scene scaffold for drafting"
    parameters:
      chapter:
        type: integer
        required: true
      scene:
        type: integer
        required: true
      title:
        type: string
        required: true
      enrichment:
        type: array
        required: false
        items: string
        description: "Additional context sources"
    returns:
      type: object
      description: "Complete scaffold object"
```

### 8.3 Action Execution Flow

```
Agent Response
      │
      ▼
┌─────────────┐
│ Parse XML   │
│ Response    │
└─────────────┘
      │
      ▼
┌─────────────┐     ┌─────────────┐
│ Display     │────▶│ User Sees   │
│ <message>   │     │ Message     │
└─────────────┘     └─────────────┘
      │
      ▼
┌─────────────┐
│ For each    │
│ <action>    │
└─────────────┘
      │
      ▼
┌─────────────┐     ┌─────────────┐
│ Validate    │────▶│ Log Invalid │
│ Against     │ No  │ Skip Action │
│ Schema      │     └─────────────┘
└─────────────┘
      │ Yes
      ▼
┌─────────────┐     ┌─────────────┐
│ Check Mode  │────▶│ Log Warning │
│ Permission  │ No  │ Skip Action │
└─────────────┘     └─────────────┘
      │ Yes
      ▼
┌─────────────┐
│ Execute     │
│ Handler     │
└─────────────┘
      │
      ▼
┌─────────────┐
│ Update      │
│ Session     │
│ State       │
└─────────────┘
```

---

## 9. Model-Specific Adaptations

### 9.1 Model Capability Matrix

```python
MODEL_CAPABILITIES = {
    # Cloud models - large context
    "gpt-4o": {
        "context_window": 128000,
        "xml_reliability": "high",
        "instruction_following": "high",
        "tier": "full"
    },
    "claude-sonnet-4": {
        "context_window": 200000,
        "xml_reliability": "very_high",
        "instruction_following": "very_high",
        "tier": "full"
    },
    "gemini-2.0-flash": {
        "context_window": 1000000,
        "xml_reliability": "medium",  # Prefers JSON
        "instruction_following": "high",
        "tier": "full"
    },
    "grok-2": {
        "context_window": 131072,
        "xml_reliability": "high",
        "instruction_following": "high",
        "tier": "full"
    },

    # Mid-tier models
    "deepseek-chat": {
        "context_window": 64000,
        "xml_reliability": "medium",
        "instruction_following": "medium",
        "tier": "medium"
    },
    "qwen-plus": {
        "context_window": 131072,
        "xml_reliability": "medium",
        "instruction_following": "medium",
        "tier": "medium"
    },
    "mistral-large": {
        "context_window": 128000,
        "xml_reliability": "high",
        "instruction_following": "high",
        "tier": "full"
    },

    # Local models - limited context
    "llama3.2:3b": {
        "context_window": 8192,
        "xml_reliability": "low",
        "instruction_following": "low",
        "tier": "minimal"
    },
    "mistral:7b": {
        "context_window": 32768,
        "xml_reliability": "medium",
        "instruction_following": "medium",
        "tier": "medium"
    }
}
```

### 9.2 Tier-Based Prompt Assembly

```python
def get_prompt_tier(model_id: str) -> str:
    """Determine prompt assembly tier for a model."""
    caps = MODEL_CAPABILITIES.get(model_id, {})
    return caps.get("tier", "medium")

def assemble_prompt_for_tier(tier: str, layers: dict) -> str:
    """Assemble prompt based on model tier."""

    if tier == "full":
        # All layers, full detail
        return "\n\n".join([
            layers["identity"],
            layers["process_map"],
            layers["mode_rules"],
            layers["session_state"],
            layers["protocols"]
        ])

    elif tier == "medium":
        # Summarized process map, trimmed state
        return "\n\n".join([
            layers["identity"],
            summarize_process_map(layers["process_map"]),
            layers["mode_rules"],
            trim_session_state(layers["session_state"], max_entries=5),
            layers["protocols"]
        ])

    elif tier == "minimal":
        # Identity + essential rules only
        return "\n\n".join([
            compress_identity(layers["identity"]),
            get_mode_essentials(layers["mode_rules"]),
            get_minimal_state(layers["session_state"]),
            get_core_protocols(layers["protocols"])
        ])
```

### 9.3 XML Reliability Handling

For models with lower XML reliability, we add explicit reminders:

```python
def add_xml_reinforcement(prompt: str, model_id: str) -> str:
    """Add XML format reminders for unreliable models."""
    caps = MODEL_CAPABILITIES.get(model_id, {})
    reliability = caps.get("xml_reliability", "medium")

    if reliability in ("low", "medium"):
        reminder = """
CRITICAL FORMAT REMINDER:
- Wrap ALL communication in <message>...</message> tags
- Wrap reasoning in <thinking>...</thinking> tags
- Wrap actions in <action type="...">...</action> tags
- Do NOT use JSON. Use XML only.
"""
        return prompt + "\n" + reminder

    return prompt
```

### 9.4 Gemini Special Handling

Gemini prefers JSON but can use XML with reinforcement:

```python
def adapt_for_gemini(prompt: str) -> str:
    """Gemini-specific adaptations."""
    # Add explicit XML preference override
    gemini_note = """
NOTE: Although you may prefer JSON, this application requires XML output.
Please use <message>, <thinking>, and <action> tags as specified in the protocols.
"""
    return prompt + "\n" + gemini_note
```

---

## 10. PromptAssembler Service

### 10.1 Service Architecture

```python
"""
PromptAssembler Service

Responsible for assembling the Context Sandwich for any model.
"""

import logging
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

from backend.agents.foreman import ForemanMode, WorkOrder
from backend.services.foreman_kb_service import ForemanKBService

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


@dataclass
class AssemblyConfig:
    """Configuration for prompt assembly."""
    model_id: str
    mode: ForemanMode
    include_thinking_reminder: bool = True
    max_kb_entries: int = 10
    max_conversation_turns: int = 10


class PromptAssembler:
    """
    Assembles the Context Sandwich for agent prompts.

    Responsibilities:
    - Load modular prompt files
    - Generate session state XML
    - Apply model-specific adaptations
    - Manage context window budget
    """

    def __init__(self, kb_service: ForemanKBService):
        self.kb_service = kb_service
        self._prompt_cache: Dict[str, str] = {}

    def assemble(
        self,
        config: AssemblyConfig,
        work_order: WorkOrder,
        conversation_history: list,
        user_message: str,
        active_context: Optional[dict] = None
    ) -> str:
        """
        Assemble complete prompt for the agent.

        Args:
            config: Assembly configuration
            work_order: Current work order state
            conversation_history: Recent conversation turns
            user_message: Current user input
            active_context: Optional context (file, beat, scene)

        Returns:
            Complete assembled prompt string
        """
        # Load static layers
        identity = self._load_prompt("identity.md")
        process_map = self._load_prompt("process_map.md")
        mode_rules = self._load_prompt(f"modes/{config.mode.value}.md")
        protocols = self._load_prompt("protocols.md")

        # Generate dynamic state
        session_state = self._generate_session_state(
            work_order=work_order,
            mode=config.mode,
            active_context=active_context,
            max_kb_entries=config.max_kb_entries
        )

        # Get model tier
        tier = get_prompt_tier(config.model_id)

        # Assemble based on tier
        layers = {
            "identity": identity,
            "process_map": process_map,
            "mode_rules": mode_rules,
            "session_state": session_state,
            "protocols": protocols
        }

        base_prompt = assemble_prompt_for_tier(tier, layers)

        # Add model-specific adaptations
        base_prompt = self._apply_model_adaptations(base_prompt, config.model_id)

        # Add conversation history
        history_str = self._format_conversation(
            conversation_history,
            max_turns=config.max_conversation_turns
        )

        # Assemble final prompt
        final_prompt = f"{base_prompt}\n\n## CONVERSATION HISTORY\n\n{history_str}\n\n## CURRENT MESSAGE\n\nUser: {user_message}"

        # Log assembly for debugging
        logger.debug(f"Assembled prompt for {config.model_id} ({tier} tier): {len(final_prompt)} chars")

        return final_prompt

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt file with caching."""
        if filename in self._prompt_cache:
            return self._prompt_cache[filename]

        path = PROMPTS_DIR / filename
        if not path.exists():
            logger.warning(f"Prompt file not found: {path}")
            return ""

        content = path.read_text(encoding="utf-8")
        self._prompt_cache[filename] = content
        return content

    def _generate_session_state(
        self,
        work_order: WorkOrder,
        mode: ForemanMode,
        active_context: Optional[dict],
        max_kb_entries: int
    ) -> str:
        """Generate session state XML."""
        lines = ['<session_state>']

        # Core positioning
        lines.append(f'  <current_mode>{mode.value.upper()}</current_mode>')
        lines.append(f'  <completion_pct>{work_order.completion_percentage:.0f}</completion_pct>')

        # Project info
        lines.append('  <project>')
        lines.append(f'    <title>{work_order.project_title}</title>')
        lines.append(f'    <protagonist>{work_order.protagonist_name}</protagonist>')
        lines.append('  </project>')

        # Active context (if provided)
        if active_context:
            lines.append('  <active_context>')
            for key, value in active_context.items():
                lines.append(f'    <{key}>{value}</{key}>')
            lines.append('  </active_context>')

        # Work order (mode-dependent detail)
        if mode in (ForemanMode.ARCHITECT, ForemanMode.VOICE_CALIBRATION):
            lines.append('  <work_order>')
            for template in work_order.templates:
                status_attr = f'status="{template.status.value}"'
                if template.missing_fields:
                    missing = ', '.join(template.missing_fields)
                    lines.append(f'    <template name="{template.name}" {status_attr} missing="{missing}"/>')
                else:
                    lines.append(f'    <template name="{template.name}" {status_attr}/>')
            lines.append('  </work_order>')

        # Knowledge context
        kb_entries = self.kb_service.get_context_for_foreman(
            project_id=work_order.project_title,
            limit=max_kb_entries
        )
        if kb_entries:
            lines.append('  <knowledge_context>')
            for entry in kb_entries:
                lines.append(f'    <entry category="{entry.category}" key="{entry.key}">')
                lines.append(f'      {entry.value}')
                lines.append('    </entry>')
            lines.append('  </knowledge_context>')

        # Notebooks
        if work_order.notebooks:
            lines.append('  <notebooks>')
            for nb_id, role in work_order.notebooks.items():
                lines.append(f'    <notebook id="{nb_id}" role="{role}"/>')
            lines.append('  </notebooks>')

        lines.append('</session_state>')

        return '\n'.join(lines)

    def _apply_model_adaptations(self, prompt: str, model_id: str) -> str:
        """Apply model-specific adaptations."""
        prompt = add_xml_reinforcement(prompt, model_id)

        if "gemini" in model_id.lower():
            prompt = adapt_for_gemini(prompt)

        return prompt

    def _format_conversation(self, history: list, max_turns: int) -> str:
        """Format conversation history."""
        recent = history[-max_turns:] if len(history) > max_turns else history

        lines = []
        for turn in recent:
            role = turn.get("role", "user").upper()
            content = turn.get("content", "")
            lines.append(f"{role}: {content}")

        return "\n\n".join(lines)

    def clear_cache(self):
        """Clear prompt cache (for development/hot-reload)."""
        self._prompt_cache.clear()
        logger.info("Prompt cache cleared")


# Singleton instance
_assembler: Optional[PromptAssembler] = None

def get_prompt_assembler() -> PromptAssembler:
    """Get or create the PromptAssembler singleton."""
    global _assembler
    if _assembler is None:
        from backend.services.foreman_kb_service import get_foreman_kb_service
        _assembler = PromptAssembler(get_foreman_kb_service())
    return _assembler
```

### 10.2 Integration with Foreman

```python
# In foreman.py - Updated chat method

async def chat(self, user_message: str) -> Dict:
    """Process a chat message using the assembled prompt."""
    from backend.services.prompt_assembler import get_prompt_assembler, AssemblyConfig

    assembler = get_prompt_assembler()

    # Determine model for this task
    model_id = await self._select_model_for_task(user_message)

    # Assemble prompt
    config = AssemblyConfig(
        model_id=model_id,
        mode=self.mode,
        max_kb_entries=10,
        max_conversation_turns=10
    )

    prompt = assembler.assemble(
        config=config,
        work_order=self.work_order,
        conversation_history=self.conversation,
        user_message=user_message,
        active_context=self._get_active_context()
    )

    # Query the model
    response = await self._query_llm(prompt, model_id)

    # Parse response
    parsed = parse_agent_response(response)

    # Execute actions
    action_results = await self._execute_actions(parsed.actions)

    # Update conversation history
    self.conversation.append({"role": "user", "content": user_message})
    self.conversation.append({"role": "assistant", "content": parsed.message})

    return {
        "message": parsed.message,
        "thinking": parsed.thinking,
        "actions": action_results,
        "content_updates": parsed.content_updates
    }
```

---

## 11. Knowledge Graph Integration

The Knowledge Graph is the **central nervous system** of Writers Factory. It stores all facts about characters, world, structure, and maintains the "living memory" that enables process-aware agents.

### 11.1 The Three-Brain Architecture

Writers Factory uses three interconnected knowledge systems:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BRAIN 1: KNOWLEDGE GRAPH                         │
│                    "The Archive" (Permanent Facts)                  │
├─────────────────────────────────────────────────────────────────────┤
│  Storage: SQLite + NetworkX (in-memory)                             │
│  Contents:                                                          │
│    - Character entities (names, relationships, traits)              │
│    - Location entities (places, connections)                        │
│    - Plot events (what happened, when, who was involved)            │
│    - Theme nodes (symbols, motifs, resonance scores)                │
│    - World rules (magic systems, physics, constraints)              │
│  Operations:                                                        │
│    - PageRank (identify central characters)                         │
│    - Shortest paths (relationship distances)                        │
│    - Subgraph extraction (scene-relevant context)                   │
│  Files: backend/graph/graph_service.py, schema.py                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Consolidator promotes
                              │ "soft facts" → "hard facts"
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BRAIN 2: FOREMAN KB                              │
│                    "The Memory" (Recent Decisions)                  │
├─────────────────────────────────────────────────────────────────────┤
│  Storage: SQLite (foreman_kb table)                                 │
│  Contents:                                                          │
│    - Character decisions (fatal flaw, arc direction)                │
│    - World decisions (rules, constraints)                           │
│    - Structure decisions (beat choices, scene order)                │
│    - Writer preferences (style, spelling, avoid patterns)           │
│  Lifecycle:                                                         │
│    1. Foreman learns fact → save_decision() → is_promoted=False     │
│    2. Consolidator runs → promotes to Knowledge Graph               │
│    3. Entry marked is_promoted=True                                 │
│  Key Method: get_context_for_foreman() → tiered retrieval           │
│  File: backend/services/foreman_kb_service.py                       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Health checks analyze
                              │ both brains
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BRAIN 3: HEALTH SERVICE                          │
│                    "The Analyzer" (Structural Analysis)             │
├─────────────────────────────────────────────────────────────────────┤
│  Storage: SQLite (health_reports, flaw_challenges, theme_overrides) │
│  Seven Health Checks:                                               │
│    A1: Pacing Plateau Detection                                     │
│    A2: Beat Progress Validation                                     │
│    A3: Timeline Consistency (LLM semantic analysis)                 │
│    B1: Fatal Flaw Challenge Monitoring                              │
│    B2: Cast Function Verification                                   │
│    C1: Symbolic Layering                                            │
│    C2: Theme Resonance (hybrid LLM + manual override)               │
│  Output: Health reports with scores, warnings, recommendations      │
│  File: backend/services/graph_health_service.py                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 11.2 Information Flow Diagram

```
                           ┌──────────────────┐
                           │   WRITER INPUT   │
                           │  (Chat, Files)   │
                           └────────┬─────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                │                                       │
                ▼                                       ▼
    ┌───────────────────┐                   ┌───────────────────┐
    │  Story Bible      │                   │  Foreman Chat     │
    │  (*.md files)     │                   │  Session          │
    └─────────┬─────────┘                   └─────────┬─────────┘
              │                                       │
              │ Ingestor                              │ Session Service
              │ (initial load)                        │ (stores events)
              ▼                                       ▼
    ┌───────────────────┐                   ┌───────────────────┐
    │                   │                   │  Foreman KB       │
    │                   │                   │  (soft facts)     │
    │   KNOWLEDGE       │                   │  is_promoted=F    │
    │   GRAPH           │◄──────────────────┤                   │
    │   (hard facts)    │   Consolidator    └───────────────────┘
    │                   │   promotes
    │                   │
    └─────────┬─────────┘
              │
              │ Context Injection
              │ (get_context_for_foreman)
              ▼
    ┌───────────────────────────────────────────────────────────┐
    │                    PROMPT ASSEMBLER                        │
    │  ┌─────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────┐  │
    │  │Identity │ │Process Map│ │Mode Rules│ │Session State │  │
    │  └─────────┘ └───────────┘ └──────────┘ └──────────────┘  │
    │                                              ▲             │
    │                         ┌────────────────────┘             │
    │                         │                                  │
    │              ┌──────────┴──────────┐                       │
    │              │ <knowledge_context> │                       │
    │              │   Character facts   │                       │
    │              │   World rules       │                       │
    │              │   Recent decisions  │                       │
    │              └─────────────────────┘                       │
    └───────────────────────────┬───────────────────────────────┘
                                │
                                │ Assembled Prompt
                                ▼
                      ┌───────────────────┐
                      │    LLM MODEL      │
                      │  (GPT-4o, Claude, │
                      │   Gemini, Ollama) │
                      └─────────┬─────────┘
                                │
                                │ Response with
                                │ <action> tags
                                ▼
                      ┌───────────────────┐
                      │  RESPONSE PARSER  │
                      │  Extract actions  │
                      └─────────┬─────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ save_decision   │  │ write_template  │  │ generate_scaffold│
│ → Foreman KB    │  │ → Story Bible   │  │ → Scene Writer   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 11.3 Context Injection Strategy

The Foreman KB Service uses **tiered retrieval** to manage context window limits:

```python
# Simplified from foreman_kb_service.py

def get_context_for_foreman(project_id: str, limit: int = 20) -> List[KBEntry]:
    """
    Smart context selection that prioritizes foundational facts.

    Tier 1 (ALWAYS include - no limit):
      - character: Fatal flaws, lies, arcs (the protagonist's core)
      - constraint: Hard rules that never change

    Tier 2 (Include RECENT entries up to limit):
      - world: Settings that may evolve
      - structure: Plot points that shift during development
      - preference: Author preferences that change
    """

    # Foundational entries - always include ALL of these
    foundational = query(
        category IN ('character', 'constraint'),
        project_id = project_id
    )

    # Fill remaining slots with recent volatile entries
    remaining_slots = limit - len(foundational)
    volatile = query(
        category IN ('world', 'structure', 'preference'),
        project_id = project_id,
        ORDER BY updated_at DESC,
        LIMIT remaining_slots
    )

    return foundational + volatile
```

**Why This Matters**: A writer might make 200 scene-specific decisions over weeks of work. Without tiered retrieval, the context would overflow and drop foundational facts like "Mickey's fatal flaw is pride." This strategy ensures Day 1 character decisions persist even after 100+ scene drafts.

### 11.4 The Consolidation Cycle

The Consolidator (`consolidator_service.py`) is "The Liver" - it digests raw conversation into structured knowledge:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONSOLIDATION CYCLE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TRIGGER: Manual API call OR scheduled (every N minutes)        │
│                                                                 │
│  STEP 1: Fetch uncommitted session events                       │
│          (raw conversation from sessions.db)                    │
│                                                                 │
│  STEP 2: For Foreman KB entries (already structured):           │
│          - Direct mapping to graph nodes                        │
│          - No LLM needed                                        │
│          - Example: "mickey_fatal_flaw" → Character node        │
│                                                                 │
│  STEP 3: For raw session events (unstructured):                 │
│          - Send to Llama 3.2: "Extract entities & relations"    │
│          - Low temperature (0.1) for consistency                │
│          - Returns {nodes: [], edges: []}                       │
│                                                                 │
│  STEP 4: Conflict detection                                     │
│          - Check for contradictions (alive↔dead, loves↔hates)   │
│          - Store conflicts in graph_conflicts.json              │
│          - Don't update on conflict (conservative)              │
│                                                                 │
│  STEP 5: Merge into knowledge_graph.json                        │
│          - File locking prevents corruption                     │
│          - Deduplication by node ID                             │
│                                                                 │
│  STEP 6: Mark entries as processed                              │
│          - Session events: committed=True                       │
│          - KB entries: is_promoted=True                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 11.5 Health Check Integration

Health checks analyze the graph to detect structural problems:

```xml
<!-- Example: After health check, inject findings into state -->
<session_state>
  ...
  <health_alerts>
    <alert severity="warning" check="B1_flaw_challenge">
      Mickey's fatal flaw (pride) hasn't been challenged in 12 scenes.
      Last challenge: Chapter 3, Scene 2.
      Recommendation: Create obstacle requiring him to accept help.
    </alert>
    <alert severity="info" check="A2_beat_progress">
      Manuscript is 45% complete but Midpoint beat not yet written.
      Expected at 50%. Consider prioritizing Midpoint scene.
    </alert>
  </health_alerts>
  ...
</session_state>
```

---

## 12. Service Integration & Data Flows

This section maps how agent actions invoke existing backend services.

### 12.1 Action → Service Mapping

| Action Type | Service Called | Method | Returns |
|-------------|----------------|--------|---------|
| `query_notebook` | `notebooklm_service` | `query_notebook(id, query)` | Notebook response text |
| `save_decision` | `foreman_kb_service` | `save_decision(...)` | Success boolean |
| `write_template` | `story_bible_service` | `write_template(name, content)` | File path |
| `update_status` | `foreman.work_order` | Direct update | Updated work order |
| `start_tournament` | `voice_calibration_service` | `start_tournament(...)` | Tournament ID |
| `select_winner` | `voice_calibration_service` | `select_winner(...)` | Voice Bundle path |
| `generate_scaffold` | `scaffold_generator_service` | `generate_scaffold(...)` | Scaffold object |
| `write_scene` | `scene_writer_service` | `generate_variants(...)` | Scene variants |
| `analyze_scene` | `scene_analyzer_service` | `analyze_scene(...)` | Analysis scores |
| `enhance_scene` | `scene_enhancement_service` | `enhance(...)` | Enhanced scene |
| `run_health_check` | `graph_health_service` | `run_check(scope)` | Health report |

### 12.2 ARCHITECT Mode Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCHITECT MODE FLOW                          │
└─────────────────────────────────────────────────────────────────┘

Writer: "Let's work on Mickey's character arc"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ PROMPT ASSEMBLER                                                │
│ Injects: work_order status, KB context (existing decisions)     │
│ Mode rules: "Challenge weak choices, require evidence"          │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ LLM RESPONSE                                                    │
│                                                                 │
│ <thinking>                                                      │
│ Work order shows Protagonist template in_progress.              │
│ KB has fatal_flaw but missing arc_resolution.                   │
│ Should probe for ending.                                        │
│ </thinking>                                                     │
│                                                                 │
│ <message>                                                       │
│ Mickey's pride is clear - but where does it take him?           │
│ Does he learn humility, or does pride destroy him?              │
│ </message>                                                      │
│                                                                 │
│ <action type="update_status">                                   │
│   <template>Protagonist</template>                              │
│   <status>in_progress</status>                                  │
│   <missing>["arc_resolution"]</missing>                         │
│ </action>                                                       │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ACTION EXECUTOR                                                 │
│ 1. Parse <action type="update_status">                          │
│ 2. Call: work_order.update_template_status(...)                 │
│ 3. Return: Updated work order to frontend                       │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
Writer: "He learns to accept help, but only from family"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ LLM RESPONSE                                                    │
│                                                                 │
│ <message>                                                       │
│ Strong choice - selective trust rather than universal change.   │
│ I'm recording this decision.                                    │
│ </message>                                                      │
│                                                                 │
│ <action type="save_decision">                                   │
│   <category>character</category>                                │
│   <key>mickey_arc_resolution</key>                              │
│   <value>Learns to accept help from family only</value>         │
│   <source>writer_stated</source>                                │
│ </action>                                                       │
│                                                                 │
│ <action type="update_status">                                   │
│   <template>Protagonist</template>                              │
│   <status>complete</status>                                     │
│ </action>                                                       │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ACTION EXECUTOR                                                 │
│ 1. foreman_kb_service.save_decision(                            │
│      category="character",                                      │
│      key="mickey_arc_resolution",                               │
│      value="Learns to accept help from family only"             │
│    )                                                            │
│ 2. work_order.update_template_status("Protagonist", "complete") │
│ 3. If all templates complete → unlock VOICE_CALIBRATION mode    │
└─────────────────────────────────────────────────────────────────┘
```

### 12.3 VOICE CALIBRATION Mode Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                 VOICE CALIBRATION MODE FLOW                     │
└─────────────────────────────────────────────────────────────────┘

Writer: "I'm ready to find Mickey's voice"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ FOREMAN guides test passage design                              │
│ "What scene would reveal Mickey's voice best?"                  │
└─────────────────────────────────────────────────────────────────┘
                    │
Writer provides scene description
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ LLM RESPONSE                                                    │
│                                                                 │
│ <action type="start_tournament">                                │
│   <test_prompt>Mickey confronts his brother about money...</test_prompt>
│   <agents>["gpt-4o", "claude-sonnet", "grok-2"]</agents>        │
│   <strategies>["ACTION", "CHARACTER", "DIALOGUE", "BALANCED"]</strategies>
│   <context>Working class Boston, 1987, first-person POV</context>
│ </action>                                                       │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ voice_calibration_service.start_tournament()                    │
│                                                                 │
│ For each agent × strategy:                                      │
│   1. Build prompt with strategy instructions                    │
│   2. Call LLM to generate ~500 word passage                     │
│   3. Score on 6 dimensions (voice auth, prose quality, etc.)    │
│                                                                 │
│ Result: 12 variants (3 agents × 4 strategies)                   │
└─────────────────────────────────────────────────────────────────┘
                    │
Writer reviews, selects winner
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ <action type="select_winner">                                   │
│   <agent_id>claude-sonnet</agent_id>                            │
│   <strategy>CHARACTER_DEPTH</strategy>                          │
│   <variant_index>2</variant_index>                              │
│   <voice_notes>Love the internal monologue style</voice_notes>  │
│ </action>                                                       │
│                                                                 │
│ <action type="generate_bundle">                                 │
│   <output_dir>content/Voice Bundle/</output_dir>                │
│ </action>                                                       │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ voice_calibration_service.generate_bundle()                     │
│                                                                 │
│ Creates:                                                        │
│   - Voice-Gold-Standard.md (winning passage + analysis)         │
│   - Voice-Anti-Pattern-Sheet.md (what to avoid)                 │
│   - Phase-Evolution-Guide.md (how voice changes through acts)   │
│                                                                 │
│ Stores path in settings: voice_bundle_path                      │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
        Mode advances to DIRECTOR
        Voice Bundle now injected in all scene prompts
```

### 12.4 DIRECTOR Mode Data Flow (Scaffold → Scene)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIRECTOR MODE FLOW                           │
│              (Scaffold Generation → Scene Writing)              │
└─────────────────────────────────────────────────────────────────┘

Writer: "Let's write Chapter 4, Scene 2 - the confrontation"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: SCAFFOLD GENERATION                                     │
│                                                                 │
│ <action type="generate_scaffold">                               │
│   <chapter>4</chapter>                                          │
│   <scene>2</scene>                                              │
│   <title>The Confrontation</title>                              │
│   <enrichment>["beat_sheet", "character_arcs", "world_rules"]</enrichment>
│ </action>                                                       │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ scaffold_generator_service.generate_scaffold()                  │
│                                                                 │
│ Pulls from Knowledge Graph:                                     │
│   - Beat Sheet → identifies this is "Midpoint" beat             │
│   - Character arcs → Mickey's flaw should be challenged         │
│   - World rules → constraints that apply to this scene          │
│   - Prior scenes → callbacks to set up                          │
│   - Future scenes → foreshadowing to plant                      │
│                                                                 │
│ Generates SmartScaffold:                                        │
│   {                                                             │
│     scaffold_id: "ch4-sc2",                                     │
│     beat_alignment: "Midpoint - False Victory",                 │
│     characters_present: ["Mickey", "Danny", "Background: bar patrons"],
│     location: "O'Malley's Bar, Southie",                        │
│     callbacks: ["the_photograph", "mother_warning"],            │
│     foreshadowing: ["danny_betrayal"],                          │
│     protagonist_constraint: "Cannot mention the money directly",│
│     scene_goal: "Mickey thinks he's won Danny's trust"          │
│   }                                                             │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Scaffold injected into <session_state> as <active_scaffold>     │
└─────────────────────────────────────────────────────────────────┘
                    │
Writer: "Looks good, let's write it"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: SCENE VARIANT GENERATION                                │
│                                                                 │
│ <action type="write_scene">                                     │
│   <scaffold_id>ch4-sc2</scaffold_id>                            │
│   <strategies>["ACTION", "CHARACTER", "BALANCED"]</strategies>  │
│   <word_target>2500</word_target>                               │
│ </action>                                                       │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ scene_writer_service.generate_variants()                        │
│                                                                 │
│ For each strategy:                                              │
│   1. Load Voice Bundle (gold standard, anti-patterns)           │
│   2. Load scaffold context                                      │
│   3. Build prompt with strategy-specific instructions:          │
│      - ACTION: Fast pacing, physical detail                     │
│      - CHARACTER: Internal landscape, psychological truth       │
│      - BALANCED: Harmonious blend                               │
│   4. Generate scene with selected model                         │
│                                                                 │
│ Result: 3 scene variants for writer to review                   │
└─────────────────────────────────────────────────────────────────┘
                    │
Writer reviews, selects variant or requests hybrid
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: SCENE ANALYSIS                                          │
│                                                                 │
│ scene_analyzer_service.analyze_scene()                          │
│                                                                 │
│ Scores on 5 categories:                                         │
│   - Voice Authenticity (matches gold standard?)                 │
│   - Prose Quality (anti-patterns detected?)                     │
│   - Beat Compliance (advances the beat?)                        │
│   - Character Consistency (arc respected?)                      │
│   - Continuity (callbacks/foreshadowing present?)               │
│                                                                 │
│ Returns: SceneAnalysis with scores + specific feedback          │
└─────────────────────────────────────────────────────────────────┘
                    │
If issues found, proceed to enhancement
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: SCENE ENHANCEMENT (Optional)                            │
│                                                                 │
│ scene_enhancement_service.enhance()                             │
│                                                                 │
│ Two modes:                                                      │
│   - Action Prompt: Quick fixes for specific issues              │
│   - Six-Pass: Deep revision (structure, voice, prose, etc.)     │
│                                                                 │
│ Result: Enhanced scene with tracked changes                     │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
Scene saved to manuscript, graph updated with scene metadata
```

### 12.5 Behavioral Shifts Per Mode

The Foreman's personality should feel noticeably different in each mode:

| Mode | Persona | Communication Style | Example Response |
|------|---------|---------------------|------------------|
| **ARCHITECT** | Structural Editor | Challenging, probing, demands evidence | "That's a circumstance, not a flaw. What internal weakness KEEPS Mickey poor?" |
| **VOICE_CALIBRATION** | Voice Coach | Analytical, comparative, celebrates nuance | "Notice how Variant 3 uses shorter sentences in tension? That's the heartbeat." |
| **DIRECTOR** | Encouraging Partner | Forward momentum, flow-focused, minimal critique | "Strong opening. Let's keep the energy - what happens when Danny walks in?" |
| **EDITOR** | Critical Polisher | Ruthless, specific, craft-focused | "Three passive constructions in this paragraph. Also 'something stirred within' - that's on the anti-pattern list." |

**Implementation**: Each mode prompt file (`prompts/modes/*.md`) includes a "## Persona" section that explicitly describes the behavioral shift.

### 12.6 Explicit Trimming Rules for Small Models

For models with limited context windows, we apply explicit trimming:

| Component | Full Tier (128K+) | Medium Tier (32K-128K) | Minimal Tier (<32K) |
|-----------|-------------------|------------------------|---------------------|
| **Identity** | Full (~500 tok) | Full (~500 tok) | Compressed (~200 tok) |
| **Process Map** | Full (~1000 tok) | Summary only (~400 tok) | **Omit entirely** |
| **Mode Rules** | Full (~800 tok) | Essential rules (~600 tok) | Core rules only (~300 tok) |
| **Session State** | Full + 10 KB entries | 5 KB entries | Mode + file + 2 KB entries |
| **Voice Bundle** | Full excerpts | Summary only | **Omit** (rely on anti-pattern list) |
| **Scaffold** | Full scaffold | Essential fields only | Beat + goal + constraint only |
| **Protocols** | Full (~800 tok) | Essential protocols (~600 tok) | Core XML rules (~200 tok) |
| **Conversation** | 10 turns | 5 turns | 2 turns |

**Trimming Functions**:

```python
def summarize_process_map(full_map: str) -> str:
    """For medium tier: reduce to mode names + one-line descriptions."""
    return """
## Writing Process (Summary)
- ARCHITECT: Build Story Bible (challenge structure, no prose)
- VOICE_CALIBRATION: Find narrative voice (run tournament, lock voice)
- DIRECTOR: Draft scenes (beat-aware, voice-consistent)
- EDITOR: Polish prose (ruthless revision)
"""

def get_minimal_state(full_state: str) -> str:
    """For minimal tier: mode + file + 2 key facts only."""
    return """
<session_state>
  <current_mode>DIRECTOR</current_mode>
  <active_file>Chapter_4_Scene_2.md</active_file>
  <voice_locked>true</voice_locked>
  <current_beat>Midpoint</current_beat>
</session_state>
"""

def compress_identity(identity: str) -> str:
    """For minimal tier: one paragraph persona."""
    return """
You are The Foreman, a structural editor guiding novel creation.
Be direct, challenge weak choices, always propose next steps.
"""
```

---

## 13. Migration Path

### Phase 1: Extract Prompts (Week 1)

1. Create `backend/prompts/` directory structure
2. Extract `ARCHITECT_SYSTEM_PROMPT` → `prompts/modes/architect.md`
3. Extract `VOICE_CALIBRATION_SYSTEM_PROMPT` → `prompts/modes/voice_calibration.md`
4. Extract `DIRECTOR_SYSTEM_PROMPT` → `prompts/modes/director.md`
5. Create `prompts/identity.md` (factor out common elements)
6. Create `prompts/process_map.md` (mode overview)
7. Create `prompts/protocols.md` (output format rules)

**Validation**: Foreman behavior unchanged, prompts load from files.

### Phase 2: Implement State XML (Week 2)

1. Create `SessionStateGenerator` class
2. Define XML schema
3. Implement `_generate_session_state()` method
4. Add state injection to prompt assembly
5. Add unit tests for state generation

**Validation**: State XML appears in assembled prompts, correct structure.

### Phase 3: Implement Output Parsing (Week 2-3)

1. Create `ResponseParser` class
2. Implement XML parsing with fallbacks
3. Update action execution to use parsed actions
4. Add tests for various response formats
5. Add graceful degradation for malformed responses

**Validation**: Actions execute correctly from XML format.

### Phase 4: Create PromptAssembler (Week 3)

1. Implement full `PromptAssembler` service
2. Add model capability matrix
3. Implement tier-based assembly
4. Add model-specific adaptations
5. Integrate with Foreman

**Validation**: Different models receive appropriately sized prompts.

### Phase 5: Convert Actions to XML (Week 4)

1. Update mode prompt files with XML action format
2. Update documentation with new format
3. Update action parsers to handle XML
4. Run integration tests across all models

**Validation**: Full end-to-end flow works with XML actions.

### Phase 6: Testing & Polish (Week 4-5)

1. Test with all supported models
2. Tune XML reinforcement for low-reliability models
3. Optimize context budgets
4. Document final architecture

---

## 14. Appendices

### Appendix A: File Structure

```
backend/
├── prompts/
│   ├── identity.md                   # Core Foreman persona (~500 tokens)
│   ├── process_map.md                # All modes overview (~1000 tokens)
│   ├── protocols.md                  # Output format rules (~800 tokens)
│   ├── modes/
│   │   ├── architect.md              # ARCHITECT detailed rules (~800 tokens)
│   │   ├── voice_calibration.md      # VOICE_CALIBRATION rules (~600 tokens)
│   │   ├── director.md               # DIRECTOR rules (~700 tokens)
│   │   └── editor.md                 # EDITOR rules (~600 tokens)
│   └── guardrails/
│       ├── voice_antipatterns.md     # Zero-tolerance patterns
│       └── continuity_rules.md       # What to check
├── services/
│   ├── prompt_assembler.py           # Context Sandwich assembly
│   ├── response_parser.py            # XML response parsing
│   └── model_capabilities.py         # Model capability matrix (existing)
└── agents/
    └── foreman.py                    # Updated to use assembler
```

### Appendix B: Token Budget Reference

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

### Appendix C: Supported Models

| Model | Provider | Context | Tier | XML Reliability |
|-------|----------|---------|------|-----------------|
| gpt-4o | OpenAI | 128K | full | high |
| gpt-4o-mini | OpenAI | 128K | full | high |
| claude-sonnet-4 | Anthropic | 200K | full | very_high |
| claude-opus-4 | Anthropic | 200K | full | very_high |
| gemini-2.0-flash | Google | 1M | full | medium |
| grok-2 | xAI | 131K | full | high |
| deepseek-chat | DeepSeek | 64K | medium | medium |
| qwen-plus | Alibaba | 131K | medium | medium |
| qwen-max | Alibaba | 32K | medium | medium |
| mistral-large | Mistral | 128K | full | high |
| llama3.2:3b | Ollama | 8K | minimal | low |
| mistral:7b | Ollama | 32K | medium | medium |

### Appendix D: Example Assembled Prompt

**For GPT-4o in ARCHITECT mode:**

```markdown
# THE FOREMAN

## Core Identity

You are **The Foreman**, the central AI collaborator in Writers Factory...

[... identity.md content ...]

---

# THE WRITING PROCESS MAP

You must determine which MODE the writer is currently in...

## MODE A: ARCHITECT
[... full mode descriptions ...]

---

# MODE: ARCHITECT - Detailed Instructions

## Your Focus in This Mode

Build the structural foundation...

[... modes/architect.md content ...]

---

<session_state>
  <current_mode>ARCHITECT</current_mode>
  <completion_pct>45</completion_pct>
  <project>
    <title>The Last Starship</title>
    <protagonist>Elena Vance</protagonist>
  </project>
  <work_order>
    <template name="Protagonist" status="in_progress" missing="arc_resolution"/>
    <template name="Beat Sheet" status="not_started"/>
    <template name="Theme" status="complete"/>
    <template name="World Rules" status="not_started"/>
  </work_order>
  <knowledge_context>
    <entry category="character" key="elena_fatal_flaw">
      Inability to trust, stemming from father's abandonment
    </entry>
  </knowledge_context>
</session_state>

---

# OUTPUT PROTOCOLS

Your responses are parsed by the Writers Factory application...

[... protocols.md content ...]

---

## CONVERSATION HISTORY

USER: I want to work on Elena's character arc

ASSISTANT: <thinking>User wants to develop protagonist arc. Current status shows arc_resolution is missing.</thinking>

<message>Let's complete Elena's arc. You've established her fatal flaw (inability to trust) and The Lie (she can only rely on herself).

**The key question**: At the story's end, does Elena learn to trust? Or does she find success without trusting?

Both are valid arcs:
1. **Positive arc**: Elena learns selective trust, opening herself to connection
2. **Negative arc**: Elena's distrust is validated, she succeeds alone but at emotional cost
3. **Flat arc**: Elena was right all along, the world catches up to her truth

Which resonates with your vision?</message>

---

## CURRENT MESSAGE

User: I think she learns to trust, but only specific people - not everyone
```

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | Dec 2025 | Initial draft |

---

*End of Document*
