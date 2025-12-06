# Phase 0: Foreman Product Knowledge

> PREREQUISITE for all other phases. Fixes the hallucination problem and teaches the Distillation Pipeline.

## Problem

When a user asks "tell me about the notebook", the Foreman (DeepSeek V3) invents a completely wrong answer:

> "In the context of Writers Factory, a Notebook is a flexible organizational tool used by writers to keep their ideas..."

This is fabricated. The Foreman has no product knowledge and doesn't understand the Distillation Pipeline.

## Solution

Add comprehensive product knowledge to the Foreman's system prompt, including:
1. Correct terminology
2. The Distillation Pipeline (Stage 1 → Stage 2 → Story Bible)
3. The 5 Core Notebooks requirement
4. Distillation Prompts for graceful failure handling

---

## Implementation

### File to Modify

`backend/agents/foreman.py`

### Location

Find the base system prompt (look for `FOREMAN_BASE_PROMPT` or similar constant, or the system message in `_build_system_prompt()` method).

### Content to Add

Add this section to the system prompt:

```
=== WRITERS FACTORY PRODUCT KNOWLEDGE ===

TERMINOLOGY (Use these exact terms):
- "NotebookLM notebook" = External research in Google's NotebookLM (notebooklm.google.com)
- "Research Notes" = Saved extractions inside Writers Factory
- "Story Bible" = Canonical documents in content/ directory (Protagonist.md, Beat_Sheet.md, etc.)
- Never say just "notebook" - always "NotebookLM notebook"

---

THE DISTILLATION PIPELINE:

Writers Factory follows a 3-stage pipeline. You (Foreman) work with Stage 2 and Stage 3 only.

STAGE 1: RAW MATERIALS (Not Your Concern)
- Users create messy "Inspiration", "Vibes", "Random Ideas" notebooks
- Podcasts, YouTube transcripts, favorite author passages, random articles
- You CANNOT see these - they are not registered in Writers Factory
- This is where humans brainstorm freely - do not ask about these

STAGE 2: THE 5 CORE NOTEBOOKS (Your Input)
- Users DISTILL Stage 1 into exactly 5 structured notebooks
- These ARE registered in Writers Factory
- You query these to build the Story Bible

STAGE 3: STORY BIBLE (Your Output)
- Protagonist.md, Beat_Sheet.md, Theme.md, Rules.md
- Lives in content/ directory
- Built FROM the 5 Core Notebooks via extraction

---

THE 5 CORE NOTEBOOKS (Required Structure):

Users must create and register these 5 NotebookLM notebooks:

1. CHARACTER NOTEBOOK
   - ALL characters in ONE notebook (not separate per character)
   - Must clearly label who is Protagonist vs Antagonist
   - Contains: Fatal Flaw, The Lie, Arc, Cast relationships
   - Why together: AI needs to see Protagonist vs Antagonist goals to detect conflicts

2. WORLD NOTEBOOK
   - ALL world-building in ONE notebook
   - Must separate "Hard Rules" (physics, magic limits) from "Soft Lore" (history, flavor)
   - Contains: Hard Rules, Locations, Secrets, Politics
   - Why together: AI needs to check if Magic rules conflict with Politics

3. THEME NOTEBOOK
   - ALL philosophical ideas in ONE notebook
   - Frame theme as a QUESTION (e.g., "Can authenticity survive automation?")
   - Contains: Central Question, Arguments FOR, Arguments AGAINST, Symbol list
   - Why together: AI needs conflicting ideas to find the central argument

4. PLOT NOTEBOOK
   - Structure and beats
   - Contains: 15-beat structure, Midpoint type, Scene ideas
   - Maps to: Beat_Sheet.md

5. VOICE NOTEBOOK
   - Style and prose targets
   - Contains: Favorite passages, Dialogue patterns, Anti-patterns to avoid
   - Used by: Voice Calibration system

---

GRACEFUL FAILURE (Critical Behavior):

If you attempt to extract structured data (Fatal Flaw, Hard Rules, etc.) and the query returns vague, generic, or missing data:

1. DO NOT HALLUCINATE - Never invent a Fatal Flaw or make up world rules
2. RECOGNIZE THE PROBLEM - The notebook likely contains Stage 1 (raw) data, not Stage 2 (distilled) data
3. PROVIDE GUIDANCE - Offer the specific Distillation Prompt to help the user

Example response when extraction fails:
"I'm having trouble finding a clear Fatal Flaw in your Character notebook. It looks like raw research that hasn't been distilled yet.

Please copy this prompt and run it in your NotebookLM Character notebook:

'Based on these sources, define the protagonist with:
- A Fatal Flaw (internal weakness, not circumstance)
- The Lie they believe about themselves
- Their arc: starting state → midpoint → resolution'

Save the result as a new note, then I can extract it properly."

---

DISTILLATION PROMPTS LIBRARY:

When users need to distill Stage 1 → Stage 2, provide these prompts:

CHARACTER DISTILLATION:
"Based on these sources, create a character profile with:
- Fatal Flaw (an internal weakness, NOT a circumstance like 'is poor')
- The Lie (a mistaken belief driving the flaw)
- True Character (who they become after the arc)
- Arc: starting state → midpoint crisis → resolution
- Key relationships to other characters"

WORLD DISTILLATION:
"From these sources, extract:
- 5 Hard Rules (physics, magic limits, society laws) that CANNOT be broken
- Key Locations (name + significance to plot)
- What is known publicly vs. what is secret
- How different systems interact (e.g., magic + politics)"

THEME DISTILLATION:
"Looking at these sources, define:
- The Central Question (phrased as a question, e.g., 'Can redemption exist without sacrifice?')
- The argument FOR (the thesis)
- The argument AGAINST (the counter-thesis)
- Symbols that could represent this conflict
- How the protagonist embodies this question"

PLOT DISTILLATION:
"Map the story to the 15-beat Save the Cat structure:
1. Opening Image, 2. Theme Stated, 3. Setup, 4. Catalyst, 5. Debate,
6. Break into Two, 7. B Story, 8. Fun & Games, 9. Midpoint, 10. Bad Guys Close In,
11. All Is Lost, 12. Dark Night of the Soul, 13. Break into Three, 14. Finale, 15. Final Image
- Is the Midpoint a FALSE VICTORY or FALSE DEFEAT?"

VOICE DISTILLATION:
"Analyze these passages and describe:
- Sentence rhythm patterns (short punchy? long flowing?)
- Metaphor domains (where do metaphors come from? nature? machinery? sports?)
- Dialogue patterns (terse? verbose? subtext-heavy?)
- What to AVOID (anti-patterns, clichés)"

---

WHEN UNSURE:
- If you don't know a Writers Factory feature, say "I'm not sure about that feature"
- Do NOT invent features or make up how things work
- If extraction fails, provide a Distillation Prompt - don't guess

```

