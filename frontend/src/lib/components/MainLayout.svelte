<!--
  MainLayout.svelte - 3-Panel IDE Layout (Cyber-Noir Theme)

  Layout matching the mockup:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ TOOLBAR                                                                  │
  ├────────────┬─────────────────────────────────┬──────────────────────────┤
  │            │                                 │                          │
  │  BINDER    │           CANVAS                │      THE FOREMAN         │
  │  (240px)   │      (flex, min 500px)          │        (400px)           │
  │            │                                 │                          │
  │  File      │   Monaco Editor                 │  [Studio ▼] [⚙️]         │
  │  Tree      │   + Breadcrumbs                 │  Chat Interface (70%)    │
  │            │                                 │  Live Graph (30%)        │
  │            │                                 │                          │
  ├────────────┴─────────────────────────────────┴──────────────────────────┤
  │ STATUS BAR                                                               │
  └─────────────────────────────────────────────────────────────────────────┘

  Binder and Foreman panels can be collapsed/expanded.
-->
<script>
  import { onMount } from 'svelte';
  import {
    foremanMode,
    foremanActive,
    showStoryBibleWizard,
    showNotebookRegistration,
    activeModal
  } from '$lib/stores';
  import Modal from './Modal.svelte';
  import Toast from './Toast.svelte';
  import StatusBar from './StatusBar.svelte';
  import SettingsPanel from './SettingsPanel.svelte';
  import StoryBibleWizard from './StoryBibleWizard.svelte';
  import NotebookRegistration from './NotebookRegistration.svelte';

  // Panel resize state (widths in pixels)
  let binderWidth = 240;
  let foremanWidth = 380;
  const MIN_BINDER_WIDTH = 180;
  const MAX_BINDER_WIDTH = 400;
  const MIN_FOREMAN_WIDTH = 300;
  const MAX_FOREMAN_WIDTH = 600;

  // Resize drag state
  let isResizingBinder = false;
  let isResizingForeman = false;
  let resizeStartX = 0;
  let resizeStartWidth = 0;

  // Settings modal
  let showSettings = false;

  // Resize handlers
  /** @param {MouseEvent} e */
  function startBinderResize(e) {
    isResizingBinder = true;
    resizeStartX = e.clientX;
    resizeStartWidth = binderWidth;
    document.addEventListener('mousemove', handleResize);
    document.addEventListener('mouseup', stopResize);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }

  /** @param {MouseEvent} e */
  function startForemanResize(e) {
    isResizingForeman = true;
    resizeStartX = e.clientX;
    resizeStartWidth = foremanWidth;
    document.addEventListener('mousemove', handleResize);
    document.addEventListener('mouseup', stopResize);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }

  /** @param {MouseEvent} e */
  function handleResize(e) {
    if (isResizingBinder) {
      const delta = e.clientX - resizeStartX;
      const newWidth = Math.min(MAX_BINDER_WIDTH, Math.max(MIN_BINDER_WIDTH, resizeStartWidth + delta));
      binderWidth = newWidth;
    } else if (isResizingForeman) {
      const delta = resizeStartX - e.clientX; // Inverted for right panel
      const newWidth = Math.min(MAX_FOREMAN_WIDTH, Math.max(MIN_FOREMAN_WIDTH, resizeStartWidth + delta));
      foremanWidth = newWidth;
    }
  }

  function stopResize() {
    isResizingBinder = false;
    isResizingForeman = false;
    document.removeEventListener('mousemove', handleResize);
    document.removeEventListener('mouseup', stopResize);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }

  // Mode colors
  const modeColors = {
    ARCHITECT: 'var(--mode-architect)',
    VOICE_CALIBRATION: 'var(--mode-voice)',
    DIRECTOR: 'var(--mode-director)',
    EDITOR: 'var(--mode-editor)'
  };

  // Mode icons
  const modeIcons = {
    ARCHITECT: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
    </svg>`,
    VOICE_CALIBRATION: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
    </svg>`,
    DIRECTOR: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polygon points="23 7 16 12 23 17 23 7"></polygon>
      <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
    </svg>`,
    EDITOR: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
    </svg>`
  };

  function openSettings() {
    showSettings = true;
  }

  // Close Story Bible wizard
  function closeStoryBibleWizard() {
    $showStoryBibleWizard = false;
    $activeModal = null;
  }

  // Close Notebook Registration
  function closeNotebookRegistration() {
    $showNotebookRegistration = false;
    $activeModal = null;
  }

  // Handle Story Bible completion
  function handleStoryBibleComplete(event) {
    closeStoryBibleWizard();
  }
