<!--
  StructureVariantSelector.svelte - Chapter Structure Variant Selection

  Displays 5 structural approaches before writing prose:
  - Action-heavy (fast pacing, many scenes)
  - Character-focused (fewer scenes, deeper psychology)
  - Dialogue-driven (conversation-centered)
  - Experimental (non-linear, flashbacks)
  - Balanced (mix of all elements)

  Writers can select a structure or create a hybrid.
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    structureVariants,
    selectedStructure,
    currentScaffold
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let sceneId = '';
  export let scaffold = '';
  export let beatDescription = '';
  export let povCharacter = '';
  export let targetWordCount = 5000;

  // Local state
  let loading = false;
  let error = null;
  let variants = [];

  // Structure type configurations
  const structureTypes = {
    ACTION_EMPHASIS: {
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,
      color: '#f85149',
      label: 'Action-Heavy',
      description: 'Fast pacing, multiple scenes, external conflict foregrounded'
    },
    CHARACTER_DEPTH: {
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
      color: '#a371f7',
      label: 'Character-Focused',
      description: 'Fewer scenes, deeper psychology, rich introspection'
    },
    DIALOGUE_FOCUS: {
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`,
      color: '#58a6ff',
      label: 'Dialogue-Driven',
      description: 'Conversation-centered, conflict through words, subtext'
    },
    ATMOSPHERIC: {
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path></svg>`,
      color: '#3fb950',
      label: 'Atmospheric',
      description: 'Setting as character, sensory immersion, mood emphasis'
    },
    BALANCED: {
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg>`,
      color: '#d29922',
      label: 'Balanced',
      description: 'Mix of action, character, dialogue - standard structure'
    }
  };

  // Generate structure variants
  async function generateVariants() {
    loading = true;
    error = null;

    try {
      const result = await apiClient.generateStructureVariants(
        sceneId || $currentScaffold?.scene_id || 'scene_1',
        beatDescription,
        povCharacter,
        targetWordCount,
        scaffold || $currentScaffold?.scaffold
      );

      variants = result.variants.map(v => ({
        ...v,
        config: structureTypes[v.name] || structureTypes.BALANCED
      }));
      $structureVariants = variants;
    } catch (err) {
      error = err.message || 'Failed to generate structure variants';
    } finally {
      loading = false;
    }
  }

  // Select a variant
  function selectVariant(variant) {
    $selectedStructure = variant;
    dispatch('select', { variant });
  }

  // Proceed to scene generation
  function proceedToGeneration() {
    if ($selectedStructure) {
      dispatch('proceed', { structure: $selectedStructure });
    }
  }

  // Close handler
  function close() {
    dispatch('close');
  }

  // Format word count
  function formatWordCount(count) {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  }
</script>

<div class="structure-selector">
  <!-- Header -->
  <div class="header">
    <div class="header-content">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
        </svg>
      </div>
      <div>
        <h2>Select Chapter Structure</h2>
        <p class="subtitle">Choose a structural approach for your scene</p>
      </div>
    </div>
    <button class="close-btn" on:click={close}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>

  <!-- Error display -->
  {#if error}
    <div class="error-banner">
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
      <span>{error}</span>
      <button on:click={() => error = null}>Dismiss</button>
    </div>
  {/if}

  <!-- Content -->
  <div class="content">
    {#if variants.length === 0 && !loading}
      <!-- Generate prompt -->
      <div class="generate-prompt">
        <div class="prompt-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
        </div>
        <h3>Explore Structural Options</h3>
        <p>Generate 5 different structural approaches for your chapter. Each approach offers a unique way to tell your story.</p>
        <button class="generate-btn" on:click={generateVariants} disabled={loading}>
          {#if loading}
            <span class="spinner"></span>
            Generating...
          {:else}
            Generate Structure Variants
          {/if}
        </button>
      </div>

    {:else if loading}
      <!-- Loading state -->
      <div class="loading-state">
        <span class="spinner large"></span>
        <p>Generating 5 structural approaches...</p>
      </div>

    {:else}
      <!-- Variants grid -->
      <div class="variants-grid">
        {#each variants as variant}
          <button
            class="variant-card"
            class:selected={$selectedStructure?.id === variant.id}
            style="--variant-color: {variant.config?.color || '#d29922'}"
            on:click={() => selectVariant(variant)}
          >
            <div class="variant-header">
              <div class="variant-icon">
                {@html variant.config?.icon || structureTypes.BALANCED.icon}
              </div>
              <div class="variant-title">
                <h4>{variant.config?.label || variant.name}</h4>
                <span class="variant-pacing">{variant.pacing} pacing</span>
              </div>
              {#if $selectedStructure?.id === variant.id}
                <div class="selected-badge">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                  </svg>
                </div>
              {/if}
            </div>

            <p class="variant-description">{variant.config?.description || variant.description}</p>

            <div class="variant-scenes">
              <div class="scenes-header">
                <span class="scenes-count">{variant.scenes?.length || 0} scenes</span>
                <span class="total-words">{formatWordCount(variant.total_word_count || 0)} words</span>
              </div>
              {#if variant.scenes && variant.scenes.length > 0}
                <div class="scenes-list">
                  {#each variant.scenes.slice(0, 4) as scene, i}
                    <div class="scene-item">
                      <span class="scene-number">{i + 1}</span>
                      <span class="scene-title">{scene.title}</span>
                      <span class="scene-words">{formatWordCount(scene.word_count)}</span>
                    </div>
                  {/each}
                  {#if variant.scenes.length > 4}
                    <div class="more-scenes">+{variant.scenes.length - 4} more</div>
                  {/if}
                </div>
              {/if}
            </div>
          </button>
        {/each}
      </div>

      <!-- Selection Info -->
      {#if $selectedStructure}
        <div class="selection-info">
          <div class="selection-content">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <span>
              <strong>{$selectedStructure.config?.label || $selectedStructure.name}</strong> selected
              ({$selectedStructure.scenes?.length || 0} scenes, {formatWordCount($selectedStructure.total_word_count || 0)} words)
            </span>
          </div>
          <button class="proceed-btn" on:click={proceedToGeneration}>
            Proceed to Scene Generation
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
        </div>
      {/if}
    {/if}
  </div>
</div>

<style>
  .structure-selector {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 85vh;
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
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.2));
    border-radius: var(--radius-md, 6px);
    color: var(--accent-gold, #d4a574);
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
    transition: all var(--transition-fast, 100ms ease);
  }

  .close-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .close-btn svg {
    width: 18px;
    height: 18px;
  }

  /* Error Banner */
  .error-banner {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--error-muted, rgba(248, 81, 73, 0.2));
    border-bottom: 1px solid var(--error, #f85149);
    color: var(--error, #f85149);
    font-size: var(--text-sm, 12px);
  }

  .error-banner svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .error-banner span {
    flex: 1;
  }

  .error-banner button {
    padding: 4px 8px;
    background: transparent;
    border: 1px solid var(--error, #f85149);
    border-radius: var(--radius-sm, 4px);
    color: var(--error, #f85149);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
  }

  /* Content */
  .content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  /* Generate Prompt */
  .generate-prompt {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: var(--space-8, 32px);
    min-height: 300px;
  }

  .prompt-icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-lg, 8px);
    color: var(--accent-gold, #d4a574);
    margin-bottom: var(--space-4, 16px);
  }

  .prompt-icon svg {
    width: 32px;
    height: 32px;
  }

  .generate-prompt h3 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .generate-prompt p {
    margin: 0 0 var(--space-4, 16px) 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    max-width: 400px;
  }

  .generate-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-3, 12px) var(--space-6, 24px);
    background: var(--accent-gold, #d4a574);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--bg-primary, #0f1419);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .generate-btn:hover:not(:disabled) {
    background: var(--accent-gold-hover, #e0b585);
  }

  .generate-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Loading State */
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-8, 32px);
    min-height: 300px;
  }

  .loading-state p {
    margin: var(--space-3, 12px) 0 0 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  /* Spinner */
  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  .spinner.large {
    width: 32px;
    height: 32px;
    border-width: 3px;
    border-top-color: var(--accent-gold, #d4a574);
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Variants Grid */
  .variants-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--space-3, 12px);
  }

  .variant-card {
    display: flex;
    flex-direction: column;
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    text-align: left;
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .variant-card:hover {
    border-color: var(--variant-color);
  }

  .variant-card.selected {
    border-color: var(--accent-gold, #d4a574);
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.1));
    box-shadow: 0 0 0 1px var(--accent-gold, #d4a574);
  }

  .variant-header {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3, 12px);
    margin-bottom: var(--space-3, 12px);
  }

  .variant-icon {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: color-mix(in srgb, var(--variant-color) 20%, transparent);
    border-radius: var(--radius-md, 6px);
    color: var(--variant-color);
    flex-shrink: 0;
  }

  .variant-icon svg,
  .variant-icon :global(svg) {
    width: 20px;
    height: 20px;
  }

  .variant-title {
    flex: 1;
  }

  .variant-title h4 {
    margin: 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .variant-pacing {
    font-size: var(--text-xs, 11px);
    color: var(--variant-color);
    text-transform: capitalize;
  }

  .selected-badge {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-gold, #d4a574);
    border-radius: 50%;
    color: var(--bg-primary, #0f1419);
    flex-shrink: 0;
  }

  .selected-badge svg {
    width: 14px;
    height: 14px;
  }

  .variant-description {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-normal, 1.5);
  }

  .variant-scenes {
    background: var(--bg-input, #161b22);
    border-radius: var(--radius-sm, 4px);
    padding: var(--space-2, 8px);
  }

  .scenes-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-2, 8px);
    padding-bottom: var(--space-2, 8px);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .scenes-count {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .total-words {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .scenes-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .scene-item {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    font-size: 10px;
  }

  .scene-number {
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-tertiary, #242d38);
    border-radius: 50%;
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    color: var(--text-muted, #6e7681);
    flex-shrink: 0;
  }

  .scene-title {
    flex: 1;
    color: var(--text-secondary, #8b949e);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .scene-words {
    color: var(--text-muted, #6e7681);
    flex-shrink: 0;
  }

  .more-scenes {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
    text-align: center;
    padding-top: var(--space-1, 4px);
  }

  /* Selection Info */
  .selection-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: var(--space-4, 16px);
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.2));
    border: 1px solid var(--accent-gold, #d4a574);
    border-radius: var(--radius-md, 6px);
  }

  .selection-content {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    font-size: var(--text-sm, 12px);
    color: var(--accent-gold, #d4a574);
  }

  .selection-content svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .selection-content strong {
    color: var(--text-primary, #e6edf3);
  }

  .proceed-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    background: var(--accent-gold, #d4a574);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--bg-primary, #0f1419);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .proceed-btn:hover {
    background: var(--accent-gold-hover, #e0b585);
  }

  .proceed-btn svg {
    width: 16px;
    height: 16px;
  }
</style>
