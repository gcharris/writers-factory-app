# Task: Mode Transition UI (Soft Guardrails)

**Priority:** Medium (UX Polish)
**Estimated Effort:** 4-6 hours
**Dependencies:** None (Foreman backend already has mode support)

---

## Problem

The top-left mode buttons (ARCHITECT, VOICE, DIRECTOR, EDITOR) are currently **disabled/display-only**. Writers can see their current mode but cannot interact with the buttons.

**Current state:**
```svelte
<button
  class="mode-tab {$foremanMode === mode ? 'active' : ''}"
  disabled={mode !== $foremanMode}  <!-- Always disabled except current -->
>
```

**Desired state:** Writers can click any mode, and the Foreman responds intelligently based on context.

---

## Design Philosophy: Soft Guardrails

**MVP (Course):** Structured workflow - Foreman leads
**Commercial (Real Writers):** Writers are opinionated - Foreman advises

The Foreman should be an **advisor, not a gatekeeper**:
- Never block mode transitions
- Always acknowledge the writer's intent
- Provide context-aware guidance
- Offer alternatives when prerequisites are missing

---

## Implementation: Hybrid Approach

### Why Hybrid?

| Approach | Pros | Cons |
|----------|------|------|
| Pure LLM | Dynamic, varied responses | Unpredictable, may miss context |
| Pure Canned | Consistent, fast | Robotic, no variation |
| **Hybrid** | Consistent logic + natural language | Best of both |

**Hybrid = Backend logic determines WHAT to say, LLM determines HOW to say it**

---

## Architecture

### 1. Frontend: Enable Mode Buttons

**File:** `frontend/src/lib/components/MainLayout.svelte`

```svelte
<!-- BEFORE -->
<button
  class="mode-tab {$foremanMode === mode ? 'active' : ''}"
  disabled={mode !== $foremanMode}
>

<!-- AFTER -->
<button
  class="mode-tab {$foremanMode === mode ? 'active' : ''}"
  class:available={canTransitionTo(mode)}
  on:click={() => requestModeTransition(mode)}
>
```

```typescript
async function requestModeTransition(targetMode: string) {
  if (targetMode === $foremanMode) return; // Already in this mode

  try {
    const response = await fetch(`${BASE_URL}/foreman/request-mode-change`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_mode: targetMode })
    });

    const result = await response.json();

    // Foreman will respond in chat - mode may or may not change
    // The response includes a chat message that appears in ForemanPanel

  } catch (e) {
    console.error('Mode transition request failed:', e);
  }
}

// Visual indicator for "recommended next" vs "available but not recommended"
function canTransitionTo(mode: string): boolean {
  // All modes always clickable, but styling differs
  return true;
}
```

### 2. Backend: New Endpoint

**File:** `backend/api.py`

```python
class ModeTransitionRequest(BaseModel):
    target_mode: str

class ModeTransitionResponse(BaseModel):
    allowed: bool
    new_mode: str | None
    foreman_message: str
    missing_prerequisites: list[str]

@app.post("/foreman/request-mode-change", response_model=ModeTransitionResponse)
async def request_mode_change(request: ModeTransitionRequest):
    """
    Handle writer's request to change Foreman mode.

    Always responds conversationally - never just blocks.
    Mode may or may not actually change based on context.
    """
    from backend.agents.foreman import foreman

    target = request.target_mode.upper()
    current = foreman.mode

    # Get prerequisite status
    prereqs = await get_mode_prerequisites(target)
    missing = [p for p in prereqs if not p["completed"]]

    # Determine transition type
    transition_type = classify_transition(current, target, missing)

    # Generate contextual response
    foreman_message = await generate_transition_response(
        current_mode=current,
        target_mode=target,
        transition_type=transition_type,
        missing_prerequisites=missing
    )

    # Decide if mode actually changes
    if transition_type in ["forward_ready", "backward_revision", "lateral"]:
        foreman.mode = target
        allowed = True
        new_mode = target
    else:
        # Mode doesn't change, but writer gets helpful guidance
        allowed = False
        new_mode = None

    return ModeTransitionResponse(
        allowed=allowed,
        new_mode=new_mode,
        foreman_message=foreman_message,
        missing_prerequisites=[p["name"] for p in missing]
    )
```

### 3. Backend: Transition Logic

**File:** `backend/services/mode_transition_service.py` (NEW)

