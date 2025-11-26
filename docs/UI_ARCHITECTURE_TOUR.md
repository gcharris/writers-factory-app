# UI Architecture Tour: The Writers Factory Studio

**Date**: November 25, 2025
**Purpose**: To map the visual layer of the Writers Factory, explaining how the frontend implements the "Cyber-Noir" aesthetic and the 4-panel studio workflow.

---

## 1. The Design Philosophy
*Visual Identity: "Cyber-Noir"*

The UI is built on a custom design system defined in `app.css`.
*   **Aesthetic**: Professional IDE meets Bloomberg Terminal.
*   **Palette**: Deep dark backgrounds (`#0f1419`) with functional accents:
    *   **Gold** (`#d4a574`): Primary actions, Director Mode.
    *   **Cyan** (`#58a6ff`): Interactive elements, links.
    *   **Purple** (`#a371f7`): Voice Calibration Mode.
    *   **Blue** (`#2f81f7`): Architect Mode.
    *   **Green** (`#3fb950`): Editor Mode / Success states.
*   **Typography**: `Inter` for UI, `JetBrains Mono` for code/data, `Merriweather` for prose.

---

## 2. The Layout Structure
*The 4-Panel Studio (`MainLayout.svelte`)*

The application uses a flexible, collapsible 4-panel layout designed to keep all tools within reach without clutter.

```mermaid
graph TD
    subgraph Layout
        Toolbar[Toolbar & Mode Tabs]
        
        subgraph Panels
            Studio[Studio Panel (Left)]
            Canvas[Canvas Panel (Center)]
            Graph[Graph Panel (Right-Inner)]
            Foreman[Foreman Panel (Right-Outer)]
        end
        
        StatusBar[Status Bar]
    end
```

### **1. Studio Panel** (Left)
*   **Component**: `StudioPanel.svelte`
*   **Role**: The "Action Deck". It changes based on the current **Foreman Mode**.
*   **Mechanism**: Uses `modeCards` reactive object to display relevant tools.
    *   *Architect*: "Create Story Bible", "Define Beats".
    *   *Voice*: "Launch Tournament", "Review Variants".
    *   *Director*: "Create Scaffold", "Generate Scene".
*   **State**: Actions trigger Modals (e.g., `StoryBibleWizard`, `VoiceTournamentLauncher`).

### **2. Canvas Panel** (Center)
*   **Component**: `FileTree.svelte` + `Editor.svelte`
*   **Role**: The "Workbench". Where the actual writing happens.
*   **Features**:
    *   **File Tree**: Navigates the project directory.
    *   **Editor**: A distraction-free writing area. Currently supports basic text editing and saving to the backend.

### **3. Graph Panel** (Right-Inner)
*   **Component**: `AgentPanel.svelte` (Placeholder for Knowledge Graph)
*   **Role**: The "Map".
*   **Current State**: Currently hosts the `AgentPanel` for selecting AI agents and running ad-hoc tournaments.
*   **Future State**: Will visualize the Knowledge Graph (Nodes/Edges) and Health Dashboard.

### **4. Foreman Panel** (Right-Outer)
*   **Component**: `ChatSidebar.svelte`
*   **Role**: The "Partner".
*   **Features**:
    *   **Chat Interface**: Direct line to the Foreman agent.
    *   **Work Order**: Visualizes the current project status (Templates, KB Stats).
    *   **Mode Awareness**: Displays the current mode (Architect, Director, etc.) and project context.

---

## 3. State Management
*The Nervous System (`stores.js`)*

State is managed via Svelte Stores, with key data persisted to `localStorage`.

*   **Session State**: `sessionId`, `chatHistory` (Persisted).
*   **Foreman State**: `foremanMode`, `foremanWorkOrder` (Synced with Backend).
*   **UI State**: `activeModal`, `showSettings`, `studioPanelCollapsed`.
*   **Data Stores**: `voiceAgents`, `sceneVariants`, `storyBibleStatus`.

---

## 4. Key Workflows

### **The Mode Switch**
When the Foreman changes modes (e.g., from Architect to Director), the **Studio Panel** automatically updates to show the relevant tools for that phase. The **Toolbar** tabs also reflect this change, allowing manual navigation if needed.

### **The Modal System**
Complex interactions (like the Story Bible Wizard or Settings) are handled in overlays (`Modal.svelte`) to preserve the context of the main workspace.

### **The "Live" Connection**
The frontend maintains a "heartbeat" with the backend:
*   **Foreman Status**: Polled on mount and after actions.
*   **File System**: Direct read/write via backend API.
*   **Agent Registry**: Fetched dynamically to populate the Agent Panel.
