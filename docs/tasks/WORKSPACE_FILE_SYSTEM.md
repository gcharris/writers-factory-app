# Workspace File System & Research Workflow

> Task specification for implementing the Distillation Pipeline with structured workspace and conflict-aware research ingestion

## The Distillation Pipeline (Core Concept)

Writers Factory is an **extraction tool, not a generation tool**. It follows a 3-stage pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: RAW MATERIALS (Data Lake)                                          │
│  Location: NotebookLM (external)                                             │
│  Character: MESSY, UNLIMITED notebooks                                       │
│                                                                              │
│  "Inspiration" / "Vibes" / "Random Ideas" - as many as you want             │
│  Podcasts, YouTube transcripts, articles, favorite authors                   │
│                                                                              │
│                          ↓ DISTILLATION PROMPTS ↓                            │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  STAGE 2: THE 5 CORE NOTEBOOKS (Structured API Contract)                     │
│  Location: NotebookLM (external) - but STRUCTURED                            │
│  Character: EXACTLY 5, RIGID format                                          │
│                                                                              │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐      │
│  │ Character │ │   World   │ │   Theme   │ │   Plot    │ │   Voice   │      │
│  │ (ALL in 1)│ │ (ALL in 1)│ │ (ALL in 1)│ │           │ │           │      │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘      │
│                                                                              │
│                          ↓ REGISTER IN FACTORY ↓                             │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  STAGE 3: STORY BIBLE (Writers Factory Output)                               │
│  Location: content/ directory                                                │
│                                                                              │
│  Protagonist.md, Beat_Sheet.md, Theme.md, Rules.md                           │
│  Built via intelligent extraction from 5 Core Notebooks                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why This Matters

Without Stage 2 distillation:
- SmartScaffoldWorkflow drowns in noise from 50 messy notebooks
- AI hallucinates or times out on unstructured input
- Conflict detection produces false positives on "vibes"

With Stage 2 distillation:
- User acts as pre-processor, formatting input for the Factory
- AI gets clean, structured data with explicit markers
- Extraction is precise and verifiable

---

## Problem Statement

Currently:
- NotebookLM extractions save to SQLite KB (not editable files)
- No way to copy research results to chat for follow-up prompts
- No distinction between "work in progress" and "completed" content
- No conflict detection when multiple notebooks have contradicting information
- No guidance for users on what notebooks to create or how to organize research
- **No distinction between Stage 1 (raw) and Stage 2 (distilled) content**
- **No enforcement of the 5 Core Notebooks structure**

## Goals

1. **Distillation Pipeline** - Teach and enforce Stage 1 → Stage 2 → Stage 3 flow
2. **5 Core Notebooks** - Enforce exactly 5 structured notebook categories
3. **Workspace Directory Structure** - Organize files by lifecycle stage
4. **Research as Files** - NotebookLM extractions become editable markdown
5. **Copy-to-Chat Workflow** - Easy way to reference any content in prompts
6. **Conflict Detection** - Flag contradictions before auto-ingestion (Stage 2 only)
7. **User Documentation** - Guide for distillation and notebook organization

---

## Terminology Guide (IMPORTANT)

To avoid confusion (both human and AI), this project uses specific terminology:

| Term | Meaning | Context |
|------|---------|---------|
| **NotebookLM notebook** | A research notebook in Google's NotebookLM product | External - lives at notebooklm.google.com |
| **Research Notes** | Extractions saved from NotebookLM queries | Internal - saved in Writers Factory |
| **Story Bible** | Canonical character/world/structure documents | Internal - lives in `content/` directory |
| **Workspace** | Active work-in-progress area | Internal - lives in `workspace/` directory |

### Why This Matters

The word "notebook" alone is ambiguous:
- Could mean NotebookLM notebook (external Google product)
- Could mean a generic notebook concept
- The Foreman hallucinated a wrong definition when asked about "the notebook"

### Usage Rules

