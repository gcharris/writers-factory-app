# 🏭 Writers Factory Desktop: Master Architecture (V4.0 - Cognitive Edition)



Version: 4.0 (The Cognitive Shift)

Date: 2025-11-22

Philosophy: Local-First, Graph-Driven, Metabolic Memory.

------



## 1. 🏗️ System Architecture (The Anatomy)



We are upgrading from a "Stateless Request/Response" model to a "Stateful Session" model with background processing.



### **A. Frontend (The Face)**



- **Tech Stack:** Tauri v2 (Rust) + SvelteKit.
- **New Component:** `SessionState` (Svelte Store). Tracks the "Working Memory" (current chat, unsaved scene ideas) separately from the "Long Term Memory" (files/graph).



### **B. Backend (The Brain)**



- **Tech Stack:** Python 3.12 (FastAPI) + `asyncio`.
- **Core Services:**
  - `Orchestrator`: Manages the Tournament (Drafting).
  - **[NEW] `SessionManager`**: Handles the "Workbench" (Short-term memory).
  - **[NEW] `MemoryService`**: The background worker (The Digestive System).
- **AI Stack:**
  - **Drafting:** Cloud APIs (GPT-4o, Claude, Grok).
  - **Digestion:** **Local Llama 3.2**. It runs cheaply in the background to clean, merge, and organize data.

------



## 2. 🧠 The Digestive System (Cognitive Metabolism)



This is the new core engine designed to prevent "Context Bloat" and "Hallucination."



### **Phase 1: The Mouth & Stomach (Session/Workbench)**



*The "Messy" Zone.*

- **Concept:** When you chat with an agent or brainstorm, it does **not** go to the Knowledge Graph immediately. It lives in the **Session**.
- **Storage:** SQLite Table `session_events` (Fast, ordered log of the conversation).
- **Action:** User clicks **"Commit"** or **"Save Scene."** This triggers the "Swallow" event.



### **Phase 2: The Liver (The Consolidator Agent)**



*The "Filtering" Zone (Background Async Task).*

- **Agent:** Local Llama 3.2 (JSON Mode).
- **Trigger:** Happens *after* the UI says "Saved."
- **Workflow (The ETL Pipeline):**
  1. **Extract:** Llama scans the new text for Entities & Facts.
  2. **Recall:** System queries the Graph: *"Do we already know about 'Mickey's Umbrella'?"*
  3. **Conflict Check:**
     - *New Fact:* "Mickey loves rain."
     - *Old Fact:* "Mickey hates rain."
     - *Result:* **CONFLICT DETECTED.**
  4. **Resolve:**
     - *Auto:* If confidence is low, discard.
     - *Manual:* Create a `MemoryIssue` alert for the user ("Conflict detected in Scene 4").
  5. **Update:** Only *verified, non-conflicting* facts are written to `knowledge_graph.json`.



### **Phase 3: Muscle Memory (Procedural Learning)**



*The "Skill" Zone.*

- **Concept:** Saving *how* to write, not just *what* to write.
- **Trigger:** When the Judge picks a winner in the Tournament.
- **Mechanism:**
  1. The system asks the Judge: *"Why did this draft win?"*
  2. Answer: *"It used short sentences and noir metaphors."*
  3. Action: This "Strategy" is vectorized and stored linked to the Character Node.
  4. **Payoff:** Next time you write this character, the prompt automatically includes: *"Style Instruction: Use short sentences and noir metaphors (proven effective in Scene 3)."*

------



## 3. 🔄 The Oracle (NotebookLM Integration)



*Unchanged from V3.0, but now integrated into the Digestion flow.*

- **Role:** The Source of Ground Truth.
- **Integration:** When the `Consolidator` finds a conflict (e.g., "What color are the uniforms?"), it can "Phone a Friend" (NotebookLM) to verify against the original PDF uploads before flagging it to the user.

------



## 4. 🛠️ Operational Workflows





### **A. The "Async Save" Pipeline**



1. **User Action:** User finishes a scene and hits `Cmd+S`.
2. **Immediate UI:** "Scene Saved to Disk." (User can keep working).
3. **Background Task:**
   - `Ingestor` wakes up.
   - Reads `Scene_4.md`.
   - Extracts 15 nodes.
   - Merges 12 (duplicates).
   - Updates 2 (new attributes).
   - Flags 1 (Conflict: "Mickey's eyes changed color").
4. **Notification:** A small "Health Dot" turns yellow. User clicks to see: *"Memory Conflict detected in Scene 4."*



### **B. The Tournament (Context-Aware)**



1. **Setup:** User selects Agents.
2. **Context Injection (The Payload):**
   - *Declarative:* "Mickey is a detective." (From Graph).
   - *Procedural:* "Write Mickey with cynicism." (From Style Vectors).
   - *Session:* "User just asked for more rain." (From Session Manager).
3. **Drafting:** Agents generate text.

------



## 5. 🗺️ Implementation Roadmap (Revised)



**Phase 1: The Foundation (✅ Done)**

- Native App Shell, File System, Basic Tournament.

**Phase 2: The Oracle (✅ Done)**

- NotebookLM MCP Bridge connected.

**Phase 3: The Metabolism (🚧 NEXT FOCUS)**

- **Step 1:** Restore `api.py` stability (Fixing the "Missing Ignition" bug).
- **Step 2:** **Build `SessionManager` (SQLite)**. Stop "fire-and-forget" chats; start logging sessions.
- **Step 3:** **Build `Consolidator` (Llama 3.2)**. The script that runs *after* the save to check for conflicts.
- **Step 4:** **The "Health Check" UI.** A panel showing the "Digestion Status" of the story.

------

