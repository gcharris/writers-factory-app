# Director Mode Specification

**Version**: 2.0
**Date**: November 23, 2025
**Status**: Backend Implementation Complete ✅

---

## Executive Summary

Director Mode is the second operational mode of the Foreman agent, activated after the Story Bible is complete. It orchestrates the **scene creation pipeline** - a multi-stage process that generates, scores, and enhances scenes using a combination of:

- **Tournament**: Multiple AI agents compete on the same task
- **Multiplier**: Each agent generates 5 creative variants
- **Scoring**: 100-point rubric evaluates all variants
- **Enhancement**: Surgical fixes polish the selected scene

This document specifies the complete workflow from Story Bible completion through final scene delivery.

---

## Prerequisites

Before Director Mode activates, the following must be complete:

### From Architect Mode (Phase 2A)
- [ ] Protagonist template (Fatal Flaw, The Lie, Arc)
- [ ] Beat Sheet (15 beats with percentages)
- [ ] Theme (central theme, theme statement)
- [ ] World Rules (fundamental constraints)
- [ ] Cast (supporting characters by function)

### From Voice Calibration (Phase 2B)
- [ ] Voice Calibration Document
- [ ] Winning agent identified
- [ ] Reference samples saved

---

## Phase 2B: Voice Calibration

### Purpose

Establish the narrative voice before any scene writing begins. This is a **tournament** where multiple agents compete to capture the writer's desired voice.

### Inputs

The writer provides one or more of:

| Input Type | Description | Example |
|------------|-------------|---------|
| **Voice Samples Notebook** | NotebookLM notebook with real person's voice | YouTube videos, podcasts, speeches |
| **Reference Novels Notebook** | NotebookLM notebook with style references | "Catcher in the Rye", "Gone Girl" |
| **Writer's Description** | Direct description of desired voice | "First person, cynical gambler, uses con-artist metaphors" |

### Process

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VOICE CALIBRATION TOURNAMENT                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Step 1: Writer provides test text                                  │
│  ─────────────────────────────────                                  │
│  A paragraph or short scene (200-500 words) that will be used      │
│  to test each agent's ability to capture the voice.                │
│                                                                      │
│  Step 2: Query NotebookLM for voice context                        │
│  ──────────────────────────────────────────                        │
│  If voice notebooks exist, extract:                                 │
│  • Speech patterns, vocabulary                                      │
│  • Metaphor domains                                                 │
│  • Rhythm and sentence structure                                    │
│  • Characteristic phrases                                           │
│                                                                      │
│  Step 3: Tournament + Multiplier                                    │
│  ────────────────────────────────                                   │
│  Each agent generates 5 variants of the test text:                 │
│                                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │ Claude  │  │ GPT-4o  │  │ Gemini  │  │  Grok   │  │DeepSeek │  │
│  │  ×5     │  │  ×5     │  │  ×5     │  │  ×5     │  │  ×5     │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│                                                                      │
│  Total: 25 voice samples                                            │
│                                                                      │
│  Step 4: Writer selection                                           │
│  ────────────────────────                                           │
│  Writer reviews all 25 samples and selects:                        │
│  • Winning agent (for this project)                                │
│  • Best variant(s) as reference samples                            │
│  • Optional: Hybrid elements from multiple variants                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Output: Voice Calibration Document

```markdown
# Voice Calibration: [Project Title]

## Narrative Structure
- **POV**: First person / Third limited / Third omniscient
- **Tense**: Past / Present
- **Voice Type**: Character voice / Author voice

## Voice Characteristics
- **Metaphor Domains**: [e.g., gambling, performance, addiction, martial arts]
- **Sentence Rhythm**: [e.g., short punchy, long flowing, varied]
- **Vocabulary Level**: [e.g., literary, accessible, technical]
- **Characteristic Phrases**: [examples from winning variants]

## Anti-Patterns (Avoid)
- [e.g., "like/as" similes - use direct metaphors instead]
- [e.g., Computer metaphors for psychology]
- [e.g., Academic meta-commentary]

## Phase Evolution
How the voice changes through the story:
- **Phase 1** (Act 1): [description]
- **Phase 2** (Act 2): [description]
- **Phase 3** (Act 3): [description]

## Tournament Results
- **Winning Agent**: [e.g., Claude Sonnet 4.5]
- **Runner-up**: [e.g., GPT-4o]
- **Reference Samples**: [links to saved winning variants]

## Voice Authentication Tests
1. **Observer Test**: Does this sound like [character] observing?
2. **Consistency Test**: Does this match the reference samples?
3. **Anti-Pattern Test**: Are forbidden patterns absent?
```

### KB Persistence

Voice decisions are saved to `foreman_kb` with category `voice`:
- `voice_pov`: "first_person"
- `voice_tense`: "past"
- `voice_winning_agent`: "claude-sonnet-4-5"
- `voice_metaphor_domains`: "gambling, performance, addiction"
- `voice_anti_patterns`: "similes, computer_metaphors, academic_commentary"

---

## Phase 3: Director Mode (Scene Creation)

### Work Order Structure

Director Mode tracks a different Work Order than Architect Mode:

```
DIRECTOR WORK ORDER: [Project Title]
Mode: DIRECTOR
Chapter: [Current Chapter Number]

Scene Slots:
  □ Scene 1: [Title] - NOT_STARTED
  ◐ Scene 2: [Title] - IN_PROGRESS (variants generated)
  ◑ Scene 3: [Title] - DRAFT_READY (selected, needs enhancement)
  ✓ Scene 4: [Title] - COMPLETE

Chapter Status: 25% complete
```

### Step 1: Scaffold Generation

For each chapter, the Foreman generates a **Gold Standard Scaffold** by reading from the Knowledge Graph.

#### Scaffold Template (ACE Format)

```markdown
# [Chapter Number]: [Chapter Title]
**For Multi-Agent Scene Pipeline**

---

## Chapter Overview
- **Title**: [Chapter Title]
- **Target Length**: [Word count] (Estimate [N] scenes)
- **Phase**: [Act and phase in story]
- **Voice**: [Voice state for this phase] - [Metaphor domains]
- **Core Function**: [What this chapter accomplishes]

---

## Strategic Context
- **Conflict Positioning**: [Role in story's central conflict]
- **Antagonist Goal**: [What opposition wants in this chapter]
- **Thematic Setup**: [How theme manifests]
- **Protagonist Constraint**: [Current limitations/bonds]

---

## Voice Requirements
- **Narrator**: [POV character] with [voice characteristics]
- **Phase Calibration**: [Appropriate metaphor style for this phase]
- **Key Voice Markers**: [Specific tells for this chapter]
- **Anti-Patterns**: [What to avoid]

---

## Continuity Checklist
- **Callbacks Required**: [References to previous chapters]
- **Character State**: [Current emotional/physical states]
- **Foreshadowing**: [Setup for future developments]
- **Technical Continuity**: [World rules to maintain]

---

## Success Criteria
- Overall quality score > 85 (A- minimum)
- Voice authenticity > 80
- Philosophical integration seamless with action
- Technical concepts accessible through character voice

---

## Scene Breakdown
1. **Scene 1**: [Beat] - [Summary]
2. **Scene 2**: [Beat] - [Summary]
3. **Scene 3**: [Beat] - [Summary]
[etc.]

---

**Ready for Multi-Agent Pipeline**
```

