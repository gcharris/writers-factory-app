# Scoring Rubrics Specification

**Version**: 2.0
**Status**: Updated for Director Mode
**Related**: DIRECTOR_MODE.md, Voice Calibration Service

---

## Overview

This spec defines the **5-category, 100-point scoring framework** used by Director Mode to evaluate scene quality. The framework is **vanilla** - it references the writer's Story Bible and Voice Bundle rather than hard-coded character-specific patterns.

### Key Principle: Voice Bundle as Source of Truth

Unlike hard-coded rubrics, this scoring system pulls its criteria dynamically from:
- **Voice Gold Standard** - What good voice looks like for THIS novel
- **Voice Anti-Patterns** - What to avoid for THIS novel
- **Voice Phase Evolution** - How voice changes across THIS novel's phases
- **Story Bible** - Character Fatal Flaws, Lies, relationships, world rules

---

## Scoring Categories

| Category | Weight | What It Measures |
|----------|--------|------------------|
| Voice Authenticity | 30 pts | Does it sound like the character? |
| Character Consistency | 20 pts | Does behavior match established psychology? |
| Metaphor Discipline | 20 pts | Are metaphors diverse and well-rotated? |
| Anti-Pattern Compliance | 15 pts | Are known bad patterns avoided? |
| Phase Appropriateness | 15 pts | Is voice complexity right for this phase? |

**Total: 100 points**

---

## Category 1: Voice Authenticity (30 points)

Voice Authenticity measures whether prose sounds like the POV character observing, or AI explaining the POV character. This is the most heavily weighted category because voice drift is the most common AI writing failure.

### 1A: Authenticity Test (10 points)

**Core Question:** Does this sound like [POV character] thinking/observing in real-time?

| Score | Criteria |
|-------|----------|
| 10 | Perfect match to Voice Gold Standard - character actively observing |
| 7 | Mostly authentic with occasional "AI explaining character" moments |
| 4 | Mix of authentic voice and academic commentary |
| 0 | Sounds like AI studying the character from outside |

**Examples (Generic):**

**10 points - Character observing:**
```
The bartender's hands moved too fast, cards appearing where they
shouldn't. Another dealer with gambler's hands. Bad combination.
```
*Why it works:* Character is actively reading the room, making judgments in their voice.

**4 points - AI explaining:**
```
The protagonist observed the bartender's rapid hand movements with
growing suspicion. His enhanced awareness allowed him to detect the
subtle card manipulations.
```
*Why it fails:* "The protagonist observed" + "enhanced awareness allowed" = AI describing character capabilities.

**0 points - Pure AI voice:**
```
Enhanced perception enabled comprehensive assessment of the
bartender's prestidigitation techniques. The sophisticated
analytical capabilities revealed underlying deception patterns.
```
*Why it fails:* Academic jargon, no personality, could be written about anyone.

### 1B: Purpose Test (10 points)

**Core Question:** Does every scene beat serve the [Theme]?

| Score | Criteria |
|-------|----------|
| 10 | Theme embedded in action, never stated explicitly |
| 7 | Theme present but occasionally stated rather than shown |
| 4 | Generic prose with theme tangential |
| 0 | Well-written but doesn't serve the theme |

**How to evaluate:** Reference Story Bible → Theme document.

**10 points - Theme embedded:**
```
She held the door for the stranger, even running late. The small
choice felt heavier than it should, weighted by everything she
was trying to prove—that kindness wasn't weakness.
```
*Theme (kindness vs. power) woven into action.*

**4 points - Theme tangential:**
```
She held the door for the stranger, then hurried to her meeting.
The conference room was already full when she arrived.
```
*Action happens but doesn't connect to theme.*

### 1C: Fusion Test (10 points)

**Core Question:** Are the character's expertise domains fused with their personality?

| Score | Criteria |
|-------|----------|
| 10 | Technical language seamlessly integrated with character voice |
| 7 | Occasional separation between expertise and personality |
| 4 | Either technical OR character voice, not fused |
| 0 | Academic analysis without character grounding |

**Example - Fused (10 points):**
```
The code was elegant—too elegant. Someone had spent serious time
making it look amateur. Same trick every high-end con ran: dress
down to avoid attention.
```
*Technical observation (code quality) fused with character's con artist psychology.*

**Example - Separated (4 points):**
```
The code exhibited sophisticated obfuscation techniques. Maria
recognized the pattern from her years of experience.
```
*Technical is technical, personality is separate statement.*

---

## Category 2: Character Consistency (20 points)

### 2A: Psychology Consistency (8 points)

**Core Question:** Does behavior match established Fatal Flaw and The Lie?