```python
"""
Mode Transition Service - Soft guardrails for workflow navigation

Transition Types:
- forward_ready: Moving forward with prerequisites met
- forward_skip: Moving forward without prerequisites (allowed but noted)
- backward_revision: Going back to revise earlier work
- lateral: Staying in same phase but different focus
- same: Already in target mode
"""

from typing import Literal
from dataclasses import dataclass

TransitionType = Literal[
    "forward_ready",
    "forward_skip",
    "backward_revision",
    "lateral",
    "same"
]

# Mode ordering for forward/backward detection
MODE_ORDER = ["ARCHITECT", "VOICE_CALIBRATION", "DIRECTOR", "EDITOR"]

# Prerequisites for each mode
MODE_PREREQUISITES = {
    "ARCHITECT": [],  # Always available
    "VOICE_CALIBRATION": [
        {"name": "story_bible_started", "check": "story_bible_has_protagonist"},
        {"name": "beat_sheet_exists", "check": "beat_sheet_has_beats"},
    ],
    "DIRECTOR": [
        {"name": "voice_calibrated", "check": "voice_bundle_exists"},
        {"name": "story_bible_complete", "check": "story_bible_complete"},
    ],
    "EDITOR": [
        {"name": "has_draft_content", "check": "manuscript_has_scenes"},
    ],
}

async def get_mode_prerequisites(target_mode: str) -> list[dict]:
    """Get prerequisites with completion status."""
    prereqs = MODE_PREREQUISITES.get(target_mode, [])
    results = []

    for prereq in prereqs:
        completed = await check_prerequisite(prereq["check"])
        results.append({
            "name": prereq["name"],
            "completed": completed
        })

    return results

async def check_prerequisite(check_name: str) -> bool:
    """Check if a specific prerequisite is met."""
    # Import services as needed
    from backend.services.story_bible_service import story_bible_service
    from backend.services.voice_calibration_service import voice_calibration_service

    checks = {
        "story_bible_has_protagonist": lambda: story_bible_service.has_protagonist(),
        "beat_sheet_has_beats": lambda: story_bible_service.beat_count() > 0,
        "voice_bundle_exists": lambda: voice_calibration_service.has_voice_bundle(),
        "story_bible_complete": lambda: story_bible_service.is_complete(),
        "manuscript_has_scenes": lambda: True,  # TODO: Check manuscript service
    }

    checker = checks.get(check_name)
    if checker:
        try:
            return await checker() if asyncio.iscoroutinefunction(checker) else checker()
        except:
            return False
    return False

def classify_transition(current: str, target: str, missing: list) -> TransitionType:
    """Classify the type of mode transition."""
    if current == target:
        return "same"

    current_idx = MODE_ORDER.index(current) if current in MODE_ORDER else 0
    target_idx = MODE_ORDER.index(target) if target in MODE_ORDER else 0

    if target_idx > current_idx:
        # Moving forward
        if not missing:
            return "forward_ready"
        else:
            return "forward_skip"
    else:
        # Moving backward
        return "backward_revision"
```

### 4. Backend: Response Generation (Hybrid)

**File:** `backend/services/mode_transition_service.py` (continued)

```python
# Canned context templates - the WHAT to say
TRANSITION_TEMPLATES = {
    "same": {
        "context": "Writer clicked on mode they're already in.",
        "guidance": "Acknowledge and offer to continue or explore options.",
        "tone": "friendly, brief"
    },
    "forward_ready": {
        "context": "Writer is ready to advance. Prerequisites met.",
        "guidance": "Celebrate progress, briefly explain what this mode offers.",
        "tone": "encouraging, forward-looking"
    },
    "forward_skip": {
        "context": "Writer wants to skip ahead. Missing: {missing}",
        "guidance": "Acknowledge intent, explain what's missing without blocking. Offer two paths: quick setup OR proceed anyway.",
        "tone": "supportive, practical"
    },
    "backward_revision": {
        "context": "Writer wants to revisit earlier work from {current} back to {target}.",
        "guidance": "Validate this is common and smart. Ask what aspect needs revision.",
        "tone": "understanding, curious"
    },
}

async def generate_transition_response(
    current_mode: str,
    target_mode: str,
    transition_type: TransitionType,
    missing_prerequisites: list
) -> str:
    """Generate a contextual, conversational response using hybrid approach."""

    template = TRANSITION_TEMPLATES[transition_type]

    # Build the prompt for the LLM
    system_prompt = f"""You are the Foreman, a creative writing partner.

The writer just clicked the {target_mode} mode button.
Current mode: {current_mode}
Transition type: {transition_type}

Context: {template["context"].format(
    missing=", ".join([p["name"] for p in missing_prerequisites]) if missing_prerequisites else "none",
    current=current_mode,
    target=target_mode
)}

Your guidance: {template["guidance"]}
Tone: {template["tone"]}

Respond in 2-3 sentences max. Be conversational, not robotic.
Do NOT use phrases like "I understand" or "Great choice".
"""

    # Use local model for quick response
    from backend.services.llm_service import llm_service

    response = await llm_service.generate(
        provider="ollama",
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"I want to switch to {target_mode} mode."}
        ],
        temperature=0.7,
        max_tokens=150
    )

    return response.content
```

