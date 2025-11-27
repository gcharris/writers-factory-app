<!--
  StageDropdown.svelte - Shows current writing stage with progress

  Stages: Conception -> Voice -> Execution -> Polish
  Checkmarks for completed, filled circle for current, empty for future.
  Click to manually change focus.

  Auto-detects stage from backend on mount and periodically.
-->
<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { currentStage, stageProgress, assistantSettings } from '$lib/stores';
  import { apiClient } from '$lib/api_client';

  const dispatch = createEventDispatcher();

  let isOpen = false;
  let dropdownRef;
  let isLoading = false;
  let nextSteps = [];
  let canAdvance = false;
  let detectionInterval;
  let manualOverride = false; // User manually selected a stage

  const stages = [
    { id: 'conception', name: 'Conception', color: '#d4a574', description: 'Story Bible, structure, world-building' },
    { id: 'voice', name: 'Voice', color: '#a371f7', description: 'Calibration, tournaments, voice reference' },
    { id: 'execution', name: 'Execution', color: '#58a6ff', description: 'Drafting scenes, writing' },
    { id: 'polish', name: 'Polish', color: '#3fb950', description: 'Editing, refinement, continuity' }
  ];

  onMount(async () => {
    document.addEventListener('click', handleClickOutside);

    // Initial detection
    await detectStage();

    // Re-detect every 60 seconds (when not manually overridden)
    detectionInterval = setInterval(() => {
      if (!manualOverride) {
        detectStage();
      }
    }, 60000);

    return () => {
      document.removeEventListener('click', handleClickOutside);
      if (detectionInterval) clearInterval(detectionInterval);
    };
  });

  onDestroy(() => {
    if (detectionInterval) clearInterval(detectionInterval);
  });

  async function detectStage() {
    if (isLoading) return;

    try {
      isLoading = true;
      const result = await apiClient.detectWritingStage();

      // Update stores with detected values
      if (!manualOverride) {
        currentStage.set(result.stage);
      }
      stageProgress.set(result.progress);
      nextSteps = result.next_steps || [];
      canAdvance = result.can_advance;

    } catch (e) {
      console.warn('Stage detection failed:', e);
      // Keep current values on error
    } finally {
      isLoading = false;
    }
  }

  // Expose refresh function for parent components
  export function refresh() {
    manualOverride = false;
    return detectStage();
  }

  function handleClickOutside(e) {
    if (dropdownRef && !dropdownRef.contains(e.target)) {
      isOpen = false;
    }
  }

  function getStageStatus(stageId) {
    const stageIndex = stages.findIndex(s => s.id === stageId);
    const currentIndex = stages.findIndex(s => s.id === $currentStage);

    if (stageIndex < currentIndex) return 'completed';
    if (stageIndex === currentIndex) return 'current';
    return 'future';
  }

  function getStageIcon(status) {
    switch (status) {
      case 'completed': return 'check';
      case 'current': return 'filled';
      default: return 'empty';
    }
  }

  async function selectStage(stage) {
    if ($assistantSettings.confirmStageChange && stage.id !== $currentStage) {
      const confirmed = confirm(`Switch focus to ${stage.name} stage?`);
      if (!confirmed) return;
    }

    manualOverride = true; // User manually selected, don't auto-update
    currentStage.set(stage.id);
    isOpen = false;
    dispatch('change', { stage: stage.id });
  }

  function resetToAutoDetect() {
    manualOverride = false;
    detectStage();
  }

  function toggle() {
    isOpen = !isOpen;
  }

  $: currentStageInfo = stages.find(s => s.id === $currentStage) || stages[0];
</script>