1. **Always say "NotebookLM notebook"** when referring to Google's product
2. **Never use "notebook" alone** in UI labels, documentation, or AI prompts
3. **Use "Research Notes"** for saved extractions in Writers Factory
4. **Use "Story Bible"** for canonical documents (not "notebook")

### Examples

| Bad | Good |
|-----|------|
| "Create a notebook for your character" | "Create a NotebookLM notebook for your character research" |
| "Register your notebooks" | "Register your NotebookLM notebooks" |
| "The notebook contains..." | "The NotebookLM notebook contains..." |
| "Save to notebook" | "Save to Research Notes" |

---

## Proposed Directory Structure

```
project/
├── workspace/                    # Active work-in-progress
│   ├── research/                 # NotebookLM extractions (markdown)
│   │   ├── characters/           # From CHARACTER Core Notebook
│   │   │   ├── protagonist_profile.md
│   │   │   └── antagonist_notes.md
│   │   ├── world/                # From WORLD Core Notebook
│   │   │   ├── hard_rules.md
│   │   │   └── locations.md
│   │   ├── theme/                # From THEME Core Notebook (singular!)
│   │   │   └── central_question.md
│   │   ├── plot/                 # From PLOT Core Notebook
│   │   │   └── beat_sheet_draft.md
│   │   └── voice/                # From VOICE Core Notebook
│   │       └── style_targets.md
│   ├── drafts/                   # Scene drafts being worked on
│   │   ├── ch01_opening.md
│   │   └── ch02_inciting.md
│   └── prompts/                  # Saved prompts/conversations
│       └── voice_calibration_session.md
│
├── manuscript/                   # Completed, reviewed scenes
│   ├── Part_1/
│   │   ├── ch01_opening.md       # Moved from drafts when "complete"
│   │   └── ch02_inciting.md
│   └── Part_2/
│
└── content/                      # Story Bible (existing structure)
    ├── Characters/               # Canonical character files
    │   └── Protagonist.md        # The "official" version
    ├── Story Bible/
    │   ├── Structure/
    │   │   └── Beat_Sheet.md
    │   └── Themes_and_Philosophy/
    └── World Bible/
```

### The 5 Research Categories (STRICT)

Research files MUST be saved into one of these 5 categories, matching the 5 Core Notebooks:

| Category | Source | Maps to Story Bible |
|----------|--------|---------------------|
| `characters/` | CHARACTER Notebook | `Protagonist.md`, `Cast.md` |
| `world/` | WORLD Notebook | `Rules.md`, `Locations.md` |
| `theme/` | THEME Notebook | `Theme.md` |
| `plot/` | PLOT Notebook | `Beat_Sheet.md` |
| `voice/` | VOICE Notebook | Voice Calibration Bundle |

**No "misc" or "other" category allowed.** If content doesn't fit, it belongs in Stage 1 (raw research), not Stage 2.

### Key Distinctions

| Location | Purpose | Editable? | Auto-ingested? |
|----------|---------|-----------|----------------|
| `workspace/research/` | Raw NotebookLM extractions | Yes | No - needs review |
| `workspace/drafts/` | Active scene work | Yes | No |
| `workspace/prompts/` | Saved conversations | Yes | No |
| `manuscript/` | Completed scenes | Read-only? | Yes - for continuity |
| `content/` | Story Bible (canon) | Yes | Yes - source of truth |

---

## Feature 1: Research as Editable Files

### Current Flow
```
NotebookLM Query → API Response → SQLite KB Entry → (invisible)
```

### Proposed Flow
```
NotebookLM Query → API Response → Markdown File in workspace/research/
                               → Display in UI with actions
                               → "Promote to Story Bible" when ready
```

### File Format
```markdown
---
source: NotebookLM
notebook: "research for character Umar"
notebook_id: ce3c54ad-fc95-44ba-a88a-19573bd6aac2
extracted: 2024-12-06T11:07:08
category: character
key: umar
status: draft  # draft | reviewed | promoted
conflicts: []  # List of conflicting file paths
---

# Umar - Character Profile

Based on the provided notebook and supporting transcripts...

[Full extraction content here]

---
## User Notes

[Space for author to add their own annotations]
```

