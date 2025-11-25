# Settings Detail Panels Implementation Plan

**Version**: 1.0
**Status**: Ready for Implementation
**Track**: Phase 5 Track 3 Phase 5
**Priority**: P1 High - Completes Settings UI
**Effort**: ~20 hours (6 components)
**Dependencies**: ✅ Backend SettingsService (Phase 3C), ✅ SettingsPanel shell (Track 1)

---

## Executive Summary

Building 6 settings detail panels to expose craft-meaningful configuration for Writers Factory's Director Mode. These panels complete the Settings UI by providing granular control over scoring, voice authentication, anti-patterns, enhancement, tournaments, and Foreman behavior.

**Goal**: Enable writers to customize AI assistance to their specific craft style
**Approach**: Reusable UI components + category-specific logic
**Integration**: 8 existing Settings API endpoints (lines 2504-2697 in api.py)

---

## Research Findings

### Existing Infrastructure ✅ Solid Foundation

**Backend (Phase 3C Complete)**:
- SettingsService with 3-tier resolution (project → global → default)
- SQLite persistence (shares sessions.db with Foreman KB)
- 11 settings categories in DefaultSettings dataclass (lines 108-283 in settings_service.py)
- 8 API endpoints: GET/POST/DELETE `/settings/{key}`, GET `/settings/category/{category}`, etc.

