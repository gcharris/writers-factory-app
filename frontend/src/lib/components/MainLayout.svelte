<!--
  MainLayout.svelte - 4-Panel IDE Layout

  Layout:
  ┌──────────────────────────────────────────────────────────────────┐
  │  TOOLBAR                                                         │
  ├───────────┬───────────────────┬─────────────┬───────────────────┤
  │           │                   │             │                   │
  │  STUDIO   │      CANVAS       │   GRAPH     │    FOREMAN        │
  │  PANEL    │      (flex-1)     │   PANEL     │    PANEL          │
  │  (280px)  │                   │   (300px)   │    (360px)        │
  │           │                   │             │                   │
  └───────────┴───────────────────┴─────────────┴───────────────────┘
  │  STATUS BAR                                                      │
  └──────────────────────────────────────────────────────────────────┘

  Each panel can be collapsed/expanded and resized.
-->
<script>
  import { onMount } from 'svelte';
  import { foremanMode, foremanActive } from '$lib/stores';
  import Modal from './Modal.svelte';
  import Toast from './Toast.svelte';
  import StatusBar from './StatusBar.svelte';
  import SettingsPanel from './SettingsPanel.svelte';

  // Panel collapse state
  let studioPanelCollapsed = false;
  let graphPanelCollapsed = false;
  let foremanPanelCollapsed = false;

  // Panel widths (pixels)
  let studioPanelWidth = 280;
  let graphPanelWidth = 300;
  let foremanPanelWidth = 360;

  // Settings modal
  let showSettings = false;

  // Mode colors
  const modeColors = {
    ARCHITECT: 'var(--mode-architect, #2f81f7)',
    VOICE_CALIBRATION: 'var(--mode-voice, #a371f7)',
    DIRECTOR: 'var(--mode-director, #d4a574)',
    EDITOR: 'var(--mode-editor, #3fb950)'
  };

  // Mode icons
  const modeIcons = {
    ARCHITECT: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
    </svg>`,
    VOICE_CALIBRATION: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
      <line x1="8" y1="23" x2="16" y2="23"></line>
    </svg>`,
    DIRECTOR: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polygon points="23 7 16 12 23 17 23 7"></polygon>
      <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
    </svg>`,
    EDITOR: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
    </svg>`
  };

  function toggleStudioPanel() {
    studioPanelCollapsed = !studioPanelCollapsed;
  }

  function toggleGraphPanel() {
    graphPanelCollapsed = !graphPanelCollapsed;
  }

  function toggleForemanPanel() {
    foremanPanelCollapsed = !foremanPanelCollapsed;
  }

  function openSettings() {
    showSettings = true;
  }
</script>

