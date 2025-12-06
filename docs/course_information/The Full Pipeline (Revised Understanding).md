## The Full Pipeline (Revised Understanding)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: RAW MATERIALS (Data Lake)                                      │
│  Location: NotebookLM (external)                                         │
│  Character: MESSY, UNLIMITED notebooks                                   │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │ "Inspiration"│  │   "Style"    │  │  "Concepts"  │  ... as many      │
│  │  Podcasts,   │  │ Favorite     │  │ "What if"    │  as they want     │
│  │  articles,   │  │ authors,     │  │ scenarios,   │                   │
│  │  interviews  │  │ blog posts   │  │ news clips   │                   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                   │
│         │                 │                 │                            │
│         └─────────────────┼─────────────────┘                            │
│                           ▼                                              │
│              DISTILLATION PROMPTS                                        │
│    "Based on X, create a protagonist with Fatal Flaw..."                │
│    "Extract the Hard Rules from our world-building..."                  │
│    "What's the central philosophical argument?"                         │
│                           │                                              │
└───────────────────────────┼──────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: THE 5 CORE NOTEBOOKS (Structured API Contract)                 │
│  Location: NotebookLM (external) - but STRUCTURED                        │
│  Character: EXACTLY 5, RIGID format                                      │
│                                                                          │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │ Character │ │   World   │ │   Theme   │ │   Plot    │ │   Voice   │  │
│  │           │ │           │ │           │ │           │ │           │  │
│  │ Fatal     │ │ Hard      │ │ Central   │ │ 15 Beats  │ │ Target    │  │
│  │ Flaw,     │ │ Rules,    │ │ Question, │ │ Scene     │ │ Authors,  │  │
│  │ The Lie,  │ │ Locations │ │ Symbols   │ │ Ideas     │ │ Patterns  │  │
│  │ Cast      │ │           │ │           │ │           │ │           │  │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘  │
│        │             │             │             │             │         │
│        └─────────────┴──────┬──────┴─────────────┴─────────────┘         │
│                             │                                            │
│                    REGISTER IN WRITERS FACTORY                           │
│                             │                                            │
└─────────────────────────────┼────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: WRITERS FACTORY (The Machine)                                  │
│  Location: Writers Factory app                                           │
│                                                                          │
│  INPUT: Queries to 5 Core Notebooks via MCP                              │
│                    │                                                     │
│                    ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  FOREMAN (ARCHITECT Mode)                                        │    │
│  │  "Extract Fatal Flaw from Character notebook"                    │    │
│  │  "Extract Hard Rules from World notebook"                        │    │
│  │  "Extract 15 beats from Plot notebook"                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                    │                                                     │
│                    ▼                                                     │
│  OUTPUT: STORY BIBLE (content/)                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                  │
│  │Protagonist.md │ │ Beat_Sheet.md │ │   Rules.md    │ ...              │
│  │(Fatal Flaw,   │ │ (15 beats,    │ │ (Hard Rules)  │                  │
│  │ The Lie, Arc) │ │  midpoint)    │ │               │                  │
│  └───────────────┘ └───────────────┘ └───────────────┘                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

------

## Key Insight: Two Types of Students

| Type            | Starting Point      | Path                                                         |
| --------------- | ------------------- | ------------------------------------------------------------ |
| **Blank Slate** | No idea, just vibes | Stage 1 → Distillation → Stage 2 → Stage 3                   |
| **Prepared**    | Has existing drafts | Upload drafts → Extract implicit structure → Stage 2 → Stage 3 |

------

## What This Means for Implementation

### We Were Conflating Stage 1 and Stage 2

Our current specs assume users register "research notebooks" without distinguishing:



- **Stage 1 notebooks** (raw materials) - we shouldn't care about these
- **Stage 2 notebooks** (5 Core) - these are what the Factory needs

### The Factory Only Sees Stage 2

Writers Factory should:



1. **NOT help with Stage 1** - that's messy exploration in NotebookLM
2. **Guide users through distillation** - prompts to extract structure from raw materials
3. **Accept exactly 5 registered notebooks** - Character, World, Theme, Plot, Voice
4. **Extract structured data** into Story Bible

### Revised Notebook Registration Flow

