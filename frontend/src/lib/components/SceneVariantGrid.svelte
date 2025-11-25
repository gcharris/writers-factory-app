<!--
  SceneVariantGrid.svelte - Director Mode Tournament Results

  Displays scene variants from multi-model tournament:
  - Rows: AI Models (Claude, GPT-4o, DeepSeek, etc.)
  - Columns: Writing Strategies (ACTION, CHARACTER, DIALOGUE, ATMOSPHERIC, BALANCED)

  Features:
  - 100-point score display with category breakdown
  - Color-coded by score tier (Gold 95+, Excellent 90+, Strong 85+, etc.)
  - Click to preview full scene
  - Multi-select for comparison or hybrid creation
  - Best variant highlighting
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    sceneVariants,
    selectedSceneVariants,
    sceneVariantsLoading,
    currentScaffold,
    selectedStructure
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let variants = [];
  export let showScores = true;
  export let selectionMode = 'multi'; // 'single' | 'multi'

  // Strategy configuration
  const strategies = [
    { id: 'ACTION_EMPHASIS', name: 'Action', icon: 'bolt', color: '#f85149' },
    { id: 'CHARACTER_DEPTH', name: 'Character', icon: 'user', color: '#a371f7' },
    { id: 'DIALOGUE_FOCUS', name: 'Dialogue', icon: 'chat', color: '#58a6ff' },
    { id: 'ATMOSPHERIC', name: 'Atmospheric', icon: 'cloud', color: '#3fb950' },
    { id: 'BALANCED', name: 'Balanced', icon: 'scale', color: '#d29922' }
  ];

  // Model colors
  const modelColors = {
    'claude': '#cc785c',
    'gpt': '#10a37f',
    'deepseek': '#0066ff',
    'qwen': '#6366f1',
    'gemini': '#4285f4',
    'ollama': '#888888'
  };

  // Score tier colors
  const scoreTiers = {
    gold: { min: 95, color: '#d4a574', label: 'Gold Standard' },
    excellent: { min: 90, color: '#3fb950', label: 'Excellent' },
    strong: { min: 85, color: '#58a6ff', label: 'Strong' },
    good: { min: 80, color: '#d29922', label: 'Good' },
    acceptable: { min: 75, color: '#8b949e', label: 'Acceptable' },
    weak: { min: 70, color: '#f85149', label: 'Needs Work' },
    fail: { min: 0, color: '#484f58', label: 'Regenerate' }
  };

  // Get unique models from variants
  $: models = [...new Set(variants.map(v => v.model))];

  // Find best variant
  $: bestVariant = variants.reduce((best, v) => {
    if (!best || (v.score && v.score > best.score)) return v;
    return best;
  }, null);

  // Create grid data structure
  $: gridData = createGridData(variants);

  function createGridData(variants) {
    const grid = {};
    models.forEach(model => {
      grid[model] = {};
      strategies.forEach(strategy => {
        const variant = variants.find(
          v => v.model === model && v.strategy === strategy.id
        );
        grid[model][strategy.id] = variant || null;
      });
    });
    return grid;
  }

  function getModelColor(model) {
    const m = model.toLowerCase();
    for (const [key, color] of Object.entries(modelColors)) {
      if (m.includes(key)) return color;
    }
    return modelColors.ollama;
  }

  function getModelName(model) {
    // Clean up model name for display
    return model.split('/').pop().split('-').slice(0, 2).join('-');
  }

  function getScoreTier(score) {
    if (!score) return scoreTiers.fail;
    for (const [key, tier] of Object.entries(scoreTiers)) {
      if (score >= tier.min) return tier;
    }
    return scoreTiers.fail;
  }

  function isSelected(variant) {
    if (!variant) return false;
    return $selectedSceneVariants.some(v => v.id === variant.id);
  }

  function isBestVariant(variant) {
    return variant && bestVariant && variant.id === bestVariant.id;
  }

  function handleVariantClick(variant) {
    if (!variant) return;

    if (selectionMode === 'single') {
      $selectedSceneVariants = [variant];
      dispatch('select', { variant });
    } else {
      // Multi-select mode (max 4 for comparison)
      if (isSelected(variant)) {
        $selectedSceneVariants = $selectedSceneVariants.filter(v => v.id !== variant.id);
      } else {
        if ($selectedSceneVariants.length < 4) {
          $selectedSceneVariants = [...$selectedSceneVariants, variant];
        }
      }
      dispatch('selectionChange', { variants: $selectedSceneVariants });
    }
  }

  function previewVariant(variant, event) {
    event.stopPropagation();
    dispatch('preview', { variant });
  }

  function truncateContent(content, maxLength = 120) {
    if (!content) return '';
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  }

  function selectBest() {
    if (bestVariant) {
      $selectedSceneVariants = [bestVariant];
      dispatch('select', { variant: bestVariant });
    }
  }

  function clearSelection() {
    $selectedSceneVariants = [];
  }

  function openComparison() {
    dispatch('compare', { variants: $selectedSceneVariants });
  }

  function createHybrid() {
    dispatch('hybrid', { variants: $selectedSceneVariants });
  }

  function proceedWithSelection() {
    dispatch('proceed', { variants: $selectedSceneVariants });
  }
