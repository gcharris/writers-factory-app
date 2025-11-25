<!--
  SettingsEnhancement.svelte - Enhancement Pipeline Configuration

  Features:
  - 4 threshold sliders (Auto, Action Prompt, 6-Pass, Rewrite)
  - Aggressiveness selection
  - Logical ordering validation
-->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import SettingsSlider from './settings/SettingsSlider.svelte';
  import SettingsRadioGroup from './settings/SettingsRadioGroup.svelte';

  // Thresholds
  let autoThreshold = 85;
  let actionPromptThreshold = 85;
  let sixPassThreshold = 70;
  let rewriteThreshold = 60;

  // Aggressiveness
  let aggressiveness = 'medium';

  // State
  let isLoading = true;
  let isSaving = false;
  let hasChanges = false;
  let originalValues = {};

  // Validation
  $: validationErrors = validateThresholds();
  $: isValid = validationErrors.length === 0;

  const aggressivenessOptions = [
    {
      value: 'conservative',
      label: 'Conservative',
      description: 'Minimal changes, preserve writer\'s voice'
    },
    {
      value: 'medium',
      label: 'Medium',
      description: 'Balanced polish with fixes'
    },
    {
      value: 'aggressive',
      label: 'Aggressive',
      description: 'Heavy optimization for score improvement'
    }
  ];

  onMount(async () => {
    await loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const settings = await apiClient.getSettingsCategory('enhancement');

      autoThreshold = settings.auto_threshold || 85;
      actionPromptThreshold = settings.action_prompt_threshold || 85;
      sixPassThreshold = settings.six_pass_threshold || 70;
      rewriteThreshold = settings.rewrite_threshold || 60;
      aggressiveness = settings.aggressiveness || 'medium';

      originalValues = {
        auto: autoThreshold,
        actionPrompt: actionPromptThreshold,
        sixPass: sixPassThreshold,
        rewrite: rewriteThreshold,
        aggressiveness
      };
    } catch (e) {
      console.error('Failed to load enhancement settings:', e);
      addToast({ type: 'error', message: 'Failed to load settings' });
    } finally {
      isLoading = false;
    }
  }

  // Track changes
  $: {
    hasChanges =
      autoThreshold !== originalValues.auto ||
      actionPromptThreshold !== originalValues.actionPrompt ||
      sixPassThreshold !== originalValues.sixPass ||
      rewriteThreshold !== originalValues.rewrite ||
      aggressiveness !== originalValues.aggressiveness;
  }

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

  async function saveSettings() {
    if (!isValid) {
      addToast({ type: 'error', message: validationErrors.join('. ') });
      return;
    }

    isSaving = true;
    try {
      await apiClient.setSetting('enhancement.auto_threshold', autoThreshold, 'enhancement');
      await apiClient.setSetting('enhancement.action_prompt_threshold', actionPromptThreshold, 'enhancement');
      await apiClient.setSetting('enhancement.six_pass_threshold', sixPassThreshold, 'enhancement');
      await apiClient.setSetting('enhancement.rewrite_threshold', rewriteThreshold, 'enhancement');
      await apiClient.setSetting('enhancement.aggressiveness', aggressiveness, 'enhancement');

      originalValues = {
        auto: autoThreshold,
        actionPrompt: actionPromptThreshold,
        sixPass: sixPassThreshold,
        rewrite: rewriteThreshold,
        aggressiveness
      };

      hasChanges = false;
      addToast({ type: 'success', message: 'Enhancement settings saved' });
    } catch (e) {
      console.error('Failed to save enhancement settings:', e);
      addToast({ type: 'error', message: 'Failed to save settings' });
    } finally {
      isSaving = false;
    }
  }

  async function resetToDefaults() {
    if (!confirm('Reset enhancement settings to defaults?')) return;

    autoThreshold = 85;
    actionPromptThreshold = 85;
    sixPassThreshold = 70;
    rewriteThreshold = 60;
    aggressiveness = 'medium';

    await saveSettings();
  }
</script>

