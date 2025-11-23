# Director Mode Specification

> Phase 3B: Scene-by-scene drafting with voice consistency

---

## Overview

**Director Mode** is the second operational mode of The Foreman, activated after the Story Bible is complete and Voice Calibration has produced a Voice Reference Bundle. The Director guides writers through scene-by-scene drafting, ensuring voice consistency and narrative coherence.

### Prerequisites (from Phase 2B)
- ✅ Complete Story Bible (Protagonist, Beat Sheet, Theme, World Rules)
- ✅ Voice Calibration Document (Gold Standard examples, Anti-Patterns, Phase Evolution)
- ✅ Knowledge Base populated with decisions, constraints, character facts

---

## Four Core Services

Director Mode comprises four services that work together:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DIRECTOR MODE PIPELINE                        │
│                                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌────────┐│
│  │  SCAFFOLD   │    │   SCENE     │    │   SCENE     │    │ SCENE  ││
│  │  GENERATOR  │───▶│   WRITER    │───▶│   ANALYZER  │───▶│ENHANCE ││
│  │             │    │             │    │             │    │        ││
│  │ Creates     │    │ Drafts      │    │ Scores      │    │ Polish ││
│  │ strategic   │    │ scenes with │    │ against     │    │ based  ││
│  │ context     │    │ Voice       │    │ 5-category  │    │ on     ││
│  │ document    │    │ Bundle      │    │ rubric      │    │ score  ││
│  └─────────────┘    └─────────────┘    └─────────────┘    └────────┘│
│         │                  │                  │                │    │
│         │                  │                  │                │    │
│         └──────────────────┴──────────────────┴────────────────┘    │
│                              │                                      │
│                              ▼                                      │
│                    ┌─────────────────────┐                         │
│                    │   KNOWLEDGE BASE    │                         │
│                    │                     │                         │
│                    │ • Voice Bundle      │                         │
│                    │ • Scene continuity  │                         │
│                    │ • Character arcs    │                         │
│                    │ • Established facts │                         │
│                    └─────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Service 1: Scaffold Generator

### Purpose
Creates a **strategic briefing document** for each chapter/scene—not just a markdown template, but contextual guidance that ensures scenes serve the larger narrative.

### Gold Standard Scaffold Structure

```markdown
## CHAPTER [X]: [TITLE]

**For Writers Factory Scene Writer**

---

#### Chapter Overview
**Title:** Chapter X: [Title]
**Target Length:** [word count] words (Estimate [N] scenes)
**Phase:** [Act/Phase from Beat Sheet]
**Voice:** [POV character] - [voice state from Voice Bundle]
**Core Function:** [What this chapter must accomplish narratively]

---

#### Strategic Context
- **Conflict Positioning:** [How this chapter fits the larger conflict]
- **Character Goals:** [What [protagonist] wants in this chapter]
- **Thematic Setup:** [How theme manifests in this chapter]
- **Protagonist Constraint:** [What limits/challenges the protagonist faces]

---

#### Success Criteria
##### Quality Thresholds
- Overall quality score > 8.5
- Voice authenticity > 8.0 (sounds like character, not AI explaining character)
- Philosophical integration seamless with action
- Technical concepts accessible through character voice

##### Voice Requirements
- Narrator must adhere to **Voice Gold Standard** from Voice Bundle
- **Mandatory Focus:** [Character-specific voice tells from Voice Calibration]
- **Phase Calibration:** Maintain [phase] voice complexity level

---

#### Continuity Checklist
- [Previous chapter callback 1]
- [Previous chapter callback 2]
- [Foreshadowing element to plant]

---

#### Ready for Scene Writer
This scaffold provides sufficient context for scene generation using the
Voice Bundle without requiring access to the full project knowledge base.

**Expected Output:** [word count] words maintaining voice consistency
```

### Data Sources for Scaffold Assembly

| Section | Source |
|---------|--------|
| Chapter Overview | Beat Sheet + Voice Calibration Document |
| Strategic Context | Knowledge Base (decisions, constraints) + Story Bible |
| Success Criteria | Voice Bundle (Gold Standard, Anti-Patterns) |
| Continuity Checklist | Knowledge Base (previous scene events) |

### API: `POST /director/scaffold/generate`

```json
{
  "chapter_number": 4,
  "chapter_title": "The Approach",
  "beat_numbers": [4, 5],
  "pov_character": "protagonist",
  "target_word_count": "5000-6000"
}
```

---

## Service 2: Scene Writer

