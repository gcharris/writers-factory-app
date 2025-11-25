## Architecture for Macro-Level Analysis (Graph Health Service)

**Target System:** Graph Health Service (New Asynchronous Agent) **Objective:** Define the architecture for **Level 2** (Structural Completeness) and **Level 3** (Narrative Health) checks that require chapter- or manuscript-level context, running asynchronously to the Scene Generation Pipeline.

### I. Layered Analysis Strategy

The system will use a **Two-Tier Analysis** structure:

1. **Tier 1 (Immediate):** Performed by the **Scene Analyzer (C.4)**, running immediately after scene creation, focusing on stylistic integrity (Voice, Anti-Patterns, Metaphor).
2. **Tier 2 (Asynchronous/Batch):** Performed by the new **Graph Health Service**, focusing on structural and macro-narrative integrity, triggered by the completion of a chapter or section.

### II. Implementation of Tier 2 Analysis Triggers

The analysis should run when enough data has accumulated to provide meaningful macro feedback.

#### 1. Primary Trigger: Chapter Assembly

The **Graph Health Service** checks must be triggered during **Chapter Assembly** (Step 4 of Director Mode).

- **Process:** When all scenes for a chapter are marked "Complete," the Foreman queues the chapter ID for the Graph Health Service.
- **Result:** The service runs Level 2/3 checks against the entire assembled chapter data stored in the Knowledge Graph.

#### 2. Secondary Trigger: Periodic Manuscript Health Check

Allow the writer to manually initiate a **Full Manuscript Health Check** at any time (e.g., once a week or upon Act completion) to run all structural checks across the entire graph.

### III. Required Level 3 Narrative Health Checks (Macro Focus)

The Graph Health Service is responsible for monitoring issues that emerge across scenes:

#### A. Structural Integrity Checks (Pacing and Progress)

| Check                         | Required Graph Data                                          | Logic & Thresholds                                           |
| ----------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Pacing Failure Detection**  | **Tension Nodes** (Scene Tension Score) for all scenes in the chapter. | Analyze the sequence of Tension Nodes. Flag a "flat spot" if **three consecutive chapters** exhibit the same Tension Score range [Implied by definition]. |
| **Beat Progress Validation**  | **Beat Nodes** (1-15) and their **Target Percentage** from `Beat_Sheet.md`. | Compare the total word count/scene count against the required Target Percentage for the current Beat. Flag **Plot Deviation** if completion significantly lags or exceeds the beat’s planned structural slot. |
| **Plot/Timeline Consistency** | **World/Rules.md** constraints and Character Location/Status History. | Run a query to detect **Timeline Errors** or **Dropped Threads** by checking for conflicts between facts established in the Story Bible and subsequent scene actions. |

#### B. Character Arc and Dimensionality Checks

| Check                               | Required Graph Data                                          | Logic & Thresholds                                           |
| ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Fatal Flaw Challenge Monitoring** | **Protagonist Node** (`Fatal Flaw`, `The Lie`) and the **Flaw Challenge Counter** (a graph property tracking time since last test). | If the counter exceeds the project’s **Flaw Challenge Frequency Threshold** (configured in Settings), trigger a Level 3 Warning. |
| **Cast Function Verification**      | **Cast Nodes** (supporting characters by function).          | Check scene appearances against defined function. Flag low scores if supporting characters appear but fail to **delineate the dimensions of the protagonist's complex nature** [Implied by definition]. |

#### C. Thematic and Symbolic Checks

| Check                                        | Required Graph Data                          | Logic & Thresholds                                           |
| -------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| **Symbolic Layering (Recurrence/Evolution)** | **Theme Nodes** and linked **Symbol Nodes**. | Track key symbols. Check if the symbol's meaning **changes as characters grow** over volumes or sections. Flag if recurrence is insufficient, or if the symbol remains static in meaning. |
| **Theme Resonance Score**                    | **Theme Statement** from `Theme.md`.         | Assess how effectively the current chapter connects back to the central theme. High score requires thematic elements to be explored during critical structural points (e.g., Beat 2 and Beat 12). |

### IV. Integration and Reporting

The Graph Health Service must report its findings clearly and integrate with the existing decision-making framework:

1. **Health Dashboard:** The results of the Tier 2 analysis should populate a **Manuscript Health Dashboard** (Frontend Work), separate from the per-scene score report.
2. **Foreman Integration:** If a macro check fails (e.g., Pacing Failure detected), the Foreman should use its **Challenge Intensity** setting to guide the writer's next decision (e.g., "Warning: The last three chapters have plateaued; the next scene must escalate the tension towards the Midpoint").

The implementation of the Graph Health Service ensures the Writers Factory provides not just line-level polish, but also foundational structural integrity, acting like a **structural engineer** who periodically checks the blueprints (Story Bible) against the actual construction (assembled chapters).