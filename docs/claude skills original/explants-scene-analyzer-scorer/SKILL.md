---
name: explants-scene-analyzer-scorer
description: Comprehensive scene evaluation system for The Explants trilogy. Scores scenes using objective criteria, compares multiplier variants, identifies improvement needs, and provides specific actionable feedback. Integrates voice authentication, character consistency, and anti-pattern detection for quality control.
---

# Explants Scene Analyzer & Scorer

## MANDATORY WORKFLOW: Step-by-Step Process

### STEP 1: Load Reference Files (REQUIRED)

**Before analyzing ANY scene, load these files from references/ directory:**

1. **Mickey-Bardot-Enhanced-Trilogy-Voice-Gold-Standard.md** (ALWAYS LOAD FIRST)
   - Contains: Observer Test, Consciousness War Test, Cognitive Fusion Test
   - Use for: Voice Authenticity scoring (30 points)
   - Critical for: Understanding authentic Mickey voice vs. AI-Mickey

2. **Mickey Voice Anti-Pattern Sheet.md** (ALWAYS LOAD SECOND)
   - Contains: Zero-tolerance violations, formulaic patterns
   - Use for: Anti-Pattern Compliance scoring (15 points)
   - Critical for: Detecting "with X precision", first-person italics, etc.

3. **metaphor-domains.md** (LOAD FOR METAPHOR SCORING)
   - Contains: Domain rotation guidelines, casino limits
   - Use for: Metaphor Discipline scoring (20 points)
   - Critical for: Detecting casino saturation, simile usage

**OPTIONAL (load as needed):**

4. **scoring-rubrics.md** (FOR DETAILED EXAMPLES)
   - Use when: Uncertain about scoring edge cases
   - Contains: Detailed examples for each scoring level

5. **output-templates.md** (FOR OUTPUT FORMATTING)
   - Use when: User specifies analysis mode (Detailed/Quick Audit/Variant Comparison)
   - Contains: Three standard output formats

6. **Scene-Polishing-Ritual-8.2-Method.md** (FOR ENHANCEMENT RECOMMENDATIONS)
   - Use when: Providing enhancement strategy recommendations
   - Contains: Enhancement process reference

**ALTERNATIVE:** If project_knowledge_search is available, search for:
- "Mickey-Bardot-Enhanced-Trilogy-Voice-Gold-Standard"
- "Mickey Voice Anti-Pattern Sheet"
- Scene-specific context (chapter, phase, character relationships)

---

## The Critical Quality Control Gap This Skill Fills

### Problem Identified
- **Subjective evaluation** making quality assessment inconsistent
- **Vague feedback** ("needs work") without specific fixes
- **No systematic approach** to variant comparison or Volume 1 audit
- **Quality drift** across 136+ scenes without objective standards

### This Skill Provides
- **Objective 100-point scoring** with specific criteria
- **Automated violation detection** for zero-tolerance anti-patterns
- **Variant comparison** with hybrid recommendations
- **Specific actionable feedback** ("Replace line 67: 'quantum substrate' → 'underlying patterns'")
- **Systematic quality control** across entire trilogy

---

## Core Scoring Framework (100-Point Scale)

| Category | Weight | Purpose |
|----------|--------|---------|
| **Voice Authenticity** | 30% | Observer/Consciousness War/Cognitive Fusion tests |
| **Character Consistency** | 20% | Psychology, capabilities, relationships, motivations |
| **Metaphor Discipline** | 20% | Domain rotation, casino limits, simile elimination |
| **Anti-Pattern Compliance** | 15% | Zero-tolerance violations, formulaic patterns |
| **Phase Appropriateness** | 15% | Voice complexity, earned technical language |

### Quality Tiers

```
95-100: GOLD STANDARD (Scene 8.2 level, publishable as-is)
90-94:  A+ EXCELLENT (Minor polish only)
85-89:  A  STRONG (Enhancement pass recommended)
80-84:  A- GOOD (1-2 specific issues to address)
75-79:  B+ ACCEPTABLE (Enhancement required)
70-74:  B  FUNCTIONAL (Multiple issues, systematic enhancement)
65-69:  B- WEAK (Fundamental voice issues, consider multiplier)
60-64:  C+ POOR (Major rework needed)
<60:    FAIL (Complete rewrite or multiplier breakthrough)
```

---

