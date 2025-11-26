<!--
  GraphControls.svelte - Search Bar, Filters, and Action Buttons

  Features:
  - Search input to find nodes by name
  - Node type filter chips (CHARACTER, LOCATION, etc.)
  - Stats display (node count, edge count)
  - Action buttons (Add Link, Refresh)
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { graphFilters, searchQuery } from '$lib/stores';

  export let nodes = [];
  export let edges = [];

  const dispatch = createEventDispatcher();

  // All available node types
  const nodeTypes = ['CHARACTER', 'LOCATION', 'THEME', 'EVENT', 'OBJECT', 'CONCEPT'];

  // Filter state (local, synced to store)
  let enabledTypes = new Set(nodeTypes);
  let search = '';

  // Stats
  $: nodeCount = nodes.length;
  $: edgeCount = edges.length;
  $: visibleNodeCount = nodes.filter(n => enabledTypes.has(n.type?.toUpperCase())).length;

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

  // Node type colors (matching Cyber-Noir theme)
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
    gap: var(--space-4, 16px);
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
    flex-wrap: wrap;
  }

  /* Search Section */
  .search-section {
    flex-shrink: 0;
  }

  .search-input-wrapper {
    position: relative;
    width: 220px;
  }

  .search-icon {
    position: absolute;
    left: var(--space-2, 8px);
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted, #6e7681);
    pointer-events: none;
  }

  .search-input {
    width: 100%;
    padding: 6px var(--space-2, 8px) 6px 34px;
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-primary, #e6edf3);
    font-size: var(--text-sm, 12px);
    transition: all 0.1s ease;
  }

  .search-input::placeholder {
    color: var(--text-muted, #6e7681);
  }

  .search-input:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
    background: var(--bg-primary, #0f1419);
  }

  .clear-search-btn {
    position: absolute;
    right: var(--space-2, 8px);
    top: 50%;
    transform: translateY(-50%);
    padding: 2px;
    background: none;
    border: none;
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: color 0.1s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .clear-search-btn:hover {
    color: var(--text-primary, #e6edf3);
  }

  /* Filters Section */
  .filters-section {
    flex: 1;
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    min-width: 0;
  }

  .filter-header {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    flex-shrink: 0;
  }

  .filter-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    font-weight: var(--font-semibold, 600);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .toggle-all-btn {
    padding: 2px var(--space-2, 8px);
    background: none;
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .toggle-all-btn:hover {
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--accent-cyan, #58a6ff);
  }

  .filter-chips {
    display: flex;
    gap: var(--space-2, 8px);
    flex-wrap: wrap;
  }

  .filter-chip {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-muted, #6e7681);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .filter-chip:hover {
    background: var(--bg-elevated, #2d3a47);
    border-color: var(--border-strong, #3d4a57);
  }

  .filter-chip.active {
    background: color-mix(in srgb, var(--chip-color) 15%, transparent);
    border-color: var(--chip-color);
    color: var(--text-primary, #e6edf3);
  }

  .chip-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    opacity: 0.5;
    flex-shrink: 0;
  }

  .filter-chip.active .chip-dot {
    opacity: 1;
  }

  /* Actions Section */
  .actions-section {
    display: flex;
    align-items: center;
    gap: var(--space-4, 16px);
    flex-shrink: 0;
  }

  .stats {
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

  .action-buttons {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px var(--space-3, 12px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .action-btn:hover {
    background: var(--accent-cyan, #58a6ff);
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
    transform: translateY(-1px);
  }

  /* Responsive adjustments */
  @media (max-width: 1000px) {
    .graph-controls {
      flex-direction: column;
      align-items: stretch;
      gap: var(--space-3, 12px);
    }

    .search-input-wrapper {
      width: 100%;
    }

    .filters-section {
      flex-direction: column;
      align-items: flex-start;
    }

    .actions-section {
      justify-content: space-between;
    }
  }
</style>
