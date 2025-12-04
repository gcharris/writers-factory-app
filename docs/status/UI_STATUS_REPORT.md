# UI Status Report & Roadmap

*Last Updated: December 4, 2025*

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

### 5. Squad Management (✅ COMPLETE - Dec 4, 2025)
*   **Enhanced SettingsSquad.svelte:** Refactored with improved layout (~400 lines).
*   **RoleModelSelector.svelte:** NEW component for per-role model assignment (~300 lines).
*   **HealthCheckModelConfig.svelte:** NEW component for health check model configuration (~180 lines).
*   **Tab Rename:** Changed from "Orchestrator" to "Squad" in settings sidebar.
*   **Features Delivered:**
    *   Role-based model selection (Editor, Researcher, Writer, Analyst).
    *   Visual role cards with model dropdowns.
    *   Health check model configuration.

### 6. Knowledge Graph Settings (✅ COMPLETE - Dec 4, 2025)
*   **SettingsGraph.svelte:** NEW settings tab for Knowledge Graph configuration (~680 lines).
*   **Features Delivered:**
    *   Edge type toggles (MOTIVATES, HINDERS, CHALLENGES, CAUSES, FORESHADOWS, CALLBACKS, KNOWS, CONTRADICTS).
    *   Extraction trigger configuration (on manuscript promote, before Foreman chat, periodic).
    *   Verification level selection (minimal, standard, thorough).
    *   Embedding provider selection (Ollama, OpenAI, none).
*   **Backend Integration:** Added graph defaults to `settings_service.py`.

---

## 🚧 Remaining UI Features & Improvements

### 1. Voice Settings (Medium Priority)
*   **Current State:** Placeholder or basic UI.
*   **Goal:** Create a dedicated "Voice" settings panel.
*   **Features Needed:**
    *   TTS Provider selection (OpenAI, ElevenLabs, Local).
    *   Voice preview/playback.
    *   Speed/Pitch controls.

### 2. Advanced Settings (Medium Priority)
*   **Current State:** Placeholder.
*   **Goal:** Implement advanced configuration options.
*   **Features Needed:**
    *   Local LLM endpoint configuration (Ollama URL).
    *   Context window size adjustments.
    *   Temperature/Top-P defaults.
    *   Data management (clear cache, export data).

### 3. Backend Integration (Technical Debt)
*   **Subscription Validation:** Move the `skoltech2026` check from client-side to a proper backend endpoint for security.
*   **Key Validation:** Implement real "Test" buttons for premium keys (currently we have the UI but need to ensure the backend `test_key` endpoint supports all providers).

### 4. Visual Polish (Low Priority)
*   **Animations:** Add subtle entry animations for lists and modals.
*   **Mobile Responsiveness:** Verify and improve layout on smaller screens (if applicable).
*   **Dark/Light Mode:** Ensure consistent theming if light mode is supported (currently optimized for Dark Mode).

---

## 📊 Progress Summary

| Category | Status | Components |
|----------|--------|------------|
| Key Management | ✅ Complete | 2 components |
| AI Models | ✅ Complete | 2 components |
| Squad Management | ✅ Complete | 3 components |
| Knowledge Graph Settings | ✅ Complete | 1 component |
| Voice Settings | 🔲 Pending | 0 components |
| Advanced Settings | 🔲 Pending | 0 components |

**Total Progress:** 8/10 settings components complete (80%)
