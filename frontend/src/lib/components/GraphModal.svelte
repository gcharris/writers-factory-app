<!--
  GraphModal.svelte - Knowledge Graph Explorer Modal

  Full-featured graph exploration tool with:
  - Search and filter controls
  - Force-directed canvas visualization
  - Node details panel
  - Relationship editor
  - Ingest button for populating graph
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import GraphExplorer from './GraphExplorer.svelte';

  const dispatch = createEventDispatcher();

  // Graph stats for header display
  let graphStats = { nodes: 0, edges: 0, types: [] };
  let ingesting = false;

  // Node type colors
  const typeColors = {
    CHARACTER: '#58a6ff',
    LOCATION: '#a371f7',
    THEME: '#d4a574',
    EVENT: '#3fb950',
    OBJECT: '#8b949e',
    CONCEPT: '#f85149'
  };

  function getNodeColor(type) {
    return typeColors[type?.toUpperCase()] || '#8b949e';
  }

  onMount(async () => {
    await fetchGraphStats();
  });

  async function fetchGraphStats() {
    try {
      const res = await fetch('http://localhost:8000/graph/stats');
      if (res.ok) {
        const data = await res.json();
        graphStats = {
          nodes: data.node_count || 0,
          edges: data.edge_count || 0,
          types: data.node_types || []
        };
      }
    } catch (e) {
      console.warn('Failed to fetch graph stats:', e);
    }
  }

  async function runIngestion() {
    if (ingesting) return;

    ingesting = true;
    try {
      const res = await fetch('http://localhost:8000/graph/ingest', {
        method: 'POST'
      });
      if (res.ok) {
        await fetchGraphStats();
        // Force a refresh by briefly remounting (or use an event)
        window.dispatchEvent(new CustomEvent('graph-refresh'));
      }
    } catch (e) {
      console.error('Ingestion failed:', e);
    } finally {
      ingesting = false;
    }
  }
</script>

<div class="graph-modal">
  <!-- Compact Header -->
  <div class="graph-modal-header">
    <div class="header-left">
      <span class="graph-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <circle cx="4" cy="6" r="2"></circle>
          <circle cx="20" cy="6" r="2"></circle>
          <circle cx="4" cy="18" r="2"></circle>
          <circle cx="20" cy="18" r="2"></circle>
          <line x1="6" y1="6" x2="9.5" y2="10"></line>
          <line x1="18" y1="6" x2="14.5" y2="10"></line>
          <line x1="6" y1="18" x2="9.5" y2="14"></line>
          <line x1="18" y1="18" x2="14.5" y2="14"></line>
        </svg>
      </span>
      <div class="header-info">
        <h2>Knowledge Graph Explorer</h2>
        <div class="header-stats">
          <span class="stat">{graphStats.nodes} nodes</span>
          <span class="stat-sep">·</span>
          <span class="stat">{graphStats.edges} edges</span>
        </div>
      </div>
    </div>

    <div class="header-actions">
      <button
        class="ingest-btn"
        on:click={runIngestion}
        disabled={ingesting}
        title="Ingest content files into graph"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
        {ingesting ? 'Ingesting...' : 'Ingest Content'}
      </button>
    </div>
  </div>

  <!-- Graph Explorer (Full Height) -->
  <div class="graph-explorer-container">
    <GraphExplorer />
  </div>

  <!-- Footer with node type legend -->
  <div class="graph-modal-footer">
    <div class="legend">
      <span class="legend-title">Types:</span>
      {#each graphStats.types as nodeType}
        <span class="legend-item">
          <span class="legend-dot" style="background: {getNodeColor(nodeType)}"></span>
          {nodeType}
        </span>
      {/each}
      {#if graphStats.types.length === 0}
        <span class="legend-empty">No nodes yet — click "Ingest Content" to populate</span>
      {/if}
    </div>
    <div class="legend-help">
      <span class="help-item">Click node to view details</span>
      <span class="help-sep">·</span>
      <span class="help-item">Double-click to pin</span>
      <span class="help-sep">·</span>
      <span class="help-item">Scroll to zoom</span>
    </div>
  </div>
</div>

<style>
  .graph-modal {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 500px;
    background: var(--bg-primary, #0f1419);
  }

  /* Header */
  .graph-modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
    flex-shrink: 0;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .graph-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: rgba(88, 166, 255, 0.15);
    border-radius: var(--radius-md, 6px);
    color: var(--accent-cyan, #58a6ff);
    flex-shrink: 0;
  }

  .header-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .graph-modal-header h2 {
    margin: 0;
    font-size: var(--text-base, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .header-stats {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  .stat-sep {
    opacity: 0.5;
  }

  .header-actions {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .ingest-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--accent-cyan, #58a6ff);
    border: none;
    border-radius: var(--radius-md, 6px);
    color: var(--bg-primary, #0f1419);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .ingest-btn:hover:not(:disabled) {
    background: var(--accent-cyan-hover, #79b8ff);
    transform: translateY(-1px);
  }

  .ingest-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Graph Explorer Container */
  .graph-explorer-container {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  /* Footer */
  .graph-modal-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2, 8px) var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-top: 1px solid var(--border, #2d3a47);
    flex-shrink: 0;
  }

  .legend {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    flex-wrap: wrap;
  }

  .legend-title {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .legend-empty {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    font-style: italic;
  }

  .legend-help {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .help-item {
    opacity: 0.8;
  }

  .help-sep {
    opacity: 0.4;
  }

  /* Responsive */
  @media (max-width: 800px) {
    .graph-modal-footer {
      flex-direction: column;
      gap: var(--space-2, 8px);
      align-items: flex-start;
    }
  }
</style>
