# one clarifying question



------

## Confirmed Architecture

| Aspect                              | Answer                                                    |
| ----------------------------------- | --------------------------------------------------------- |
| **Where distillation happens**      | OUTSIDE the app (in NotebookLM)                           |
| **Where distillation prompts live** | INSIDE the app (docs + Foreman brain)                     |
| **5 Core enforcement**              | Strict SLOTS, flexible CONTENT (can have gaps)            |
| **Foreman's role**                  | Guide distillation, explain the pipeline, provide prompts |

------

## The Key Technical Insight

> "The Factory accepts specific data types. Please format your raw inspiration into these types before entering."

This is the **API Contract** metaphor. Writers Factory is like a function:



```python
def writers_factory(
    character_notebook: NotebookLM,   # Required slot
    world_notebook: NotebookLM,       # Required slot
    theme_notebook: NotebookLM,       # Required slot
    plot_notebook: NotebookLM,        # Required slot
    voice_notebook: NotebookLM        # Required slot
) -> StoryBible:
    """
    Input: 5 structured NotebookLM notebooks
    Output: Protagonist.md, Beat_Sheet.md, Rules.md, Theme.md
    
    Will fail or hallucinate if inputs are unstructured Stage 1 data.
    """
```

------

## One Clarifying Question for the Other Agent

**On "Flexible Content" for the 5 slots:**

 

When a user registers a notebook that's supposed to be "Character" but contains messy Stage 1 content (random podcasts, no Fatal Flaw structure), should the system:

 

**Option A**: Accept it silently, let SmartScaffoldWorkflow fail/hallucinate later **Option B**: Run a "quality check" on registration to warn: "This notebook doesn't appear to contain structured character data. Consider running distillation prompts first." **Option C**: Accept it, but when Foreman queries it and gets garbage, Foreman says: "I couldn't extract a Fatal Flaw from your Character notebook. Here's a distillation prompt to run..."

 

My instinct is **Option C** - fail gracefully at query time with helpful guidance. But this affects Phase 2 (Conflict Detection) and Phase 4 (Promotion) logic.



------

## Proposed Updates to Task Specs

Once clarified, here's what needs updating:



### Phase 0: Foreman Knowledge

**Add:**



```
THE DISTILLATION PIPELINE:

You (Foreman) work with STAGE 2 notebooks only.

STAGE 1 (Raw Materials) - NOT YOUR CONCERN:
- Users' messy "Inspiration", "Vibes", "Random Ideas" notebooks
- You cannot see these - they're not registered
- This is where humans brainstorm freely

STAGE 2 (5 Core Notebooks) - YOUR INPUT:
- Character, World, Theme, Plot, Voice
- Structured, distilled from Stage 1
- These ARE registered in Writers Factory
- You query these to build the Story Bible

IF USER ASKS "How do I turn my podcast notes into a character?":
- Provide the Character Distillation Prompt
- Explain they do this in NotebookLM (external)
- Then register the RESULT as their Character notebook

IF YOUR QUERY RETURNS GARBAGE (no Fatal Flaw, no structure):
- Don't hallucinate
- Say: "I couldn't find structured character data. Try this distillation prompt in NotebookLM: [prompt]"
```

### Phase 1: File-Based Research

**Change categories to strict 5:**



```
workspace/research/
├── characters/   # From Character Core Notebook
├── world/        # From World Core Notebook  
├── theme/        # From Theme Core Notebook
├── plot/         # From Plot Core Notebook
└── voice/        # From Voice Core Notebook
```

### Phase 5: Documentation

**Add Distillation Prompts Library:**



- CHARACTER: Extract Fatal Flaw, The Lie, Arc
- WORLD: Extract Hard Rules, Locations, Secrets
- THEME: Extract Central Question, Arguments, Symbols
- PLOT: Extract 15 beats, Midpoint type
- VOICE: Extract style patterns, anti-patterns