| Score | Criteria |
|-------|----------|
| 8 | Perfect alignment - every action reflects Fatal Flaw/Lie |
| 6 | Mostly consistent, 1-2 minor deviations |
| 3 | Several behaviors contradict established psychology |
| 0 | Fundamental violation of established personality |

**How to evaluate:** Reference Story Bible → Protagonist → Fatal Flaw, The Lie.

**Example - Fatal Flaw: "Inability to accept help" / Lie: "Everyone has an angle"**

**8 points - Aligned:**
```
"Let me help you with that," she offered.
His hands tightened on the box. "I've got it."
```
*Refuses help automatically, consistent with Flaw.*

**0 points - Contradicted:**
```
"Let me help you with that," she offered.
"Thanks, I appreciate it." He handed over the box gratefully.
```
*Accepts help without hesitation - violates Fatal Flaw.*

### 2B: Capability Validation (6 points)

**Core Question:** Are all actions within established character limits?

| Score | Criteria |
|-------|----------|
| 6 | All actions justified by established abilities |
| 4 | One plausible but unestablished capability stretch |
| 2 | Unexplained capability used |
| 0 | Breaks established limits |

**How to evaluate:** Reference Story Bible → Character Profile → Capabilities.

### 2C: Relationship Dynamics (6 points)

**Core Question:** Do interactions match established relationship patterns?

| Score | Criteria |
|-------|----------|
| 6 | Authentic to established dynamics |
| 4 | Generally authentic, some generic beats |
| 2 | Misaligned with established patterns |
| 0 | Contradicts relationship fundamentals |

**How to evaluate:** Reference Story Bible → Characters → Relationships and Knowledge Base → relationship entries.

---

## Category 3: Metaphor Discipline (20 points)

### 3A: Domain Rotation (10 points)

**Core Question:** Are metaphor domains diverse and properly rotated?

| Score | Criteria |
|-------|----------|
| 10 | No domain >30%, diverse across character's experience |
| 7 | Mostly balanced, one domain slightly overused (30-35%) |
| 4 | Heavy reliance on 1-2 domains (35-45%) |
| 0 | Single domain saturation (>45%) |

**How to evaluate:** Count metaphors by domain, reference Voice Bundle → Metaphor Domains.

**Example Domain Analysis:**
```
Total metaphors: 20
- Cooking: 4 (20%) - "simmered," "recipe for disaster," "half-baked," "slow burn"
- Music: 5 (25%) - "crescendo," "off-key," "rhythm," "harmony," "played it"
- Medicine: 4 (20%) - "diagnosis," "symptoms," "treatment," "infection"
- Architecture: 4 (20%) - "foundation," "scaffolding," "blueprint," "collapse"
- Sports: 3 (15%) - "overtime," "bench," "game plan"

SCORE: 10 - Good rotation, no domain over 25%
```

**Problem Example:**
```
Total metaphors: 15
- Cooking: 8 (53%) - SATURATION
- Music: 4 (27%)
- Other: 3 (20%)

SCORE: 0 - Cooking domain saturated
```

### 3B: Simile Elimination (5 points)

**Core Question:** Are similes avoided in favor of direct metaphors?

| Score | Criteria |
|-------|----------|
| 5 | Zero similes - all direct transformation |
| 3 | 1-2 similes, mostly direct metaphors |
| 1 | Multiple comparison structures |
| 0 | Simile-heavy ("like", "as if" frequent) |

**Direct metaphor (preferred):**
```
Sunlight weaponized itself against the concrete.
Fear assembled in her chest like casino chips.
The conversation found its tempo.
```

**Simile (avoid):**
```
The sunlight was like a weapon against the concrete.
She felt fear like stacked casino chips.
The conversation moved as if it had found a rhythm.
```

### 3C: Direct Transformation (5 points)

**Core Question:** Do objects/concepts BECOME metaphors through active verbs?

| Score | Criteria |
|-------|----------|
| 5 | Strong verb promotion - nouns become verbs |
| 3 | Mixed transformation approaches |
| 1 | Mostly comparison-based |
| 0 | No active transformation |

**Examples of verb promotion:**
```
✓ "Desperation geometried against cement" (noun → verb)
✓ "Silence architectured around them" (noun → verb)
✓ "The room tensioned" (noun → verb)
```

---

## Category 4: Anti-Pattern Compliance (15 points)

### 4A: Zero-Tolerance Violations (10 points)

**Starting score: 10. Deduct -2 per violation.**

Zero-tolerance patterns are sourced from Voice Anti-Patterns document. Common patterns:

