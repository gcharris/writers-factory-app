# The Writer's Pre-Flight Manual

## You Are the Context Engineer

Writers Factory is a professional novel-writing IDE. It operates on one principle: **Structure Before Freedom**.

AI models are Amnesiac Geniuses—they've read every book ever written but can't remember what they wrote three pages ago. To fix this, Writers Factory uses a Knowledge Graph that remembers your story. But that brain is only as good as the information you feed it.

**Do not enter the Factory with a blank page. Do not connect 50 hours of raw podcast transcripts. You must first distill your inspiration into 5 Core Notebooks.**

------

## The 3-Stage Pipeline

| Stage              | What It Is                           | Where It Lives                                     |
| :----------------- | :----------------------------------- | :------------------------------------------------- |
| **Stage 1: Raw**   | Messy brainstorming, podcasts, vibes | Your private NotebookLM notebooks (NOT registered) |
| **Stage 2: Core**  | Distilled, structured data           | 5 Core Notebooks (registered in Writers Factory)   |
| **Stage 3: Bible** | Canonical Story Bible                | Built by The Foreman inside Writers Factory        |

The Factory only sees Stage 2 and 3. Stage 1 is your private creative chaos.

------

## Phase 1: The Raw Gather

**Tool**: Google NotebookLM (notebooklm.google.com)

Create as many "Stage 1" notebooks as you want:

- **Inspiration notebooks**: Research PDFs, YouTube transcripts, articles
- **Vibes notebooks**: Character inspirations, "what if" scenarios
- **Style notebooks**: Passages from authors you admire

**No rules here.** Hoard freely. These notebooks will NOT be connected to Writers Factory.

------

## Phase 2: The Distillation (Creating the 5 Core Notebooks)

**Tool**: Google NotebookLM (using Distillation Prompts)

Now create exactly **5 new notebooks** in NotebookLM—one for each category. Use the prompts below to transform your raw Stage 1 notes into structured Stage 2 content.

### Notebook 1: CHARACTER

**Why one notebook for ALL characters?** The AI needs to see Protagonist vs Antagonist together to detect if their goals properly conflict.

**Distillation Prompt** (copy into NotebookLM chat with your raw notes as sources):

```
Based on these sources, create character profiles with:

For each major character:
- Character Type: protagonist | antagonist | supporting
- Fatal Flaw: An internal weakness (NOT a circumstance like "is poor")
- The Lie: A mistaken belief driving the flaw
- Arc: starting state → midpoint crisis → resolution
- Key relationships to other characters

Clearly label who is the PROTAGONIST.
```

### Notebook 2: WORLD

**Why one notebook for ALL world-building?** The AI needs to see how systems interact—does magic conflict with politics? Are there logic errors?

**Distillation Prompt**:

```
From these sources, extract:

HARD RULES (Cannot be broken - physics, magic limits, society laws):
1. [Rule]
2. [Rule]
3. [Rule]

LOCATIONS (Key places with plot significance):
- [Location]: [Why it matters]

SYSTEM INTERACTIONS:
- How does [magic/technology] interact with [politics/society]?

Clearly separate Hard Rules from background lore.
```

### Notebook 3: THEME

**Why frame as a question?** A statement like "honesty matters" is weak. A question like "Can authenticity survive in a world of masks?" creates story.

**Distillation Prompt**:

```
Looking at these sources, define:

CENTRAL QUESTION (phrase as a question):
"Can [thesis] exist despite [counter-thesis]?"

THESIS (argument FOR):
[What the story argues is true]

COUNTER-THESIS (argument AGAINST):
[The valid opposing view - not just the villain's view, but a legitimate challenge]

SYMBOLS:
- [Symbol]: Represents [meaning]

How does the protagonist's arc embody this question?
```

### Notebook 4: PLOT

**Distillation Prompt**:

```
Map this story to the 15-beat Save the Cat structure:

1. Opening Image (1%)
2. Theme Stated (5%)
3. Setup (1-10%)
4. Catalyst (10%)
5. Debate (10-20%)
6. Break into Two (20%)
7. B Story (22%)
8. Fun & Games (20-50%)
9. Midpoint (50%) - Is this FALSE VICTORY or FALSE DEFEAT?
10. Bad Guys Close In (50-75%)
11. All Is Lost (75%)
12. Dark Night of the Soul (75-80%)
13. Break into Three (80%)
14. Finale (80-99%)
15. Final Image (99-100%)

State the MIDPOINT TYPE clearly.
```

### Notebook 5: VOICE

**This one is different.** It doesn't produce a Story Bible file—it trains the Voice Calibration system.

**What to include**:

- Passages from authors you want to emulate
- Your own writing samples (if available)
- Dialogue patterns to match
- **Anti-patterns**: What to AVOID (clichés, rhythms you hate, forbidden words)

------

## Phase 3: The Handoff (Entering the Factory)

**Tool**: Writers Factory Desktop App

### Step 1: Launch and Register

1. Open Writers Factory
2. Click the **NOTEBOOK** button (top-right toolbar)
3. For each of your 5 Core Notebooks:
   - Paste the NotebookLM URL or ID
   - Select the matching category (Character, World, Theme, Plot, Voice)
   - Click Register

### Step 2: Enter ARCHITECT Mode

1. The Foreman (your AI partner) starts in ARCHITECT mode
2. It will query your registered notebooks to understand your story
3. Through conversation, it builds your Story Bible:
   - Protagonist.md (from Character notebook)
   - Rules.md (from World notebook)
   - Theme.md (from Theme notebook)
   - Beat_Sheet.md (from Plot notebook)

### Step 3: Voice Calibration (When Ready)

After Story Bible is complete:

1. Transition to VOICE mode
2. The system runs a "tournament" where multiple AI models compete to match your voice
3. The winner becomes your Voice Bundle

------

## Pre-Flight Checklist

Before clicking "Register Notebook," verify each Core Notebook has:

| Notebook  | Required Markers                                      |
| :-------- | :---------------------------------------------------- |
| Character | "Fatal Flaw" and "The Lie" explicitly stated          |
| World     | At least 3 "Hard Rules" clearly labeled               |
| Theme     | Central Question phrased as a question                |
| Plot      | Midpoint labeled as "False Victory" or "False Defeat" |
| Voice     | Anti-patterns listed (what to avoid)                  |

**If the Foreman can't find these markers, it will ask you to distill further. This is the system working correctly—it's asking for structure, not inventing answers.**

------

## What NOT to Do

| Mistake                           | Why It Fails                            |
| :-------------------------------- | :-------------------------------------- |
| Register raw Stage 1 notebooks    | AI drowns in noise, extraction fails    |
| Create one notebook per character | AI can't see relationships              |
| Skip the distillation prompts     | Missing markers = Foreman can't extract |
| Rush to DIRECTOR mode             | Story Bible incomplete = plot holes     |

------

*"The Factory doesn't write the story for you. It builds the Iron Man suit. You have to bring the pilot."*