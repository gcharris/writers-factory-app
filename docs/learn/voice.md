---
layout: default
title: Voice Calibration

---


# Voice Calibration System

**Discovering Your Narrative Voice Through AI Competition**

---

## Overview

The Voice Calibration System is **Phase 2B of the Writer's Journey**. It uses a multi-model tournament to help writers discover and lock in their unique authorial voice before entering the drafting phase.

**Core Philosophy**: Rather than the writer trying to describe their voice abstractly, they see 15-25 writing samples from different AI models and simply pick the one that sounds most like them.

---

## Where It Fits

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE WRITER'S JOURNEY                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 0    Phase 1      Phase 2B        Phase 3      Phase 4   │
│  Research → ARCHITECT → VOICE MODE → DIRECTOR MODE → EDITOR    │
│  (NotebookLM) (Story Bible) (Tournament)  (Drafting)   (Polish) │
│                              ▲                                   │
│                              │                                   │
│                         YOU ARE HERE                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Prerequisites**: Story Bible complete (ARCHITECT Mode)
**Unlocks**: DIRECTOR Mode (scene drafting with voice consistency)

---

## The Tournament Process

### 1. Configuration (SETUP)

The writer provides:
- **Test Prompt**: A scene description for agents to write
- **Test Context**: Setting, mood, characters, stakes
- **Voice Description** (optional): Hints about desired style
- **Agent Selection**: Which AI models to compete (3+ required)

### 2. Generation (RUNNING)

Each selected agent generates 5 variants using different strategies:

| Strategy | Focus | Characteristics |
|----------|-------|-----------------|
| **ACTION_EMPHASIS** | Physical conflict | Fast pacing, external action, dialogue in motion |
| **CHARACTER_DEPTH** | Psychology | Slower pacing, internal landscape, emotional truth |
| **DIALOGUE_FOCUS** | Conversation | Subtext, conflict through words, relationship dynamics |
| **BRAINSTORMING** | Exploration | Multiple perspectives, experimental approaches |
| **BALANCED** | Hybrid | Mix of elements, standard structure |

**Example**: 4 agents × 5 strategies = 20 variants generated concurrently (~2-5 minutes)

### 3. Selection (REVIEW)

The writer reviews variants in a matrix view:
- Rows: AI Agents (Claude, GPT-4o, DeepSeek, etc.)
- Columns: Writing Strategies
- Features: Preview, word count, optional scores, multi-select for comparison

### 4. Configuration (SELECT WINNER)

After picking the winning variant:
- **POV**: First person / Third limited / Third omniscient
- **Tense**: Past / Present
- **Voice Type**: Narrator / Character voice / Hybrid
- **Metaphor Domains**: Boxing, weather, architecture, etc.
- **Anti-Patterns**: Phrases to avoid
- **Phase Evolution**: How voice changes through story acts

### 5. Bundle Generation (COMPLETE)

Four reference files are created:

| File | Purpose |
|------|---------|
| `Voice-Gold-Standard.md` | Reference sample + authentication tests |
| `Voice-Anti-Pattern-Sheet.md` | Patterns to avoid, AI tells |
| `Phase-Evolution-Guide.md` | How voice adapts by story phase |
| `voice_settings.yaml` | Scoring weights and thresholds |

---

## How It Integrates With GraphRAG

The Voice Calibration system produces artifacts that **enhance GraphRAG context injection**:

### Voice Bundle → Scene Generation

When DIRECTOR Mode generates a scene:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCENE GENERATION CONTEXT                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  From GraphRAG:                   From Voice Bundle:            │
│  ├── Character ego-graphs         ├── Gold Standard sample      │
│  ├── Active HINDERS edges         ├── Anti-patterns list        │
│  ├── Unresolved FORESHADOWS       ├── Metaphor domains          │
│  ├── Current tension score        ├── Phase-appropriate voice   │
│  └── Pacing recommendations       └── Scoring thresholds        │
│                                                                 │
│                         ↓                                       │
│              LLM generates scene with:                          │
│              - Narrative consistency (Graph)                    │
│              - Voice consistency (Bundle)                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Verification Integration

The **Tiered Verification System** (GraphRAG Phase 4) can check voice:

| Tier | Voice Checks |
|------|--------------|
| FAST | Anti-pattern detection (forbidden phrases) |
| MEDIUM | POV/tense consistency, metaphor usage |
| SLOW | Full voice authenticity scoring via LLM |

---

## How It Integrates With Narrative Dashboard

The **Tension Indicator** and **Pacing Dashboard** (from NARRATIVE_DASHBOARD_UI.md) provide feedback that influences voice:

### Phase Evolution Trigger

```javascript
// When tension changes significantly, voice should adapt
if (currentTension > 0.7 && previousTension < 0.5) {
  // High tension phase: use "climax" voice profile
  voiceProfile = phaseEvolution.climax;
}
```

