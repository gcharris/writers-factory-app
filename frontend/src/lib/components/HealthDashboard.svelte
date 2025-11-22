<script>
  import { onMount } from 'svelte';

  const API_URL = 'http://127.0.0.1:8000';

  /** @typedef {{ id: string, type: string, desc?: string }} GraphNode */
  /** @typedef {{ node_id: string, existing_desc: string, new_desc: string, type?: string }} Conflict */
  /** @typedef {{ node_count: number, edge_count: number, recent_nodes: GraphNode[] }} GraphStats */

  let status = 'loading';
  let isLoading = false;
  let isDigesting = false;
  let errorMsg = '';

  // Health data
  /** @type {GraphStats} */
  let graphStats = { node_count: 0, edge_count: 0, recent_nodes: [] };
  /** @type {Conflict[]} */
  let conflicts = [];
  let uncommittedCount = 0;
  /** @type {Date | null} */
  let lastRefresh = null;

  // Auto-refresh toggle
  let autoRefresh = false;
  /** @type {ReturnType<typeof setInterval> | null} */
  let refreshInterval = null;

  onMount(() => {
    fetchHealthStatus();
    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
    };
  });

  $: if (autoRefresh) {
    refreshInterval = setInterval(fetchHealthStatus, 30000); // 30s
  } else if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }

  async function fetchHealthStatus() {
    isLoading = true;
    errorMsg = '';

    try {
      const res = await fetch(`${API_URL}/health/status`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      graphStats = data.graph_stats || { node_count: 0, edge_count: 0, recent_nodes: [] };
      conflicts = data.conflicts || [];
      uncommittedCount = data.uncommitted_count || 0;
      lastRefresh = new Date();
      status = 'ready';
    } catch (err) {
      status = 'error';
      errorMsg = err instanceof Error ? err.message : 'Failed to fetch health status';
    } finally {
      isLoading = false;
    }
  }

  async function digestNow() {
    isDigesting = true;
    errorMsg = '';

    try {
      const res = await fetch(`${API_URL}/graph/consolidate`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error(`Digest failed (${res.status})`);

      const result = await res.json();
      // Refresh stats after digestion
      await fetchHealthStatus();

      // Show brief success message
      if (result.total_nodes_added > 0 || result.total_edges_added > 0) {
        alert(`Digested: +${result.total_nodes_added} nodes, +${result.total_edges_added} edges`);
      }
    } catch (err) {
      errorMsg = err instanceof Error ? err.message : 'Digest failed';
    } finally {
      isDigesting = false;
    }
  }

  /** @param {Date | null} date */
  function formatTime(date) {
    if (!date) return '--';
    return date.toLocaleTimeString();
  }

  /** @param {string} type */
  function getNodeTypeIcon(type) {
    /** @type {Record<string, string>} */
    const icons = {
      'CHARACTER': '👤',
      'LOCATION': '📍',
      'OBJECT': '📦',
      'EVENT': '⚡',
      'ORGANIZATION': '🏢',
      'THEME': '💡',
      'PLOT_POINT': '📌'
    };
    return icons[type] || '•';
  }
</script>

<div class="health-panel">
  <div class="hd-header">
    <div class="title-group">
      <h3>Metabolism</h3>
      <span class={`status-dot ${status === 'ready' ? 'green' : status === 'error' ? 'red' : 'yellow'}`}></span>
    </div>
    <div class="header-actions">
      <label class="auto-toggle" title="Auto-refresh every 30s">
        <input type="checkbox" bind:checked={autoRefresh} />
        Auto
      </label>
      <button class="refresh-btn" on:click={fetchHealthStatus} disabled={isLoading}>
        {isLoading ? '...' : '⟳'}
      </button>
    </div>
  </div>

  <!-- Section 1: Uncommitted Events -->
  <div class="section metabolism-status">
    <div class="metric-row">
      <span class="metric-label">Uncommitted Events</span>
      <span class="metric-value" class:warning={uncommittedCount > 10}>
        {uncommittedCount}
      </span>
    </div>
    <button
      class="digest-btn"
      on:click={digestNow}
      disabled={isDigesting || uncommittedCount === 0}
    >
      {#if isDigesting}
        Digesting...
      {:else if uncommittedCount === 0}
        All Digested ✓
      {:else}
        Digest Now →
      {/if}
    </button>
    {#if lastRefresh}
      <small class="last-refresh">Last checked: {formatTime(lastRefresh)}</small>
    {/if}
  </div>

  <!-- Section 2: Graph Vitals -->
  <div class="section graph-vitals">
    <h4>Knowledge Graph</h4>
    <div class="vitals-grid">
      <div class="vital">
        <span class="vital-value">{graphStats.node_count}</span>
        <span class="vital-label">Nodes</span>
      </div>
      <div class="vital">
        <span class="vital-value">{graphStats.edge_count}</span>
        <span class="vital-label">Edges</span>
      </div>
    </div>

    {#if graphStats.recent_nodes && graphStats.recent_nodes.length > 0}
      <div class="recent-entities">
        <h5>Recent Entities</h5>
        <ul>
          {#each graphStats.recent_nodes.slice(0, 5) as node}
            <li>
              <span class="entity-icon">{getNodeTypeIcon(node.type)}</span>
              <span class="entity-name">{node.id}</span>
              <span class="entity-type">{node.type}</span>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>

  <!-- Section 3: Conflicts -->
  <div class="section conflicts-section">
    <h4>
      Conflicts
      {#if conflicts.length > 0}
        <span class="conflict-badge">{conflicts.length}</span>
      {/if}
    </h4>
    {#if conflicts.length === 0}
      <p class="no-conflicts">No conflicts detected</p>
    {:else}
      <ul class="conflict-list">
        {#each conflicts.slice(0, 5) as conflict}
          <li class="conflict-item">
            <strong>{conflict.node_id}</strong>
            <div class="conflict-details">
              <span class="existing">"{conflict.existing_desc}"</span>
              <span class="vs">vs</span>
              <span class="new">"{conflict.new_desc}"</span>
            </div>
          </li>
        {/each}
      </ul>
      {#if conflicts.length > 5}
        <small class="more-conflicts">+{conflicts.length - 5} more conflicts</small>
      {/if}
    {/if}
  </div>

  {#if errorMsg}
    <div class="error-box">{errorMsg}</div>
  {/if}
</div>

<style>
  .health-panel {
    background: #ffffff;
    border-top: 1px solid #e5e7eb;
    border-bottom: 1px solid #e5e7eb;
    padding: 1rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    gap: 1rem;
    font-family: sans-serif;
    color: #1f2937;
  }

  .hd-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .title-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  h3 {
    margin: 0;
    font-size: 0.95rem;
    color: #111827;
  }

  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }
  .status-dot.green { background: #10b981; }
  .status-dot.red { background: #ef4444; }
  .status-dot.yellow { background: #f59e0b; }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .auto-toggle {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.75rem;
    color: #6b7280;
    cursor: pointer;
  }

  .auto-toggle input {
    width: 14px;
    height: 14px;
  }

  .refresh-btn {
    background: none;
    border: 1px solid #d1d5db;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
  }
  .refresh-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.75rem;
    background: #f9fafb;
    border-radius: 6px;
  }

  h4 {
    margin: 0;
    font-size: 0.85rem;
    color: #374151;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  h5 {
    margin: 0.5rem 0 0.25rem 0;
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* Metabolism Status */
  .metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .metric-label {
    font-size: 0.85rem;
    color: #4b5563;
  }

  .metric-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #10b981;
  }
  .metric-value.warning {
    color: #f59e0b;
  }

  .digest-btn {
    background: #10b981;
    color: white;
    border: none;
    padding: 0.6rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.85rem;
  }
  .digest-btn:hover:not(:disabled) {
    background: #059669;
  }
  .digest-btn:disabled {
    background: #d1d5db;
    color: #6b7280;
    cursor: not-allowed;
  }

  .last-refresh {
    font-size: 0.7rem;
    color: #9ca3af;
    text-align: right;
  }

  /* Graph Vitals */
  .vitals-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }

  .vital {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.5rem;
    background: #ffffff;
    border-radius: 4px;
    border: 1px solid #e5e7eb;
  }

  .vital-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2563eb;
  }

  .vital-label {
    font-size: 0.7rem;
    color: #6b7280;
    text-transform: uppercase;
  }

  .recent-entities ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .recent-entities li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0;
    border-bottom: 1px solid #e5e7eb;
    font-size: 0.8rem;
  }
  .recent-entities li:last-child {
    border-bottom: none;
  }

  .entity-icon {
    font-size: 0.9rem;
  }

  .entity-name {
    flex: 1;
    font-weight: 500;
    color: #1f2937;
  }

  .entity-type {
    font-size: 0.65rem;
    color: #9ca3af;
    text-transform: uppercase;
    background: #f3f4f6;
    padding: 0.1rem 0.4rem;
    border-radius: 3px;
  }

  /* Conflicts */
  .conflict-badge {
    background: #ef4444;
    color: white;
    font-size: 0.7rem;
    padding: 0.1rem 0.4rem;
    border-radius: 10px;
    font-weight: 600;
  }

  .no-conflicts {
    font-size: 0.8rem;
    color: #10b981;
    margin: 0;
  }

  .conflict-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .conflict-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid #e5e7eb;
    font-size: 0.8rem;
  }
  .conflict-item:last-child {
    border-bottom: none;
  }

  .conflict-details {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    margin-top: 0.25rem;
    font-size: 0.75rem;
  }

  .existing {
    color: #ef4444;
  }

  .vs {
    color: #9ca3af;
    font-style: italic;
  }

  .new {
    color: #f59e0b;
  }

  .more-conflicts {
    color: #6b7280;
    font-size: 0.75rem;
  }

  .error-box {
    background: #fee2e2;
    color: #b91c1c;
    padding: 0.75rem;
    border-radius: 4px;
    font-size: 0.85rem;
  }
</style>