### Purpose
Generates scene drafts using multi-model competition with Voice Bundle injection.

### Voice Bundle Integration

Every scene generation call includes:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SCENE WRITER CONTEXT                              │
├─────────────────────────────────────────────────────────────────────┤
│ [SCAFFOLD]                                                           │
│   Strategic context from Scaffold Generator                          │
│                                                                      │
│ [VOICE BUNDLE]                                                       │
│   ├── voice_gold_standard.md   (winning examples from calibration)  │
│   ├── voice_anti_patterns.md   (what to avoid)                      │
│   └── voice_phase_evolution.md (how voice changes across phases)    │
│                                                                      │
│ [CONTINUITY CONTEXT]                                                 │
│   Recent scene summaries, established facts from KB                  │
│                                                                      │
│ [PROMPT]                                                             │
│   "Write Scene X.Y according to scaffold, maintaining voice per      │
│   Gold Standard and avoiding Anti-Patterns"                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Multi-Model Competition

Leverages existing tournament infrastructure from Voice Calibration:

1. **3-5 models** generate scene drafts (based on available API keys)
2. Each draft receives Scene Analyzer score
3. **Winning draft** proceeds to Enhancement (if needed)
4. **All drafts** saved for comparison

### API: `POST /director/scene/write`

```json
{
  "scaffold_id": "ch4-scaffold",
  "scene_number": "4.1",
  "scene_prompt": "Write the opening scene where the antagonist arrives",
  "tournament_mode": true,
  "models": ["claude", "gpt4", "gemini"]
}
```

---

## Service 3: Scene Analyzer

### Purpose
Evaluates scene drafts against a **5-category, 100-point rubric** derived from the writer's Voice Calibration output.

### The Vanilla Scoring Framework

The original Explants skills used Mickey Bardot-specific tests. The vanilla version maps these to generic concepts that reference the writer's Story Bible and Voice Bundle:

| Original (Mickey-specific) | Vanilla (Any Novel) | Weight |
|---------------------------|---------------------|--------|
| Observer Test | **Authenticity Test** | 10 pts |
| Consciousness War Test | **Purpose Test** | 10 pts |
| Cognitive Fusion Test | **Fusion Test** | 10 pts |
| Character Consistency | Character Consistency | 20 pts |
| Metaphor Discipline | Metaphor Discipline | 20 pts |
| Anti-Pattern Compliance | Anti-Pattern Compliance | 15 pts |
| Phase Appropriateness | Phase Appropriateness | 15 pts |

### Category 1: Voice Authenticity (30 points)

#### Authenticity Test (10 points)
**Question:** Does this sound like [POV character] observing, or AI explaining [POV character]?

Scoring rubric sourced from **Voice Gold Standard**:
- **10 pts:** Perfect match to Gold Standard voice - character observing in real-time
- **7 pts:** Mostly authentic with occasional AI-explaining moments
- **4 pts:** Mix of authentic and academic commentary
- **0 pts:** Sounds like AI studying the character

#### Purpose Test (10 points)
**Question:** Does every scene beat serve the [Theme] argument?

Sourced from **Story Bible - Theme** and **Beat Sheet**:
- **10 pts:** Theme embedded in action, never stated explicitly
- **7 pts:** Theme present but occasionally stated rather than shown
- **4 pts:** Generic prose with theme tangential
- **0 pts:** Well-written but doesn't serve the theme

#### Fusion Test (10 points)
**Question:** Are the character's specialized knowledge domains fused with their personality?

Sourced from **Character Profile** (expertise + psychology):
- **10 pts:** Technical/specialized language seamlessly integrated with character voice
- **7 pts:** Occasional separation between expertise and personality
- **4 pts:** Either technical OR character voice, not fused
- **0 pts:** Academic analysis without character grounding

### Category 2: Character Consistency (20 points)

#### Psychology Consistency (8 points)
Does behavior match established **Fatal Flaw** and **The Lie**?

Sourced from **Story Bible - Protagonist**:
- **8 pts:** Perfect alignment with Fatal Flaw/Lie
- **6 pts:** Mostly consistent, 1-2 minor deviations
- **3 pts:** Several inconsistencies
- **0 pts:** Contradicts established psychology

#### Capability Validation (6 points)
Are all actions within established character limits?

Sourced from **Story Bible - Character Profile**:
- **6 pts:** All actions justified by established abilities
- **4 pts:** One plausible but unestablished capability
- **2 pts:** Unexplained capability used
- **0 pts:** Breaks established limits

#### Relationship Dynamics (6 points)
Do interactions match established relationship patterns?

