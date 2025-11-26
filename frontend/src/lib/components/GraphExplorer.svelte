<!--
  GraphExplorer.svelte - Advanced Knowledge Graph Explorer

  Full-featured graph exploration tool with:
  - Force-directed canvas visualization
  - Search and filter controls
  - Node details panel (slide-in from right)
  - Relationship editor modal

  This is the "power tool" version of the graph viewer.
  LiveGraph.svelte remains as a simple widget for quick views.
-->
<script>
  import { onMount } from 'svelte';
  import { selectedNode, graphFilters } from '$lib/stores';
  import GraphCanvas from './GraphCanvas.svelte';
  import GraphControls from './GraphControls.svelte';
  import GraphNodeDetails from './GraphNodeDetails.svelte';
  import GraphRelationshipEditor from './GraphRelationshipEditor.svelte';

  // Graph data
  let nodes = [];
  let edges = [];
  let loading = true;
  let error = '';

  // UI state
  let showNodeDetails = false;
  let showRelationshipEditor = false;
  let relationshipEditorMode = 'create'; // 'create' or 'edit'
  let selectedEdge = null;

  // Fetch graph data on mount
  onMount(async () => {
    await loadGraph();
  });

  async function loadGraph() {
    loading = true;
    error = '';

    try {
      const response = await fetch('http://localhost:8000/graph/export');
      if (!response.ok) throw new Error('Failed to load graph');

      const data = await response.json();
      nodes = data.nodes || [];
      edges = data.edges || [];
    } catch (e) {
      console.error('Graph load error:', e);
      error = e.message;
    } finally {
      loading = false;
    }
  }

  // Event handlers
  function handleNodeClick(event) {
    const node = event.detail;
    selectedNode.set(node);
    showNodeDetails = true;
  }

  function handleNodeDoubleClick(event) {
    const node = event.detail;
    selectedNode.set(node);
    showNodeDetails = true;
  }

  function handleEdgeClick(event) {
    selectedEdge = event.detail;
    relationshipEditorMode = 'edit';
    showRelationshipEditor = true;
  }

  function handleCreateRelationship() {
    relationshipEditorMode = 'create';
    selectedEdge = null;
    showRelationshipEditor = true;
  }

  function handleNodeUpdated(event) {
    const updatedNode = event.detail;
    nodes = nodes.map(n => n.id === updatedNode.id ? updatedNode : n);
  }

  function handleRelationshipCreated(event) {
    const newEdge = event.detail;
    edges = [...edges, newEdge];
    showRelationshipEditor = false;
  }

  function handleRelationshipUpdated(event) {
    const updatedEdge = event.detail;
    edges = edges.map(e => e.id === updatedEdge.id ? updatedEdge : e);
    showRelationshipEditor = false;
  }

  function handleRelationshipDeleted(event) {
    const deletedEdgeId = event.detail.id;
    edges = edges.filter(e => e.id !== deletedEdgeId);
    showRelationshipEditor = false;
  }

  function handleCloseDetails() {
    showNodeDetails = false;
    selectedNode.set(null);
  }

  function handleCloseRelationshipEditor() {
    showRelationshipEditor = false;
    selectedEdge = null;
  }

  // Subscribe to selected node changes
  $: if ($selectedNode) {
    showNodeDetails = true;
  }
</script>

<div class="graph-explorer">
  {#if loading}
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Loading knowledge graph...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <p>Failed to load graph</p>
      <p class="error-detail">{error}</p>
      <button class="retry-btn" on:click={loadGraph}>Retry</button>
    </div>
  {:else}
    <!-- Controls (Search + Filters) -->
    <div class="graph-controls-container">
      <GraphControls
        {nodes}
        {edges}
        on:create-relationship={handleCreateRelationship}
        on:refresh={loadGraph}
      />
    </div>

    <!-- Main Graph Area -->
    <div class="graph-main-area">
      <!-- Canvas (Force-Directed Graph) -->
      <div class="graph-canvas-container" class:with-panel={showNodeDetails}>
        <GraphCanvas
          {nodes}
          {edges}
          on:node-click={handleNodeClick}
          on:node-double-click={handleNodeDoubleClick}
          on:edge-click={handleEdgeClick}
        />
      </div>

      <!-- Node Details Panel (Slides in from right) -->
      {#if showNodeDetails}
        <div class="node-details-container">
          <GraphNodeDetails
            {edges}
            {nodes}
            on:close={handleCloseDetails}
            on:node-updated={handleNodeUpdated}
          />
        </div>
      {/if}
    </div>

    <!-- Relationship Editor Modal -->
    {#if showRelationshipEditor}
      <GraphRelationshipEditor
        mode={relationshipEditorMode}
        edge={selectedEdge}
        {nodes}
        on:created={handleRelationshipCreated}
        on:updated={handleRelationshipUpdated}
        on:deleted={handleRelationshipDeleted}
        on:close={handleCloseRelationshipEditor}
      />
    {/if}
  {/if}
</div>

<style>
  .graph-explorer {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary, #0f1419);
    position: relative;
  }

  /* Loading State */
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted, #6e7681);
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border, #2d3a47);
    border-top-color: var(--accent-cyan, #58a6ff);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: var(--space-3, 12px);
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Error State */
  .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted, #6e7681);
    text-align: center;
    padding: var(--space-4, 16px);
  }

  .error-state svg {
    color: var(--error, #f85149);
    margin-bottom: var(--space-3, 12px);
  }

  .error-detail {
    font-size: var(--text-xs, 11px);
    color: var(--error, #f85149);
    margin-top: var(--space-1, 4px);
  }

  .retry-btn {
    margin-top: var(--space-4, 16px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .retry-btn:hover {
    background: var(--accent-cyan-hover, #79b8ff);
    transform: translateY(-1px);
  }

  /* Layout Containers */
  .graph-controls-container {
    flex-shrink: 0;
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .graph-main-area {
    flex: 1;
    display: flex;
    position: relative;
    min-height: 0;
    overflow: hidden;
  }

  .graph-canvas-container {
    flex: 1;
    position: relative;
    min-height: 0;
    transition: margin-right 0.2s ease;
  }

  .graph-canvas-container.with-panel {
    margin-right: 320px;
  }

  .node-details-container {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 320px;
    background: var(--bg-secondary, #1a2027);
    border-left: 1px solid var(--border, #2d3a47);
    box-shadow: var(--shadow-lg, 0 8px 24px rgba(0, 0, 0, 0.4));
    z-index: 10;
    animation: slideIn 0.2s ease-out;
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%);
    }
    to {
      transform: translateX(0);
    }
  }
</style>
