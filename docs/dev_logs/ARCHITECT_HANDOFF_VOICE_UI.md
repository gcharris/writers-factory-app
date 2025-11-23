# Architect's Directive: Voice Calibration UI Implementation

**To:** Coder Agent
**From:** Gemini Architect
**Date:** November 23, 2025
**Subject:** Phase 2B Frontend Implementation (Voice Calibration)

## Context
The backend for Phase 2B (Voice Calibration) is complete. We now need to implement the frontend user interface to allow writers to run the Voice Calibration Tournament.

## Objectives
1.  Update `api_client.ts` to support the new Voice Calibration endpoints.
2.  Create `VoiceCalibration.svelte` to manage the tournament workflow.
3.  Integrate this new component into `ChatSidebar.svelte`.

## Specification

### 1. API Client Updates (`frontend/src/lib/api_client.ts`)
Add the following methods to the `ApiClient` class. Ensure they map correctly to the endpoints defined in `backend/api.py`.

```typescript
// Voice Calibration
async getVoiceAgents(useCase = "tournament") { ... } // GET /voice-calibration/agents
async startVoiceTournament(projectId, testPrompt, testContext, agentIds, variantsPerAgent = 5) { ... } // POST /voice-calibration/tournament/start
async getTournamentStatus(tournamentId) { ... } // GET /voice-calibration/tournament/{id}/status
async selectTournamentWinner(tournamentId, winnerAgentId, winnerVariantIndex, voiceConfig) { ... } // POST /voice-calibration/tournament/{id}/select
async generateVoiceBundle(projectId) { ... } // POST /voice-calibration/generate-bundle/{id}
async advanceToVoiceCalibration() { ... } // POST /foreman/mode/voice-calibration
async advanceToDirector() { ... } // POST /foreman/mode/director
```

### 2. New Component: `VoiceCalibration.svelte`
**Path:** `frontend/src/lib/components/VoiceCalibration.svelte`

**State Machine:**
The component should handle 4 distinct states:
1.  **SETUP**:
    - Fetch available agents (`getVoiceAgents`).
    - Display a form:
        - `Test Prompt` (Textarea, required): The scene/passage to write.
        - `Context` (Textarea, required): Setting, characters, mood.
        - `Agent Selection` (Checkbox list): Allow selecting multiple agents.
    - Action: "Start Tournament" button.

2.  **RUNNING**:
    - Display a loading state (spinner/progress bar).
    - Poll `getTournamentStatus` every 2 seconds.
    - Show "Generating variants..." message.

3.  **SELECTION**:
    - Display the results (Variants).
    - **Layout**: Group variants by Agent. Use an accordion or tabs to save space.
    - **Variant Card**: Show the text content and the strategy used (e.g., "Action Emphasis").
    - **Action**: "Select as Winner" button on *each* variant.
    - **Refinement Form** (appears after selection or alongside):
        - `POV` (Dropdown: First, Third Limited, Third Omniscient)
        - `Tense` (Dropdown: Past, Present)
        - `Voice Type` (Dropdown: Character, Author)
    - Action: "Confirm & Lock Voice" button.

4.  **COMPLETE**:
    - Show success message: "Voice Calibration Complete".
    - Action: "Proceed to Director Mode" button (calls `advanceToDirector`).

### 3. Integration: `ChatSidebar.svelte`
**Path:** `frontend/src/lib/components/ChatSidebar.svelte`

- **Logic**: Check `$foremanMode`.
- **Condition**:
    - IF `$foremanMode === 'voice_calibration'`, render `<VoiceCalibration />` *instead of* the standard chat input area (or overlay it).
    - IF `$foremanMode === 'architect'` AND `$foremanWorkOrder.is_complete`, show a button: "Advance to Voice Calibration" (calls `advanceToVoiceCalibration`).

## Design Guidelines
- **Aesthetics**: Use the existing "Writers Factory" style (Tailwind/CSS).
- **Feedback**: Use toast notifications or clear error messages for failed API calls.
- **Resilience**: Handle network errors gracefully during polling.

## Verification
- Start the app.
- Complete a dummy Story Bible (or mock the state).
- Click "Advance to Voice Calibration".
- Run a tournament with 2 agents.
- Select a winner.
- Verify transition to Director Mode.