Sourced from **Story Bible - Characters** and **KB relationship entries**:
- **6 pts:** Authentic to established dynamics
- **4 pts:** Generally authentic, some generic beats
- **2 pts:** Misaligned with established patterns
- **0 pts:** Contradicts relationship fundamentals

### Category 3: Metaphor Discipline (20 points)

#### Domain Rotation (10 points)
Are metaphor domains diverse and rotated?

Sourced from **Voice Calibration - Metaphor Domains**:
- **10 pts:** No domain >30%, diverse across character's experience
- **7 pts:** Mostly balanced, one domain slightly overused
- **4 pts:** Heavy reliance on 1-2 domains
- **0 pts:** Single domain saturation (>40%)

#### Simile Elimination (5 points)
Are similes avoided in favor of direct metaphors?

- **5 pts:** Zero similes, all direct transformation
- **3 pts:** 1-2 similes, mostly direct metaphors
- **1 pt:** Multiple comparison structures
- **0 pts:** Simile-heavy ("like", "as if" frequent)

#### Direct Transformation (5 points)
Do objects/concepts BECOME metaphors through active verbs?

- **5 pts:** Strong verb promotion (nouns become verbs)
- **3 pts:** Mixed transformation approaches
- **1 pt:** Mostly comparison-based
- **0 pts:** No active transformation

### Category 4: Anti-Pattern Compliance (15 points)

#### Zero-Tolerance Violations (10 points)
Start at 10, deduct -2 per violation.

Sourced from **Voice Anti-Patterns** document:
- First-person italics with wrong POV
- "With [adjective] precision" constructions
- Computer psychology ("brain processed")
- "With [obvious] [noun]" constructions

#### Formulaic Patterns (5 points)
Start at 5, deduct -1 per violation.

- Adverb-verb combinations ("walked carefully")
- "Despite the [noun]" transitions
- Vague atmosphere ("the air seemed tense")
- Excessive pattern repetition

### Category 5: Phase Appropriateness (15 points)

#### Voice Complexity Match (8 points)
Is voice complexity appropriate for story phase?

Sourced from **Voice Phase Evolution** document:
- **8 pts:** Perfect alignment with phase expectations
- **6 pts:** Generally correct with minor anachronisms
- **3 pts:** Wrong complexity level for phase
- **0 pts:** Completely inappropriate voice

#### Earned Language (7 points)
Is specialized terminology justified by character's experience at this point?

- **7 pts:** All terms earned through character experience
- **5 pts:** 1-2 slightly premature terms
- **2 pts:** Premature specialized language
- **0 pts:** Inappropriate academic jargon

### Automated Pattern Detection

The analyzer uses regex patterns to detect violations:

```python
# Zero-Tolerance Violations
PATTERNS = {
    "first_person_italics": r"\*[^*]*\b(we|I)\b[^*]*\*",
    "with_precision": r"\bwith \w+ precision\b",
    "with_adjective_noun": r"\bwith (the |a |an )?([\w]+) ([\w]+)\b",
    "computer_psychology": r"\b(brain|mind|consciousness) (processed|computed|analyzed)\b"
}

# Metaphor Domain Detection (populated from Voice Bundle)
DOMAIN_PATTERNS = {
    # These come from the writer's Voice Calibration output
    "domain_1": [keywords from Voice Bundle],
    "domain_2": [keywords from Voice Bundle],
    # ...
}
```

### API: `POST /director/scene/analyze`

```json
{
  "scene_id": "scene-4-1",
  "scene_content": "[full scene text]",
  "pov_character": "protagonist",
  "phase": "act2"
}
```

Response:
```json
{
  "total_score": 85,
  "grade": "B+",
  "categories": {
    "voice_authenticity": { "score": 26, "max": 30, "details": {...} },
    "character_consistency": { "score": 18, "max": 20, "details": {...} },
    "metaphor_discipline": { "score": 16, "max": 20, "details": {...} },
    "anti_pattern_compliance": { "score": 12, "max": 15, "details": {...} },
    "phase_appropriateness": { "score": 13, "max": 15, "details": {...} }
  },
  "violations": [
    { "type": "zero_tolerance", "pattern": "with practiced precision", "line": 42 }
  ],
  "enhancement_needed": true,
  "recommended_mode": "action_prompt"
}
```

---

## Service 4: Scene Enhancement

### Purpose
Polishes scenes based on analyzer feedback. Two modes based on score threshold.

### Mode Selection

