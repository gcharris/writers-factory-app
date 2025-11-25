<!--
  SettingsContext.svelte - Context & Memory Management Configuration

  Features:
  - Max conversation history slider
  - KB context limit slider
  - Voice bundle injection selection
  - Continuity context depth slider
-->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import SettingsSlider from './settings/SettingsSlider.svelte';
  import SettingsRadioGroup from './settings/SettingsRadioGroup.svelte';

  // Context settings
  let maxConversationHistory = 20;
  let kbContextLimit = 1000;
  let voiceBundleInjection = 'full';
  let continuityContextDepth = 3;

  // State
  let isLoading = true;
  let isSaving = false;
  let hasChanges = false;
  let originalValues = {};

  const voiceBundleOptions = [
    {
      value: 'minimal',
      label: 'Minimal',
      description: 'Just anti-patterns (smallest context)'
    },
    {
      value: 'summary',
      label: 'Summary',
      description: 'Core voice rules (balanced)'
    },
    {
      value: 'full',
      label: 'Full',
      description: 'Complete voice bundle (maximum guidance)'
    }
  ];

  // Estimated context usage
  $: estimatedTokens = calculateEstimatedTokens();

  onMount(async () => {
    await loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const settings = await apiClient.getSettingsCategory('context');

      maxConversationHistory = settings.max_conversation_history || 20;
      kbContextLimit = settings.kb_context_limit || 1000;
      voiceBundleInjection = settings.voice_bundle_injection || 'full';
      continuityContextDepth = settings.continuity_context_depth || 3;

      originalValues = {
        maxConversationHistory,
        kbContextLimit,
        voiceBundleInjection,
        continuityContextDepth
      };
    } catch (e) {
      console.error('Failed to load context settings:', e);
      addToast({ type: 'error', message: 'Failed to load settings' });
    } finally {
      isLoading = false;
    }
  }

  // Track changes
  $: {
    hasChanges =
      maxConversationHistory !== originalValues.maxConversationHistory ||
      kbContextLimit !== originalValues.kbContextLimit ||
      voiceBundleInjection !== originalValues.voiceBundleInjection ||
      continuityContextDepth !== originalValues.continuityContextDepth;
  }

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

  async function saveSettings() {
    isSaving = true;
    try {
      await apiClient.setSetting('context.max_conversation_history', maxConversationHistory, 'context');
      await apiClient.setSetting('context.kb_context_limit', kbContextLimit, 'context');
      await apiClient.setSetting('context.voice_bundle_injection', voiceBundleInjection, 'context');
      await apiClient.setSetting('context.continuity_context_depth', continuityContextDepth, 'context');

      originalValues = {
        maxConversationHistory,
        kbContextLimit,
        voiceBundleInjection,
        continuityContextDepth
      };

      hasChanges = false;
      addToast({ type: 'success', message: 'Context settings saved' });
    } catch (e) {
      console.error('Failed to save context settings:', e);
      addToast({ type: 'error', message: 'Failed to save settings' });
    } finally {
      isSaving = false;
    }
  }

  async function resetToDefaults() {
    if (!confirm('Reset context settings to defaults?')) return;

    maxConversationHistory = 20;
    kbContextLimit = 1000;
    voiceBundleInjection = 'full';
    continuityContextDepth = 3;

    await saveSettings();
  }
</script>

<div class="settings-context">
  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Conversation History -->
    <div class="section-header">
      <h4>Conversation History</h4>
      <p class="section-desc">How many recent messages The Foreman remembers</p>
    </div>

    <SettingsSlider
      label="Max Messages"
      bind:value={maxConversationHistory}
      min={10}
      max={50}
      tooltip="Number of recent conversation turns to keep in context"
    />

    <!-- Knowledge Base Context -->
    <div class="section-header">
      <h4>Knowledge Base Context</h4>
      <p class="section-desc">Tokens allocated to KB entries in prompts</p>
    </div>

    <SettingsSlider
      label="Token Limit"
      bind:value={kbContextLimit}
      min={500}
      max={2000}
      step={100}
      tooltip="Maximum tokens for KB context (character, world, constraints)"
    />

    <!-- Voice Bundle Injection -->
    <div class="section-header">
      <h4>Voice Bundle Injection</h4>
      <p class="section-desc">How much voice guidance to include in every prompt</p>
    </div>

    <SettingsRadioGroup
      bind:value={voiceBundleInjection}
      options={voiceBundleOptions}
    />

    <!-- Scene Continuity -->
    <div class="section-header">
      <h4>Scene Continuity</h4>
      <p class="section-desc">How many previous scenes to reference for continuity</p>
    </div>

    <SettingsSlider
      label="Previous Scenes"
      bind:value={continuityContextDepth}
      min={1}
      max={5}
      tooltip="Number of previous scenes included for context and consistency"
    />

    <!-- Estimated Usage -->
    <div class="usage-estimate">
      <div class="estimate-header">
        <span class="estimate-label">Estimated Total Context:</span>
        <span class="estimate-value">{estimatedTokens.toLocaleString()} tokens</span>
      </div>
      <div class="estimate-bar">
        <div class="estimate-fill" style="width: {Math.min((estimatedTokens / 8000) * 100, 100)}%"></div>
      </div>
      <div class="estimate-hint">
        Most models support 8,000+ tokens. Current settings use ~{Math.round((estimatedTokens / 8000) * 100)}% of typical limit.
      </div>
    </div>

    <!-- Info Note -->
    <div class="info-note">
      ⓘ Higher values provide more context but use more tokens. Lower values reduce costs but may miss important details.
    </div>

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
  .settings-context {
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

  .section-header:first-child {
    margin-top: 0;
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

  .usage-estimate {
    padding: 1rem;
    background: var(--bg-tertiary, #242d38);
    border-radius: 6px;
    margin: 1.5rem 0;
  }

  .estimate-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .estimate-label {
    font-size: 0.875rem;
    color: var(--text-secondary, #8b949e);
    font-weight: 500;
  }

  .estimate-value {
    font-size: 1rem;
    color: var(--accent-gold, #d4a574);
    font-weight: 700;
    font-family: 'Courier New', monospace;
  }

  .estimate-bar {
    height: 8px;
    background: var(--bg-elevated, #2d3640);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .estimate-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--success, #3fb950), var(--accent-cyan, #58a6ff));
    transition: width 0.3s ease;
  }

  .estimate-hint {
    font-size: 0.75rem;
    color: var(--text-muted, #6e7681);
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
