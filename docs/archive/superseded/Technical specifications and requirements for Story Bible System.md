## Technical specifications and requirements for Story Bible System

This document outlines the **technical specifications and requirements** for implementing **Phase 2: Story Bible System**, focusing on the ingestion of unstructured user data (from NotebookLM) and the subsequent generation and parsing of required Story Bible artifacts.

This system is mandated to enforce the **Structure Before Freedom** philosophy, requiring the completion and validation of these artifacts before the Execution Phase (drafting) begins.

------

## Writers Factory: Phase 2 Technical Specification (Story Bible Scaffolding)

**Target Audience:** AI Programmer, Backend Agent Developer **Phase Goal:** Convert unstructured research/notes (NotebookLM export) into required, structured Story Bible Markdown files, then ingest these into the Knowledge Graph. **Dependency:** Phase 0 (NotebookLM Bridge/Ingestion) must be complete.

### I. Required Story Bible Artifacts and Storage

The Story Bible serves as the **World Bible** and the basis for **Context Injection** (RAG-lite). All artifacts must be stored as Markdown files within the defined project folder structure, which is subsequently ingested by the Graph Engine.

#### A. Required Artifact Schema (Mandatory for Phase 2 Completion)

The system must create scaffolding templates for the following required documents:

1. **`Protagonist.md`**: Defines the central character's internal and external complexity.
2. **`Beat_Sheet.md`**: Enforces the macro-structure of the narrative.
3. **`Scene_Strategy.md`**: Placeholder for future scene-level execution plans.
4. **`04_Theme.md` / `Themes_and_Philosophy/`**: Captures core ideas for **Theme Resonance** checks.

#### B. Directory Structure (Output Location)

The AI scaffolding agent must create and populate files within the defined standard folder structure (e.g., under `content/my-novel/`):

| Folder Name                   | Required Files/Content               | Source Rationale                                             |
| ----------------------------- | ------------------------------------ | ------------------------------------------------------------ |
| **`/Characters/`**            | `Protagonist.md`, `Antagonist.md`    | Maps to the Character Development dashboard, tracking conflicts and arcs. |
| **`/Story_Structure/`**       | `Beat_Sheet.md`, `Scene_Strategy.md` | Aligns with Chapter Planner requirements for flow consistency. |
| **`/Themes_and_Philosophy/`** | `04_Theme.md`, `05_Philosophy.md`    | Essential for **Level 3: Narrative Health** checks (Theme Resonance) and Symbolic Layering. |
| **`/World_Building/`**        | `World/Rules.md`, `Locations.md`     | Captures unique setting rules and facts for consistency checks. |
| **`/Research/`**              | `NotebookLM_Export_Summary.md`       | Contains synthesized source material from external NotebookLM data. |

### II. Data Ingestion and Scaffolding Logic

The system initialization must begin with the **NotebookLM Preparation** step, where the user has uploaded research, journals, or personal writing. The AI’s first task is to process this unstructured data and use it to pre-populate the Story Bible scaffolding.

#### A. AI Scaffolding Agent Task

A specialized agent (part of the **Guided Creation Wizard**) must be tasked to analyze the NotebookLM export and synthesize content for the required fields.

| Step                              | Agent Task & Logic                                           | Source Reference |
| --------------------------------- | ------------------------------------------------------------ | ---------------- |
| **1. Source Data Retrieval**      | Query the **NotebookLM Bridge** for the uploaded text/notes (e.g., 5,000 words of personal writing/research). |                  |
| **2. High-Concept Extraction**    | **Prompt Logic:** Analyze the source data for keywords related to premise, logline components (character, goal, conflict), genre, and tone. If a logline exists, extract it to pre-populate **High Concept Development** (Q6-Q10). |                  |
| **3. Non-Fiction Branching**      | **Conditional Logic:** If genre is non-fiction, assess the corpus for the **3 Keys**. Extract passages demonstrating: 1. Deep knowledge ("head knowledge"); 2. Deep emotional conviction ("heart knowledge"). Flag insufficient conviction for later prompting. |                  |
| **4. Character & Flaw Synthesis** | **Prompt Logic:** Synthesize a draft of the protagonist's core conflict. Search for descriptions of goals, fears, and weaknesses. Draft the **Fatal Flaw** and the **Mistaken Belief** (The Lie). |                  |
| **5. Voice Profile Generation**   | **Output:** Generate a detailed **Voice Profile** based on the user's personal writing. This profile is immediately used by the Stylometry agents (Phase 3) to ensure the writer aims to **sound like themselves**. |                  |

