<!--
  StatusBar.svelte - Shows background task progress and work order status

  Displays:
  - Active task with progress (e.g., "Generating voice variants... 3/5")
  - Idle state with completed count and history link
  - Expandable details for running tasks
-->
<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { workOrders, activeWorkOrder } from '$lib/stores';

  const dispatch = createEventDispatcher();

  let isExpanded = false;
  let pollInterval;

  // Computed values from stores
  $: hasActiveTask = $activeWorkOrder !== null;
  $: completedToday = $workOrders.filter(wo =>
    wo.status === 'completed' &&
    isToday(wo.completed_at)
  ).length;
  $: recentWorkOrders = $workOrders.slice(0, 5);

  function isToday(dateStr) {
    if (!dateStr) return false;
    const date = new Date(dateStr);
    const today = new Date();
    return date.toDateString() === today.toDateString();
  }

  function getTaskIcon(type) {
    switch (type) {
      case 'voice_tournament': return '🎤';
      case 'scene_generation': return '✍️';
      case 'story_bible': return '📖';
      case 'health_check': return '🩺';
      case 'consolidation': return '🧠';
      default: return '⚙️';
    }
  }

  function getStatusColor(status) {
    switch (status) {
      case 'running': return 'var(--accent-cyan, #58a6ff)';
      case 'completed': return 'var(--success, #3fb950)';
      case 'failed': return 'var(--error, #f85149)';
      case 'pending': return 'var(--warning, #d29922)';
      default: return 'var(--text-muted, #8b949e)';
    }
  }

  function formatDuration(startTime, endTime) {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diff = Math.floor((end - start) / 1000);

    if (diff < 60) return `${diff}s`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ${diff % 60}s`;
    return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`;
  }

  function openHistory() {
    dispatch('open-history');
  }

  function toggleExpand() {
    isExpanded = !isExpanded;
  }

  function cancelTask() {
    if ($activeWorkOrder) {
      dispatch('cancel-task', { id: $activeWorkOrder.id });
    }
  }
</script>

