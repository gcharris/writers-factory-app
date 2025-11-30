# Settings System Quick Start

Fast reference for working with the Writer's Factory App settings system.

## TL;DR

```javascript
// Load settings
const settings = await apiClient.getSettingsCategory('scoring');
const weight = settings.voice_authenticity_weight; // 30

// Save setting
await apiClient.setSetting('scoring.voice_authenticity_weight', 35, 'scoring');

// Reset to defaults
await apiClient.resetSettings('scoring');
```

---

## Settings at a Glance

| Category | Key Settings | Defaults | Purpose |
|----------|-------------|----------|---------|
| **scoring** | 5 rubric weights | 30/20/20/15/15 | Scene scoring weights |
| **anti_patterns** | Pattern rules | 35 built-in | Prose pattern detection |
| **enhancement** | 4 thresholds | 85/85/70/60 | Enhancement pipeline |
| **tournament** | Variants, strategies | 5 variants, all strategies | Scene generation |
| **foreman** | Behavior levels | medium/questioning/balanced | AI personality |
| **context** | Token limits | 20 msgs, 1000 KB | Memory management |

---

## Common Tasks

### Change Scoring Weights

```javascript
// Literary Fiction preset (voice-heavy)
await apiClient.setSetting('scoring.voice_authenticity_weight', 40, 'scoring');
await apiClient.setSetting('scoring.character_consistency_weight', 25, 'scoring');
await apiClient.setSetting('scoring.metaphor_discipline_weight', 15, 'scoring');
await apiClient.setSetting('scoring.anti_pattern_compliance_weight', 10, 'scoring');
await apiClient.setSetting('scoring.phase_appropriateness_weight', 10, 'scoring');
```

### Add Custom Anti-Pattern

```javascript
const customPattern = {
  pattern: 'very|really|just',  // Regex
  severity: 'formulaic',         // 'zero' or 'formulaic'
  reason: 'Weak intensifiers'
};

const settings = await apiClient.getSettingsCategory('anti_patterns');
settings.custom_patterns.push(customPattern);
await apiClient.setSetting('anti_patterns.custom_patterns', settings.custom_patterns, 'anti_patterns');
```

### Adjust Enhancement Aggressiveness

```javascript
// Conservative - minimal changes
await apiClient.setSetting('enhancement.aggressiveness', 'conservative', 'enhancement');

// Aggressive - heavy optimization
await apiClient.setSetting('enhancement.aggressiveness', 'aggressive', 'enhancement');
```

### Reduce Token Usage

```javascript
// Minimal voice bundle (3000 → 500 tokens)
await apiClient.setSetting('context.voice_bundle_injection', 'minimal', 'context');

// Reduce conversation history (2000 → 1000 tokens)
await apiClient.setSetting('context.max_conversation_history', 10, 'context');

// Reduce continuity depth (1500 → 500 tokens)
await apiClient.setSetting('context.continuity_context_depth', 1, 'context');

// Total savings: ~5000 tokens
```

### Make Foreman More Proactive

```javascript
await apiClient.setSetting('foreman.proactiveness', 'high', 'foreman');
await apiClient.setSetting('foreman.challenge_level', 'critical', 'foreman');
await apiClient.setSetting('foreman.verbosity', 'detailed', 'foreman');
```

---

## Settings Resolution Order

```
Project Override → Global Setting → Default Value
```

**Example:**
```javascript
// Default: 30
DEFAULT_VOICE_WEIGHT = 30

// Global setting: 35
await apiClient.setSetting('scoring.voice_authenticity_weight', 35, 'scoring');

// Project override: 40
await apiClient.setProjectSetting(projectId, 'scoring.voice_authenticity_weight', 40);

// Result for this project: 40
// Result for other projects: 35
```

---

## Validation Rules

### Scoring
- All 5 weights must sum to exactly 100
- Each weight has min/max constraints (see [SETTINGS_SYSTEM.md](./SETTINGS_SYSTEM.md))

### Enhancement
- Logical ordering required:
  ```
  rewrite_threshold < six_pass_threshold ≤ action_prompt_threshold
  ```

### Tournament
- At least 1 strategy must be selected
- Variants per agent: 3-10

### Context
- Token estimation shown in real-time
- Warning if > 8000 tokens (typical model limit)

---

## Component Usage

### In a Svelte Component

```svelte
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import SettingsSlider from './Settings/SettingsSlider.svelte';

  let voiceWeight = 30;
  let isLoading = true;
  let isSaving = false;

  onMount(async () => {
    try {
      const settings = await apiClient.getSettingsCategory('scoring');
      voiceWeight = settings.voice_authenticity_weight || 30;
    } catch (e) {
      addToast({ type: 'error', message: 'Failed to load settings' });
    } finally {
      isLoading = false;
    }
  });

  async function saveSettings() {
    isSaving = true;
    try {
      await apiClient.setSetting(
        'scoring.voice_authenticity_weight',
        voiceWeight,
        'scoring'
      );
      addToast({ type: 'success', message: 'Settings saved' });
    } catch (e) {
      addToast({ type: 'error', message: 'Failed to save settings' });
    } finally {
      isSaving = false;
    }
  }
</script>

{#if isLoading}
  <div>Loading...</div>
{:else}
  <SettingsSlider
    label="Voice Authenticity Weight"
    bind:value={voiceWeight}
    min={10}
    max={50}
    tooltip="How heavily to penalize AI-sounding prose"
  />
  <button on:click={saveSettings} disabled={isSaving}>
    {isSaving ? 'Saving...' : 'Save'}
  </button>
{/if}
```

---

## Shared UI Components

### SettingsSlider

```svelte
<SettingsSlider
  label="Max Messages"
  bind:value={maxMessages}
  min={10}
  max={50}
  step={1}
  tooltip="Hover explanation"
  unit=""
  disabled={false}
/>
```