| Score Range | Mode | Description |
|-------------|------|-------------|
| 85+ | **Action Prompt** | Surgical fixes for specific violations |
| 70-84 | **6-Pass Enhancement** | Full polish pipeline |
| <70 | **Rewrite** | Return to Scene Writer |

### Action Prompt Mode (Score 85+)

For scenes that are close to target, generate a surgical fix prompt:

```
The scene scores 87/100 but has these specific issues:

1. Line 42: "with practiced precision" - Zero-tolerance violation
   FIX: Replace with direct metaphor showing precision

2. Lines 78-92: Gambling metaphors at 38% - approaching saturation
   FIX: Replace 2 gambling metaphors with [alternate domain from Voice Bundle]

3. Line 156: Character trusted authority without reading angles
   FIX: Add internal resistance per Fatal Flaw

Apply these fixes while preserving the scene's strong voice.
```

### 6-Pass Enhancement Mode (Score 70-84)

Full polish pipeline:

| Pass | Focus | From Voice Bundle |
|------|-------|-------------------|
| 1 | Voice Authentication | Gold Standard comparison |
| 2 | Character Consistency | Fatal Flaw/Lie alignment |
| 3 | Metaphor Rebalancing | Domain rotation targets |
| 4 | Anti-Pattern Sweep | Pattern elimination |
| 5 | Phase Calibration | Phase Evolution alignment |
| 6 | Final Polish | Integration check |

### API: `POST /director/scene/enhance`

```json
{
  "scene_id": "scene-4-1",
  "analysis_result": { /* from analyzer */ },
  "mode": "action_prompt"
}
```

---

## Knowledge Base Writes

Director Mode writes to KB after each scene:

```
KB Entry: Scene/4.1
─────────────────────
Status: completed
Final Score: 92/100
Events Established:
  - Antagonist arrived at [location]
  - Protagonist's reaction revealed [trait]
  - [Plot element] introduced

Character Arc Progress:
  - Protagonist: Still holding The Lie (Act 2 appropriate)
  - Antagonist: Philosophy revealed

Continuity Notes:
  - [Object] mentioned - must appear later
  - [Promise] made - must be fulfilled
```

---

## Integration with Foreman

Director Mode extends The Foreman's capabilities:

```python
class Foreman:
    modes = ["ARCHITECT", "VOICE_CALIBRATION", "DIRECTOR", "EDITOR"]

    def transition_to_director(self):
        """Validates prerequisites before entering Director Mode"""
        assert self.story_bible.is_complete()
        assert self.voice_bundle.exists()
        self.mode = "DIRECTOR"

    def director_conversation(self, user_message):
        """Director Mode conversation handler"""
        # Context includes:
        # - Current chapter scaffold
        # - Voice Bundle summary
        # - Recent KB entries
        # - Scene status (drafted, scored, enhanced)
        pass
```

### Director Conversation Example

```
FOREMAN: "You're ready to draft Scene 4.1 - this serves Beat 4 (Catalyst).

         From your Story Bible:
         • [Protagonist]'s Fatal Flaw: [flaw from Story Bible]
         • The Lie: [lie from Story Bible]
         • This beat needs: The inciting incident

         From previous scenes:
         • Scene 3.3 established [event]
         • Scene 3.4 showed [development]

         I've generated a scaffold for Chapter 4. Ready to start drafting?"

WRITER: "Yes, let's draft scene 4.1"

FOREMAN: [Invokes Scene Writer with Voice Bundle]

         "Draft complete. Score: 78/100 (B)

         Issues found:
         - Voice drifted to AI-explaining in lines 45-60
         - [Domain] metaphors at 42% (saturation)
         - One psychology inconsistency (line 89)

         Recommend 6-Pass Enhancement. Proceed?"
```

---

## File Locations

```
backend/
├── services/
│   ├── scaffold_generator_service.py
│   ├── scene_writer_service.py
│   ├── scene_analyzer_service.py
│   └── scene_enhancement_service.py
└── models/
    └── scoring.py  # Scoring rubric models

docs/
└── specs/
    ├── DIRECTOR_MODE.md (this file)
    └── SCORING_RUBRICS.md (detailed examples)
```

---

## Implementation Order

1. **SceneAnalyzerService** - Foundation (scoring framework everything depends on)
2. **ScaffoldGeneratorService** - Strategic context assembly
3. **SceneWriterService** - Multi-model drafting with Voice Bundle
4. **SceneEnhancementService** - Polish pipeline

---

*Director Mode Specification v1.0*
*Writers Factory - Phase 3B*