### III. Core Parser Requirements

The following parsers are critical for extracting structured data from the Markdown files to update the Knowledge Graph (`nodes` and `edges`). This data is necessary for **Level 3: Narrative Health Checks** (Phase 3).

#### A. `Protagonist.md` Parser (`Protagonist.md` is a required field)

The parser must distinguish between the character's internal reality and external presentation, and flag weak character design.

| Field to Extract (Graph Node Data) | Source Definition & Parser Logic                             | Rationale (Health Check)                                     |
| ---------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **True Character**                 | Core traits, internal disposition (loyal, honest, cowardly). | Used for **Character Alignment** scoring (Step 3 in Pipeline). |
| **Characterization**               | Observable qualities (appearance, mannerisms, speech).       | Used for **Voice Consistency** checks (Step 3 in Pipeline).  |
| **Fatal Flaw / Lie**               | The weakness that drives the plot/conflict. The **Mistaken Belief** driving the flaw. | Critical for **Flaw Challenge** detection (Level 3 Health Check). |
| **Contradiction Metric**           | A calculated score (e.g., 0.0-1.0) assessing complexity. **Logic:** Detect contradiction *within* true character (e.g., ambitious but guilt-ridden) or *between* True Character and Characterization (e.g., charming thief). The protagonist **must** be the most dimensional character. | Prevents "stick figure" characters.                          |

#### B. `Beat_Sheet.md` Parser (`Beat_Sheet.md` is a required field)

This parser must strictly enforce the **Save the Cat! 15-Beat Walkthrough** structure.

| Field to Extract (Graph Node Data) | Source Definition & Parser Logic                             | Rationale (Graph Node/Edge)                                  |
| ---------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Beat Sequence**                  | 1 to 15 (e.g., Beat 4: Catalyst).                            | Creates **Beat Nodes** linked by `ADVANCES` edges.           |
| **Target Percentage**              | The beat’s approximate location (e.g., 10%, 50%, 80%).       | Used by the **Pacing Graph** (Day 4 activity) to visualize tension against structure. |
| **Midpoint Type**                  | Must identify if Beat 9 (Midpoint) is a **"false victory"** or a **"false defeat"**. | Determines the required direction (upward/downward) of the subsequent **Bad Guys Close In** sequence. |
| **Theme Link**                     | Extracted Beat 2 (**Theme Stated**) content.                 | Used to verify if the **Dark Night of the Soul** (Beat 12) correctly processes and learns the theme/life lesson. |

### IV. Validation and Graph Integration

Phase 2 is formally complete only when the structural validation passes, triggering the shift to Phase 3 (Execution).

#### A. Phase 2 Completion Validation (Level 2 Health Checks)

The system must run **Level 2: Story Bible Completeness** checks:

- [ ] All 5 foundational docs exist.
- [ ] Protagonist has Fatal Flaw defined.
- [ ] Beat Sheet has all 15 beats defined.
- [ ] Scene Strategy exists for drafted scenes (Placeholder for later).

#### B. Graph Ingestion Flow

Upon successful validation, the parsed data must immediately initialize the **Knowledge Graph** (Step 1 of the "Living Brain" metabolism).

- **Ingestion:** Parse Story Bible Markdown files → Build initial graph structure.
- **Node Creation:** Create `Character`, `Beat`, `Theme`, and `Location` Nodes based on parsed data.
- **Edge Creation:** Create `KNOWS`, `DEPENDS_ON`, and `CONTRADICTS` Edges to map relationships and conflicts defined in the Story Bible.

This rigorous data ingestion ensures that all subsequent drafting via the Scene Generation Pipeline (Phase 3) has the necessary **context** to enforce **Graph Consistency** and **Character Alignment** scoring.

------

**Analogy for System Function:** The Story Bible System acts like a sophisticated pre-flight check for a commercial airliner. The AI takes the pilot's disorganized travel notes (NotebookLM research) and automatically loads them into the **structured flight plan** (`Protagonist.md` and `Beat_Sheet.md`). The parser then verifies that all critical components (like the **Fatal Flaw** and **15 plot beats**) are present and correctly calibrated before the plane (the manuscript) is cleared for takeoff (Phase 3: Execution).