## Primary Use Cases

### Use Case 1: Variant Comparison (5 Multiplier Outputs)

**Input:** 5 scene variations from explants-scene-multiplier
**Process:** Score each variant, identify strengths/weaknesses, recommend best approach
**Output:** Ranked variants with specific fixes and hybrid strategies

**Example Output:**
```
VARIANT ANALYSIS RESULTS:
1. Variant 5: 94/100 (A+ Excellent) ⭐ RECOMMENDED
2. Variant 2: 92/100 (A+ Excellent) 
3. Variant 1: 87/100 (A Strong)
4. Variant 4: 85/100 (A Strong)
5. Variant 3: 79/100 (B+ Acceptable)

RECOMMENDED: Variant 5 with one quick fix
Line 67: "quantum substrate" → "underlying patterns"
Expected post-fix score: 96/100
```

### Use Case 2: Volume 1 Scene Audit

**Input:** Existing scenes from completed Volume 1
**Process:** Batch scoring to identify which scenes need rework
**Output:** Prioritized list with specific enhancement needs

**Example Output:**
```
VOLUME 1 AUDIT RESULTS:
PRIORITY 1 (Immediate Rework): 12 scenes < 70 points
PRIORITY 2 (Enhancement Required): 23 scenes 70-79 points
PRIORITY 3 (Polish Pass): 45 scenes 80-89 points
GOLD STANDARD (Preserve): 8 scenes 95-100 points

SCENE: 1.3.2_blackjack.md - 73/100 (B Functional)
CRITICAL FIXES NEEDED:
- Line 47: "with practiced precision" [Zero-tolerance violation]
- Line 103: "we realized the trap" [First-person italics violation]
- Casino metaphor saturation: 62% (reduce to 25%)
```

### Use Case 3: Quality Gate Enforcement

**Input:** Enhanced scene ready for approval
**Process:** Final scoring to determine if scene meets publication standards
**Output:** Pass/fail with specific remaining issues

### Use Case 4: Agent Handoff (Action Prompt Generation)

**Input:** Single scene requiring specific fixes
**Process:** Generate executable fix instructions for another agent or human
**Output:** ACTION PROMPT with line-by-line surgical fixes

**When to Use:**
- Preparing fixes for another agent to apply
- Creating batch fix instructions for multiple scenes
- Documenting enhancement steps for human review
- Ensuring no unnecessary rewrites (surgical fixes only)

**Output Format:** MODE 4 (see references/output-templates.md)

**Example Workflow:**
```
1. Analyze scene: "Provide ACTION PROMPT for 1.18.1 Ben Demo.md"
   → Generates prompt with 9 specific fixes

2. Review in chat or save to: Enhancement-Prompts/1.18.1-action-prompt.md

3. Hand off to enhancement skill: "Apply fixes from 1.18.1-action-prompt.md"
   → Produces: 1.18.1 Ben Demo [enhanced].md

4. Human compares original vs enhanced, decides: accept/reject/iterate
```

**Integration:** Works with explants-scene-enhancement skill for automated fix application

### Use Case 5: Scene Multiplier Variant Selection

**Input:** 5 variation files from scene-multiplier skill
**Process:** Score each variant, comparative analysis, hybrid recommendations
**Output:** MODE 3 (VARIANT COMPARISON) with recommended best + hybrid options

**When to Use:**
- After scene-multiplier generates 5 creative variations
- Need objective scoring framework for comparison
- Want data-driven hybrid strategy suggestions
- Preparing for external review (e.g., Gemini AI)

**Integration with External Review:**
- Analyzer provides **structured scoring** (quantitative)
- External reviewer (Gemini) provides **creative judgment** (qualitative)
- Both perspectives inform human decision
- External review often catches what project-context-heavy analysis misses

**Output Format:** MODE 3 (see references/output-templates.md)

**Example Workflow:**