<div class="stage-dropdown" bind:this={dropdownRef}>
  <button
    class="dropdown-trigger"
    on:click={toggle}
    title="Current writing stage"
    style="--stage-color: {currentStageInfo.color}"
  >
    <span class="stage-indicator" style="background: {currentStageInfo.color}"></span>
    <span class="trigger-text">{currentStageInfo.name}</span>
    <span class="trigger-arrow" class:open={isOpen}>
      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </span>
  </button>

  {#if isOpen}
    <div class="dropdown-menu">
      {#each stages as stage}
        {@const status = getStageStatus(stage.id)}
        {@const progress = $stageProgress[stage.id] || 0}
        <button
          class="dropdown-item {status}"
          on:click={() => selectStage(stage)}
          style="--stage-color: {stage.color}"
        >
          <span class="item-indicator">
            {#if status === 'completed'}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            {:else if status === 'current'}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="6"></circle>
              </svg>
            {:else}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"></circle>
              </svg>
            {/if}
          </span>
          <span class="item-content">
            <span class="item-header">
              <span class="item-name">{stage.name}</span>
              {#if progress > 0}
                <span class="item-progress">{progress}%</span>
              {/if}
            </span>
            <span class="item-desc">{stage.description}</span>
          </span>
        </button>
      {/each}

      <!-- Next Steps for Current Stage -->
      {#if nextSteps.length > 0}
        <div class="next-steps">
          <span class="next-steps-label">Next steps:</span>
          <ul>
            {#each nextSteps.slice(0, 3) as step}
              <li>{step}</li>
            {/each}
          </ul>
        </div>
      {/if}

      <div class="dropdown-footer">
        {#if manualOverride}
          <span class="footer-text override">
            Manual focus active.
            <button class="reset-btn" on:click={resetToAutoDetect}>Reset to auto</button>
          </span>
        {:else if isLoading}
          <span class="footer-text">Detecting stage...</span>
        {:else}
          <span class="footer-text">Stage auto-detected. Click to change focus.</span>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .stage-dropdown {
    position: relative;
  }

  .dropdown-trigger {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #c9d1d9);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .dropdown-trigger:hover {
    background: var(--bg-elevated, #2d3748);
    border-color: var(--stage-color);
    color: var(--text-primary, #e6edf3);
  }

  .stage-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .trigger-text {
    font-weight: 500;
  }

  .trigger-arrow {
    display: flex;
    align-items: center;
    transition: transform 0.15s ease;
  }

  .trigger-arrow.open {
    transform: rotate(180deg);
  }

  .dropdown-menu {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    min-width: 260px;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    z-index: 100;
    overflow: hidden;
  }

  .dropdown-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    width: 100%;
    padding: 10px 12px;
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    color: var(--text-secondary, #c9d1d9);
    font-size: var(--text-sm, 12px);
    text-align: left;
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .dropdown-item:hover {
    background: var(--bg-tertiary, #252d38);
  }

  .dropdown-item.current {
    border-left-color: var(--stage-color);
    background: rgba(255, 255, 255, 0.03);
  }

  .dropdown-item.completed .item-indicator {
    color: var(--success, #3fb950);
  }

  .dropdown-item.current .item-indicator {
    color: var(--stage-color);
  }

  .dropdown-item.future .item-indicator {
    color: var(--text-muted, #8b949e);
  }

  .item-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .item-content {
    display: flex;
    flex-direction: column;
    gap: 2px;
    flex: 1;
  }

  .item-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }

  .item-name {
    font-weight: 500;
  }

  .dropdown-item.current .item-name {
    color: var(--stage-color);
  }

  .item-progress {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  .item-desc {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  .dropdown-footer {
    padding: 8px 12px;
    background: var(--bg-tertiary, #252d38);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .footer-text {
    font-size: 10px;
    color: var(--text-muted, #8b949e);
    font-style: italic;
  }

  .footer-text.override {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--warning, #d29922);
    font-style: normal;
  }

  .reset-btn {
    padding: 2px 6px;
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    color: var(--text-secondary, #c9d1d9);
    font-size: 9px;
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .reset-btn:hover {
    background: var(--bg-secondary, #1a2027);
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--accent-cyan, #58a6ff);
  }

  /* Next Steps */
  .next-steps {
    padding: 8px 12px;
    background: rgba(88, 166, 255, 0.05);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .next-steps-label {
    font-size: 10px;
    font-weight: 600;
    color: var(--accent-cyan, #58a6ff);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .next-steps ul {
    margin: 4px 0 0 0;
    padding-left: 14px;
    list-style: disc;
  }

  .next-steps li {
    font-size: 10px;
    color: var(--text-muted, #8b949e);
    line-height: 1.4;
    margin-bottom: 2px;
  }

  .next-steps li:last-child {
    margin-bottom: 0;
  }
</style>
