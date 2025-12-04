# Squad Management Enhancement Task

> Add per-role model configuration UI beyond tournament models.

## Status: Ready for Implementation
**Priority:** High
**Estimated Effort:** 8-10 hours
**Target Milestone:** Dec 8, 2025

---

## Problem Statement

The current `SettingsSquad.svelte` only exposes **tournament model selection**. Writers cannot:
1. See or change which model handles Foreman strategic tasks (complex reasoning)
2. See or change which model handles Foreman coordination (quick routing)
3. Configure individual health check models (7 different checks)

The backend supports all these configurations via `squad_service.py` and `settings_service.py`, but the UI doesn't expose them.

---

## Current State

### What Exists (SettingsSquad.svelte - 1043 lines)
- Active squad display with name, icon, description
- "Change Squad" button → Opens SquadWizard modal
- Tournament model picker (checkbox grid with cost estimation)
- Save/Reset custom tournament selection
- Info panel explaining squads

### What's Missing
1. **Foreman Role Configuration** - No UI to assign models to strategic vs coordinator tasks
2. **Health Check Model Configuration** - No UI for the 7 health check model assignments
3. **Per-Role Cost Visibility** - User can't see cost breakdown by role

---

## Solution: Role-Based Model Configuration

### New Section: "Model Assignments"

Add a new section to SettingsSquad.svelte between "Active Squad" and "Tournament Models":

```
┌─────────────────────────────────────────────────────────────────────┐
│ MODEL ASSIGNMENTS                                    [Use Defaults] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ THE FOREMAN                                                  │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                              │   │
│  │  Strategic Thinking          ▼ DeepSeek V3                   │   │
│  │  Complex reasoning: beat analysis, theme guidance,           │   │
│  │  structural planning, conflict resolution                    │   │
│  │                                                              │   │
│  │  Coordination               ▼ Mistral 7B (Local)             │   │
│  │  Quick routing: task classification, simple responses        │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ HEALTH CHECKS                           [▼ Show Individual]  │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                              │   │
│  │  Default Model              ▼ Qwen Plus                      │   │
│  │  Used for: Pacing, Beat Progress, Symbolic Layering          │   │
│  │                                                              │   │
│  │  Timeline Consistency       ▼ Claude Sonnet (override)       │   │
│  │  Theme Resonance            ▼ GPT-4o (override)              │   │
│  │  Flaw Challenges            ▼ DeepSeek V3 (override)         │   │
│  │  Cast Function              ▼ Qwen Plus (default)            │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Estimated Monthly Cost: $2.50 (strategic) + $0 (local) = $2.50    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

### Task 1: Create RoleModelSelector Component

**File:** `frontend/src/lib/components/Settings/RoleModelSelector.svelte`

**Props:**
```typescript
interface RoleModelSelectorProps {
  role: string;                    // "foreman_strategic" | "foreman_coordinator" | "health_default" etc.
  label: string;                   // "Strategic Thinking"
  description: string;             // "Complex reasoning: beat analysis..."
  currentModel: string;            // "deepseek-chat"
  availableModels: TournamentModel[];
  onSelect: (modelId: string) => void;
  showCost?: boolean;
}
```

**Features:**
- Dropdown with model names (not IDs)
- Shows tier badge (Budget/Premium/Free)
- Shows availability status (green check / red lock if missing API key)
- Hover shows cost per 1M tokens
- Disabled options for unavailable models

**Size:** ~150-200 lines

### Task 2: Create HealthCheckModelConfig Component

**File:** `frontend/src/lib/components/Settings/HealthCheckModelConfig.svelte`

**Purpose:** Collapsible section for health check model overrides.

**State:**
- Default model (applies to all)
- Per-check overrides (only show if different from default)
- Collapsed by default to reduce visual complexity

**Health Check Types:**
1. `pacing` - Pacing Plateau Detection
2. `beat_progress` - Beat Progress Validation
3. `timeline` - Timeline Consistency (often overridden to Claude)
4. `flaw_challenges` - Fatal Flaw Challenge Monitoring
5. `cast_function` - Cast Function Verification
6. `symbolic` - Symbolic Layering
7. `theme` - Theme Resonance (often overridden to GPT-4o)

**Size:** ~250-300 lines

### Task 3: Extend SettingsSquad.svelte

**Modifications:**

1. Add new section "Model Assignments" after "Active Squad"
2. Import and use RoleModelSelector for Foreman roles
3. Import and use HealthCheckModelConfig for health checks
4. Add "Use Squad Defaults" button to reset all overrides
5. Add cost estimation for role assignments (not just tournament)

**New API Calls:**
```typescript
// Get current role assignments
GET /settings/category/foreman → { coordinator_model, task_models: {...} }
GET /settings/category/health_checks → { models: { default_model, timeline, theme, ... } }