```
1. GENERATE VARIATIONS (scene-multiplier skill)
   Scene-multiplier creates:
   - 2.3.1-variation-A.md (casino-heavy metaphors)
   - 2.3.1-variation-B.md (addiction-focused)
   - 2.3.1-variation-C.md (martial arts emphasis)
   - 2.3.1-variation-D.md (performance angle)
   - 2.3.1-variation-E.md (balanced blend)

2. ANALYZER MODE 3: Structured Scoring
   "Compare variants A through E for scene 2.3.1"

   Output includes:
   - Scores table (all 5 variants with category breakdowns)
   - Recommended: Variant C (88/100)
   - Alternative: Variant B (85/100 - stronger character dynamics)
   - Hybrid suggestion: "Base C + dialogue from B (lines 45-52) + metaphor from D (line 78) = estimated 93/100"

3. EXTERNAL REVIEW (Optional - Gemini AI): Creative Judgment
   Paste all 5 variations into Gemini

   Gemini response might prefer:
   - Different variant (e.g., "B flows best despite lower technical score")
   - Different hybrid (e.g., "D's opening + C's middle + B's ending")
   - Identifies voice authenticity issues technical scoring missed

4. HUMAN SYNTHESIS
   Compare both analyses:
   - Analyzer: Technical scoring + hybrid recipe
   - Gemini: Flow/voice/creativity assessment

   Decide:
   - Pure variant (A, B, C, D, or E)
   - Analyzer's hybrid suggestion
   - Gemini's hybrid suggestion
   - Custom hybrid (human intuition combining both reviews)

5. PROCEED TO ENHANCEMENT
   Selected/hybrid variant → Analyzer MODE 2 (audit) → Generate action prompt → Enhancement → Verify
```

**Hybrid Assembly Methods:**
- **Manual:** Human copy/paste sections from multiple variants
- **Action Prompt:** Precise instructions for scene-writer to assemble hybrid
- **Direct Edit:** Apply specific line replacements to base variant

**Input Format:**
Provide all 5 variant files or paste text with clear variant labels:
```
Analyze these 5 variants using MODE 3:
[paste variation A text]

---VARIANT B---
[paste variation B text]

[etc.]
```

---

## STEP 2: Analysis Workflow

### For ANY Scene Analysis:

**Step 2A: Read the Scene**
- Note the phase (Vegas/Facility/Quantum/Post-Threshold)
- Identify primary characters
- Understand scene function in story

**Step 2B: Apply Scoring Framework**
Use the loaded reference files to score each category:

1. **Voice Authenticity (30 pts)** - Reference: Mickey-Bardot-Enhanced-Trilogy-Voice-Gold-Standard.md
   - Run Observer Test: Does this sound like Mickey observing?
   - Run Consciousness War Test: Does this serve the ideological argument?
   - Run Cognitive Fusion Test: Technical precision + cynical wisdom?

2. **Character Consistency (20 pts)** - Reference: Character psychology from Gold Standard
   - Psychology: Does character behave consistently?
   - Capabilities: Are actions within established limits?
   - Relationships: Are dynamics authentic?

3. **Metaphor Discipline (20 pts)** - Reference: metaphor-domains.md
   - Count metaphors by domain (gambling, addiction, martial arts, music, medical)
   - Calculate percentages - flag if casino >25% or any domain >30%
   - Detect similes ("like a/an", "as if", "resembled")

4. **Anti-Pattern Compliance (15 pts)** - Reference: Mickey Voice Anti-Pattern Sheet.md
   - Search for zero-tolerance violations (first-person italics, "with X precision")
   - Search for formulaic patterns ("walked carefully", "despite the", "the air seemed")
   - Deduct 2 pts per zero-tolerance, 1 pt per formulaic

5. **Phase Appropriateness (15 pts)** - Reference: Gold Standard Phase Evolution
   - Verify voice complexity matches phase
   - Check technical language is earned by Mickey's experience level

**Step 2C: Calculate Total Score**
- Sum all category scores (max 100)
- Determine quality tier (Gold Standard 95-100, Excellent 90-94, etc.)

**Step 2D: Generate Output**
- Reference: output-templates.md for format
- Choose mode: Detailed Analysis, Quick Audit, or Variant Comparison
- Provide specific line-by-line fixes
- Estimate post-fix score

---

## Detailed Scoring Criteria

### A. Voice Authenticity (30 points)

#### Observer Test (10 points)
**Question:** Does this sound like Mickey observing, or an AI explaining Mickey's observations?

**10 points:** Mickey observing in real-time, philosophy embedded in action
**7 points:** Mostly authentic but occasional AI-explaining-Mickey moments
**4 points:** Mix of authentic observation and academic commentary
**0 points:** Sounds like AI studying Mickey, not Mickey's voice

