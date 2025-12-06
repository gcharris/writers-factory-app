---
layout: default
title: Pre-Flight Manual
protected: true
---

<script>
if (!sessionStorage.getItem('authenticated')) {
    window.location.href = "/portal/";
}
</script>

# Writers Factory Pre-Flight Manual

> Complete your research in NotebookLM before launching Writers Factory.

---

## Overview

Writers Factory is an **extraction tool, not a generation tool**. It doesn't brainstorm your novel from scratch - it transforms your existing creative research into a structured Story Bible that powers consistent AI-assisted drafting.

**Before opening Writers Factory, you must have completed research in Google NotebookLM.**

---

## The 3-Stage Pipeline

| Stage | What It Is | Where It Lives |
|-------|-----------|----------------|
| **Stage 1** | Raw brainstorming - podcasts, articles, vibes | Your private NotebookLM notebooks (NOT registered) |
| **Stage 2** | Distilled, structured data | Your 5 Core Notebooks (registered in Writers Factory) |
| **Stage 3** | Canonical Story Bible | `content/` directory in Writers Factory |

**Writers Factory only sees Stage 2 and 3.** Stage 1 is your private creative chaos.

---

## Pre-Flight Checklist

Before launching Writers Factory, verify you have completed these steps:

### 1. Create Your 5 Core Notebooks in NotebookLM

Go to [notebooklm.google.com](https://notebooklm.google.com) and create exactly 5 notebooks:

- [ ] **[Your Novel] - Characters** (ALL characters in ONE notebook)
- [ ] **[Your Novel] - World** (ALL world-building in ONE notebook)
- [ ] **[Your Novel] - Theme** (ALL philosophical ideas in ONE notebook)
- [ ] **[Your Novel] - Plot** (Structure and beats)
- [ ] **[Your Novel] - Voice** (Style targets and samples)

### 2. Distill Your Raw Research

For each Core Notebook, run the appropriate Distillation Prompt in NotebookLM's chat. See [DISTILLATION_PROMPTS.md](./DISTILLATION_PROMPTS.md) for the full prompts.

**Quick reference - key markers the AI looks for:**

| Notebook | Required Markers |
|----------|-----------------|
| Characters | "Fatal Flaw", "The Lie", "Arc" |
| World | "Hard Rule", "Cannot be broken" |
| Theme | "Central Question", "Thesis", "Counter-thesis" |
| Plot | Beat names (Catalyst, Midpoint, All Is Lost, Finale), "Midpoint Type" |
| Voice | "Rhythm", "Anti-pattern" |

### 3. Verify Your Notebooks Have Structure

Before registering, check that your notebooks contain the markers above. Open each notebook in NotebookLM and verify:

**Characters Notebook:**
```
- Character Type: protagonist | antagonist | supporting
- Fatal Flaw: [internal weakness, NOT circumstance]
- The Lie: [mistaken belief driving the flaw]
- Arc: [start → midpoint → resolution]
```

**World Notebook:**
```
HARD RULES (Cannot be broken):
1. [Rule that is physically/magically impossible to violate]
2. [Rule that is physically/magically impossible to violate]
```

**Theme Notebook:**
```
CENTRAL QUESTION: "Can [thesis] exist despite [counter-thesis]?"
THESIS: [argument FOR]
COUNTER-THESIS: [argument AGAINST]
```

**Plot Notebook:**
```
4. CATALYST (10%): [inciting incident]
9. MIDPOINT (50%): [event]
   MIDPOINT TYPE: False Victory | False Defeat
11. ALL IS LOST (75%): [lowest point]
14. FINALE (80-99%): [climax]
```

**Voice Notebook:**
```
SENTENCE RHYTHM: [description]
ANTI-PATTERNS (What to AVOID): [list]
```

---

## Launching Writers Factory

Once your 5 Core Notebooks are ready:

### Step 1: Register Your Notebooks

1. Open Writers Factory
2. Click the **NOTEBOOK** button in the top toolbar
3. Paste each NotebookLM URL or ID
4. Assign the correct category (Characters, World, Theme, Plot, Voice)

**Your notebooks stay in NotebookLM.** Writers Factory queries them remotely - you don't download or upload files.

### Step 2: Start ARCHITECT Mode

The Foreman (your AI partner) starts in **ARCHITECT mode**. This is where your Story Bible gets built.

The Foreman will:
1. Query your registered notebooks
2. Extract structured data (looking for the markers above)
3. Help you build Story Bible documents interactively

### Step 3: Respond to Extraction Failures

If the Foreman can't find structured data, it will:
1. **NOT hallucinate** - it won't make up a Fatal Flaw
2. **Diagnose** - explain what's missing
3. **Offer help** - provide the specific Distillation Prompt to run

This is the system working correctly. Go back to NotebookLM, run the prompt, and try again.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Registering raw notebooks | Extraction fails constantly | Distill first using the prompts |
| One notebook per character | AI can't see relationships | Combine ALL characters in ONE notebook |
| No Hard Rules labeled | AI can't enforce world consistency | Mark which rules are immutable |
| Theme as statement ("Love matters") | AI can't generate conflict | Frame as question ("Can love survive betrayal?") |
| Missing midpoint type | AI can't calibrate second act | State FALSE VICTORY or FALSE DEFEAT |

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

## Quick Links

- [The 5 Core Notebooks](./FIVE_CORE_NOTEBOOKS.md) - Detailed setup guide
- [Distillation Prompts](./DISTILLATION_PROMPTS.md) - Copy-paste prompts for NotebookLM
- [Narrative Protocol](./NARRATIVE%20PROTOCOL.md) - The methodology behind Writers Factory

---

## Technical Note: NotebookLM Integration

Your notebooks are queried via NotebookLM's interface. The integration:
- Keeps your research in NotebookLM (no file downloads)
- Queries notebooks on-demand during ARCHITECT mode
- Extracts structured data based on the markers above

If you encounter connection issues, verify:
1. You're logged into the same Google account
2. The notebook URLs/IDs are correct
3. The notebooks are not in a shared workspace with restricted access

---

*Created for Writers Factory Distillation Pipeline*
