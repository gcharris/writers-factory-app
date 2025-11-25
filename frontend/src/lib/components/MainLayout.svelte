<script lang="ts">
  import { onMount } from 'svelte';
  import ChatSidebar from './ChatSidebar.svelte';
  import ForemanChatPanel from './ForemanChatPanel.svelte';
  import StudioPanel from './StudioPanel.svelte';
  import Editor from './Editor.svelte';
  import FileTree from './FileTree.svelte';

  // Panel visibility state
  let showFileTree = true;
  let showStudioPanel = true;
  let showForemanPanel = true;
  let showChatPanel = true;

  // Graph minimap state
  let showGraphMinimap = true;
  let graphExpanded = false;

  // Panel widths (percentages) - FileTree is fixed width
  let fileTreeWidth = 250; // pixels
  let studioPanelWidth = 25; // 25%
  let foremanPanelWidth = 50; // 50% - main writing area
  let chatPanelWidth = 25;   // 25%

  // Resize state
  let isResizing = false;
  let resizingPanel: 'studio' | 'graph' | 'foreman' | null = null;
  let resizeStartX = 0;
  let resizeStartWidth = 0;

  // Toolbar state
  let currentProject = 'Untitled Project';
  let foremanMode: 'ARCHITECT' | 'VOICE' | 'DIRECTOR' | 'IDLE' = 'IDLE';

  onMount(() => {
    // Load saved layout preferences
    loadLayoutPreferences();

    // Check Foreman mode
    checkForemanMode();

    // Setup window resize listener
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  });

  function loadLayoutPreferences() {
    const saved = localStorage.getItem('writers-factory-layout');
    if (saved) {
      try {
        const layout = JSON.parse(saved);
        showStudioPanel = layout.showStudioPanel ?? true;
        showGraphPanel = layout.showGraphPanel ?? true;
        showForemanPanel = layout.showForemanPanel ?? true;
        showChatPanel = layout.showChatPanel ?? true;
        studioPanelWidth = layout.studioPanelWidth ?? 25;
        graphPanelWidth = layout.graphPanelWidth ?? 25;
        foremanPanelWidth = layout.foremanPanelWidth ?? 25;
        chatPanelWidth = layout.chatPanelWidth ?? 25;
      } catch (error) {
        console.error('Failed to load layout preferences:', error);
      }
    }
  }

  function saveLayoutPreferences() {
    const layout = {
      showStudioPanel,
      showGraphPanel,
      showForemanPanel,
      showChatPanel,
      studioPanelWidth,
      graphPanelWidth,
      foremanPanelWidth,
      chatPanelWidth,
    };
    localStorage.setItem('writers-factory-layout', JSON.stringify(layout));
  }

  async function checkForemanMode() {
    try {
      const response = await fetch('http://localhost:8000/foreman/status');
      if (response.ok) {
        const data = await response.json();
        foremanMode = data.mode || 'IDLE';
      }
    } catch (error) {
      console.error('Failed to check Foreman mode:', error);
    }
  }

  function togglePanel(panel: 'studio' | 'graph' | 'foreman' | 'chat') {
    switch (panel) {
      case 'studio':
        showStudioPanel = !showStudioPanel;
        break;
      case 'graph':
        showGraphPanel = !showGraphPanel;
        break;
      case 'foreman':
        showForemanPanel = !showForemanPanel;
        break;
      case 'chat':
        showChatPanel = !showChatPanel;
        break;
    }
    saveLayoutPreferences();
  }

  function startResize(panel: 'studio' | 'graph' | 'foreman', event: MouseEvent) {
    isResizing = true;
    resizingPanel = panel;
    resizeStartX = event.clientX;

    switch (panel) {
      case 'studio':
        resizeStartWidth = studioPanelWidth;
        break;
      case 'graph':
        resizeStartWidth = graphPanelWidth;
        break;
      case 'foreman':
        resizeStartWidth = foremanPanelWidth;
        break;
    }

    event.preventDefault();
  }

  function handleMouseMove(event: MouseEvent) {
    if (!isResizing || !resizingPanel) return;

    const containerWidth = window.innerWidth;
    const deltaX = event.clientX - resizeStartX;
    const deltaPercent = (deltaX / containerWidth) * 100;

    let newWidth = resizeStartWidth + deltaPercent;

    // Constrain width (minimum 15%, maximum 50%)
    newWidth = Math.max(15, Math.min(50, newWidth));

    switch (resizingPanel) {
      case 'studio':
        studioPanelWidth = newWidth;
        break;
      case 'graph':
        graphPanelWidth = newWidth;
        break;
      case 'foreman':
        foremanPanelWidth = newWidth;
        break;
    }

    // Normalize widths to total 100%
    normalizeWidths();
  }

  function handleMouseUp() {
    if (isResizing) {
      isResizing = false;
      resizingPanel = null;
      saveLayoutPreferences();
    }
  }

  function normalizeWidths() {
    const visiblePanels = [
      showStudioPanel ? studioPanelWidth : 0,
      showGraphPanel ? graphPanelWidth : 0,
      showForemanPanel ? foremanPanelWidth : 0,
      showChatPanel ? chatPanelWidth : 0,
    ];

    const totalWidth = visiblePanels.reduce((sum, w) => sum + w, 0);

    if (totalWidth > 0) {
      const scale = 100 / totalWidth;
      studioPanelWidth *= scale;
      graphPanelWidth *= scale;
      foremanPanelWidth *= scale;
      chatPanelWidth *= scale;
    }
  }

  function resetLayout() {
    showStudioPanel = true;
    showGraphPanel = true;
    showForemanPanel = true;
    showChatPanel = true;
    studioPanelWidth = 25;
    graphPanelWidth = 25;
    foremanPanelWidth = 25;
    chatPanelWidth = 25;
    saveLayoutPreferences();
  }

  function getModeColor(mode: string): string {
    switch (mode) {
      case 'ARCHITECT': return '#ffb000'; // Amber
      case 'VOICE': return '#00ff88'; // Neon green
      case 'DIRECTOR': return '#00d9ff'; // Electric blue
      default: return '#888888'; // Gray
    }
  }

  function getModeIcon(mode: string): string {
    switch (mode) {
      case 'ARCHITECT': return '📐';
      case 'VOICE': return '🎤';
      case 'DIRECTOR': return '🎬';
      default: return '💤';
    }
  }

  // Calculate visible panels count
  $: visiblePanelsCount = [showStudioPanel, showGraphPanel, showForemanPanel, showChatPanel].filter(Boolean).length;
  $: normalizeWidths();
