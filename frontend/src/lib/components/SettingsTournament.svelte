<!--
  SettingsTournament.svelte - Scene Tournament Configuration

  Features:
  - Variants per agent slider
  - Writing strategy checkboxes
  - Display options toggles
-->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import SettingsSlider from './settings/SettingsSlider.svelte';
  import SettingsToggle from './settings/SettingsToggle.svelte';

  // Tournament settings
  let variantsPerAgent = 5;
  let strategies = ['ACTION', 'CHARACTER', 'DIALOGUE', 'ATMOSPHERIC', 'BALANCED'];
  let autoScoreVariants = true;
  let showLosingVariants = true;
  let topNDisplay = 5;

  // State
  let isLoading = true;
  let isSaving = false;
  let hasChanges = false;
  let originalValues = {};

  const allStrategies = [
    { value: 'ACTION', label: 'ACTION', description: 'Action/conflict-driven scenes' },
    { value: 'CHARACTER', label: 'CHARACTER', description: 'Psychology and interiority' },
    { value: 'DIALOGUE', label: 'DIALOGUE', description: 'Conversation-heavy scenes' },
    { value: 'ATMOSPHERIC', label: 'ATMOSPHERIC', description: 'Setting and mood emphasis' },
    { value: 'BALANCED', label: 'BALANCED', description: 'Even distribution' }
  ];

  onMount(async () => {
    await loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const settings = await apiClient.getSettingsCategory('tournament');

      variantsPerAgent = settings.variants_per_agent || 5;
      strategies = settings.strategies || ['ACTION', 'CHARACTER', 'DIALOGUE', 'ATMOSPHERIC', 'BALANCED'];
      autoScoreVariants = settings.auto_score_variants !== undefined ? settings.auto_score_variants : true;
      showLosingVariants = settings.show_losing_variants !== undefined ? settings.show_losing_variants : true;
      topNDisplay = settings.top_n_display || 5;

      originalValues = {
        variantsPerAgent,
        strategies: [...strategies],
        autoScoreVariants,
        showLosingVariants,
        topNDisplay
      };
    } catch (e) {
      console.error('Failed to load tournament settings:', e);
      addToast({ type: 'error', message: 'Failed to load settings' });
    } finally {
      isLoading = false;
    }
  }

  // Track changes
  $: {
    hasChanges =
      variantsPerAgent !== originalValues.variantsPerAgent ||
      JSON.stringify(strategies) !== JSON.stringify(originalValues.strategies) ||
      autoScoreVariants !== originalValues.autoScoreVariants ||
      showLosingVariants !== originalValues.showLosingVariants ||
      topNDisplay !== originalValues.topNDisplay;
  }

  function toggleStrategy(strategyValue) {
    if (strategies.includes(strategyValue)) {
      strategies = strategies.filter(s => s !== strategyValue);
    } else {
      strategies = [...strategies, strategyValue];
    }
  }

  async function saveSettings() {
    if (strategies.length === 0) {
      addToast({ type: 'error', message: 'At least one strategy must be selected' });
      return;
    }

    isSaving = true;
    try {
      await apiClient.setSetting('tournament.variants_per_agent', variantsPerAgent, 'tournament');
      await apiClient.setSetting('tournament.strategies', strategies, 'tournament');
      await apiClient.setSetting('tournament.auto_score_variants', autoScoreVariants, 'tournament');
      await apiClient.setSetting('tournament.show_losing_variants', showLosingVariants, 'tournament');
      await apiClient.setSetting('tournament.top_n_display', topNDisplay, 'tournament');

      originalValues = {
        variantsPerAgent,
        strategies: [...strategies],
        autoScoreVariants,
        showLosingVariants,
        topNDisplay
      };

      hasChanges = false;
      addToast({ type: 'success', message: 'Tournament settings saved' });
    } catch (e) {
      console.error('Failed to save tournament settings:', e);
      addToast({ type: 'error', message: 'Failed to save settings' });
    } finally {
      isSaving = false;
    }
  }

  async function resetToDefaults() {
    if (!confirm('Reset tournament settings to defaults?')) return;

    variantsPerAgent = 5;
    strategies = ['ACTION', 'CHARACTER', 'DIALOGUE', 'ATMOSPHERIC', 'BALANCED'];
    autoScoreVariants = true;
    showLosingVariants = true;
    topNDisplay = 5;

    await saveSettings();
  }
</script>

<div class="settings-tournament">
  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Variants Slider -->
    <SettingsSlider
      label="Variants per Agent"
      bind:value={variantsPerAgent}
      min={3}
      max={10}
      tooltip="How many scene variants each agent generates"
    />

    <!-- Writing Strategies -->
    <div class="section-header">
      <h4>Writing Strategies ({strategies.length} selected)</h4>
      <p class="section-desc">Which strategies agents use when generating scenes</p>
    </div>

    <div class="strategies-grid">
      {#each allStrategies as strategy}
        <label class="strategy-card" class:selected={strategies.includes(strategy.value)}>
          <input
            type="checkbox"
            checked={strategies.includes(strategy.value)}
            on:change={() => toggleStrategy(strategy.value)}
          />
          <div class="strategy-content">
            <span class="strategy-label">{strategy.label}</span>
            <span class="strategy-desc">{strategy.description}</span>
          </div>
        </label>
      {/each}
    </div>

    <!-- Display Options -->
    <div class="section-header">
      <h4>Display Options</h4>
    </div>

    <SettingsToggle
      bind:checked={autoScoreVariants}
      label="Auto-score all variants"
      description="Automatically run scoring on all generated variants"
    />

    <SettingsToggle
      bind:checked={showLosingVariants}
      label="Show losing variants"
      description="Display all variants, not just top N"
    />

    <SettingsSlider
      label="Top N to Highlight"
      bind:value={topNDisplay}
      min={3}
      max={10}
      tooltip="How many top variants to visually highlight"
      disabled={!showLosingVariants}
    />

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefaults} disabled={isSaving}>
        Reset to Defaults
      </button>
      <button class="btn-primary" on:click={saveSettings} disabled={!hasChanges || isSaving}>
        {isSaving ? 'Saving...' : 'Save Changes'}
      </button>
    </div>
  {/if}
</div>

<style>
  .settings-tournament {
    padding: 1rem 0;
  }

  .loading {
    text-align: center;
    color: var(--text-secondary, #8b949e);
    padding: 2rem;
  }

  .section-header {
    margin: 1.5rem 0 1rem 0;
  }

  .section-header h4 {
    margin: 0 0 0.25rem 0;
    font-size: 0.9375rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 600;
  }

  .section-desc {
    margin: 0;
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
  }

  .strategies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  .strategy-card {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg-tertiary, #242d38);
    border: 2px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .strategy-card:hover {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--accent-gold, #d4a574);
  }

  .strategy-card.selected {
    background: rgba(212, 165, 116, 0.1);
    border-color: var(--accent-gold, #d4a574);
  }

  .strategy-card input[type="checkbox"] {
    margin-top: 0.125rem;
    cursor: pointer;
  }

  .strategy-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    flex: 1;
  }

  .strategy-label {
    font-size: 0.875rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 600;
  }

  .strategy-desc {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    line-height: 1.4;
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
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