### Step 2: Chapter Layout Exploration

Before writing individual scenes, explore different chapter structures.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHAPTER LAYOUT VARIANTS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Generate 5 different structural approaches:                        │
│                                                                      │
│  Variant 1: Action-heavy (5 scenes, fast pacing)                   │
│  ├── Scene 1: [beat] - 800 words                                   │
│  ├── Scene 2: [beat] - 1000 words                                  │
│  ├── Scene 3: [beat] - 800 words                                   │
│  ├── Scene 4: [beat] - 1200 words                                  │
│  └── Scene 5: [beat] - 1200 words                                  │
│                                                                      │
│  Variant 2: Character-focused (3 scenes, deeper psychology)        │
│  ├── Scene 1: [beat] - 1800 words                                  │
│  ├── Scene 2: [beat] - 2000 words                                  │
│  └── Scene 3: [beat] - 1800 words                                  │
│                                                                      │
│  Variant 3: Dialogue-driven (4 scenes, conversation-centered)      │
│  [etc.]                                                             │
│                                                                      │
│  Variant 4: Experimental (non-linear, flashbacks)                  │
│  [etc.]                                                             │
│                                                                      │
│  Variant 5: Balanced (mix of action/character/dialogue)            │
│  [etc.]                                                             │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  External Review (Optional):                                        │
│  Share variants with Gemini/human for fresh perspective            │
│                                                                      │
│  Selection:                                                         │
│  Writer chooses best structure OR creates hybrid                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Step 3: Scene Generation Pipeline

For each scene in the selected chapter structure:

#### Generation Options

| Option | Agents | Variants/Agent | Total Variants | Use Case |
|--------|--------|----------------|----------------|----------|
| **A: Multiplier Only** | 1 (winning) | 5 | 5 | Fast, economical |
| **B: Tournament Only** | 3-5 | 1 | 3-5 | Agent comparison |
| **C: Tournament + Multiplier** | 3 | 5 | 15 | Balanced exploration |
| **D: Full Power** | 5 | 5 | 25 | Maximum creativity |

#### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SCENE GENERATION PIPELINE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  INPUT: Scene scaffold (from chapter structure)                     │
│  ───────────────────────────────────────────                        │
│  • Scene number and title                                           │
│  • Beat it serves                                                   │
│  • Content summary                                                  │
│  • Word count target                                                │
│  • Voice requirements (from Voice Calibration)                      │
│  • Continuity context (from Knowledge Graph)                        │
│                                                                      │
│  GENERATION (Option C example - Tournament + Multiplier)            │
│  ───────────────────────────────────────────────────────            │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │  ┌─────────┐      ┌─────────┐      ┌─────────┐             │   │
│  │  │ Claude  │      │ GPT-4o  │      │ Gemini  │             │   │
│  │  └────┬────┘      └────┬────┘      └────┬────┘             │   │
│  │       │                │                │                   │   │
│  │       ▼                ▼                ▼                   │   │
│  │  ┌─────────┐      ┌─────────┐      ┌─────────┐             │   │
│  │  │ v1, v2  │      │ v1, v2  │      │ v1, v2  │             │   │
│  │  │ v3, v4  │      │ v3, v4  │      │ v3, v4  │             │   │
│  │  │ v5      │      │ v5      │      │ v5      │             │   │
│  │  └─────────┘      └─────────┘      └─────────┘             │   │
│  │                                                              │   │
│  │  Total: 15 variants                                         │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  SCORING                                                            │
│  ───────                                                            │
│  All 15 variants scored on 100-point rubric:                       │
│                                                                      │
│  │ Variant      │ Voice │ Char │ Meta │ Anti │ Phase │ TOTAL │     │
│  │──────────────│───────│──────│──────│──────│───────│───────│     │
│  │ Claude v3    │  28   │  19  │  18  │  14  │  14   │  93   │ ⭐  │
│  │ GPT-4o v2    │  27   │  18  │  19  │  15  │  13   │  92   │     │
│  │ Claude v1    │  26   │  18  │  17  │  14  │  14   │  89   │     │
│  │ Gemini v4    │  25   │  17  │  18  │  13  │  13   │  86   │     │
│  │ [etc.]       │       │      │      │      │       │       │     │
│                                                                      │
│  SELECTION                                                          │
│  ─────────                                                          │
│  Writer reviews top-scoring variants and:                          │
│  • Selects single best variant, OR                                 │
│  • Creates hybrid (e.g., Claude v3 opening + GPT-4o v2 dialogue)  │
│                                                                      │
│  ENHANCEMENT                                                        │
│  ───────────                                                        │
│  Selected scene → Analyzer generates Action Prompt                 │
│  Action Prompt → Enhancer applies surgical fixes                   │
│  Target: Score improvement to 95+                                  │
│                                                                      │
│  OUTPUT: Enhanced scene file                                        │
│  ────────────────────────────                                       │
│  • [volume].[chapter].[scene] [✓].md                              │
│  • Archived variants in Archive/                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Step 4: Chapter Assembly

After all scenes are complete:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHAPTER ASSEMBLY                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Combine enhanced scenes                                         │
│     [2.5.1 ✓].md + [2.5.2 ✓].md + [2.5.3 ✓].md → [2.5.0].md       │
│                                                                      │
│  2. Full chapter enhancement pass                                   │
│     • Check transitions between scenes                              │
│     • Verify voice consistency across chapter                       │
│     • Run anti-pattern audit                                        │
│                                                                      │
│  3. Final scoring                                                   │
│     • Target: Chapter score > 85                                   │
│     • All scenes individually > 80                                 │
│                                                                      │
│  4. Archive and mark complete                                       │
│     • Working files → Archive/                                     │
│     • Final: [2.5.0 Chapter Title ✓].md                           │
│                                                                      │
│  5. Update Knowledge Graph                                          │
│     • New character states                                          │
│     • Plot developments                                             │
│     • World rule applications                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Scoring Rubric

### 100-Point Scale

| Category | Weight | Description |
|----------|--------|-------------|
| **Voice Authenticity** | 30% | Observer Test, Consciousness War Test, Cognitive Fusion Test |
| **Character Consistency** | 20% | Psychology, capabilities, relationships, motivations |
| **Metaphor Discipline** | 20% | Domain rotation, limits per domain, direct vs. simile |
| **Anti-Pattern Compliance** | 15% | Zero-tolerance violations, formulaic patterns |
| **Phase Appropriateness** | 15% | Voice complexity matches story phase |

