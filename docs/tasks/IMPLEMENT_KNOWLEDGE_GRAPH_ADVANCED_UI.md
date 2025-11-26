# Implement Knowledge Graph Advanced UI

**Task**: Build interactive graph exploration and editing components
**Date**: 2025-11-26
**Priority**: High
**Estimated Effort**: 20-25 hours
**Assigned To**: Available for any agent (Gemini, Claude Code, etc.)

---

## Problem Statement

The current GraphPanel.svelte provides basic visualization using a force-directed graph, but lacks critical features for writers to effectively explore and manage their story's knowledge graph:

**Current Limitations:**
- ❌ Can't edit node properties (character traits, location details)
- ❌ Can't create/edit relationships between nodes
- ❌ No filtering (show only CHARACTERS, hide THEMES, etc.)
- ❌ No search (find "Mickey" or "quantum consciousness")
- ❌ No node details panel (click node → see all properties)
- ❌ Can't manually position important nodes

**Writers need:**
- ✅ Click node → edit its properties in a side panel
- ✅ Right-click → create relationship to another node
- ✅ Search bar → find nodes by name/type/content
- ✅ Filter checkboxes → show/hide node types
- ✅ Details panel → see all node data + connected nodes
- ✅ Drag-and-pin → lock important nodes in place

---

## Background: Current Implementation

### Existing GraphPanel.svelte
**Location:** `frontend/src/lib/components/GraphPanel.svelte`

**What it does:**
- Fetches graph data from `/graph/export`
- Renders nodes as circles with force-directed physics
- Shows node labels and relationship edges
- Allows dragging nodes (but they spring back)
- Click node → shows tooltip with basic info

