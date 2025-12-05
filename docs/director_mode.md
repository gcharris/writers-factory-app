---
layout: default
title: Director Mode
---

# Director Mode: The Scene Creation Pipeline

> **"We don't write scenes. We manufacture them with precision engineering."**

Director Mode is where the magic happens. After completing your Story Bible (ARCHITECT Mode) and calibrating your voice (VOICE Mode), you enter the drafting phase with a complete creative infrastructure supporting every word.

---

## The Problem with "Just Write"

Traditional AI writing assistance works like this:

1. You: "Write me a scene where Mickey enters the casino."
2. AI: *Generates something generic*
3. You: "No, that's not right..."
4. AI: *Generates something slightly different but still generic*
5. Repeat until frustrated.

The fundamental problem? **The AI doesn't know your novel.** It doesn't know Mickey's fatal flaw, your voice preferences, or what happened in the previous scene.

---

## The Director Mode Solution

Director Mode treats scene creation like a **manufacturing pipeline**—not a guessing game.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     THE SCENE CREATION PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│     ┌──────────┐                                                        │
│     │ SCAFFOLD │  "What does this scene need to accomplish?"            │
│     └────┬─────┘                                                        │
│          │                                                              │
│          ▼                                                              │
│     ┌──────────┐                                                        │
│     │STRUCTURE │  "What's the best way to structure it?"                │
│     └────┬─────┘                                                        │
│          │                                                              │
│          ▼                                                              │
│     ┌──────────┐                                                        │
│     │ GENERATE │  "Let multiple AI models compete to draft it."         │
│     └────┬─────┘                                                        │
│          │                                                              │
│          ▼                                                              │
│     ┌──────────┐                                                        │
│     │ COMPARE  │  "Which version is best? Can we combine the best parts?"│
│     └────┬─────┘                                                        │
│          │                                                              │
│          ▼                                                              │
│     ┌──────────┐                                                        │
│     │ ENHANCE  │  "Polish based on the 100-point scoring rubric."       │
│     └────┬─────┘                                                        │
│          │                                                              │
│          ▼                                                              │
│     ┌──────────┐                                                        │
│     │ COMPLETE │  "Save and move to the next scene."                    │
│     └──────────┘                                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

Each step is **informed by your creative infrastructure**:
- Your **Story Bible** provides character psychology and plot beats
- Your **Voice Bundle** ensures every draft sounds like you
- Your **Knowledge Graph** prevents contradictions and tracks continuity

---

## The 6 Steps Explained

### Step 1: Scaffold

Before any AI writes a word, we build a **strategic briefing document**.

**You provide:**
- Chapter and scene number
- Which beat this serves (from your Beat Sheet)
- Characters present
- A brief description of what happens

**The system adds:**
- Character psychology (Fatal Flaw, The Lie)
- Previous scene continuity
- Voice requirements from your Voice Bundle
- World rules that apply
- Optional: Research from NotebookLM

**The output:** A comprehensive scaffold that tells the AI everything it needs to know—not just *what* to write, but *how* to write it for your specific novel.

---

### Step 2: Structure

Not every scene should be structured the same way. A chase scene has different pacing than a confession scene.

The system generates **5 structural approaches**:

| Approach | Best For | Pacing |
|----------|----------|--------|
| **Action-Forward** | Chase, fight, escape | Fast |
| **Character-Driven** | Internal conflict, decisions | Medium |
| **Dialogue-Heavy** | Negotiations, revelations | Slow-Medium |
| **Atmospheric** | Setting establishment, mood | Slow |
| **Balanced** | Standard scenes | Varied |

You choose the structure that fits the scene's emotional needs.

---

### Step 3: Generate (The Tournament)

Here's where the manufacturing power kicks in.

Instead of asking one AI to write one draft and hoping for the best, we run a **tournament**:

- **3 AI models** (Claude, GPT-4o, DeepSeek)
- **5 writing strategies** each (Action, Character, Dialogue, Brainstorming, Balanced)
- **15 total variants** generated in parallel

Each variant is automatically scored against the **100-Point Rubric**:

| Category | Points | What It Measures |
|----------|--------|------------------|
| Voice Authenticity | 30 | Does it sound like YOU, not generic AI? |
| Character Consistency | 20 | Does behavior match established psychology? |
| Metaphor Discipline | 20 | Are metaphor domains diverse? No saturation? |
| Anti-Pattern Compliance | 15 | Zero forbidden constructions? |
| Phase Appropriateness | 15 | Does voice complexity match story phase? |

**Result:** You see a grid of 15 options, each with a quality score. No more guessing which version is better—the rubric tells you.

---

### Step 4: Compare & Select

With 15 scored variants, you have real options:

- **Select the best:** Usually the highest-scoring variant
- **Compare 2-4:** Side-by-side view with score breakdowns
- **Create a hybrid:** "Use the opening from Claude-Character, the middle from GPT-Dialogue, and the ending from DeepSeek-Action"

The system makes it easy to see exactly *why* each variant scored the way it did, so you can make informed creative decisions.

---

### Step 5: Enhance

Even the best draft can be improved. Based on the score, the system recommends an enhancement approach:

| Score | Recommendation | What Happens |
|-------|----------------|--------------|
| 85+ | **Action Prompt** | Surgical fixes—specific line changes |
| 70-84 | **6-Pass Enhancement** | Full polish pipeline |
| <70 | **Regenerate** | Start over with different approach |

**Action Prompt example:**
```
The scene scores 91/100 but has these specific issues:

1. Line 42: "with practiced precision" → Zero-tolerance violation
   FIX: Replace with direct metaphor showing precision

2. Lines 78-92: Gambling metaphors at 38% → Approaching saturation
   FIX: Replace 2 gambling metaphors with boxing domain

3. Line 156: Character trusted authority without reading angles
   FIX: Add internal resistance per Fatal Flaw
```