---

## Mode-Specific Behaviors

### ARCHITECT Mode
- **Forward from START:** Welcome, explain Story Bible workflow
- **Backward from any:** "Revisiting foundations - what needs adjustment?"

### VOICE_CALIBRATION Mode
- **Forward ready:** "Time to find your voice. Let's run a tournament."
- **Forward skip (no story bible):** "I can run voice samples, but they'll be generic without your characters. Want to do a quick protagonist sketch first?"
- **Backward from DIRECTOR:** "Recalibrating mid-draft? Smart - your scenes will help me understand your actual voice better."

### DIRECTOR Mode
- **Forward ready:** "Story Bible complete, voice calibrated. Let's draft your first scene."
- **Forward skip (no voice):** "Jumping to drafting! I'll use general best practices since I don't have your voice profile. Want quick voice samples first, or dive in?"
- **Backward from EDITOR:** "Back to drafting - which scene needs rework?"

### EDITOR Mode
- **Forward ready:** "Polish time. Let's review your draft for consistency and flow."
- **Forward skip (no draft):** "Nothing to edit yet! Head to Director mode to draft some scenes first."

---

## UI Enhancements

### Visual States for Mode Buttons

```css
/* Current mode - bright, active */
.mode-tab.active {
  background: var(--mode-color);
  color: white;
  border-color: var(--mode-color);
}

/* Available and recommended - subtle glow */
.mode-tab.recommended {
  border-color: var(--mode-color);
  opacity: 0.8;
}

/* Available but prerequisites missing - dimmed */
.mode-tab.available {
  opacity: 0.5;
  border-color: var(--border);
}

/* Hover state - all buttons respond */
.mode-tab:hover:not(.active) {
  opacity: 1;
  transform: translateY(-1px);
}
```

### Tooltip Enhancement

Show prerequisite status on hover:

```svelte
<button
  class="mode-tab"
  title={getModeTooltip(mode)}
>

function getModeTooltip(mode: string): string {
  if (mode === $foremanMode) return `Currently in ${mode} mode`;

  const prereqs = $modePrerequisites[mode];
  if (!prereqs?.length) return `Switch to ${mode} mode`;

  const missing = prereqs.filter(p => !p.completed);
  if (!missing.length) return `Ready for ${mode} mode`;

  return `${mode} mode\nMissing: ${missing.map(p => p.name).join(", ")}`;
}
```

---

## Status Bar Cleanup (Bundled)

While implementing mode transitions, also clean up the status bar:

1. **Remove "Backend Online"** - unnecessary for desktop app
2. **Remove duplicate mode indicator** - top bar is sufficient
3. **Remove "Budget" badge** - Squad system obsolete
4. **Add UsageIndicator** - wire up the existing component

```svelte
<!-- StatusBar.svelte - simplified -->
<footer class="status-bar">
  <div class="status-left">
    <!-- Project name or file path -->
    <span class="project-name">{$foremanProjectTitle || "No Project"}</span>
  </div>

  <div class="status-right">
    <!-- Usage tracking -->
    <UsageIndicator />
  </div>
</footer>
```

---

## Testing Checklist

### Mode Transitions
- [ ] Click ARCHITECT from any mode → appropriate response
- [ ] Click VOICE without story bible → offers quick setup
- [ ] Click DIRECTOR without voice → allows but notes limitation
- [ ] Click EDITOR without draft → redirects to DIRECTOR
- [ ] Click current mode → brief acknowledgment
- [ ] Backward transitions → asks what needs revision

### Visual States
- [ ] Current mode clearly highlighted
- [ ] Other modes show appropriate opacity
- [ ] Hover effects work on all buttons
- [ ] Tooltips show prerequisite status

### Status Bar
- [ ] "Backend Online" removed
- [ ] Bottom mode indicator removed
- [ ] "Budget" badge removed
- [ ] UsageIndicator visible and functional

---

## Files to Modify

| File | Changes |
|------|---------|
| `frontend/src/lib/components/MainLayout.svelte` | Enable mode buttons, add click handlers |
| `frontend/src/lib/components/StatusBar.svelte` | Simplify, add UsageIndicator |
| `backend/api.py` | Add `/foreman/request-mode-change` endpoint |
| `backend/services/mode_transition_service.py` | NEW - transition logic and response generation |

---

## Success Criteria

1. Writers can click any mode button
2. Foreman responds conversationally (not with error modals)
3. Mode changes when appropriate, guidance provided when not
4. UI clearly shows current mode and available transitions
5. Status bar simplified and shows usage tracking
6. `npm run check` passes

---

*Created: Dec 5, 2025*
*Philosophy: Advisor, not gatekeeper*