### Quality Tiers

| Score | Tier | Action |
|-------|------|--------|
| 95-100 | GOLD STANDARD | Publish as-is |
| 90-94 | A+ EXCELLENT | Minor polish only |
| 85-89 | A STRONG | Enhancement pass recommended |
| 80-84 | A- GOOD | 1-2 specific issues to address |
| 75-79 | B+ ACCEPTABLE | Enhancement required |
| 70-74 | B FUNCTIONAL | Multiple issues, systematic enhancement |
| 65-69 | B- WEAK | Consider regeneration |
| <65 | FAIL | Regenerate with different approach |

### Voice Authentication Tests

1. **Observer Test**: Does this sound like [character] observing, or AI explaining [character]'s observations?

2. **Consistency Test**: Does this match the Voice Calibration reference samples?

3. **Anti-Pattern Test**: Are forbidden patterns (similes, computer metaphors, etc.) absent?

---

## File Naming Convention

### Standard Format: `volume.chapter.scene`

```
Scaffolds:
  2.5.0 [Title]_SCAFFOLD.md         Chapter-level scaffold

Structure:
  2.5.0_LAYOUT_VARIANTS.md          5 structural options
  2.5.0_FINAL_STRUCTURE.md          Chosen structure

Scene Development:
  2.5.1_VARIANTS.md                 5+ variants for scene 1
  2.5.1_DRAFT.md                    Selected/hybrid version
  2.5.1_ENHANCED.md                 After enhancement pass
  2.5.1 [✓].md                      Final approved scene

Chapter Assembly:
  2.5.0_ASSEMBLED.md                All scenes combined
  2.5.0_ENHANCED.md                 After chapter enhancement
  2.5.0 [Title] [✓].md              Final approved chapter

Archive:
  Archive/2.5.1_VARIANTS.md         Working files preserved
  Archive/2.5.0 [original].md       Pre-enhancement versions
```

---

## API Endpoints (Implemented ✅)

All endpoints are available at `http://localhost:8000`. Total: 16 Director Mode endpoints.

### Scaffold Generation

```
POST /director/scaffold/draft-summary
  Stage 1: Generate draft summary with enrichment suggestions
  Body: { project_id, chapter_number, scene_number, beat_info, characters, scene_description }

POST /director/scaffold/enrich
  Fetch enrichment data from NotebookLM
  Body: { notebook_id, query }

POST /director/scaffold/generate
  Stage 2: Generate full scaffold with optional enrichment
  Body: { project_id, chapter_number, scene_number, title, beat_info, characters, ... }
```

### Scene Writing

```
POST /director/scene/structure-variants
  Generate 5 structural approaches before prose
  Body: { scene_id, beat_description, scaffold?, pov_character, target_word_count }

POST /director/scene/generate-variants
  Multi-model tournament with 5 strategies each
  Body: { scene_id, scaffold, structure_variant, voice_bundle_path?, models?, strategies? }

POST /director/scene/create-hybrid
  Combine best elements from multiple variants
  Body: { scene_id, variant_ids, sources, instructions }

POST /director/scene/quick-generate
  Fast single-model generation (no tournament)
  Body: { scene_id, scaffold, voice_bundle_path?, strategy, target_word_count }
```

### Scene Analysis

```
POST /director/scene/analyze
  Full 5-category analysis with scoring
  Body: { scene_id, scene_content, pov_character, phase, voice_bundle_path?, story_bible? }

POST /director/scene/compare
  Analyze and rank multiple variants
  Body: { variants: {model: content}, pov_character, phase, voice_bundle_path? }

POST /director/scene/detect-patterns
  Quick anti-pattern detection (real-time feedback)
  Body: scene_content (string)

POST /director/scene/analyze-metaphors
  Quick metaphor domain analysis
  Body: scene_content, voice_bundle_path?
```

### Scene Enhancement

```
POST /director/scene/enhance
  Auto-select enhancement mode based on score
  Body: { scene_id, scene_content, phase, voice_bundle_path?, story_bible?, force_mode? }

POST /director/scene/action-prompt
  Generate surgical fixes (preview only)
  Body: { scene_id, scene_content, phase, voice_bundle_path? }

POST /director/scene/apply-fixes
  Apply OLD → NEW replacements
  Body: { scene_id, scene_content, fixes: [{old_text, new_text, ...}] }

POST /director/scene/six-pass
  Force full 6-pass enhancement ritual
  Body: { scene_id, scene_content, phase, voice_bundle_path?, story_bible? }
```

### Foreman Mode Control (existing)

```
POST /foreman/mode/director
  Transition Foreman to Director Mode (requires Story Bible complete)

GET /foreman/mode
  Get current mode and transition eligibility
```

---

## Implementation Status

### Phase 1: Voice Calibration Infrastructure ✅
- [x] Voice tournament endpoint (`/voice-calibration/tournament/*`)
- [x] Multi-agent parallel generation
- [x] Voice Calibration Document template
- [x] KB persistence for voice decisions
- [x] Voice Bundle generation (`/voice-calibration/generate-bundle`)

### Phase 2: Scaffold Generation ✅
- [x] Two-stage scaffold flow (Draft Summary → Full Scaffold)
- [x] NotebookLM enrichment integration
- [x] Runs on Ollama (free, local)
- [ ] Structure selection UI (Phase 5)

### Phase 3: Scene Pipeline ✅
- [x] Tournament + Multiplier generation (3 models × 5 strategies = 15 variants)
- [x] 5-category scoring rubric implementation
- [x] Variant comparison endpoint
- [x] Enhancement action prompt generation
- [ ] Variant comparison UI (Phase 5)

### Phase 4: Enhancement Pipeline ✅
- [x] Action Prompt mode (surgical fixes)
- [x] 6-Pass Enhancement mode
- [x] Auto-mode selection based on score
- [x] Re-scoring after enhancement

### Phase 5: Foreman Orchestration ✅
- [x] Director Mode action handlers in foreman.py
- [x] `generate_draft_summary`, `enrich_scaffold`, `generate_scaffold` actions
- [x] `write_scene`, `analyze_scene`, `enhance_scene` actions
- [x] `advance_to_editor` mode transition

### Remaining Work (Phase 5 - Frontend)
- [ ] Frontend UI for scaffold review
- [ ] Structure variant selection UI
- [ ] Scene variant comparison/selection UI
- [ ] Enhancement review UI

---

## Appendix A: Multiplier Science

Research shows that asking an LLM for multiple variants (5+) forces genuinely different creative approaches rather than surface-level rewording. The "verbalized sampling" technique uses probability targets:

- **0.07-0.08**: Highly creative approaches (often best)
- **0.09-0.11**: Creative but accessible
- **0.12-0.14**: Broad appeal, safer choices

