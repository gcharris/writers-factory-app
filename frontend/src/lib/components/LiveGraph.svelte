<!--
  LiveGraph.svelte - Force-Directed Knowledge Graph Visualization

  Displays the knowledge graph with:
  - Force-directed layout (D3.js style physics)
  - Node types with distinct colors (CHARACTER, LOCATION, THEME, etc.)
  - Interactive pan/zoom
  - Node labels
  - Edge connections
-->
<script>
  import { onMount, onDestroy } from 'svelte';

  // Graph data
  let nodes = [];
  let edges = [];
  let loading = true;
  let error = '';

  // SVG dimensions
  let width = 0;
  let height = 0;
  let containerRef;

  // View state (pan/zoom)
  let viewX = 0;
  let viewY = 0;
  let scale = 1;
  let isDragging = false;
  let dragStart = { x: 0, y: 0 };

  // Selected node
  let selectedNode = null;

  // Physics simulation state
  let animationFrame;
  let simulationRunning = false;

  // Node type colors matching mockup
  const nodeColors = {
    CHARACTER: '#58a6ff',      // Cyan
    PERSON: '#58a6ff',
    LOCATION: '#a371f7',       // Purple
    PLACE: '#a371f7',
    THEME: '#d4a574',          // Gold
    PLOT_POINT: '#3fb950',     // Green
    EVENT: '#3fb950',
    OBJECT: '#f85149',         // Red
    ITEM: '#f85149',
    ORGANIZATION: '#d29922',   // Yellow
    CONCEPT: '#8b949e',        // Gray
    DEFAULT: '#6e7681'
  };

  onMount(async () => {
    await fetchGraphData();
    initializeSimulation();

    // Handle resize
    const resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        width = entry.contentRect.width;
        height = entry.contentRect.height;
        centerView();
      }
    });

    if (containerRef) {
      resizeObserver.observe(containerRef);
    }

    return () => {
      resizeObserver.disconnect();
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  });

  async function fetchGraphData() {
    loading = true;
    error = '';

    try {
      const res = await fetch('http://localhost:8000/graph/view');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();

      // Transform API data to visualization format
      nodes = (data.nodes || []).map((node, i) => ({
        id: node.id || `node-${i}`,
        label: node.id || node.label || 'Unknown',
        type: (node.type || 'DEFAULT').toUpperCase(),
        description: node.desc || node.description || '',
        // Initialize positions randomly
        x: Math.random() * 300 - 150,
        y: Math.random() * 300 - 150,
        vx: 0,
        vy: 0
      }));

      edges = (data.edges || []).map((edge, i) => ({
        id: `edge-${i}`,
        source: edge.source || edge.from,
        target: edge.target || edge.to,
        type: edge.type || edge.relation || ''
      }));

      loading = false;
      simulationRunning = true;
      runSimulation();
    } catch (e) {
      console.error('Failed to fetch graph:', e);
      error = e.message;
      loading = false;

      // Use sample data for demonstration
      createSampleData();
    }
  }

  function createSampleData() {
    // Sample data matching the mockup
    nodes = [
      { id: 'Mickey', label: 'Mickey', type: 'CHARACTER', x: 0, y: -50, vx: 0, vy: 0 },
      { id: 'Sarah', label: 'Sarah', type: 'CHARACTER', x: -80, y: 80, vx: 0, vy: 0 },
      { id: 'The Woman', label: 'The Woman', type: 'CHARACTER', x: 80, y: 60, vx: 0, vy: 0 },
      { id: 'Casino', label: 'Casino', type: 'LOCATION', x: -60, y: -80, vx: 0, vy: 0 },
      { id: 'Peer Occupation', label: 'Peer Occupation', type: 'CONCEPT', x: 20, y: 20, vx: 0, vy: 0 },
      { id: 'Current Witnessing', label: 'Current Witnessing', type: 'EVENT', x: 60, y: -30, vx: 0, vy: 0 },
    ];

    edges = [
      { id: 'e1', source: 'Mickey', target: 'Sarah', type: 'KNOWS' },
      { id: 'e2', source: 'Mickey', target: 'The Woman', type: 'MEETS' },
      { id: 'e3', source: 'Mickey', target: 'Casino', type: 'LOCATION' },
      { id: 'e4', source: 'Sarah', target: 'Peer Occupation', type: 'HAS' },
      { id: 'e5', source: 'The Woman', target: 'Current Witnessing', type: 'INVOLVED' },
      { id: 'e6', source: 'Peer Occupation', target: 'Current Witnessing', type: 'RELATES' },
    ];

    simulationRunning = true;
    runSimulation();
  }

  function initializeSimulation() {
    centerView();
  }

  function centerView() {
    if (width && height) {
      viewX = width / 2;
      viewY = height / 2;
    }
  }

  function runSimulation() {
    if (!simulationRunning) return;

    // Simple force-directed physics
    const repulsion = 50;
    const attraction = 0.05;
    const damping = 0.9;
    const centerForce = 0.01;

    // Node-node repulsion
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x;
        const dy = nodes[j].y - nodes[i].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = repulsion / (dist * dist);

        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        nodes[i].vx -= fx;
        nodes[i].vy -= fy;
        nodes[j].vx += fx;
        nodes[j].vy += fy;
      }
    }

    // Edge attraction
    for (const edge of edges) {
      const source = nodes.find(n => n.id === edge.source);
      const target = nodes.find(n => n.id === edge.target);

      if (source && target) {
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;

        const fx = dx * attraction;
        const fy = dy * attraction;

        source.vx += fx;
        source.vy += fy;
        target.vx -= fx;
        target.vy -= fy;
      }
    }

    // Center force
    for (const node of nodes) {
      node.vx -= node.x * centerForce;
      node.vy -= node.y * centerForce;
    }

    // Apply velocities with damping
    let totalMovement = 0;
    for (const node of nodes) {
      node.vx *= damping;
      node.vy *= damping;
      node.x += node.vx;
      node.y += node.vy;
      totalMovement += Math.abs(node.vx) + Math.abs(node.vy);
    }

    // Trigger reactivity
    nodes = nodes;

    // Continue simulation if nodes are still moving
    if (totalMovement > 0.1) {
      animationFrame = requestAnimationFrame(runSimulation);
    } else {
      simulationRunning = false;
    }
  }

  // Interaction handlers
  function handleMouseDown(e) {
    if (e.target.closest('.graph-node')) return;
    isDragging = true;
    dragStart = { x: e.clientX - viewX, y: e.clientY - viewY };
  }

  function handleMouseMove(e) {
    if (!isDragging) return;
    viewX = e.clientX - dragStart.x;
    viewY = e.clientY - dragStart.y;
  }

  function handleMouseUp() {
    isDragging = false;
  }

  function handleWheel(e) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    scale = Math.max(0.3, Math.min(3, scale * delta));
  }

  function selectNode(node) {
    selectedNode = selectedNode?.id === node.id ? null : node;
  }

  function getNodeColor(type) {
    return nodeColors[type] || nodeColors.DEFAULT;
  }

  function getEdgePath(edge) {
    const source = nodes.find(n => n.id === edge.source);
    const target = nodes.find(n => n.id === edge.target);

    if (!source || !target) return '';

    // Simple curved path
    const midX = (source.x + target.x) / 2;
    const midY = (source.y + target.y) / 2;
    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const offset = Math.min(20, Math.sqrt(dx * dx + dy * dy) * 0.1);

    // Perpendicular offset for curve
    const perpX = -dy / Math.sqrt(dx * dx + dy * dy) * offset;
    const perpY = dx / Math.sqrt(dx * dx + dy * dy) * offset;

    return `M ${source.x} ${source.y} Q ${midX + perpX} ${midY + perpY} ${target.x} ${target.y}`;
  }

  // Refresh graph
  function refreshGraph() {
    fetchGraphData();
  }
