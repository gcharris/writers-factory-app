<!--
  SixPassEnhancement.svelte - 6-Pass Enhancement Tracker

  Displays progress through the 6-pass enhancement ritual:
  1. Sensory Anchoring - Add sight/sound/smell/taste/touch
  2. Verb Promotion + Simile Elimination - Strong verbs, no clichés
  3. Metaphor Rotation - Vary metaphor domains
  4. Voice Embed - Weave in voice artifacts
  5. Italics Gate - Remove 80% of italics
  6. Voice Authentication - Final voice consistency check

  Shows real-time progress, changes made, and content preview.
-->
<script>
  import { createEventDispatcher, onDestroy } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    sixPassProgress,
    currentSceneContent,
    currentSceneScore,
    enhancementLoading
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let sceneId = '';
  export let sceneContent = '';
  export let phase = 'Act 1';
  export let voiceBundlePath = '';

  // Local state
  let running = false;
  let currentPass = 0;
  let passes = [];
  let finalContent = '';
  let originalScore = 0;
  let finalScore = 0;
  let totalChanges = 0;
  let error = null;

  // Pass configurations
  const passConfigs = [
    {
      number: 1,
      name: 'Sensory Anchoring',
      description: 'Add sight, sound, smell, taste, touch details',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`,
      color: '#58a6ff'
    },
    {
      number: 2,
      name: 'Verb Promotion',
      description: 'Strengthen verbs, eliminate similes and clichés',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,
      color: '#f85149'
    },
    {
      number: 3,
      name: 'Metaphor Rotation',
      description: 'Vary metaphor domains, prevent saturation',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z"></path></svg>`,
      color: '#a371f7'
    },
    {
      number: 4,
      name: 'Voice Embed',
      description: 'Weave in Gold Standard voice artifacts',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path></svg>`,
      color: '#d4a574'
    },
    {
      number: 5,
      name: 'Italics Gate',
      description: 'Remove 80% of italics emphasis',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="4" x2="10" y2="4"></line><line x1="14" y1="20" x2="5" y2="20"></line><line x1="15" y1="4" x2="9" y2="20"></line></svg>`,
      color: '#d29922'
    },
    {
      number: 6,
      name: 'Voice Auth',
      description: 'Final voice consistency verification',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
      color: '#3fb950'
    }
  ];

  // Use props or store
  $: content = sceneContent || $currentSceneContent;
  $: score = $currentSceneScore || originalScore;

  // Get pass status
  function getPassStatus(passNumber) {
    if (currentPass > passNumber) return 'complete';
    if (currentPass === passNumber && running) return 'running';
    if (currentPass === passNumber) return 'current';
    return 'pending';
  }

  // Get pass result
  function getPassResult(passNumber) {
    return passes.find(p => p.pass_number === passNumber);
  }

  // Start 6-pass enhancement
  async function startEnhancement() {
    if (!content) return;

    running = true;
    $enhancementLoading = true;
    error = null;
    currentPass = 1;
    passes = [];
    originalScore = score || 0;

    try {
      const result = await apiClient.runSixPassEnhancement(
        sceneId || 'scene_1',
        content,
        phase,
        voiceBundlePath
      );

      passes = result.passes;
      finalContent = result.final_content;
      originalScore = result.original_score;
      finalScore = result.final_score;
      totalChanges = result.total_changes;
      currentPass = 7; // All complete

      $currentSceneContent = finalContent;
      $currentSceneScore = finalScore;
      $sixPassProgress = {
        complete: true,
        passes: passes,
        total_changes: totalChanges
      };

      dispatch('complete', {
        content: finalContent,
        originalScore: originalScore,
        finalScore: finalScore,
        totalChanges: totalChanges
      });
    } catch (err) {
      error = err.message || 'Enhancement failed';
    } finally {
      running = false;
      $enhancementLoading = false;
    }
  }

  // Accept enhanced content
  function acceptEnhancement() {
    if (finalContent) {
      dispatch('accept', { content: finalContent, score: finalScore });
    }
  }

  // Reject and keep original
  function rejectEnhancement() {
    dispatch('reject');
  }

  // Close handler
  function close() {
    dispatch('close');
  }
</script>