</script>

<div class="scene-variant-grid">
  <!-- Header -->
  <div class="grid-header-bar">
    <div class="header-title">
      <h3>Scene Variants</h3>
      <span class="variant-count">{variants.length} variants generated</span>
    </div>
    {#if bestVariant}
      <button class="select-best-btn" on:click={selectBest}>
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        Select Best ({bestVariant.score || 0})
      </button>
    {/if}
  </div>

  <!-- Grid Container -->
  <div class="grid-container">
    <!-- Grid Header -->
    <div class="grid-header">
      <div class="header-cell model-header">
        <span class="model-label">Model</span>
      </div>
      {#each strategies as strategy}
        <div class="header-cell strategy-header" style="--strategy-color: {strategy.color}">
          <div class="strategy-icon">
            {#if strategy.icon === 'bolt'}
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M11 21h-1l1-7H7.5c-.88 0-.33-.75-.31-.78C8.48 10.94 10.42 7.54 13.01 3h1l-1 7h3.51c.4 0 .62.19.4.66C12.97 17.55 11 21 11 21z"/></svg>
            {:else if strategy.icon === 'user'}
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
            {:else if strategy.icon === 'chat'}
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
            {:else if strategy.icon === 'cloud'}
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"/></svg>
            {:else}
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9-4.03-9-9-9zm0 16c-3.86 0-7-3.14-7-7s3.14-7 7-7 7 3.14 7 7-3.14 7-7 7z"/><circle cx="12" cy="12" r="3"/></svg>
            {/if}
          </div>
          <span class="strategy-name">{strategy.name}</span>
        </div>
      {/each}
    </div>

    <!-- Grid Body -->
    <div class="grid-body">
      {#each models as model}
        <div class="grid-row">
          <div class="row-header" style="--model-color: {getModelColor(model)}">
            <div class="model-indicator"></div>
            <span class="model-name">{getModelName(model)}</span>
          </div>
          {#each strategies as strategy}
            {@const variant = gridData[model]?.[strategy.id]}
            {@const tier = variant ? getScoreTier(variant.score) : null}
            <button
              class="variant-cell"
              class:empty={!variant}
              class:selected={isSelected(variant)}
              class:best={isBestVariant(variant)}
              style="--strategy-color: {strategy.color}; --score-color: {tier?.color || '#484f58'}"
              on:click={() => handleVariantClick(variant)}
              disabled={!variant}
            >
              {#if variant}
                <div class="variant-content">
                  {#if showScores && variant.score}
                    <div class="score-header">
                      <span class="score-value" style="color: {tier.color}">{variant.score}</span>
                      {#if isBestVariant(variant)}
                        <span class="best-badge">
                          <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                          </svg>
                        </span>
                      {/if}
                    </div>
                  {/if}
                  <div class="variant-preview">
                    {truncateContent(variant.content)}
                  </div>
                  <div class="variant-footer">
                    <span class="word-count">{variant.word_count} words</span>
                    {#if tier}
                      <span class="tier-label" style="color: {tier.color}">{tier.label}</span>
                    {/if}
                  </div>
                </div>
                <button class="expand-btn" on:click={(e) => previewVariant(variant, e)} title="Preview full scene">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
                  </svg>
                </button>
                {#if isSelected(variant)}
                  <div class="selected-indicator">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                    </svg>
                  </div>
                {/if}
              {:else}
                <div class="empty-state">
                  <span>No variant</span>
                </div>
              {/if}
            </button>
          {/each}
        </div>
      {/each}
    </div>
  </div>

  <!-- Selection Bar -->
  {#if $selectedSceneVariants.length > 0}
    <div class="selection-bar">
      <div class="selection-info">
        <span class="selection-count">{$selectedSceneVariants.length} selected</span>
        <button class="clear-btn" on:click={clearSelection}>Clear</button>
      </div>
      <div class="selection-actions">
        {#if $selectedSceneVariants.length >= 2}
          <button class="action-btn" on:click={openComparison}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
            Compare
          </button>
          <button class="action-btn" on:click={createHybrid}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
            </svg>
            Create Hybrid
          </button>
        {/if}
        <button class="proceed-btn" on:click={proceedWithSelection}>
          Use Selection
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .scene-variant-grid {
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-md, 6px);
    overflow: hidden;
  }

  /* Header Bar */
  .grid-header-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .header-title {
    display: flex;
    align-items: baseline;
    gap: var(--space-2, 8px);
  }

  .header-title h3 {
    margin: 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .variant-count {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .select-best-btn {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: 4px 10px;
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.2));
    border: 1px solid var(--accent-gold, #d4a574);
    border-radius: var(--radius-full, 9999px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--accent-gold, #d4a574);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .select-best-btn:hover {
    background: var(--accent-gold, #d4a574);
    color: var(--bg-primary, #0f1419);
  }

  .select-best-btn svg {
    width: 12px;
    height: 12px;
  }

  /* Grid Container */
  .grid-container {
    overflow-x: auto;
  }

  /* Grid Header */
  .grid-header {
    display: grid;
    grid-template-columns: 100px repeat(5, 1fr);
    gap: 1px;
    background: var(--border, #2d3a47);
    min-width: 700px;
  }

  .header-cell {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
  }

  .model-header {
    display: flex;
    align-items: center;
  }

  .model-label {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .strategy-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1, 4px);
  }

  .strategy-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--strategy-color);
  }

  .strategy-icon svg {
    width: 16px;
    height: 16px;
  }

  .strategy-name {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
  }

  /* Grid Body */
  .grid-body {
    display: flex;
    flex-direction: column;
    gap: 1px;
    background: var(--border, #2d3a47);
    min-width: 700px;
  }

  .grid-row {
    display: grid;
    grid-template-columns: 100px repeat(5, 1fr);
    gap: 1px;
  }

  .row-header {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
  }

  .model-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--model-color);
    flex-shrink: 0;
  }

  .model-name {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* Variant Cell */
  .variant-cell {
    position: relative;
    min-height: 120px;
    padding: var(--space-2, 8px);
    background: var(--bg-secondary, #1a2027);
    border: none;
    text-align: left;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .variant-cell:hover:not(:disabled) {
    background: var(--bg-tertiary, #242d38);
  }

  .variant-cell.selected {
    background: rgba(88, 166, 255, 0.1);
    box-shadow: inset 0 0 0 2px var(--accent-cyan, #58a6ff);
  }

  .variant-cell.best {
    box-shadow: inset 0 0 0 2px var(--accent-gold, #d4a574);
  }

  .variant-cell.best.selected {
    box-shadow: inset 0 0 0 2px var(--accent-gold, #d4a574), inset 0 0 0 4px var(--accent-cyan, #58a6ff);
  }

  .variant-cell.empty {
    cursor: default;
  }

  .variant-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    gap: var(--space-1, 4px);
  }

  .score-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .score-value {
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-bold, 700);
  }

  .best-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    color: var(--accent-gold, #d4a574);
  }

  .best-badge svg {
    width: 14px;
    height: 14px;
  }

  .variant-preview {
    flex: 1;
    font-size: var(--text-xs, 11px);
    line-height: 1.4;
    color: var(--text-secondary, #8b949e);
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
  }

  .variant-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2, 8px);
    padding-top: var(--space-1, 4px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .word-count {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .tier-label {
    font-size: 9px;
    font-weight: var(--font-medium, 500);
    text-transform: uppercase;
  }

  /* Expand button */
  .expand-btn {
    position: absolute;
    top: var(--space-1, 4px);
    right: var(--space-1, 4px);
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-elevated, #2d3640);
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    opacity: 0;
    transition: all 0.15s ease;
  }

  .variant-cell:hover .expand-btn {
    opacity: 1;
  }

  .expand-btn:hover {
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  .expand-btn svg {
    width: 14px;
    height: 14px;
  }

  /* Selected indicator */
  .selected-indicator {
    position: absolute;
    bottom: var(--space-1, 4px);
    right: var(--space-1, 4px);
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-cyan, #58a6ff);
    border-radius: 50%;
    color: var(--bg-primary, #0f1419);
  }

  .selected-indicator svg {
    width: 12px;
    height: 12px;
  }

  /* Empty state */
  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  /* Selection Bar */
  .selection-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .selection-info {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .selection-count {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .clear-btn {
    padding: 4px 8px;
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .clear-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .selection-actions {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: 6px 12px;
    background: var(--bg-elevated, #2d3640);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .action-btn:hover {
    background: var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--accent-cyan, #58a6ff);
  }

  .action-btn svg {
    width: 14px;
    height: 14px;
  }

  .proceed-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: 6px 16px;
    background: var(--accent-gold, #d4a574);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--bg-primary, #0f1419);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .proceed-btn:hover {
    background: var(--accent-gold-hover, #e0b585);
  }

  .proceed-btn svg {
    width: 14px;
    height: 14px;
  }
</style>