```
Current (wrong):
  "Register a NotebookLM notebook" 
  → Pick any category
  → Unlimited notebooks

Correct:
  "Register your 5 Core Notebooks"
  → Character (required)
  → World (required)  
  → Theme (required)
  → Plot (required)
  → Voice (required)
  
  Each slot accepts ONE notebook ID.
  All 5 must be registered to proceed.
```

------

## Revised Phase Breakdown

### Phase 0: Foreman Knowledge

Add understanding of the **Distillation Pipeline**:



```
THE DISTILLATION PIPELINE:

STAGE 1 (Raw Materials - outside Writers Factory):
- Users create UNLIMITED messy notebooks in NotebookLM
- "Inspiration", "Style", "Concepts" - whatever they want
- This is for brainstorming - Writers Factory doesn't see these

STAGE 2 (5 Core Notebooks - what you work with):
- Users DISTILL raw materials into exactly 5 structured notebooks
- Character, World, Theme, Plot, Voice
- These are registered in Writers Factory
- You (Foreman) query these to build the Story Bible

YOUR ROLE:
- Don't ask about Stage 1 notebooks - those are private exploration
- DO guide extraction from 5 Core Notebooks
- Help users who skipped Stage 1 by prompting them to build Core Notebooks
```

### Phase 1: File-Based Research

**No change to core feature**, but clarify:



- Research Notes come from the **5 Core Notebooks only**
- Categories are fixed: `characters/`, `world/`, `theme/`, `plot/`, `voice/`

### Phase 4: Promotion - The Intelligent Bridge

This becomes even more important. Promotion must:



- Know which Core Notebook the data came from
- Map to the correct Story Bible document
- Extract the right fields (Fatal Flaw → Protagonist.md, Hard Rules → Rules.md)

### Phase 5: Documentation

Add **Distillation Guide**:



- How to create Stage 1 notebooks (examples)
- Distillation prompts for each Core Notebook
- "Blank Slate" vs "Prepared" paths

------

## New Feature Idea: Distillation Prompts Library

Should Writers Factory provide **pre-written distillation prompts**?



```
┌─────────────────────────────────────────────────────────────────────┐
│  DISTILLATION PROMPTS (in app or documentation)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📚 CHARACTER DISTILLATION                                           │
│  "Based on [raw materials], create a protagonist with:              │
│   - A Fatal Flaw (internal weakness, not circumstance)              │
│   - The Lie they believe about themselves                           │
│   - Their arc: starting state → midpoint → resolution"              │
│                                                                      │
│  🌍 WORLD DISTILLATION                                               │
│  "From [raw materials], list:                                       │
│   - 5 Hard Rules (physics, magic limits - CANNOT be broken)         │
│   - Key Locations (name, significance)                              │
│   - What's known publicly vs. what's secret"                        │
│                                                                      │
│  💭 THEME DISTILLATION                                               │
│  "Looking at [raw materials], answer:                               │
│   - What's the central philosophical QUESTION?                      │
│   - What's the argument FOR the theme?                              │
│   - What's the argument AGAINST (the counter-thesis)?               │
│   - List symbols that could represent this conflict"                │
│                                                                      │
│  📊 PLOT DISTILLATION                                                │
│  "From [raw materials], map to the 15-beat structure:               │
│   - Opening Image, Catalyst, Midpoint, All Is Lost, etc.            │
│   - Is this False Victory or False Defeat at midpoint?"             │
│                                                                      │
│  ✍️ VOICE DISTILLATION                                               │
│  "Analyze [favorite passages] and describe:                         │
│   - Sentence rhythm patterns                                        │
│   - Metaphor domains (where do metaphors come from?)                │
│   - What to AVOID (anti-patterns)"                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

------

## Questions for Brainstorming

1. **Should distillation happen IN the app or BEFORE?**
   - Current assumption: Users do distillation in NotebookLM, then register
   - Alternative: Foreman helps distill raw notebooks into Core structure
2. **Should we enforce "5 Core" registration?**
   - Strict: Must register all 5 to proceed past onboarding
   - Flexible: Can start with fewer, but Foreman warns about gaps
3. **Where do Distillation Prompts live?**
   - In documentation only (Phase 5)
   - As copyable templates in the app
   - As Foreman suggestions ("Try asking your Inspiration notebook...")

What's your vision for how much of Stage 1→2 distillation happens inside vs. outside the app?