| Pattern | Example | Why It Fails |
|---------|---------|--------------|
| Wrong-POV italics | `*We realized the trap*` (in 3rd person) | Breaks POV consistency |
| "With X precision" | `with practiced precision` | Cliche, tells not shows |
| Computer psychology | `brain processed the trauma` | Mechanical, not human |
| "With [adj] [noun]" | `with obvious concern` | Lazy description |

**Example scoring:**
```
Scene contains:
- Line 42: "with practiced precision" → -2
- Line 89: "his mind processed" → -2

SCORE: 10 - 4 = 6
```

### 4B: Formulaic Patterns (5 points)

**Starting score: 5. Deduct -1 per violation.**

| Pattern | Example | Why It Fails |
|---------|---------|--------------|
| Adverb-verb | `walked carefully` | Weak verb + modifier |
| "Despite the" | `despite the noise` | Overused transition |
| Vague atmosphere | `the air seemed tense` | Tells not shows |
| Repetition | Same pattern 3+ times | Lacks variety |

**Fixes:**
```
❌ "walked carefully" → ✓ "picked her way through"
❌ "the air seemed tense" → ✓ "her collar felt tight"
❌ "despite the noise" → ✓ "Noise erupted. She kept moving."
```

---

## Category 5: Phase Appropriateness (15 points)

### 5A: Voice Complexity Match (8 points)

**Core Question:** Is voice complexity appropriate for story phase?

| Score | Criteria |
|-------|----------|
| 8 | Perfect alignment with phase expectations |
| 6 | Generally correct with minor anachronisms |
| 3 | Wrong complexity level for phase |
| 0 | Completely inappropriate voice |

**How to evaluate:** Reference Voice Bundle → Phase Evolution document.

**Example phases:**

- **Act 1 (Setup):** Grounded, relatable voice - reader learning the world
- **Act 2A (Fun & Games):** Voice can flex into specialty domains
- **Act 2B (Bad Guys Close In):** Darker, more cynical
- **Act 3 (Finale):** Full integration of all learned voice elements

### 5B: Earned Language (7 points)

**Core Question:** Is specialized terminology justified by character's experience at this point?

| Score | Criteria |
|-------|----------|
| 7 | All technical terms earned through character experience |
| 5 | 1-2 slightly premature terms |
| 2 | Multiple premature specialized terms |
| 0 | Inappropriate academic jargon |

**Example:**
If character learns quantum physics in Chapter 12, they shouldn't use quantum terminology in Chapter 3.

---

## Automated Pattern Detection

### Regex Patterns for Anti-Pattern Detection

```python
ZERO_TOLERANCE_PATTERNS = {
    "first_person_italics": r"\*[^*]*\b(we|I)\b[^*]*\*",
    "with_precision": r"\bwith \w+ precision\b",
    "with_adjective_noun": r"\bwith (the |a |an )?(obvious|clear|visible|apparent) \w+\b",
    "computer_psychology": r"\b(brain|mind|consciousness) (processed|computed|analyzed|calculated)\b"
}

FORMULAIC_PATTERNS = {
    "adverb_verb": r"\b(walked|moved|spoke|said|looked) (carefully|slowly|quickly|quietly|loudly)\b",
    "despite_the": r"\bdespite the \w+\b",
    "seemed_was": r"\b(air|room|atmosphere|silence) (seemed|was|felt) \w+\b"
}
```

### Domain Detection (Populated from Voice Bundle)

```python
# These patterns come from Voice Bundle → Metaphor Domains
def load_domain_patterns(voice_bundle_path):
    """Load metaphor domain keywords from Voice Bundle."""
    domains = load_yaml(voice_bundle_path / "metaphor_domains.yaml")
    return {
        domain_name: r"\b(" + "|".join(keywords) + r")\b"
        for domain_name, keywords in domains.items()
    }
```

---

## Scoring Aggregation

### Scene Score Calculation