### Benefits
- Version controllable (git)
- Editable by author
- Searchable with standard tools
- Viewable in main editor
- Clear provenance tracking

---

## Feature 2: Copy-to-Chat Workflow

### From File Tree (Binder)
- Hover on any file → "Copy to Chat" button
- Copies file content (or selection) to chat input
- Formats as context block:
  ```
  [From: workspace/research/characters/umar_profile.md]

  <content here>
  ```

### From Editor
- Select text → Right-click → "Copy to Chat"
- Or toolbar button when text selected
- Already partially implemented

### From NotebookLM Results
- Add "Copy to Chat" button alongside "Save to Research Notes"
- Copies the result directly to chat input for follow-up questions

### From Saved Notes UI
- Each note card gets "Copy to Chat" action
- Useful for building composite prompts from multiple extractions

---

## Feature 3: Conflict Detection

### The Problem
User has two notebooks:
- "Research for Umar" says Umar is 45 years old
- "World Building 2035" says the protagonist is in their 30s

Automatic ingestion would create contradictions in the Knowledge Graph.

### Proposed Solution

#### Stage 1: Detection
When saving new research, scan existing workspace/research/ files for:
- Same category + overlapping entities
- Contradicting facts (using LLM analysis)

```python
async def detect_conflicts(new_content: str, category: str) -> list[Conflict]:
    """Find potential conflicts with existing research."""
    existing = load_research_files(category)
    conflicts = []

    for file in existing:
        # Use LLM to check for contradictions
        result = await llm_service.analyze_contradiction(
            new_content,
            file.content,
            focus="factual claims about characters, timeline, world rules"
        )
        if result.has_conflict:
            conflicts.append(Conflict(
                file=file.path,
                description=result.explanation,
                severity=result.severity  # minor | significant | breaking
            ))

    return conflicts
```

#### Stage 2: User Resolution
When conflicts detected:
1. Show conflict banner in UI
2. Display side-by-side comparison
3. Options:
   - **Keep Both** - Author will reconcile manually
   - **Prefer New** - Archive old, use new
   - **Prefer Existing** - Discard new
   - **Merge** - Open editor with both, let author combine

#### Stage 3: Promotion Gate
Files can only be "promoted" to Story Bible (`content/`) after:
- No unresolved conflicts
- Author has marked as "reviewed"
- Optional: Foreman review pass

---

## Feature 4: Scene Lifecycle

### States
```
DRAFT → IN_REVIEW → COMPLETE → LOCKED
```

### Draft (workspace/drafts/)
- Active editing
- Not ingested into continuity checks
- Can have multiple versions

### In Review
- Author marks scene as "ready for review"
- Foreman can analyze for:
  - Voice consistency
  - Beat alignment
  - Continuity issues
- Author addresses feedback

### Complete
- Moved to `manuscript/`
- Ingested into Knowledge Graph for continuity
- Still editable but changes tracked

### Locked (optional)
- Read-only
- Used for "final draft" protection

### UI Indicator
Scene files show status badge in file tree:
- 📝 Draft
- 🔍 In Review
- ✅ Complete
- 🔒 Locked

---

## Feature 5: The 5 Core Notebooks (CRITICAL)

### The Structure

Writers Factory requires EXACTLY 5 Core Notebooks - no more, no less:

```
NotebookLM Notebooks (Google) - STAGE 2 ONLY
├── [PROJECT] CHARACTER              # ONE notebook for ALL characters
│   └── Protagonist, Antagonist, Supporting Cast together
├── [PROJECT] WORLD                  # ONE notebook for ALL world-building
│   └── Hard Rules, Locations, Politics, Magic - all together
├── [PROJECT] THEME                  # ONE notebook for ALL philosophy
│   └── Central Question, Thesis, Counter-thesis
├── [PROJECT] PLOT                   # Structure and beats
│   └── 15-beat structure, Midpoint type
└── [PROJECT] VOICE                  # Style targets
    └── Favorite passages, Dialogue patterns, Anti-patterns
```