</script>

<div class="main-layout">
  <!-- Toolbar -->
  <div class="toolbar">
    <div class="toolbar-left">
      <div class="logo">
        <span class="logo-icon">✍️</span>
        <span class="logo-text">Writers Factory</span>
      </div>

      <div class="mode-indicator" style="border-color: {getModeColor(foremanMode)};">
        <span class="mode-icon">{getModeIcon(foremanMode)}</span>
        <span class="mode-text">{foremanMode} Mode</span>
      </div>

      <div class="project-name">
        <span class="project-icon">📁</span>
        <span>{currentProject}</span>
      </div>
    </div>

    <div class="toolbar-center">
      <!-- Panel toggles -->
      <button
        class="panel-toggle {showStudioPanel ? 'active' : ''}"
        on:click={() => togglePanel('studio')}
        title="Toggle Studio Panel"
      >
        Studio
      </button>
      <button
        class="panel-toggle {showForemanPanel ? 'active' : ''}"
        on:click={() => togglePanel('foreman')}
        title="Toggle Writing Panel"
      >
        Writing
      </button>
      <button
        class="panel-toggle {showChatPanel ? 'active' : ''}"
        on:click={() => togglePanel('chat')}
        title="Toggle Foreman Panel"
      >
        Foreman
      </button>
    </div>

    <div class="toolbar-right">
      <button class="toolbar-button" on:click={resetLayout} title="Reset Layout">
        <span class="icon">⟲</span>
      </button>
      <button class="toolbar-button" title="Settings">
        <span class="icon">⚙️</span>
      </button>
      <button class="toolbar-button" title="Help">
        <span class="icon">?</span>
      </button>
    </div>
  </div>

  <!-- Main Content: FileTree + Panels -->
  <div class="content-area">
    <!-- File Tree Sidebar (Scrivener-style) -->
    {#if showFileTree}
      <aside class="file-tree-sidebar" style="width: {fileTreeWidth}px;">
        <FileTree />
      </aside>
    {/if}

    <!-- Main Panel Area -->
    <div class="panels-container">
      {#if visiblePanelsCount === 0}
        <div class="empty-state">
          <p>All panels are hidden. Click the panel toggles in the toolbar to show them.</p>
          <button class="btn-reset" on:click={resetLayout}>Reset Layout</button>
        </div>
      {:else}
      <!-- Studio Panel -->
      {#if showStudioPanel}
        <div class="panel studio-panel" style="width: {studioPanelWidth}%;">
          <div class="panel-header">
            <h3>Studio</h3>
            <button class="panel-close" on:click={() => togglePanel('studio')}>×</button>
          </div>
          <div class="panel-content">
            <StudioPanel />
          </div>
        </div>
        <div
          class="resize-handle"
          on:mousedown={(e) => startResize('studio', e)}
        ></div>
      {/if}

      <!-- Writing/Editor Panel -->
      {#if showForemanPanel}
        <div class="panel foreman-panel" style="width: {foremanPanelWidth}%;">
          <div class="panel-header">
            <h3>Writing</h3>
            <button class="panel-close" on:click={() => togglePanel('foreman')}>×</button>
          </div>
          <div class="panel-content">
            <Editor />
          </div>
        </div>
        <div
          class="resize-handle"
          on:mousedown={(e) => startResize('foreman', e)}
        ></div>
      {/if}

      <!-- Chat Panel -->
      {#if showChatPanel}
        <div class="panel chat-panel" style="width: {chatPanelWidth}%;">
          <div class="panel-content">
            <ForemanChatPanel />
          </div>
        </div>
      {/if}
    {/if}
    </div>

    <!-- Graph Minimap (Floating Widget) -->
    {#if showGraphMinimap}
      <div class="graph-minimap {graphExpanded ? 'expanded' : ''}">
        <div class="minimap-header">
          <span class="minimap-title">🕸️ Graph</span>
          <button
            class="minimap-expand"
            on:click={() => graphExpanded = !graphExpanded}
            title={graphExpanded ? 'Collapse' : 'Expand'}
          >
            {graphExpanded ? '◀' : '▶'}
          </button>
          <button
            class="minimap-close"
            on:click={() => showGraphMinimap = false}
            title="Close"
          >
            ×
          </button>
        </div>
        <div class="minimap-content">
          {#if graphExpanded}
            <p class="minimap-placeholder">Knowledge graph visualization will appear here</p>
          {:else}
            <div class="minimap-thumbnail">
              <span class="thumbnail-icon">🕸️</span>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .main-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
    background: #1a1a1a;
    color: #ffffff;
    overflow: hidden;
  }

  /* Toolbar */
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 48px;
    background: #2d2d2d;
    border-bottom: 2px solid #00d9ff;
    padding: 0 1rem;
    flex-shrink: 0;
  }

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    font-size: 1.1rem;
  }

  .logo-icon {
    font-size: 1.5rem;
  }

  .logo-text {
    color: #00d9ff;
  }

  .mode-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.75rem;
    background: #1a1a1a;
    border: 2px solid;
    border-radius: 4px;
    font-weight: 500;
    font-size: 0.875rem;
  }

  .mode-icon {
    font-size: 1rem;
  }

  .project-name {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #b0b0b0;
    font-size: 0.875rem;
  }

  .project-icon {
    font-size: 1rem;
  }

  .toolbar-center {
    display: flex;
    gap: 0.5rem;
  }

  .panel-toggle {
    padding: 0.5rem 1rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #b0b0b0;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .panel-toggle:hover {
    background: #252525;
    border-color: #00d9ff;
    color: #00d9ff;
  }

  .panel-toggle.active {
    background: #00d9ff20;
    border-color: #00d9ff;
    color: #00d9ff;
  }

  .toolbar-right {
    display: flex;
    gap: 0.5rem;
  }

  .toolbar-button {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #b0b0b0;
    cursor: pointer;
    transition: all 0.2s;
  }

  .toolbar-button:hover {
    background: #252525;
    border-color: #00d9ff;
    color: #00d9ff;
  }

  .icon {
    font-size: 1rem;
  }

  /* Content Area */
  .content-area {
    display: flex;
    flex: 1;
    overflow: hidden;
    position: relative;
  }

  /* File Tree Sidebar (Scrivener-style) */
  .file-tree-sidebar {
    flex-shrink: 0;
    background: #252525;
    border-right: 1px solid #404040;
    overflow-y: auto;
    overflow-x: hidden;
  }

  /* Main Panels Container */
  .panels-container {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    color: #888888;
  }

  .btn-reset {
    margin-top: 1rem;
    padding: 0.75rem 1.5rem;
    background: #00d9ff;
    color: #1a1a1a;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-reset:hover {
    background: #00b8d9;
  }

  /* Panels */
  .panel {
    display: flex;
    flex-direction: column;
    background: #252525;
    border-right: 1px solid #404040;
    overflow: hidden;
  }

  .panel:last-of-type {
    border-right: none;
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 40px;
    padding: 0 1rem;
    background: #2d2d2d;
    border-bottom: 1px solid #404040;
    flex-shrink: 0;
  }

  .panel-header h3 {
    margin: 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: #00d9ff;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .panel-close {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    color: #888888;
    font-size: 1.5rem;
    cursor: pointer;
    transition: color 0.2s;
  }

  .panel-close:hover {
    color: #ff4444;
  }

  .panel-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
  }

  /* Placeholder content */
  .placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #888888;
    text-align: center;
    padding: 2rem;
  }

  .placeholder p {
    margin: 0.5rem 0;
  }

  .placeholder-hint {
    font-size: 0.875rem;
    color: #666666;
  }

  /* Resize handle */
  .resize-handle {
    width: 4px;
    background: #404040;
    cursor: col-resize;
    transition: background 0.2s;
    flex-shrink: 0;
  }

  .resize-handle:hover {
    background: #00d9ff;
  }

  /* Scrollbar styling */
  .panel-content::-webkit-scrollbar {
    width: 8px;
  }

  .panel-content::-webkit-scrollbar-track {
    background: #1a1a1a;
  }

  .panel-content::-webkit-scrollbar-thumb {
    background: #404040;
    border-radius: 4px;
  }

  .panel-content::-webkit-scrollbar-thumb:hover {
    background: #505050;
  }

  /* User select prevention during resize */
  :global(body.resizing) {
    user-select: none;
    cursor: col-resize !important;
  }

  /* Graph Minimap (Floating Widget) */
  .graph-minimap {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: #2d2d2d;
    border: 2px solid #00d9ff;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    z-index: 1000;
    transition: all 0.3s ease;
  }

  .graph-minimap:not(.expanded) {
    width: 120px;
    height: 120px;
  }

  .graph-minimap.expanded {
    width: 400px;
    height: 400px;
  }

  .minimap-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem;
    background: #252525;
    border-bottom: 1px solid #404040;
    border-radius: 6px 6px 0 0;
  }

  .minimap-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #00d9ff;
  }

  .minimap-expand,
  .minimap-close {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    color: #888888;
    font-size: 1rem;
    cursor: pointer;
    transition: color 0.2s;
  }

  .minimap-expand:hover {
    color: #00d9ff;
  }

  .minimap-close:hover {
    color: #ff4444;
  }

  .minimap-content {
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    height: calc(100% - 40px);
  }

  .minimap-thumbnail {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }

  .thumbnail-icon {
    font-size: 3rem;
    opacity: 0.5;
  }

  .minimap-placeholder {
    color: #888888;
    text-align: center;
    font-size: 0.875rem;
  }
</style>
