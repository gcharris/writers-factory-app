<!--
  WorkOrderTracker.svelte - Template progress tracker for ARCHITECT mode

  Shows the 4 Story Bible templates with completion status:
  - Protagonist.md (Fatal Flaw, The Lie, Arc)
  - Beat_Sheet.md (15 beats)
  - Theme.md (Central theme, statement)
  - World_Rules.md (Fundamental constraints)

  Features:
  - Progress percentage bar
  - Individual template status icons
  - Click to open template editor
  - Mode transition button when complete
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    foremanWorkOrder,
    storyBibleStatus,
    storyBibleLoading,
    templateStatus,
    activeModal,
    modalData
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Template definitions
  const templates = [
    {
      id: 'protagonist',
      name: 'Protagonist',
      description: 'Fatal Flaw, The Lie, Character Arc',
      icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>`,
      requiredFields: ['fatal_flaw', 'the_lie']
    },
    {
      id: 'beat_sheet',
      name: 'Beat Sheet',
      description: '15-beat Save the Cat! structure',
      icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="8" y1="6" x2="21" y2="6"></line>
        <line x1="8" y1="12" x2="21" y2="12"></line>
        <line x1="8" y1="18" x2="21" y2="18"></line>
        <line x1="3" y1="6" x2="3.01" y2="6"></line>
        <line x1="3" y1="12" x2="3.01" y2="12"></line>
        <line x1="3" y1="18" x2="3.01" y2="18"></line>
      </svg>`,
      requiredFields: ['beats']
    },
    {
      id: 'theme',
      name: 'Theme',
      description: 'Central theme and thematic argument',
      icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M12 16v-4"></path>
        <path d="M12 8h.01"></path>
      </svg>`,
      requiredFields: ['central_theme']
    },
    {
      id: 'world_rules',
      name: 'World Rules',
      description: 'Fundamental constraints and rules',
      icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="2" y1="12" x2="22" y2="12"></line>
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
      </svg>`,
      requiredFields: ['fundamental_rules']
    }
  ];

  // Computed status from store
  $: statuses = $templateStatus;

  // Overall completion
  $: overallCompletion = calculateOverallCompletion(statuses);
  $: canAdvance = overallCompletion >= 80; // Need 80% to advance to Voice Calibration

  function calculateOverallCompletion(statuses) {
    const values = Object.values(statuses);
    if (values.length === 0) return 0;
    const total = values.reduce((sum, t) => sum + (t.completion || 0), 0);
    return Math.round(total / values.length);
  }

  // Status icon based on completion
  function getStatusIcon(status) {
    if (status === 'complete') {
      return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--success, #3fb950)" stroke-width="2.5">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>`;
    } else if (status === 'partial') {
      return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--warning, #d29922)" stroke-width="2">
        <circle cx="12" cy="12" r="10" stroke-dasharray="31.4 31.4" stroke-dashoffset="15.7"></circle>
      </svg>`;
    } else {
      return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted, #6e7681)" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
      </svg>`;
    }
  }

  function getStatusColor(status) {
    if (status === 'complete') return 'var(--success, #3fb950)';
    if (status === 'partial') return 'var(--warning, #d29922)';
    return 'var(--text-muted, #6e7681)';
  }

  function handleTemplateClick(templateId) {
    $activeModal = 'template-editor';
    $modalData = { templateId };
    dispatch('edit', { templateId });
  }

  function handleAdvanceMode() {
    dispatch('advance', { toMode: 'VOICE_CALIBRATION' });
  }

  // Refresh status from backend
  async function refreshStatus() {
    $storyBibleLoading = true;
    try {
      const status = await apiClient.getStoryBibleStatus();
      $storyBibleStatus = status;

      // Update template statuses based on response
      $templateStatus = {
        protagonist: {
          status: status.protagonist?.fatal_flaw && status.protagonist?.the_lie ? 'complete'
                 : status.protagonist?.name ? 'partial' : 'pending',
          completion: status.checks?.find(c => c.name.includes('Protagonist'))?.passed ? 100
                     : status.protagonist?.name ? 50 : 0
        },
        beat_sheet: {
          status: status.beat_sheet?.completion >= 100 ? 'complete'
                 : status.beat_sheet?.completion > 0 ? 'partial' : 'pending',
          completion: status.beat_sheet?.completion || 0
        },
        theme: {
          status: status.checks?.find(c => c.name.includes('Theme'))?.passed ? 'complete' : 'pending',
          completion: status.checks?.find(c => c.name.includes('Theme'))?.passed ? 100 : 0
        },
        world_rules: {
          status: status.checks?.find(c => c.name.includes('World'))?.passed ? 'complete' : 'pending',
          completion: status.checks?.find(c => c.name.includes('World'))?.passed ? 100 : 0
        }
      };
    } catch (error) {
      console.error('Failed to refresh Story Bible status:', error);
    } finally {
      $storyBibleLoading = false;
    }
  }

  onMount(() => {
    refreshStatus();
  });