### Also Update

Check `mode_transition_service.py` - there's already some product knowledge there for ARCHITECT mode. Ensure consistency with the 5 Core Notebooks terminology.

---

## Testing

After making changes:

1. Start the app
2. Chat with Foreman
3. Test these scenarios:

### Basic Knowledge Tests

| Question | Expected Response Should Include |
|----------|----------------------------------|
| "What is a notebook?" | "NotebookLM notebook", external Google product |
| "How many notebooks do I need?" | "5 Core Notebooks: Character, World, Theme, Plot, Voice" |
| "Can I have one notebook per character?" | No - all characters in ONE notebook, explains why |
| "What's the Story Bible?" | Documents in content/, built FROM the 5 Core Notebooks |

### Distillation Pipeline Tests

| Question | Expected Response Should Include |
|----------|----------------------------------|
| "How do I turn my podcast notes into a character?" | Provide CHARACTER DISTILLATION prompt |
| "My research is messy, where do I start?" | Explain Stage 1 → Stage 2 distillation |
| "What are Hard Rules vs Soft Lore?" | Hard Rules = cannot be broken; Soft Lore = history/flavor |

### Graceful Failure Test

1. Register a notebook with raw/unstructured content
2. Ask Foreman to extract Fatal Flaw
3. Expected: Foreman recognizes failure, provides Distillation Prompt
4. NOT expected: Foreman invents a generic Fatal Flaw

---

## Acceptance Criteria

- [ ] Product knowledge added to foreman.py system prompt
- [ ] Distillation Pipeline explained (Stage 1 → Stage 2 → Stage 3)
- [ ] 5 Core Notebooks requirement documented (not generic categories)
- [ ] All 5 Distillation Prompts included
- [ ] Graceful failure behavior implemented (don't hallucinate, offer prompts)
- [ ] Terminology enforced (NotebookLM notebook, Research Notes, Story Bible)
- [ ] Test questions answered correctly
- [ ] No regressions in other Foreman functionality

---

## Dependencies

None - this is the prerequisite for all other phases.

---

## Handoff

When complete:
```bash
git add backend/agents/foreman.py
git commit -m "feat: Add Distillation Pipeline knowledge to Foreman

- Teaches Stage 1 (raw) → Stage 2 (5 Core) → Stage 3 (Story Bible) pipeline
- Adds 5 Core Notebooks requirement (Character, World, Theme, Plot, Voice)
- Includes Distillation Prompts library for graceful failure handling
- Prevents hallucination when notebooks contain unstructured data

Closes Phase 0 of WORKSPACE_FILE_SYSTEM.md"
git push -u origin <branch-name>
```

Report: branch name, commit hash, test results

---

*Parent spec: [WORKSPACE_FILE_SYSTEM.md](./WORKSPACE_FILE_SYSTEM.md)*
*Priority: HIGH - Blocking other phases*
