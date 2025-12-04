<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { slide } from 'svelte/transition';
  import RoleModelSelector from './RoleModelSelector.svelte';

  export let config: Record<string, string> = {}; // { default_model: '...', timeline_consistency: '...', ... }
  export let availableModels: any[] = [];
  export let disabled: boolean = false;

  const dispatch = createEventDispatcher();

  let isExpanded = false;

  const HEALTH_CHECKS = [
    { key: 'timeline_consistency', label: 'Timeline Consistency', desc: 'Checks for chronological errors and continuity' },
    { key: 'theme_resonance', label: 'Theme Resonance', desc: 'Analyzes thematic depth and symbol usage' },
    { key: 'flaw_challenges', label: 'Flaw Challenges', desc: 'Ensures protagonist flaw is tested' },
    { key: 'cast_function', label: 'Cast Function', desc: 'Verifies character purpose and voice' },
    { key: 'pacing_analysis', label: 'Pacing Analysis', desc: 'Detects tension plateaus and drag' },
    { key: 'beat_progress', label: 'Beat Progress', desc: 'Validates structural beat alignment' },
    { key: 'symbolic_layering', label: 'Symbolic Layering', desc: 'Checks for motif consistency' }
  ];

  function toggleExpand() {
    isExpanded = !isExpanded;
  }

  function handleModelSelect(key: string, modelId: string) {
    const newConfig = { ...config, [key]: modelId };
    dispatch('change', newConfig);
  }

  // Helper to check if a specific check is using the default model
  function isUsingDefault(key: string) {
    return !config[key] || config[key] === config.default_model;
  }
</script>

<div class="health-config">
  <div class="config-header">
    <div class="header-content">
      <h3>Health Checks</h3>
      <p class="subtitle">Configure models for structural and thematic analysis</p>
    </div>
    <button class="btn-toggle" on:click={toggleExpand}>
      {isExpanded ? 'Hide Individual Checks' : 'Show Individual Checks'}
    </button>
  </div>

  <div class="default-section">
    <RoleModelSelector
      role="default_model"
      label="Default Health Model"
      description="Used for all checks unless overridden below"
      currentModel={config.default_model || 'gpt-4o'}
      {availableModels}
      {disabled}
      on:select={(e) => handleModelSelect('default_model', e.detail.modelId)}
    />
  </div>

  {#if isExpanded}
    <div class="overrides-section" transition:slide>
      {#each HEALTH_CHECKS as check}
        <div class="check-row">
          <RoleModelSelector
            role={check.key}
            label={check.label}
            description={check.desc}
            currentModel={config[check.key] || config.default_model}
            {availableModels}
            {disabled}
            on:select={(e) => handleModelSelect(check.key, e.detail.modelId)}
          />
          {#if !isUsingDefault(check.key)}
            <button 
              class="btn-reset" 
              title="Reset to Default"
              on:click={() => handleModelSelect(check.key, config.default_model)}
              {disabled}
            >
              ↩
            </button>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .health-config {
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 8px;
    overflow: hidden;
    margin-top: 1rem;
  }

  .config-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem;
    background: #252525;
    border-bottom: 1px solid #404040;
  }

  .header-content h3 {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
    color: #ffffff;
  }

  .subtitle {
    margin: 0;
    font-size: 0.85rem;
    color: #888;
  }

  .btn-toggle {
    background: transparent;
    border: 1px solid #404040;
    color: #00d9ff;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-toggle:hover {
    background: #2d2d2d;
    border-color: #00d9ff;
  }

  .default-section {
    padding: 0.5rem;
  }

  .overrides-section {
    border-top: 1px solid #404040;
    background: #151515;
    padding: 0.5rem;
  }

  .check-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
  }

  .btn-reset {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    background: #2d2d2d;
    border: 1px solid #404040;
    color: #888;
    width: 24px;
    height: 24px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
    z-index: 10; /* Ensure it's above the selector click area if overlapping */
  }

  .btn-reset:hover {
    color: #00d9ff;
    border-color: #00d9ff;
  }
</style>
