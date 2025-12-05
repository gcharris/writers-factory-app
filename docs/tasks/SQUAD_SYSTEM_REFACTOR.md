# Task: Squad System Refactor (Align with Key Provisioning)

**Priority:** High (UX Clarity)
**Estimated Effort:** 4-6 hours
**Dependencies:** Key provisioning system (already implemented)

---

## Problem

The Squad system was designed **before** the key provisioning model existed. It assumes users bring their own API keys and choose presets based on available keys. But the MVP model is:

| Category | Providers | Who Pays |
|----------|-----------|----------|
| **FREE FOR MVP** | DeepSeek, Qwen, Mistral, Zhipu, Kimi, Yandex | You (subsidized) |
| **PREMIUM** | OpenAI, Anthropic, xAI, Google | User (their own keys) |
| **LOCAL** | Ollama | Free (runs locally) |

### Current Issues

1. **Presets don't match reality:**
   - "Unfiltered Squad" requires `XAI_API_KEY` - but xAI is PREMIUM (user pays)
   - "Russian Writers Squad" requires `YANDEX_API_KEY` - Yandex IS free, but users don't know this
   - Costs shown ($20/month, $80/month) are developer estimates, not what users pay

2. **Lock icons confuse:**
   - Show models user CAN'T use because they haven't configured premium keys
   - FREE models mixed in with locked premium models
   - No explanation of what's free vs requires user keys

3. **Disconnect from Chat Selector:**
   - User picks Squad → sets defaults for background tasks
   - User picks Chat Model → overrides for conversation
   - These are disconnected and confusing

4. **Chat Model Selector is correct:**
   - `ModelSelector.svelte` already implements the right UX
   - Shows "NO KEY" badge for premium without user keys
   - Free for MVP models always available

---

## Recommended Solution: Option 2 - Simplify

**Remove Squad complexity, enhance existing components.**

### Phase 1: Simplify Settings

Replace `SettingsSquad.svelte` with a simpler **"AI Setup"** panel:

```
┌─────────────────────────────────────┐
│ Your AI Setup                       │
├─────────────────────────────────────┤
│ ✓ FREE FOR MVP                      │
│   DeepSeek V3, Qwen Plus, Mistral,  │
│   Zhipu, Kimi - all ready to use!   │
│                                     │
│ ⭐ PREMIUM (Add your keys)          │
│   ○ OpenAI    [Add Key]             │
│   ○ Anthropic [Add Key]             │
│   ○ xAI       [Add Key]             │
│                                     │
│ 💻 LOCAL                            │
│   ✓ Ollama: mistral:7b, llama3.2    │
│                                     │
│ Default for chat: [DeepSeek V3 ▼]   │
│ Default for tasks: [Auto ▼]         │
└─────────────────────────────────────┘
```

### Phase 2: Remove Squad Components

Files to remove or simplify:

```
frontend/src/lib/components/Squads/SquadWizard.svelte     # Remove
frontend/src/lib/components/Settings/SettingsSquad.svelte # Replace with AISetup
frontend/src/lib/components/Settings/RoleModelSelector.svelte     # Remove (if only used by Squad)
frontend/src/lib/components/Settings/HealthCheckModelConfig.svelte # Keep (may be useful)
```

### Phase 3: Update API Client

Remove Squad-related types and functions:
- `SquadPreset`
- `TournamentModel`
- `TournamentCostEstimate`
- Squad-related API calls

### Phase 4: Backend Cleanup

Review and simplify:
- `/squad/*` endpoints - may be removable
- Model assignment logic - simplify to "default model" + "premium if available"

---

## Alternative: Quick Fixes (If Keeping Squad)

If full refactor is too much, these quick fixes align Squad with provisioning:

1. **Remove lock icons** - just hide unavailable models
2. **Remove monthly cost estimates** - irrelevant for MVP
3. **Rename preset tiers:**
   - "Free" → "Free for MVP"
   - "Budget" → Keep
   - "Premium" → "Requires Your Keys"
4. **Add explanatory text:** "Free for MVP models are subsidized during beta - no API keys needed!"
5. **Simplify presets to:**

| Preset | What It Means |
|--------|---------------|
| Starter | DeepSeek only (free, always works) |
| Budget | All FREE FOR MVP models |
| Premium | FREE + user's premium keys (if configured) |
| Local Only | Ollama only (offline, private) |

---

## Implementation Steps

### If Full Refactor (Recommended):

1. [ ] Create new `SettingsAISetup.svelte` component
2. [ ] Wire up to existing key provisioning status
3. [ ] Add "Default Model" setting (chat + tasks)
4. [ ] Remove/archive Squad components
5. [ ] Update `SettingsPanel.svelte` tab list
6. [ ] Update API client types
7. [ ] Test model selection flow end-to-end

### If Quick Fixes:

1. [ ] Remove lock icons from Squad UI
2. [ ] Remove cost estimates
3. [ ] Update preset names and descriptions
4. [ ] Add explanatory banner about free provisioning
5. [ ] Hide advanced role assignment behind "Advanced" toggle

---

## Files Involved

### Frontend
- `frontend/src/lib/components/Settings/SettingsSquad.svelte` (777 lines)
- `frontend/src/lib/components/Squads/SquadWizard.svelte`
- `frontend/src/lib/components/Settings/RoleModelSelector.svelte`
- `frontend/src/lib/components/Settings/HealthCheckModelConfig.svelte`
- `frontend/src/lib/components/chat/ModelSelector.svelte` (the good one)
- `frontend/src/lib/api_client.ts` (Squad types)
- `frontend/src/lib/stores.js` (Squad state)

### Backend
- `backend/api.py` - `/squad/*` endpoints
- Model assignment in Foreman/Director services

---

## Success Criteria

1. New user opens app → sees "Free for MVP" models immediately available
2. No confusing presets or cost estimates
3. Clear path to add premium keys if desired
4. Single source of truth for model selection
5. `npm run check` passes
6. No TypeScript errors

---

## Decision Needed

**Which approach?**
- [ ] Full refactor (4-6 hours) - Clean, aligned with provisioning
- [ ] Quick fixes (1-2 hours) - Band-aid, keeps technical debt

---

*Created: Dec 5, 2025*
*Context: Claude IDE analysis of Squad vs Provisioning mismatch*