</script>

<div class="layout-container">
  <!-- Toolbar -->
  <header class="toolbar">
    <div class="toolbar-left">
      <div class="app-title">
        <span class="app-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
          </svg>
        </span>
        <span>Writers Factory</span>
      </div>

      <!-- Mode Tabs (workflow stages - VOICE is a tool, not a stage) -->
      {#if $foremanActive}
        <nav class="mode-tabs">
          {#each ['ARCHITECT', 'DIRECTOR', 'EDITOR'] as mode}
            <button
              class="mode-tab {$foremanMode === mode ? 'active' : ''}"
              style="--mode-color: {modeColors[mode]}"
              disabled={mode !== $foremanMode}
            >
              <span class="mode-icon">{@html modeIcons[mode]}</span>
              <span class="mode-name">{mode}</span>
            </button>
          {/each}
        </nav>
      {/if}
    </div>

    <!-- Tools & Settings (RIGHT) -->
    <div class="toolbar-right">
      <!-- Studio Tools Button -->
      <button class="toolbar-tool-btn" on:click={() => activeModal.set('studio-tools')} title="Studio Tools">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
          <polyline points="2 17 12 22 22 17"></polyline>
          <polyline points="2 12 12 17 22 12"></polyline>
        </svg>
        <span>STUDIO</span>
      </button>

      <!-- Knowledge Graph Button -->
      <button class="toolbar-tool-btn" on:click={() => activeModal.set('graph-viewer')} title="Knowledge Graph">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <circle cx="19" cy="5" r="2"></circle>
          <circle cx="5" cy="5" r="2"></circle>
          <circle cx="19" cy="19" r="2"></circle>
          <circle cx="5" cy="19" r="2"></circle>
          <line x1="12" y1="9" x2="12" y2="5"></line>
          <line x1="14.5" y1="13.5" x2="17" y2="17"></line>
          <line x1="9.5" y1="13.5" x2="7" y2="17"></line>
        </svg>
        <span>GRAPH</span>
      </button>

      <!-- Settings Button -->
      <button class="window-btn settings" on:click={openSettings} title="Settings">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
        </button>
    </div>
  </header>

  <!-- Main Panel Area -->
  <div class="panel-container" class:resizing={isResizingBinder || isResizingForeman}>
    <!-- BINDER Panel (Left) -->
    <aside class="panel panel-binder" style="width: {binderWidth}px;">
      <div class="panel-content">
        <slot name="binder" />
      </div>
    </aside>

    <!-- Resize Handle (Binder/Canvas) -->
    <button
      class="resize-handle"
      on:mousedown={startBinderResize}
      aria-label="Resize binder panel"
    ></button>

    <!-- CANVAS Panel (Center) -->
    <main class="panel panel-canvas">
      <slot name="canvas" />
    </main>

    <!-- Resize Handle (Canvas/Foreman) -->
    <button
      class="resize-handle"
      on:mousedown={startForemanResize}
      aria-label="Resize assistant panel"
    ></button>

    <!-- Chat Panel (Right) -->
    <aside class="panel panel-foreman" style="width: {foremanWidth}px;">
      <div class="panel-content">
        <slot name="foreman" />
      </div>
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

  <!-- Story Bible Wizard Modal -->
  <Modal
    bind:open={$showStoryBibleWizard}
    title="Story Bible Wizard"
    size="large"
    on:close={closeStoryBibleWizard}
  >
    <StoryBibleWizard
      on:complete={handleStoryBibleComplete}
      on:close={closeStoryBibleWizard}
    />
  </Modal>

  <!-- NotebookLM Registration Modal -->
  <Modal
    bind:open={$showNotebookRegistration}
    title="NotebookLM Integration"
    size="medium"
    on:close={closeNotebookRegistration}
  >
    <NotebookRegistration on:close={closeNotebookRegistration} />
  </Modal>
</div>

<style>
  .layout-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
    background: var(--bg-primary);
    overflow: hidden;
  }

  /* ============================================
   * TOOLBAR
   * ============================================ */
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: var(--header-height);
    padding: 0 var(--space-3);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    -webkit-app-region: drag; /* Allow window dragging on toolbar */
  }

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: var(--space-6);
    -webkit-app-region: no-drag;
  }

  .app-title {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-weight: var(--font-semibold);
    font-size: var(--text-sm);
    color: var(--text-primary);
  }

  .app-icon {
    display: flex;
    color: var(--accent-gold);
  }

  .mode-tabs {
    display: flex;
    gap: 2px;
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
    padding: 2px;
  }

  .mode-tab {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-3);
    background: transparent;
    border: none;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .mode-tab:disabled {
    cursor: default;
  }

  .mode-tab:hover:not(.active):not(:disabled) {
    color: var(--text-secondary);
  }

  .mode-tab.active {
    background: var(--bg-secondary);
    color: var(--mode-color);
    box-shadow: var(--shadow-sm);
  }

  .mode-icon {
    display: flex;
    width: 14px;
    height: 14px;
  }

  .mode-name {
    font-size: 10px;
    letter-spacing: 0.5px;
  }

  .toolbar-right {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    -webkit-app-region: no-drag;
  }

  /* Toolbar tool buttons (STUDIO, GRAPH) - styled like mode tabs */
  .toolbar-tool-btn {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-3);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: 10px;
    font-weight: var(--font-medium);
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .toolbar-tool-btn:hover {
    background: var(--bg-elevated);
    border-color: var(--border-strong);
    color: var(--text-primary);
  }

  .toolbar-tool-btn:active {
    background: var(--accent-cyan);
    color: white;
    border-color: var(--accent-cyan);
  }

  .window-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .window-btn:hover {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
  }

  .window-btn.settings:hover {
    color: var(--accent-gold);
  }

  /* ============================================
   * PANEL CONTAINER
   * ============================================ */
  .panel-container {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  /* Disable transitions during resize for smooth dragging */
  .panel-container.resizing .panel {
    transition: none;
  }

  /* ============================================
   * RESIZE HANDLES
   * ============================================ */
  .resize-handle {
    width: 4px;
    padding: 0;
    border: none;
    background: transparent;
    cursor: col-resize;
    flex-shrink: 0;
    transition: background var(--transition-fast);
    position: relative;
  }

  .resize-handle::after {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 1px;
    width: 2px;
    background: var(--border);
  }

  .resize-handle:hover {
    background: var(--accent-cyan);
  }

  .resize-handle:hover::after {
    background: var(--accent-cyan);
  }

  /* ============================================
   * PANELS (Base Styles)
   * ============================================ */
  .panel {
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary);
    transition: width 0.15s ease;
  }

  .panel-content {
    flex: 1;
    overflow: hidden;
  }

  /* ============================================
   * BINDER PANEL (Left)
   * ============================================ */
  .panel-binder {
    flex-shrink: 0;
  }

  /* ============================================
   * CANVAS PANEL (Center)
   * ============================================ */
  .panel-canvas {
    flex: 1;
    min-width: 400px;
    background: var(--bg-primary);
  }

  /* ============================================
   * FOREMAN PANEL (Right - Primary AI Interface)
   * ============================================ */
  .panel-foreman {
    flex-shrink: 0;
  }
</style>
