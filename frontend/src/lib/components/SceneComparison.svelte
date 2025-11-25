<!--
  SceneComparison.svelte - Side-by-Side Variant Comparison

  Compare 2-4 scene variants with:
  - Score breakdown by category (Voice 30, Character 20, Metaphor 20, Anti-Pattern 15, Phase 15)
  - Diff highlighting (optional)
  - Section-by-section view
  - Quick select/reject controls
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { selectedSceneVariants } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let variants = [];

  // Local state
  let highlightDiffs = false;
  let viewMode = 'full'; // 'full' | 'sections' | 'scores'

  // Score categories
  const scoreCategories = [
    { key: 'voice_authenticity', label: 'Voice', weight: 30, color: '#d4a574' },
    { key: 'character_consistency', label: 'Character', weight: 20, color: '#a371f7' },
    { key: 'metaphor_discipline', label: 'Metaphor', weight: 20, color: '#58a6ff' },
    { key: 'anti_pattern_compliance', label: 'Anti-Pattern', weight: 15, color: '#3fb950' },
    { key: 'phase_appropriateness', label: 'Phase', weight: 15, color: '#d29922' }
  ];

  // Use provided variants or store
  $: displayVariants = variants.length > 0 ? variants : $selectedSceneVariants;

  // Get score tier
  function getScoreTier(score) {
    if (score >= 95) return { label: 'Gold', color: '#d4a574' };
    if (score >= 90) return { label: 'Excellent', color: '#3fb950' };
    if (score >= 85) return { label: 'Strong', color: '#58a6ff' };
    if (score >= 80) return { label: 'Good', color: '#d29922' };
    if (score >= 75) return { label: 'Acceptable', color: '#8b949e' };
    return { label: 'Needs Work', color: '#f85149' };
  }

  // Get model display name
  function getModelName(model) {
    return model?.split('/').pop()?.split('-').slice(0, 2).join('-') || 'Unknown';
  }

  // Get strategy display name
  function getStrategyName(strategy) {
    const names = {
      'ACTION_EMPHASIS': 'Action',
      'CHARACTER_DEPTH': 'Character',
      'DIALOGUE_FOCUS': 'Dialogue',
      'ATMOSPHERIC': 'Atmospheric',
      'BALANCED': 'Balanced'
    };
    return names[strategy] || strategy;
  }

  // Select variant as winner
  function selectWinner(variant) {
    dispatch('selectWinner', { variant });
  }

  // Remove from comparison
  function removeVariant(variant) {
    $selectedSceneVariants = $selectedSceneVariants.filter(v => v.id !== variant.id);
    dispatch('remove', { variant });
  }

  // Create hybrid from selections
  function createHybrid() {
    dispatch('createHybrid', { variants: displayVariants });
  }

  // Close comparison
  function close() {
    dispatch('close');
  }
</script>