**What we'll build on:**
- ✅ Keep the force-directed layout engine (it's good!)
- ✅ Keep the drag functionality (enhance it with pinning)
- ✅ Keep the visual style (cyber-noir theme)
- ➕ Add filtering, search, editing, and details panel

---

## Architecture Overview

### Component Breakdown (5 New Components)

```
GraphPanel.svelte (existing - minor updates)
├── GraphExplorer.svelte (NEW - main container)
│   ├── GraphCanvas.svelte (NEW - enhanced force-directed canvas)
│   ├── GraphControls.svelte (NEW - search + filters)
│   ├── GraphNodeDetails.svelte (NEW - node properties panel)
│   └── GraphRelationshipEditor.svelte (NEW - create/edit edges)
```

### Component Responsibilities

1. **GraphExplorer.svelte** - Main container with layout
2. **GraphCanvas.svelte** - Force-directed graph rendering with interactions
3. **GraphControls.svelte** - Search bar, filter checkboxes, zoom controls
4. **GraphNodeDetails.svelte** - Side panel showing selected node details
5. **GraphRelationshipEditor.svelte** - Modal for creating/editing relationships

---

## Implementation Plan

### Step 1: Create GraphExplorer.svelte (Main Container)

**File:** `frontend/src/lib/components/GraphExplorer.svelte`

**Purpose:** Layout container that coordinates all graph components

```svelte
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

  // Fetch graph data
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
  function handleNodeClick(node) {
    selectedNode.set(node);
    showNodeDetails = true;
  }

  function handleNodeDoubleClick(node) {
    selectedNode.set(node);
    showNodeDetails = true;
    // Could also trigger edit mode
  }

  function handleEdgeClick(edge) {
    selectedEdge = edge;
    relationshipEditorMode = 'edit';
    showRelationshipEditor = true;
  }

  function handleCreateRelationship() {
    relationshipEditorMode = 'create';
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

  // Subscribe to selected node changes
  selectedNode.subscribe(node => {
    showNodeDetails = !!node;
  });
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

    <!-- Canvas (Force-Directed Graph) -->
    <div class="graph-canvas-container">
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
          on:close={handleCloseDetails}
          on:node-updated={handleNodeUpdated}
        />
      </div>
    {/if}

    <!-- Relationship Editor Modal -->
    {#if showRelationshipEditor}
      <GraphRelationshipEditor
        mode={relationshipEditorMode}
        edge={selectedEdge}
        {nodes}
        on:created={handleRelationshipCreated}
        on:updated={handleRelationshipUpdated}
        on:deleted={handleRelationshipDeleted}
        on:close={() => showRelationshipEditor = false}
      />
    {/if}
  {/if}
</div>

<style>
  .graph-explorer {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary);
    position: relative;
  }

  /* Loading State */
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted);
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--accent-cyan);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: var(--space-3);
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
    color: var(--text-muted);
    text-align: center;
    padding: var(--space-4);
  }

  .error-state svg {
    color: var(--error);
    margin-bottom: var(--space-3);
  }

  .error-detail {
    font-size: var(--text-xs);
    color: var(--error);
    margin-top: var(--space-1);
  }

  .retry-btn {
    margin-top: var(--space-4);
    padding: var(--space-2) var(--space-4);
    background: var(--accent-cyan);
    color: var(--bg-primary);
    border: none;
    border-radius: var(--radius-md);
    font-weight: var(--font-semibold);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .retry-btn:hover {
    background: var(--accent-cyan-hover);
    transform: translateY(-1px);
  }

  /* Layout Containers */
  .graph-controls-container {
    flex-shrink: 0;
    border-bottom: 1px solid var(--border);
  }

  .graph-canvas-container {
    flex: 1;
    position: relative;
    min-height: 0;
  }

  .node-details-container {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 320px;
    background: var(--bg-secondary);
    border-left: 1px solid var(--border);
    box-shadow: var(--shadow-lg);
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
```

---

### Step 2: Create GraphControls.svelte (Search + Filters)

**File:** `frontend/src/lib/components/GraphControls.svelte`

**Purpose:** Search bar, node type filters, zoom controls

```svelte
<script>
  import { createEventDispatcher } from 'svelte';
  import { graphFilters, searchQuery } from '$lib/stores';

  export let nodes = [];
  export let edges = [];

  const dispatch = createEventDispatcher();

  // Filter state
  let nodeTypes = ['CHARACTER', 'LOCATION', 'THEME', 'EVENT', 'OBJECT', 'CONCEPT'];
  let enabledTypes = new Set(nodeTypes);

  // Search state
  let search = '';

  // Stats
  $: nodeCount = nodes.length;
  $: edgeCount = edges.length;
  $: visibleNodeCount = nodes.filter(n => enabledTypes.has(n.type)).length;

  // Update store when filters change
  $: {
    graphFilters.set({
      enabledTypes: Array.from(enabledTypes),
      searchQuery: search
    });
    searchQuery.set(search);
  }

  function toggleNodeType(type) {
    if (enabledTypes.has(type)) {
      enabledTypes.delete(type);
    } else {
      enabledTypes.add(type);
    }
    enabledTypes = enabledTypes; // Trigger reactivity
  }

  function toggleAll() {
    if (enabledTypes.size === nodeTypes.length) {
      enabledTypes.clear();
    } else {
      enabledTypes = new Set(nodeTypes);
    }
  }

  function clearSearch() {
    search = '';
  }

  // Node type colors (matching your theme)
  const typeColors = {
    CHARACTER: '#58a6ff', // cyan
    LOCATION: '#a371f7',  // purple
    THEME: '#d4a574',     // gold
    EVENT: '#3fb950',     // green
    OBJECT: '#8b949e',    // muted
    CONCEPT: '#f85149'    // red
  };
</script>

<div class="graph-controls">
  <!-- Search Bar -->
  <div class="search-section">
    <div class="search-input-wrapper">
      <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.35-4.35"></path>
      </svg>
      <input
        type="text"
        bind:value={search}
        placeholder="Search nodes..."
        class="search-input"
      />
      {#if search}
        <button class="clear-search-btn" on:click={clearSearch} title="Clear search">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      {/if}
    </div>
  </div>

  <!-- Node Type Filters -->
  <div class="filters-section">
    <div class="filter-header">
      <span class="filter-label">Show:</span>
      <button class="toggle-all-btn" on:click={toggleAll}>
        {enabledTypes.size === nodeTypes.length ? 'Hide All' : 'Show All'}
      </button>
    </div>
    <div class="filter-chips">
      {#each nodeTypes as type}
        <button
          class="filter-chip"
          class:active={enabledTypes.has(type)}
          style="--chip-color: {typeColors[type]}"
          on:click={() => toggleNodeType(type)}
        >
          <span class="chip-dot" style="background: {typeColors[type]}"></span>
          {type}
        </button>
      {/each}
    </div>
  </div>

  <!-- Stats + Actions -->
  <div class="actions-section">
    <div class="stats">
      <span class="stat">{visibleNodeCount}/{nodeCount} nodes</span>
      <span class="stat-sep">·</span>
      <span class="stat">{edgeCount} edges</span>
    </div>
    <div class="action-buttons">
      <button
        class="action-btn"
        on:click={() => dispatch('create-relationship')}
        title="Create new relationship"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Add Link
      </button>
      <button
        class="action-btn"
        on:click={() => dispatch('refresh')}
        title="Refresh graph"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"></path>
        </svg>
        Refresh
      </button>
    </div>
  </div>
</div>

<style>
  .graph-controls {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-3) var(--space-4);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
  }

  /* Search Section */
  .search-section {
    flex-shrink: 0;
  }

  .search-input-wrapper {
    position: relative;
    width: 240px;
  }

  .search-icon {
    position: absolute;
    left: var(--space-2);
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
  }

  .search-input {
    width: 100%;
    padding: 6px var(--space-2) 6px 34px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    transition: all var(--transition-fast);
  }

  .search-input:focus {
    outline: none;
    border-color: var(--accent-cyan);
    background: var(--bg-primary);
  }

  .clear-search-btn {
    position: absolute;
    right: var(--space-2);
    top: 50%;
    transform: translateY(-50%);
    padding: 2px;
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    transition: color var(--transition-fast);
  }

  .clear-search-btn:hover {
    color: var(--text-primary);
  }

  /* Filters Section */
  .filters-section {
    flex: 1;
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .filter-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .filter-label {
    font-size: var(--text-xs);
    color: var(--text-muted);
    font-weight: var(--font-semibold);
  }

  .toggle-all-btn {
    padding: 2px var(--space-2);
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: var(--text-xs);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .toggle-all-btn:hover {
    border-color: var(--accent-cyan);
    color: var(--accent-cyan);
  }

  .filter-chips {
    display: flex;
    gap: var(--space-2);
    flex-wrap: wrap;
  }

  .filter-chip {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px var(--space-2);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-muted);
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .filter-chip:hover {
    background: var(--bg-elevated);
    border-color: var(--border-strong);
  }

  .filter-chip.active {
    background: color-mix(in srgb, var(--chip-color) 15%, transparent);
    border-color: var(--chip-color);
    color: var(--text-primary);
  }

  .chip-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    opacity: 0.5;
  }

  .filter-chip.active .chip-dot {
    opacity: 1;
  }

  /* Actions Section */
  .actions-section {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    flex-shrink: 0;
  }

  .stats {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    font-size: var(--text-xs);
    color: var(--text-muted);
    font-family: var(--font-mono);
  }

  .stat-sep {
    opacity: 0.5;
  }

  .action-buttons {
    display: flex;
    gap: var(--space-2);
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px var(--space-3);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .action-btn:hover {
    background: var(--accent-cyan);
    border-color: var(--accent-cyan);
    color: var(--bg-primary);
    transform: translateY(-1px);
  }
</style>
```

---

### Step 3: Create stores.js additions

**File:** `frontend/src/lib/stores.js`

Add these new stores (if not already present):

```javascript
// Knowledge Graph stores
export const selectedNode = writable(null);
export const graphFilters = writable({
  enabledTypes: ['CHARACTER', 'LOCATION', 'THEME', 'EVENT', 'OBJECT', 'CONCEPT'],
  searchQuery: ''
});
export const searchQuery = writable('');
```

---

### Step 4: Create GraphCanvas.svelte (Enhanced Force-Directed Graph)

**File:** `frontend/src/lib/components/GraphCanvas.svelte`

**Purpose:** Canvas-based force-directed graph with interactions

**Key Features:**
- Force-directed layout simulation
- Drag nodes (with pinning on double-click)
- Click node → emit event
- Click edge → emit event
- Apply filters from store
- Apply search highlighting

**Note:** This component is complex (~400-500 lines). Here's the structure:

```svelte
<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { graphFilters, searchQuery } from '$lib/stores';

  export let nodes = [];
  export let edges = [];

  const dispatch = createEventDispatcher();

  let canvas;
  let ctx;
  let width = 800;
  let height = 600;

  // Physics simulation variables
  let simulation;
  let simulationNodes = [];
  let simulationEdges = [];

  // Interaction state
  let draggedNode = null;
  let hoveredNode = null;
  let pinnedNodes = new Set();

  // Filter state
  let enabledTypes = new Set();
  let search = '';

  // Subscribe to stores
  graphFilters.subscribe(filters => {
    enabledTypes = new Set(filters.enabledTypes);
  });

  searchQuery.subscribe(q => {
    search = q.toLowerCase();
  });

  // Initialize simulation on mount
  onMount(() => {
    initCanvas();
    initSimulation();
    startAnimationLoop();
  });

  onDestroy(() => {
    stopAnimationLoop();
  });

  function initCanvas() {
    if (!canvas) return;
    ctx = canvas.getContext('2d');
    resizeCanvas();
  }

  function resizeCanvas() {
    if (!canvas) return;
    width = canvas.parentElement.clientWidth;
    height = canvas.parentElement.clientHeight;
    canvas.width = width;
    canvas.height = height;
  }

  function initSimulation() {
    // Convert nodes/edges to simulation format with physics
    simulationNodes = nodes.map((n, i) => ({
      ...n,
      x: width / 2 + Math.random() * 100 - 50,
      y: height / 2 + Math.random() * 100 - 50,
      vx: 0,
      vy: 0,
      radius: getNodeRadius(n)
    }));

    simulationEdges = edges.map(e => ({
      ...e,
      source: simulationNodes.find(n => n.id === e.source),
      target: simulationNodes.find(n => n.id === e.target)
    }));

    // Start physics simulation (simplified)
    simulation = setInterval(updatePhysics, 16); // ~60fps
  }

  function updatePhysics() {
    // Apply forces: repulsion, attraction (edges), centering
    // This is a simplified physics engine - use d3-force or similar for production

    const centerForce = 0.01;
    const repulsionStrength = 5000;
    const edgeStrength = 0.1;
    const damping = 0.9;

    // Center force
    simulationNodes.forEach(node => {
      if (pinnedNodes.has(node.id) || node === draggedNode) return;

      const dx = width / 2 - node.x;
      const dy = height / 2 - node.y;
      node.vx += dx * centerForce;
      node.vy += dy * centerForce;
    });

    // Repulsion between nodes
    for (let i = 0; i < simulationNodes.length; i++) {
      for (let j = i + 1; j < simulationNodes.length; j++) {
        const a = simulationNodes[i];
        const b = simulationNodes[j];
        if (pinnedNodes.has(a.id) && pinnedNodes.has(b.id)) continue;

        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = repulsionStrength / (dist * dist);

        if (!pinnedNodes.has(a.id) && a !== draggedNode) {
          a.vx -= (dx / dist) * force;
          a.vy -= (dy / dist) * force;
        }
        if (!pinnedNodes.has(b.id) && b !== draggedNode) {
          b.vx += (dx / dist) * force;
          b.vy += (dy / dist) * force;
        }
      }
    }

    // Edge attraction
    simulationEdges.forEach(edge => {
      const { source, target } = edge;
      if (!source || !target) return;
      if (pinnedNodes.has(source.id) && pinnedNodes.has(target.id)) return;

      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = (dist - 100) * edgeStrength;

      if (!pinnedNodes.has(source.id) && source !== draggedNode) {
        source.vx += (dx / dist) * force;
        source.vy += (dy / dist) * force;
      }
      if (!pinnedNodes.has(target.id) && target !== draggedNode) {
        target.vx -= (dx / dist) * force;
        target.vy -= (dy / dist) * force;
      }
    });

    // Update positions
    simulationNodes.forEach(node => {
      if (pinnedNodes.has(node.id) || node === draggedNode) return;

      node.x += node.vx;
      node.y += node.vy;
      node.vx *= damping;
      node.vy *= damping;

      // Boundary constraints
      node.x = Math.max(node.radius, Math.min(width - node.radius, node.x));
      node.y = Math.max(node.radius, Math.min(height - node.radius, node.y));
    });
  }

  function startAnimationLoop() {
    function animate() {
      if (!ctx) return;
      render();
      requestAnimationFrame(animate);
    }
    animate();
  }

  function stopAnimationLoop() {
    if (simulation) clearInterval(simulation);
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    // Apply filters
    const visibleNodes = simulationNodes.filter(n => enabledTypes.has(n.type));
    const visibleEdges = simulationEdges.filter(e =>
      e.source && e.target &&
      enabledTypes.has(e.source.type) &&
      enabledTypes.has(e.target.type)
    );

    // Draw edges
    ctx.strokeStyle = '#2d3a47';
    ctx.lineWidth = 1;
    visibleEdges.forEach(edge => {
      ctx.beginPath();
      ctx.moveTo(edge.source.x, edge.source.y);
      ctx.lineTo(edge.target.x, edge.target.y);
      ctx.stroke();
    });

    // Draw nodes
    visibleNodes.forEach(node => {
      const isHovered = node === hoveredNode;
      const isSearchMatch = search && node.name.toLowerCase().includes(search);
      const isPinned = pinnedNodes.has(node.id);

      // Node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);
      ctx.fillStyle = getNodeColor(node.type, isHovered || isSearchMatch);
      ctx.fill();

      if (isPinned) {
        ctx.strokeStyle = '#d4a574'; // Gold for pinned
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Node label
      ctx.fillStyle = '#e6edf3';
      ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.name, node.x, node.y + node.radius + 12);

      // Search highlight
      if (isSearchMatch) {
        ctx.strokeStyle = '#58a6ff'; // Cyan highlight
        ctx.lineWidth = 3;
        ctx.stroke();
      }
    });
  }

  function getNodeColor(type, highlighted) {
    const colors = {
      CHARACTER: '#58a6ff',
      LOCATION: '#a371f7',
      THEME: '#d4a574',
      EVENT: '#3fb950',
      OBJECT: '#8b949e',
      CONCEPT: '#f85149'
    };
    const baseColor = colors[type] || '#8b949e';
    return highlighted ? baseColor : baseColor + '99'; // Add transparency if not highlighted
  }

  function getNodeRadius(node) {
    // Size by importance or connection count
    const baseRadius = 20;
    const connections = edges.filter(e => e.source === node.id || e.target === node.id).length;
    return baseRadius + Math.min(connections * 2, 20);
  }

  // Mouse interaction handlers
  function handleMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const node = findNodeAt(x, y);
    if (node) {
      draggedNode = node;
    }
  }

  function handleMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (draggedNode) {
      draggedNode.x = x;
      draggedNode.y = y;
      draggedNode.vx = 0;
      draggedNode.vy = 0;
    } else {
      hoveredNode = findNodeAt(x, y);
    }
  }

  function handleMouseUp() {
    draggedNode = null;
  }

  function handleClick(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const node = findNodeAt(x, y);
    if (node) {
      dispatch('node-click', node);
    }
  }

  function handleDoubleClick(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const node = findNodeAt(x, y);
    if (node) {
      // Pin/unpin node
      if (pinnedNodes.has(node.id)) {
        pinnedNodes.delete(node.id);
      } else {
        pinnedNodes.add(node.id);
      }
      pinnedNodes = pinnedNodes; // Trigger reactivity
      dispatch('node-double-click', node);
    }
  }

  function findNodeAt(x, y) {
    return simulationNodes.find(node => {
      const dx = node.x - x;
      const dy = node.y - y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      return dist <= node.radius;
    });
  }

  // Update simulation when nodes/edges change
  $: if (nodes && edges) {
    initSimulation();
  }
</script>

<canvas
  bind:this={canvas}
  on:mousedown={handleMouseDown}
  on:mousemove={handleMouseMove}
  on:mouseup={handleMouseUp}
  on:click={handleClick}
  on:dblclick={handleDoubleClick}
  class="graph-canvas"
></canvas>

<style>
  .graph-canvas {
    width: 100%;
    height: 100%;
    cursor: grab;
  }

  .graph-canvas:active {
    cursor: grabbing;
  }
</style>
```

---

### Step 5: Create GraphNodeDetails.svelte (Node Properties Panel)

**File:** `frontend/src/lib/components/GraphNodeDetails.svelte`

**Purpose:** Side panel showing selected node details with editing

```svelte
<script>
  import { createEventDispatcher } from 'svelte';
  import { selectedNode } from '$lib/stores';

  const dispatch = createEventDispatcher();

  let node = null;
  let editing = false;
  let editedProperties = {};
  let saving = false;

  // Subscribe to selected node
  selectedNode.subscribe(n => {
    node = n;
    if (node) {
      editedProperties = { ...node.properties };
    }
  });

  async function saveChanges() {
    if (!node) return;

    saving = true;
    try {
      const response = await fetch(`http://localhost:8000/graph/nodes/${node.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ properties: editedProperties })
      });

      if (!response.ok) throw new Error('Failed to update node');

      const updatedNode = await response.json();
      dispatch('node-updated', updatedNode);
      editing = false;
    } catch (e) {
      console.error('Save failed:', e);
      alert('Failed to save changes: ' + e.message);
    } finally {
      saving = false;
    }
  }

  function cancelEdit() {
    editedProperties = { ...node.properties };
    editing = false;
  }

  function close() {
    dispatch('close');
  }

  // Get connected nodes
  $: connectedNodes = node ? getConnectedNodes(node.id) : [];

  function getConnectedNodes(nodeId) {
    // This would come from edges data - simplified here
    return [];
  }