<div class="status-bar" class:expanded={isExpanded} class:has-task={hasActiveTask}>
  {#if hasActiveTask}
    <!-- Active Task Display -->
    <div class="status-content active" role="button" tabindex="0" on:click={toggleExpand} on:keydown={(e) => e.key === 'Enter' && toggleExpand()}>
      <div class="task-info">
        <span class="task-icon">{getTaskIcon($activeWorkOrder.type)}</span>
        <span class="task-name">{$activeWorkOrder.name}</span>
        {#if $activeWorkOrder.progress}
          <span class="task-progress">
            {$activeWorkOrder.progress.current}/{$activeWorkOrder.progress.total}
          </span>
        {/if}
      </div>

      <div class="task-actions">
        {#if $activeWorkOrder.progress}
          <div class="progress-bar">
            <div
              class="progress-fill"
              style="width: {($activeWorkOrder.progress.current / $activeWorkOrder.progress.total) * 100}%"
            ></div>
          </div>
        {:else}
          <div class="spinner"></div>
        {/if}

        <span class="expand-btn" title={isExpanded ? 'Collapse' : 'Expand'}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            {#if isExpanded}
              <polyline points="18 15 12 9 6 15"></polyline>
            {:else}
              <polyline points="6 9 12 15 18 9"></polyline>
            {/if}
          </svg>
        </span>
      </div>
    </div>

    <!-- Expanded Details -->
    {#if isExpanded}
      <div class="expanded-details">
        <div class="detail-row">
          <span class="detail-label">Type:</span>
          <span class="detail-value">{$activeWorkOrder.type.replace(/_/g, ' ')}</span>
        </div>
        {#if $activeWorkOrder.started_at}
          <div class="detail-row">
            <span class="detail-label">Duration:</span>
            <span class="detail-value">{formatDuration($activeWorkOrder.started_at)}</span>
          </div>
        {/if}
        {#if $activeWorkOrder.message}
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">{$activeWorkOrder.message}</span>
          </div>
        {/if}

        <div class="detail-actions">
          <button class="cancel-btn" on:click|stopPropagation={cancelTask}>
            Cancel Task
          </button>
        </div>
      </div>
    {/if}
  {:else}
    <!-- Idle State -->
    <div class="status-content idle">
      <div class="idle-info">
        {#if completedToday > 0}
          <span class="completed-badge">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            {completedToday} task{completedToday !== 1 ? 's' : ''} completed today
          </span>
        {:else}
          <span class="idle-text">No active tasks</span>
        {/if}
      </div>

      <button class="history-btn" on:click={openHistory}>
        View history
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>
    </div>
  {/if}

  <!-- Recent Activity (when idle and has history) -->
  {#if !hasActiveTask && recentWorkOrders.length > 0 && isExpanded}
    <div class="recent-activity">
      <div class="recent-header">Recent Activity</div>
      {#each recentWorkOrders as wo}
        <div class="recent-item">
          <span class="recent-icon" style="color: {getStatusColor(wo.status)}">
            {getTaskIcon(wo.type)}
          </span>
          <span class="recent-name">{wo.name}</span>
          <span class="recent-status" style="color: {getStatusColor(wo.status)}">
            {wo.status}
          </span>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .status-bar {
    display: flex;
    flex-direction: column;
    background: var(--bg-tertiary, #252d38);
    border-top: 1px solid var(--border, #2d3a47);
    font-size: var(--text-xs, 11px);
  }

  .status-bar.has-task {
    background: rgba(88, 166, 255, 0.05);
    border-top-color: var(--accent-cyan, #58a6ff);
  }

  .status-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    width: 100%;
    background: transparent;
    border: none;
    cursor: pointer;
    text-align: left;
    color: var(--text-secondary, #c9d1d9);
    user-select: none;
  }

  .status-content.idle {
    cursor: default;
  }

  .status-content.active:hover {
    background: rgba(88, 166, 255, 0.1);
  }

  .status-content.active:focus {
    outline: none;
    background: rgba(88, 166, 255, 0.1);
  }

  /* Task Info */
  .task-info {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    min-width: 0;
  }

  .task-icon {
    font-size: 14px;
    flex-shrink: 0;
  }

  .task-name {
    color: var(--text-primary, #e6edf3);
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .task-progress {
    color: var(--accent-cyan, #58a6ff);
    font-weight: 600;
    flex-shrink: 0;
  }

  /* Task Actions */
  .task-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .progress-bar {
    width: 60px;
    height: 4px;
    background: var(--bg-secondary, #1a2027);
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--accent-cyan, #58a6ff);
    border-radius: 2px;
    transition: width 0.3s ease;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid var(--border, #2d3a47);
    border-top-color: var(--accent-cyan, #58a6ff);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .expand-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
    background: transparent;
    border: none;
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: color 0.15s ease;
  }

  .expand-btn:hover {
    color: var(--text-secondary, #c9d1d9);
  }

  /* Expanded Details */
  .expanded-details {
    padding: 8px 12px 12px;
    border-top: 1px solid var(--border, #2d3a47);
    background: var(--bg-secondary, #1a2027);
  }

  .detail-row {
    display: flex;
    gap: 8px;
    margin-bottom: 4px;
  }

  .detail-label {
    color: var(--text-muted, #8b949e);
    min-width: 60px;
  }

  .detail-value {
    color: var(--text-secondary, #c9d1d9);
    text-transform: capitalize;
  }

  .detail-actions {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .cancel-btn {
    padding: 4px 12px;
    background: transparent;
    border: 1px solid var(--error, #f85149);
    border-radius: var(--radius-sm, 4px);
    color: var(--error, #f85149);
    font-size: 10px;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .cancel-btn:hover {
    background: rgba(248, 81, 73, 0.1);
  }

  /* Idle State */
  .idle-info {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .completed-badge {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--success, #3fb950);
  }

  .idle-text {
    color: var(--text-muted, #8b949e);
    font-style: italic;
  }

  .history-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    background: transparent;
    border: none;
    color: var(--text-muted, #8b949e);
    font-size: 10px;
    cursor: pointer;
    transition: color 0.15s ease;
  }

  .history-btn:hover {
    color: var(--accent-cyan, #58a6ff);
  }

  /* Recent Activity */
  .recent-activity {
    padding: 8px 12px;
    border-top: 1px solid var(--border, #2d3a47);
    background: var(--bg-secondary, #1a2027);
  }

  .recent-header {
    font-size: 9px;
    font-weight: 600;
    color: var(--text-muted, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }

  .recent-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 0;
  }

  .recent-icon {
    font-size: 12px;
  }

  .recent-name {
    flex: 1;
    color: var(--text-secondary, #c9d1d9);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .recent-status {
    font-size: 9px;
    text-transform: uppercase;
    font-weight: 500;
  }
</style>
