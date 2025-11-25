## Guidance for Scene-Level Agent Refinement

**Target Agent:** Scene Analyzer/Scorer (C.4) and Scene Enhancement Agent (C.5) **Objective:** Provide detailed instructions on refactoring the hard-coded *Explants*-era rules into configurable systems, ready for the generalized Writer's Factory. This focuses on making the current **Director Mode** scoring and enhancement functional for any project style.

### I. Generalizing the Scoring Rubric (Scene Analyzer C.4)

The current 100-point rubric weights are hard-coded (30/20/20/15/15). The Scene Analyzer must be updated to dynamically read the weights for the five categories from the **Settings Service** instead of using fixed values.

**Implementation Instruction:** The Scene Analyzer must retrieve the following configuration values from the **Scoring Rubric Weights** section of the Settings Service before calculating the score:

1. **Voice Authenticity Weight** (Default: 30)
2. **Character Consistency Weight** (Default: 20)
3. **Metaphor Discipline Weight** (Default: 20)
4. **Anti-Pattern Compliance Weight** (Default: 15)
5. **Phase Appropriateness Weight** (Default: 15)

**Crucial Logic Check:** Ensure the total weight retrieved always sums to 100 before proceeding with variant comparison.

### II. Implementing Dynamic Anti-Pattern Detection (Scene Analyzer C.4)

The current system relies on fixed Zero-Tolerance and Formulaic Patterns. These lists and their penalties must become dynamic based on the project's **Voice Calibration Document** and the **Anti-Pattern Detection Settings**.

**Implementation Instruction:** The Scene Analyzer must run two distinct anti-pattern passes:

#### Pass 1: Project-Specific Anti-Patterns

1. **Dynamic List Loading:** Retrieve the current lists of **Zero-Tolerance Patterns** and **Formulaic Patterns** from the **Anti-Pattern Detection Settings**.
2. **Severity Override Check:** Before applying a penalty, check the **Severity Overrides** map. If a writer has downgraded a built-in Zero-Tolerance pattern (e.g., `first_person_italics`) to a simple warning (Formulaic), apply the new configured penalty (-1 point) instead of the default Zero-Tolerance penalty (-2 points).
3. **Custom Pattern Integration:** Integrate detection for **Custom Patterns** defined by the writer.

#### Pass 2: Universal AI Anti-Patterns (Always Active)

1. **Run Pattern Matching:** Run the Scene Analyzer against the pre-defined list of **Universal AI Anti-Patterns**. These patterns (like **Promotional Puffery**, **Shallow -ing Analysis**, and **AI Vocabulary Overuse**) must be flagged regardless of project settings.
2. **Fixed Scoring Impact:** Assign a fixed penalty of **-0.5 points each** for these universal patterns, capped at **-3 points total** per scene, and ensure they are flagged in the score report for human review.
3. **Writer Override Check:** Consult the **Writer Override** mechanism in the Voice Calibration Document. If a writer explicitly allows a specific AI pattern (e.g., `Em Dash Overuse`), suppress the penalty and warning.

### III. Generalizing Metaphor Discipline (Scene Analyzer C.4 & Enhancement C.5)

The fixed rules concerning **Simile Tolerance** and **Domain Saturation** are critical roadblocks to generalization.

**Implementation Instruction (Scene Analyzer C.4):** Update the Metaphor Analysis to retrieve the following four settings dynamically from the **Metaphor Discipline Settings**:

1. **Domain Saturation Threshold:** (Default: 30%). Use this value (e.g., 20%-50%) to penalize scenes where any single metaphor domain exceeds the allowed percentage.
2. **Primary Domain Allowance:** (Default: 35%). Allow one designated primary domain to operate at this higher threshold if configured.
3. **Simile Tolerance:** (Default: 2). Instead of the hard-coded scheme penalizing *all* similes, calculate the penalty based on the retrieved tolerance level. If the writer sets tolerance to 4, only 5+ similes should trigger the lowest score tier (1/5 points).
4. **Minimum Domains Required:** (Default: 3). Use this value when scoring for **Metaphor Discipline** to ensure diversity.

**Implementation Instruction (Scene Enhancement C.5):** Update the **6-Pass Enhancement Mode**:

1. **Pass 2 (Verb Promotion):** The original rule to **Convert ALL similes to direct metaphors** must now be conditional. If the project's **Simile Tolerance** setting is greater than 0, the agent must be conservative in converting similes, preserving them if they fall within the tolerated limit.
2. **Pass 3 (Metaphor Rotation):** The agent must use the project-specific **Domain Saturation Threshold** retrieved from the settings, instead of the hard-coded **30%**.

### IV. Dynamic Enhancement Triggering (Scene Enhancement C.5)

The thresholds that trigger the three enhancement modes (Action Prompt, 6-Pass, Rewrite) must be configurable.

**Implementation Instruction:** The Foreman must retrieve the thresholds from the **Enhancement Pipeline Settings**:

1. **Action Prompt Mode:** Triggered if the score is between the **Action Prompt Threshold** (Default: 85) and the **Auto-Enhancement Threshold** (Default: 85). This results in **surgical fixes only**.
2. **6-Pass Enhancement Mode:** Triggered if the score falls below the **Auto-Enhancement Threshold** but above the **Rewrite Threshold** (Default: <70).
3. **Enhancement Aggressiveness:** The enhancement agent must read the **Enhancement Aggressiveness** level (Conservative/Medium/Aggressive) and adjust its scope of changes accordingly. For example, **Conservative** means minimal changes, only fixing violations.

