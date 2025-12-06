**5 Core Notebooks**

You should **NOT** create a separate notebook for every individual character or minor world detail.

Instead, you should consolidate your notes into the **5 Core Notebooks** (Character, Plot, Voice, World, Theme).

Here is the specific instruction strategy for the writer, explaining *why* the Factory needs the data grouped this way to build the Story Bible successfully.

1. Notebook 1: Characters (The Cast)

**Instruction:** Throw **all** character ideas into this single notebook. Do not create separate notebooks for each person.

• **Why?** The **AI Scaffolding Agent** is programmed to query this notebook to understand *relationships* and the cast hierarchy. It needs to see the Protagonist and Antagonist in the same context to detect if their goals properly conflict.

• **How to Organize Within the Notebook:**

  ◦ Upload separate documents (sources) for the **Protagonist** and **Antagonist** within this notebook.

  ◦ **Critical Labeling:** You must clearly label who is the "Protagonist" and who is the "Antagonist" in the text. The system specifically looks to extract the **Fatal Flaw** and **The Lie** for the main character to populate `Protagonist.md`.

  ◦ **Supporting Cast:** Group minor characters into a single "Cast List" document. The AI needs to scan this to ensure the cast functions as a "solar system" around the protagonist to reveal their dimensions.

2. Notebook 4: World (The Context)

**Instruction:** Throw **all** world-building types (magic systems, locations, history, politics) into this one notebook.

• **Why?** The Factory uses this data to populate `Rules.md` and check for **Graph Consistency**. The AI needs to see how your "Magic System" interacts with your "Politics" to catch logic errors (e.g., if magic is rare, why is the king a wizard?).

• **How to Organize Within the Notebook:**

  ◦ **Hard Rules vs. Soft Lore:** Explicitly separate "Hard Rules" (physics, magic limitations) from "History/Flavor." The AI extracts Hard Rules to create constraints for the **Graph Engine** to prevent plot holes later.

  ◦ **Locations:** List key locations here. The system will parse these into **Location Nodes** in the Knowledge Graph.

3. Notebook 5: Theme (The Argument)

**Instruction:** Dump all philosophical questions, arguments, and abstract ideas here.

• **Why?** The system uses this to generate `04_Theme.md` and score **Theme Resonance**. It needs to see *conflicting* ideas to identify the story's central "Philosophical Argument" or "Truth".

• **How to Organize Within the Notebook:**

  ◦ **The Question:** Frame your theme as a question (e.g., "Can redemption exist without sacrifice?").

  ◦ **Symbolism:** List objects you want to use as symbols here. The AI tracks **Symbol Recurrence** and **Evolution**, so it needs a master list of symbols to watch for.

Summary: The "Raw Material" Strategy

Think of these Notebooks as the **Raw Materials Loading Dock**. The Writers Factory (specifically the `SmartScaffoldWorkflow`) acts as the sorting machine.

• **Input:** You provide the "messy" but grouped raw text in NotebookLM.

• **Process:** The Agent runs specific queries (e.g., "Extract Protagonist Fatal Flaw," "Extract Magic Rules").

• **Output:** The Factory builds the structured **Story Bible** files (`Protagonist.md`, `Beat_Sheet.md`, `Rules.md`) in your project folder.

**Final Advice for the Writer:** "Don't pre-sort your ideas into tiny boxes. Group them by category (Character, World, Theme). The AI is smart enough to pull the specific needle it needs from the haystack, provided the haystack is labeled 'Needles'."