You can preview the fixes before applying them.

---

### Step 6: Complete

The scene is done. The system:

1. **Saves** the final draft to your manuscript
2. **Updates** the Knowledge Graph with new facts
3. **Resolves** any FORESHADOW → CALLBACK edges
4. **Recalculates** tension levels

Then you choose what's next:
- Start the next scene
- Review the full chapter
- Return to dashboard
- Edit in the Monaco editor

---

## The Integration Architecture

Director Mode doesn't work in isolation. Every step pulls from your complete creative infrastructure:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SCENE GENERATION REQUEST                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    CONTEXT ASSEMBLY                              │   │
│   ├─────────────────────────────────────────────────────────────────┤   │
│   │                                                                   │   │
│   │   Story Bible          Voice Bundle         GraphRAG              │   │
│   │   ├── Protagonist      ├── Gold Standard    ├── Ego-graph        │   │
│   │   ├── Beat Sheet       ├── Anti-patterns    ├── Active conflicts │   │
│   │   ├── Theme            ├── Metaphor domains ├── Unresolved       │   │
│   │   └── World Rules      └── Phase voice          foreshadows      │   │
│   │                                                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                     LLM GENERATION                               │   │
│   │                                                                   │   │
│   │   The AI receives ALL relevant context before writing a word.    │   │
│   │   It cannot hallucinate because it has the facts.                │   │
│   │   It cannot sound generic because it has your voice.             │   │
│   │                                                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    VERIFICATION                                   │   │
│   │                                                                   │   │
│   │   After generation, the system checks:                           │   │
│   │   - Dead characters don't appear                                 │   │
│   │   - Anti-patterns eliminated                                     │   │
│   │   - POV consistent                                               │   │
│   │   - Timeline coherent                                            │   │
│   │   - Voice authentic                                              │   │
│   │                                                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    GRAPH UPDATE                                   │   │
│   │                                                                   │   │
│   │   New facts are extracted and added to the Knowledge Graph:      │   │
│   │   - New entities → add nodes                                     │   │
│   │   - New relationships → add edges                                │   │
│   │   - Resolved foreshadows → convert to CALLBACKS                  │   │
│   │   - Tension recalculated                                         │   │
│   │                                                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The 100-Point Rubric

Every scene is scored objectively. Here's how:

### Voice Authenticity (30 points)

| Test | Points | Question |
|------|--------|----------|
| Authenticity | 10 | Does this sound like the POV character observing, or AI explaining the character? |
| Purpose | 10 | Does every beat serve the theme? |
| Fusion | 10 | Are technical/specialized concepts fused with character voice? |

### Character Consistency (20 points)

| Test | Points | Question |
|------|--------|----------|
| Psychology | 8 | Does behavior match Fatal Flaw and The Lie? |
| Capability | 6 | Are all actions within established limits? |
| Relationships | 6 | Do interactions match established dynamics? |

### Metaphor Discipline (20 points)

| Test | Points | Question |
|------|--------|----------|
| Domain Rotation | 10 | No single domain >30%? |
| Simile Elimination | 5 | Direct metaphors instead of "like" comparisons? |
| Transformation | 5 | Objects BECOME metaphors through active verbs? |

### Anti-Pattern Compliance (15 points)

Start at 15, deduct for violations:
- **-2** per zero-tolerance violation (e.g., "with practiced precision")
- **-1** per formulaic pattern (e.g., excessive adverbs)

### Phase Appropriateness (15 points)

| Test | Points | Question |
|------|--------|----------|
| Complexity | 8 | Does voice complexity match story phase? |
| Earned Language | 7 | Is specialized terminology justified by this point in the story? |

---

## Real Example

**Scenario:** Writing Chapter 4, Scene 1 — Mickey enters the casino for the first time since the incident.

**Step 1 (Scaffold):** System pulls Mickey's psychology (needs control, hides vulnerability), casino world rules, previous scene summary, and voice requirements.

**Step 2 (Structure):** Writer chooses "Character-Driven" — internal conflict → external trigger → decision.

**Step 3 (Generate):** 15 variants produced in ~30 seconds. Top scorer: Claude Sonnet - Character at 91/100.

**Step 4 (Compare):** Writer compares top 3, notices GPT has a better opening. Creates hybrid.

**Step 5 (Enhance):** Hybrid scores 89. System suggests Action Prompt with 3 surgical fixes. Applied → 94/100.

**Step 6 (Complete):** Scene saved. GraphRAG updated with new facts. Mickey's TENSION_LEVEL increases. Ready for Scene 2.

**Time:** ~5 minutes for a polished, voice-consistent, continuity-verified scene.

---

## Why This Works

Traditional AI writing fails because:
1. **No memory** — Every request starts from scratch
2. **No voice** — Generic prose that sounds like everyone
3. **No verification** — Hallucinations and contradictions slip through
4. **No options** — You get one draft and hope it's good

Director Mode succeeds because:
1. **Full context** — Story Bible + Voice Bundle + Knowledge Graph
2. **Your voice** — Calibrated through tournament selection
3. **Automated checks** — 100-point rubric catches problems
4. **15 options** — Explore creative space systematically

---

## Technical Implementation

For the technical specification including:
- API endpoints
- Component architecture
- State management
- Full code examples

See: **[Director Mode UI Task Spec](tasks/DIRECTOR_MODE_UI)**

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Voice Calibration](voice_calibration) | How we capture your voice |
| [GraphRAG](graphrag) | The knowledge graph that powers verification |
| [Systems Integration](systems_integration) | How all systems work together |
| [Writer's Journey](journey) | The complete creative workflow |

---

*Director Mode: Where preparation meets production.*