<div class="scene-comparison">
  <!-- Header -->
  <div class="header">
    <div class="header-content">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
      </div>
      <div>
        <h2>Compare Variants</h2>
        <p class="subtitle">{displayVariants.length} variants selected</p>
      </div>
    </div>
    <div class="header-actions">
      <div class="view-toggle">
        <button class:active={viewMode === 'full'} on:click={() => viewMode = 'full'}>Full</button>
        <button class:active={viewMode === 'scores'} on:click={() => viewMode = 'scores'}>Scores</button>
      </div>
      <button class="close-btn" on:click={close}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  </div>

  <!-- Comparison Content -->
  <div class="comparison-content">
    {#if displayVariants.length === 0}
      <div class="empty-state">
        <p>No variants selected for comparison</p>
        <p class="hint">Select 2-4 variants from the grid to compare</p>
      </div>
    {:else}
      <div class="variants-container" style="--variant-count: {displayVariants.length}">
        {#each displayVariants as variant, index}
          <div class="variant-column">
            <!-- Variant Header -->
            <div class="variant-header">
              <div class="variant-info">
                <span class="variant-model">{getModelName(variant.model)}</span>
                <span class="variant-strategy">{getStrategyName(variant.strategy)}</span>
              </div>
              <button class="remove-btn" on:click={() => removeVariant(variant)} title="Remove from comparison">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            <!-- Score Summary -->
            {#if variant.score}
              {@const tier = getScoreTier(variant.score)}
              <div class="score-summary">
                <div class="total-score" style="--tier-color: {tier.color}">
                  <span class="score-value">{variant.score}</span>
                  <span class="score-label">{tier.label}</span>
                </div>
              </div>
            {/if}

            <!-- Score Breakdown -->
            {#if viewMode === 'scores' || viewMode === 'full'}
              <div class="score-breakdown">
                {#each scoreCategories as category}
                  {@const score = variant.scores?.[category.key] || 0}
                  {@const percentage = (score / category.weight) * 100}
                  <div class="score-row">
                    <span class="category-label">{category.label}</span>
                    <div class="score-bar">
                      <div class="score-fill" style="width: {percentage}%; background: {category.color}"></div>
                    </div>
                    <span class="category-score">{score}/{category.weight}</span>
                  </div>
                {/each}
              </div>
            {/if}

            <!-- Content Preview -->
            {#if viewMode === 'full'}
              <div class="content-preview">
                <pre>{variant.content}</pre>
              </div>
            {/if}

            <!-- Word Count -->
            <div class="variant-footer">
              <span class="word-count">{variant.word_count} words</span>
              <button class="select-btn" on:click={() => selectWinner(variant)}>
                Select as Winner
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Actions -->
  {#if displayVariants.length >= 2}
    <div class="actions">
      <button class="hybrid-btn" on:click={createHybrid}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
        </svg>
        Create Hybrid from These Variants
      </button>
    </div>
  {/if}
</div>

<style>
  .scene-comparison {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-lg, 8px);
    overflow: hidden;
  }

  /* Header */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .header-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
    border-radius: var(--radius-md, 6px);
    color: var(--accent-cyan, #58a6ff);
  }

  .header-icon svg {
    width: 24px;
    height: 24px;
  }

  .header h2 {
    margin: 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .subtitle {
    margin: 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .view-toggle {
    display: flex;
    background: var(--bg-input, #161b22);
    border-radius: var(--radius-md, 6px);
    padding: 2px;
  }

  .view-toggle button {
    padding: 4px 12px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .view-toggle button.active {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .close-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
  }

  .close-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .close-btn svg {
    width: 18px;
    height: 18px;
  }

  /* Comparison Content */
  .comparison-content {
    flex: 1;
    overflow: auto;
    padding: var(--space-4, 16px);
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
  }

  .empty-state p {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .empty-state .hint {
    margin-top: var(--space-2, 8px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  /* Variants Container */
  .variants-container {
    display: grid;
    grid-template-columns: repeat(var(--variant-count), 1fr);
    gap: var(--space-3, 12px);
    min-width: calc(var(--variant-count) * 280px);
  }

  .variant-column {
    display: flex;
    flex-direction: column;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    overflow: hidden;
  }

  .variant-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3, 12px);
    background: var(--bg-elevated, #2d3640);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .variant-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .variant-model {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .variant-strategy {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .remove-btn {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
  }

  .remove-btn:hover {
    background: var(--error-muted, rgba(248, 81, 73, 0.2));
    color: var(--error, #f85149);
  }

  .remove-btn svg {
    width: 14px;
    height: 14px;
  }

  /* Score Summary */
  .score-summary {
    padding: var(--space-3, 12px);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .total-score {
    display: flex;
    align-items: baseline;
    gap: var(--space-2, 8px);
  }

  .score-value {
    font-size: var(--text-2xl, 24px);
    font-weight: var(--font-bold, 700);
    color: var(--tier-color);
  }

  .score-label {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--tier-color);
    text-transform: uppercase;
  }

  /* Score Breakdown */
  .score-breakdown {
    padding: var(--space-3, 12px);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .score-row {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    margin-bottom: var(--space-2, 8px);
  }

  .score-row:last-child {
    margin-bottom: 0;
  }

  .category-label {
    width: 70px;
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .score-bar {
    flex: 1;
    height: 6px;
    background: var(--bg-input, #161b22);
    border-radius: var(--radius-full, 9999px);
    overflow: hidden;
  }

  .score-fill {
    height: 100%;
    border-radius: var(--radius-full, 9999px);
    transition: width var(--transition-normal, 200ms ease);
  }

  .category-score {
    width: 36px;
    font-size: 10px;
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
    text-align: right;
  }

  /* Content Preview */
  .content-preview {
    flex: 1;
    padding: var(--space-3, 12px);
    overflow-y: auto;
    max-height: 300px;
  }

  .content-preview pre {
    margin: 0;
    font-family: var(--font-ui);
    font-size: var(--text-xs, 11px);
    line-height: 1.6;
    color: var(--text-secondary, #8b949e);
    white-space: pre-wrap;
  }

  /* Variant Footer */
  .variant-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3, 12px);
    background: var(--bg-elevated, #2d3640);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .word-count {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .select-btn {
    padding: 4px 12px;
    background: var(--accent-gold, #d4a574);
    border: none;
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--bg-primary, #0f1419);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .select-btn:hover {
    background: var(--accent-gold-hover, #e0b585);
  }

  /* Actions */
  .actions {
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .hybrid-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2, 8px);
    width: 100%;
    padding: var(--space-3, 12px);
    background: var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
    border: 1px solid var(--accent-cyan, #58a6ff);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--accent-cyan, #58a6ff);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .hybrid-btn:hover {
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  .hybrid-btn svg {
    width: 16px;
    height: 16px;
  }
</style>