When combined with tournament (multiple agents), the exploration space multiplies:
- 5 agents × 5 variants = 25 unique approaches
- Different agents have different creative biases
- Combination maximizes chance of finding optimal solution

---

## Appendix B: Tournament Agent Strengths

| Agent | Strengths | Best For |
|-------|-----------|----------|
| **Claude Sonnet** | Nuance, philosophical depth, voice consistency | Literary fiction, complex characters |
| **GPT-4o** | Polish, structure, technical accuracy | Plot-driven scenes, dialogue |
| **Gemini Pro** | Speed, world-building, research integration | Exposition, setting description |
| **Grok** | Unconventional takes, humor, edge | Unique voices, breaking conventions |
| **DeepSeek** | Cost-effective, reliable baseline | Draft generation, bulk work |

---

## Appendix C: Vanilla Skill Requirements

The original Explants skills were project-specific (Mickey Bardot voice, Consciousness War theme, specific metaphor domains). For Writers Factory, skills must be **vanilla** (work for any novel). This appendix defines how each skill translates from project-specific to universal.

---

### C.1 Smart Scaffold Generator

**Original (Explants)**: Used ACE template with Mickey's voice requirements, three-way ideological war positioning, specific antagonist goals, and Techno-Feudal terminology.

**Vanilla Version**: Generates Gold Standard Scaffold for any chapter using Story Bible context.

#### Required Inputs (from Knowledge Graph/Story Bible)
```
MANDATORY:
- chapter_number: int
- chapter_title: string
- act_number: int
- act_title: string
- setting: string (location, time)
- pov_character: string
- beats: list[string] (key plot points)
- word_count_target: int

FROM STORY BIBLE:
- voice_calibration: object (from Phase 2B)
- character_states: dict (current emotional/physical state of characters)
- protagonist_constraint: string (current limitation from Fatal Flaw)
- theme_manifestation: string (how theme appears in this chapter)
- conflict_positioning: string (role in central conflict)
- continuity_callbacks: list[string] (previous chapter references)
- foreshadowing_requirements: list[string] (setup for future)
```

#### Output Template
```markdown
# [Chapter Number]: [Chapter Title]
**For Multi-Agent Scene Pipeline**

---

## Chapter Overview
- **Title**: [from input]
- **Target Length**: [word_count_target] (Estimate [N] scenes)
- **Phase**: [act_title]
- **Voice**: [from voice_calibration.voice_state] - [voice_calibration.metaphor_domains]
- **Core Function**: [derived from beat_sheet position]

---

## Strategic Context
- **Conflict Positioning**: [from conflict_positioning]
- **Antagonist Goal**: [derived from character_states of antagonist]
- **Thematic Setup**: [from theme_manifestation]
- **Protagonist Constraint**: [from protagonist_constraint - Fatal Flaw expression]

---

## Voice Requirements
- **Narrator**: [pov_character] with [voice_calibration characteristics]
- **Phase Calibration**: [voice_calibration.phase_evolution for this act]
- **Key Voice Markers**: [voice_calibration.characteristic_phrases]
- **Anti-Patterns**: [voice_calibration.anti_patterns]

---

## Continuity Checklist
- **Callbacks Required**: [from continuity_callbacks]
- **Character State Consistency**: [from character_states]
- **Foreshadowing Requirements**: [from foreshadowing_requirements]
- **World Rule Compliance**: [from world_rules in Story Bible]

---

## Success Criteria
- Overall quality score > [threshold from project settings, default 85]
- Voice authenticity > [threshold, default 80]
- Character consistency verified against Story Bible
- Thematic integration seamless with action

---

## Scene Breakdown
[Generated from beats - each beat becomes 1-2 scenes]
1. **Scene 1**: [Beat 1] - [Summary derived from beat]
2. **Scene 2**: [Beat 2] - [Summary]
[etc.]

---

**Ready for Multi-Agent Pipeline**
```

---

### C.2 Scene Writer

**Original (Explants)**: Hardcoded Enhanced Mickey Bardot voice rules (retrospective narrator, quantum hindsight, specific metaphor domains, zero-tolerance for first-person italics).

**Vanilla Version**: Generates scenes matching any Voice Calibration Document.

#### Required Inputs
```
MANDATORY:
- scene_scaffold: object (from Scaffold Generator)
- voice_calibration: object (from Phase 2B)

FROM VOICE CALIBRATION:
- pov: "first_person" | "third_limited" | "third_omniscient"
- tense: "past" | "present"
- voice_type: "character_voice" | "author_voice"
- metaphor_domains: list[string]
- sentence_rhythm: string
- vocabulary_level: string
- characteristic_phrases: list[string]
- anti_patterns: list[string]
- phase_evolution: dict[act -> voice_state]

FROM STORY BIBLE:
- character_psychology: object (for POV character)
- character_capabilities: list[string]
- relationship_dynamics: dict
```

#### Core Voice Rules (Universal)
```
Rule A: Process Over Noun
- Consciousness/emotion/action words are VERBS, not static nouns
- ✅ "Fear moved through him"
- ❌ "He felt fear"

Rule B: Appropriate Distance
- If voice_type == "character_voice": Character experiences directly
- If voice_type == "author_voice": Narrator observes character

Rule C: Metaphor Style
- If anti_patterns includes "similes": Use direct metaphors
  ✅ "Sunlight weaponized itself"
  ❌ "Sunlight was like a weapon"
- Otherwise: Follow project preference

Rule D: Domain Discipline
- Rotate through metaphor_domains
- No single domain > 30% of total metaphors
- Primary domain (first in list) can go to 40%
```

#### Quality Standards
```
- Word count: 800-1200 words per scene (adjustable)
- Metaphors: 2-4 per scene, rotated domains
- Sensory details: 3+ per scene section
- Dialogue: Grounded in physical action
```

---

### C.3 Scene Multiplier

**Original (Explants)**: Generated 5 variants with transformation-specific strategies (QBV Emergence, Identity Recursion, Harmonic Integration).

**Vanilla Version**: Generates 5 creative variants using universal diversification strategies.

#### Diversification Strategies (Universal)

```
Strategy A: ACTION EMPHASIS
- Fast pacing, physical detail
- External conflict foregrounded
- Dialogue in motion
- Best for: Chase scenes, fights, discoveries

Strategy B: CHARACTER DEPTH
- Slower pacing, internal landscape
- Psychology and motivation foregrounded
- Rich introspection
- Best for: Decision points, revelations, quiet moments

Strategy C: DIALOGUE FOCUS
- Conversation-centered
- Conflict through words
- Subtext and tension
- Best for: Confrontations, negotiations, relationship beats

Strategy D: ATMOSPHERIC
- Setting as character
- Sensory immersion
- Mood and tone emphasized
- Best for: Openings, transitions, building dread

Strategy E: BALANCED
- Mix of all elements
- Standard scene structure
- Reliable execution
- Best for: Default approach
```

