<!--
  SettingsForeman.svelte - Foreman Behavior Configuration

  Features:
  - Proactiveness level selection
  - Challenge intensity selection
  - Explanation verbosity selection
  - Auto-KB writes toggle
-->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import SettingsRadioGroup from './settings/SettingsRadioGroup.svelte';
  import SettingsToggle from './settings/SettingsToggle.svelte';

  // Foreman settings
  let proactiveness = 'medium';
  let challengeIntensity = 'medium';
  let explanationVerbosity = 'medium';
  let autoKBWrites = true;

  // State
  let isLoading = true;
  let isSaving = false;
  let hasChanges = false;
  let originalValues = {};

  const proactivenessOptions = [
    {
      value: 'low',
      label: 'Low',
      description: 'Responds when asked only. Minimal suggestions.'
    },
    {
      value: 'medium',
      label: 'Medium',
      description: 'Guides the process. Suggests next steps.'
    },
    {
      value: 'high',
      label: 'High',
      description: 'Directive. Proactive planning and suggestions.'
    }
  ];

  const challengeOptions = [
    {
      value: 'low',
      label: 'Low',
      description: 'Minimal pushback on decisions.'
    },
    {
      value: 'medium',
      label: 'Medium',
      description: 'Reasonable challenges on weak choices.'
    },
    {
      value: 'high',
      label: 'High',
      description: 'Strong challenges. Questions assumptions.'
    }
  ];

  const verbosityOptions = [
    {
      value: 'low',
      label: 'Low',
      description: 'Terse responses. Minimal explanation.'
    },
    {
      value: 'medium',
      label: 'Medium',
      description: 'Balanced explanations with key points.'
    },
    {
      value: 'high',
      label: 'High',
      description: 'Detailed craft reasoning and examples.'
    }
  ];

  onMount(async () => {
    await loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const settings = await apiClient.getSettingsCategory('foreman');

      proactiveness = settings.proactiveness || 'medium';
      challengeIntensity = settings.challenge_intensity || 'medium';
      explanationVerbosity = settings.explanation_verbosity || 'medium';
      autoKBWrites = settings.auto_kb_writes !== undefined ? settings.auto_kb_writes : true;

      originalValues = {
        proactiveness,
        challengeIntensity,
        explanationVerbosity,
        autoKBWrites
      };
    } catch (e) {
      console.error('Failed to load foreman settings:', e);
      addToast({ type: 'error', message: 'Failed to load settings' });
    } finally {
      isLoading = false;
    }
  }

  // Track changes
  $: {
    hasChanges =
      proactiveness !== originalValues.proactiveness ||
      challengeIntensity !== originalValues.challengeIntensity ||
      explanationVerbosity !== originalValues.explanationVerbosity ||
      autoKBWrites !== originalValues.autoKBWrites;
  }

  // Warning if all settings are low
  $: showLowWarning = proactiveness === 'low' && challengeIntensity === 'low' && explanationVerbosity === 'low';

  async function saveSettings() {
    isSaving = true;
    try {
      await apiClient.setSetting('foreman.proactiveness', proactiveness, 'foreman');
      await apiClient.setSetting('foreman.challenge_intensity', challengeIntensity, 'foreman');
      await apiClient.setSetting('foreman.explanation_verbosity', explanationVerbosity, 'foreman');
      await apiClient.setSetting('foreman.auto_kb_writes', autoKBWrites, 'foreman');

      originalValues = {
        proactiveness,
        challengeIntensity,
        explanationVerbosity,
        autoKBWrites
      };

      hasChanges = false;
      addToast({ type: 'success', message: 'Foreman settings saved' });
    } catch (e) {
      console.error('Failed to save foreman settings:', e);
      addToast({ type: 'error', message: 'Failed to save settings' });
    } finally {
      isSaving = false;
    }
  }

  async function resetToDefaults() {
    if (!confirm('Reset Foreman settings to defaults?')) return;

    proactiveness = 'medium';
    challengeIntensity = 'medium';
    explanationVerbosity = 'medium';
    autoKBWrites = true;

    await saveSettings();
  }
</script>

<div class="settings-foreman">
  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Proactiveness -->
    <SettingsRadioGroup
      label="Proactiveness"
      bind:value={proactiveness}
      options={proactivenessOptions}
    />

    <!-- Challenge Intensity -->
    <SettingsRadioGroup
      label="Challenge Intensity"
      bind:value={challengeIntensity}
      options={challengeOptions}
    />

    <!-- Explanation Verbosity -->
    <SettingsRadioGroup
      label="Explanation Verbosity"
      bind:value={explanationVerbosity}
      options={verbosityOptions}
    />

    <!-- Auto-KB Writes -->
    <div class="section-header">
      <h4>Automation</h4>
    </div>

    <SettingsToggle
      bind:checked={autoKBWrites}
      label="Auto-save decisions to Knowledge Base"
      description="Automatically capture creative decisions during conversations"
    />

    <!-- Warning for passive Foreman -->
    {#if showLowWarning}
      <div class="warning-note">
        ⚠ With all settings on Low, The Foreman becomes very passive. Consider increasing at least one setting for better guidance.
      </div>
    {/if}

    <!-- Info Note -->
    <div class="info-note">
      ⓘ These settings control The Foreman's personality and interaction style. Adjust based on how much guidance you want during the creative process.
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
  .settings-foreman {
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
    margin: 0;
    font-size: 0.9375rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 600;
  }

  .warning-note {
    font-size: 0.75rem;
    color: #ff9f43;
    padding: 0.75rem;
    background: rgba(255, 159, 67, 0.1);
    border-left: 3px solid #ff9f43;
    border-radius: 4px;
    margin-bottom: 1rem;
    line-height: 1.5;
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
