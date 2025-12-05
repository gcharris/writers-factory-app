<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { fade } from 'svelte/transition';

  export let role: string;
  export let label: string;
  export let description: string;
  export let currentModel: string;
  export let availableModels: any[] = []; // Typed as any[] for flexibility, expects TournamentModel structure
  export let showCost: boolean = true;
  export let disabled: boolean = false;

  const dispatch = createEventDispatcher();

  let isOpen = false;

  // Find the selected model object
  $: selectedModelObj = availableModels.find(m => m.id === currentModel) || availableModels[0];

  function toggleDropdown() {
    if (!disabled) {
      isOpen = !isOpen;
    }
  }

  function selectModel(modelId: string) {
    dispatch('select', { role, modelId });
    isOpen = false;
  }

  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (isOpen && !target.closest('.role-selector')) {
      isOpen = false;
    }
  }

  function getTierColor(tier: string) {
    switch (tier) {
      case 'budget': return '#00ff88'; // Green
      case 'balanced': return '#00d9ff'; // Cyan
      case 'premium': return '#bd93f9'; // Purple
      default: return '#888';
    }
  }

  function getTierLabel(tier: string) {
    return tier.charAt(0).toUpperCase() + tier.slice(1);
  }
</script>

<svelte:window on:click={handleClickOutside} />

<div class="role-selector" class:disabled>
  <div class="role-info">
    <div class="role-header">
      <span class="role-label">{label}</span>
      {#if showCost && selectedModelObj && selectedModelObj.cost_per_1m_tokens != null}
        <span class="role-cost" title="Cost per 1M tokens">
          ${selectedModelObj.cost_per_1m_tokens.toFixed(2)}/1M
        </span>
      {/if}
    </div>
    <p class="role-description">{description}</p>
  </div>

  <div class="selector-container">
    <button class="selector-button" on:click|stopPropagation={toggleDropdown} {disabled}>
      {#if selectedModelObj}
        <div class="selected-model">
          <span class="model-name">{selectedModelObj.name}</span>
          <span class="model-tier" style="color: {getTierColor(selectedModelObj.quality_tier)}">
            {getTierLabel(selectedModelObj.quality_tier)}
          </span>
        </div>
      {:else}
        <span class="placeholder">Select Model...</span>
      {/if}
      <span class="chevron" class:open={isOpen}>▼</span>
    </button>

    {#if isOpen}
      <div class="dropdown-menu" transition:fade={{ duration: 100 }}>
        {#each availableModels as model}
          <button
            class="dropdown-item"
            class:selected={model.id === currentModel}
            class:unavailable={!model.is_active}
            disabled={!model.is_active}
            on:click|stopPropagation={() => selectModel(model.id)}
          >
            <div class="model-info">
              <span class="item-name">{model.name}</span>
              <span class="item-provider">{model.provider}</span>
            </div>
            <div class="model-meta">
              <span class="item-tier" style="color: {getTierColor(model.quality_tier)}">
                {getTierLabel(model.quality_tier)}
              </span>
              {#if !model.is_active}
                <span class="lock-icon" title="Missing API Key">🔒</span>
              {/if}
            </div>
          </button>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .role-selector {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 8px;
    gap: 1.5rem;
    transition: border-color 0.2s;
  }

  .role-selector:hover {
    border-color: #505050;
  }

  .role-selector.disabled {
    opacity: 0.6;
    pointer-events: none;
  }

  .role-info {
    flex: 1;
    min-width: 0;
  }

  .role-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.25rem;
  }

  .role-label {
    font-weight: 600;
    color: #ffffff;
    font-size: 0.95rem;
  }

  .role-cost {
    font-size: 0.75rem;
    color: #888;
    background: #2d2d2d;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
  }

  .role-description {
    margin: 0;
    font-size: 0.85rem;
    color: #b0b0b0;
    line-height: 1.4;
  }

  .selector-container {
    position: relative;
    width: 240px;
    flex-shrink: 0;
  }

  .selector-button {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.625rem 0.875rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 6px;
    color: #ffffff;
    cursor: pointer;
    transition: all 0.2s;
  }

  .selector-button:hover:not(:disabled) {
    border-color: #00d9ff;
    background: #333;
  }

  .selector-button:disabled {
    cursor: not-allowed;
    opacity: 0.7;
  }

  .selected-model {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .model-name {
    font-size: 0.9rem;
    font-weight: 500;
  }

  .model-tier {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .chevron {
    font-size: 0.75rem;
    color: #888;
    transition: transform 0.2s;
  }

  .chevron.open {
    transform: rotate(180deg);
  }

  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin-top: 0.5rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    z-index: 100;
    max-height: 300px;
    overflow-y: auto;
  }

  .dropdown-item {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: transparent;
    border: none;
    border-bottom: 1px solid #404040;
    color: #ffffff;
    cursor: pointer;
    text-align: left;
    transition: background 0.2s;
  }

  .dropdown-item:last-child {
    border-bottom: none;
  }

  .dropdown-item:hover:not(:disabled) {
    background: #3a3a3a;
  }

  .dropdown-item.selected {
    background: #1a3a4a;
    border-left: 3px solid #00d9ff;
  }

  .dropdown-item.unavailable {
    opacity: 0.5;
    cursor: not-allowed;
    background: #252525;
  }

  .model-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .item-name {
    font-size: 0.9rem;
    font-weight: 500;
  }

  .item-provider {
    font-size: 0.75rem;
    color: #888;
  }

  .model-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
  }

  .item-tier {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .lock-icon {
    font-size: 0.8rem;
  }
</style>