</script>

<div class="work-order-tracker">
  <div class="tracker-header">
    <h4 class="tracker-title">Story Bible Progress</h4>
    <button class="refresh-btn" on:click={refreshStatus} disabled={$storyBibleLoading} title="Refresh status">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class:spinning={$storyBibleLoading}>
        <polyline points="23 4 23 10 17 10"></polyline>
        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
      </svg>
    </button>
  </div>

  <!-- Overall progress bar -->
  <div class="overall-progress">
    <div class="progress-bar">
      <div
        class="progress-fill"
        style="width: {overallCompletion}%; background: {overallCompletion >= 80 ? 'var(--success, #3fb950)' : 'var(--accent-cyan, #58a6ff)'}"
      ></div>
    </div>
    <span class="progress-text">{overallCompletion}%</span>
  </div>

  <!-- Template list -->
  <div class="template-list">
    {#each templates as template}
      {@const status = statuses[template.id] || { status: 'pending', completion: 0 }}
      <button
        class="template-item"
        on:click={() => handleTemplateClick(template.id)}
      >
        <div class="template-icon" style="color: {getStatusColor(status.status)}">
          {@html template.icon}
        </div>
        <div class="template-info">
          <span class="template-name">{template.name}</span>
          <span class="template-desc">{template.description}</span>
        </div>
        <div class="template-status">
          {@html getStatusIcon(status.status)}
        </div>
      </button>
    {/each}
  </div>

  <!-- Advance mode button -->
  {#if canAdvance}
    <button class="advance-btn" on:click={handleAdvanceMode}>
      <span>Ready for Voice Calibration</span>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="5" y1="12" x2="19" y2="12"></line>
        <polyline points="12 5 19 12 12 19"></polyline>
      </svg>
    </button>
  {:else}
    <div class="incomplete-notice">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M12 16v-4"></path>
        <path d="M12 8h.01"></path>
      </svg>
      <span>Complete Story Bible to advance</span>
    </div>
  {/if}
</div>

<style>
  .work-order-tracker {
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
  }

  .tracker-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .tracker-title {
    margin: 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .refresh-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .refresh-btn:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-secondary, #8b949e);
  }

  .refresh-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .spinning {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .overall-progress {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .progress-bar {
    flex: 1;
    height: 6px;
    background: var(--bg-elevated, #2d3640);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    transition: width var(--transition-normal, 200ms ease);
  }

  .progress-text {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
    min-width: 32px;
    text-align: right;
  }

  .template-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .template-item {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px);
    background: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius-sm, 4px);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
    text-align: left;
  }

  .template-item:hover {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--border, #2d3a47);
  }

  .template-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-sm, 4px);
    flex-shrink: 0;
  }

  .template-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .template-name {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .template-desc {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .template-status {
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .advance-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--success, #3fb950);
    border: none;
    border-radius: var(--radius-md, 6px);
    color: var(--bg-primary, #0f1419);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .advance-btn:hover {
    filter: brightness(1.1);
  }

  .incomplete-notice {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px);
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }
</style>
