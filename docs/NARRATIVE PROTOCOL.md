

### **Writers Factory: Narrative Protocol & Methodology**



Version: 1.0

Scope: Defines the mandatory creative process and data artifacts required to engineer a professional novel within the Factory.

------



#### **1. Philosophy: Engineering Over "Pantsing"**



The Factory enforces a professional standard: **Creativity requires constraints.** The system guides the writer through a mandatory "Preparation Phase" (Phases 1-3) before allowing access to the "Execution Phase" (Drafting Chapter 1). This ensures no scene is written without a structural purpose.

------



#### **2. The Story Bible Blueprint (Data Structure)**



The "Story Bible" is not a single file but a collection of structured artifacts that the AI uses to "ground" its generation. The system must guide the user to create these specific documents.

**Phase 1: Foundational Mindset (The "Why")**

- **Goal:** Establish discipline and audience focus.
- **Artifacts (Input Data):**
  - `01_Mindset.md`: Commitment assessment. (AI uses this to gauge user seriousness/tone).
  - `02_Audience.md`: Target demographic and purpose. (AI uses this to tune vocabulary and pacing).
  - `03_Premise.md`: High Concept Logline. (The "North Star" for all critiques).
  - `04_Theme.md`: Core Theme/Life Lesson. (AI checks if scenes resonate with this theme).
  - `05_Voice.md`: Voice rules and research notes. (AI style guide).

**Phase 2: Character Construction (The "Who")**

- **Goal:** Create dimensional characters driven by contradiction.
- **Artifacts (Input Data):**
  - `Characters/Protagonist.md`:
    - **True Character vs. Characterization:** The core contradiction (e.g., "Honest but a Liar").
    - **Fatal Flaw:** The internal weakness blocking success.
    - **The Lie:** The mistaken belief driving the flaw.
  - `Characters/Cast.md`: Supporting characters defined by their *function* to the protagonist.

**Phase 3: Plot Architecture (The "What")**

- **Goal:** A structural blueprint ensuring pacing and emotional resonance.
- **Artifacts (Input Data):**
  - `Structure/Beat_Sheet.md`: The 15-Beat "Save the Cat" roadmap. (AI uses this to know "Where are we in the story?").
  - `Structure/Scene_Strategy.md`: For *every* scene:
    - **Goal:** What does the character want?
    - **Conflict:** What stops them?
    - **Outcome:** Do they get it? (Yes/No/But/And).
  - `World/Rules.md`: The physics and rules of the setting.

------



#### **3. The "Living Brain" Workflow**



How the system maintains and re-creates the Bible during writing.

1. **Ingestion (The Setup):**
   - User creates the artifacts in Phases 1-3 (likely querying NotebookLM to generate initial drafts).
   - The **Graph Engine** parses these files to build the initial state (Nodes: Characters, Themes; Edges: Relationships).
2. **Execution (The Drafting Loop):**
   - **Pre-Flight Check:** Before drafting a scene, the AI reads `Structure/Scene_Strategy.md` and `Characters/Protagonist.md`.
   - **Context Injection:** It injects the specific *Fatal Flaw* and *Current Beat* into the prompt.
   - **Drafting:** The Squad generates the scene.
3. **Maintenance (The Feedback Loop):**
   - **The "Archivist" Agent:** After a scene is finalized, this background agent analyzes it.
   - **Update Logic:**
     - *Did the character learn a lesson?* -> Update `Character Arc` progress.
     - *Did a new fact emerge?* -> Update `World/Rules.md`.
     - *Did the plot deviate?* -> Flag `Structure/Beat_Sheet.md` for review.
   - **Result:** The Story Bible is **dynamic**. It evolves with the manuscript, ensuring the "Brain" always has the latest truth.

------



#### **4. Next Steps for Implementation**



Now that we have defined *what* data we need, we can build the *technical components* to handle it.

1. **Save this Document:** Save this as `docs/NARRATIVE_PROTOCOL.md`.
2. **Update Roadmap:** Ensure the "Graph Ingestor" is specifically designed to parse these *exact* file types (`Mindset`, `Protagonist`, `Beat_Sheet`).
3. **Begin Phase 3:** Now we can confidently build the **Graph Ingestor**, knowing exactly what data structure it needs to look for.

