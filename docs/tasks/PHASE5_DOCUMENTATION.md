# Phase 5: Documentation

> In-app guidance for the Distillation Pipeline, 5 Core Notebooks, and workflow.

## The Key Educational Mission

Writers Factory is an **extraction tool, not a generation tool**. Documentation must teach:

1. **Stage 1**: Raw brainstorming (messy, unlimited notebooks)
2. **Stage 2**: Distillation into 5 Core Notebooks (structured)
3. **Stage 3**: Story Bible extraction (via Foreman)

---

## Deliverables

### 1. Distillation Prompts Library (CRITICAL)

**Location**: `docs/DISTILLATION_PROMPTS.md` + accessible in-app

**Purpose**: Give users copy-paste prompts to run in NotebookLM to distill Stage 1 → Stage 2.

**Content**:

```markdown
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

"""
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
"""

---

## WORLD DISTILLATION

Copy this prompt to extract world rules:

"""
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
"""

---

## THEME DISTILLATION

Copy this prompt to crystallize your theme:

"""
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
"""

---

## PLOT DISTILLATION

Copy this prompt to map your story structure:

"""
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
"""

---

## VOICE DISTILLATION

Copy this prompt to analyze prose style:

"""
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
"""
```

---

### 2. The 5 Core Notebooks Guide

**Location**: `docs/FIVE_CORE_NOTEBOOKS.md` + in-app onboarding

**Content**:

```markdown
# The 5 Core Notebooks

> Writers Factory accepts exactly 5 structured notebooks. No more, no less.

## Why Only 5?

Writers Factory's AI agents need structured input to function. The SmartScaffoldWorkflow queries specific categories. If you have 50 messy notebooks, the AI drowns in noise.

The 5 Core Notebooks are your **API contract** with the Factory.

---

## The 5 Notebooks

### 1. CHARACTER (One Notebook for ALL Characters)

**DO**: Put ALL characters in ONE notebook
**DON'T**: Create separate notebooks per character

**Why together?**
The AI needs to see Protagonist vs Antagonist in the same context to:
- Detect if their goals properly conflict
- Understand the cast hierarchy
- Map relationships

**What to include**:
- Protagonist profile (Fatal Flaw, The Lie, Arc)
- Antagonist profile (Motivation, Goal)
- Supporting cast list
- Relationship map

**Label clearly**: The AI specifically looks for "Fatal Flaw" and "The Lie" markers.

---

### 2. WORLD (One Notebook for ALL World-Building)

**DO**: Put ALL world aspects in ONE notebook
**DON'T**: Create separate notebooks for "Magic" vs "Politics"

**Why together?**
The AI needs to see how systems interact:
- Does magic conflict with politics?
- Are there logic errors? (If magic is rare, why is every leader a wizard?)

**What to include**:
- **Hard Rules**: Physics, magic limits - CANNOT be broken
- **Soft Lore**: History, culture - can flex
- **Locations**: Key places with significance
- **Secrets**: What's hidden from readers/characters

**Critical**: Clearly label which rules are HARD (immutable).

---

### 3. THEME (One Notebook for ALL Philosophy)

**DO**: Put ALL thematic ideas in ONE notebook
**DON'T**: Create separate notebooks per theme

**Why together?**
The AI needs conflicting ideas to find the central argument:
- Thesis vs Counter-thesis
- The story's philosophical debate

**What to include**:
- Central Question (phrased as a question)
- Arguments FOR (thesis)
- Arguments AGAINST (counter-thesis)
- Symbols and their meanings
- How protagonist embodies the theme

---

### 4. PLOT (One Notebook for Structure)

**What to include**:
- 15-beat structure (Save the Cat)
- Midpoint type (False Victory / False Defeat)
- Scene ideas
- Subplot outlines

---

### 5. VOICE (One Notebook for Style)

**What to include**:
- Passages from authors you admire
- Dialogue patterns to emulate
- Rhythms to match
- Anti-patterns to AVOID

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| One notebook per character | AI can't see relationships | Combine into ONE Character notebook |
| Mixing Stage 1 and Stage 2 | AI gets noise with signal | Keep raw research separate from distilled notebooks |
| No Hard Rules labeled | AI can't enforce world consistency | Explicitly mark which rules are immutable |
| Generic theme | AI can't find conflict | Frame theme as a QUESTION with opposing sides |
```

---

### 3. In-App Onboarding (Updated)

