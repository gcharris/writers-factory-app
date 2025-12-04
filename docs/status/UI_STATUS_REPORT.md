# UI Status Report & Roadmap

## ✅ Completed & Working Features

### 1. Unified AI Model & Key Configuration
*   **Shared Components:** Created `CloudModelsList.svelte` and `PremiumKeyForm.svelte` to ensure identical UI/UX between the Setup Wizard and Settings Panel.
*   **Consistent Data:** Both views now use the same data source and logic for displaying model status and pricing.

### 2. Key Management (formerly Premium Keys)
*   **Renamed & Reorganized:** The section is now clearly labeled "Key Management".
*   **Subscription Gating:** Implemented a "Writers Factory Subscription" section.
    *   **Code:** `skoltech2026`
    *   **Functionality:** Unlocks "Included Free" models (DeepSeek, Moonshot, etc.) across the app.
    *   **Persistence:** Subscription status is saved to `localStorage` so it persists across reloads.
*   **Premium Keys:** Users can configure OpenAI, Anthropic, xAI, and Gemini keys.
*   **Link Fixes:** "Get API Key" links now correctly open in a new tab.

### 3. AI Models List
*   **Moonshot Fix:** Corrected the provider ID to `kimi` to match the backend, ensuring accurate status reporting.
*   **Gating Logic:** "Included Free" models show as "Locked" until the subscription code is entered.
*   **Visual Feedback:** Added "Unlock" buttons and visual indicators for locked states.

### 4. General UI Polish
*   **Sidebar:** Updated labels to "Key Management" and "AI Models" for clarity.
*   **Navigation:** "Configure" buttons in the AI Models list correctly navigate to the Key Management tab.

---

## 🚧 Remaining UI Features & Improvements

### 1. Squad Management (High Priority)
*   **Current State:** The "Orchestrator" (Squad) settings are likely basic or using old components (`SettingsSquad.svelte`).
*   **Goal:** Refactor to use a shared, premium UI similar to the new Key Management.
*   **Features Needed:**
    *   Visual "Squad" builder (drag-and-drop or card-based).
    *   Role configuration (Editor, Researcher, Writer).
    *   Model assignment per agent (e.g., assign Claude to Editor, GPT-4 to Writer).

### 2. Voice Settings
*   **Current State:** Placeholder or basic UI.
*   **Goal:** Create a dedicated "Voice" settings panel.
*   **Features Needed:**
    *   TTS Provider selection (OpenAI, ElevenLabs, Local).
    *   Voice preview/playback.
    *   Speed/Pitch controls.

### 3. Advanced Settings
*   **Current State:** Placeholder.
*   **Goal:** Implement advanced configuration options.
*   **Features Needed:**
    *   Local LLM endpoint configuration (Ollama URL).
    *   Context window size adjustments.
    *   Temperature/Top-P defaults.
    *   Data management (clear cache, export data).

### 4. Backend Integration (Technical Debt)
*   **Subscription Validation:** Move the `skoltech2026` check from client-side to a proper backend endpoint for security.
*   **Key Validation:** Implement real "Test" buttons for premium keys (currently we have the UI but need to ensure the backend `test_key` endpoint supports all providers).

### 5. Visual Polish
*   **Animations:** Add subtle entry animations for lists and modals.
*   **Mobile Responsiveness:** Verify and improve layout on smaller screens (if applicable).
*   **Dark/Light Mode:** Ensure consistent theming if light mode is supported (currently optimized for Dark Mode).