**Detection Patterns:**
```
✅ PASS: "Mickey watched the patterns repeat"
❌ FAIL: "Enhanced perspective provided clinical analysis"
❌ FAIL: "Mickey understood what his consciousness couldn't grasp"
```

#### Consciousness War Test (10 points)
**Question:** Does this scene serve the consciousness war argument?

**10 points:** Every scene beat serves ideological argument through embedded observation
**7 points:** Philosophical function present but sometimes stated vs. shown
**4 points:** Generic well-written prose, philosophy tangential
**0 points:** No philosophical function or consciousness warfare themes

**Requirements:**
- Shows consciousness resisting control/optimization
- Demonstrates cost of transcendence through concrete details
- Argues for authentic vs. optimized consciousness (embedded, not stated)

#### Cognitive Fusion Test (10 points)
**Question:** Does this demonstrate algorithmic precision applied to human folly?

**10 points:** Technical clarity serving cynical wisdom seamlessly
**7 points:** Technical clarity present but occasional cynicism loss
**4 points:** Either technical OR cynical, not fused
**0 points:** Academic analysis without street-smart grounding

### B. Character Consistency (20 points)

#### Psychology Consistency (8 points)
- **8 points:** Perfect alignment with established cognitive patterns
- **6 points:** Mostly consistent with 1-2 minor deviations
- **3 points:** Several inconsistencies with established psychology
- **0 points:** Character behaves in contradictory ways

**For Mickey:** Con artist + quantum hindsight + addiction recovery wisdom + protective mission

#### Capability Validation (6 points)
- **6 points:** All actions within established character capabilities
- **4 points:** One capability stretch but plausible
- **2 points:** Character does something unexplained by backstory
- **0 points:** Capability violations break established limits

#### Relationship Dynamics (6 points)
- **6 points:** Interactions authentic to established relationships
- **4 points:** Minor dynamic inconsistencies
- **2 points:** Relationship feels generic or misaligned
- **0 points:** Contradicts established relationship patterns

### C. Metaphor Discipline (20 points)