#### Output Format
```xml
<response id="1">
<strategy>ACTION_EMPHASIS</strategy>
<text>[Scene variant 1]</text>
<probability>0.08</probability>
</response>

<response id="2">
<strategy>CHARACTER_DEPTH</strategy>
<text>[Scene variant 2]</text>
<probability>0.09</probability>
</response>

[Continue for 5 variants]
```

#### What to Diversify
- Pacing and rhythm
- Balance of action/introspection/dialogue
- Metaphor selection (within domains)
- Scene structure (linear vs. fragmented)
- Emotional beats and tension

#### What NOT to Diversify
- Character voice (maintain authenticity)
- POV/perspective (respect voice_calibration)
- World rules (stay within Story Bible)
- Plot requirements (hit required beats)

---

### C.4 Scene Analyzer/Scorer

**Original (Explants)**: 100-point rubric with Mickey-specific tests (Observer Test, Consciousness War Test, Cognitive Fusion Test).

**Vanilla Version**: 100-point rubric with universal voice authentication.

#### Universal Scoring Framework

```
| Category               | Weight | Criteria |
|------------------------|--------|----------|
| Voice Authenticity     | 30%    | Voice Calibration compliance |
| Character Consistency  | 20%    | Story Bible compliance |
| Metaphor Discipline    | 20%    | Domain rotation, style rules |
| Anti-Pattern Compliance| 15%    | Absence of forbidden patterns |
| Phase Appropriateness  | 15%    | Voice evolution stage match |
```

#### Voice Authentication Tests (Universal)

**Test 1: Authenticity Test (replaces Observer Test)**
```
Question: Does this sound like [POV character] experiencing/observing,
          or AI explaining what [character] experiences/observes?

10 points: Character in moment, voice natural
7 points:  Mostly authentic, occasional AI-explaining-character moments
4 points:  Mix of authentic and academic commentary
0 points:  Sounds like AI studying character, not character's voice
```

**Test 2: Purpose Test (replaces Consciousness War Test)**
```
Question: Does this scene serve its story function?

10 points: Every beat advances plot AND develops character AND reinforces theme
7 points:  Serves function but sometimes tells instead of shows
4 points:  Generic well-written prose, function tangential
0 points:  Scene doesn't serve story needs
```

**Test 3: Fusion Test (replaces Cognitive Fusion Test)**
```
Question: Does voice integrate knowledge and personality seamlessly?

10 points: Character knowledge serves voice naturally
7 points:  Mostly seamless, occasional info-dump moments
4 points:  Knowledge OR personality, not fused
0 points:  Academic exposition without character grounding
```

#### Anti-Pattern Detection (Universal)

```python
# Configure from voice_calibration.anti_patterns

DEFAULT_ZERO_TOLERANCE = [
    r'\*[^*]*\b(we|I)\b[^*]*\*',  # First-person italics (if applicable)
    r'\bwith \w+ precision\b',     # "with X precision" filler
]

DEFAULT_FORMULAIC = [
    r'\bwalked \w+ly\b',           # "walked carefully"
    r'\b(despite|because|even though)\b',  # Explanatory connectors
    r'\bthe air seemed to\b',      # Vague atmospheric filler
]

# Simile detection (if anti_patterns includes "similes")
SIMILE_PATTERNS = [
    r'\b(like (a|an|the)|as if|resembled|seemed like)\b'
]
```

#### Metaphor Analysis

```python
def analyze_metaphor_distribution(scene_text, voice_calibration):
    domains = voice_calibration.metaphor_domains
    domain_counts = count_metaphors_by_domain(scene_text, domains)

    # Score criteria
    total = sum(domain_counts.values())
    scores = {
        "rotation": 10 if no_domain_exceeds(domain_counts, 0.30, total) else
                   7 if no_domain_exceeds(domain_counts, 0.40, total) else 4,
        "primary_limit": 5 if primary_under(domain_counts, domains[0], 0.40) else 3,
        "variety": 5 if len([d for d in domains if domain_counts[d] > 0]) >= 3 else 3
    }
    return sum(scores.values())  # Max 20 points
```

---

### C.5 Scene Enhancement

**Original (Explants)**: Two modes - Action Prompt (surgical fixes) and Full 6-pass enhancement.

**Vanilla Version**: Same two modes, driven by Voice Calibration.

#### Mode 1: Action Prompt (Surgical Fixes)

Generated from Analyzer score report. Format:

```markdown
# ENHANCEMENT ACTION PROMPT
Scene: [scene_id]
Current Score: [score]/100
Target Score: [target]/100

## CRITICAL FIXES (Apply in Order)

### Fix 1: [Category] - Line [N]
- Current: "[exact text to find]"
- Replace: "[corrected text]"
- Reason: [Anti-pattern violation / Voice drift / etc.]

### Fix 2: [Category] - Line [N]
[etc.]

## VERIFICATION
After applying fixes:
1. Re-run scorer to confirm improvement
2. Expected post-fix score: [estimated]
```

#### Mode 2: Full Enhancement (6-Pass)

*Based on the proven explants-scene-enhancement skill workflow (see AGENT_HANDOFF_WISDOM.md).*

```
Pass 1: SENSORY ANCHORING
- Find abstract mood descriptions ("the atmosphere was tense")
- Replace with concrete sensory details: air, light, texture, sound, smell
- Target 3 sensory anchors per major section
- Do NOT change dialogue or major plot points

Pass 2: VERB PROMOTION + SIMILE ELIMINATION
- Make environment ACT: "lobby air wheezed," "architecture confessed"
- Convert ALL similes ("like X", "as if") to direct metaphors
- Use literal-metaphorical reality: things BECOME, not resemble
- Promote nouns to verbs where possible
- Examples: "like a weapon" → "weaponized itself"

Pass 3: METAPHOR ROTATION
- No single domain should exceed 30% of metaphors
- Gambling metaphors: max 2-3 per scene
- Rotate between available domains from Voice Bundle
- Replace some metaphors from saturated domains with alternatives

Pass 4: VOICE EMBED (Not Hover)
- Delete sentences that "explain" what the previous sentence showed
- Insights should be EMBEDDED in action, not floating above it
- No academic meta-commentary ("Enhanced perspective analyzing...")
- Test each insight: Is it IN the action or ABOUT the action?
- BAD: "He noticed the pattern. This suggested danger."
- GOOD: "The pattern screamed danger."

Pass 5: ITALICS GATE
- Count current italics usage
- If 0-1: No change needed
- If >1: Reduce to maximum of 1
- Keep italics ONLY for: character arc moments, earned wisdom, critical turning points
- Insight should work without italics emphasis

Pass 6: VOICE AUTHENTICATION
- Observer Test: Character thinking vs AI explaining?
- Purpose Test: Every beat serves the theme?
- Fusion Test: Analytical precision fused with character voice?
- Make minimal changes - only fix what fails the tests
```

