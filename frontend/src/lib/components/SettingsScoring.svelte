<!--
  SettingsScoring.svelte - Scoring Rubric Weights Configuration

  Features:
  - 5 linked sliders (must sum to 100)
  - Preset system (Literary Fiction, Thriller, Romance, Balanced)
  - Real-time validation
  - Project override support
-->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import SettingsSlider from './settings/SettingsSlider.svelte';

  // Slider values
  let voiceWeight = 30;
  let characterWeight = 20;
  let metaphorWeight = 20;
  let antiPatternWeight = 15;
  let phaseWeight = 15;

  // Preset selection
  let selectedPreset = 'balanced';

  // State
  let isLoading = true;
  let isSaving = false;
  let hasChanges = false;
  let originalValues = {};

  // Presets
  const PRESETS = {
    balanced: {
      name: 'Balanced (Default)',
      voice: 30,
      character: 20,
      metaphor: 20,
      antiPattern: 15,
      phase: 15
    },
    literary_fiction: {
      name: 'Literary Fiction',
      voice: 40,
      character: 25,
      metaphor: 15,
      antiPattern: 10,
      phase: 10
    },
    commercial_thriller: {
      name: 'Commercial Thriller',
      voice: 25,
      character: 20,
      metaphor: 15,
      antiPattern: 25,
      phase: 15
    },
    genre_romance: {
      name: 'Genre Romance',
      voice: 20,
      character: 30,
      metaphor: 20,
      antiPattern: 15,
      phase: 15
    }
  };

  // Computed total
  $: total = voiceWeight + characterWeight + metaphorWeight + antiPatternWeight + phaseWeight;
  $: isValid = total === 100;

  // Track changes
  $: {
    hasChanges =
      voiceWeight !== originalValues.voice ||
      characterWeight !== originalValues.character ||
      metaphorWeight !== originalValues.metaphor ||
      antiPatternWeight !== originalValues.antiPattern ||
      phaseWeight !== originalValues.phase;
  }

  onMount(async () => {
    await loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const settings = await apiClient.getSettingsCategory('scoring');

      voiceWeight = settings.voice_authenticity_weight || 30;
      characterWeight = settings.character_consistency_weight || 20;
      metaphorWeight = settings.metaphor_discipline_weight || 20;
      antiPatternWeight = settings.anti_pattern_compliance_weight || 15;
      phaseWeight = settings.phase_appropriateness_weight || 15;

      originalValues = {
        voice: voiceWeight,
        character: characterWeight,
        metaphor: metaphorWeight,
        antiPattern: antiPatternWeight,
        phase: phaseWeight
      };

      // Detect which preset is active
      detectPreset();
    } catch (e) {
      console.error('Failed to load scoring settings:', e);
      addToast({ type: 'error', message: 'Failed to load settings' });
    } finally {
      isLoading = false;
    }
  }

  function detectPreset() {
    for (const [key, preset] of Object.entries(PRESETS)) {
      if (
        voiceWeight === preset.voice &&
        characterWeight === preset.character &&
        metaphorWeight === preset.metaphor &&
        antiPatternWeight === preset.antiPattern &&
        phaseWeight === preset.phase
      ) {
        selectedPreset = key;
        return;
      }
    }
    selectedPreset = 'custom';
  }

  function applyPreset(presetKey) {
    if (presetKey === 'custom') return;

    const preset = PRESETS[presetKey];
    voiceWeight = preset.voice;
    characterWeight = preset.character;
    metaphorWeight = preset.metaphor;
    antiPatternWeight = preset.antiPattern;
    phaseWeight = preset.phase;
    selectedPreset = presetKey;
  }

  // Linked slider logic - redistribute proportionally
  function handleSliderChange(changedKey, newValue) {
    const sliders = {
      voice: { value: voiceWeight, min: 10, max: 50 },
      character: { value: characterWeight, min: 10, max: 30 },
      metaphor: { value: metaphorWeight, min: 10, max: 30 },
      antiPattern: { value: antiPatternWeight, min: 5, max: 25 },
      phase: { value: phaseWeight, min: 5, max: 25 }
    };

    // Update the changed slider
    sliders[changedKey].value = newValue;

    // Calculate remaining points to distribute
    const remaining = 100 - newValue;

    // Get other sliders
    const others = Object.entries(sliders).filter(([key]) => key !== changedKey);

    // Calculate current sum of other sliders
    const currentSum = others.reduce((sum, [_, slider]) => sum + slider.value, 0);

    if (currentSum === 0) {
      // Edge case: all others are 0, distribute evenly
      const perSlider = Math.floor(remaining / others.length);
      others.forEach(([key, slider], i) => {
        slider.value = i === others.length - 1 ? remaining - (perSlider * (others.length - 1)) : perSlider;
      });
    } else {
      // Proportionally redistribute
      others.forEach(([key, slider]) => {
        const proportion = slider.value / currentSum;
        slider.value = Math.round(remaining * proportion);
      });

      // Fix rounding errors - adjust largest slider
      const actualSum = newValue + others.reduce((sum, [_, slider]) => sum + slider.value, 0);
      if (actualSum !== 100) {
        const largest = others.reduce((max, current) =>
          current[1].value > max[1].value ? current : max
        );
        largest[1].value += (100 - actualSum);
      }
    }

    // Apply the new values
    voiceWeight = sliders.voice.value;
    characterWeight = sliders.character.value;
    metaphorWeight = sliders.metaphor.value;
    antiPatternWeight = sliders.antiPattern.value;
    phaseWeight = sliders.phase.value;

    // Check if still matches a preset
    detectPreset();
  }

  async function saveSettings() {
    if (!isValid) {
      addToast({ type: 'error', message: 'Weights must sum to 100' });
      return;
    }

    isSaving = true;
    try {
      await apiClient.setSetting('scoring.voice_authenticity_weight', voiceWeight, 'scoring');
      await apiClient.setSetting('scoring.character_consistency_weight', characterWeight, 'scoring');
      await apiClient.setSetting('scoring.metaphor_discipline_weight', metaphorWeight, 'scoring');
      await apiClient.setSetting('scoring.anti_pattern_compliance_weight', antiPatternWeight, 'scoring');
      await apiClient.setSetting('scoring.phase_appropriateness_weight', phaseWeight, 'scoring');

      originalValues = {
        voice: voiceWeight,
        character: characterWeight,
        metaphor: metaphorWeight,
        antiPattern: antiPatternWeight,
        phase: phaseWeight
      };

      hasChanges = false;
      addToast({ type: 'success', message: 'Scoring settings saved' });
    } catch (e) {
      console.error('Failed to save scoring settings:', e);
      addToast({ type: 'error', message: 'Failed to save settings' });
    } finally {
      isSaving = false;
    }
  }

  async function resetToDefaults() {
    if (!confirm('Reset scoring weights to defaults (Balanced preset)?')) return;

    const preset = PRESETS.balanced;
    voiceWeight = preset.voice;
    characterWeight = preset.character;
    metaphorWeight = preset.metaphor;
    antiPatternWeight = preset.antiPattern;
    phaseWeight = preset.phase;
    selectedPreset = 'balanced';

    await saveSettings();
  }
