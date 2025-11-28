<!--
  Step3ApiKeys.svelte - API Keys Configuration (Optional)

  Purpose: Let users add their own API keys for premium models.
  Re-uses the existing SettingsAgents.svelte component.
-->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import SettingsAgents from '../Settings/SettingsAgents.svelte';

  const dispatch = createEventDispatcher();

  function handleBack() {
    dispatch('back');
  }

  function handleContinue() {
    dispatch('next');
  }

  function handleSkip() {
    dispatch('next');
  }
</script>

<div class="step-api-keys">
  <div class="step-header">
    <h2>Add API Keys</h2>
    <p class="step-description">
      Configure your API keys for premium cloud models. This step is optional.
    </p>
  </div>

  <!-- Embedded SettingsAgents Component -->
  <div class="settings-container">
    <SettingsAgents />
  </div>

  <!-- Navigation -->
  <div class="step-actions">
    <button class="btn-secondary" on:click={handleBack}>
      <span class="arrow">←</span>
      Back
    </button>
    <div class="right-buttons">
      <button class="btn-skip" on:click={handleSkip}>
        Skip for now
      </button>
      <button class="btn-primary" on:click={handleContinue}>
        Continue
        <span class="arrow">→</span>
      </button>
    </div>
  </div>
</div>

<style>
  .step-api-keys {
    max-width: 100%;
    margin: 0 auto;
  }

  .step-header {
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .step-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #ffffff;
  }

  .step-description {
    color: var(--text-secondary, #8b949e);
    margin: 0;
    font-size: 1rem;
  }

  /* Settings Container */
  .settings-container {
    max-height: 50vh;
    overflow-y: auto;
    margin-bottom: 1.5rem;
    padding: 0.5rem;
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 8px;
  }

  /* Override some SettingsAgents styles for the wizard context */
  .settings-container :global(.settings-agents) {
    padding: 1rem;
  }

  .settings-container :global(.header) {
    display: none; /* Hide the duplicate header */
  }

  .settings-container :global(.info-panel) {
    display: none; /* Hide the info panel - we have our own */
  }

  /* Navigation */
  .step-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .right-buttons {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-primary:hover {
    background: #00b8d9;
  }

  .btn-secondary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: var(--text-secondary, #8b949e);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 6px;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    background: var(--bg-tertiary, #242d38);
    border-color: var(--accent-cyan, #00d9ff);
    color: var(--accent-cyan, #00d9ff);
  }

  .btn-skip {
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: var(--text-secondary, #8b949e);
    border: none;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    transition: color 0.2s;
    text-decoration: underline;
    text-underline-offset: 2px;
  }

  .btn-skip:hover {
    color: #ffffff;
  }

  .arrow {
    font-size: 1.25rem;
  }

  /* Responsive */
  @media (max-width: 600px) {
    .step-actions {
      flex-direction: column;
      gap: 1rem;
    }

    .right-buttons {
      flex-direction: column;
      width: 100%;
    }

    .btn-primary, .btn-secondary {
      width: 100%;
      justify-content: center;
    }

    .btn-skip {
      order: 1;
    }
  }
</style>
