<!--
  VoiceVariantGrid.svelte - Tournament Variants Display

  Displays 15-25 voice variants in a grid layout:
  - Rows: AI Agents
  - Columns: Writing Strategies (ACTION, CHARACTER, DIALOGUE, ATMOSPHERIC, BALANCED)

  Features:
  - Color-coded by agent
  - Strategy icons in headers
  - Score badges (if scored)
  - Click to preview variant
  - Multi-select for comparison
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import {
    tournamentVariants,
    selectedVariants,
    currentTournament
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let variants = [];
  export let showScores = false;
  export let selectionMode = 'single'; // 'single' | 'multi'

  // Strategy configuration
  const strategies = [
    { id: 'ACTION_EMPHASIS', name: 'Action', icon: 'bolt', color: '#f85149' },
    { id: 'CHARACTER_DEPTH', name: 'Character', icon: 'user', color: '#a371f7' },
    { id: 'DIALOGUE_FOCUS', name: 'Dialogue', icon: 'chat', color: '#58a6ff' },
    { id: 'ATMOSPHERIC', name: 'Atmospheric', icon: 'cloud', color: '#3fb950' },
    { id: 'BALANCED', name: 'Balanced', icon: 'scale', color: '#d29922' }
  ];

  // Agent colors
  const agentColors = {
    'claude': '#cc785c',
    'gpt': '#10a37f',
    'deepseek': '#0066ff',
    'qwen': '#6366f1',
    'ollama': '#888888'
  };

  // Get unique agents from variants
  $: agents = [...new Set(variants.map(v => v.agent_id))];

  // Create grid data structure
  $: gridData = createGridData(variants);

  function createGridData(variants) {
    const grid = {};
    agents.forEach(agentId => {
      grid[agentId] = {};
      strategies.forEach(strategy => {
        const variant = variants.find(
          v => v.agent_id === agentId && v.strategy === strategy.id
        );
        grid[agentId][strategy.id] = variant || null;
      });
    });
    return grid;
  }

  function getAgentColor(agentId) {
    const id = agentId.toLowerCase();
    for (const [key, color] of Object.entries(agentColors)) {
      if (id.includes(key)) return color;
    }
    return agentColors.ollama;
  }

  function getAgentName(agentId) {
    const variant = variants.find(v => v.agent_id === agentId);
    return variant?.agent_name || agentId;
  }

  function isSelected(variant) {
    if (!variant) return false;
    return $selectedVariants.some(
      v => v.agent_id === variant.agent_id && v.strategy === variant.strategy
    );
  }

  function handleVariantClick(variant) {
    if (!variant) return;

    if (selectionMode === 'single') {
      $selectedVariants = [variant];
      dispatch('select', { variant });
    } else {
      // Multi-select mode
      if (isSelected(variant)) {
        $selectedVariants = $selectedVariants.filter(
          v => !(v.agent_id === variant.agent_id && v.strategy === variant.strategy)
        );
      } else {
        if ($selectedVariants.length < 4) {
          $selectedVariants = [...$selectedVariants, variant];
        }
      }
      dispatch('selectionChange', { variants: $selectedVariants });
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
</script>

<div class="variant-grid-container">
  <!-- Grid Header -->
  <div class="grid-header">
    <div class="header-cell agent-header">
      <span class="agent-label">Agent</span>
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
    {#each agents as agentId}
      <div class="grid-row">
        <div class="row-header" style="--agent-color: {getAgentColor(agentId)}">
          <div class="agent-indicator"></div>
          <span class="agent-name">{getAgentName(agentId)}</span>
        </div>
        {#each strategies as strategy}
          {@const variant = gridData[agentId]?.[strategy.id]}
          <button
            class="variant-cell"
            class:empty={!variant}
            class:selected={isSelected(variant)}
            style="--strategy-color: {strategy.color}"
            on:click={() => handleVariantClick(variant)}
            disabled={!variant}
          >
            {#if variant}
              <div class="variant-content">
                <div class="variant-preview">
                  {truncateContent(variant.content)}
                </div>
                <div class="variant-footer">
                  <span class="word-count">{variant.word_count} words</span>
                  {#if showScores && variant.score}
                    <span class="score-badge" class:high={variant.score >= 85} class:medium={variant.score >= 70 && variant.score < 85}>
                      {variant.score}
                    </span>
                  {/if}
                </div>
              </div>
              <button class="expand-btn" on:click={(e) => previewVariant(variant, e)} title="Preview full text">
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

  <!-- Selection Info -->
  {#if selectionMode === 'multi' && $selectedVariants.length > 0}
    <div class="selection-bar">
      <span class="selection-count">{$selectedVariants.length} variant(s) selected</span>
      <button class="clear-btn" on:click={() => $selectedVariants = []}>
        Clear selection
      </button>
      <button class="compare-btn" on:click={() => dispatch('compare', { variants: $selectedVariants })} disabled={$selectedVariants.length < 2}>
        Compare Selected
      </button>
    </div>
  {/if}
</div>

<style>
  .variant-grid-container {
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-md, 6px);
    overflow: hidden;
  }

  /* Header */
  .grid-header {
    display: grid;
    grid-template-columns: 120px repeat(5, 1fr);
    gap: 1px;
    background: var(--border, #2d3a47);
  }

  .header-cell {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
  }

  .agent-header {
    display: flex;
    align-items: center;
  }

  .agent-label {
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

  /* Body */
  .grid-body {
    display: flex;
    flex-direction: column;
    gap: 1px;
    background: var(--border, #2d3a47);
  }

  .grid-row {
    display: grid;
    grid-template-columns: 120px repeat(5, 1fr);
    gap: 1px;
  }

  .row-header {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
  }

  .agent-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--agent-color);
    flex-shrink: 0;
  }

  .agent-name {
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
    min-height: 100px;
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

  .variant-cell.empty {
    cursor: default;
  }

  .variant-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    gap: var(--space-2, 8px);
  }

  .variant-preview {
    flex: 1;
    font-size: var(--text-xs, 11px);
    line-height: 1.4;
    color: var(--text-secondary, #8b949e);
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
  }

  .variant-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2, 8px);
  }

  .word-count {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .score-badge {
    padding: 2px 6px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-full, 9999px);
    font-size: 10px;
    font-weight: var(--font-semibold, 600);
    color: var(--text-secondary, #8b949e);
  }

  .score-badge.high {
    background: rgba(63, 185, 80, 0.2);
    color: var(--success, #3fb950);
  }

  .score-badge.medium {
    background: rgba(210, 153, 34, 0.2);
    color: var(--warning, #d29922);
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

  /* Selection bar */
  .selection-bar {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
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

  .compare-btn {
    margin-left: auto;
    padding: 6px 12px;
    background: var(--accent-cyan, #58a6ff);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--bg-primary, #0f1419);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .compare-btn:hover:not(:disabled) {
    filter: brightness(1.1);
  }

  .compare-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