### Pacing-Voice Alignment

| Pacing Type | Recommended Voice Characteristics |
|-------------|-----------------------------------|
| `fast` | Short sentences, action verbs, minimal introspection |
| `slow` | Longer sentences, more internal landscape, description |
| `balanced` | Mix of above |
| `concluding` | Resolution tone, emotional payoff, callbacks |

The Narrative Dashboard can suggest voice adjustments based on pacing analysis.

---

## Architecture

### Backend

```
backend/
├── services/
│   └── voice_calibration_service.py    # Tournament orchestration
├── models/
│   └── tournament.py                   # Data models
├── agents/
│   └── orchestrator.py                 # SceneTournament, DraftCritic
└── api.py                              # Endpoints
```

### Frontend

```
frontend/src/lib/
├── components/
│   ├── VoiceCalibration.svelte         # Master component (TO CREATE)
│   ├── VoiceTournamentLauncher.svelte  # Configuration UI
│   ├── VoiceVariantGrid.svelte         # Matrix display
│   ├── VoiceComparisonView.svelte      # Side-by-side compare
│   ├── VoiceBundleGenerator.svelte     # Bundle generation
│   ├── VoiceVariantSelector.svelte     # Winner selection
│   └── VoiceEvolutionChart.svelte      # Evolution tracking
├── api_client.ts                       # API methods
└── stores.js                           # State management
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/voice-calibration/agents` | GET | List available agents |
| `/voice-calibration/tournament/start` | POST | Start tournament |
| `/voice-calibration/tournament/{id}/status` | GET | Poll status |
| `/voice-calibration/tournament/{id}/variants` | GET | Get variants |
| `/voice-calibration/tournament/{id}/select` | POST | Select winner |
| `/voice-calibration/generate-bundle/{project_id}` | POST | Generate bundle |
| `/voice-calibration/{project_id}` | GET | Get existing calibration |

---

## The Voice Bundle Files

### Voice-Gold-Standard.md

```markdown
# Voice Reference: Gold Standard

## Winning Sample
[The full text of the winning variant]

## Authentication Tests

### Test 1: Authenticity Check
Question: Is the narrator EXPERIENCING the scene or EXPLAINING it?
Pass if: Reader feels immersed, not lectured

### Test 2: Purpose Check
Question: Does this scene serve its beat function?
Pass if: Clear narrative purpose beyond "this happened"

### Test 3: Fusion Check
Question: Are voice and knowledge seamlessly integrated?
Pass if: Story Bible details feel natural, not info-dumped
```

### Voice-Anti-Pattern-Sheet.md

```markdown
# Voice Anti-Patterns

## Forbidden Phrases
- "It's important to note that..."
- "Furthermore..." / "Moreover..."
- "In conclusion..."
- [Any AI-sounding formulations]

## Tone Violations
- Excessive hedging ("perhaps", "might", "seems")
- Over-explanation of character motivation
- Breaking POV for convenience

## Project-Specific Bans
[Writer-defined patterns to avoid]
```

### Phase-Evolution-Guide.md

```markdown
# Voice Phase Evolution

## Act 1: Setup
- Longer sentences, world-building rhythm
- More descriptive, establishing tone
- Character voice emerging

## Act 2A: Rising Action
- Increasing tension in prose
- Shorter paragraphs during conflict
- Internal thoughts more fragmented

## Act 2B: Midpoint & Beyond
- Clipped, urgent prose in crisis
- Callbacks to earlier language
- Voice reflects character growth

## Act 3: Resolution
- Return to opening rhythm (transformed)
- Emotional resonance prioritized
- Earned payoff language
```

---

## Implementation Status

| Component | Status |
|-----------|--------|
| Backend service | Complete |
| API endpoints | Complete |
| VoiceTournamentLauncher | Complete |
| VoiceVariantGrid | Complete |
| VoiceComparisonView | Complete |
| VoiceBundleGenerator | Complete |
| VoiceVariantSelector | Complete |
| api_client.ts methods | Complete |
| stores.js state | Complete |
| **VoiceCalibration.svelte** | **TO CREATE** |
| ChatSidebar integration | TO DO |

---

## Related Documentation

- [Writer's Journey](journey.md) - Full creative workflow
- [GraphRAG Conceptual](graphrag.md) - Knowledge graph philosophy
- [GraphRAG Implementation](graphrag_implementation.md) - Technical details
- [Task: Voice Calibration UI](tasks/VOICE_CALIBRATION_UI.md) - Implementation spec
- [Task: Narrative Dashboard](tasks/NARRATIVE_DASHBOARD_UI.md) - Tension/pacing UI

---

*Documentation created: December 5, 2025*
*Status: Backend complete, Frontend needs master component*
