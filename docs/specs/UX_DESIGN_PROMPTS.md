# Writers Factory - UX Design Prompts

**Generated for**: Gemini 3.0 / Figma Make
**Context**: Desktop Application (Tauri + Svelte)
**Date**: November 24, 2025

---

## Section A: UI Element Inventory

### 1. Global Navigation & Shell
*   **App Shell**: Three-column layout (Left Sidebar, Center Editor, Right Sidebar).
*   **Status Bar**: Bottom strip showing:
    *   Graph Stats (Nodes/Edges count).
    *   Metabolism Status (Uncommitted events, "Digesting" indicator).
    *   Agent Status (Active model, API latency).
    *   Conflict Warning (Red indicator if narrative contradictions exist).
*   **Command Palette** (`Cmd+K`): Spotlight-style modal for quick actions (Ingest, Digest, Switch Agent, Open File).
*   **Tabs/Workspace Switcher**: Mechanism to switch main view (Manuscript vs. Graph vs. Settings).

### 2. Core Writing Experience (Left & Center)
*   **File Tree (Left Sidebar)**:
    *   **Project Hierarchy**: Story Bible (locked structure), Manuscript (Acts/Chapters/Scenes), World, Characters.
    *   **Context Menus**: "Ingest to Graph", "Analyze Scene".
    *   **Sync Indicators**: Icons showing if file is synced to Graph.
*   **Main Editor (Center)**:
    *   **Monaco/Markdown Editor**: Clean, distraction-free writing area.
    *   **Inline Agent Actions**: "Ask Agent", "Enhance Selection" (via right-click or floating widget).
    *   **Gutter Indicators**: Line numbers, change tracking.
    *   **Breadcrumbs**: Path navigation (e.g., Act 1 > Chapter 3 > Scene 2).

### 3. Director Mode & Agents (Right Sidebar & Overlays)
*   **Foreman Chat Interface**:
    *   **Chat Stream**: Conversation with the Foreman agent.
    *   **Work Order Display**: Current task status (e.g., "Chapter 3: 25% Complete").
    *   **Mode Indicator**: Badge showing current mode (Architect / Director / Editor).
*   **Voice Calibration Tournament (Modal/View)**:
    *   **Variant Grid**: Display of 5 text variants side-by-side or in a grid.
    *   **Voting/Selection Controls**: "Select Winner", "Save as Reference".
    *   **Scoring Display**: 100-point score breakdown per variant.
*   **Scene Pipeline Dashboard**:
    *   **Scaffold View**: Read-only or editable outline for the scene.
    *   **Structure Selector**: Choice between 5 chapter layouts (Action, Character, etc.).
    *   **Generation Controls**: "Run Tournament", "Generate Variants".

### 4. Knowledge & Metabolism (Right Sidebar / Dedicated View)
*   **Health Dashboard**:
    *   **Vitals**: Node/Edge counts, recent entities.
    *   **Conflict List**: Detected narrative contradictions (e.g., "Eye color: Blue vs Green").
    *   **Metabolism Trigger**: "Digest Now" button to process chat history into graph.
*   **Graph Explorer (Modal/View)**:
    *   **Interactive Graph**: Nodes and edges visualization.
    *   **Node Details**: Sidebar showing properties of selected entity (e.g., Character attributes).
    *   **Search/Filter**: Find specific nodes or relationship types.
*   **NotebookLM Panel**:
    *   **Source List**: Available notebooks (World, Voice, Craft).
    *   **Query Interface**: Ask specific questions to external notebooks.

### 5. Settings & Configuration (Modal)
*   **Agent Configuration**: API Key inputs (masked), Model selection dropdowns.
*   **Scoring Rubric**: Sliders for weighting (Voice vs. Plot vs. Theme).
*   **Voice Strictness**: Dropdowns for "Authenticity", "Purpose", "Fusion".
*   **Project Overrides**: Visual indication of global vs. project-specific settings.

