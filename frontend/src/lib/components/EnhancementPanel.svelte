<!--
  EnhancementPanel.svelte - Enhancement Mode Selector

  Determines and displays the appropriate enhancement mode:
  - Action Prompt (85+): Surgical fixes for high-scoring scenes
  - 6-Pass Enhancement (70-84): Full enhancement ritual
  - Rewrite (<70): Regeneration recommended

  Shows current score, recommended mode, and allows manual override.
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    currentSceneContent,
    currentSceneScore,
    currentSceneAnalysis,
    enhancementMode,
    enhancementLoading,
    actionPromptFixes,
    sixPassProgress
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let sceneId = '';
  export let sceneContent = '';
  export let phase = 'Act 1';
  export let voiceBundlePath = '';

  // Local state
  let selectedMode = null;
  let loading = false;
  let error = null;

  // Enhancement mode configurations
  const modes = [
    {
      id: 'action_prompt',
      label: 'Action Prompt',
      description: 'Surgical fixes for specific issues',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>`,
      scoreRange: '85+',
      minScore: 85,
      color: '#3fb950',
      features: [
        'Preview fixes before applying',
        'Accept/reject individual changes',
        'Minimal disruption to prose',
        'Fast iteration'
      ]
    },
    {
      id: 'six_pass',
      label: '6-Pass Enhancement',
      description: 'Full enhancement ritual',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path></svg>`,
      scoreRange: '70-84',
      minScore: 70,
      maxScore: 84,
      color: '#d29922',
      features: [
        'Sensory Anchoring',
        'Verb Promotion + Simile Elimination',
        'Metaphor Rotation',
        'Voice Embed',
        'Italics Gate',
        'Voice Authentication'
      ]
    },
    {
      id: 'rewrite',
      label: 'Rewrite Recommended',
      description: 'Consider regenerating this scene',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>`,
      scoreRange: '<70',
      maxScore: 69,
      color: '#f85149',
      features: [
        'Fundamental issues detected',
        'Enhancement may not be cost-effective',
        'Consider new tournament variants',
        'Review scaffold and structure'
      ]
    }
  ];

  // Use props or store
  $: content = sceneContent || $currentSceneContent;
  $: score = $currentSceneScore;

  // Recommended mode based on score
  $: recommendedMode = getRecommendedMode(score);

  function getRecommendedMode(score) {
    if (!score) return null;
    if (score >= 85) return 'action_prompt';
    if (score >= 70) return 'six_pass';
    return 'rewrite';
  }

  // Get mode config
  function getModeConfig(modeId) {
    return modes.find(m => m.id === modeId);
  }

  // Select mode
  function selectMode(modeId) {
    selectedMode = modeId;
    $enhancementMode = modeId;
  }

  // Start enhancement
  async function startEnhancement() {
    if (!selectedMode || !content) return;

    loading = true;
    $enhancementLoading = true;
    error = null;

    try {
      if (selectedMode === 'action_prompt') {
        // Generate action prompt fixes
        const result = await apiClient.generateActionPrompt(
          sceneId || 'scene_1',
          content,
          phase,
          voiceBundlePath
        );
        $actionPromptFixes = result.fixes;
        dispatch('actionPromptReady', { fixes: result.fixes });
      } else if (selectedMode === 'six_pass') {
        // Start 6-pass enhancement
        dispatch('startSixPass', { sceneId, content, phase });
      } else {
        // Rewrite - go back to scene generation
        dispatch('rewrite');
      }
    } catch (err) {
      error = err.message || 'Failed to start enhancement';
    } finally {
      loading = false;
      $enhancementLoading = false;
    }
  }

  // Close handler
  function close() {
    dispatch('close');
  }
</script>

<div class="enhancement-panel">
  <!-- Header -->
  <div class="header">
    <div class="header-content">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9"></path>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
        </svg>
      </div>
      <div>
        <h2>Enhance Scene</h2>
        <p class="subtitle">Polish your scene to perfection</p>
      </div>
    </div>
    <button class="close-btn" on:click={close}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>

  <!-- Score Display -->
  {#if score}
    {@const tier = getModeConfig(recommendedMode)}
    <div class="score-display" style="--tier-color: {tier?.color || '#8b949e'}">
      <div class="score-circle">
        <span class="score-value">{score}</span>
        <span class="score-max">/100</span>
      </div>
      <div class="score-info">
        <span class="score-tier">{tier?.label || 'Unknown'}</span>
        <span class="score-desc">Recommended: {tier?.description || 'Analysis required'}</span>
      </div>
    </div>
  {:else}
    <div class="no-score">
      <p>Scene not yet analyzed. Run analysis to determine enhancement mode.</p>
    </div>
  {/if}

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

  <!-- Mode Selection -->
  <div class="content">
    <h3>Select Enhancement Mode</h3>
    <div class="modes-grid">
      {#each modes as mode}
        {@const isRecommended = recommendedMode === mode.id}
        {@const isDisabled = score && (
          (mode.minScore && score < mode.minScore) ||
          (mode.maxScore && score > mode.maxScore)
        ) && !isRecommended}
        <button
          class="mode-card"
          class:selected={selectedMode === mode.id}
          class:recommended={isRecommended}
          class:disabled={isDisabled}
          style="--mode-color: {mode.color}"
          on:click={() => !isDisabled && selectMode(mode.id)}
          disabled={isDisabled}
        >
          {#if isRecommended}
            <div class="recommended-badge">Recommended</div>
          {/if}
          <div class="mode-header">
            <div class="mode-icon">
              {@html mode.icon}
            </div>
            <div class="mode-info">
              <h4>{mode.label}</h4>
              <span class="mode-range">Score: {mode.scoreRange}</span>
            </div>
          </div>
          <p class="mode-description">{mode.description}</p>
          <ul class="mode-features">
            {#each mode.features as feature}
              <li>{feature}</li>
            {/each}
          </ul>
        </button>
      {/each}
    </div>
  </div>

  <!-- Actions -->
  <div class="actions">
    <button class="secondary-btn" on:click={close}>Cancel</button>
    <button
      class="primary-btn"
      on:click={startEnhancement}
      disabled={!selectedMode || loading}
    >
      {#if loading}
        <span class="spinner"></span>
        Processing...
      {:else if selectedMode === 'action_prompt'}
        Generate Fixes
      {:else if selectedMode === 'six_pass'}
        Start 6-Pass
      {:else if selectedMode === 'rewrite'}
        Return to Generation
      {:else}
        Select a Mode
      {/if}
    </button>
  </div>
</div>

<style>
  .enhancement-panel {
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
  }

  .close-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .close-btn svg {
    width: 18px;
    height: 18px;
  }

  /* Score Display */
  .score-display {
    display: flex;
    align-items: center;
    gap: var(--space-4, 16px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .score-circle {
    display: flex;
    align-items: baseline;
    justify-content: center;
    width: 80px;
    height: 80px;
    background: color-mix(in srgb, var(--tier-color) 20%, transparent);
    border: 2px solid var(--tier-color);
    border-radius: 50%;
  }

  .score-value {
    font-size: var(--text-2xl, 24px);
    font-weight: var(--font-bold, 700);
    color: var(--tier-color);
  }

  .score-max {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .score-info {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .score-tier {
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--tier-color);
  }

  .score-desc {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .no-score {
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .no-score p {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-muted, #6e7681);
    text-align: center;
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

  .content h3 {
    margin: 0 0 var(--space-4, 16px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  /* Modes Grid */
  .modes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: var(--space-3, 12px);
  }

  .mode-card {
    position: relative;
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

  .mode-card:hover:not(:disabled) {
    border-color: var(--mode-color);
  }

  .mode-card.selected {
    border-color: var(--mode-color);
    box-shadow: 0 0 0 1px var(--mode-color), inset 0 0 20px color-mix(in srgb, var(--mode-color) 10%, transparent);
  }

  .mode-card.recommended {
    border-color: var(--mode-color);
  }

  .mode-card.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .recommended-badge {
    position: absolute;
    top: -8px;
    right: var(--space-3, 12px);
    padding: 2px 8px;
    background: var(--mode-color);
    border-radius: var(--radius-full, 9999px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    color: var(--bg-primary, #0f1419);
    text-transform: uppercase;
  }

  .mode-header {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3, 12px);
    margin-bottom: var(--space-3, 12px);
  }

  .mode-icon {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: color-mix(in srgb, var(--mode-color) 20%, transparent);
    border-radius: var(--radius-md, 6px);
    color: var(--mode-color);
    flex-shrink: 0;
  }

  .mode-icon :global(svg) {
    width: 20px;
    height: 20px;
  }

  .mode-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .mode-info h4 {
    margin: 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .mode-range {
    font-size: var(--text-xs, 11px);
    color: var(--mode-color);
  }

  .mode-description {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .mode-features {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .mode-features li {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    font-size: 10px;
    color: var(--text-muted, #6e7681);
    margin-bottom: var(--space-1, 4px);
  }

  .mode-features li::before {
    content: '';
    width: 4px;
    height: 4px;
    background: var(--mode-color);
    border-radius: 50%;
    flex-shrink: 0;
  }

  /* Actions */
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3, 12px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .secondary-btn,
  .primary-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .secondary-btn {
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    color: var(--text-secondary, #8b949e);
  }

  .secondary-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .primary-btn {
    background: var(--accent-gold, #d4a574);
    border: none;
    color: var(--bg-primary, #0f1419);
  }

  .primary-btn:hover:not(:disabled) {
    background: var(--accent-gold-hover, #e0b585);
  }

  .primary-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Spinner */
  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