**Location**: Show when user first opens NotebookLM Panel with no notebooks registered.

**Content**:

```svelte
{#if notebooks.length === 0 && !dismissedOnboarding}
<div class="onboarding-card">
    <h2>Connect Your 5 Core Notebooks</h2>

    <p>Writers Factory needs exactly 5 structured NotebookLM notebooks:</p>

    <ol>
        <li><strong>Character</strong> - ALL characters in one notebook</li>
        <li><strong>World</strong> - ALL world-building in one notebook</li>
        <li><strong>Theme</strong> - ALL philosophical ideas in one notebook</li>
        <li><strong>Plot</strong> - Structure and beats</li>
        <li><strong>Voice</strong> - Style targets and samples</li>
    </ol>

    <div class="callout">
        <strong>First time?</strong> You'll need to "distill" your raw research first.
        <a href="#distillation">Get Distillation Prompts →</a>
    </div>

    <button on:click={showSetupGuide}>How to set up my notebooks</button>
    <button on:click={dismissOnboarding}>I've got my notebooks ready</button>
</div>
{/if}
```

### 4. Distillation Prompt Access in Foreman

When Foreman detects Stage 1 data or extraction failure, it should offer the relevant prompt:

```python
# In Foreman response when extraction fails
if extraction_failed and category == "characters":
    response += """

I couldn't find structured character data. Try running this Distillation Prompt in your NotebookLM:

---
Based on these sources, create a character profile with:
- Fatal Flaw (internal weakness, NOT circumstance)
- The Lie (mistaken belief driving the flaw)
- Arc: starting state → midpoint → resolution
---

Save the output, then I can extract it properly.
"""
```

### 5. Contextual Tooltips (Updated)

| Element | Tooltip |
|---------|---------|
| NOTEBOOK button | "Register your 5 Core NotebookLM notebooks (Character, World, Theme, Plot, Voice)" |
| Save to Research Notes | "Save to workspace/research/ for editing before Story Bible" |
| Category dropdown | "Must match one of your 5 Core Notebooks" |
| Promote button | "Move to Story Bible after Structure Check passes" |

---

## File Deliverables

| File | Content |
|------|---------|
| `docs/DISTILLATION_PROMPTS.md` | Copy-paste prompts for NotebookLM |
| `docs/FIVE_CORE_NOTEBOOKS.md` | Explanation of the 5 notebooks |
| `docs/WRITERS_JOURNEY.md` | Update with Distillation Pipeline |
| In-app onboarding component | Updated with 5 Core focus |

---

## Testing

1. Clear localStorage, open app
2. Go to NotebookLM Panel with no notebooks
3. Verify onboarding shows 5 Core Notebooks guidance
4. Click "Get Distillation Prompts" → verify prompts accessible
5. Register a notebook → verify category dropdown is strict (5 options)
6. Try to save extraction with raw Stage 1 data → verify Foreman offers distillation prompt
7. Check all tooltips reflect 5 Core terminology

---

## Acceptance Criteria

- [ ] `DISTILLATION_PROMPTS.md` created with all 5 category prompts
- [ ] `FIVE_CORE_NOTEBOOKS.md` created with setup guide
- [ ] In-app onboarding updated to emphasize 5 Core structure
- [ ] Foreman offers distillation prompts on extraction failure
- [ ] All documentation corrected (no more "one notebook per character")
- [ ] Tooltips reflect 5 Core terminology
- [ ] Help menu links to both guides

---

## Dependencies

- **Phase 0** (Foreman knows distillation prompts)
- **Phase 1** (5 category file structure exists)

---

## Handoff

When complete:
```bash
git add docs/ frontend/
git commit -m "docs: Add Distillation Pipeline and 5 Core Notebooks documentation

- DISTILLATION_PROMPTS.md with copy-paste prompts for NotebookLM
- FIVE_CORE_NOTEBOOKS.md with setup guide
- Updated in-app onboarding
- Foreman offers distillation prompts on failure
- Fixed 'one notebook per character' to 'all characters in one'

Closes Phase 5 of WORKSPACE_FILE_SYSTEM.md"
git push -u origin <branch-name>
```

Report: branch name, commit hash, test results

---

*Parent spec: [WORKSPACE_FILE_SYSTEM.md](./WORKSPACE_FILE_SYSTEM.md)*
*Priority: LOW - Polish (but critical for user education)*