**Frontend (Track 1 Complete)**:
- SettingsPanel.svelte with tabbed navigation (14 lines)
- SettingsAgents.svelte (API keys) - 100+ lines
- SettingsOrchestrator.svelte (quality tiers) - 150+ lines
- Design system: Cyber-noir with gold accents (#d4a574)

**Settings Categories in Backend**:
1. ✅ `scoring` - Voice/Character/Metaphor/Anti-Pattern/Phase weights (lines 117-135)
2. ✅ `anti_patterns` - Zero-tolerance/Formulaic/Custom patterns (lines 138-152)
3. ✅ `enhancement` - Auto/ActionPrompt/6-Pass/Rewrite thresholds (lines 155-161)
4. ✅ `tournament` - Variants per agent, strategies, display (lines 164-170)
5. ✅ `foreman` - Proactiveness, challenge, task models (lines 173-193)
6. ✅ `context` - Max history, KB limit, voice bundle (lines 196-201)

### Design System Patterns (from SettingsOrchestrator.svelte)

**Color Palette**:
- Background Primary: `#0f1419`
- Background Secondary: `#1a2027`
- Background Tertiary: `#242d38`
- Accent Gold: `#d4a574` (primary CTA)
- Accent Cyan: `#58a6ff` (secondary highlights)
- Success Green: `#3fb950`
- Text Primary: `#e6edf3`
- Text Secondary: `#8b949e`
- Text Muted: `#6e7681`

**Component Patterns**:
- Card-based layouts with rounded corners
- Icons paired with labels
- Progressive disclosure (expandable sections)
- Real-time validation feedback
- Save/Reset buttons with loading states
- Tooltips for craft guidance

---

## Component Specifications

### Component 1: SettingsScoring.svelte (~200 lines)

**Purpose**: Configure 5-category rubric weights with presets
**Complexity**: HIGH (linked slider logic)
**Effort**: 3 hours

**UI Layout**:
```
┌─ Scoring Rubric Weights ────────────────────────────┐
│ Preset: [Balanced ▼]  (Literary, Thriller, etc.)   │
│                                                      │
│ Voice Authenticity        30 ████████░░░  (10-50)   │
│ Character Consistency     20 █████░░░░░░  (10-30)   │
│ Metaphor Discipline       20 █████░░░░░░  (10-30)   │
│ Anti-Pattern Compliance   15 ████░░░░░░░  (5-25)    │
│ Phase Appropriateness     15 ████░░░░░░░  (5-25)    │
│ Total: 100/100 ✓                                    │
│ [Reset to Global]  [Save Changes]                   │
└──────────────────────────────────────────────────────┘
```

**Key Features**:
- **Linked Sliders**: Changing one auto-adjusts others to maintain sum=100
- **Presets**: 4 configurations (Literary Fiction, Thriller, Romance, Balanced)
- **Validation**: Red indicator if sum ≠ 100
- **Tooltips**: Craft guidance per slider

**Backend Integration**:
```javascript
const settings = await apiClient.getSettingsCategory('scoring');
await apiClient.setSetting('scoring.voice_authenticity_weight', value);
```

**Algorithm: Linked Slider Logic**
```javascript
function updateLinkedSliders(changedKey, newValue) {
  const others = sliders.filter(s => s.key !== changedKey);
  const total = 100;
  const remaining = total - newValue;

  // Calculate current sum of other sliders
  const currentSum = others.reduce((sum, s) => sum + s.value, 0);

  // Proportionally redistribute
  others.forEach(slider => {
    const proportion = slider.value / currentSum;
    slider.value = Math.round(remaining * proportion);
  });

  // Handle rounding errors - adjust largest slider
  const actualSum = newValue + others.reduce((sum, s) => sum + s.value, 0);
  if (actualSum !== total) {
    const largest = others.reduce((max, s) => s.value > max.value ? s : max);
    largest.value += (total - actualSum);
  }
}
```

**Presets**:
```javascript
const PRESETS = {
  literary_fiction: { voice: 40, character: 25, metaphor: 15, anti: 10, phase: 10 },
  commercial_thriller: { voice: 25, character: 20, metaphor: 15, anti: 25, phase: 15 },
  genre_romance: { voice: 20, character: 30, metaphor: 20, anti: 15, phase: 15 },
  balanced: { voice: 30, character: 20, metaphor: 20, anti: 15, phase: 15 }
};
```

**Edge Cases**:
- Slider at minimum + proportional reduction would go below minimum
- All sliders at minimum except one
- User manually edits to sum ≠ 100 (show warning, disable save)
- Preset selection while unsaved changes exist

---

### Component 2: SettingsAntiPatterns.svelte (~250 lines)

**Purpose**: Configure anti-pattern detection with custom patterns
**Complexity**: HIGH (pattern builder, regex validation)
**Effort**: 3 hours

**UI Layout**:
```
┌─ Anti-Pattern Detection ─────────────────────────────┐
│ Zero-Tolerance Patterns (-2 points)                  │
│ ☑ First-person italics without dialogue tag          │
│ ☑ "with X precision" phrasing                        │
│                                                       │
│ Formulaic Patterns (-1 point)                        │
│ ☐ "despite the" (disabled)                           │
│ ☑ "eyes widened"                                     │
│                                                       │
│ Custom Patterns                                       │
│ ┌───────────────────────────────────────────────┐    │
│ │ suddenly      Formulaic [-1]  [Remove]       │    │
│ └───────────────────────────────────────────────┘    │
│ [+ Add Custom Pattern]                                │
│ [Reset to Defaults]  [Save Changes]                  │
└───────────────────────────────────────────────────────┘
```

**Key Features**:
- **Toggle Built-in Patterns**: Enable/disable system patterns
- **Custom Pattern Builder**: Input + severity dropdown + optional reason
- **Pattern List**: Display custom patterns with edit/remove
- **Regex Validation**: Test pattern syntax before saving

**Backend Integration**:
```javascript
const patterns = await apiClient.getSettingsCategory('anti_patterns');
await apiClient.setSetting('anti_patterns.zero_tolerance.first_person_italics.enabled', true);
await apiClient.setSetting('anti_patterns.custom', [
  {pattern: "suddenly", severity: "formulaic", reason: "Overused surprise"}
]);
```

**Custom Pattern Modal**:
```
┌─ Add Custom Pattern ──────────────────────┐
│ Pattern:                                  │
│ ┌─────────────────────────────────────┐   │
│ │ suddenly                            │   │
│ └─────────────────────────────────────┘   │
│                                           │
│ Severity:                                 │
│ (○) Ignore  (●) Formulaic -1  (○) Zero -2 │
│                                           │
│ Reason (optional):                        │
│ ┌─────────────────────────────────────┐   │
│ │ Overused surprise word              │   │
│ └─────────────────────────────────────┘   │
│                                           │
│ [Test Pattern]  [Cancel]  [Add]           │
└───────────────────────────────────────────┘
```

**Regex Validation**:
```javascript
function validatePattern(pattern) {
  try {
    new RegExp(pattern);
    return { valid: true };
  } catch (e) {
    return { valid: false, error: e.message };
  }
}
```

**Edge Cases**:
- Invalid regex syntax
- Duplicate patterns
- Pattern matches empty string
- Pattern overlaps with built-in patterns

---

### Component 3: SettingsEnhancement.svelte (~180 lines)

**Purpose**: Configure enhancement pipeline thresholds
**Complexity**: MEDIUM (4 sliders + validation)
**Effort**: 2 hours

**UI Layout**:
```
┌─ Enhancement Pipeline ────────────────────────────────┐
│ Thresholds                                           │
│ Auto-Suggest Enhancement    85 █████████░  (70-95)   │
│ Action Prompt (Surgical)    85 █████████░  (80-95)   │
│ 6-Pass Full Enhancement     70 ███████░░░  (60-80)   │
│ Rewrite Recommended         60 ██████░░░░  (50-70)   │
│                                                       │
│ Aggressiveness:                                       │
│ (○) Conservative  (●) Medium  (○) Aggressive          │
│                                                       │
│ [Reset to Defaults]  [Save Changes]                  │
└───────────────────────────────────────────────────────┘
```

**Key Features**:
- **4 Threshold Sliders**: Auto, Action, 6-Pass, Rewrite
- **Logical Ordering Validation**: Rewrite < 6-Pass ≤ Action Prompt
- **Aggressiveness Radio**: Conservative/Medium/Aggressive
- **Visual Indicators**: Color-code score ranges

**Backend Integration**:
```javascript
const enh = await apiClient.getSettingsCategory('enhancement');
await apiClient.setSetting('enhancement.auto_threshold', 85);
await apiClient.setSetting('enhancement.aggressiveness', 'medium');
```

**Validation Logic**:
```javascript
function validateThresholds(auto, action, sixPass, rewrite) {
  const errors = [];

  if (rewrite >= sixPass) {
    errors.push("Rewrite threshold must be below 6-Pass threshold");
  }
  if (sixPass > action) {
    errors.push("6-Pass threshold cannot exceed Action Prompt threshold");
  }

  return errors;
}
```

**Edge Cases**:
- Thresholds overlap illogically
- Auto threshold = Action threshold (acceptable, but show tooltip)
- All thresholds at maximum (nothing will trigger enhancement)

---

### Component 4: SettingsTournament.svelte (~150 lines)

**Purpose**: Configure scene tournament behavior
**Complexity**: LOW (simple controls)
**Effort**: 2 hours

**UI Layout**:
```
┌─ Scene Tournament Settings ───────────────────────────┐
│ Variants per Agent          5 █████░░░░░  (3-10)     │
│                                                       │
│ Writing Strategies (5 selected)                       │
│ ☑ ACTION        - Action/conflict scenes             │
│ ☑ CHARACTER     - Psychology/interiority             │
│ ☑ DIALOGUE      - Conversation-heavy                 │
│ ☑ ATMOSPHERIC   - Setting/mood emphasis              │
│ ☑ BALANCED      - Even distribution                  │
│                                                       │
│ Display Options                                       │
│ ☑ Auto-score all variants                            │
│ ☑ Show losing variants                               │
│ Top N to highlight: 5                                 │
│                                                       │
│ [Reset to Defaults]  [Save Changes]                  │
└───────────────────────────────────────────────────────┘
```

**Backend Integration**:
```javascript
const tourn = await apiClient.getSettingsCategory('tournament');
await apiClient.setSetting('tournament.variants_per_agent', 5);
await apiClient.setSetting('tournament.strategies', ['ACTION', 'CHARACTER']);
```

**Edge Cases**:
- Must select at least 1 strategy
- Top N > total variants possible

---

### Component 5: SettingsForeman.svelte (~160 lines)

**Purpose**: Configure Foreman behavior
**Complexity**: LOW (dropdowns + toggle)
**Effort**: 2 hours

**UI Layout**:
```
┌─ The Foreman Behavior ────────────────────────────────┐
│ Proactiveness:                                        │
│ (○) Low  (●) Medium  (○) High                         │
│                                                       │
│ Challenge Intensity:                                  │
│ (○) Low  (●) Medium  (○) High                         │
│                                                       │
│ Explanation Verbosity:                                │
│ (○) Low  (●) Medium  (○) High                         │
│                                                       │
│ ☑ Auto-save decisions to Knowledge Base              │
│                                                       │
│ [Reset to Defaults]  [Save Changes]                  │
└───────────────────────────────────────────────────────┘
```

**Backend Integration**:
```javascript
const foreman = await apiClient.getSettingsCategory('foreman');
await apiClient.setSetting('foreman.proactiveness', 'medium');
await apiClient.setSetting('foreman.auto_kb_writes', true);
```

**Edge Cases**:
- All settings Low (warn user Foreman becomes passive)

---

### Component 6: SettingsContext.svelte (~140 lines)

**Purpose**: Advanced context window management
**Complexity**: LOW (sliders + radio)
**Effort**: 2 hours

**UI Layout**:
```
┌─ Context & Memory Management ─────────────────────────┐
│ Max Messages           20 ██████░░░░  (10-50)         │
│ KB Token Limit       1000 █████░░░░░  (500-2000)      │
│                                                       │
│ Voice Bundle Injection:                               │
│ (○) Minimal  (●) Summary  (○) Full                    │
│                                                       │
│ Previous Scenes: 3                                    │
│                                                       │
│ [Reset to Defaults]  [Save Changes]                  │
└───────────────────────────────────────────────────────┘
```

**Backend Integration**:
```javascript
const ctx = await apiClient.getSettingsCategory('context');
await apiClient.setSetting('context.max_conversation_history', 20);
await apiClient.setSetting('context.voice_bundle_injection', 'full');
```

**Edge Cases**:
- Calculate total context usage estimate
- Warn if exceeds model limits

---

## Shared UI Components

### SettingsSlider.svelte (~80 lines)
```svelte
<script>
  export let label = '';
  export let value = 0;
  export let min = 0;
  export let max = 100;
  export let step = 1;
  export let tooltip = '';
  export let unit = '';
</script>

<div class="setting-slider">
  <div class="slider-header">
    <label>{label}</label>
    <span class="value">{value}{unit}</span>
  </div>
  <input
    type="range"
    bind:value
    {min}
    {max}
    {step}
    title={tooltip}
  />
  <div class="slider-labels">
    <span>{min}</span>
    <span>{max}</span>
  </div>
</div>
```

### SettingsRadioGroup.svelte (~60 lines)
```svelte
<script>
  export let label = '';
  export let value = '';
  export let options = []; // [{value, label, description}]
</script>

<div class="radio-group">
  <label class="group-label">{label}</label>
  {#each options as option}
    <label class="radio-option">
      <input
        type="radio"
        bind:group={value}
        value={option.value}
      />
      <div class="option-content">
        <span class="option-label">{option.label}</span>
        {#if option.description}
          <span class="option-desc">{option.description}</span>
        {/if}
      </div>
    </label>
  {/each}
</div>
```

### SettingsToggle.svelte (~40 lines)
```svelte
<script>
  export let label = '';
  export let checked = false;
  export let description = '';
</script>

<label class="toggle">
  <input type="checkbox" bind:checked />
  <span class="toggle-switch"></span>
  <div class="toggle-label">
    <span>{label}</span>
    {#if description}
      <span class="description">{description}</span>
    {/if}
  </div>
</label>
```

### SettingsSection.svelte (~50 lines)
```svelte
<script>
  export let title = '';
  export let expanded = true;
</script>

<div class="settings-section" class:expanded>
  <button class="section-header" on:click={() => expanded = !expanded}>
    <span class="title">{title}</span>
    <span class="chevron">{expanded ? '▼' : '▶'}</span>
  </button>
  {#if expanded}
    <div class="section-content">
      <slot></slot>
    </div>
  {/if}
</div>
```

---

## Implementation Strategy

### Phase 1: Shared Components (2 hours)
1. Create SettingsSlider.svelte
2. Create SettingsRadioGroup.svelte
3. Create SettingsToggle.svelte
4. Create SettingsSection.svelte
5. Create utility functions (validateWeightsSum, loadPreset, etc.)

### Phase 2: High-Priority Components (8 hours)
1. SettingsScoring.svelte (~3h) - Linked slider logic
2. SettingsAntiPatterns.svelte (~3h) - Pattern builder
3. SettingsEnhancement.svelte (~2h) - Threshold validation

### Phase 3: Medium-Priority Components (6 hours)
4. SettingsTournament.svelte (~2h)
5. SettingsForeman.svelte (~2h)
6. SettingsContext.svelte (~2h)

### Phase 4: Integration & Polish (4 hours)
1. Update SettingsPanel.svelte navigation
2. Test project override indicators
3. Test export/import
4. Add loading states
5. Add confirmation dialogs
6. Responsive layout polish

---

## Technical Considerations

### State Management
- Local state until "Save Changes"
- Svelte stores for dirty tracking
- Navigation guard for unsaved changes

### Validation
- Client-side before API calls
- Server-side in SettingsService
- Inline error display (not toasts)

### Project Overrides
- Blue indicator when overriding global
- "Reset to Global" button
- Clear messaging

### Performance
- Debounce slider changes (300ms)
- Lazy load defaults
- Cache category data

### Accessibility
- Keyboard navigation
- ARIA labels
- High contrast support

---

## Testing Checklist

### Unit Tests (per component)
- [ ] Loads defaults correctly
- [ ] Saves successfully
- [ ] Validates ranges
- [ ] Handles errors
- [ ] Resets to defaults

### Integration Tests
- [ ] Settings persist across reloads
- [ ] Project overrides work
- [ ] Export/import roundtrip
- [ ] Changes affect scoring

### Edge Cases
- [ ] Concurrent edits
- [ ] Offline mode
- [ ] Invalid responses
- [ ] Preset collisions

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Linked slider complexity | High | Reusable component + tests |
| Regex validation false positives | Medium | "Test Pattern" button |
| Settings not reflected | High | Integration test |
| Lost unsaved changes | Medium | Navigation warning |
| Override confusion | Low | Visual indicators |

---

## Success Criteria

- [ ] All 6 components render
- [ ] Settings persist (global + project)
- [ ] Preset system works
- [ ] Custom patterns saveable
- [ ] Validation prevents invalid states
- [ ] Export/import works
- [ ] Design matches cyber-noir aesthetic
- [ ] Tooltips provide craft guidance
- [ ] Responsive layout

---

## Effort Breakdown

| Component | Complexity | Hours |
|-----------|-----------|-------|
| Shared UI | Medium | 2 |
| SettingsScoring | High | 3 |
| SettingsAntiPatterns | High | 3 |
| SettingsEnhancement | Medium | 2 |
| SettingsTournament | Low | 2 |
| SettingsForeman | Low | 2 |
| SettingsContext | Low | 2 |
| Integration | Medium | 4 |
| **Total** | | **20** |

---

**Document Version**: 1.0
**Created**: 2025-11-25
**Ready for Implementation**: Yes
**Dependencies Met**: Yes (Backend Phase 3C complete)
