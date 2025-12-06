---
layout: default
title: The 5 Core Notebooks
protected: true
---

<script>
if (!sessionStorage.getItem('authenticated')) {
    window.location.href = "/portal/";
}
</script>

# The 5 Core Notebooks

> Writers Factory accepts exactly 5 structured notebooks. No more, no less.

## Why Only 5?

Writers Factory's AI agents need structured input to function. The Foreman queries specific categories. If you have 50 messy notebooks, the AI drowns in noise.

The 5 Core Notebooks are your **API contract** with the Factory.

---

## The Distillation Pipeline

Before registering notebooks, understand the 3-stage pipeline:

| Stage | What It Is | Where It Lives |
|-------|-----------|----------------|
| **Stage 1** | Raw brainstorming - podcasts, articles, "vibes" | Your private NotebookLM notebooks (NOT registered) |
| **Stage 2** | Distilled, structured data | Your 5 Core Notebooks (registered in Writers Factory) |
| **Stage 3** | Canonical Story Bible | `content/` directory in Writers Factory |

**The Factory only sees Stage 2 and 3.** Stage 1 is your private creative chaos.

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

**Critical**: Clearly label which rules are HARD (immutable). The AI uses these for conflict detection.

---

### 3. THEME (One Notebook for ALL Philosophy)

**DO**: Put ALL thematic ideas in ONE notebook
**DON'T**: Create separate notebooks per theme

**Why together?**
The AI needs conflicting ideas to find the central argument:
- Thesis vs Counter-thesis
- The story's philosophical debate

**What to include**:
- Central Question (phrased as a question, e.g., "Can redemption exist without sacrifice?")
- Arguments FOR (thesis)
- Arguments AGAINST (counter-thesis)
- Symbols and their meanings
- How protagonist embodies the theme

**Key**: Frame theme as a **question**, not a statement. "Honesty matters" is weak. "Can authenticity survive in a world of masks?" creates story.

---

### 4. PLOT (One Notebook for Structure)

**What to include**:
- 15-beat structure (Save the Cat format)
- Midpoint type (False Victory / False Defeat)
- Scene ideas
- Subplot outlines

**Required beats** (at minimum):
- Catalyst (inciting incident)
- Midpoint (false victory or false defeat)
- All Is Lost (lowest point)
- Finale (climax)

---

### 5. VOICE (One Notebook for Style)

**What to include**:
- Passages from authors you admire
- Dialogue patterns to emulate
- Rhythms to match
- Anti-patterns to AVOID (clichés, forbidden phrases)

**Special case**: Voice doesn't produce a Story Bible file. It triggers Voice Calibration - the tournament system that tunes AI writing to match your style.

---

## Setting Up Your 5 Core Notebooks

### Step 1: Organize Your Raw Research

Go through your existing NotebookLM notebooks. Sort content into 5 mental buckets:
- Is this about characters? → goes to CHARACTER distillation
- Is this about the world? → goes to WORLD distillation
- Is this about theme? → goes to THEME distillation
- Is this about structure? → goes to PLOT distillation
- Is this about style? → goes to VOICE distillation

### Step 2: Create 5 New NotebookLM Notebooks

In NotebookLM (notebooklm.google.com):
1. Create: "Novel Name - Characters"
2. Create: "Novel Name - World"
3. Create: "Novel Name - Theme"
4. Create: "Novel Name - Plot"
5. Create: "Novel Name - Voice"

### Step 3: Distill Into Each Notebook

Use the [Distillation Prompts](./DISTILLATION_PROMPTS.md) to transform raw research into structured notes.

For each raw notebook:
1. Open it in NotebookLM
2. Copy the relevant Distillation Prompt
3. Paste and run
4. Copy the output to the appropriate Core Notebook

### Step 4: Register in Writers Factory

1. Open Writers Factory
2. Click NOTEBOOK button (top-right toolbar)
3. Paste NotebookLM URL or ID
4. Assign correct category

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| One notebook per character | AI can't see relationships | Combine into ONE Character notebook |
| Mixing Stage 1 and Stage 2 | AI gets noise with signal | Keep raw research separate from distilled notebooks |
| No Hard Rules labeled | AI can't enforce world consistency | Explicitly mark which rules are immutable |
| Generic theme | AI can't find conflict | Frame theme as a QUESTION with opposing sides |
| Registering raw notebooks | Extraction fails constantly | Distill first, then register |

---

## Graceful Failure

If the Foreman can't find structured data in your notebook, it will:
1. **NOT hallucinate** - won't make up a Fatal Flaw
2. **Diagnose** - explain what's missing
3. **Offer help** - provide the specific Distillation Prompt to run

This is the system working correctly. It's asking you to distill before it can extract.

---

## The Flow

```
Stage 1 (Raw)              Stage 2 (Core)            Stage 3 (Bible)
-------------              -------------             ---------------
Podcast notes    →  Character Notebook  → Protagonist.md
Random ideas     →  World Notebook      → Rules.md
Vibes notebook   →  Theme Notebook      → Theme.md
Book highlights  →  Plot Notebook       → Beat_Sheet.md
Style refs       →  Voice Notebook      → Voice Bundle

     [Distillation]         [The Foreman]
```

---

*Created for Writers Factory Distillation Pipeline*
