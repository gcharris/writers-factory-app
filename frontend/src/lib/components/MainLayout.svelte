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
    activeModal,
    addForemanMessage
  } from '$lib/stores';
  import Modal from './Modal.svelte';
  import Toast from './Toast.svelte';
  import StatusBar from './StatusBar.svelte';
  import SettingsPanel from './SettingsPanel.svelte';
  import StoryBibleWizard from './StoryBibleWizard.svelte';
  import NotebookRegistration from './NotebookRegistration.svelte';

  const BASE_URL = 'http://localhost:8000';

  // Mode transition state
  /** @type {Record<string, {mode: string, prerequisites: Array<{name: string, completed: boolean}>, all_met: boolean, ready: boolean}>} */
  let modePrerequisites = {};
  let isTransitioning = false;

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
  /** @type {Record<string, string>} */
  const modeColors = {
    ARCHITECT: 'var(--mode-architect)',
    VOICE: 'var(--mode-voice)',
    VOICE_CALIBRATION: 'var(--mode-voice)',
    DIRECTOR: 'var(--mode-director)',
    EDITOR: 'var(--mode-editor)'
  };

  // Mode icons
  /** @type {Record<string, string>} */
  const modeIcons = {
    ARCHITECT: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
    </svg>`,
    VOICE: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
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
  /** @param {CustomEvent} event */
  function handleStoryBibleComplete(event) {
    closeStoryBibleWizard();
  }

  // ==========================================================================
  // Mode Transition (Soft Guardrails)
  // ==========================================================================

  /** @type {Record<string, string>} */
  const MODE_API_MAP = {
    'ARCHITECT': 'architect',
    'VOICE': 'voice_calibration',
    'VOICE_CALIBRATION': 'voice_calibration',
    'DIRECTOR': 'director',
    'EDITOR': 'editor'
  };

  // Load prerequisites for all modes
  async function loadAllPrerequisites() {
    const modes = ['architect', 'voice_calibration', 'director', 'editor'];
    for (const mode of modes) {
      try {
        const response = await fetch(`${BASE_URL}/foreman/prerequisites/${mode}`);
        if (response.ok) {
          const data = await response.json();
          modePrerequisites[mode] = data;
        }
      } catch (e) {
        console.warn(`Failed to load prerequisites for ${mode}:`, e);
      }
    }
    modePrerequisites = modePrerequisites; // Trigger reactivity
  }

  // Request a mode transition
  /** @param {string} targetMode */
  async function requestModeTransition(targetMode) {
    const apiMode = MODE_API_MAP[targetMode];
    if (!apiMode) return;

    // Don't transition to current mode (but still allow clicking for feedback)
    const currentApiMode = $foremanMode ? MODE_API_MAP[$foremanMode] : 'architect';

    if (isTransitioning) return;
    isTransitioning = true;

    try {
      const response = await fetch(`${BASE_URL}/foreman/request-mode-change`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_mode: apiMode })
      });

      if (response.ok) {
        const result = await response.json();

        // Add Foreman's response to the chat
        if (result.foreman_message && typeof addForemanMessage === 'function') {
          addForemanMessage(result.foreman_message);
        }

        // Update mode if transition was allowed
        if (result.allowed && result.new_mode) {
          // Map API mode back to display mode
          const displayMode = result.new_mode.toUpperCase() === 'VOICE_CALIBRATION'
            ? 'VOICE'
            : result.new_mode.toUpperCase();
          foremanMode.set(displayMode);
        }

        // Refresh prerequisites after mode change
        await loadAllPrerequisites();
      }
    } catch (e) {
      console.error('Mode transition request failed:', e);
    } finally {
      isTransitioning = false;
    }
  }

  // Get tooltip for a mode button
  /** @param {string} mode */
  function getModeTooltip(mode) {
    const apiMode = MODE_API_MAP[mode];
    if (!apiMode) return `Switch to ${mode} mode`;

    const currentApiMode = $foremanMode ? MODE_API_MAP[$foremanMode] : 'architect';
    if (apiMode === currentApiMode) {
      return `Currently in ${mode} mode`;
    }

    const prereqs = modePrerequisites[apiMode];
    if (!prereqs || !prereqs.prerequisites?.length) {
      return `Switch to ${mode} mode`;
    }

    const missing = prereqs.prerequisites.filter(/** @param {{completed: boolean, name: string}} p */ p => !p.completed);
    if (!missing.length) {
      return `Ready for ${mode} mode`;
    }

    return `${mode} mode\nMissing: ${missing.map(/** @param {{name: string}} p */ p => p.name.replace(/_/g, ' ')).join(', ')}`;
  }

  // Check if mode prerequisites are met
  /** @param {string} mode */
  function areModePrereqsMet(mode) {
    const apiMode = MODE_API_MAP[mode];
    if (!apiMode || apiMode === 'architect') return true;

    const prereqs = modePrerequisites[apiMode];
    if (!prereqs || !prereqs.prerequisites?.length) return true;

    return prereqs.all_met;
  }

  // Load prerequisites on mount
  onMount(() => {
    loadAllPrerequisites();
    // Refresh every 30 seconds
    const interval = setInterval(loadAllPrerequisites, 30000);
    return () => clearInterval(interval);
  });
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

      <!-- Mode Tabs (workflow stages) -->
      <nav class="mode-tabs">
        {#each ['ARCHITECT', 'VOICE', 'DIRECTOR', 'EDITOR'] as mode}
          <button
            class="mode-tab {$foremanMode === mode ? 'active' : ''}"
            class:prereqs-met={areModePrereqsMet(mode)}
            class:transitioning={isTransitioning}
            style="--mode-color: {modeColors[mode]}"
            on:click={() => requestModeTransition(mode)}
            title={getModeTooltip(mode)}
          >
            <span class="mode-icon">{@html modeIcons[mode]}</span>
            <span class="mode-name">{mode}</span>
          </button>
        {/each}
      </nav>
    </div>

    <!-- Tools & Settings (RIGHT) -->
    <div class="toolbar-right">
      <!-- NotebookLM Button -->
      <button class="toolbar-tool-btn" on:click={() => activeModal.set('notebooklm')} title="NotebookLM Research">
        <svg width="16" height="16" viewBox="0 0 106 78" fill="currentColor" stroke="none">
          <path d="M52.96.1C23.71.1,0,23.61,0,52.62v25.15h9.76v-2.51c0-11.77,9.61-21.31,21.48-21.31s21.48,9.54,21.48,21.31v2.51h9.76v-2.51c0-17.11-13.99-30.98-31.24-30.98-6.72,0-12.94,2.1-18.03,5.69,5.33-10.51,16.31-17.73,28.99-17.73,17.91,0,32.43,14.41,32.43,32.16v13.36h9.76v-13.36c0-23.11-18.89-41.85-42.19-41.85-10.48,0-20.06,3.79-27.44,10.06,7.25-13.59,21.63-22.84,38.21-22.84,23.86,0,43.2,19.18,43.2,42.84v25.15h9.76v-25.15C105.92,23.61,82.21.1,52.96.1Z"></path>
        </svg>
        <span>NOTEBOOK</span>
      </button>

      <!-- Studio Tools Button -->
      <button class="toolbar-tool-btn" on:click={() => activeModal.set('studio-tools')} title="Studio Tools">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3l1.912 5.813a2 2 0 0 1 1.275 1.275L21 12l-5.813 1.912a2 2 0 0 1-1.275 1.275L12 21l-1.912-5.813a2 2 0 0 1-1.275-1.275L3 12l5.813-1.912a2 2 0 0 1 1.275-1.275L12 3Z" />
          <path d="M5 3v4" />
          <path d="M9 5H1" />
          <path d="M20 21l2-2" />
          <path d="M20 21l-2 2" />
          <path d="M20 21l-2-2" />
          <path d="M20 21l2 2" />
        </svg>
        <span>STUDIO</span>
      </button>

      <!-- Knowledge Graph Button -->
      <button class="toolbar-tool-btn" on:click={() => activeModal.set('graph-viewer')} title="Knowledge Graph">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3" />
          <path d="M12 3v6" />
          <path d="M12 15v6" />
          <path d="M4.2 7.5l5.2 3" />
          <path d="M14.6 13.5l5.2 3" />
          <path d="M19.8 7.5l-5.2 3" />
          <path d="M9.4 13.5l-5.2 3" />
          <circle cx="12" cy="3" r="1.5" />
          <circle cx="12" cy="21" r="1.5" />
          <circle cx="4.2" cy="7.5" r="1.5" />
          <circle cx="19.8" cy="7.5" r="1.5" />
          <circle cx="4.2" cy="16.5" r="1.5" />
          <circle cx="19.8" cy="16.5" r="1.5" />
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
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: all var(--transition-fast);
    opacity: 0.5;
  }

  /* Prerequisites met - more visible */
  .mode-tab.prereqs-met {
    opacity: 0.8;
    border-color: var(--border);
  }

  /* Transitioning state - show loading */
  .mode-tab.transitioning {
    cursor: wait;
  }

  .mode-tab:hover:not(.active) {
    opacity: 1;
    color: var(--text-secondary);
    border-color: var(--mode-color);
    transform: translateY(-1px);
  }

  .mode-tab.active {
    background: var(--bg-secondary);
    color: var(--mode-color);
    border-color: var(--mode-color);
    box-shadow: var(--shadow-sm);
    opacity: 1;
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
