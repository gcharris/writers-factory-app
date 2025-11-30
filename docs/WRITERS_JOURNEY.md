# Writers Factory - The Complete Writer's Journey

> A comprehensive guide to the writer's experience from installation to polished manuscript.
> **Purpose**: Testing and debugging reference for QA of the complete workflow.
> **Last Updated**: November 30, 2025

---

## Table of Contents

1. [Journey Overview](#journey-overview)
2. [Phase 0: Installation & Setup](#phase-0-installation--setup)
3. [Phase 1: ARCHITECT Mode](#phase-1-architect-mode---story-bible-creation)
4. [Phase 2: VOICE_CALIBRATION Mode](#phase-2-voice_calibration-mode---finding-the-voice)
5. [Phase 3: DIRECTOR Mode](#phase-3-director-mode---drafting-scenes)
6. [Phase 4: EDITOR Mode](#phase-4-editor-mode---polish--revision)
7. [Complete Workflow Diagram](#complete-workflow-diagram)
8. [Testing Checklist](#testing-checklist)
9. [Known Issues & Blockers](#known-issues--blockers)

---

## Journey Overview

Writers Factory enforces a professional methodology called the **Narrative Protocol**:

> **"Structure Before Freedom"** - Writers must complete foundational artifacts before drafting.

The journey follows **four Foreman modes** that mirror a professional writing process:

```
ARCHITECT → VOICE_CALIBRATION → DIRECTOR → EDITOR
   │              │                 │          │
   │              │                 │          └─ Polish & Revision
   │              │                 └─ Scene Drafting (with scaffolds)
   │              └─ Voice Tournament (find narrative voice)
   └─ Story Bible Creation (structure, characters, theme)
```

**Core Principle**: The Foreman (AI creative partner) guides the writer through each phase, refusing to advance until requirements are met.

---

## Phase 0: Installation & Setup

### Step 0.1: App Installation

**What Happens**:
- Writer downloads and installs the Tauri desktop app
- First launch triggers the **Onboarding Wizard**

**Technical Components**:
- `frontend/src/lib/components/Onboarding/OnboardingWizard.svelte`
- 4-step wizard flow

### Step 0.2: Onboarding Wizard (4 Steps)

#### Step 1: Workspace Location
**Component**: `Step1WorkspaceLocation.svelte`

**Purpose**: Choose where writing projects will be stored.

**User Actions**:
1. See default path suggestion (`~/Documents/Writers Factory`)
2. Click "Browse" to select custom folder (Tauri native dialog)
3. Can choose cloud-synced folders (Dropbox, iCloud)
4. Path is validated via backend (`POST /system/workspace/validate`)

**Success Criteria**:
- [ ] Valid, writable directory selected
- [ ] Path stored in `workspacePath` store (localStorage)

**Backend Endpoints**:
- `GET /system/workspace/default` - Gets default path
- `POST /system/workspace/validate` - Validates path
- `POST /workspace/init` - Creates project structure (called later)

---

#### Step 2: Local AI Setup
**Component**: `Step1LocalAI.svelte`

**Purpose**: Ensure Ollama is installed and working with required models.

**User Actions**:
1. App checks if Ollama is running (`http://localhost:11434`)
2. Verifies required models are installed:
   - `llama3.2:3b` - Fast backup agent
   - `mistral:7b` - The Foreman (main AI partner)
3. If missing, shows installation instructions
4. "Test Connection" button validates setup

**Success Criteria**:
- [ ] Ollama server responding
- [ ] Required models available
- [ ] Test query returns valid response

**Backend Endpoints**:
- `GET /agents/available` - Lists available agents
- Internal Ollama health check

---

#### Step 3: Cloud Models (Optional)
**Component**: `Step2CloudModels.svelte`

**Purpose**: Configure cloud AI providers for enhanced features.

**User Actions**:
1. See list of supported providers:
   - OpenAI (GPT-4o)
   - Anthropic (Claude Sonnet)
   - DeepSeek
   - Qwen (Alibaba)
   - xAI (Grok)
   - Mistral
2. Enter API keys (optional)
3. Test each key to verify validity
4. Can skip - local Ollama is sufficient for basic use

**Success Criteria**:
- [ ] Any entered keys are validated
- [ ] Keys stored securely via Settings Service

**Backend Endpoints**:
- `POST /settings/agents` - Save API keys
- `GET /orchestrator/available-providers` - List providers

---

#### Step 4: Name Your Assistant
**Component**: `Step3NameAssistant.svelte`

**Purpose**: Personalize the Foreman.

**User Actions**:
1. Enter a name for the AI assistant (default: "Foreman")
2. See a preview of the assistant's greeting
3. Click "Finish" to complete onboarding

**Success Criteria**:
- [ ] Assistant name saved
- [ ] Onboarding marked complete in localStorage
- [ ] Main app layout loads

---

### Step 0.3: Project Initialization

**After Onboarding**:
1. Writer clicks "New Project"
2. Enters project title and protagonist name
3. Backend creates folder structure:

```
workspace/
└── projects/
    └── {project_name}/
        └── content/
            ├── Characters/
            ├── Story Bible/
            │   ├── Structure/
            │   └── Themes_and_Philosophy/
            └── World Bible/
```

**Backend Endpoint**: `POST /workspace/init`

**Foreman Initialization**: `POST /foreman/start`
```json
{
  "project_title": "My Novel",
  "protagonist_name": "Alice"
}
```

**Result**: Foreman enters **ARCHITECT mode** and presents the Work Order.

---

## Phase 1: ARCHITECT Mode - Story Bible Creation

### Overview

**Goal**: Build a complete Story Bible with all required structural artifacts.

**Duration**: This is the longest phase. Writers may spend days/weeks here.

**The Foreman's Role**:
- Guides writer through requirements
- Challenges weak structural choices
- Queries NotebookLM for research
- Refuses to advance until Story Bible is complete

### The Work Order

The Foreman maintains a **Work Order** tracking these required templates:

| Template | File Path | Required Fields |
|----------|-----------|-----------------|
| **Protagonist** | `Characters/{name}.md` | fatal_flaw, the_lie, arc_start, arc_resolution |
| **Beat Sheet** | `Story Bible/Structure/Beat_Sheet.md` | beat_1 through beat_15, midpoint_type |
| **Theme** | `Story Bible/Themes_and_Philosophy/Theme.md` | central_theme, theme_statement |
| **World Rules** | `World Bible/Rules.md` | fundamental_rules |

### Step 1.1: Protagonist Creation

**What Writer Does**:
1. Chat with Foreman about their protagonist
2. Define the **Fatal Flaw** (internal weakness)
3. Define **The Lie** (mistaken belief driving the flaw)
4. Map the character arc (start → midpoint → resolution)

**Foreman Challenges**:
- "That sounds like circumstance, not flaw. What's the *internal* weakness?"
- "The Lie must be something they *believe*, not a situation."

**Technical Flow**:
```
User: "My protagonist is poor and desperate"
Foreman: {"action": "save_decision", "category": "character", "key": "situation", "value": "poor and desperate"}
Foreman: "That's circumstance. What internal flaw does this poverty trigger? Fear of vulnerability? Inability to trust?"
```

**Template Generated**: `Protagonist.md` with all sections filled

**Validation**: `StoryBibleService.parse_protagonist()` extracts structured data

---

### Step 1.2: Beat Sheet Construction (15 Beats)

**What Writer Does**:
1. Map their story to the 15-beat "Save the Cat!" structure
2. Define each beat's purpose and content

**The 15 Beats**:

| # | Beat | % | Purpose |
|---|------|---|---------|
| 1 | Opening Image | 1% | "Before" snapshot |
| 2 | Theme Stated | 5% | Theme hinted |
| 3 | Setup | 1-10% | Ordinary world |
| 4 | Catalyst | 10% | Inciting incident |
| 5 | Debate | 10-20% | Protagonist hesitates |
| 6 | Break into Two | 20% | Protagonist commits |
| 7 | B Story | 22% | Subplot begins |
| 8 | Fun & Games | 20-50% | Promise of premise |
| 9 | Midpoint | 50% | FALSE VICTORY or FALSE DEFEAT |
| 10 | Bad Guys Close In | 50-75% | Opposition tightens |
| 11 | All Is Lost | 75% | Lowest point |
| 12 | Dark Night of the Soul | 75-80% | Protagonist despairs |
| 13 | Break into Three | 80% | Solution discovered |
| 14 | Finale | 80-99% | Final confrontation |
| 15 | Final Image | 99-100% | Mirror of opening |

**Critical Choice: Midpoint Type**
- **False Victory**: Things seem to be going well (then collapse)
- **False Defeat**: Things seem hopeless (then turn around)

**Template Generated**: `Beat_Sheet.md`

---

### Step 1.3: Theme Definition

**What Writer Does**:
1. Define the central theme (core idea explored)
2. Write a theme statement (one-sentence encapsulation)

**Example**:
- Central Theme: "The cost of vengeance"
- Theme Statement: "Revenge destroys the avenger more than the target."

**Template Generated**: `Theme.md`

---

### Step 1.4: World Rules

**What Writer Does**:
1. Define fundamental rules of the story world
2. These are non-negotiable laws the AI must respect

**Examples**:
- "Magic requires a physical toll on the caster"
- "FTL travel takes 3 weeks minimum"
- "The dead cannot be brought back"

**Template Generated**: `Rules.md`

---

### Step 1.5: NotebookLM Integration (Optional)

**Purpose**: Writer can register external NotebookLM notebooks as research sources.

**Notebook Roles**:
- **World Notebooks**: Setting, rules, factions
- **Character/Voice Notebooks**: Voice samples, real people models
- **Craft Reference Notebooks**: Favorite novels, films, techniques
- **Project Notebook**: Final synthesized Story Bible (created last)

**Foreman Actions**:
```json
{"action": "query_notebook", "notebook_id": "abc123", "query": "How does the protagonist speak?"}
```

---

### Phase 1 Completion Gate

**Foreman refuses to advance until**:
- [ ] `Protagonist.md` exists with Fatal Flaw and The Lie defined
- [ ] `Beat_Sheet.md` has all 15 beats + midpoint type
- [ ] `Theme.md` has central_theme and theme_statement
- [ ] `Rules.md` has at least 1 fundamental rule

**Check Endpoint**: `GET /story-bible/status`

**Response**:
```json
{
  "phase2_complete": true,
  "completion_score": 100,
  "protagonist": { "is_valid": true, "fatal_flaw": "..." },
  "beat_sheet": { "is_valid": true, "beats": 15 }
}
```

**Transition**: Foreman triggers `{"action": "advance_to_voice_calibration"}`

---

## Phase 2: VOICE_CALIBRATION Mode - Finding the Voice

### Overview

**Goal**: Discover the narrative voice through a tournament of AI agents.

**Duration**: 1-2 sessions (a few hours)

**Output**: Voice Reference Bundle (files that travel with every scene call)

### Step 2.1: Test Passage Design

**What Writer Does**:
1. Work with Foreman to craft a **key scene** (~500 words)
2. Scene should exercise all "voice muscles":
   - Dialogue
   - Action
   - Interiority (internal thoughts)
   - World details

**Why This Scene**:
- This becomes the "gold standard" for voice
- All future scenes will be compared to it

---

### Step 2.2: Agent Selection

**What Writer Does**:
1. See available agents (based on configured API keys)
2. Select 3-5 agents for the tournament
3. Each agent brings different strengths

**Available Agents** (from `agents.yaml`):
| Agent | Strengths |
|-------|-----------|
| Claude Sonnet | Voice, nuance, philosophical depth |
| GPT-4o | Polish, structure, consistency |
| Gemini Pro | Speed, world-building |
| Grok | Unconventional takes, humor |
| DeepSeek | Cost-effective drafts |
| Mistral (local) | Free, decent prose |

**Endpoint**: `GET /tournament/agents`

---

### Step 2.3: Tournament Execution

**What Happens**:
1. Each selected agent generates **5 variants** using different strategies
2. Total: 15-25 variants to review

**The 5 Strategies (Multiplier)**:
| Strategy | Focus |
|----------|-------|
| ACTION_EMPHASIS | Fast pacing, physical detail, momentum |
| CHARACTER_DEPTH | Interior landscape, psychological truth |
| DIALOGUE_FOCUS | Voice through conversation, subtext |
| BRAINSTORMING | Idea exploration, multiple perspectives |
| BALANCED | Harmonious blend of all elements |

**Endpoint**: `POST /tournament/run`
```json
{
  "test_prompt": "...",
  "agents": ["claude-sonnet", "gpt-4o", "deepseek"],
  "context": "..."
}
```

---

### Step 2.4: Variant Review & Selection

**What Writer Does**:
1. Review all generated variants
2. Identify what WORKS and what DOESN'T
3. Articulate WHY certain passages resonate

**Foreman Challenges**:
- "What specifically do you like about this one?"
- "Is it the rhythm? The word choice? The imagery?"

**UI Component**: `VoiceVariantGrid.svelte`

---

### Step 2.5: Winner Selection

**What Writer Does**:
1. Select winning agent + strategy combination
2. Add voice notes (what makes this voice work)

**Endpoint**: `POST /tournament/select-winner`
```json
{
  "agent_id": "claude-sonnet",
  "variant_index": 2,
  "voice_notes": "Love the sparse dialogue, heavy interiority, metaphors from nature"
}
```

---

### Step 2.6: Voice Bundle Generation

**What's Created**:

#### Voice-Gold-Standard.md
- The winning passage
- Detailed voice analysis
- "This is what good looks like"

#### Voice-Anti-Pattern-Sheet.md
- Patterns to AVOID
- Examples of what NOT to do
- Penalty triggers for the scorer

#### Phase-Evolution-Guide.md
- How voice adapts through story arcs
- Act 1 voice vs Act 3 voice
- Earned language progression

#### voice_settings.yaml
- Machine-readable settings
- POV, tense, metaphor domains
- Injected into every agent call

**Endpoint**: `POST /voice-calibration/generate-bundle`

---

### Phase 2 Completion Gate

**Foreman refuses to advance until**:
- [ ] Tournament has been run
- [ ] Winner has been selected
- [ ] Voice Bundle has been generated
- [ ] Writer confirms "voice lock"

**Transition**: `{"action": "advance_to_director"}`

---

## Phase 3: DIRECTOR Mode - Drafting Scenes

### Overview

**Goal**: Write the manuscript scene-by-scene with AI assistance.

**Duration**: The bulk of writing time (weeks/months)

**The Foreman's Role**:
- Maintains Beat Sheet as compass
- Injects Voice Bundle into every call
- Tracks continuity across scenes
- Runs health checks after chapters

### The Director Mode Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIRECTOR MODE PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. DRAFT SUMMARY                                                │
│     └─ Preview what's next, suggest enrichment                   │
│                        ↓                                         │
│  2. SCAFFOLD GENERATION                                          │
│     └─ Full strategic briefing with context                      │
│                        ↓                                         │
│  3. STRUCTURE VARIANTS                                           │
│     └─ 5 different chapter layout options                        │
│                        ↓                                         │
│  4. SCENE GENERATION                                             │
│     └─ Multiple models × strategies = 15+ variants               │
│                        ↓                                         │
│  5. SCORING                                                      │
│     └─ 5-category rubric, 100-point scale                        │
│                        ↓                                         │
│  6. SELECTION                                                    │
│     └─ Writer picks winner or hybrid                             │
│                        ↓                                         │
│  7. ENHANCEMENT                                                  │
│     └─ Polish based on score:                                    │
│        • 85+: Action Prompt (surgical fixes)                     │
│        • 70-84: 6-Pass Enhancement                               │
│        • <70: Return to step 4 (rewrite)                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Step 3.1: Draft Summary

**What Foreman Does**:
1. Presents next scene based on Beat Sheet position
2. Shows what context is available
3. Offers enrichment suggestions (NotebookLM queries)

**Example Conversation**:
```
Foreman: "Alright, next up is Scene 4.1 - this is where the Catalyst hits.
         I have context on Jane's fatal flaw and her relationship with Joe.
         Would you like me to query your World notebook for the location details?"
```

**Service**: `ScaffoldGeneratorService.generate_draft_summary()`

---

### Step 3.2: Scaffold Generation

**After Writer Approves**:
The full scaffold document is generated containing:

| Section | Content |
|---------|---------|
| **Chapter Overview** | Beat, voice state, core function |
| **Strategic Context** | Conflict positioning, character goals, thematic setup |
| **Success Criteria** | Quality thresholds, voice requirements |
| **Continuity Checklist** | Callbacks to include, foreshadowing to plant |
| **Enrichment Data** | Any NotebookLM query results |

**Service**: `ScaffoldGeneratorService.generate_scaffold()`

---

### Step 3.3: Structure Variants

**What Happens**:
Ollama generates 5 different structural approaches for the chapter:

| Variant | Approach |
|---------|----------|
| A | Fast-paced, many short beats |
| B | Slow-burn, character focus |
| C | Dialogue-heavy |
| D | Action sequence |
| E | Balanced blend |

**Writer Selects** preferred structure before scene generation.

**Service**: `SceneWriterService.generate_structure_variants()`

---

### Step 3.4: Scene Generation (Tournament)

**What Happens**:
1. Selected models each write the scene
2. Each model produces 5 variants (different strategies)
3. Total: 15+ scene variants

**Default Tournament Models**:
- Claude Sonnet
- GPT-4o
- DeepSeek

**All Calls Include**:
- The scaffold document
- Voice Bundle files
- Relevant KB entries
- Continuity notes

**Service**: `SceneWriterService.generate_scene_variants()`

---

### Step 3.5: Scoring (5-Category Rubric)

**Each Variant is Scored** (100 points):

| Category | Weight | What It Measures |
|----------|--------|------------------|
| **Voice Authenticity** | 30% | Matches Voice Bundle |
| **Character Consistency** | 20% | Psychology, capabilities |
| **Metaphor Discipline** | 20% | Domain rotation, no similes |
| **Anti-Pattern Compliance** | 15% | Zero-tolerance patterns |
| **Phase Appropriateness** | 15% | Voice complexity for story phase |

**Grade Thresholds**:
- A: 92+
- A-: 85+
- B+: 80+
- B: 75+
- B-: 70+
- C+: 65+
- C: 60+
- D: <60

**Service**: `SceneAnalyzerService.analyze_scene()`

---

### Step 3.6: Selection

**What Writer Does**:
1. Review scored variants
2. Select winner OR request hybrid (combine best parts)
3. Proceed to enhancement

**UI Component**: `SceneVariantGrid.svelte`

---

### Step 3.7: Enhancement

**Based on Score**:

#### Score 85+ → Action Prompt
- Surgical fixes for specific violations
- Preserves what's working
- Fixes only flagged issues

**Service**: `SceneEnhancementService.generate_action_prompt()`

**Output**: Markdown document with specific fixes:
```markdown
### FIX 1: Replace weak verb
**OLD:** "She walked slowly to the door"
**NEW:** "She crept toward the door"
```

---

#### Score 70-84 → 6-Pass Enhancement

**The Six Passes**:

| Pass | Focus |
|------|-------|
| 1 | **Core Consistency** - Verify voice fundamentals |
| 2 | **Clarity** - Ensure each scene purpose is clear |
| 3 | **Rhythm** - Fix sentence flow |
| 4 | **Metaphor** - Check domain discipline |
| 5 | **Sensory** - Enhance imagery |
| 6 | **Polish** - Final word-level refinements |

**Service**: `SceneEnhancementService.apply_six_pass_enhancement()`

---

#### Score <70 → Rewrite
- Return to Step 3.4
- Try different model/strategy combination
- Flag structural issues in scaffold

---

### Step 3.8: Chapter Completion & Health Check

**After Completing a Chapter**:
Foreman recommends running a **Graph Health Check**.

**What Health Checks Detect**:
- Pacing plateaus (flat tension)
- Beat structure deviations
- Timeline consistency problems
- Fatal Flaw challenge frequency
- Supporting character underutilization
- Symbol and theme resonance

**Foreman Action**:
```json
{"action": "run_health_check", "scope": "chapter", "chapter_id": "chapter_4"}
```

**Service**: `GraphHealthService`

---

## Phase 4: EDITOR Mode - Polish & Revision

### Overview

**Goal**: Full manuscript polish and revision.

**Status**: Currently uses same system prompt as DIRECTOR (TODO: dedicated prompt)

**What's Available**:
- Full manuscript review
- Voice consistency checks across chapters
- Timeline validation
- Character arc verification
- Theme resonance scoring

### Step 4.1: Manuscript Health Dashboard

**What Writer Sees**:
- Overall manuscript score
- Chapter-by-chapter breakdown
- Trend analysis (is quality improving?)
- Flagged issues for review

**UI Component**: `GraphHealthDashboard.svelte`

---

### Step 4.2: Full Revision Pass

**What Writer Does**:
1. Address flagged health check issues
2. Run scenes back through enhancement pipeline if needed
3. Verify continuity and callbacks

---

### Step 4.3: Final Polish

**Checklist**:
- [ ] All health checks passing (>80 score)
- [ ] Voice consistent across manuscript
- [ ] All 15 beats present and functioning
- [ ] Fatal Flaw arc complete
- [ ] Theme resonates at key moments

---

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WRITERS FACTORY JOURNEY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 0: SETUP                                                       │    │
│  │   Install App → Onboarding Wizard → Create Project                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                               ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 1: ARCHITECT MODE                                              │    │
│  │                                                                      │    │
│  │   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │    │
│  │   │ Protagonist  │ → │  Beat Sheet  │ → │Theme + World │            │    │
│  │   │ Fatal Flaw   │   │  15 Beats    │   │   Rules      │            │    │
│  │   │ The Lie      │   │  Midpoint    │   │              │            │    │
│  │   └──────────────┘   └──────────────┘   └──────────────┘            │    │
│  │                                                                      │    │
│  │   ✓ Story Bible Complete → GATE PASS                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                               ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 2: VOICE_CALIBRATION MODE                                      │    │
│  │                                                                      │    │
│  │   Design Test    Run Tournament    Select Winner    Generate Bundle  │    │
│  │   Passage    →   (3-5 agents   →   (agent +     →   (Gold Standard, │    │
│  │   (~500 words)    × 5 strategies)   strategy)       Anti-Patterns)  │    │
│  │                                                                      │    │
│  │   ✓ Voice Bundle Generated → GATE PASS                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                               ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 3: DIRECTOR MODE (Repeat for each scene)                       │    │
│  │                                                                      │    │
│  │   Draft     Scaffold   Structure   Scene Gen   Score   Enhance      │    │
│  │   Summary → Generate → Variants → Tournament → 100pt → (85+/70-84)  │    │
│  │                                    15+ variants  rubric              │    │
│  │                                                                      │    │
│  │   After each chapter: Health Check                                   │    │
│  │   ✓ Manuscript Complete → GATE PASS                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                               ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ PHASE 4: EDITOR MODE                                                 │    │
│  │                                                                      │    │
│  │   Health Dashboard → Revision Pass → Final Polish → DONE!           │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Testing Checklist

### Phase 0: Installation & Setup
- [ ] App installs correctly on macOS/Windows
- [ ] Onboarding wizard appears on first launch
- [ ] Workspace location can be selected and validated
- [ ] Ollama connection test works
- [ ] Model availability check works
- [ ] Cloud API key entry and validation works
- [ ] Assistant naming saves correctly
- [ ] Onboarding completion flag persists

### Phase 1: ARCHITECT Mode
- [ ] Foreman starts in ARCHITECT mode
- [ ] Work Order displays with 4 templates
- [ ] Protagonist template can be created via chat
- [ ] Fatal Flaw validation catches circumstance vs. internal flaw
- [ ] Beat Sheet can be filled (15 beats)
- [ ] Midpoint type selection works
- [ ] Theme and World Rules can be created
- [ ] NotebookLM integration works (if configured)
- [ ] Story Bible status check returns accurate data
- [ ] Gate prevents advancing with incomplete Bible
- [ ] Transition to VOICE_CALIBRATION works when complete

### Phase 2: VOICE_CALIBRATION Mode
- [ ] Available agents list shows correctly
- [ ] Agent selection UI works
- [ ] Tournament runs without errors
- [ ] All 5 strategies generate variants
- [ ] Variants display in grid
- [ ] Winner selection saves correctly
- [ ] Voice Bundle generates all 3 files + YAML
- [ ] Gate prevents advancing without bundle
- [ ] Transition to DIRECTOR works

### Phase 3: DIRECTOR Mode
- [ ] Draft summary generates correctly
- [ ] Enrichment suggestions appear (if notebooks configured)
- [ ] Full scaffold generates with all sections
- [ ] Structure variants generate (5 options)
- [ ] Scene tournament runs with multiple models
- [ ] All 5 strategies produce variants
- [ ] Scoring runs on all variants
- [ ] Score breakdown shows 5 categories
- [ ] Selection saves correctly
- [ ] Action Prompt generates for 85+ scores
- [ ] 6-Pass Enhancement works for 70-84 scores
- [ ] Rewrite triggers for <70 scores
- [ ] Health checks run after chapter completion
- [ ] Continuity tracking works across scenes

### Phase 4: EDITOR Mode
- [ ] Mode transition from DIRECTOR works
- [ ] Health dashboard displays manuscript status
- [ ] Can re-run scenes through enhancement
- [ ] Final health check returns accurate status

### Cross-Phase Tests
- [ ] Knowledge Graph updates as work progresses
- [ ] Session history persists across restarts
- [ ] Work Order status persists across restarts
- [ ] File tree shows created files
- [ ] Files can be opened in editor
- [ ] Settings changes take effect immediately

---

## Known Issues & Blockers

### Current Issues (as of Nov 30, 2025)

| Issue | Severity | Impact |
|-------|----------|--------|
| FileTree file loading broken | HIGH | Writers can't open files to edit |
| EDITOR mode uses DIRECTOR prompt | LOW | Missing dedicated editor guidance |
| ~1028 TypeScript type errors | MEDIUM | May cause runtime issues |

### Blockers for Testing

1. **FileTree**: Must fix Tauri FS integration before testing file workflow
2. **Work Orders UI**: Incomplete - can't visualize Foreman tasks

### Workarounds

- **FileTree**: Use external editor (Typora) for now
- **Work Orders**: Check Foreman chat for task status

---

## API Endpoint Reference

### Setup & Initialization
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/system/workspace/default` | GET | Get default workspace path |
| `/system/workspace/validate` | POST | Validate workspace path |
| `/workspace/init` | POST | Create project structure |
| `/foreman/start` | POST | Initialize Foreman for project |

### Foreman & Chat
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/foreman/chat` | POST | Send message to Foreman |
| `/foreman/status` | GET | Get Foreman state |
| `/foreman/notebook` | POST | Register NotebookLM notebook |
| `/foreman/reset` | POST | Reset for new project |

### Story Bible
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/story-bible/status` | GET | Check Bible completeness |
| `/story-bible/scaffold` | POST | Generate template structure |

### Voice Calibration
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tournament/agents` | GET | List available agents |
| `/tournament/run` | POST | Run voice tournament |
| `/tournament/select-winner` | POST | Select winning variant |
| `/voice-calibration/generate-bundle` | POST | Generate Voice Bundle |

### Director Mode
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/director/draft-summary` | POST | Generate draft summary |
| `/director/scaffold` | POST | Generate full scaffold |
| `/director/structure-variants` | POST | Generate structure options |
| `/director/scene-variants` | POST | Run scene tournament |
| `/director/analyze` | POST | Score a scene |
| `/director/enhance` | POST | Enhance a scene |

### Health
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health/check` | POST | Run health check |
| `/health/dashboard` | GET | Get dashboard data |
| `/health/trends` | GET | Get historical trends |

---

*Document created by Claude (eloquent-raman agent) for QA testing and debugging purposes.*
