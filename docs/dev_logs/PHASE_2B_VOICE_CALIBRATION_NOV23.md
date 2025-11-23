# Phase 2B: Voice Calibration Implementation

**Date:** November 23, 2025
**Status:** Complete
**Architect Guidance:** Gemini (see GEMINI_ARCHITECT_REVIEW_NOV23.md)

---

## Overview

Phase 2B implements the Voice Calibration system - a tournament-based approach to discovering and locking the narrative voice before scene drafting begins. This bridges the gap between Story Bible completion (Architect Mode) and scene writing (Director Mode).

---

## Key Design Decisions

### 1. Dynamic Agent Selection
Before any tournament, the system scans available API keys and presents only configured agents to the writer. This accommodates writers with different API access levels.

**Implementation:** `VoiceCalibrationService.get_available_agents()` reads from `agents.yaml` and validates keys against `.env`.

### 2. Voice Reference Bundle
A critical design requirement: voice reference files must travel with EVERY agent call during scene writing. This ensures voice consistency across all scene generation.

**Bundle Contents:**
- `Voice-Gold-Standard.md` - The winning passage + analysis
- `Voice-Anti-Pattern-Sheet.md` - What to AVOID
- `Phase-Evolution-Guide.md` - How voice adapts through story arcs

### 3. 5-Variant Multiplier Strategy
Each agent generates 5 variants using different creative strategies:

| Strategy | Focus | Best For |
|----------|-------|----------|
| ACTION_EMPHASIS | Fast pacing, physical detail | Chase scenes, fights |
| CHARACTER_DEPTH | Internal landscape, psychology | Decision points, revelations |
| DIALOGUE_FOCUS | Conversation-centered conflict | Confrontations, negotiations |
| ATMOSPHERIC | Setting as character, sensory | Openings, building dread |
| BALANCED | Harmonious blend | Default approach |

### 4. Mode Transition Guards
- Cannot enter VOICE_CALIBRATION until Story Bible is complete
- Cannot enter DIRECTOR until Voice Bundle is generated
- Each transition is logged to KB for audit trail

---

## Files Created/Modified

### New Files

#### `backend/services/voice_calibration_service.py` (~600 lines)

Core service for voice calibration tournaments.

```python
class VoiceCalibrationService:
    """
    Manages voice calibration tournaments for narrative voice discovery.

    Key Methods:
    - get_available_agents(use_case) -> List[AgentInfo]
    - get_ready_agents(use_case) -> List[AgentInfo]
    - start_tournament(project_id, test_prompt, ...) -> TournamentResult
    - select_winner(tournament_id, agent_id, variant_index, ...) -> VoiceCalibrationDocument
    - generate_voice_bundle(project_id, output_dir) -> Dict[str, Path]
    """
```

**Data Classes:**
- `AgentInfo` - Agent metadata with availability status
- `VoiceVariant` - Single variant with strategy and content
- `TournamentResult` - Complete tournament results
- `VoiceCalibrationDocument` - Final voice specification

### Modified Files

#### `backend/agents/foreman.py`

**Added to ForemanMode enum:**
```python
class ForemanMode(Enum):
    ARCHITECT = "architect"           # Stage 1
    VOICE_CALIBRATION = "voice_calibration"  # Stage 1.5 (NEW)
    DIRECTOR = "director"             # Stage 2
    EDITOR = "editor"                 # Stage 3
```

**New System Prompts:**
- `VOICE_CALIBRATION_SYSTEM_PROMPT` - Guides writer through tournament process
- `DIRECTOR_SYSTEM_PROMPT` - Scene drafting guidance (placeholder expanded)

**New Action Handlers:**
- `_handle_advance_to_voice_calibration()` - Validates Story Bible completion
- `_handle_start_tournament()` - Initiates voice tournament
- `_handle_select_winner()` - Records winning voice
- `_handle_generate_bundle()` - Creates voice reference files
- `_handle_advance_to_director()` - Validates voice lock before transition

**New Guard Methods:**
- `can_advance_to_voice_calibration()` - Check eligibility
- `can_advance_to_director()` - Check eligibility

#### `backend/api.py`

