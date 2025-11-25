<!--
  VoiceComparisonView.svelte - Side-by-Side Variant Comparison

  Features:
  - Compare 2-4 variants side by side
  - Highlight differences between variants
  - Show strategy and agent info for each
  - Score breakdown (if available)
  - Quick select winner from comparison
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { selectedVariants } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let variants = [];
  export let showScores = false;

  // Strategy colors
  const strategyColors = {
    'ACTION_EMPHASIS': '#f85149',
    'CHARACTER_DEPTH': '#a371f7',
    'DIALOGUE_FOCUS': '#58a6ff',
    'BRAINSTORMING': '#3fb950',
    'BALANCED': '#d29922'
  };

  // Agent colors
  const agentColors = {
    'claude': '#cc785c',
    'gpt': '#10a37f',
    'deepseek': '#0066ff',
    'qwen': '#6366f1',
    'ollama': '#888888'
  };

  function getAgentColor(agentId) {
    const id = agentId.toLowerCase();
    for (const [key, color] of Object.entries(agentColors)) {
      if (id.includes(key)) return color;
    }
    return agentColors.ollama;
  }

  function getStrategyColor(strategy) {
    return strategyColors[strategy] || '#8b949e';
  }

  function formatStrategy(strategy) {
    return strategy
      .replace('_EMPHASIS', '')
      .replace('_DEPTH', '')
      .replace('_FOCUS', '')
      .split('_')
      .map(w => w.charAt(0) + w.slice(1).toLowerCase())
      .join(' ');
  }

  function selectWinner(variant) {
    dispatch('selectWinner', { variant });
  }

  function removeFromComparison(variant) {
    $selectedVariants = $selectedVariants.filter(
      v => !(v.agent_id === variant.agent_id && v.strategy === variant.strategy)
    );
    dispatch('remove', { variant });
  }

  function handleClose() {
    dispatch('close');
  }

  // Split content into paragraphs for better display
  function getParagraphs(content) {
    if (!content) return [];
    return content.split('\n\n').filter(p => p.trim());
  }
</script>

<div class="comparison-container">
  <div class="comparison-header">
    <h3 class="comparison-title">Compare Variants</h3>
    <span class="variant-count">{variants.length} variants</span>
    <button class="close-btn" on:click={handleClose}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 6L6 18M6 6l12 12"/>
      </svg>
    </button>
  </div>

  <div class="comparison-body" style="--column-count: {variants.length}">
    {#each variants as variant, index}
      <div class="variant-column">
        <!-- Column Header -->
        <div class="column-header" style="--agent-color: {getAgentColor(variant.agent_id)}">
          <div class="agent-badge">
            <span class="agent-indicator"></span>
            <span class="agent-name">{variant.agent_name}</span>
          </div>
          <div
            class="strategy-badge"
            style="--strategy-color: {getStrategyColor(variant.strategy)}"
          >
            {formatStrategy(variant.strategy)}
          </div>
          <button
            class="remove-btn"
            on:click={() => removeFromComparison(variant)}
            title="Remove from comparison"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Variant Content -->
        <div class="column-content">
          <div class="content-scroll">
            {#each getParagraphs(variant.content) as paragraph}
              <p class="prose-paragraph">{paragraph}</p>
            {/each}
          </div>
        </div>

        <!-- Column Footer -->
        <div class="column-footer">
          <div class="meta-info">
            <span class="word-count">{variant.word_count} words</span>
            {#if showScores && variant.score}
              <span
                class="score"
                class:high={variant.score >= 85}
                class:medium={variant.score >= 70 && variant.score < 85}
                class:low={variant.score < 70}
              >
                Score: {variant.score}
              </span>
            {/if}
          </div>
          <button
            class="select-winner-btn"
            on:click={() => selectWinner(variant)}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 13l4 4L19 7"/>
            </svg>
            Select Winner
          </button>
        </div>
      </div>
    {/each}
  </div>

  {#if variants.length < 2}
    <div class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
      <p>Select at least 2 variants from the grid to compare</p>
    </div>
  {/if}
</div>

<style>
  .comparison-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-lg, 8px);
    overflow: hidden;
  }

  .comparison-header {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .comparison-title {
    margin: 0;
    font-size: var(--text-md, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .variant-count {
    padding: 2px 8px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-full, 9999px);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .close-btn {
    margin-left: auto;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .close-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .close-btn svg {
    width: 16px;
    height: 16px;
  }

  /* Comparison Body */
  .comparison-body {
    display: grid;
    grid-template-columns: repeat(var(--column-count, 2), 1fr);
    gap: 1px;
    flex: 1;
    min-height: 0;
    background: var(--border, #2d3a47);
  }

  .variant-column {
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary, #1a2027);
  }

  /* Column Header */
  .column-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .agent-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .agent-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--agent-color);
  }

  .agent-name {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .strategy-badge {
    padding: 2px 8px;
    background: rgba(var(--strategy-color), 0.15);
    border-radius: var(--radius-full, 9999px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--strategy-color);
  }

  .remove-btn {
    margin-left: auto;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    opacity: 0.5;
    transition: all 0.15s ease;
  }

  .remove-btn:hover {
    opacity: 1;
    background: var(--bg-elevated, #2d3640);
    color: var(--error, #f85149);
  }

  .remove-btn svg {
    width: 12px;
    height: 12px;
  }

  /* Column Content */
  .column-content {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  .content-scroll {
    height: 100%;
    padding: var(--space-3, 12px);
    overflow-y: auto;
  }

  .prose-paragraph {
    margin: 0 0 var(--space-3, 12px) 0;
    font-family: 'Merriweather', Georgia, serif;
    font-size: var(--text-sm, 12px);
    line-height: 1.7;
    color: var(--text-primary, #e6edf3);
  }

  .prose-paragraph:last-child {
    margin-bottom: 0;
  }

  /* Column Footer */
  .column-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .meta-info {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .word-count {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .score {
    padding: 2px 8px;
    border-radius: var(--radius-full, 9999px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
  }

  .score.high {
    background: rgba(63, 185, 80, 0.2);
    color: var(--success, #3fb950);
  }

  .score.medium {
    background: rgba(210, 153, 34, 0.2);
    color: var(--warning, #d29922);
  }

  .score.low {
    background: rgba(248, 81, 73, 0.2);
    color: var(--error, #f85149);
  }

  .select-winner-btn {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: 6px 12px;
    background: var(--accent-gold, #d4a574);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--bg-primary, #0f1419);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .select-winner-btn:hover {
    filter: brightness(1.1);
  }

  .select-winner-btn svg {
    width: 14px;
    height: 14px;
  }

  /* Empty State */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-3, 12px);
    padding: var(--space-8, 32px);
    color: var(--text-muted, #6e7681);
  }

  .empty-state svg {
    width: 48px;
    height: 48px;
    opacity: 0.5;
  }

  .empty-state p {
    margin: 0;
    font-size: var(--text-sm, 12px);
    text-align: center;
  }

  /* Scrollbar styling */
  .content-scroll::-webkit-scrollbar {
    width: 6px;
  }

  .content-scroll::-webkit-scrollbar-track {
    background: var(--bg-secondary, #1a2027);
  }

  .content-scroll::-webkit-scrollbar-thumb {
    background: var(--border, #2d3a47);
    border-radius: 3px;
  }

  .content-scroll::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted, #6e7681);
  }
</style>