</script>

<div
  class="live-graph"
  bind:this={containerRef}
  on:mousedown={handleMouseDown}
  on:mousemove={handleMouseMove}
  on:mouseup={handleMouseUp}
  on:mouseleave={handleMouseUp}
  on:wheel={handleWheel}
>
  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <span>Loading graph...</span>
    </div>
  {:else if error && nodes.length === 0}
    <div class="error">
      <span class="error-icon">⚠</span>
      <span>{error}</span>
      <button on:click={refreshGraph}>Retry</button>
    </div>
  {:else if nodes.length === 0}
    <div class="empty">
      <span class="empty-icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </span>
      <span>No graph data yet</span>
      <span class="hint">Start a project to build your knowledge graph</span>
    </div>
  {:else}
    <svg class="graph-svg" {width} {height}>
      <g transform="translate({viewX}, {viewY}) scale({scale})">
        <!-- Edges -->
        {#each edges as edge}
          <path
            class="graph-edge"
            d={getEdgePath(edge)}
            fill="none"
          />
        {/each}

        <!-- Nodes -->
        {#each nodes as node}
          <g
            class="graph-node {selectedNode?.id === node.id ? 'selected' : ''}"
            transform="translate({node.x}, {node.y})"
            on:click={() => selectNode(node)}
          >
            <!-- Node circle -->
            <circle
              r="16"
              fill={getNodeColor(node.type)}
              opacity="0.2"
            />
            <circle
              r="8"
              fill={getNodeColor(node.type)}
            />

            <!-- Node label -->
            <text
              y="24"
              text-anchor="middle"
              class="node-label"
            >
              {node.label.length > 12 ? node.label.slice(0, 12) + '...' : node.label}
            </text>
          </g>
        {/each}
      </g>
    </svg>

    <!-- Controls -->
    <div class="graph-controls">
      <button on:click={() => scale = Math.min(3, scale * 1.2)} title="Zoom In">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          <line x1="11" y1="8" x2="11" y2="14"></line>
          <line x1="8" y1="11" x2="14" y2="11"></line>
        </svg>
      </button>
      <button on:click={() => scale = Math.max(0.3, scale * 0.8)} title="Zoom Out">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          <line x1="8" y1="11" x2="14" y2="11"></line>
        </svg>
      </button>
      <button on:click={centerView} title="Center">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <circle cx="12" cy="12" r="3"></circle>
        </svg>
      </button>
      <button on:click={refreshGraph} title="Refresh">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"></polyline>
          <polyline points="1 20 1 14 7 14"></polyline>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg>
      </button>
    </div>

    <!-- Node count -->
    <div class="graph-stats">
      <span class="stat">{nodes.length} nodes</span>
      <span class="stat">{edges.length} edges</span>
    </div>

    <!-- Selected node info -->
    {#if selectedNode}
      <div class="node-info">
        <div class="node-info-header" style="border-color: {getNodeColor(selectedNode.type)}">
          <span class="node-type" style="color: {getNodeColor(selectedNode.type)}">{selectedNode.type}</span>
          <span class="node-name">{selectedNode.label}</span>
        </div>
        {#if selectedNode.description}
          <div class="node-description">{selectedNode.description}</div>
        {/if}
      </div>
    {/if}
  {/if}
</div>

<style>
  .live-graph {
    position: relative;
    width: 100%;
    height: 100%;
    background: var(--bg-primary);
    overflow: hidden;
    cursor: grab;
    user-select: none;
  }

  .live-graph:active {
    cursor: grabbing;
  }

  .graph-svg {
    width: 100%;
    height: 100%;
  }

  /* Loading state */
  .loading {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    color: var(--text-muted);
    font-size: var(--text-xs);
  }

  .spinner {
    width: 24px;
    height: 24px;
    border: 2px solid var(--border);
    border-top-color: var(--accent-cyan);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Error state */
  .error {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    color: var(--text-muted);
    font-size: var(--text-xs);
  }

  .error-icon {
    color: var(--warning);
    font-size: var(--text-lg);
  }

  .error button {
    padding: var(--space-1) var(--space-3);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    font-size: var(--text-xs);
    cursor: pointer;
  }

  .error button:hover {
    background: var(--bg-elevated);
    color: var(--text-primary);
  }

  /* Empty state */
  .empty {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    color: var(--text-muted);
    font-size: var(--text-xs);
  }

  .empty-icon {
    color: var(--text-muted);
    opacity: 0.5;
  }

  .hint {
    font-size: 10px;
    color: var(--text-disabled);
  }

  /* Graph edges */
  .graph-edge {
    stroke: var(--border);
    stroke-width: 1;
    opacity: 0.6;
  }

  /* Graph nodes */
  .graph-node {
    cursor: pointer;
    transition: transform var(--transition-fast);
  }

  .graph-node:hover {
    transform: scale(1.1);
  }

  .graph-node.selected circle {
    stroke: var(--text-primary);
    stroke-width: 2;
  }

  .node-label {
    fill: var(--text-secondary);
    font-size: 10px;
    font-family: var(--font-ui);
    pointer-events: none;
  }

  /* Controls */
  .graph-controls {
    position: absolute;
    bottom: var(--space-2);
    right: var(--space-2);
    display: flex;
    gap: 2px;
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
    padding: 2px;
    box-shadow: var(--shadow-md);
  }

  .graph-controls button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .graph-controls button:hover {
    background: var(--bg-elevated);
    color: var(--text-primary);
  }

  /* Stats */
  .graph-stats {
    position: absolute;
    bottom: var(--space-2);
    left: var(--space-2);
    display: flex;
    gap: var(--space-2);
    font-size: 10px;
    color: var(--text-muted);
  }

  /* Node info popup */
  .node-info {
    position: absolute;
    top: var(--space-2);
    left: var(--space-2);
    max-width: 200px;
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    overflow: hidden;
  }

  .node-info-header {
    padding: var(--space-2);
    border-left: 3px solid;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .node-type {
    font-size: 9px;
    font-weight: var(--font-bold);
    letter-spacing: 0.5px;
  }

  .node-name {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
  }

  .node-description {
    padding: var(--space-2);
    font-size: var(--text-xs);
    color: var(--text-secondary);
    border-top: 1px solid var(--border);
  }
</style>