---

## Section B: AI Design Prompts

### Prompt 1 – The "Cockpit": Main Writing Workspace
**Role**: You are a Lead Product Designer for a professional creative IDE.
**Task**: Design the main interface of "Writers Factory," a desktop app for novelists.
**Context**: This is a tool for serious, structured writing, not just a text editor. It needs to feel like an IDE (like VS Code) but optimized for prose.
**Layout Requirements**:
*   **Three-Panel Layout**:
    *   **Left**: File Explorer tree showing a novel structure (Story Bible folder, Act 1 folder, Chapter files).
    *   **Center**: A clean, elegant Markdown editor showing a dramatic scene. Typography should be serif, highly readable.
    *   **Right**: The "Foreman" agent chat panel. It shows a "Work Order" at the top (e.g., "Current Task: Draft Scene 2.1") and a chat history below.
*   **Bottom Status Bar**: A thin, technical bar showing "Graph Nodes: 1,240", "Uncommitted: 3", and "Model: Claude 3.5".
**Visual Tone**: Dark mode, "Cyber-Noir" aesthetic. Slate grays, muted gold accents for "Director Mode" elements. Professional, focused, dense but organized.

### Prompt 2 – Director Mode: Voice Calibration Tournament
**Role**: You are a UI/UX Designer specializing in AI-human collaboration tools.
**Task**: Design the "Voice Calibration Tournament" interface.
**Context**: The user is selecting the "voice" for their novel. The AI has generated 5 different versions of the same paragraph using different personas (e.g., "Gritty Noir", "Lyrical", "Minimalist").
**Layout Requirements**:
*   **Header**: Title "Voice Calibration Tournament" and a progress bar "Round 1 of 3".
*   **Main Grid**: A horizontal scroll or grid layout displaying 5 cards.
    *   Each card contains a paragraph of text (the variant).
    *   Each card has a header identifying the agent/strategy (e.g., "Claude - Action Focus", "GPT-4 - Atmospheric").
    *   Each card has a "Select Winner" button and a "View Analysis" link.
*   **Comparison View**: A way to see them side-by-side.
**Visual Tone**: High-tech, comparative. Think "A/B Testing" dashboard meets "Literary Review". Clean typography to make reading the variants easy.

### Prompt 3 – The "Living Brain": Knowledge Graph Explorer
**Role**: You are a Data Visualization Designer.
**Task**: Design the Knowledge Graph Explorer view.
**Context**: The writer needs to see the connections in their story world (characters, locations, plot items).
**Layout Requirements**:
*   **Main Canvas**: A large, interactive force-directed graph. Nodes are circles (Characters, Locations), edges are lines connecting them.
    *   Nodes should have icons (👤 for characters, 📍 for locations).
    *   Selected node "Mickey Bardot" is highlighted.
*   **Overlay Panel (Right)**: A "Node Detail" floating panel showing data for "Mickey Bardot":
    *   Attributes: "Fatal Flaw: Hubris", "Eye Color: Grey".
    *   Relationships: "Brother of: Sarah", "Enemy of: The State".
*   **Controls**: Zoom/Pan controls, and a "Filter" bar to show only "Characters" or "Act 1 items".
**Visual Tone**: Scientific, futuristic. Deep blue/black background, neon node colors (cyan, magenta).

### Prompt 4 – Health Dashboard & Metabolism
**Role**: You are a System UI Designer.
**Task**: Design the "Health & Metabolism" Dashboard.
**Context**: This panel shows the "health" of the story structure and the status of the AI's background processing ("Metabolism").
**Layout Requirements**:
*   **Panel Layout**: A vertical sidebar or dashboard view.
*   **Section 1: Vitals**: Big number cards for "Total Nodes", "Total Edges", "Word Count".
*   **Section 2: Metabolism**: A status indicator showing "Digesting Session..." with a progress bar. A list of "Uncommitted Events" (e.g., "User defined new character: 'Rook'").
*   **Section 3: Conflicts**: A warning list showing narrative contradictions.
    *   Item: "Conflict: Rook's Age".
    *   Detail: "Story Bible says 30 vs. Scene 4 says 45".
    *   Action: "Resolve" button.
