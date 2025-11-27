<!--
  WorkOrderHistory.svelte - Modal showing work order history

  Displays completed, failed, and cancelled work orders.
  Allows clearing old entries and viewing details.
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { workOrders, clearOldWorkOrders } from '$lib/stores';

  const dispatch = createEventDispatcher();

  let filterStatus = 'all'; // 'all' | 'completed' | 'failed' | 'cancelled'

  $: filteredOrders = $workOrders.filter(wo => {
    if (filterStatus === 'all') return wo.status !== 'running' && wo.status !== 'pending';
    return wo.status === filterStatus;
  });

  $: stats = {
    total: $workOrders.filter(wo => wo.status !== 'running' && wo.status !== 'pending').length,
    completed: $workOrders.filter(wo => wo.status === 'completed').length,
    failed: $workOrders.filter(wo => wo.status === 'failed').length,
    cancelled: $workOrders.filter(wo => wo.status === 'cancelled').length
  };

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
      case 'completed': return 'var(--success, #3fb950)';
      case 'failed': return 'var(--error, #f85149)';
      case 'cancelled': return 'var(--text-muted, #8b949e)';
      default: return 'var(--text-muted, #8b949e)';
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return '—';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;

    // Less than 24 hours: show relative time
    if (diff < 24 * 60 * 60 * 1000) {
      if (diff < 60 * 1000) return 'Just now';
      if (diff < 60 * 60 * 1000) return `${Math.floor(diff / 60000)}m ago`;
      return `${Math.floor(diff / 3600000)}h ago`;
    }

    // Less than 7 days: show day name
    if (diff < 7 * 24 * 60 * 60 * 1000) {
      return date.toLocaleDateString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' });
    }

    // Otherwise: show full date
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
  }

  function formatDuration(startTime, endTime) {
    if (!startTime || !endTime) return '—';
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diff = Math.floor((end - start) / 1000);

    if (diff < 60) return `${diff}s`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ${diff % 60}s`;
    return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`;
  }

  function handleClearOld() {
    if (confirm('Clear work orders older than 7 days?')) {
      clearOldWorkOrders(7);
    }
  }

  function handleClearAll() {
    if (confirm('Clear all completed work order history?')) {
      workOrders.update(orders =>
        orders.filter(o => o.status === 'running' || o.status === 'pending')
      );
    }
  }

  function close() {
    dispatch('close');
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      close();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="modal-backdrop" on:click={close} role="presentation">
  <div class="modal" on:click|stopPropagation role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <div class="modal-header">
      <h2 id="modal-title">Work Order History</h2>
      <button class="close-btn" on:click={close} aria-label="Close">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="modal-content">
      <!-- Stats Row -->
      <div class="stats-row">
        <button
          class="stat-btn"
          class:active={filterStatus === 'all'}
          on:click={() => filterStatus = 'all'}
        >
          <span class="stat-value">{stats.total}</span>
          <span class="stat-label">Total</span>
        </button>
        <button
          class="stat-btn completed"
          class:active={filterStatus === 'completed'}
          on:click={() => filterStatus = 'completed'}
        >
          <span class="stat-value">{stats.completed}</span>
          <span class="stat-label">Completed</span>
        </button>
        <button
          class="stat-btn failed"
          class:active={filterStatus === 'failed'}
          on:click={() => filterStatus = 'failed'}
        >
          <span class="stat-value">{stats.failed}</span>
          <span class="stat-label">Failed</span>
        </button>
        <button
          class="stat-btn cancelled"
          class:active={filterStatus === 'cancelled'}
          on:click={() => filterStatus = 'cancelled'}
        >
          <span class="stat-value">{stats.cancelled}</span>
          <span class="stat-label">Cancelled</span>
        </button>
      </div>

      <!-- Work Order List -->
      <div class="order-list">
        {#if filteredOrders.length === 0}
          <div class="empty-state">
            <span class="empty-icon">📋</span>
            <p>No work orders to display</p>
          </div>
        {:else}
          {#each filteredOrders as order}
            <div class="order-item" style="--status-color: {getStatusColor(order.status)}">
              <div class="order-icon">{getTaskIcon(order.type)}</div>
              <div class="order-content">
                <div class="order-header">
                  <span class="order-name">{order.name}</span>
                  <span class="order-status" style="color: {getStatusColor(order.status)}">
                    {order.status}
                  </span>
                </div>
                <div class="order-meta">
                  <span class="order-type">{order.type.replace(/_/g, ' ')}</span>
                  <span class="order-separator">•</span>
                  <span class="order-time">{formatDate(order.completed_at || order.started_at)}</span>
                  {#if order.started_at && order.completed_at}
                    <span class="order-separator">•</span>
                    <span class="order-duration">{formatDuration(order.started_at, order.completed_at)}</span>
                  {/if}
                </div>
                {#if order.error}
                  <div class="order-error">{order.error}</div>
                {/if}
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>

    <div class="modal-footer">
      <button class="footer-btn" on:click={handleClearOld}>
        Clear old (7+ days)
      </button>
      <button class="footer-btn danger" on:click={handleClearAll}>
        Clear all history
      </button>
    </div>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 200;
    animation: fadeIn 0.15s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .modal {
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    width: 90%;
    max-width: 500px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
    animation: slideUp 0.2s ease;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .modal-header h2 {
    margin: 0;
    font-size: var(--text-lg, 16px);
    font-weight: 600;
    color: var(--text-primary, #e6edf3);
  }

  .close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
    background: transparent;
    border: none;
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    border-radius: var(--radius-sm, 4px);
    transition: all 0.15s ease;
  }

  .close-btn:hover {
    background: var(--bg-tertiary, #252d38);
    color: var(--text-primary, #e6edf3);
  }

  .modal-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px 20px;
  }

  /* Stats Row */
  .stats-row {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }

  .stat-btn {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px 8px;
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .stat-btn:hover {
    border-color: var(--border-strong, #444c56);
  }

  .stat-btn.active {
    border-color: var(--accent-cyan, #58a6ff);
    background: rgba(88, 166, 255, 0.1);
  }

  .stat-btn.completed .stat-value {
    color: var(--success, #3fb950);
  }

  .stat-btn.failed .stat-value {
    color: var(--error, #f85149);
  }

  .stat-btn.cancelled .stat-value {
    color: var(--text-muted, #8b949e);
  }

  .stat-value {
    font-size: var(--text-lg, 16px);
    font-weight: 600;
    color: var(--text-primary, #e6edf3);
  }

  .stat-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
    margin-top: 2px;
  }

  /* Order List */
  .order-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    color: var(--text-muted, #8b949e);
  }

  .empty-icon {
    font-size: 32px;
    margin-bottom: 8px;
    opacity: 0.5;
  }

  .empty-state p {
    margin: 0;
    font-size: var(--text-sm, 13px);
  }

  .order-item {
    display: flex;
    gap: 12px;
    padding: 12px;
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-left: 3px solid var(--status-color);
    border-radius: var(--radius-md, 6px);
    transition: all 0.15s ease;
  }

  .order-item:hover {
    border-color: var(--border-strong, #444c56);
  }

  .order-icon {
    font-size: 18px;
    flex-shrink: 0;
  }

  .order-content {
    flex: 1;
    min-width: 0;
  }

  .order-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 4px;
  }

  .order-name {
    font-weight: 500;
    color: var(--text-primary, #e6edf3);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .order-status {
    font-size: var(--text-xs, 11px);
    font-weight: 500;
    text-transform: uppercase;
    flex-shrink: 0;
  }

  .order-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  .order-type {
    text-transform: capitalize;
  }

  .order-separator {
    opacity: 0.5;
  }

  .order-error {
    margin-top: 6px;
    padding: 6px 8px;
    background: rgba(248, 81, 73, 0.1);
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--error, #f85149);
  }

  /* Footer */
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 12px 20px;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .footer-btn {
    padding: 6px 12px;
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #c9d1d9);
    font-size: var(--text-sm, 12px);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .footer-btn:hover {
    background: var(--bg-tertiary, #252d38);
    border-color: var(--border-strong, #444c56);
  }

  .footer-btn.danger {
    border-color: var(--error, #f85149);
    color: var(--error, #f85149);
  }

  .footer-btn.danger:hover {
    background: rgba(248, 81, 73, 0.1);
  }
</style>