---

### C.6 Character Identity Framework

**Original (Explants)**: Mickey Bardot psychological profile, decision framework, specific voice tells.

**Vanilla Version**: Template for any character generated by Architect Mode.

#### Character Bible Entry (Generated in Architect Mode)

```markdown
# Character: [Name]

## Psychology Profile
- **Fatal Flaw**: [from protagonist template]
- **The Lie**: [false belief they hold]
- **Ghost**: [past event creating the lie]
- **Core Fear**: [what they're avoiding]
- **Core Desire**: [what they truly want]

## Decision Framework
When faced with [situation type], [character] will:
- Default to: [habitual response based on flaw]
- Under pressure: [escalated response]
- Growth moment: [how they break pattern]

## Voice Tells (for dialogue/POV)
- **Vocabulary**: [words they use, don't use]
- **Sentence patterns**: [how they construct thoughts]
- **Metaphor domains**: [their frame of reference]
- **Verbal tics**: [characteristic phrases]

## Capability Limits
- **Can do**: [established skills]
- **Cannot do**: [limitations]
- **Learning arc**: [skills to acquire through story]

## Relationship Dynamics
- With [Character B]: [dynamic - trust level, conflict source]
- With [Character C]: [dynamic]
[etc.]
```

---

### C.7 Integration: Story Bible → Skills Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    STORY BIBLE TO SKILLS FLOW                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STORY BIBLE (Architect Mode Output)                                    │
│  ───────────────────────────────────                                    │
│  • Protagonist Template → Character Identity Framework                  │
│  • Beat Sheet → Scaffold Generator scene breakdown                      │
│  • Theme → Purpose Test criteria                                        │
│  • World Rules → Continuity checks                                      │
│  • Cast → Relationship dynamics validation                              │
│                                                                          │
│  VOICE CALIBRATION (Phase 2B Output)                                    │
│  ──────────────────────────────────                                     │
│  • Voice Calibration Document → Scene Writer core rules                 │
│  • Anti-patterns list → Analyzer detection patterns                     │
│  • Metaphor domains → Domain rotation scoring                           │
│  • Phase evolution → Phase appropriateness scoring                      │
│  • Reference samples → Authenticity comparison                          │
│                                                                          │
│  SKILL INVOCATION CHAIN                                                  │
│  ──────────────────────                                                  │
│  1. Scaffold Generator                                                   │
│     Input: Beat Sheet + Knowledge Graph context                         │
│     Output: Chapter scaffold with scene breakdown                       │
│                                                                          │
│  2. Scene Writer (via Multiplier)                                       │
│     Input: Scene scaffold + Voice Calibration                           │
│     Output: 5 scene variants per scene                                  │
│                                                                          │
│  3. Scene Analyzer/Scorer                                               │
│     Input: Variants + Voice Calibration + Story Bible                   │
│     Output: Scores + recommended best + hybrid options                  │
│                                                                          │
│  4. Scene Enhancement                                                    │
│     Input: Selected variant + Score report                              │
│     Output: Polished scene meeting quality threshold                    │
│                                                                          │
│  5. [Repeat 2-4 for each scene in chapter]                             │
│                                                                          │
│  6. Chapter Assembly                                                    │
│     Input: All enhanced scenes                                          │
│     Output: Complete chapter + Knowledge Graph updates                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### C.8 Minimum Viable Story Bible for Director Mode

To enter Director Mode, the following must exist in Knowledge Graph:

```
REQUIRED:
✓ protagonist_fatal_flaw: string
✓ protagonist_lie: string
✓ protagonist_arc: string (transformation description)
✓ theme_statement: string
✓ beat_sheet: list[Beat] (at least 15 beats with positions)
✓ world_rules: list[string] (at least 3 fundamental constraints)
✓ voice_calibration: VoiceCalibrationDocument

RECOMMENDED:
○ cast: list[Character] (supporting characters)
○ protagonist_ghost: string
○ antagonist_goal: string
○ subplots: list[Subplot]
```

If any REQUIRED field is missing, Foreman remains in Architect Mode until complete.

---

## Appendix D: Universal AI Anti-Patterns (All Projects)

Unlike project-specific anti-patterns (which come from Voice Calibration), these are **universal AI tells** that most writers will want to avoid. The Scene Analyzer should flag these regardless of project settings.

This is a "stylistic fingerprint scanner" - patterns that reveal AI-generated text through statistical predictability rather than authentic voice.

---

### D.1 Content and Tone Indicators

LLMs regress to the mean, substituting generic positive claims for specific, nuanced detail.

| Pattern | Flag Words/Phrases | Problem |
|---------|-------------------|---------|
| **Exaggerated Importance** | *stands/serves as*, *is a testament/reminder*, *plays a vital/significant/crucial/pivotal role*, *indelible mark*, *profound heritage* | Generic positive claims instead of specific detail |
| **Promotional Puffery** | *continues to captivate*, *groundbreaking*, *stunning natural beauty*, *enduring/lasting legacy*, *boasts a*, *nestled*, *in the heart of* | Sounds like ad copy, not prose |
| **Shallow -ing Analysis** | *ensuring...*, *highlighting...*, *emphasizing...*, *reflecting...*, *underscoring...*, *showcasing...*, *aligns with...*, *contributing to...* | Disembodied narrator telling meaning instead of showing impact |
| **Didactic Disclaimers** | *it's important/critical/crucial to note/remember/consider* | Breaks fourth wall with unnecessary instruction |
| **Formulaic Conclusions** | *In summary*, *In conclusion*, *Overall* | Unnecessary recap that kills momentum |
| **Challenge/Prospect Pattern** | *Despite its... faces several challenges...* | Rigid outline structure bleeding through |

---

### D.2 Language and Grammar Indicators

Statistical modeling produces predictable vocabulary and structures.

| Pattern | Flag Words/Phrases | Problem |
|---------|-------------------|---------|
| **AI Vocabulary Overuse** | **crucial**, **pivotal**, **tapestry** (abstract), **intricate/intricacies**, **enduring**, **fostering**, **showcase/showcasing**, **underscore/underscoring** | Disproportionately favored by LLMs |
| **Elegant Variation** | Rapid synonym cycling (e.g., "protagonist" → "key player" → "eponymous character" in close proximity) | Repetition-penalty code creating unnatural variation |
| **False Ranges** | *"from ... to ..."* with unrelated endpoints | Meaningless but sounds impressive |
| **Rule of Three Overuse** | Consistent "adjective, adjective, adjective" or "phrase, phrase, and phrase" | Makes superficial points seem comprehensive |
| **Negative Parallelisms** | *"Not only ... but ..."*, *"It is not just about ..., it's ..."* | Stilted, overly formal in creative work |
| **Vague Attribution** | *Observers have cited*, *Some critics argue* | Unnamed authorities (unless deliberate in dialogue) |