// Update role assignments
PUT /settings/category/foreman → { coordinator_model, task_models: {...} }
PUT /settings/category/health_checks → { models: {...} }
```

**Added Lines:** ~200-250 lines

### Task 4: Backend - Add Role Assignment Endpoints (if missing)

**Check if these exist:**
```
GET /settings/category/foreman
PUT /settings/category/foreman
GET /settings/category/health_checks
PUT /settings/category/health_checks
```

If missing, add to `api.py`:
```python
@app.get("/squad/role-assignments")
async def get_role_assignments():
    """Get current model assignments for all roles."""
    return {
        "foreman": {
            "strategic": settings.get("foreman.task_models.strategic"),
            "coordinator": settings.get("foreman.coordinator_model")
        },
        "health_checks": {
            "default": settings.get("health_checks.models.default_model"),
            "timeline": settings.get("health_checks.models.timeline"),
            # ... etc
        }
    }

@app.put("/squad/role-assignments")
async def update_role_assignments(assignments: RoleAssignments):
    """Update model assignments for roles."""
    # Validate models are available
    # Update settings
    pass
```

**Added Lines:** ~50-80 lines if needed

---

## API Reference

### Existing Endpoints to Use

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/squad/active` | GET | Get current squad ID and setup status |
| `/squad/available` | GET | Get all squad presets with availability |
| `/squad/tournament-models` | GET | Get tournament models with selection status |
| `/settings/category/{category}` | GET/PUT | Read/write settings by category |

### Backend Data Structures

**Foreman Task Types** (from foreman.py):
- `coordinator` - Quick task classification
- `health_check_review` - Review health report findings
- `voice_calibration_guidance` - Guide voice discovery
- `beat_structure_advice` - Structural guidance
- `conflict_resolution` - Story conflict resolution
- `scaffold_enrichment_decisions` - Smart scaffold enrichment
- `theme_analysis` - Theme exploration
- `structural_planning` - Plot structure planning

**Health Check Types** (from graph_health_service.py):
- `pacing` / `beat_progress` / `timeline` / `flaw_challenges` / `cast_function` / `symbolic` / `theme`

---

## UI/UX Guidelines

### Visual Hierarchy
1. **Active Squad** - Most prominent (current design is good)
2. **Model Assignments** - Collapsed "Advanced" section by default
3. **Tournament Models** - Full grid (current design is good)

### Interaction Pattern
- Squad wizard handles initial setup → sets sensible defaults
- Model Assignments is for power users who want to tweak
- Most users should never need to touch it

### Color Coding
- Use existing tier colors: Budget (green), Balanced (cyan), Premium (purple)
- Use existing availability indicators: green check, red lock

---

## Testing Checklist

- [ ] RoleModelSelector shows correct available models
- [ ] Unavailable models are disabled with "Missing API key" tooltip
- [ ] Changing strategic model updates settings correctly
- [ ] Changing coordinator model updates settings correctly
- [ ] Health check overrides persist after page reload
- [ ] "Use Squad Defaults" resets all role assignments
- [ ] Cost estimation updates when roles change
- [ ] Works with all 3 squad types (Local, Hybrid, Pro)

---

## Files to Create/Modify

| File | Action | Lines |
|------|--------|-------|
| `frontend/src/lib/components/Settings/RoleModelSelector.svelte` | CREATE | ~180 |
| `frontend/src/lib/components/Settings/HealthCheckModelConfig.svelte` | CREATE | ~280 |
| `frontend/src/lib/components/Settings/SettingsSquad.svelte` | MODIFY | +220 |
| `backend/api.py` | MODIFY (if needed) | +60 |
| **Total** | | ~740 lines |

---

## Success Criteria

1. User can see which models handle Foreman strategic vs coordinator tasks
2. User can override individual health check models
3. Changes persist and take effect immediately
4. "Use Squad Defaults" restores all assignments to squad preset values
5. No regression in existing tournament model selection

---

## References

- [SettingsSquad.svelte](frontend/src/lib/components/Settings/SettingsSquad.svelte) - Current implementation
- [squad_service.py](backend/services/squad_service.py) - Backend squad logic
- [foreman.py](backend/agents/foreman.py) - Task model routing
- [graph_health_service.py](backend/services/graph_health_service.py) - Health check models
- [SETTINGS_SQUAD_REDESIGN.md](docs/tasks/SETTINGS_SQUAD_REDESIGN.md) - Original squad design doc

---

*Created: December 4, 2025*
*Status: Ready for Implementation*