### SettingsRadioGroup

```svelte
<SettingsRadioGroup
  bind:value={selectedOption}
  options={[
    { value: 'low', label: 'Low', description: 'Minimal' },
    { value: 'high', label: 'High', description: 'Maximum' }
  ]}
/>
```

### SettingsToggle

```svelte
<SettingsToggle
  bind:checked={isEnabled}
  label="Enable Feature"
  description="What this does"
/>
```

### SettingsSection

```svelte
<SettingsSection title="Advanced Options" bind:expanded={isExpanded}>
  <!-- Content here -->
</SettingsSection>
```

---

## API Reference

### Frontend API Client

```javascript
// Get all settings in category
const settings = await apiClient.getSettingsCategory('category_name');
// Returns: { key1: value1, key2: value2, ... }

// Set individual setting
await apiClient.setSetting('category.key', value, 'category_name');
// Returns: void (throws on error)

// Reset category to defaults (Phase 5.2)
await apiClient.resetSettings('category_name');
// Returns: void

// Get project-specific settings (Phase 5.2)
const settings = await apiClient.getProjectSettings(projectId);
// Returns: { key1: value1, key2: value2, ... }

// Set project-specific setting (Phase 5.2)
await apiClient.setProjectSetting(projectId, 'category.key', value);
// Returns: void
```

### Backend Endpoints (Phase 5.2)

```
GET    /settings/{category}                 - Get category settings
POST   /settings/{category}/{key}           - Set individual setting
DELETE /settings/{category}/{key}           - Remove setting (revert to default)
GET    /settings/project/{project_id}       - Get project overrides
POST   /settings/project/{project_id}/{key} - Set project override
DELETE /settings/project/{project_id}/{key} - Remove project override
POST   /settings/reset/{category}           - Reset category to defaults
GET    /settings/defaults                   - Get all default values
```

---

## Presets

### Scoring Presets

```javascript
// Balanced (default)
{ voice: 30, character: 20, metaphor: 20, antiPattern: 15, phase: 15 }

// Literary Fiction (voice-heavy)
{ voice: 40, character: 25, metaphor: 15, antiPattern: 10, phase: 10 }

// Commercial Thriller (anti-pattern strict)
{ voice: 25, character: 20, metaphor: 15, antiPattern: 25, phase: 15 }

// Genre Romance (character-heavy)
{ voice: 20, character: 30, metaphor: 20, antiPattern: 15, phase: 15 }
```

### Enhancement Presets

```javascript
// Conservative (higher thresholds, less enhancement)
{ auto: 90, actionPrompt: 90, sixPass: 75, rewrite: 65, aggressiveness: 'conservative' }

// Aggressive (lower thresholds, more enhancement)
{ auto: 80, actionPrompt: 80, sixPass: 65, rewrite: 55, aggressiveness: 'aggressive' }
```

### Foreman Presets

```javascript
// Supportive Coach
{ proactiveness: 'low', challenge: 'supportive', verbosity: 'balanced' }

// Questioning Collaborator (default)
{ proactiveness: 'medium', challenge: 'questioning', verbosity: 'balanced' }

// Critical Director
{ proactiveness: 'high', challenge: 'critical', verbosity: 'detailed' }
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Settings not loading | Check backend is running on port 8000 |
| Changes not saving | Verify setting key format: `category.key` |
| Validation errors | Check constraints in [SETTINGS_SYSTEM.md](./SETTINGS_SYSTEM.md) |
| Token count too high | Reduce voice bundle, conversation history, or continuity depth |
| Foreman too passive | Increase proactiveness, challenge, or verbosity |
| Too many variants | Reduce `variants_per_agent` or deselect strategies |

---

## Files Reference

| File | Purpose |
|------|---------|
| [frontend/src/lib/components/SettingsPanel.svelte](../frontend/src/lib/components/SettingsPanel.svelte) | Main container with tabs |
| [frontend/src/lib/components/SettingsScoring.svelte](../frontend/src/lib/components/SettingsScoring.svelte) | Rubric weights |
| [frontend/src/lib/components/SettingsAntiPatterns.svelte](../frontend/src/lib/components/SettingsAntiPatterns.svelte) | Pattern detection |
| [frontend/src/lib/components/SettingsEnhancement.svelte](../frontend/src/lib/components/SettingsEnhancement.svelte) | Enhancement thresholds |
| [frontend/src/lib/components/SettingsTournament.svelte](../frontend/src/lib/components/SettingsTournament.svelte) | Scene generation |
| [frontend/src/lib/components/SettingsForeman.svelte](../frontend/src/lib/components/SettingsForeman.svelte) | AI behavior |
| [frontend/src/lib/components/SettingsContext.svelte](../frontend/src/lib/components/SettingsContext.svelte) | Memory management |
| [frontend/src/lib/components/Settings/](../frontend/src/lib/components/Settings/) | Shared UI components |

---

## Related Docs

- [SETTINGS_SYSTEM.md](./SETTINGS_SYSTEM.md) - Complete system documentation
- [SETTINGS_API_REFERENCE.md](./SETTINGS_API_REFERENCE.md) - API endpoint reference
- [SETTINGS_UI_COMPONENTS.md](./SETTINGS_UI_COMPONENTS.md) - Component API docs
- [SETTINGS_BACKEND_IMPLEMENTATION.md](./SETTINGS_BACKEND_IMPLEMENTATION.md) - Backend architecture

---

## Next Steps

1. **Read the full docs**: [SETTINGS_SYSTEM.md](./SETTINGS_SYSTEM.md)
2. **Explore components**: Open Settings panel in app
3. **Backend implementation**: Phase 5.2 endpoints
4. **Add new settings**: Follow guide in main docs