---

### D.3 Style and Punctuation Indicators

Visual and rhythmic patterns that reveal AI generation.

| Pattern | Description | Problem |
|---------|-------------|---------|
| **Em Dash Overuse** | Em dashes (—) used much more frequently than commas, parentheses, or colons | "Punched up" sales rhythm |
| **Curly Quotes** | "..." and ' instead of straight quotes | Common in raw AI output |
| **Excessive Boldface** | Phrases bolded mechanically for emphasis | "Key takeaways" style, not prose style |
| **Title Case Headings** | All Main Words Capitalized | Strong AI chatbot preference |

---

### D.4 Integration with Scene Analyzer

The Scene Analyzer should run **two anti-pattern passes**:

**Pass 1: Project-Specific (from Voice Calibration)**
```python
# Configured per project
project_anti_patterns = voice_calibration.anti_patterns
# e.g., ["similes", "computer_metaphors", "first_person_italics"]
```

**Pass 2: Universal AI Anti-Patterns (always active)**
```python
UNIVERSAL_AI_PATTERNS = {
    # Content
    "exaggerated_importance": [
        r'\b(stands|serves) as\b',
        r'\bis a testament\b',
        r'\bplays a (vital|significant|crucial|pivotal) role\b',
        r'\bindelible mark\b',
        r'\bprofound heritage\b',
    ],
    "promotional_puffery": [
        r'\bcontinues to captivate\b',
        r'\bgroundbreaking\b',
        r'\bstunning natural beauty\b',
        r'\b(enduring|lasting) legacy\b',
        r'\bboasts a\b',
        r'\bnestled\b',
        r'\bin the heart of\b',
    ],
    "shallow_ing_analysis": [
        r',\s*(ensuring|highlighting|emphasizing|reflecting|underscoring|showcasing|contributing to)\b',
    ],
    "didactic_disclaimers": [
        r"\bit'?s (important|critical|crucial) to (note|remember|consider)\b",
    ],
    "formulaic_conclusions": [
        r'\b(In summary|In conclusion|Overall),',
    ],

    # Language
    "ai_vocabulary": [
        r'\bcrucial\b',
        r'\bpivotal\b',
        r'\btapestry\b',  # as abstract noun
        r'\b(intricate|intricacies)\b',
        r'\benduring\b',
        r'\bfostering\b',
        r'\b(showcase|showcasing)\b',
        r'\b(underscore|underscoring)\b',
    ],
    "false_ranges": [
        r'\bfrom .{5,50} to .{5,50}\b',  # Needs semantic check
    ],
    "negative_parallelisms": [
        r'\bNot only\b.{5,50}\bbut\b',
        r"\bIt is not just about\b.{5,50}\bit'?s\b",
    ],
}
```

**Scoring Impact:**
- Universal AI patterns: **-0.5 points each** (warning, not zero-tolerance)
- More than 5 in a scene: **-3 points total** (capped)
- Flagged for human review in score report

**Report Format:**
```markdown
## AI Pattern Flags (Universal)
⚠️ Line 23: "plays a crucial role" [ai_vocabulary + exaggerated_importance]
⚠️ Line 47: "from the darkest despair to the brightest hope" [false_ranges]
⚠️ Line 89: "underscoring the importance" [shallow_ing_analysis]

AI Pattern Count: 3 (acceptable, minor deduction)
Recommendation: Review flagged lines for authentic alternatives
```

---

### D.5 Writer Override

Some writers may intentionally use patterns flagged here. The Voice Calibration Document can include:

```yaml
ai_pattern_overrides:
  allow:
    - "rule_of_three"  # Writer likes triads
    - "em_dash_heavy"  # Stylistic choice
  severity:
    ai_vocabulary: "ignore"  # Writer doesn't care about this
    promotional_puffery: "error"  # Absolutely not in this project
```

---

## Part E: Graph Health Service (Phase 3D) 🚧

**Status**: In Implementation
**Context**: Macro-level structural validation to complement scene-level quality checks

### E.1 The Two-Tier Quality System

Director Mode uses a **two-tier analysis pyramid**:

```
┌─────────────────────────────────────────────────────────┐
│          TIER 2: Macro-Level Health                     │
│          (Graph Health Service - Phase 3D)              │
│          • Pacing across chapters                       │
│          • Beat structure compliance                    │
│          • Character arc tracking                       │
│          • Timeline consistency                         │
│          • Theme resonance at critical beats            │
├─────────────────────────────────────────────────────────┤
│          TIER 1: Scene-Level Quality                    │
│          (Scene Analyzer - Phase 3B)                    │
│          • Voice authenticity                           │
│          • Anti-pattern compliance                      │
│          • Metaphor discipline                          │
└─────────────────────────────────────────────────────────┘
```

**Analogy**: If Scene Analyzer is the **line editor**, Graph Health Service is the **structural engineer**.

---

### E.2 Strategic Architecture Decisions

#### Decision 1: Full LLM Semantic Analysis for Timeline Consistency

**Problem**: Timeline conflicts are nuanced and require semantic understanding:
- "Character arrives at sunset" vs. "It's still noon"
- "The missing documents mentioned in Ch. 2" never resolved

**Solution**: Full Ollama LLM-powered semantic analysis (not simplified regex)

**Settings**:
```yaml
health_checks:
  timeline:
    enabled: true
    semantic_analysis: true  # Use LLM
    check_character_locations: true
    check_world_rules: true
    check_dropped_threads: true
    confidence_threshold: 0.7
```

---

#### Decision 2: Hybrid LLM + Manual Override for Theme Resonance

**Problem**: Thematic success is subjective - LLM may miss subtle writer intent

**Solution**: Automated LLM scoring with manual override capability

**Workflow**:
1. LLM auto-scores theme resonance at critical beats (0-10)
2. Writer reviews scores in health report
3. Writer can override via API: `POST /health/theme/override`
4. Future health checks respect manual overrides

**Settings**:
```yaml
health_checks:
  theme:
    auto_score: true  # Enable LLM scoring
    allow_manual_override: true
    min_resonance_score: 6
```

---

#### Decision 3: Auto-Trigger After Every Chapter

**Problem**: Balance between proactive detection and workflow interruption

**Solution**: Automatically run health checks after each chapter assembly, respecting Foreman proactiveness

**Behavior by Proactiveness Level**:
- **High**: Show all warnings, block on critical errors
- **Medium** (default): Show warnings, allow continue with acknowledgment
- **Low**: Silent mode, store reports but don't interrupt

**Settings**:
```yaml
health_checks:
  reporting:
    auto_trigger: true
    notification_mode: "foreman_proactive"  # Respects foreman.proactiveness
```

---