</script>

<div class="settings-scoring">
  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Preset Selection -->
    <div class="preset-section">
      <label for="preset-select">Preset:</label>
      <select
        id="preset-select"
        bind:value={selectedPreset}
        on:change={(e) => applyPreset(e.target.value)}
      >
        {#each Object.entries(PRESETS) as [key, preset]}
          <option value={key}>{preset.name}</option>
        {/each}
        <option value="custom">Custom</option>
      </select>
    </div>

    <!-- Scoring Weights -->
    <div class="weights-section">
      <SettingsSlider
        label="Voice Authenticity"
        bind:value={voiceWeight}
        min={10}
        max={50}
        tooltip="How heavily to penalize AI-sounding prose and explanation"
        on:change={() => handleSliderChange('voice', voiceWeight)}
      />

      <SettingsSlider
        label="Character Consistency"
        bind:value={characterWeight}
        min={10}
        max={30}
        tooltip="Psychology, capability, and relationship alignment"
        on:change={() => handleSliderChange('character', characterWeight)}
      />

      <SettingsSlider
        label="Metaphor Discipline"
        bind:value={metaphorWeight}
        min={10}
        max={30}
        tooltip="Domain rotation and transformation quality"
        on:change={() => handleSliderChange('metaphor', metaphorWeight)}
      />

      <SettingsSlider
        label="Anti-Pattern Compliance"
        bind:value={antiPatternWeight}
        min={5}
        max={25}
        tooltip="Pattern avoidance strictness"
        on:change={() => handleSliderChange('antiPattern', antiPatternWeight)}
      />

      <SettingsSlider
        label="Phase Appropriateness"
        bind:value={phaseWeight}
        min={5}
        max={25}
        tooltip="Voice complexity matching story phase"
        on:change={() => handleSliderChange('phase', phaseWeight)}
      />
    </div>

    <!-- Total Display -->
    <div class="total-section" class:invalid={!isValid}>
      <span class="total-label">Total:</span>
      <span class="total-value">{total}/100</span>
      {#if !isValid}
        <span class="error-icon">⚠</span>
      {:else}
        <span class="success-icon">✓</span>
      {/if}
    </div>

    <!-- Info Note -->
    <div class="info-note">
      ⓘ Changes affect all future scene scoring. Higher weights increase impact on final score.
    </div>

    <!-- Actions -->
    <div class="actions">
      <button
        class="btn-secondary"
        on:click={resetToDefaults}
        disabled={isSaving}
      >
        Reset to Defaults
      </button>
      <button
        class="btn-primary"
        on:click={saveSettings}
        disabled={!hasChanges || !isValid || isSaving}
      >
        {isSaving ? 'Saving...' : 'Save Changes'}
      </button>
    </div>
  {/if}
</div>

<style>
  .settings-scoring {
    padding: 1rem 0;
  }

  .loading {
    text-align: center;
    color: var(--text-secondary, #8b949e);
    padding: 2rem;
  }

  .preset-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding: 0.75rem;
    background: var(--bg-tertiary, #242d38);
    border-radius: 6px;
  }

  .preset-section label {
    font-size: 0.875rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 500;
  }

  .preset-section select {
    flex: 1;
    padding: 0.5rem;
    background: var(--bg-elevated, #2d3640);
    border: 1px solid var(--text-muted, #6e7681);
    border-radius: 4px;
    color: var(--text-primary, #e6edf3);
    font-size: 0.875rem;
    cursor: pointer;
  }

  .preset-section select:focus {
    outline: none;
    border-color: var(--accent-gold, #d4a574);
  }

  .weights-section {
    margin-bottom: 1.5rem;
  }

  .total-section {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: var(--bg-tertiary, #242d38);
    border: 2px solid var(--success, #3fb950);
    border-radius: 6px;
    margin-bottom: 1rem;
  }

  .total-section.invalid {
    border-color: var(--danger, #f85149);
    background: rgba(248, 81, 73, 0.1);
  }

  .total-label {
    font-size: 0.875rem;
    color: var(--text-secondary, #8b949e);
    font-weight: 500;
  }

  .total-value {
    font-size: 1.25rem;
    color: var(--accent-gold, #d4a574);
    font-weight: 700;
    font-family: 'Courier New', monospace;
  }

  .success-icon {
    margin-left: auto;
    color: var(--success, #3fb950);
    font-size: 1.25rem;
  }

  .error-icon {
    margin-left: auto;
    color: var(--danger, #f85149);
    font-size: 1.25rem;
  }

  .info-note {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    padding: 0.75rem;
    background: rgba(88, 166, 255, 0.1);
    border-left: 3px solid var(--accent-cyan, #58a6ff);
    border-radius: 4px;
    margin-bottom: 1.5rem;
    line-height: 1.5;
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.625rem 1.25rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    border: none;
  }

  .btn-primary {
    background: var(--accent-gold, #d4a574);
    color: var(--bg-primary, #0f1419);
  }

  .btn-primary:hover:not(:disabled) {
    background: #e0b584;
    transform: translateY(-1px);
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
    border: 1px solid var(--text-muted, #6e7681);
  }

  .btn-secondary:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--accent-gold, #d4a574);
  }

  .btn-secondary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
