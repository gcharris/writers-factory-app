# The Writer's Journey: From Research to Polished Novel

**The Complete Creative Workflow in Writers Factory**

---

## The Core Truth

> **Writers Factory is an extraction tool, not a generation tool.**

The AI doesn't write your novel. It helps you extract the novel that already exists in your research, your notes, your head.

Without your source material, the AI produces generic content.
With your source material, the AI becomes a precision extraction engine.

---

## The Six Phases

```
RESEARCH → SETUP → ARCHITECT → VOICE → DIRECTOR → EDITOR
    │         │         │          │        │         │
    │         │         │          │        │         └─ Polish & ship
    │         │         │          │        └─ Scene drafting (scaffolds)
    │         │         │          └─ Voice tournament (find YOUR sound)
    │         │         └─ Story Bible (extract structure from research)
    │         └─ Install app + connect your notebooks
    └─ BUILD YOUR NOTEBOOKS FIRST (this is the real work)
```

---

## Phase 0: Research Foundation

> **This happens BEFORE you touch Writers Factory.**

### The Problem

Most people launch the app and start chatting. They improvise answers to the Foreman's questions. The result: a Story Bible built on whatever they happened to think of that moment.

### The Solution

Build your research library in NotebookLM **first**. When you start Writers Factory, every question the Foreman asks gets answered by querying *your* research, not generating guesses.

### What to Build

| Notebook | Contents | Why It Matters |
|----------|----------|----------------|
| **Characters** | Backstories, psychology, interviews with yourself about them | Grounds character decisions in deliberate thought |
| **World** | Setting, rules, factions, history | Prevents world-building contradictions |
| **Theme** | Essays on your central argument, counterarguments | Ensures thematic coherence |
| **Craft** | Passages from authors you admire, style analysis | Gives voice calibration real targets |
| **Plot** | Beat sheets, scene ideas, structure experiments | Speeds up ARCHITECT mode |

### The Test

Before proceeding, your notebooks should be able to answer:
- Who is my protagonist, and what drives them internally?
- What is the central theme I'm exploring?
- What are the immutable rules of my world?
- What does my ideal prose sound like?

If your notebooks can't answer these, add more material.

---

## Phase 1: Installation & Setup

### The Quick Version

1. Download Writers Factory
2. Run the Onboarding Wizard (workspace, Ollama, API keys, name your assistant)
3. Create a new project
4. **Immediately register your NotebookLM notebooks** (this is not optional)

### The Critical Step

After creating your project, click "NotebookLM" in the header and register each notebook you built in Phase 0. Assign roles:

- `character` - For protagonist/cast questions
- `world` - For setting/rules questions
- `theme` - For thematic exploration
- `craft` - For voice and style references
- `plot` - For structure questions

**Test each connection.** The Foreman is now grounded in your research.

---

## Phase 2: ARCHITECT Mode

> **Goal: Build your Story Bible by extracting from research.**

The Foreman guides you through four required templates:

| Template | What You Define | How NotebookLM Helps |
|----------|-----------------|---------------------|
| **Protagonist** | Fatal Flaw, The Lie, Character Arc | Queries character notebook for your notes |
| **Beat Sheet** | 15-beat structure, midpoint type | Queries plot notebook for your outlines |
| **Theme** | Central theme, theme statement | Queries theme notebook for your essays |
| **World Rules** | Immutable laws of your world | Queries world notebook for your world-building |

### The Difference

**Without NotebookLM:**
> Foreman: "What's your protagonist's fatal flaw?"
> You: "Uh... pride, I guess?"

**With NotebookLM:**
> Foreman: "What's your protagonist's fatal flaw?"
> *[Queries your character notebook]*
> Foreman: "Your notes describe Marcus as having 'a pathological need for control stemming from childhood abandonment.' Should we formalize this as his fatal flaw?"

### The Gate

You cannot advance until all four templates are complete. This is intentional. Structure before freedom.

---

## Phase 3: VOICE_CALIBRATION Mode

> **Goal: Find YOUR narrative voice through a tournament.**

### The Tournament

