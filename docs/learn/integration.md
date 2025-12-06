---
layout: default
title: Systems Integration

---


# Systems Integration: GraphRAG, Voice Calibration, and Narrative Dashboard

**How the Intelligent Systems Work Together**

---

## Overview

Writers Factory has three interconnected intelligent systems that work together to provide writers with consistency, feedback, and quality:

| System | Purpose | When Active |
|--------|---------|-------------|
| **GraphRAG** | Narrative memory & consistency | All phases |
| **Voice Calibration** | Authorial voice discovery & enforcement | Phase 2B, then Director |
| **Narrative Dashboard** | Real-time tension & pacing feedback | Director Mode |

This document explains how these systems interact and reinforce each other.

---

## The Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SCENE GENERATION REQUEST                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Writer clicks "Generate Scene" in DIRECTOR Mode                       │
│                                                                         │
│                              ↓                                          │
│   ┌───────────────────────────────────────────────────────────────────┐ │
│   │                    CONTEXT ASSEMBLY                                │ │
│   ├───────────────────────────────────────────────────────────────────┤ │
│   │                                                                   │ │
│   │   GraphRAG                 Voice Bundle         Narrative Analysis │ │
│   │   ├── Ego-graph           ├── Gold Standard    ├── Tension: 65%  │ │
│   │   │   (2-hop neighbors)   ├── Anti-patterns    ├── Pacing: fast  │ │
│   │   ├── Active HINDERS      ├── Metaphor domains ├── Phase: rising │ │
│   │   ├── FORESHADOWS due     ├── Phase voice      └── Suggestion:   │ │
│   │   ├── Character facts     └── POV/tense            "Add obstacle"│ │
│   │   └── World rules                                                 │ │
│   │                                                                   │ │
│   └───────────────────────────────────────────────────────────────────┘ │
│                              ↓                                          │
│   ┌───────────────────────────────────────────────────────────────────┐ │
│   │                     LLM GENERATION                                 │ │
│   │                                                                   │ │
│   │   System Prompt includes:                                         │ │
│   │   - Story Bible artifacts                                         │ │
│   │   - GraphRAG context (what's relevant NOW)                        │ │
│   │   - Voice reference (how to write it)                             │ │
│   │   - Pacing guidance (what rhythm is needed)                       │ │
│   │                                                                   │ │
│   └───────────────────────────────────────────────────────────────────┘ │
│                              ↓                                          │
│   ┌───────────────────────────────────────────────────────────────────┐ │
│   │                    VERIFICATION                                    │ │
│   │                                                                   │ │
│   │   FAST checks:          MEDIUM checks:        SLOW checks:        │ │
│   │   - Dead characters?    - Flaw challenged?    - Voice authentic?  │ │
│   │   - Anti-patterns?      - Beat alignment?     - Full semantic     │ │
│   │   - POV consistent?     - Timeline ok?        - Graph consistency │ │
│   │                                                                   │ │
│   └───────────────────────────────────────────────────────────────────┘ │
│                              ↓                                          │
│   ┌───────────────────────────────────────────────────────────────────┐ │
│   │                    GRAPH UPDATE                                    │ │
│   │                                                                   │ │
│   │   Narrative Extractor analyzes the new scene:                     │ │
│   │   - New entities → add nodes                                      │ │
│   │   - New relationships → add edges                                 │ │
│   │   - Resolved foreshadows → mark as CALLBACKS                      │ │
│   │   - Tension recalculated                                          │ │
│   │                                                                   │ │
│   └───────────────────────────────────────────────────────────────────┘ │
│                              ↓                                          │
│                    Dashboard Updates                                    │
│                    Tension meter refreshes                              │
│                    Pacing chart updates                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## System 1: GraphRAG (The Living Brain)

### What It Does
- Stores entities (characters, locations, events) as **nodes**
- Stores relationships (MOTIVATES, HINDERS, FORESHADOWS) as **edges**
- Provides semantic search via embeddings
- Calculates narrative metrics (tension, pacing, communities)

### When It Activates
- **ARCHITECT Mode**: Builds initial graph from Story Bible
- **DIRECTOR Mode**: Updates graph after each scene
- **EDITOR Mode**: Validates consistency during polish

### Key Integration Points

**Voice Calibration uses GraphRAG to:**
- Provide character ego-graphs for test prompts
- Ensure tournament variants respect world rules

**Narrative Dashboard uses GraphRAG to:**
- Display tension score from edge analysis
- Show pacing ratios from edge categorization
- Visualize character communities

---

## System 2: Voice Calibration (The Artistic Fingerprint)

### What It Does
- Runs multi-model tournament to discover writer's voice
- Produces Voice Bundle (4 reference files)
- Provides scoring criteria for all future generation

### When It Activates
- **Phase 2B**: Tournament runs once per project
- **DIRECTOR Mode**: Bundle travels with every generation request

### Key Integration Points

**GraphRAG enhances Voice Calibration:**
- Test prompts can include character context from graph
- Winner selection considers graph-consistency in variants

**Narrative Dashboard interacts with Voice:**
- Pacing analysis suggests voice adjustments
- Phase detection triggers voice evolution
- High-tension scenes use climax voice profile

---

## System 3: Narrative Dashboard (The Real-Time Feedback)

### What It Does
- Displays tension score with visual indicator
- Shows pacing breakdown (action/setup/resolution)
- Provides recommendations for narrative balance

### When It Activates
- **DIRECTOR Mode**: Always visible
- **Graph Explorer**: Enhanced view with analysis overlay

### Key Integration Points

**GraphRAG powers the Dashboard:**
- Tension calculated from edge types (HINDERS, CHALLENGES, etc.)
- Pacing from edge categorization
- Communities from Louvain detection

**Voice Calibration responds to Dashboard:**
- Phase evolution triggered by pacing shifts
- Voice adjusts to tension levels

---

## Data Flow Example

**Scenario**: Writer generates a climactic confrontation scene.

### Step 1: Context Assembly

GraphRAG provides:
```json
{
  "ego_graph": {
    "protagonist": "Mickey",
    "neighbors": ["Sarah", "Casino", "The Woman"],
    "active_hinders": ["Guard blocks escape", "Woman knows his secret"],
    "unresolved_foreshadows": ["Gun from Act 1"]
  },
  "tension_score": 0.72,
  "pacing": "fast"
}
```

Voice Bundle provides:
```yaml
phase: climax
voice_characteristics:
  sentences: short, punchy
  metaphors: boxing (uppercut, jab, corner)
  pov: first_person_past
anti_patterns:
  - "It seemed"
  - "Perhaps"
  - excessive adverbs
```

### Step 2: Generation

LLM receives combined context:
```
You are writing a CLIMACTIC scene. The tension is HIGH (72%).
Current pacing is FAST - use short sentences, action verbs.

CONTEXT:
- Mickey is confronting The Woman at the Casino
- She knows his secret (unresolved HINDERS edge)
- The gun from Act 1 is present (FORESHADOW → must become CALLBACK)

VOICE:
- Write in first person past tense
- Use boxing metaphors (uppercut, jab)
- NO hedging language ("perhaps", "seemed")

Generate the scene.
```

### Step 3: Verification

FAST tier:
- No anti-patterns detected
- POV consistent (first person)
- Dead characters check: PASS

MEDIUM tier:
- Flaw challenged? Mickey's control issues tested: YES
- Beat alignment: CLIMAX scene matches tension: YES

### Step 4: Graph Update

Narrative Extractor processes new scene:
```json
{
  "new_edges": [
    {"type": "CALLBACKS", "from": "Gun", "to": "Confrontation"},
    {"type": "REVEALS", "from": "Woman", "to": "Mickey's Past"}
  ],
  "resolved_foreshadows": 1,
  "tension_delta": -0.15
}
```

### Step 5: Dashboard Update

- Tension meter: 72% → 57% (resolution begun)
- Pacing: fast → balanced
- Recommendation: "Good progress on resolution"

---

## UI Components by System

### GraphRAG UI
| Component | Purpose |
|-----------|---------|
| `GraphExplorer.svelte` | Full graph visualization |
| `GraphCanvas.svelte` | Force-directed physics rendering |
| `LiveGraph.svelte` | Simple widget view |
| `GraphNodeDetails.svelte` | Entity detail panel |

### Voice Calibration UI
| Component | Purpose |
|-----------|---------|
| `VoiceCalibration.svelte` | Master orchestrator (TO CREATE) |
| `VoiceTournamentLauncher.svelte` | Tournament configuration |
| `VoiceVariantGrid.svelte` | Variant matrix display |
| `VoiceComparisonView.svelte` | Side-by-side comparison |
| `VoiceBundleGenerator.svelte` | Bundle generation |

### Narrative Dashboard UI
| Component | Purpose |
|-----------|---------|
| `TensionIndicator.svelte` | Tension score display (TO CREATE) |
| `PacingDashboard.svelte` | Pacing ratios chart (TO CREATE) |
| `NarrativeDashboard.svelte` | Combined dashboard (TO CREATE) |

### Enhanced Graph Explorer UI (TO CREATE)
| Feature | Purpose |
|---------|---------|
| Community coloring | Visualize character clusters |
| Bridge highlighting | Show protagonist/connectors |
| Tension edge animation | Visualize narrative forces |
| Analysis overlay | Show metrics on graph |

---

## API Endpoints by System

### GraphRAG
```
GET  /graph/analysis/tension
GET  /graph/analysis/pacing
GET  /graph/analysis/communities
GET  /graph/analysis/bridges
GET  /graph/analysis/summary
POST /graph/extract-narrative
GET  /graph/ego-network/{entity}
POST /graph/semantic-search
```

### Voice Calibration
```
GET  /voice-calibration/agents
POST /voice-calibration/tournament/start
GET  /voice-calibration/tournament/{id}/status
GET  /voice-calibration/tournament/{id}/variants
POST /voice-calibration/tournament/{id}/select
POST /voice-calibration/generate-bundle/{project_id}
```

### Verification (bridges all systems)
```
POST /verification/run
POST /verification/run-all
GET  /verification/notifications
```

---

## Task Specs for Remaining Work

| Task | Document | Priority |
|------|----------|----------|
| Voice Calibration Master Component | [VOICE_CALIBRATION_UI.md](tasks/VOICE_CALIBRATION_UI.md) | High |
| Narrative Dashboard | [NARRATIVE_DASHBOARD_UI.md](tasks/NARRATIVE_DASHBOARD_UI.md) | High |
| Graph Explorer Enhancement | [GRAPH_EXPLORER_ENHANCEMENT.md](tasks/GRAPH_EXPLORER_ENHANCEMENT.md) | Critical (Demo) |

---

## Demo Flow (Course Presentation)

### Part 1: GraphRAG Foundation (5 min)
1. Show the knowledge graph with entities
2. Explain edge types (MOTIVATES, HINDERS, FORESHADOWS)
3. Switch to Analysis View → communities appear, tension animates

### Part 2: Voice Calibration (5 min)
1. Launch tournament with 4 agents
2. Show variant grid (20 samples)
3. Select winner, configure voice
4. Generate bundle

### Part 3: Integrated Generation (5 min)
1. Show context assembly (GraphRAG + Voice)
2. Generate a scene
3. Watch verification run
4. See graph update, tension change
5. Dashboard reflects new state

### The Hook
"These three systems - GraphRAG for memory, Voice for consistency, Dashboard for feedback - work together to ensure every generated scene honors your vision, maintains continuity, and moves the story forward. This is what we mean by engineering creativity."

---

## Related Documentation

- [GraphRAG Conceptual](graphrag.md) - Philosophy and design
- [GraphRAG Implementation](graphrag_implementation.md) - Technical details
- [Voice Calibration](voice_calibration.md) - Voice system docs
- [Writer's Journey](journey.md) - Full creative workflow

---

*Documentation created: December 5, 2025*
*Branch: nifty-antonelli*
