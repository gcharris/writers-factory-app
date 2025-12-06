---
layout: default
title: Distillation Prompts

---


# Distillation Prompts Library

> Use these prompts in NotebookLM to transform raw research into structured Core Notebooks.

## How to Use

1. Open your Stage 1 (raw) NotebookLM notebook
2. Copy a prompt below
3. Paste into NotebookLM chat
4. Save the output to your Core Notebook

---

## CHARACTER DISTILLATION

Copy this prompt to transform character research into structured data:

```
Based on these sources, create a character profile with:

- **Character Type**: protagonist | antagonist | supporting
- **Fatal Flaw**: An internal weakness (NOT a circumstance like "is poor")
- **The Lie**: A mistaken belief driving the flaw
- **True Character**: Who they become after the arc
- **Arc**:
  - Starting state (who they are at the beginning)
  - Midpoint crisis (what breaks them)
  - Resolution (how they transform)
- **Key Relationships**: List other characters and their relationship

Format the output with clear headers.
```

---

## WORLD DISTILLATION

Copy this prompt to extract world rules:

```
From these sources, extract:

**HARD RULES** (Cannot be broken - physics, magic limits, society laws):
1. [Rule]
2. [Rule]
3. [Rule]
(List at least 3)

**LOCATIONS** (Key places with plot significance):
- [Location]: [Why it matters]

**SECRETS** (What the reader/characters don't know yet):
- [Secret]

**SYSTEM INTERACTIONS** (How different systems affect each other):
- How does [magic/technology] interact with [politics/society]?

Clearly separate Hard Rules from background lore.
```

---

## THEME DISTILLATION

Copy this prompt to crystallize your theme:

```
Looking at these sources, define:

**CENTRAL QUESTION** (Phrase as a question):
"Can [thesis] exist despite [counter-thesis]?"

**THESIS** (The argument FOR):
[What the story argues is true]

**COUNTER-THESIS** (The argument AGAINST):
[The valid opposing view - this is NOT the villain's view, but a legitimate challenge]

**SYMBOLS**:
- [Symbol 1]: Represents [meaning]
- [Symbol 2]: Represents [meaning]

**PROTAGONIST EMBODIMENT**:
How does the protagonist's arc embody this thematic question?
```

---

## PLOT DISTILLATION

Copy this prompt to map your story structure:

```
Map this story to the 15-beat Save the Cat structure:

1. **Opening Image** (1%): The "before" snapshot
2. **Theme Stated** (5%): Theme hinted in dialogue
3. **Setup** (1-10%): Ordinary world
4. **Catalyst** (10%): Inciting incident
5. **Debate** (10-20%): Protagonist hesitates
6. **Break into Two** (20%): Commits to journey
7. **B Story** (22%): Subplot begins (usually relationship)
8. **Fun & Games** (20-50%): Promise of the premise
9. **Midpoint** (50%): FALSE VICTORY or FALSE DEFEAT?
10. **Bad Guys Close In** (50-75%): Opposition tightens
11. **All Is Lost** (75%): Lowest point
12. **Dark Night of the Soul** (75-80%): Despair
13. **Break into Three** (80%): Solution discovered
14. **Finale** (80-99%): Final confrontation
15. **Final Image** (99-100%): Mirror of opening

**MIDPOINT TYPE**: Is this a FALSE VICTORY (things seem good, then collapse) or FALSE DEFEAT (things seem bad, then turn around)?
```

---

## VOICE DISTILLATION

Copy this prompt to analyze prose style:

```
Analyze these passages and describe:

**SENTENCE RHYTHM**:
- Short and punchy? Long and flowing?
- Variation patterns?

**METAPHOR DOMAINS**:
- Where do metaphors come from? (nature, machinery, sports, music, warfare?)
- Are similes used or avoided?

**DIALOGUE PATTERNS**:
- Terse or verbose?
- Subtext-heavy or direct?
- Distinct voices per character?

**ANTI-PATTERNS** (What to AVOID):
- Clichés to never use
- Rhythms that feel wrong
- Words that break the voice
```

---

## Why These Prompts?

These prompts are designed to produce output that Writers Factory can **extract**. The AI looks for specific markers:

| Category | Key Markers | What AI Extracts |
|----------|-------------|------------------|
| Characters | "Fatal Flaw", "The Lie", "Arc" | Protagonist.md fields |
| World | "Hard Rule", "Cannot be broken" | Rules.md, conflict checking |
| Theme | "Central Question", "Thesis" | Theme.md structure |
| Plot | Beat names, "Midpoint" | Beat_Sheet.md |
| Voice | "Rhythm", "Anti-pattern" | Voice Calibration inputs |

Without these markers, the AI can't find what it needs and will ask you to distill.

---

## Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| Vague flaw like "is poor" | AI rejects as circumstance, not flaw | Use internal weakness like "need for control" |
| Theme as statement | Can't generate conflict | Frame as question: "Can X exist despite Y?" |
| Missing midpoint type | AI can't calibrate second act | State FALSE VICTORY or FALSE DEFEAT |
| No Hard Rules labeled | Can't enforce world consistency | Explicitly mark immutable rules |

---

*Created for Writers Factory Distillation Pipeline*
