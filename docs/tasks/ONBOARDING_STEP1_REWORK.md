# Task: Rework Onboarding Step 1 - Simplified Local AI Setup

## Overview

Step 1 of the OnboardingWizard currently has overly complex model recommendation logic that suggests large models (deepseek-r1:7b) to users with 16GB+ RAM. This is unnecessary and wastes users' time/bandwidth.

**Key Insight**: The local Ollama model is ONLY used for The Foreman's casual chat and onboarding assistance. All heavy lifting (scene generation, voice tournaments, analysis) uses cloud APIs. Writers don't need powerful local models.

## Current State

**File**: `frontend/src/lib/components/Onboarding/Step1LocalAI.svelte`

Current flow:
1. Scan hardware (RAM, CPU, GPU, Ollama status)
2. Recommend model based on RAM tier (low/medium/high)
3. Show all 3 model options with "Recommended" badge on one
4. User can install any model
5. Continue when any model is installed

**Problems**:
- Recommends 4.5GB deepseek-r1:7b to users with 16GB RAM (unnecessary)
- Shows 3 model options causing decision paralysis
- Downloads take too long for larger models
- Tiered recommendations serve no practical purpose

## Target State

Simplified flow:
1. Check if Ollama is installed
   - If NO: Show "Install Ollama" with link to ollama.ai and "Rescan" button
   - If YES: Proceed to model check
2. Check if `llama3.2:3b` is installed
   - If YES: Show "Ready!" status and enable Continue
   - If NO: Show single Install button for llama3.2:3b with progress bar
3. Continue when llama3.2:3b is installed

**Key Changes**:
- Remove tiered model recommendations entirely
- Only offer ONE model: `llama3.2:3b` (2GB, fast, sufficient)
- Simplify UI to binary states: "Install Ollama" → "Install Model" → "Ready"
- Remove hardware grid display (unnecessary complexity)
- Keep Ollama version display for troubleshooting

## Implementation Details

### 1. Simplify State

Replace:
```typescript
const modelRecommendations = {
  low: { id: 'llama3.2:3b', ... },
  medium: { id: 'mistral:7b', ... },
  high: { id: 'deepseek-r1:7b', ... }
};
```

With:
```typescript
const requiredModel = {
  id: 'llama3.2:3b',
  name: 'Llama 3.2',
  description: 'Fast, lightweight AI for your writing assistant',
  size: '2GB'
};
```

### 2. Simplify Ready Check

Replace:
```typescript
$: isReady = hardwareInfo?.ollama_installed && hardwareInfo.ollama_models.length > 0;
```

With:
```typescript
$: hasRequiredModel = hardwareInfo?.ollama_models?.some(m =>
  m.includes('llama3.2') || m.includes('llama3.2:3b')
);
$: isReady = hardwareInfo?.ollama_installed && hasRequiredModel;
```

### 3. Remove getRecommendedModel Function

Delete entirely - no longer needed.

### 4. Simplify UI Structure

New structure:
```
┌─────────────────────────────────────────┐
│  Local AI Setup                         │
│  Your writing assistant needs a local   │
│  AI model to work offline.              │
├─────────────────────────────────────────┤
│                                         │
│  [If Ollama not installed]              │
│  ┌─────────────────────────────────┐    │
│  │ ⚠️ Ollama Required               │    │
│  │ Ollama runs AI models locally.  │    │
│  │ [Install Ollama ↗]  [Rescan]    │    │
│  └─────────────────────────────────┘    │
│                                         │
│  [If Ollama installed, model missing]   │
│  ┌─────────────────────────────────┐    │
│  │ ✓ Ollama v0.12.10               │    │
│  │                                 │    │
│  │ 📦 Llama 3.2 (2GB)              │    │
│  │ Fast, lightweight AI            │    │
│  │ [Install]  or  [===    ] 45%    │    │
│  └─────────────────────────────────┘    │
│                                         │
│  [If ready]                             │
│  ┌─────────────────────────────────┐    │
│  │ ✓ Ollama v0.12.10               │    │
│  │ ✓ Llama 3.2 installed           │    │
│  │                                 │    │
│  │ Your local AI is ready!         │    │
│  └─────────────────────────────────┘    │
│                                         │
├─────────────────────────────────────────┤
│                        [Continue →]     │
└─────────────────────────────────────────┘
```

### 5. Keep Backend Endpoints

The following endpoints already exist and work:
- `GET /system/hardware` - Returns hardware info including `ollama_installed`, `ollama_version`, `ollama_models`
- `POST /system/ollama/pull` - Starts model download
- `GET /system/ollama/pull-status?model=<name>` - Returns download progress

No backend changes needed.

### 6. Remove Unused Code

Delete from Step1LocalAI.svelte:
- `modelRecommendations` object
- `getRecommendedModel()` function
- Hardware grid display (RAM, CPU, GPU cards)
- "Recommendation box" showing max params
- Alternative model options in the install section

### 7. Update Messaging

Old: "Let's set up your local AI assistant first. This ensures you can always write, even offline."

New: "Your writing assistant needs a small AI model for offline help. This takes about 2 minutes."

## Files to Modify

1. `frontend/src/lib/components/Onboarding/Step1LocalAI.svelte` - Main changes
2. (Optional) `frontend/src/lib/api_client.ts` - If HardwareInfo type needs updating

## Testing

1. Uninstall llama3.2 model: `ollama rm llama3.2:3b`
2. Open app - should see "Install" button
3. Click Install - should see progress bar
4. Wait for completion - should see "Ready" state
5. Click Continue - should advance to Step 2

To test Ollama-not-installed state:
1. Stop Ollama: `pkill ollama`
2. Open app - should see "Install Ollama" prompt
3. Start Ollama: `ollama serve`
4. Click Rescan - should show model install UI

## Acceptance Criteria

- [ ] Only one model offered: llama3.2:3b
- [ ] No hardware tier recommendations
- [ ] Clear 3-state UI: Install Ollama → Install Model → Ready
- [ ] Progress bar works during download
- [ ] Continue button disabled until ready
- [ ] Ollama version shown for troubleshooting
- [ ] Clean, simple UI without decision paralysis

## Notes

- The Foreman uses `llama3.2:3b` (defined in CLAUDE.md)
- mistral:7b is used by foreman.py but llama3.2:3b is the backup/onboarding model
- Cloud APIs handle all quality-critical tasks
- This simplification reduces onboarding friction significantly