**Visual Tone**: Diagnostic, clean. Uses traffic light colors (Green/Yellow/Red) for status indicators.

### Prompt 5 – Settings Configuration Panel
**Role**: You are a UX Designer for complex configuration systems.
**Task**: Design the "Settings & Configuration" modal.
**Context**: Power users need to tweak the AI's behavior, scoring weights, and API keys.
**Layout Requirements**:
*   **Sidebar Navigation**: Categories like "Agents", "Scoring", "Voice", "Enhancement".
*   **Content Area (Scoring Category)**:
    *   **Sliders**: 5 linked sliders for "Voice Authenticity", "Character Consistency", "Metaphor Discipline", etc. They must sum to 100%.
    *   **Dropdown**: "Preset" selector (e.g., "Literary Fiction", "Thriller").
*   **Content Area (Agents Category)**:
    *   Input fields for API Keys (masked like passwords).
    *   "Test Connection" buttons next to each key.
**Visual Tone**: Utility-focused, clean. Standard form elements but styled to match the app's dark professional theme.

### Prompt 6 – Scene Pipeline: Scoring & Enhancement
**Role**: You are a UX Designer for editorial tools.
**Task**: Design the "Scene Evaluation" view.
**Context**: The AI has analyzed a written scene and is providing feedback and "enhancement" options.
**Layout Requirements**:
*   **Split View**:
    *   **Left**: The scene text (read-only or editable). Highlights on specific sentences (e.g., yellow for "Passive Voice", red for "Anti-Pattern").
    *   **Right**: The Analysis Panel.
*   **Analysis Panel**:
    *   **Score Card**: A big "85/100" score at the top.
    *   **Breakdown**: Radar chart or bar chart showing the 5 rubric categories (Voice, Character, etc.).
    *   **Action Actions**: A list of suggested fixes. "Apply Fix: Change passive voice to active" with an "Accept/Reject" toggle.
**Visual Tone**: Editorial, critical. Like a "Track Changes" interface on steroids. Clear distinction between the user's text and AI suggestions.

### Prompt 7 – Story Bible Architect
**Role**: You are a UX Designer for a wizard-style interface.
**Task**: Design the "Story Bible Architect" view.
**Context**: The user is building the foundational documents for their novel (Protagonist, World, Theme) with AI help.
**Layout Requirements**:
*   **Two-Column Layout**:
    *   **Left (Chat/Guide)**: The "Architect" agent asking questions. "Tell me about your protagonist's fatal flaw."
    *   **Right (Live Document)**: A preview of the `Protagonist.md` file being built in real-time.
*   **NotebookLM Integration**: A small "Reference" drawer showing "Consulting: Psychology Notebook".
**Visual Tone**: Constructive, foundational. Warmer tones (paper, sepia hints) to distinguish "Planning" mode from the "Cyber-Noir" of "Director Mode".

### Prompt 8 – Command Palette & Quick Actions
**Role**: You are a UI Interaction Designer.
**Task**: Design the Command Palette interaction.
**Context**: The user hits `Cmd+K` to open a quick action bar.
**Layout Requirements**:
*   **Overlay**: A centered modal search bar, floating over the blurred main interface.
*   **Search Input**: Large text input with placeholder "Type a command or search...".
*   **Results List**: A list of actionable items below the input.
    *   "Run Metabolism Digest" (System Action)
    *   "Switch to Director Mode" (Navigation)
    *   "Open Chapter 5" (File)
    *   "Ingest Story Bible" (Data Action)
*   **Keyboard Hints**: Small badges showing shortcuts (e.g., `↵` to select).
**Visual Tone**: Minimalist, fast. High contrast for readability.