### Why ONE Notebook Per Category (Not Per Entity)

| Old Advice (WRONG) | New Advice (CORRECT) | Why |
|--------------------|----------------------|-----|
| One notebook per character | ALL characters in ONE | AI needs to see Protagonist vs Antagonist goals to detect conflicts |
| Separate World notebooks | ALL world in ONE | AI needs to check if Magic conflicts with Politics |
| Multiple Theme notebooks | ALL themes in ONE | AI needs conflicting ideas to find central argument |

### What Each Core Notebook Contains

**CHARACTER** (All in one):
- Protagonist: Fatal Flaw, The Lie, Arc
- Antagonist: Motivation, Goal, Conflict with protagonist
- Supporting Cast: Roles, Relationships
- Clearly label who is Protagonist/Antagonist

**WORLD** (All in one):
- Hard Rules (CANNOT be broken) - explicitly labeled
- Soft Lore (history, flavor) - can flex
- Locations with plot significance
- Secrets (hidden from readers/characters)

**THEME** (All in one):
- Central Question (phrased as a question)
- Thesis (argument FOR)
- Counter-thesis (argument AGAINST)
- Symbols and their meanings

**PLOT**:
- 15-beat Save the Cat structure
- Midpoint type: False Victory or False Defeat
- Scene ideas mapped to beats

**VOICE**:
- Passages from admired authors
- Dialogue patterns to emulate
- Anti-patterns to AVOID

### Workflow Guide (Updated for Distillation Pipeline)

```
STAGE 1: RAW RESEARCH (Before Writers Factory)
   └── Create UNLIMITED messy notebooks in NotebookLM
   └── Upload sources: podcasts, articles, interviews, favorite authors
   └── This is your "Data Lake" - throw everything at the wall

DISTILLATION STEP (Still in NotebookLM)
   └── Copy Distillation Prompts from Writers Factory docs
   └── Run prompts in raw notebooks to extract structured data
   └── Save outputs to 5 Core Notebooks

STAGE 2: 5 CORE NOTEBOOKS (Register in Writers Factory)
   └── Register exactly 5 notebooks: Character, World, Theme, Plot, Voice
   └── Each notebook contains distilled, structured content
   └── Factory queries these via MCP bridge

EXTRACTION PHASE
   └── Use NotebookLM Panel to query Core Notebooks
   └── Save extractions to workspace/research/{category}/
   └── Files are editable markdown with YAML frontmatter

REVIEW & CONFLICT PHASE
   └── Stage Check: Is this Stage 2 (distilled) or Stage 1 (raw)?
   └── Hard Rules Check: Any violations of World Rules?
   └── Conflict Check: Contradictions with existing research?
   └── Resolve before proceeding

PROMOTION PHASE
   └── Structure Check: Does it have required fields?
   └── Promote to Story Bible with intelligent transformation
   └── Character → Protagonist.md, World → Rules.md, etc.

STAGE 3: STORY BIBLE (content/)
   └── Canonical documents built from promoted research
   └── Protagonist.md, Beat_Sheet.md, Theme.md, Rules.md
   └── Knowledge Graph updated
```

---

## Feature 6: Foreman Product Knowledge (CRITICAL)

### The Problem (Discovered via Testing)

When a user asked "tell me about the notebook", the Foreman (DeepSeek V3) **hallucinated a completely wrong explanation**:

> "In the context of Writers Factory, a Notebook is a flexible organizational tool used by writers to keep their ideas, scenes, and character notes in one place. Think of it as a hybrid between a mind map, an outline, and a note-taking system..."