1. Write a test passage (~500 words) that exercises dialogue, action, interiority
2. Select 3+ AI models to compete
3. Each model generates variants in different styles
4. You compare, select favorites, provide feedback
5. System learns what "your voice" sounds like

### The Output

A **Voice Bundle** - a mathematical profile of your style that guides all future generation.

### Why Notebooks Matter Here

Your **craft notebook** (with passages from authors you admire) gives the tournament real targets. "Sound more like this" becomes precise, not vague.

---

## Phase 4: DIRECTOR Mode

> **Goal: Draft scenes using scaffolds and tournaments.**

### The Pipeline

```
Scaffold → Structure Variants → Scene Tournament → Enhancement → Analysis
```

1. **Scaffold**: AI generates a scene skeleton based on your beat sheet
2. **Structure Variants**: Multiple approaches (action-heavy, dialogue-heavy, etc.)
3. **Scene Tournament**: Models compete to draft the scene
4. **Enhancement**: 6-pass polish (pacing, voice, sensory, etc.)
5. **Analysis**: 100-point score with violation flagging

### The 100-Point Rubric

| Category | Points | What It Measures |
|----------|--------|------------------|
| Voice Authenticity | 30 | Does it sound like your voice bundle? |
| Character Consistency | 20 | Are characters acting in-character? |
| Metaphor Discipline | 20 | Fresh metaphors, no clichés? |
| Anti-Pattern Compliance | 15 | Avoiding banned patterns? |
| Phase Appropriateness | 15 | Right content for this story beat? |

### Why Notebooks Matter Here

Your **world notebook** prevents continuity errors. Your **character notebook** keeps psychology consistent. Your **craft notebook** guides enhancement choices.

---

## Phase 5: EDITOR Mode

> **Goal: Polish the complete manuscript.**

### Health Checks

The system runs diagnostics:
- **Pacing Analysis**: Tension curves across scenes
- **Voice Drift Detection**: Did your voice slip?
- **Continuity Validation**: Any world-rule violations?
- **Character Arc Tracking**: Is the arc landing?

### The Final Pass

You address flagged issues, run final health checks, and export your polished manuscript.

---

## The Philosophy

### Why This Order?

| Phase | Prevents |
|-------|----------|
| Research Foundation | Generic, ungrounded content |
| ARCHITECT | Structural collapse at 30,000 words |
| VOICE_CALIBRATION | Generic AI voice |
| DIRECTOR | Unfocused, meandering drafts |
| EDITOR | Shipping rough work |

Each phase is a gate. You cannot skip ahead. This is the Narrative Protocol.

### The Iron Man Suit

You are Tony Stark. Writers Factory is the suit.

The suit doesn't replace your judgment—it amplifies it. It doesn't write your novel—it extracts it from your research at superhuman speed.

**Your job:** Provide the vision, the research, the taste.
**The suit's job:** Query, generate, compare, refine—at scale.

---

## Quick Reference

### Key Endpoints (for Engineers)

| Phase | Key Endpoint |
|-------|--------------|
| Setup | `POST /foreman/start` |
| Notebooks | `POST /foreman/notebook` |
| Story Bible | `GET /story-bible/status` |
| Voice Tournament | `POST /voice-calibration/tournament/start` |
| Scene Generation | `POST /director/scaffold/generate` |
| Health Check | `GET /health/narrative-report` |

### Key Components (for Developers)

| Phase | Key Components |
|-------|---------------|
| Setup | `OnboardingWizard.svelte`, `NotebookLMPanel.svelte` |
| ARCHITECT | `ForemanPanel.svelte`, `StoryBibleWizard.svelte` |
| VOICE | `VoiceTournamentLauncher.svelte`, `VoiceVariantGrid.svelte` |
| DIRECTOR | `ScaffoldGenerator.svelte`, `SceneVariantGrid.svelte` |
| EDITOR | `HealthDashboard.svelte`, `ScoreDisplay.svelte` |

---

## Full Technical Documentation

This is the simplified course version. For complete technical details, testing checklists, and API references:

**[→ Full Writers Journey Documentation](WRITERS_JOURNEY.md)**

---

*Writers Factory: Engineering the Muse.*