#### Domain Rotation (10 points)
**Target Distribution:**
- Gambling/casino: Maximum 25% of total metaphors
- Addiction/recovery: 20-30% (Mickey's core experience)
- Martial arts: 15-25% (physical grounding)
- Music/performance: 10-20% (rhythm and authenticity)
- Other domains: 15-25% (medical, architecture, childhood)

**Scoring:**
- **10 points:** Diverse rotation, no domain >30%, casino ≤25%
- **7 points:** Good rotation but slight overuse of one domain
- **4 points:** Heavy reliance on 1-2 domains, others neglected
- **0 points:** Casino/gambling saturation (>40% of metaphors)

#### Simile Elimination (5 points)
- **5 points:** All metaphors direct ("sunlight weaponized itself"), zero similes
- **3 points:** 1-2 similes present ("like a weapon")
- **1 point:** Multiple similes weakening prose
- **0 points:** Simile-heavy prose ("like," "as if," "resembled")

#### Direct Transformation (5 points)
- **5 points:** Objects/concepts BECOME metaphors through verb promotion
- **3 points:** Mix of direct and distant metaphors
- **1 point:** Mostly comparison-based metaphors
- **0 points:** All metaphors are comparisons, no transformation

### D. Anti-Pattern Compliance (15 points)

#### Zero-Tolerance Violations (10 points)
**Each violation = -2 points**

**Critical Patterns:**
- First-person italics: `*We realized*` → `*Mickey realized*`
- "With [adjective] precision": `with practiced precision` → DELETE

- **"With + Abstract Noun" (MANNER violations)**: CRITICAL PATTERN - Very common, easy to miss

  **The Problem:** Using "with + abstract noun" as a lazy shortcut to describe HOW an action is performed. This is "generic AI literary voice" - it TELLS instead of SHOWS. It's academic commentary, not lived experience.

  **❌ UNACCEPTABLE (Manner "With"):**
  - `with practiced efficiency` → Show the efficiency through action
  - `with the confidence of a weapon` → Show the confidence, don't tell it
  - `with familiar hunger` → `hunger familiar as the cards` (make it concrete)
  - `with the muscle memory of addiction` → `The old routine took over`
  - `with temporary euphoria` → `flooded him—temporary euphoria`
  - `With a flourish...` → Show the flourish through specific action

  **✅ ACCEPTABLE (Prepositional "With"):**
  - `with a few scattered players` (describing state, not manner)
  - `with each win` (functional relationship, not manner)
  - `He was with Noni` (prepositional relationship)
  - `He hit the guy with the bottle` (tool/instrument, not manner)

  **The Fix Pattern (Mickey's Voice):**
  - Instead of: "He did it with confidence"
  - Mickey's Voice: Show the action itself. "The edges snapped. The weapon was loaded."

  **Detection regex:** `\bwith (the |a |an )?([\w]+) ([\w]+)\b`
  **NOTE:** This regex catches BOTH types. Human review required to distinguish manner vs. prepositional usage.

- **Weak Similes ("Like/As" violations)**: CRITICAL - Violates "Literal Metaphorical Reality"

  **Mickey's Rule:** "My voice avoids traditional similes. I don't say 'X is like Y.' In my world, 'X IS Y.' It's what the guides call 'Literal Metaphorical Reality.'"

  **❌ UNACCEPTABLE (Traditional Simile):**
  - `pips crawling like ants` → Things don't RESEMBLE other things

  **✅ ACCEPTABLE (Literal Metaphorical Reality):**
  - `pips crawled, little black ants on a mission` → The pips BECOME ants
  - `The pips became ants, crawling over the felt` → Direct transformation

  **Why This Matters:** This isn't just style. It's how this consciousness works. In Mickey's quantum-analog fusion perspective, things don't resemble other things - they transform into them.

  **Detection regex:** `\b(like (a|an|the)|as if|resembled|seemed like)\b`

- Computer metaphors for psychology: `brain processed` → Use addiction/gambling metaphors

#### Formulaic Patterns (5 points)
**Each violation = -1 point**

**Detection Patterns:**
- "walked [adverb]ly" → Show specific movement
- "despite/because/even though" → Cut explanatory language
- "the air seemed to" → Character-specific sensory details
- Recognition repetition: Vary "Mickey recognized" constructions

### E. Phase Appropriateness (15 points)

#### Voice Complexity Match (8 points)
**Phase Evolution:**
- **Phase 1 (Vegas):** Grounded noir, casino/performance metaphors
- **Phase 2 (Facility):** Blended analog/quantum awareness
- **Phase 3 (Quantum):** Enhanced consciousness, process thinking
- **Phase 4 (Post-Threshold):** Full quantum-analog integration

**Scoring:**
- **8 points:** Perfect phase alignment
- **6 points:** Mostly appropriate with minor anachronisms
- **3 points:** Voice complexity mismatch
- **0 points:** Completely wrong phase voice

#### Earned Technical Language (7 points)
- **7 points:** Technical terms justified by Mickey's quantum experience
- **5 points:** Mostly earned but 1-2 premature technical terms
- **2 points:** Technical language before Mickey has context
- **0 points:** Academic jargon inappropriate to Mickey's knowledge state

---

## Automated Detection Patterns

### Zero-Tolerance Violations
```
first_person_italics: \*[^*]*\b(we|I)\b[^*]*\*
with_precision: \bwith \w+ precision\b
with_adjective_noun: \bwith (the |a |an )?([\w]+) ([\w]+)\b
computer_psychology: \b(processed|downloaded|uploaded)\b.*\b(emotion|thought|feeling)\b
formulaic_walking: \bwalked \w+ly\b
explanatory_connectors: \b(despite|because|even though|due to)\b
```

### Metaphor Domain Detection
```
gambling: \b(casino|poker|blackjack|chips|dealer|house edge|odds|bet|wager|gamble)\b
addiction: \b(craving|withdrawal|detox|relapse|recovery|sobriety|fix|dependency)\b
martial_arts: \b(stance|balance|center|kata|sparring|dojo|sensei|discipline)\b
music: \b(rhythm|tempo|harmony|cadence|note|chord|symphony|tune)\b
medical: \b(surgical|diagnosis|symptom|treatment|therapy|prescription|anatomy)\b
```

### Quality Checks
```
simile_detection: \b(like (a|an|the)|as if|resembled|seemed like)\b
voice_hovering: \b(Enhanced perspective|providing analysis|clinical analysis)\b
academic_tone: \b(furthermore|moreover|in conclusion|it should be noted)\b
```

---

## Application Guidelines

### For Variant Comparison

**Step 1: Score All Variants**
```
Variant 1: 87/100 (A - Strong)
Variant 2: 92/100 (A+ - Excellent)
Variant 3: 79/100 (B+ - Acceptable)
Variant 4: 85/100 (A - Strong)
Variant 5: 94/100 (A+ - Excellent) ⭐ RECOMMENDED
```

**Step 2: Category Analysis**
Identify which variant excels in each category:
- Best voice authenticity: Variant 5 (29/30)
- Best character consistency: Variant 2 (19/20)
- Best metaphor discipline: Variant 5 (19/20)
- Cleanest anti-patterns: Variant 5 (15/15)

**Step 3: Specific Fixes**
```
VARIANT 5 FIXES:
Line 67: "quantum substrate" → "underlying patterns" (+4 points)
Expected post-fix score: 98/100 (Gold Standard)
```

**Step 4: Hybrid Strategy (Optional)**
```
HYBRID RECOMMENDATION:
Base: Variant 5 (strongest overall)
Incorporate from V2: Character interaction (lines 45-62) - stronger dynamics
Expected hybrid score: 96/100
```

### For Volume 1 Audit

**Step 1: Batch Processing**
Score all scenes systematically:
```
PART 1: 44 scenes - Average score: 78/100
PART 2: 39 scenes - Average score: 82/100
PART 3: 14 scenes - Average score: 85/100
PART 4: 39 scenes - Average score: 81/100
```

**Step 2: Prioritization**
```
IMMEDIATE ATTENTION (Score < 70): 12 scenes
ENHANCEMENT REQUIRED (70-79): 23 scenes
POLISH RECOMMENDED (80-89): 45 scenes
EXCELLENT (90-94): 48 scenes
GOLD STANDARD (95-100): 8 scenes
```

**Step 3: Detailed Reports**
```
SCENE: 1.3.2_blackjack.md
SCORE: 73/100 (B - Functional)
ENHANCEMENT REQUIRED

CRITICAL ISSUES:
❌ Line 47: "with practiced precision" [Zero-tolerance]
❌ Line 103: "*we realized the trap*" [First-person italics]
❌ Casino metaphor saturation: 18/29 metaphors (62%)

RECOMMENDED FIXES:
1. Delete "with practiced precision" phrase
2. Change "*we realized*" to "*Mickey realized*"
3. Convert 8 casino metaphors to addiction/martial arts
4. Expected post-fix score: 84/100 (A-)
```

---

## Integration with Other Skills

### Workflow Integration
1. **explants-scene-multiplier** → Generate 5 variants
2. **explants-scene-analyzer-scorer** → Score and recommend best
3. **explants-scene-enhancement** → Apply specific fixes
4. **explants-scene-analyzer-scorer** → Final quality gate

### Voice Authentication Connection
This skill operationalizes the voice tests from:
- Mickey-Bardot-Enhanced-Trilogy-Voice-Gold-Standard
- Mickey Voice Anti-Pattern Sheet
- Enhanced-Voice-Strategy-Advanced

### Character Consistency Connection
Validates scenes against:
- mickey-bardot-character-identity framework
- Character decision patterns and psychology
- Relationship dynamics and trust patterns

---

## Quality Gates and Standards

### Publication Standards
- **Minimum acceptable:** 80/100 (A- Good)
- **Recommended standard:** 85/100 (A Strong)
- **Gold standard target:** 95/100 (Publishable as-is)

### Enhancement Triggers
- **Score < 70:** Consider multiplier breakthrough
- **Score 70-79:** Enhancement pass required
- **Score 80-84:** Targeted fixes for specific issues
- **Score 85-89:** Polish pass recommended
- **Score 90-94:** Minor tweaks only
- **Score 95-100:** Preserve as-is

### Success Markers
- **Authentic Mickey voice** that passes all three authentication tests
- **Character decisions** that feel inevitable given psychology and mission
- **Metaphor discipline** that serves story without domain saturation
- **Clean prose** free of anti-patterns and formulaic constructions
- **Phase-appropriate complexity** that matches Mickey's knowledge evolution

---

**Created:** October 2024  
**Purpose:** Objective scene evaluation and quality control for The Explants trilogy  
**Integration:** Works with voice, character identity, scene generation, and enhancement skills  
**Status:** Primary quality assurance tool for trilogy production