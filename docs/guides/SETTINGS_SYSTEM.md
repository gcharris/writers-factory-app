# Settings System Documentation

Complete guide to the Writer's Factory App settings system architecture, components, and usage.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Settings Categories](#settings-categories)
3. [Component Reference](#component-reference)
4. [Backend Integration](#backend-integration)
5. [Adding New Settings](#adding-new-settings)
6. [Design System](#design-system)

---

## Architecture Overview

The settings system is built with a 3-tier resolution model:

```
Project Override → Global Setting → Default Value
```

### Key Principles

- **Category-based organization**: Settings grouped by domain (scoring, enhancement, etc.)
- **Shared UI components**: Reusable sliders, toggles, radio groups, and sections
- **Real-time validation**: Immediate feedback on invalid configurations
- **Change tracking**: Dirty state detection with unsaved changes warnings
- **Optimistic UI**: Fast local updates with backend persistence

### File Structure

```
frontend/src/lib/components/
├── Settings/                      # Shared UI components
│   ├── SettingsSlider.svelte      # Numeric range input
│   ├── SettingsRadioGroup.svelte  # Mutually exclusive options
│   ├── SettingsToggle.svelte      # Boolean flags
│   └── SettingsSection.svelte     # Collapsible containers
├── SettingsPanel.svelte           # Main container with tab navigation
├── SettingsScoring.svelte         # Rubric weights
├── SettingsAntiPatterns.svelte    # Pattern detection rules
├── SettingsEnhancement.svelte     # Polish thresholds
├── SettingsTournament.svelte      # Scene generation config
├── SettingsForeman.svelte         # AI behavior
└── SettingsContext.svelte         # Memory management
```

---

## Settings Categories

### 1. Scoring (scoring)

Configure the 5-category rubric weights for scene scoring.

**Settings:**
- `voice_authenticity_weight` (10-50, default: 30)
- `character_consistency_weight` (10-30, default: 20)
- `metaphor_discipline_weight` (10-30, default: 20)
- `anti_pattern_compliance_weight` (5-25, default: 15)
- `phase_appropriateness_weight` (5-25, default: 15)

**Constraint:** All weights must sum to exactly 100.

**Presets:**
- **Balanced** (default): 30/20/20/15/15
- **Literary Fiction**: 40/25/15/10/10 (voice-heavy)
- **Commercial Thriller**: 25/20/15/25/15 (anti-pattern strict)
- **Genre Romance**: 20/30/20/15/15 (character-heavy)

**Use Case:** Adjust rubric weights to match your genre or writing style.

---

### 2. Anti-Patterns (anti_patterns)

Configure pattern detection rules that flag problematic prose.

**Built-in Patterns:**

**Zero-Tolerance (-2 points):**
- "suddenly" / "all of a sudden"
- "realized" / "noticed"
- Filtering verbs (seemed, appeared, felt like)
- Expository names
- Cliché metaphors
- Thought verbs (thought, wondered, knew)

**Formulaic (-1 point):**
- Adverbs (-ly words)
- Passive voice
- Filter phrases (could see, heard the, felt the)
- Weak verbs (is/was/had)
- Telling emotions (angry, happy, sad)

**Custom Patterns:**
- Add your own regex patterns with severity levels
- Include optional reason/explanation
- Validated before saving

**Settings:**
- `zero_tolerance_patterns` (array of pattern objects)
- `formulaic_patterns` (array of pattern objects)
- `custom_patterns` (array of user-defined patterns)

**Use Case:** Enforce your personal style guide or avoid specific writing habits.

---

### 3. Enhancement (enhancement)

Configure thresholds that determine which enhancement mode runs.

**Thresholds:**
- `auto_threshold` (70-95, default: 85) - Score below which enhancement is auto-suggested
- `action_prompt_threshold` (80-95, default: 85) - Score above which surgical fixes are used
- `six_pass_threshold` (60-80, default: 70) - Score below which full 6-pass runs
- `rewrite_threshold` (50-70, default: 60) - Score below which rewrite is recommended

**Constraint:** Must maintain logical ordering:
```
rewrite_threshold < six_pass_threshold ≤ action_prompt_threshold
```

**Aggressiveness:**
- `aggressiveness` (conservative/medium/aggressive, default: medium)
  - **Conservative**: Minimal changes, preserve writer's voice
  - **Medium**: Balanced polish with fixes
  - **Aggressive**: Heavy optimization for score improvement

**Enhancement Pipeline:**
- **Score ≥ 85**: No enhancement (scene is publication-ready)
- **85 > Score ≥ 70**: Action Prompt (surgical OLD → NEW fixes)
- **70 > Score ≥ 60**: 6-Pass Full Enhancement (comprehensive rewrite)
- **Score < 60**: Rewrite Recommended (start over)

**Use Case:** Control how aggressively the system polishes your scenes.

---

### 4. Tournament (tournament)

Configure the scene generation tournament behavior.

**Settings:**
- `variants_per_agent` (3-10, default: 5) - How many variants each model generates
- `strategies` (array, default: all 5) - Which writing strategies to use
  - ACTION: Action/conflict-driven scenes
  - CHARACTER: Psychology and interiority
  - DIALOGUE: Conversation-heavy scenes
  - ATMOSPHERIC: Setting and mood emphasis
  - BALANCED: Even distribution
- `auto_score_variants` (bool, default: true) - Automatically run scoring on all variants
- `show_losing_variants` (bool, default: true) - Display all variants or just top N
- `top_n_display` (3-10, default: 5) - How many top variants to highlight

**Constraint:** At least 1 strategy must be selected.

**Tournament Math:**
- 3 models × 5 strategies × 5 variants = **75 total scene variants**
- With auto-scoring: **75 scenes scored in parallel**
- Top 5 highlighted based on composite score

**Use Case:** Balance quality vs. speed by adjusting variant count and strategies.

---

### 5. Foreman (foreman)

Configure The Foreman's AI behavior and interaction style.

**Settings:**
- `proactiveness` (low/medium/high, default: medium)
  - **Low**: Responds when asked only
  - **Medium**: Guides the process
  - **High**: Directive, proactive planning
- `challenge_level` (supportive/questioning/critical, default: questioning)
  - **Supportive**: Encourages, affirms decisions
  - **Questioning**: Asks clarifying questions
  - **Critical**: Challenges assumptions, demands rigor
- `verbosity` (terse/balanced/detailed, default: balanced)
  - **Terse**: Brief responses, minimal explanation
  - **Balanced**: Concise with key context
  - **Detailed**: Comprehensive explanations
- `auto_kb_writes` (bool, default: true) - Automatically write to Knowledge Base

**Warning System:**
If all settings are Low/Supportive/Terse, the system warns:
> "All settings are at minimum. The Foreman will be very passive. Consider increasing at least one for a more engaged experience."

**Use Case:** Match The Foreman's personality to your preferred working style.

---

### 6. Context (context)

Configure context window management and token allocation.

**Settings:**
- `max_conversation_history` (10-50, default: 20) - Number of recent messages to keep
- `kb_context_limit` (500-2000, default: 1000) - Tokens allocated to KB entries
- `voice_bundle_injection` (minimal/summary/full, default: full)
  - **Minimal**: Just anti-patterns (~500 tokens)
  - **Summary**: Core voice rules (~1500 tokens)
  - **Full**: Complete voice bundle (~3000 tokens)
- `continuity_context_depth` (1-5, default: 3) - Number of previous scenes to reference

**Token Estimation:**
```javascript
total_tokens =
  (max_conversation_history × 100) +  // ~100 tokens per message
  kb_context_limit +                   // KB context
  voice_bundle_size +                  // 500/1500/3000
  (continuity_context_depth × 500)     // ~500 tokens per scene
```

**Example:**
- 20 messages = 2,000 tokens
- 1,000 KB limit = 1,000 tokens
- Full voice bundle = 3,000 tokens
- 3 previous scenes = 1,500 tokens
- **Total: 7,500 tokens** (~94% of 8,000 token limit)

**Use Case:** Balance context richness vs. token costs.

---

## Component Reference

### Shared Components

#### SettingsSlider

Numeric range input with label, value display, and min/max indicators.

```svelte
<SettingsSlider
  label="Max Messages"
  bind:value={maxConversationHistory}
  min={10}
  max={50}
  tooltip="Number of recent conversation turns to keep in context"
/>
```

**Props:**
- `label` (string): Display name
- `value` (number): Current value (bind)
- `min` (number, default: 0): Minimum value
- `max` (number, default: 100): Maximum value
- `step` (number, default: 1): Increment size
- `tooltip` (string): Hover explanation
- `unit` (string): Suffix (e.g., "%", "ms")
- `disabled` (bool): Read-only mode

**Styling:**
- Gold accent fill (`--accent-gold`)
- Responsive thumb with hover effects
- Min/max labels on track

---

#### SettingsRadioGroup

Radio buttons for mutually exclusive options with descriptions.

```svelte
<SettingsRadioGroup
  bind:value={aggressiveness}
  options={[
    { value: 'low', label: 'Low', description: 'Minimal changes' },
    { value: 'medium', label: 'Medium', description: 'Balanced polish' },
    { value: 'high', label: 'High', description: 'Heavy optimization' }
  ]}
/>
```

**Props:**
- `label` (string, optional): Group label
- `value` (string): Selected value (bind)
- `options` (array): Option objects with value/label/description

**Styling:**
- Custom radio indicator (gold accent when selected)
- Card-based layout with hover effects
- Description text below label

---

#### SettingsToggle

Toggle switch for boolean settings.

```svelte
<SettingsToggle
  bind:checked={autoScoreVariants}
  label="Auto-score all variants"
  description="Automatically run scoring on all generated variants"
/>
```

**Props:**
- `checked` (bool): Toggle state (bind)
- `label` (string): Display name
- `description` (string, optional): Explanation text
- `disabled` (bool): Read-only mode

**Styling:**
- Animated switch with gold accent when checked
- Inline label and description

---

#### SettingsSection

Collapsible section container for organizing settings.

```svelte
<SettingsSection title="Zero-Tolerance Patterns" bind:expanded={zeroExpanded}>
  <!-- Content here -->
</SettingsSection>
```

**Props:**
- `title` (string): Section header
- `expanded` (bool, default: true): Collapsed state (bind)

**Styling:**
- Chevron indicator (▶ / ▼)
- Smooth expand/collapse animation

---

### Main Panels

#### SettingsScoring

**Features:**
- Linked slider logic (proportional redistribution)
- 4 genre presets + custom
- Real-time sum validation (must equal 100)
- Visual indicator (✓ when valid, ⚠ when invalid)

**Complex Logic - Linked Sliders:**
When one slider changes, the others adjust proportionally to maintain sum=100:

```javascript
function handleSliderChange(changedKey, newValue) {
  // 1. Update the changed slider
  sliders[changedKey].value = newValue;

  // 2. Calculate remaining points to distribute
  const remaining = 100 - newValue;

  // 3. Get other sliders and their current sum
  const others = Object.entries(sliders).filter(([key]) => key !== changedKey);
  const currentSum = others.reduce((sum, [_, slider]) => sum + slider.value, 0);

  // 4. Proportionally redistribute
  others.forEach(([key, slider]) => {
    const proportion = slider.value / currentSum;
    slider.value = Math.round(remaining * proportion);
  });

  // 5. Fix rounding errors by adjusting the largest slider
  const actualSum = newValue + others.reduce((sum, [_, s]) => sum + s.value, 0);
  if (actualSum !== 100) {
    const largest = others.reduce((max, curr) =>
      curr[1].value > max[1].value ? curr : max
    );
    largest[1].value += (100 - actualSum);
  }
}
```

**API Calls:**
```javascript
// Load
const settings = await apiClient.getSettingsCategory('scoring');

// Save
await apiClient.setSetting('scoring.voice_authenticity_weight', 30, 'scoring');
await apiClient.setSetting('scoring.character_consistency_weight', 20, 'scoring');
// ... etc
```

---

#### SettingsAntiPatterns

**Features:**
- Built-in pattern toggles (zero-tolerance, formulaic)
- Custom pattern builder modal
- Regex validation before saving
- Severity levels (zero-tolerance, formulaic)
- Optional reason/explanation

**Custom Pattern Modal:**
```svelte
<div class="modal">
  <div class="form-group">
    <label>Pattern:</label>
    <input bind:value={pattern} placeholder="e.g., suddenly" />
    <span class="hint">Supports regex patterns</span>
  </div>
  <div class="form-group">
    <label>Severity:</label>
    <input type="radio" bind:group={severity} value="zero" /> Zero-Tolerance (-2)
    <input type="radio" bind:group={severity} value="formulaic" /> Formulaic (-1)
  </div>
  <div class="form-group">
    <label>Reason (optional):</label>
    <textarea bind:value={reason} />
  </div>
</div>
```

**Regex Validation:**
```javascript
function validatePattern(pattern) {
  try {
    new RegExp(pattern);
    return { valid: true };
  } catch (e) {
    return { valid: false, error: `Invalid regex: ${e.message}` };
  }
}
```

---

#### SettingsEnhancement

**Features:**
- 4 threshold sliders with logical ordering validation
- Visual score range bar with color coding
- Aggressiveness selection (conservative/medium/aggressive)
- Real-time validation error display

**Threshold Validation:**
```javascript
function validateThresholds() {
  const errors = [];
  if (rewriteThreshold >= sixPassThreshold) {
    errors.push('Rewrite threshold must be below 6-Pass threshold');
  }
  if (sixPassThreshold > actionPromptThreshold) {
    errors.push('6-Pass threshold cannot exceed Action Prompt threshold');
  }
  return errors;
}
```

**Visual Score Range Bar:**
```svelte
<div class="range-bar">
  <div class="range-segment rewrite" style="width: {rewriteThreshold}%">
    <span>Rewrite</span>
  </div>
  <div class="range-segment six-pass" style="width: {sixPassThreshold - rewriteThreshold}%">
    <span>6-Pass</span>
  </div>
  <div class="range-segment action-prompt" style="width: {actionPromptThreshold - sixPassThreshold}%">
    <span>Action</span>
  </div>
  <div class="range-segment no-enhance" style="width: {100 - actionPromptThreshold}%">
    <span>No Enhance</span>
  </div>
</div>
```

Color coding:
- Red (rewrite): Score < 60
- Orange (6-pass): 60 ≤ Score < 70
- Cyan (action): 70 ≤ Score < 85
- Green (no enhance): Score ≥ 85

---

#### SettingsTournament

**Features:**
- Variants per agent slider (3-10)
- 5 writing strategies multi-select with checkboxes
- Display options toggles (auto-score, show losing variants)
- Top N highlight slider (only enabled if showing losing variants)
- Validation: At least 1 strategy required

**Strategy Grid:**
Uses a responsive grid layout with card-based checkboxes:

```svelte
<div class="strategies-grid">
  {#each allStrategies as strategy}
    <label class="strategy-card" class:selected={strategies.includes(strategy.value)}>
      <input type="checkbox" checked={strategies.includes(strategy.value)} />
      <div class="strategy-content">
        <span class="strategy-label">{strategy.label}</span>
        <span class="strategy-desc">{strategy.description}</span>
      </div>
    </label>
  {/each}
</div>
```

---

#### SettingsForeman

**Features:**
- Proactiveness level radio group (low/medium/high)
- Challenge level radio group (supportive/questioning/critical)
- Verbosity radio group (terse/balanced/detailed)
- Auto-KB writes toggle
- Warning system for passive configuration

**Warning Logic:**
```javascript
$: showWarning =
  proactiveness === 'low' &&
  challengeLevel === 'supportive' &&
  verbosity === 'terse';
```

If all settings are at minimum, display:
```svelte
{#if showWarning}
  <div class="warning-box">
    ⚠ All settings are at minimum. The Foreman will be very passive.
  </div>
{/if}
```

---

#### SettingsContext

**Features:**
- 4 sliders (conversation history, KB limit, continuity depth)
- Voice bundle injection radio group (minimal/summary/full)
- Real-time token usage estimation
- Visual progress bar showing % of typical 8,000 token limit

**Token Estimation Logic:**
```javascript
function calculateEstimatedTokens() {
  let total = 0;

  // Conversation history (~100 tokens per message)
  total += maxConversationHistory * 100;

  // KB context
  total += kbContextLimit;

  // Voice bundle
  if (voiceBundleInjection === 'minimal') total += 500;
  else if (voiceBundleInjection === 'summary') total += 1500;
  else total += 3000;

  // Continuity (previous scenes, ~500 tokens each)
  total += continuityContextDepth * 500;

  return total;
}
```

**Usage Visualization:**
```svelte
<div class="usage-estimate">
  <div class="estimate-header">
    <span>Estimated Total Context:</span>
    <span class="value">{estimatedTokens.toLocaleString()} tokens</span>
  </div>
  <div class="estimate-bar">
    <div class="fill" style="width: {Math.min((estimatedTokens / 8000) * 100, 100)}%"></div>
  </div>
  <div class="hint">
    Most models support 8,000+ tokens. Current settings use ~{Math.round((estimatedTokens / 8000) * 100)}%.
  </div>
</div>
```

---

## Backend Integration

### API Client Methods

The settings system uses two primary API methods:

#### Get Settings Category
```javascript
const settings = await apiClient.getSettingsCategory('category_name');
```

**Returns:** Object with all settings in the category
**Example:**
```javascript
{
  voice_authenticity_weight: 30,
  character_consistency_weight: 20,
  metaphor_discipline_weight: 20,
  anti_pattern_compliance_weight: 15,
  phase_appropriateness_weight: 15
}
```

#### Set Individual Setting
```javascript
await apiClient.setSetting('category.key', value, 'category_name');
```

**Parameters:**
- `key` (string): Dotted path (e.g., 'scoring.voice_authenticity_weight')
- `value` (any): Setting value (number, string, bool, array, object)
- `category` (string): Category for grouping

**Example:**
```javascript
await apiClient.setSetting('enhancement.auto_threshold', 85, 'enhancement');
```

### Settings Resolution

Backend implements 3-tier resolution:

```python
def get_setting(key: str, project_id: Optional[str] = None):
    # 1. Check project override
    if project_id:
        override = db.query(ProjectSetting).filter_by(
            project_id=project_id, key=key
        ).first()
        if override:
            return override.value

    # 2. Check global setting
    global_setting = db.query(GlobalSetting).filter_by(key=key).first()
    if global_setting:
        return global_setting.value

    # 3. Return default
    return DEFAULTS.get(key)
```

### Backend Endpoints (Phase 5.2)

**To be implemented:**

```
GET  /settings/{category}           - Get all settings in category
POST /settings/{category}/{key}     - Set individual setting
GET  /settings/project/{project_id} - Get project-specific overrides
POST /settings/project/{project_id} - Set project override
DELETE /settings/project/{project_id}/{key} - Remove project override
GET  /settings/defaults             - Get all default values
POST /settings/reset/{category}     - Reset category to defaults
```

---

## Adding New Settings

### Step 1: Define the Setting

Add default value to backend `DEFAULTS` dict:

```python
DEFAULTS = {
    'my_category.my_setting': 42,
    'my_category.my_flag': True,
    'my_category.my_options': ['option1', 'option2']
}
```

### Step 2: Create or Update Panel Component

If creating a new panel:

```svelte
<!-- frontend/src/lib/components/SettingsMyCategory.svelte -->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import SettingsSlider from './Settings/SettingsSlider.svelte';

  // Local state
  let mySetting = 42;
  let isLoading = true;
  let isSaving = false;
  let hasChanges = false;
  let originalValues = {};

  // Load settings on mount
  onMount(async () => {
    await loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const settings = await apiClient.getSettingsCategory('my_category');
      mySetting = settings.my_setting || 42;
      originalValues = { mySetting };
    } catch (e) {
      console.error('Failed to load settings:', e);
      addToast({ type: 'error', message: 'Failed to load settings' });
    } finally {
      isLoading = false;
    }
  }

  // Track changes
  $: hasChanges = mySetting !== originalValues.mySetting;

  async function saveSettings() {
    isSaving = true;
    try {
      await apiClient.setSetting('my_category.my_setting', mySetting, 'my_category');
      originalValues = { mySetting };
      hasChanges = false;
      addToast({ type: 'success', message: 'Settings saved' });
    } catch (e) {
      console.error('Failed to save settings:', e);
      addToast({ type: 'error', message: 'Failed to save settings' });
    } finally {
      isSaving = false;
    }
  }
</script>

<div class="settings-my-category">
  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <SettingsSlider
      label="My Setting"
      bind:value={mySetting}
      min={0}
      max={100}
      tooltip="What this setting controls"
    />

    <div class="actions">
      <button class="btn-primary" on:click={saveSettings} disabled={!hasChanges || isSaving}>
        {isSaving ? 'Saving...' : 'Save Changes'}
      </button>
    </div>
  {/if}
</div>

<style>
  .settings-my-category {
    padding: 1rem 0;
  }
  /* Add styles following cyber-noir design system */
</style>
```

### Step 3: Register in SettingsPanel

Update [SettingsPanel.svelte](frontend/src/lib/components/SettingsPanel.svelte):

```svelte
<script>
  import SettingsMyCategory from './SettingsMyCategory.svelte';

  const tabs = [
    // ... existing tabs
    { id: 'my-category', label: 'My Category', icon: 'settings', priority: 'P2' },
  ];
</script>

<!-- Content Area -->
<div class="settings-content">
  <!-- ... existing tabs -->
  {:else if activeTab === 'my-category'}
    <SettingsMyCategory />
</div>
```

### Step 4: Test

1. Run dev server: `npm run dev`
2. Open Settings panel
3. Navigate to new tab
4. Verify loading, changing, saving, and validation

---

## Design System

All settings components follow the cyber-noir design system established by Cloud Claude's Director Mode UI.

### Color Palette

```css
/* Primary Colors */
--accent-gold: #d4a574;      /* Primary CTA, accents */
--accent-cyan: #58a6ff;      /* Secondary highlights */

/* Backgrounds */
--bg-primary: #0f1419;       /* Main background */
--bg-secondary: #1a2027;     /* Panel background */
--bg-tertiary: #242d38;      /* Card background */
--bg-elevated: #2d3640;      /* Hover state */

/* Text */
--text-primary: #e6edf3;     /* Main text */
--text-secondary: #8b949e;   /* Secondary text */
--text-muted: #6e7681;       /* Disabled/hint text */

/* Status */
--success: #3fb950;          /* Success state */
--danger: #f85149;           /* Error state */
--warning: #ff9f43;          /* Warning state */

/* Borders */
--border: #2d3a47;           /* Subtle borders */
```

### Typography

```css
/* Font Sizes */
--text-xs: 11px;
--text-sm: 12px;
--text-base: 14px;
--text-lg: 16px;
--text-xl: 18px;

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
```

### Border Radius

```css
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;
--radius-full: 9999px;
```

### Transitions

```css
--transition-fast: 100ms ease;
--transition-base: 150ms ease;
--transition-slow: 300ms ease;
```

### Component Patterns

#### Buttons

```css
.btn-primary {
  padding: 0.625rem 1.25rem;
  background: var(--accent-gold);
  color: var(--bg-primary);
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  transition: all var(--transition-base);
  border: none;
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: #e0b584;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

#### Cards

```css
.card {
  padding: 1rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

.card:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-gold);
}
```

#### Input Fields

```css
input[type="text"],
input[type="number"],
textarea {
  padding: 0.5rem;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--text-base);
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--accent-gold);
}
```

---

## Best Practices

### Change Tracking

Always implement change tracking to enable unsaved changes warnings:

```javascript
// Store original values on load
originalValues = { setting1: value1, setting2: value2 };

// Track changes reactively
$: hasChanges =
  setting1 !== originalValues.setting1 ||
  setting2 !== originalValues.setting2;

// Disable save button when no changes
<button disabled={!hasChanges || isSaving}>Save</button>
```

### Validation

Validate before saving to prevent invalid states:

```javascript
async function saveSettings() {
  // Validate
  if (!isValid) {
    addToast({ type: 'error', message: 'Invalid configuration' });
    return;
  }

  // Save
  isSaving = true;
  try {
    // ... API calls
  } finally {
    isSaving = false;
  }
}
```

### Loading States

Always show loading state while fetching:

```svelte
{#if isLoading}
  <div class="loading">Loading settings...</div>
{:else}
  <!-- Settings UI -->
{/if}
```

### Error Handling

Wrap API calls in try/catch and show user-friendly errors:

```javascript
try {
  await apiClient.setSetting('key', value, 'category');
  addToast({ type: 'success', message: 'Settings saved' });
} catch (e) {
  console.error('Failed to save:', e);
  addToast({ type: 'error', message: 'Failed to save settings' });
}
```

### Tooltips

Always provide tooltips explaining what each setting does:

```svelte
<SettingsSlider
  label="Max Messages"
  tooltip="Number of recent conversation turns to keep in context"
  bind:value={maxMessages}
/>
```

---

## Troubleshooting

### Settings not loading

1. Check browser console for API errors
2. Verify backend is running on port 8000
3. Check network tab for failed requests
4. Verify settings category name matches backend

### Changes not saving

1. Check `hasChanges` is true
2. Verify save button is enabled
3. Check console for API errors
4. Verify setting key format matches backend

### Validation errors

1. Check validation logic in component
2. Verify constraints are documented
3. Show validation errors to user
4. Disable save button when invalid

### UI not updating

1. Check reactivity (using `$:` or `bind:`)
2. Verify state variables are declared with `let`
3. Check for mutation issues (use spread operator)
4. Verify component re-renders on state change

---

## Future Enhancements

### Phase 5.2: Backend Implementation

- Implement all settings endpoints
- Add database migrations for settings tables
- Add project-specific override support
- Add settings import/export

### Phase 5.3: Advanced Features

- Settings search/filter
- Bulk reset to defaults
- Settings presets sharing
- Settings diff view (current vs. default)
- Settings validation on backend
- Settings audit log

---

## Related Documentation

- [SETTINGS_API_REFERENCE.md](./SETTINGS_API_REFERENCE.md) - Complete API endpoint reference
- [SETTINGS_UI_COMPONENTS.md](./SETTINGS_UI_COMPONENTS.md) - Component API docs
- [SETTINGS_BACKEND_IMPLEMENTATION.md](./SETTINGS_BACKEND_IMPLEMENTATION.md) - Backend architecture
