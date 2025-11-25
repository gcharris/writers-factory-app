## Complete Inventory of All Stylistic Checks

### 1. SCORING CATEGORY WEIGHTS (100 points total)

| Category                | Default Weight | Configurable? |
| ----------------------- | -------------- | ------------- |
| Voice Authenticity      | 30 pts         | Should be     |
| Character Consistency   | 20 pts         | Should be     |
| Metaphor Discipline     | 20 pts         | Should be     |
| Anti-Pattern Compliance | 15 pts         | Should be     |
| Phase Appropriateness   | 15 pts         | Should be     |

------

### 2. ANTI-PATTERN DETECTION

#### Zero-Tolerance Patterns (-2 points each)

| Pattern Name             | Regex                                                        | Description                                     | Universal?                           |
| ------------------------ | ------------------------------------------------------------ | ----------------------------------------------- | ------------------------------------ |
| `first_person_italics`   | `\*[^*]*\b(we|I)\b[^*]*\*`                                   | First-person in italics (breaks 3rd person POV) | **No** - only matters for 3rd person |
| `with_precision`         | `\bwith \w+ precision\b`                                     | "With X precision" cliche                       | Somewhat - AI-typical                |
| `computer_psychology`    | `\b(brain|mind|consciousness) (processed|computed|analyzed|calculated)\b` | Computer metaphors for psychology               | Somewhat - AI-typical                |
| `with_obvious_adjective` | `\bwith (obvious|clear|visible|apparent|evident) \w+\b`      | "With obvious X" lazy description               | Somewhat                             |

#### Formulaic Patterns (-1 point each)

| Pattern Name        | Regex                                                        | Description                  | Universal?                                  |
| ------------------- | ------------------------------------------------------------ | ---------------------------- | ------------------------------------------- |
| `adverb_verb`       | `\b(walked|moved|spoke|said|looked|turned|stood) (carefully|slowly|quickly|quietly|loudly|suddenly)\b` | Weak adverb-verb combination | **Debatable** - some writers like this      |
| `despite_the`       | `\bdespite the \w+\b`                                        | Overused transition          | **No** - many writers use this deliberately |
| `atmosphere_seemed` | `\b(air|room|atmosphere|silence) (seemed|was|felt) \w+\b`    | Vague atmosphere             | Somewhat                                    |
| `suddenly`          | `\bsuddenly\b`                                               | Overused surprise word       | **Debatable**                               |

------

### 3. METAPHOR DISCIPLINE THRESHOLDS

| Setting                          | Current Value | Description                                     |
| -------------------------------- | ------------- | ----------------------------------------------- |
| Domain Saturation Threshold      | **30%**       | Max % for any single metaphor domain            |
| Heavy Reliance Threshold         | **35%**       | Deduct some points                              |
| Full Saturation Threshold        | **45%**       | Deduct all domain points                        |
| Simile Tolerance (Full Score)    | **0**         | Zero similes = 5/5 points                       |
| Simile Tolerance (Partial Score) | **2**         | 1-2 similes = 3/5 points                        |
| Simile Tolerance (Minimum Score) | **4**         | 3-4 similes = 1/5 points                        |
| Minimum Domains for Diversity    | **4**         | Need 4+ active domains for full transform score |

#### Default Metaphor Domains (Hard-coded)

- gambling, music, cooking, architecture, medicine, nature

------

### 4. ENHANCEMENT THRESHOLDS

| Setting                 | Current Value | Description                           |
| ----------------------- | ------------- | ------------------------------------- |
| Action Prompt Threshold | **85**        | Score 85+ → surgical fixes only       |
| Six-Pass Threshold      | **70**        | Score 70-84 → full 6-pass enhancement |
| Rewrite Threshold       | **<70**       | Score <70 → rewrite recommended       |

------

### 5. GRADE THRESHOLDS

| Grade | Minimum Score |
| ----- | ------------- |
| A     | 92            |
| A-    | 85            |
| B+    | 80            |
| B     | 75            |
| B-    | 70            |
| C+    | 65            |
| C     | 60            |
| D     | <60           |

------

### 6. 6-PASS ENHANCEMENT SPECIFICS

| Pass                         | Hard-coded Rules                                    |
| ---------------------------- | --------------------------------------------------- |
| Pass 1: Sensory Anchoring    | Target **3** sensory anchors per section            |
| Pass 2: Verb Promotion       | Convert **ALL** similes to direct metaphors         |
| Pass 3: Metaphor Rotation    | No domain > **30%**, gambling max **2-3 per scene** |
| Pass 4: Voice Embed          | Delete **all** hovering commentary                  |
| Pass 5: Italics Gate         | Limit to **0-1** per scene                          |
| Pass 6: Voice Authentication | Run 3 tests, minimal changes                        |

------

### 7. SIMILE DETECTION PATTERN

```python
r"\b(like|as if|as though|resembled|similar to)\b"
```

This is **hard-coded** and penalizes ALL similes - problematic for writers who use similes deliberately.



------

## What Should Be Configurable (50% Slider Concept)

Every item above should have a **project-level configuration** that:



1. **Can be disabled entirely** ("ignore")
2. **Can be severity-adjusted** (zero-tolerance ↔ formulaic ↔ warning ↔ ignore)
3. **Can have threshold adjusted** (30% → 50% for domain saturation)
4. **Can have custom patterns added/removed**

### Proposed Configuration Structure

```yaml
# voice_patterns.yaml (per project)
scoring_weights:
  voice_authenticity: 30      # 10-50
  character_consistency: 20   # 10-30
  metaphor_discipline: 20     # 10-30
  anti_pattern_compliance: 15 # 5-25
  phase_appropriateness: 15   # 5-25

anti_patterns:
  zero_tolerance:
    first_person_italics:
      enabled: true           # false for 1st person POV
      penalty: -2
    with_precision:
      enabled: true
      penalty: -2
    computer_psychology:
      enabled: true
      penalty: -2
    with_obvious_adjective:
      enabled: true
      penalty: -2
  
  formulaic:
    adverb_verb:
      enabled: true
      penalty: -1
    despite_the:
      enabled: false          # Writer likes this
      penalty: 0
    atmosphere_seemed:
      enabled: true
      penalty: -1
    suddenly:
      enabled: true
      penalty: -1
  
  custom: []                  # Writer's own patterns

metaphor_settings:
  saturation_threshold: 30    # 20-50%
  simile_tolerance: 0         # 0-10 allowed
  penalize_similes: true      # false = similes allowed
  min_domains_for_diversity: 3
  domains:                    # Custom for project
    - gambling
    - addiction
    - performance

enhancement:
  action_prompt_threshold: 85
  six_pass_threshold: 70
  italics_limit: 1            # 0-5
  sensory_anchors_per_section: 3
  
grade_thresholds:
  A: 92
  A-: 85
  # etc.
```

This would be generated during **Voice Calibration** and stored in the Voice Bundle directory alongside the markdown files.