#### Decision 4: SQLite Persistence for Longitudinal Analysis

**Problem**: On-demand generation is simpler, but historical data enables trend analysis

**Solution**: Store all health reports in SQLite with 365-day retention

**Benefits**:
- Trend analysis: "Is chapter pacing improving over time?"
- A/B testing: "Did tighter flaw challenge frequency improve character arc?"
- Writer learning: Historical health metrics

**API**:
```python
GET /health/trends/pacing_plateaus?start_date=2025-01-01&end_date=2025-11-24
# Returns: [
#   {"chapter_id": "1.2", "plateaus_detected": 1, "timestamp": "2025-05-10"},
#   {"chapter_id": "2.3", "plateaus_detected": 0, "timestamp": "2025-08-15"}
# ]
```

**Settings**:
```yaml
health_checks:
  reporting:
    store_history: true
    retention_days: 365
```

---

### E.3 Health Check Categories

#### A. Structural Integrity

1. **Pacing Plateau Detection**
   - Detects 3+ consecutive chapters with flat tension (within 1 point)
   - Warns before reader boredom sets in

2. **Beat Progress Validation**
   - Ensures 15-beat structure compliance
   - Warns if beats deviate >5% from target manuscript position
   - Errors if deviation >10%

3. **Timeline Consistency** (Full LLM Semantic Analysis)
   - Character location tracking
   - World rules compliance
   - Dropped thread detection
   - Semantic contradiction analysis

#### B. Character Arc Health

1. **Fatal Flaw Challenge Monitoring**
   - Tracks scenes since protagonist's Fatal Flaw was tested
   - Warns if gap exceeds threshold (default: 10 scenes)

2. **Cast Function Verification**
   - Ensures supporting characters serve their narrative function
   - Warns if characters appear too rarely (<3 times)

#### C. Thematic Health

1. **Symbolic Layering**
   - Tracks symbol recurrence (min: 3 occurrences)
   - Detects static vs. evolving symbol meanings

2. **Theme Resonance** (Hybrid LLM + Manual Override)
   - LLM auto-scores theme presence at critical beats
   - Writers can override scores via `/health/theme/override`
   - Warns if theme absent from critical structural beats

---

### E.4 API Endpoints (Phase 3D)

```python
# Core health checks
POST /health/check
  Body: {"scope": "chapter", "chapter_id": "2.5"}
        {"scope": "act", "act_number": 2}
        {"scope": "manuscript"}

GET /health/report/{report_id}

POST /health/export
  Body: {"report_id": "health_report_123", "format": "markdown"}

# Longitudinal analysis
GET /health/trends/{metric}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
  Metrics: pacing_plateaus, beat_deviations, flaw_challenges, theme_resonance, overall_health

# Theme manual override
POST /health/theme/override
  Body: {"beat_id": "beat_7", "theme_id": "theme_identity", "manual_score": 9, "reason": "..."}

GET /health/theme/overrides?project_id={id}
```

---

### E.5 Integration with Scene Analyzer

**Scene Analyzer (Tier 1)** runs on every scene generation:
- Immediate feedback (< 5 seconds)
- Voice authenticity, anti-patterns, metaphor discipline
- Score determines enhancement mode

**Graph Health Service (Tier 2)** runs after chapter assembly:
- Asynchronous background job (30-60 seconds)
- Macro-level structure, pacing, character arcs, theme
- Foreman integrates warnings into guidance

**Complementary, Not Redundant**: Scene Analyzer validates **prose quality**, Graph Health validates **narrative structure**.

---

### E.6 Foreman Integration

After chapter assembly:

```python
async def on_chapter_complete(self, chapter_id: str):
    # 1. Assemble chapter
    # 2. Trigger Graph Health check (background)
    health_report = await graph_health_service.run_chapter_health_check(chapter_id)

    # 3. Store report
    self.kb_service.set(f"chapter_{chapter_id}_health", health_report.to_json())

    # 4. Present warnings to writer
    if health_report.has_critical_warnings():
        return self._create_challenge_message(health_report)
    elif health_report.has_warnings():
        return self._create_guidance_message(health_report)
    else:
        return "Chapter health: CLEAN. Excellent structural integrity."
```

---

### E.7 Health Report Format

```json
{
  "report_id": "health_report_123",
  "scope": "chapter",
  "chapter_id": "chapter_2.5",
  "overall_score": 87,
  "timestamp": "2025-11-24T15:30:00Z",
  "warnings": [
    {
      "type": "PACING_PLATEAU",
      "severity": "warning",
      "message": "Flat pacing detected: Chapters 2.3 through 2.5 have similar tension (6, 6, 6)",
      "recommendation": "Next scene should escalate tension significantly",
      "chapters": ["chapter_2.3", "chapter_2.4", "chapter_2.5"]
    },
    {
      "type": "WEAK_THEME",
      "severity": "warning",
      "beat": "Midpoint",
      "theme": "theme_identity",
      "resonance": 5,
      "message": "Theme resonance at 'Midpoint' is weak (5/10)",
      "recommendation": "Strengthen thematic callback in Midpoint scene"
    }
  ]
}
```

**Markdown Export**:
```markdown
# Health Report: Chapter 2.5
**Overall Score**: 87/100 (Good)
**Timestamp**: 2025-11-24 15:30 UTC

## Warnings

### ⚠️ Pacing Plateau Detected
**Severity**: Warning
**Chapters**: 2.3, 2.4, 2.5
**Issue**: Flat pacing - tension scores are 6, 6, 6 (too similar)
**Recommendation**: Next scene should escalate tension significantly

### ⚠️ Weak Theme Resonance
**Severity**: Warning
**Beat**: Midpoint
**Theme**: Identity Integration
**Score**: 5/10 (below threshold of 6)
**Recommendation**: Strengthen thematic callback in Midpoint scene
```

---

### E.8 Settings Summary

All Phase 3D settings live in `voice_settings.yaml` or Settings Service:

```yaml
health_checks:
  enabled: true

  pacing:
    plateau_window: 3
    plateau_tolerance: 1.0
    enabled: true

  structure:
    beat_deviation_warning: 5  # % off target
    beat_deviation_error: 10
    enabled: true

  character:
    flaw_challenge_frequency: 10  # Max scenes without test
    min_cast_appearances: 3
    enabled: true

  theme:
    min_symbol_occurrences: 3
    min_resonance_score: 6
    auto_score: true  # LLM scoring
    allow_manual_override: true
    enabled: true

  timeline:
    enabled: true
    semantic_analysis: true  # Full LLM analysis
    check_character_locations: true
    check_world_rules: true
    check_dropped_threads: true
    confidence_threshold: 0.7

  reporting:
    store_history: true
    retention_days: 365
    auto_trigger: true
    notification_mode: "foreman_proactive"
```

---

*End of Part E (Phase 3D Specification)*

---

*End of Specification*