```python
@dataclass
class SceneScore:
    # Voice Authenticity (30 total)
    authenticity_test: int    # 0-10
    purpose_test: int         # 0-10
    fusion_test: int          # 0-10

    # Character Consistency (20 total)
    psychology: int           # 0-8
    capability: int           # 0-6
    relationship: int         # 0-6

    # Metaphor Discipline (20 total)
    domain_rotation: int      # 0-10
    simile_elimination: int   # 0-5
    transformation: int       # 0-5

    # Anti-Pattern Compliance (15 total)
    zero_tolerance: int       # 0-10
    formulaic: int            # 0-5

    # Phase Appropriateness (15 total)
    voice_complexity: int     # 0-8
    earned_language: int      # 0-7

    @property
    def voice_authenticity(self) -> int:
        return self.authenticity_test + self.purpose_test + self.fusion_test

    @property
    def character_consistency(self) -> int:
        return self.psychology + self.capability + self.relationship

    @property
    def metaphor_discipline(self) -> int:
        return self.domain_rotation + self.simile_elimination + self.transformation

    @property
    def anti_pattern_compliance(self) -> int:
        return self.zero_tolerance + self.formulaic

    @property
    def phase_appropriateness(self) -> int:
        return self.voice_complexity + self.earned_language

    @property
    def total(self) -> int:
        return (
            self.voice_authenticity +
            self.character_consistency +
            self.metaphor_discipline +
            self.anti_pattern_compliance +
            self.phase_appropriateness
        )

    @property
    def grade(self) -> str:
        t = self.total
        if t >= 92: return 'A'
        if t >= 85: return 'A-'
        if t >= 80: return 'B+'
        if t >= 75: return 'B'
        if t >= 70: return 'B-'
        if t >= 65: return 'C+'
        if t >= 60: return 'C'
        return 'D'
```

### Grade Thresholds and Actions

| Score | Grade | Enhancement Mode |
|-------|-------|------------------|
| 92-100 | A | None needed - publish |
| 85-91 | A- | Optional polish |
| 80-84 | B+ | Action Prompt (surgical fixes) |
| 70-79 | B/B- | 6-Pass Enhancement |
| <70 | C or below | Rewrite recommended |

---

## API Response Format

```json
{
  "total_score": 85,
  "grade": "A-",
  "categories": {
    "voice_authenticity": {
      "score": 26,
      "max": 30,
      "subcategories": {
        "authenticity_test": { "score": 9, "max": 10, "notes": "Minor AI-explaining in lines 45-50" },
        "purpose_test": { "score": 8, "max": 10, "notes": "Theme stated once at line 78" },
        "fusion_test": { "score": 9, "max": 10, "notes": "Strong fusion throughout" }
      }
    },
    "character_consistency": {
      "score": 18,
      "max": 20,
      "subcategories": {
        "psychology": { "score": 7, "max": 8, "notes": "One moment of trust contradicts Fatal Flaw" },
        "capability": { "score": 6, "max": 6, "notes": "All actions justified" },
        "relationship": { "score": 5, "max": 6, "notes": "One generic beat with mentor" }
      }
    },
    "metaphor_discipline": {
      "score": 17,
      "max": 20,
      "subcategories": {
        "domain_rotation": { "score": 8, "max": 10, "notes": "Cooking at 32%" },
        "simile_elimination": { "score": 4, "max": 5, "notes": "One simile at line 92" },
        "transformation": { "score": 5, "max": 5, "notes": "Excellent verb promotion" }
      }
    },
    "anti_pattern_compliance": {
      "score": 12,
      "max": 15,
      "subcategories": {
        "zero_tolerance": { "score": 8, "max": 10, "violations": ["with practiced precision (line 42)"] },
        "formulaic": { "score": 4, "max": 5, "violations": ["despite the noise (line 67)"] }
      }
    },
    "phase_appropriateness": {
      "score": 12,
      "max": 15,
      "subcategories": {
        "voice_complexity": { "score": 7, "max": 8, "notes": "One complexity anachronism" },
        "earned_language": { "score": 5, "max": 7, "notes": "Two premature technical terms" }
      }
    }
  },
  "enhancement_needed": true,
  "recommended_mode": "action_prompt",
  "action_prompt": "Fix the following 4 issues while preserving scene voice:\n1. Line 42: Replace 'with practiced precision'...\n2. Line 67: Rewrite 'despite the noise'...\n3. Line 78: Show theme through action instead of stating...\n4. Reduce cooking metaphors (replace 2 with architecture domain)"
}
```

---

## Migration from V1.0

This V2.0 rubric replaces the previous 5-dimension structure. Key changes:

| V1.0 | V2.0 | Notes |
|------|------|-------|
| Voice Consistency (25) | Voice Authenticity (30) | Split into 3 tests, weighted higher |
| Metaphor Discipline (25) | Metaphor Discipline (20) | Added domain rotation tracking |
| Anti-Pattern (20) | Anti-Pattern Compliance (15) | Split into zero-tolerance + formulaic |
| Structure (20) | *Moved to Scaffold* | Now part of scaffold validation |
| Functionality (10) | *Moved to Scaffold* | Now part of scaffold validation |
| - | Character Consistency (20) | New category from Explants skills |
| - | Phase Appropriateness (15) | New category from Explants skills |

**Rationale:** Structure and Functionality are scaffold concerns (Does the scene serve its purpose?). The new categories focus on execution quality (How well is it written?).

---

*Scoring Rubrics Specification v2.0*
*Writers Factory - Director Mode*