<div class="settings-enhancement">
  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Thresholds Section -->
    <div class="section-header">
      <h4>Enhancement Thresholds</h4>
      <p class="section-desc">Score ranges that trigger different enhancement modes</p>
    </div>

    <div class="thresholds-section">
      <SettingsSlider
        label="Auto-Suggest Enhancement"
        bind:value={autoThreshold}
        min={70}
        max={95}
        tooltip="Score below which enhancement is automatically suggested"
      />

      <SettingsSlider
        label="Action Prompt (Surgical Fixes)"
        bind:value={actionPromptThreshold}
        min={80}
        max={95}
        tooltip="Score above which surgical OLD → NEW fixes are used (high-quality scenes)"
      />

      <SettingsSlider
        label="6-Pass Full Enhancement"
        bind:value={sixPassThreshold}
        min={60}
        max={80}
        tooltip="Score below which full 6-pass enhancement runs (medium-quality scenes)"
      />

      <SettingsSlider
        label="Rewrite Recommended"
        bind:value={rewriteThreshold}
        min={50}
        max={70}
        tooltip="Score below which rewrite is recommended (low-quality scenes)"
      />
    </div>

    <!-- Validation Errors -->
    {#if validationErrors.length > 0}
      <div class="validation-errors">
        {#each validationErrors as error}
          <div class="error-message">⚠ {error}</div>
        {/each}
      </div>
    {/if}

    <!-- Score Range Visual -->
    <div class="score-range-visual">
      <div class="range-bar">
        <div class="range-segment rewrite" style="width: {rewriteThreshold}%">
          <span class="range-label">Rewrite</span>
        </div>
        <div class="range-segment six-pass" style="width: {sixPassThreshold - rewriteThreshold}%">
          <span class="range-label">6-Pass</span>
        </div>
        <div class="range-segment action-prompt" style="width: {actionPromptThreshold - sixPassThreshold}%">
          <span class="range-label">Action</span>
        </div>
        <div class="range-segment no-enhance" style="width: {100 - actionPromptThreshold}%">
          <span class="range-label">No Enhance</span>
        </div>
      </div>
      <div class="range-axis">
        <span>0</span>
        <span>50</span>
        <span>100</span>
      </div>
    </div>

    <!-- Aggressiveness Section -->
    <div class="section-header">
      <h4>Enhancement Aggressiveness</h4>
      <p class="section-desc">How much the enhancer modifies your prose</p>
    </div>

    <SettingsRadioGroup
      bind:value={aggressiveness}
      options={aggressivenessOptions}
    />

    <!-- Info Note -->
    <div class="info-note">
      ⓘ Lower thresholds = more scenes enhanced. Higher aggressiveness = more changes per scene.
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefaults} disabled={isSaving}>
        Reset to Defaults
      </button>
      <button class="btn-primary" on:click={saveSettings} disabled={!hasChanges || !isValid || isSaving}>
        {isSaving ? 'Saving...' : 'Save Changes'}
      </button>
    </div>
  {/if}
</div>

<style>
  .settings-enhancement {
    padding: 1rem 0;
  }

  .loading {
    text-align: center;
    color: var(--text-secondary, #8b949e);
    padding: 2rem;
  }

  .section-header {
    margin-bottom: 1rem;
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

  .thresholds-section {
    margin-bottom: 1.5rem;
  }

  .validation-errors {
    margin-bottom: 1rem;
  }

  .error-message {
    padding: 0.75rem;
    background: rgba(248, 81, 73, 0.1);
    border-left: 3px solid var(--danger, #f85149);
    border-radius: 4px;
    color: var(--danger, #f85149);
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
  }

  .score-range-visual {
    margin: 1.5rem 0;
    padding: 1rem;
    background: var(--bg-tertiary, #242d38);
    border-radius: 6px;
  }

  .range-bar {
    display: flex;
    height: 40px;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .range-segment {
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    transition: width 0.3s ease;
  }

  .range-segment.rewrite {
    background: #f85149;
  }

  .range-segment.six-pass {
    background: #ff9f43;
  }

  .range-segment.action-prompt {
    background: var(--accent-cyan, #58a6ff);
  }

  .range-segment.no-enhance {
    background: var(--success, #3fb950);
  }

  .range-label {
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  }

  .range-axis {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: var(--text-muted, #6e7681);
    padding: 0 0.25rem;
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