This is **completely fabricated**. The Foreman doesn't know:
- What NotebookLM actually is (Google's AI research product)
- How it integrates with Writers Factory
- The actual workflow users need to follow

### Why This Happens

The Foreman's system prompt contains no product knowledge. When users ask about app features, the LLM confidently invents plausible-sounding but incorrect answers.

### Required Product Knowledge

The Foreman must understand these core concepts:

```
TERMINOLOGY (CRITICAL - See Terminology Guide above)
- Always say "NotebookLM notebook" - never just "notebook"
- "Research Notes" = saved extractions in Writers Factory
- "Story Bible" = canonical documents in content/
- If unsure about a feature, say "I'm not sure - let me help you find that information"

NOTEBOOKLM NOTEBOOKS (External - Google Product)
- Google's AI-powered research tool at notebooklm.google.com
- Users upload PDFs, docs, web pages as "sources"
- NotebookLM indexes sources and can answer questions about them
- Users create SEPARATE NotebookLM notebooks for different research areas
- This is OUTSIDE Writers Factory - users do this in their browser

WRITERS FACTORY INTEGRATION
- Users REGISTER their NotebookLM notebooks in Writers Factory
- Click NOTEBOOK button in toolbar → paste NotebookLM notebook URL/ID
- Assign a category: Character, World, Voice, Theme, Craft
- Writers Factory can then QUERY these NotebookLM notebooks via MCP bridge

WORKFLOW
1. User creates NotebookLM notebooks in NotebookLM (external)
2. User uploads research documents to each NotebookLM notebook
3. User registers NotebookLM notebook IDs in Writers Factory
4. User uses Characters/World tabs to extract structured info
5. Extractions are saved to Research Notes
6. Foreman uses Research Notes when building Story Bible

STORY BIBLE (Writers Factory Feature)
- Structured documents in content/ directory
- Protagonist.md, Beat_Sheet.md, Theme.md, World_Rules.md
- Built FROM Research Notes, not the same as research
- Foreman guides user through creating these
```

### Implementation Options

1. **System Prompt Addition** (Fastest)
   - Add product knowledge section to `foreman.py` base prompt
   - ~500 tokens of context
   - Always available

2. **KB Seed Entries** (Structured)
   - Pre-populate Foreman KB with product definitions
   - Query on startup and include in context
   - Can be updated without code changes

3. **RAG from Documentation** (Most Flexible)
   - Foreman queries docs/ when user asks about features
   - Always up-to-date with latest docs
   - Higher latency

### Recommended: Hybrid Approach

1. **Core definitions in system prompt** (always available)
2. **Detailed guides in KB** (queryable when needed)
3. **"I don't know" fallback** - If unsure, Foreman should say "Let me check the documentation" rather than guess

---

## Implementation Phases

Each phase has a detailed task specification. Click to view full implementation details.

| Phase | Task Spec | Priority | Dependencies |
|-------|-----------|----------|--------------|
| **Phase 0** | [PHASE0_FOREMAN_KNOWLEDGE.md](./PHASE0_FOREMAN_KNOWLEDGE.md) | HIGH (Blocker) | None |
| **Phase 1** | [PHASE1_FILE_BASED_RESEARCH.md](./PHASE1_FILE_BASED_RESEARCH.md) | HIGH | Phase 0 |
| **Phase 2** | [PHASE2_CONFLICT_DETECTION.md](./PHASE2_CONFLICT_DETECTION.md) | MEDIUM | Phase 1 |
| **Phase 3** | [PHASE3_SCENE_LIFECYCLE.md](./PHASE3_SCENE_LIFECYCLE.md) | MEDIUM | Phase 1 |
| **Phase 4** | [PHASE4_PROMOTION_WORKFLOW.md](./PHASE4_PROMOTION_WORKFLOW.md) | MEDIUM | Phase 1, 2 |
| **Phase 5** | [PHASE5_DOCUMENTATION.md](./PHASE5_DOCUMENTATION.md) | LOW | Phase 0, 1 |

### Summary

- **Phase 0**: Teach Foreman the Distillation Pipeline + 5 Core Notebooks + Distillation Prompts
- **Phase 1**: Save extractions as markdown files with strict 5-category validation
- **Phase 2**: Stage Check + Hard Rules priority + Conflict detection (Stage 2 only)
- **Phase 3**: Track scene status draft→complete (workflow)
- **Phase 4**: Intelligent promotion with Structure Check + category-specific transformation
- **Phase 5**: Distillation Prompts Library + 5 Core Notebooks documentation

---

## Open Questions

1. **NotebookLM Notebook Templates**: Should we provide Google NotebookLM notebook templates users can copy?

2. **Conflict Threshold**: How aggressive should conflict detection be? Too sensitive = noise, too loose = missed contradictions.

3. **Multi-Project**: Does workspace/ need project isolation, or is one workspace per app instance sufficient?

---

## Student Quick-Start Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOTEBOOKLM (Google)                          │
│                  notebooklm.google.com                          │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │ NotebookLM  │  │ NotebookLM  │  │ NotebookLM  │           │
│   │ Notebook:   │  │ Notebook:   │  │ Notebook:   │           │
│   │ "Umar       │  │ "World      │  │ "Voice      │           │
│   │ Research"   │  │ Building"   │  │ Reference"  │           │
│   │             │  │             │  │             │           │
│   │ PDFs, docs, │  │ PDFs, docs, │  │ PDFs, docs, │           │
│   │ web pages   │  │ web pages   │  │ web pages   │           │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘           │
│          │                │                │                   │
└──────────┼────────────────┼────────────────┼───────────────────┘
           │                │                │
           │    Copy NotebookLM notebook IDs │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WRITERS FACTORY                              │
│                                                                 │
│  STEP 1: REGISTER                                               │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │    Click NOTEBOOK button in toolbar                     │   │
│   │    Paste NotebookLM notebook ID → Assign Category → Save│   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  STEP 2: EXTRACT                                                │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │    NotebookLM Panel → Characters/World tabs             │   │
│   │    Ask questions: "What is Umar's fatal flaw?"          │   │
│   │    → Queries your NotebookLM notebooks via MCP bridge   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  STEP 3: SAVE                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │    Click "Save to Research Notes" button                │   │
│   │    → Saved as markdown file in workspace/research/      │   │
│   │    → Appears in File Tree (left panel)                  │   │
│   │    → Also visible in "Saved Notes" tab                  │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  STEP 4: REVIEW & EDIT                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │    Click file in File Tree → Opens in Main Editor       │   │
│   │    • Edit the extraction (fix errors, add notes)        │   │
│   │    • Cmd+S (Mac) or Ctrl+S (Win) to SAVE changes        │   │
│   │    • Changes saved to file on disk automatically        │   │
│   │                                                         │   │
│   │    Repeat: Extract more → Save → Edit → until ready     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  STEP 5: BUILD STORY BIBLE (with Foreman)                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │    Chat with Foreman in ARCHITECT mode                  │   │
│   │    Foreman reads your Research Notes and helps create:  │   │
│   │    • Protagonist.md (character arc, fatal flaw)         │   │
│   │    • Beat_Sheet.md (15-beat structure)                  │   │
│   │    • Theme.md, World_Rules.md                           │   │
│   │                                                         │   │
│   │    These are saved to content/ → your canonical "truth" │   │
│   │    Cmd+S / Ctrl+S to save Story Bible edits             │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

KEY TERMINOLOGY:
• NotebookLM notebook = Your research in Google's NotebookLM (external)
• Research Notes = Saved extractions in Writers Factory (editable files)
• Story Bible = Canonical docs in content/ (Protagonist, Beat Sheet, etc.)

FILE LOCATIONS:
• workspace/research/  → Your Research Notes (drafts, editable)
• content/             → Story Bible (canonical, reviewed)

HOW TO SAVE:
• Cmd+S (Mac) or Ctrl+S (Windows) while in the editor
• Changes save to the file on your computer
• Files live in your chosen Workspace folder (set during onboarding)
```

---

## Related Documentation

- [WRITERS_JOURNEY.md](../WRITERS_JOURNEY.md) - Overall workflow
- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture
- [FOREMAN_KB_SERVICE.md](../BACKEND_SERVICES.md) - Current KB implementation

---

*Created: 2024-12-06*
*Updated: 2024-12-06 - Added Distillation Pipeline, 5 Core Notebooks, Stage/Structure Checks*
*Status: DRAFT - Ready for Implementation*