</script>

{#if node}
  <div class="node-details-panel">
    <!-- Header -->
    <div class="panel-header">
      <div class="header-content">
        <span class="node-type-badge" style="background: {getTypeColor(node.type)}">{node.type}</span>
        <h3 class="node-name">{node.name}</h3>
      </div>
      <button class="close-btn" on:click={close} title="Close">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="panel-content">
      <!-- Properties Section -->
      <div class="section">
        <div class="section-header">
          <h4 class="section-title">Properties</h4>
          {#if !editing}
            <button class="edit-btn" on:click={() => editing = true}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Edit
            </button>
          {/if}
        </div>

        <div class="properties-list">
          {#each Object.entries(editedProperties) as [key, value]}
            <div class="property-item">
              <div class="property-key">{key}</div>
              {#if editing}
                <textarea
                  bind:value={editedProperties[key]}
                  class="property-value-input"
                  rows="2"
                ></textarea>
              {:else}
                <div class="property-value">{value}</div>
              {/if}
            </div>
          {/each}
        </div>

        {#if editing}
          <div class="edit-actions">
            <button class="save-btn" on:click={saveChanges} disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            <button class="cancel-btn" on:click={cancelEdit}>Cancel</button>
          </div>
        {/if}
      </div>

      <!-- Connected Nodes Section -->
      <div class="section">
        <h4 class="section-title">Connected Nodes ({connectedNodes.length})</h4>
        {#if connectedNodes.length > 0}
          <div class="connected-list">
            {#each connectedNodes as connected}
              <div class="connected-item">
                <span class="connected-type-dot" style="background: {getTypeColor(connected.type)}"></span>
                <span class="connected-name">{connected.name}</span>
                <span class="connected-relationship">{connected.relationship}</span>
              </div>
            {/each}
          </div>
        {:else}
          <p class="empty-message">No connections</p>
        {/if}
      </div>

      <!-- Metadata Section -->
      <div class="section">
        <h4 class="section-title">Metadata</h4>
        <div class="metadata-grid">
          <div class="metadata-item">
            <span class="metadata-label">ID</span>
            <span class="metadata-value">{node.id}</span>
          </div>
          <div class="metadata-item">
            <span class="metadata-label">Created</span>
            <span class="metadata-value">{node.created || 'Unknown'}</span>
          </div>
          <div class="metadata-item">
            <span class="metadata-label">Updated</span>
            <span class="metadata-value">{node.updated || 'Unknown'}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<script context="module">
  function getTypeColor(type) {
    const colors = {
      CHARACTER: '#58a6ff',
      LOCATION: '#a371f7',
      THEME: '#d4a574',
      EVENT: '#3fb950',
      OBJECT: '#8b949e',
      CONCEPT: '#f85149'
    };
    return colors[type] || '#8b949e';
  }
</script>

<style>
  .node-details-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-secondary);
  }

  /* Header */
  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    border-bottom: 1px solid var(--border);
  }

  .header-content {
    flex: 1;
  }

  .node-type-badge {
    display: inline-block;
    padding: 2px var(--space-2);
    border-radius: var(--radius-sm);
    color: var(--bg-primary);
    font-size: var(--text-xs);
    font-weight: var(--font-bold);
    text-transform: uppercase;
    margin-bottom: var(--space-1);
  }

  .node-name {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  .close-btn {
    padding: var(--space-1);
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    transition: color var(--transition-fast);
  }

  .close-btn:hover {
    color: var(--text-primary);
  }

  /* Content */
  .panel-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4);
  }

  .section {
    margin-bottom: var(--space-6);
  }

  .section:last-child {
    margin-bottom: 0;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-3);
  }

  .section-title {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0;
  }

  .edit-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px var(--space-2);
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: var(--text-xs);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .edit-btn:hover {
    border-color: var(--accent-cyan);
    color: var(--accent-cyan);
  }

  /* Properties */
  .properties-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .property-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .property-key {
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .property-value {
    font-size: var(--text-sm);
    color: var(--text-primary);
    line-height: 1.6;
  }

  .property-value-input {
    width: 100%;
    padding: var(--space-2);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    font-family: inherit;
    resize: vertical;
  }

  .property-value-input:focus {
    outline: none;
    border-color: var(--accent-cyan);
  }

  .edit-actions {
    display: flex;
    gap: var(--space-2);
    margin-top: var(--space-3);
  }

  .save-btn,
  .cancel-btn {
    flex: 1;
    padding: var(--space-2) var(--space-3);
    border: none;
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .save-btn {
    background: var(--accent-cyan);
    color: var(--bg-primary);
  }

  .save-btn:hover:not(:disabled) {
    background: var(--accent-cyan-hover);
    transform: translateY(-1px);
  }

  .save-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .cancel-btn {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
  }

  .cancel-btn:hover {
    background: var(--bg-elevated);
  }

  /* Connected Nodes */
  .connected-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .connected-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2);
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
  }

  .connected-type-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .connected-name {
    flex: 1;
    font-size: var(--text-sm);
    color: var(--text-primary);
  }

  .connected-relationship {
    font-size: var(--text-xs);
    color: var(--text-muted);
    font-style: italic;
  }

  .empty-message {
    font-size: var(--text-sm);
    color: var(--text-muted);
    font-style: italic;
    margin: 0;
  }

  /* Metadata */
  .metadata-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .metadata-item {
    display: flex;
    justify-content: space-between;
    padding: var(--space-2);
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
  }

  .metadata-label {
    font-size: var(--text-xs);
    color: var(--text-muted);
    font-weight: var(--font-semibold);
  }

  .metadata-value {
    font-size: var(--text-xs);
    color: var(--text-secondary);
    font-family: var(--font-mono);
  }
</style>
```

---

## Step 6: Create GraphRelationshipEditor.svelte (Modal)

**File:** `frontend/src/lib/components/GraphRelationshipEditor.svelte`

**(Simplified version - full spec continues in next section...)**

This component handles creating and editing edges between nodes. It's a modal overlay with:
- Source/target node selection (dropdowns)
- Relationship type input
- Properties editor
- Save/Delete/Cancel buttons

---

## Testing Checklist

After implementation, verify:

- [ ] **Graph loads** - Nodes and edges render correctly
- [ ] **Search works** - Type "Mickey" → node highlights
- [ ] **Filters work** - Uncheck "CHARACTER" → characters hide
- [ ] **Node click** - Click node → details panel slides in
- [ ] **Node drag** - Drag node → moves smoothly
- [ ] **Node pin** - Double-click node → stays in place (gold border)
- [ ] **Edit properties** - Click "Edit" → change property → save → updates in graph
- [ ] **Create relationship** - Click "Add Link" → select nodes → save → new edge appears
- [ ] **Edge click** - Click edge → relationship editor opens
- [ ] **Performance** - 100+ nodes render smoothly at 60fps
- [ ] **Responsive** - Resizing window updates canvas dimensions

---

## API Endpoints Required

### Existing (Already Implemented)
- `GET /graph/export` - Get full graph data ✅

### New (Need to Add)
- `PATCH /graph/nodes/{id}` - Update node properties
- `POST /graph/relationships` - Create new relationship
- `PATCH /graph/relationships/{id}` - Update relationship
- `DELETE /graph/relationships/{id}` - Delete relationship

**Backend Task:** Add these 4 endpoints to `backend/api.py` (simple CRUD operations)

---

## Files Summary

**New Files (5):**
1. `GraphExplorer.svelte` (~250 lines) - Main container
2. `GraphControls.svelte` (~300 lines) - Search + filters
3. `GraphCanvas.svelte` (~500 lines) - Force-directed canvas
4. `GraphNodeDetails.svelte` (~350 lines) - Details panel
5. `GraphRelationshipEditor.svelte` (~250 lines) - Relationship modal

**Modified Files (2):**
1. `stores.js` - Add `selectedNode`, `graphFilters`, `searchQuery`
2. `GraphPanel.svelte` - Replace content with `<GraphExplorer />`

**Total Estimated Lines:** ~1,650 lines of new Svelte code

**Estimated Effort:** 20-25 hours (including testing and refinement)

---

## Common Issues & Solutions

### Issue 1: Canvas not resizing
**Solution:** Add window resize listener in `GraphCanvas.svelte`

### Issue 2: Physics simulation lags with 100+ nodes
**Solution:** Use Web Workers for physics calculations or reduce simulation frequency

### Issue 3: Pinned nodes drift slightly
**Solution:** Set `vx = 0, vy = 0` in `updatePhysics()` for pinned nodes

### Issue 4: Search highlighting not visible
**Solution:** Increase stroke width and use brighter color (#58a6ff)

---

## Future Enhancements (Not in this task)

- Minimap (bird's-eye view of full graph)
- Zoom controls (mouse wheel or pinch)
- Export graph as image (PNG/SVG)
- Layout algorithms (hierarchical, radial, force-atlas)
- Time-based filtering (show graph state at Chapter 5)
- Community detection (cluster related nodes with colors)

---

## Reference

- D3.js force-directed graphs: https://d3js.org/d3-force
- Canvas API: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- Graph visualization best practices: https://graphviz.org/

The goal: **Interactive, professional-grade graph exploration** that lets writers understand and manage their story's knowledge structure.

---

*Spec created: 2025-11-26 by Claude Code*
*Ready for implementation by: Gemini, Claude Code, Claude Cloud, or any available agent*