**New Voice Calibration Endpoints:**
```
GET  /voice-calibration/agents              - List available agents
POST /voice-calibration/tournament/start    - Start tournament
GET  /voice-calibration/tournament/{id}/status   - Get status
GET  /voice-calibration/tournament/{id}/variants - Get all variants
POST /voice-calibration/tournament/{id}/select   - Select winner
POST /voice-calibration/generate-bundle/{project_id} - Generate bundle
GET  /voice-calibration/{project_id}        - Get stored calibration
```

**New Mode Transition Endpoints:**
```
GET  /foreman/mode                          - Get current mode + eligibility
POST /foreman/mode/voice-calibration        - Advance to voice calibration
POST /foreman/mode/director                 - Advance to director mode
```

---

## API Usage Examples

### 1. Check Available Agents
```bash
curl http://localhost:8000/voice-calibration/agents
```

Response:
```json
{
  "agents": [
    {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai", "enabled": true, "has_valid_key": true},
    {"id": "claude-sonnet-3-7", "name": "Claude 3.7 Sonnet", "provider": "anthropic", "enabled": true, "has_valid_key": true}
  ],
  "ready_count": 7
}
```

### 2. Start Tournament
```bash
curl -X POST http://localhost:8000/voice-calibration/tournament/start \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "Big Brain",
    "test_prompt": "Write a 500-word scene where Mickey enters a casino...",
    "test_context": "Chapter 3, Mickey is testing his new abilities",
    "agent_ids": ["gpt-4o", "claude-sonnet-3-7", "deepseek-v3"]
  }'
```

### 3. Select Winner
```bash
curl -X POST http://localhost:8000/voice-calibration/tournament/abc123/select \
  -H "Content-Type: application/json" \
  -d '{
    "winner_agent_id": "claude-sonnet-3-7",
    "winner_variant_index": 2,
    "voice_notes": "Love the cynical undertone and gambling metaphors"
  }'
```

### 4. Generate Voice Bundle
```bash
curl -X POST http://localhost:8000/voice-calibration/generate-bundle/Big%20Brain
```

### 5. Advance to Director Mode
```bash
curl -X POST http://localhost:8000/foreman/mode/director
```

---

## Testing Results

### Agent Detection (7 agents ready)
```
gpt-4o: GPT-4o (openai) - enabled=True, has_key=True
claude-sonnet-3-7: Claude 3.7 Sonnet (anthropic) - enabled=True, has_key=True
grok-2: Grok 2 (xai) - enabled=True, has_key=True
deepseek-v3: DeepSeek V3 (deepseek) - enabled=True, has_key=True
qwen-plus: Qwen Plus (qwen) - enabled=True, has_key=True
mistral-large: Mistral Large (mistral) - enabled=True, has_key=True
zhipu-glm4: Zhipu GLM-4 (zhipu) - enabled=True, has_key=True
```

### Mode Transition Logic
- Early transition blocked with clear error message
- Transition succeeds after Story Bible completion
- System prompt changes correctly per mode

---

## Integration with Director Mode

The Voice Calibration Document produced by this phase feeds directly into Director Mode's scene writing pipeline:

```
Story Bible (Architect)
    → Voice Calibration (Phase 2B)
        → Voice Bundle Files
            → Scene Writer (Director Mode)
                → Every agent call includes voice references
```

See `docs/specs/DIRECTOR_MODE_SPECIFICATION.md` Appendix C for how vanilla skills consume the Voice Calibration Document.

---

## Known Limitations / Future Work

1. **Tournament Persistence**: Currently tournaments are stored in-memory. For production, should persist to SQLite.

2. **Variant Comparison UI**: The backend generates variants, but the frontend comparison UI is not yet implemented.

3. **Anti-Pattern Extraction**: The `generate_voice_bundle()` method creates placeholder anti-patterns. Should analyze losing variants to extract actual anti-patterns.

4. **Phase Evolution**: Currently a placeholder. Should derive from beat sheet position and protagonist arc.

---

## Architecture Alignment

This implementation follows the Gemini Architect's recommendation:
- Phase 2B before Director Mode (voice must be locked first)
- Dynamic agent selection (scan keys before tournament)
- Voice Reference Bundle concept (files travel with agent calls)
- Mode transition guards (Story Bible → Voice Cal → Director)

---

*End of Dev Log*