<div class="layout-container">
  <!-- Toolbar -->
  <header class="toolbar">
    <div class="toolbar-left">
      <div class="app-title">
        <span class="app-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
          </svg>
        </span>
        <span>Writers Factory</span>
      </div>

      <!-- Mode Tabs -->
      {#if $foremanActive}
        <nav class="mode-tabs">
          {#each ['ARCHITECT', 'VOICE_CALIBRATION', 'DIRECTOR', 'EDITOR'] as mode}
            <button
              class="mode-tab {$foremanMode === mode ? 'active' : ''}"
              style="--mode-color: {modeColors[mode]}"
              disabled={mode !== $foremanMode}
            >
              <span class="mode-icon">{@html modeIcons[mode]}</span>
              <span class="mode-name">{mode.replace('_', ' ')}</span>
            </button>
          {/each}
        </nav>
      {/if}
    </div>

    <div class="toolbar-right">
      <button class="toolbar-btn" on:click={openSettings} title="Settings">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
      </button>
    </div>
  </header>

  <!-- Main Panel Area -->
  <div class="panel-container">
    <!-- Studio Panel (Left) -->
    <aside
      class="panel panel-studio {studioPanelCollapsed ? 'collapsed' : ''}"
      style="--panel-width: {studioPanelWidth}px"
    >
      <div class="panel-header">
        <span class="panel-title">Studio</span>
        <button class="panel-toggle" on:click={toggleStudioPanel} title={studioPanelCollapsed ? 'Expand' : 'Collapse'}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            {#if studioPanelCollapsed}
              <polyline points="9 18 15 12 9 6"></polyline>
            {:else}
              <polyline points="15 18 9 12 15 6"></polyline>
            {/if}
          </svg>
        </button>
      </div>
      {#if !studioPanelCollapsed}
        <div class="panel-content">
          <slot name="studio" />
        </div>
      {/if}
    </aside>

    <!-- Canvas Panel (Center) -->
    <main class="panel panel-canvas">
      <slot name="canvas" />
    </main>

    <!-- Graph Panel -->
    <aside
      class="panel panel-graph {graphPanelCollapsed ? 'collapsed' : ''}"
      style="--panel-width: {graphPanelWidth}px"
    >
      <div class="panel-header">
        <span class="panel-title">Knowledge Graph</span>
        <button class="panel-toggle" on:click={toggleGraphPanel} title={graphPanelCollapsed ? 'Expand' : 'Collapse'}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            {#if graphPanelCollapsed}
              <polyline points="15 18 9 12 15 6"></polyline>
            {:else}
              <polyline points="9 18 15 12 9 6"></polyline>
            {/if}
          </svg>
        </button>
      </div>
      {#if !graphPanelCollapsed}
        <div class="panel-content">
          <slot name="graph" />
        </div>
      {/if}
    </aside>

    <!-- Foreman Panel (Right) -->
    <aside
      class="panel panel-foreman {foremanPanelCollapsed ? 'collapsed' : ''}"
      style="--panel-width: {foremanPanelWidth}px"
    >
      <div class="panel-header" style="--mode-color: {modeColors[$foremanMode] || modeColors.ARCHITECT}">
        <span class="panel-title">Foreman</span>
        {#if $foremanMode}
          <span class="mode-badge">{$foremanMode.replace('_', ' ')}</span>
        {/if}
        <button class="panel-toggle" on:click={toggleForemanPanel} title={foremanPanelCollapsed ? 'Expand' : 'Collapse'}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            {#if foremanPanelCollapsed}
              <polyline points="15 18 9 12 15 6"></polyline>
            {:else}
              <polyline points="9 18 15 12 9 6"></polyline>
            {/if}
          </svg>
        </button>
      </div>
      {#if !foremanPanelCollapsed}
        <div class="panel-content">
          <slot name="foreman" />
        </div>
      {/if}
    </aside>
  </div>

  <!-- Status Bar -->
  <StatusBar />

  <!-- Toast Notifications -->
  <Toast />

  <!-- Settings Modal -->
  <Modal bind:open={showSettings} title="Settings" size="large">
    <SettingsPanel />
  </Modal>
</div>

<style>
  .layout-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
    background: var(--bg-primary, #0f1419);
    overflow: hidden;
  }

  /* Toolbar */
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: var(--header-height, 40px);
    padding: 0 var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: var(--space-6, 24px);
  }

  .app-title {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .app-icon {
    display: flex;
    color: var(--accent-gold, #d4a574);
  }

  .mode-tabs {
    display: flex;
    gap: var(--space-1, 4px);
  }

  .mode-tab {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: var(--space-1, 4px) var(--space-3, 12px);
    background: transparent;
    border: none;
    border-radius: var(--radius-md, 6px);
    color: var(--text-muted, #6e7681);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .mode-tab:disabled {
    cursor: default;
  }

  .mode-tab:hover:not(.active):not(:disabled) {
    background: var(--bg-tertiary, #242d38);
  }

  .mode-tab.active {
    background: color-mix(in srgb, var(--mode-color) 20%, transparent);
    color: var(--mode-color);
  }

  .mode-icon {
    display: flex;
    width: 16px;
    height: 16px;
  }

  .mode-name {
    text-transform: capitalize;
  }

  .toolbar-right {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .toolbar-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: transparent;
    border: none;
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .toolbar-btn:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  /* Panel Container */
  .panel-container {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  /* Panels */
  .panel {
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary, #1a2027);
    border-right: 1px solid var(--border, #2d3a47);
    transition: width var(--transition-normal, 200ms ease);
  }

  .panel:last-child {
    border-right: none;
  }

  .panel-studio {
    width: var(--panel-width, 280px);
  }

  .panel-canvas {
    flex: 1;
    min-width: var(--panel-canvas-min, 500px);
    background: var(--bg-primary, #0f1419);
  }

  .panel-graph {
    width: var(--panel-width, 300px);
  }

  .panel-foreman {
    width: var(--panel-width, 360px);
    border-left: 1px solid var(--border, #2d3a47);
    border-right: none;
  }

  .panel.collapsed {
    width: 40px;
  }

  .panel-header {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    height: 36px;
    padding: 0 var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .panel.collapsed .panel-header {
    padding: 0;
    justify-content: center;
  }

  .panel-title {
    flex: 1;
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .panel.collapsed .panel-title {
    display: none;
  }

  .mode-badge {
    padding: 2px 6px;
    background: color-mix(in srgb, var(--mode-color, var(--accent-cyan)) 20%, transparent);
    border-radius: var(--radius-sm, 4px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    color: var(--mode-color, var(--accent-cyan));
    text-transform: uppercase;
  }

  .panel.collapsed .mode-badge {
    display: none;
  }

  .panel-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .panel-toggle:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-secondary, #8b949e);
  }

  .panel-content {
    flex: 1;
    overflow-y: auto;
  }

  .panel.collapsed .panel-content {
    display: none;
  }
</style>