<div class="six-pass-enhancement">
  <!-- Header -->
  <div class="header">
    <div class="header-content">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path>
        </svg>
      </div>
      <div>
        <h2>6-Pass Enhancement</h2>
        <p class="subtitle">Full enhancement ritual</p>
      </div>
    </div>
    <button class="close-btn" on:click={close}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>

  <!-- Score Progress -->
  <div class="score-progress">
    <div class="score-item">
      <span class="score-label">Original</span>
      <span class="score-value original">{originalScore || score || '?'}</span>
    </div>
    {#if currentPass > 6}
      <div class="score-arrow">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="5" y1="12" x2="19" y2="12"></line>
          <polyline points="12 5 19 12 12 19"></polyline>
        </svg>
      </div>
      <div class="score-item">
        <span class="score-label">Enhanced</span>
        <span class="score-value enhanced">{finalScore}</span>
      </div>
      <div class="score-improvement">
        +{finalScore - originalScore} points
      </div>
    {:else if running}
      <div class="score-arrow running">
        <span class="spinner"></span>
      </div>
      <div class="score-item">
        <span class="score-label">Processing</span>
        <span class="score-value pending">...</span>
      </div>
    {/if}
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

  <!-- Passes Grid -->
  <div class="content">
    <div class="passes-grid">
      {#each passConfigs as pass}
        {@const status = getPassStatus(pass.number)}
        {@const result = getPassResult(pass.number)}
        <div
          class="pass-card"
          class:complete={status === 'complete'}
          class:running={status === 'running'}
          class:current={status === 'current'}
          class:pending={status === 'pending'}
          style="--pass-color: {pass.color}"
        >
          <div class="pass-header">
            <div class="pass-icon">
              {#if status === 'complete'}
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
              {:else if status === 'running'}
                <span class="pass-spinner"></span>
              {:else}
                {@html pass.icon}
              {/if}
            </div>
            <div class="pass-info">
              <span class="pass-number">Pass {pass.number}</span>
              <h4>{pass.name}</h4>
            </div>
            {#if result}
              <span class="changes-badge">
                {result.changes_made} changes
              </span>
            {/if}
          </div>
          <p class="pass-description">{pass.description}</p>
          {#if status === 'running'}
            <div class="pass-progress">
              <div class="progress-bar">
                <div class="progress-fill"></div>
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>

    <!-- Results Summary -->
    {#if currentPass > 6}
      <div class="results-summary">
        <h3>Enhancement Complete</h3>
        <div class="results-stats">
          <div class="stat">
            <span class="stat-value">{totalChanges}</span>
            <span class="stat-label">Total Changes</span>
          </div>
          <div class="stat">
            <span class="stat-value improvement">+{finalScore - originalScore}</span>
            <span class="stat-label">Score Improvement</span>
          </div>
          <div class="stat">
            <span class="stat-value">{finalScore}</span>
            <span class="stat-label">Final Score</span>
          </div>
        </div>

        <div class="preview-section">
          <h4>Enhanced Content Preview</h4>
          <div class="preview-content">
            <pre>{finalContent.substring(0, 500)}...</pre>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Actions -->
  <div class="actions">
    {#if currentPass === 0}
      <button class="secondary-btn" on:click={close}>Cancel</button>
      <button class="primary-btn" on:click={startEnhancement} disabled={running || !content}>
        Start 6-Pass Enhancement
      </button>
    {:else if currentPass > 6}
      <button class="secondary-btn" on:click={rejectEnhancement}>
        Keep Original
      </button>
      <button class="primary-btn" on:click={acceptEnhancement}>
        Accept Enhanced Version
      </button>
    {:else}
      <div class="running-status">
        <span class="spinner"></span>
        <span>Processing Pass {currentPass} of 6...</span>
      </div>
    {/if}
  </div>
</div>

<style>
  .six-pass-enhancement {
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
    background: var(--warning-muted, rgba(210, 153, 34, 0.2));
    border-radius: var(--radius-md, 6px);
    color: var(--warning, #d29922);
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

  /* Score Progress */
  .score-progress {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-4, 16px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .score-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .score-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .score-value {
    font-size: var(--text-xl, 18px);
    font-weight: var(--font-bold, 700);
  }

  .score-value.original {
    color: var(--text-secondary, #8b949e);
  }

  .score-value.enhanced {
    color: var(--success, #3fb950);
  }

  .score-value.pending {
    color: var(--warning, #d29922);
  }

  .score-arrow {
    color: var(--text-muted, #6e7681);
  }

  .score-arrow svg {
    width: 20px;
    height: 20px;
  }

  .score-arrow.running {
    display: flex;
    align-items: center;
  }

  .score-improvement {
    padding: 4px 12px;
    background: var(--success-muted, rgba(63, 185, 80, 0.2));
    border-radius: var(--radius-full, 9999px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--success, #3fb950);
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

  /* Passes Grid */
  .passes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--space-3, 12px);
  }

  .pass-card {
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    padding: var(--space-3, 12px);
    transition: all var(--transition-fast, 100ms ease);
  }

  .pass-card.complete {
    border-color: var(--success, #3fb950);
    background: var(--success-muted, rgba(63, 185, 80, 0.1));
  }

  .pass-card.running {
    border-color: var(--pass-color);
    box-shadow: 0 0 0 1px var(--pass-color), 0 0 20px color-mix(in srgb, var(--pass-color) 30%, transparent);
  }

  .pass-card.pending {
    opacity: 0.5;
  }

  .pass-header {
    display: flex;
    align-items: flex-start;
    gap: var(--space-2, 8px);
    margin-bottom: var(--space-2, 8px);
  }

  .pass-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: color-mix(in srgb, var(--pass-color) 20%, transparent);
    border-radius: var(--radius-md, 6px);
    color: var(--pass-color);
    flex-shrink: 0;
  }

  .pass-card.complete .pass-icon {
    background: var(--success, #3fb950);
    color: var(--bg-primary, #0f1419);
  }

  .pass-icon :global(svg) {
    width: 18px;
    height: 18px;
  }

  .pass-spinner {
    width: 18px;
    height: 18px;
    border: 2px solid transparent;
    border-top-color: var(--pass-color);
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  .pass-info {
    flex: 1;
  }

  .pass-number {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
  }

  .pass-info h4 {
    margin: 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .changes-badge {
    padding: 2px 6px;
    background: var(--success-muted, rgba(63, 185, 80, 0.2));
    border-radius: var(--radius-full, 9999px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    color: var(--success, #3fb950);
  }

  .pass-description {
    margin: 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .pass-progress {
    margin-top: var(--space-2, 8px);
  }

  .progress-bar {
    height: 4px;
    background: var(--bg-input, #161b22);
    border-radius: var(--radius-full, 9999px);
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    width: 100%;
    background: var(--pass-color);
    border-radius: var(--radius-full, 9999px);
    animation: progress-pulse 1.5s ease-in-out infinite;
  }

  @keyframes progress-pulse {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
  }

  /* Results Summary */
  .results-summary {
    margin-top: var(--space-4, 16px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--success, #3fb950);
    border-radius: var(--radius-md, 6px);
  }

  .results-summary h3 {
    margin: 0 0 var(--space-4, 16px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--success, #3fb950);
  }

  .results-stats {
    display: flex;
    justify-content: space-around;
    padding-bottom: var(--space-4, 16px);
    border-bottom: 1px solid var(--border, #2d3a47);
    margin-bottom: var(--space-4, 16px);
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .stat-value {
    font-size: var(--text-xl, 18px);
    font-weight: var(--font-bold, 700);
    color: var(--text-primary, #e6edf3);
  }

  .stat-value.improvement {
    color: var(--success, #3fb950);
  }

  .stat-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .preview-section h4 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
  }

  .preview-content {
    background: var(--bg-input, #161b22);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    padding: var(--space-3, 12px);
    max-height: 150px;
    overflow-y: auto;
  }

  .preview-content pre {
    margin: 0;
    font-family: var(--font-ui);
    font-size: var(--text-xs, 11px);
    line-height: 1.5;
    color: var(--text-secondary, #8b949e);
    white-space: pre-wrap;
  }

  /* Actions */
  .actions {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .running-status {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    font-size: var(--text-sm, 12px);
    color: var(--warning, #d29922);
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
    background: var(--warning, #d29922);
    border: none;
    color: var(--bg-primary, #0f1419);
  }

  .primary-btn:hover:not(:disabled) {
    background: var(--warning-hover, #e3b341);
  }

  .primary-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
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

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
