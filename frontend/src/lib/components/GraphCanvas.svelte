<!--
  GraphCanvas.svelte - Canvas-based Force-Directed Graph

  Features:
  - Force-directed physics simulation
  - Drag nodes around
  - Double-click to pin/unpin nodes
  - Click node to select
  - Click edge to select
  - Filter by node type
  - Search highlighting
  - Zoom with mouse wheel
-->
<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { graphFilters, searchQuery, pinnedNodes } from '$lib/stores';

  export let nodes = [];
  export let edges = [];

  const dispatch = createEventDispatcher();

  let canvas;
  let ctx;
  let width = 800;
  let height = 600;
  let animationFrameId;
  let physicsInterval;

  // Simulation state
  let simulationNodes = [];
  let simulationEdges = [];

  // Interaction state
  let draggedNode = null;
  let hoveredNode = null;
  let hoveredEdge = null;
  let localPinnedNodes = new Set();

  // View state
  let zoom = 1;
  let panX = 0;
  let panY = 0;
  let isPanning = false;
  let lastMouseX = 0;
  let lastMouseY = 0;

  // Filter state
  let enabledTypes = new Set(['CHARACTER', 'LOCATION', 'THEME', 'EVENT', 'OBJECT', 'CONCEPT']);
  let search = '';

  // Subscribe to stores
  const unsubFilters = graphFilters.subscribe(filters => {
    enabledTypes = new Set(filters.enabledTypes);
  });

  const unsubSearch = searchQuery.subscribe(q => {
    search = q?.toLowerCase() || '';
  });

  const unsubPinned = pinnedNodes.subscribe(pins => {
    localPinnedNodes = pins;
  });

  // Node type colors
  const typeColors = {
    CHARACTER: '#58a6ff',
    LOCATION: '#a371f7',
    THEME: '#d4a574',
    EVENT: '#3fb950',
    OBJECT: '#8b949e',
    CONCEPT: '#f85149'
  };

  onMount(() => {
    initCanvas();
    initSimulation();
    startAnimationLoop();
    window.addEventListener('resize', handleResize);
  });

  onDestroy(() => {
    stopAnimationLoop();
    window.removeEventListener('resize', handleResize);
    unsubFilters();
    unsubSearch();
    unsubPinned();
  });

  function handleResize() {
    resizeCanvas();
  }

  function initCanvas() {
    if (!canvas) return;
    ctx = canvas.getContext('2d');
    resizeCanvas();
  }

  function resizeCanvas() {
    if (!canvas || !canvas.parentElement) return;
    width = canvas.parentElement.clientWidth;
    height = canvas.parentElement.clientHeight;
    canvas.width = width;
    canvas.height = height;
  }

  function initSimulation() {
    // Convert nodes to simulation format with physics properties
    simulationNodes = nodes.map((n, i) => {
      // Spread nodes in a circle pattern initially
      const angle = (i / nodes.length) * 2 * Math.PI;
      const radius = Math.min(width, height) * 0.3;
      return {
        ...n,
        x: width / 2 + Math.cos(angle) * radius + (Math.random() - 0.5) * 50,
        y: height / 2 + Math.sin(angle) * radius + (Math.random() - 0.5) * 50,
        vx: 0,
        vy: 0,
        radius: getNodeRadius(n)
      };
    });

    // Link edges to node objects
    simulationEdges = edges.map(e => ({
      ...e,
      source: simulationNodes.find(n => n.id === e.source_id || n.id === e.source),
      target: simulationNodes.find(n => n.id === e.target_id || n.id === e.target)
    })).filter(e => e.source && e.target);

    // Start physics simulation
    if (physicsInterval) clearInterval(physicsInterval);
    physicsInterval = setInterval(updatePhysics, 16); // ~60fps
  }

  function updatePhysics() {
    const centerForce = 0.005;
    const repulsionStrength = 8000;
    const edgeStrength = 0.05;
    const idealEdgeLength = 150;
    const damping = 0.85;

    // Filter visible nodes
    const visibleNodes = simulationNodes.filter(n => enabledTypes.has(n.type?.toUpperCase()));

    // Center force - pull nodes toward center
    visibleNodes.forEach(node => {
      if (localPinnedNodes.has(node.id) || node === draggedNode) return;

      const dx = width / 2 - node.x;
      const dy = height / 2 - node.y;
      node.vx += dx * centerForce;
      node.vy += dy * centerForce;
    });

    // Repulsion between nodes
    for (let i = 0; i < visibleNodes.length; i++) {
      for (let j = i + 1; j < visibleNodes.length; j++) {
        const a = visibleNodes[i];
        const b = visibleNodes[j];

        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const minDist = a.radius + b.radius + 30;

        if (dist < minDist * 3) {
          const force = repulsionStrength / (dist * dist);

          if (!localPinnedNodes.has(a.id) && a !== draggedNode) {
            a.vx -= (dx / dist) * force;
            a.vy -= (dy / dist) * force;
          }
          if (!localPinnedNodes.has(b.id) && b !== draggedNode) {
            b.vx += (dx / dist) * force;
            b.vy += (dy / dist) * force;
          }
        }
      }
    }

    // Edge attraction - connected nodes pull together
    simulationEdges.forEach(edge => {
      const { source, target } = edge;
      if (!source || !target) return;
      if (!enabledTypes.has(source.type?.toUpperCase()) || !enabledTypes.has(target.type?.toUpperCase())) return;

      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = (dist - idealEdgeLength) * edgeStrength;

      if (!localPinnedNodes.has(source.id) && source !== draggedNode) {
        source.vx += (dx / dist) * force;
        source.vy += (dy / dist) * force;
      }
      if (!localPinnedNodes.has(target.id) && target !== draggedNode) {
        target.vx -= (dx / dist) * force;
        target.vy -= (dy / dist) * force;
      }
    });

    // Update positions
    visibleNodes.forEach(node => {
      if (localPinnedNodes.has(node.id) || node === draggedNode) {
        node.vx = 0;
        node.vy = 0;
        return;
      }

      node.x += node.vx;
      node.y += node.vy;
      node.vx *= damping;
      node.vy *= damping;

      // Boundary constraints (with padding)
      const padding = node.radius + 20;
      node.x = Math.max(padding, Math.min(width - padding, node.x));
      node.y = Math.max(padding, Math.min(height - padding, node.y));
    });
  }

  function startAnimationLoop() {
    function animate() {
      if (!ctx) return;
      render();
      animationFrameId = requestAnimationFrame(animate);
    }
    animate();
  }

  function stopAnimationLoop() {
    if (animationFrameId) cancelAnimationFrame(animationFrameId);
    if (physicsInterval) clearInterval(physicsInterval);
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    // Apply zoom and pan
    ctx.save();
    ctx.translate(panX, panY);
    ctx.scale(zoom, zoom);

    // Filter visible nodes
    const visibleNodes = simulationNodes.filter(n => enabledTypes.has(n.type?.toUpperCase()));
    const visibleEdges = simulationEdges.filter(e =>
      e.source && e.target &&
      enabledTypes.has(e.source.type?.toUpperCase()) &&
      enabledTypes.has(e.target.type?.toUpperCase())
    );

    // Draw edges first (behind nodes)
    visibleEdges.forEach(edge => {
      const isHovered = edge === hoveredEdge;

      ctx.beginPath();
      ctx.moveTo(edge.source.x, edge.source.y);
      ctx.lineTo(edge.target.x, edge.target.y);
      ctx.strokeStyle = isHovered ? '#58a6ff' : '#3d4a57';
      ctx.lineWidth = isHovered ? 2 : 1;
      ctx.stroke();

      // Draw edge label if hovered
      if (isHovered && edge.label) {
        const midX = (edge.source.x + edge.target.x) / 2;
        const midY = (edge.source.y + edge.target.y) / 2;
        ctx.fillStyle = '#8b949e';
        ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(edge.label || edge.relationship || '', midX, midY - 5);
      }
    });

    // Draw nodes
    visibleNodes.forEach(node => {
      const isHovered = node === hoveredNode;
      const isSearchMatch = search && node.name?.toLowerCase().includes(search);
      const isPinned = localPinnedNodes.has(node.id);
      const nodeColor = typeColors[node.type?.toUpperCase()] || '#8b949e';

      // Node glow for search matches
      if (isSearchMatch) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + 8, 0, 2 * Math.PI);
        ctx.fillStyle = nodeColor + '40';
        ctx.fill();
      }

      // Node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);

      // Fill with gradient for depth
      const gradient = ctx.createRadialGradient(
        node.x - node.radius * 0.3, node.y - node.radius * 0.3, 0,
        node.x, node.y, node.radius
      );
      gradient.addColorStop(0, isHovered ? nodeColor : nodeColor + 'cc');
      gradient.addColorStop(1, isHovered ? nodeColor + 'cc' : nodeColor + '80');
      ctx.fillStyle = gradient;
      ctx.fill();

      // Border
      if (isPinned) {
        ctx.strokeStyle = '#d4a574'; // Gold for pinned
        ctx.lineWidth = 3;
        ctx.stroke();
      } else if (isSearchMatch) {
        ctx.strokeStyle = '#58a6ff';
        ctx.lineWidth = 3;
        ctx.stroke();
      } else if (isHovered) {
        ctx.strokeStyle = '#e6edf3';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Pin icon for pinned nodes
      if (isPinned) {
        ctx.fillStyle = '#d4a574';
        ctx.font = '10px -apple-system';
        ctx.textAlign = 'center';
        ctx.fillText('📌', node.x, node.y - node.radius - 8);
      }

      // Node label
      ctx.fillStyle = isHovered || isSearchMatch ? '#e6edf3' : '#c9d1d9';
      ctx.font = `${isHovered ? '12px' : '11px'} -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';

      // Truncate long names
      let displayName = node.name || 'Unknown';
      if (displayName.length > 15) {
        displayName = displayName.substring(0, 12) + '...';
      }
      ctx.fillText(displayName, node.x, node.y + node.radius + 6);

      // Type label (smaller, below name)
      if (isHovered) {
        ctx.fillStyle = nodeColor;
        ctx.font = '9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.fillText(node.type || '', node.x, node.y + node.radius + 20);
      }
    });

    ctx.restore();

    // Draw zoom indicator
    ctx.fillStyle = '#6e7681';
    ctx.font = '10px -apple-system';
    ctx.textAlign = 'right';
    ctx.fillText(`${Math.round(zoom * 100)}%`, width - 10, height - 10);
  }

  function getNodeRadius(node) {
    const baseRadius = 18;
    // Size by connection count
    const connections = edges.filter(e =>
      (e.source_id || e.source) === node.id ||
      (e.target_id || e.target) === node.id
    ).length;
    return baseRadius + Math.min(connections * 2, 14);
  }

  // Convert screen coordinates to canvas coordinates
  function screenToCanvas(screenX, screenY) {
    return {
      x: (screenX - panX) / zoom,
      y: (screenY - panY) / zoom
    };
  }

  // Mouse interaction handlers
  function handleMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    const screenX = e.clientX - rect.left;
    const screenY = e.clientY - rect.top;
    const { x, y } = screenToCanvas(screenX, screenY);

    const node = findNodeAt(x, y);
    if (node) {
      draggedNode = node;
      canvas.style.cursor = 'grabbing';
    } else {
      // Start panning
      isPanning = true;
      lastMouseX = screenX;
      lastMouseY = screenY;
      canvas.style.cursor = 'move';
    }
  }

  function handleMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    const screenX = e.clientX - rect.left;
    const screenY = e.clientY - rect.top;
    const { x, y } = screenToCanvas(screenX, screenY);

    if (draggedNode) {
      draggedNode.x = x;
      draggedNode.y = y;
      draggedNode.vx = 0;
      draggedNode.vy = 0;
    } else if (isPanning) {
      const dx = screenX - lastMouseX;
      const dy = screenY - lastMouseY;
      panX += dx;
      panY += dy;
      lastMouseX = screenX;
      lastMouseY = screenY;
    } else {
      // Update hover state
      hoveredNode = findNodeAt(x, y);
      hoveredEdge = hoveredNode ? null : findEdgeAt(x, y);
      canvas.style.cursor = hoveredNode || hoveredEdge ? 'pointer' : 'grab';
    }
  }

  function handleMouseUp() {
    draggedNode = null;
    isPanning = false;
    canvas.style.cursor = 'grab';
  }

  function handleMouseLeave() {
    hoveredNode = null;
    hoveredEdge = null;
    draggedNode = null;
    isPanning = false;
    canvas.style.cursor = 'grab';
  }

  function handleClick(e) {
    const rect = canvas.getBoundingClientRect();
    const screenX = e.clientX - rect.left;
    const screenY = e.clientY - rect.top;
    const { x, y } = screenToCanvas(screenX, screenY);

    const node = findNodeAt(x, y);
    if (node) {
      dispatch('node-click', node);
      return;
    }

    const edge = findEdgeAt(x, y);
    if (edge) {
      dispatch('edge-click', edge);
    }
  }

  function handleDoubleClick(e) {
    const rect = canvas.getBoundingClientRect();
    const screenX = e.clientX - rect.left;
    const screenY = e.clientY - rect.top;
    const { x, y } = screenToCanvas(screenX, screenY);

    const node = findNodeAt(x, y);
    if (node) {
      // Toggle pin state
      const newPinned = new Set(localPinnedNodes);
      if (newPinned.has(node.id)) {
        newPinned.delete(node.id);
      } else {
        newPinned.add(node.id);
      }
      pinnedNodes.set(newPinned);
      dispatch('node-double-click', node);
    }
  }

  function handleWheel(e) {
    e.preventDefault();

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Zoom toward mouse position
    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
    const newZoom = Math.max(0.3, Math.min(3, zoom * zoomFactor));

    // Adjust pan to zoom toward mouse
    panX = mouseX - (mouseX - panX) * (newZoom / zoom);
    panY = mouseY - (mouseY - panY) * (newZoom / zoom);

    zoom = newZoom;
  }

  function findNodeAt(x, y) {
    // Search in reverse order (top nodes first)
    for (let i = simulationNodes.length - 1; i >= 0; i--) {
      const node = simulationNodes[i];
      if (!enabledTypes.has(node.type?.toUpperCase())) continue;

      const dx = node.x - x;
      const dy = node.y - y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist <= node.radius + 5) {
        return node;
      }
    }
    return null;
  }

  function findEdgeAt(x, y) {
    const threshold = 8;

    for (const edge of simulationEdges) {
      if (!edge.source || !edge.target) continue;
      if (!enabledTypes.has(edge.source.type?.toUpperCase())) continue;
      if (!enabledTypes.has(edge.target.type?.toUpperCase())) continue;

      // Point-to-line distance
      const x1 = edge.source.x, y1 = edge.source.y;
      const x2 = edge.target.x, y2 = edge.target.y;

      const A = x - x1;
      const B = y - y1;
      const C = x2 - x1;
      const D = y2 - y1;

      const dot = A * C + B * D;
      const lenSq = C * C + D * D;
      let param = -1;
      if (lenSq !== 0) param = dot / lenSq;

      let xx, yy;
      if (param < 0) {
        xx = x1; yy = y1;
      } else if (param > 1) {
        xx = x2; yy = y2;
      } else {
        xx = x1 + param * C;
        yy = y1 + param * D;
      }

      const dx = x - xx;
      const dy = y - yy;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < threshold) {
        return edge;
      }
    }
    return null;
  }

  // Re-init simulation when data changes
  $: if (nodes && edges && canvas) {
    initSimulation();
  }
</script>

<canvas
  bind:this={canvas}
  on:mousedown={handleMouseDown}
  on:mousemove={handleMouseMove}
  on:mouseup={handleMouseUp}
  on:mouseleave={handleMouseLeave}
  on:click={handleClick}
  on:dblclick={handleDoubleClick}
  on:wheel={handleWheel}
  class="graph-canvas"
></canvas>

<style>
  .graph-canvas {
    width: 100%;
    height: 100%;
    display: block;
    cursor: grab;
    background: var(--bg-primary, #0f1419);
  }

  .graph-canvas:active {
    cursor: grabbing;
  }
</style>
