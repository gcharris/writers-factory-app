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

  // Panel collapse state
  let binderCollapsed = false;
  let foremanCollapsed = false;

  // Settings modal
  let showSettings = false;

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

  function toggleBinder() {
    binderCollapsed = !binderCollapsed;
  }

  function toggleForeman() {
    foremanCollapsed = !foremanCollapsed;
  }

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
              <span class="mode-name">{mode === 'VOICE_CALIBRATION' ? 'VOICE' : mode}</span>
            </button>
          {/each}
        </nav>
      {/if}
    </div>

    <div class="toolbar-right">
      <!-- Window controls placeholder -->
      <div class="window-controls">
        <button class="window-btn" title="Minimize">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        <button class="window-btn" title="Maximize">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"></rect>
          </svg>
        </button>
        <button class="window-btn settings" on:click={openSettings} title="Settings">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Panel Area -->
  <div class="panel-container">
    <!-- BINDER Panel (Left) -->
    <aside class="panel panel-binder {binderCollapsed ? 'collapsed' : ''}">
      <div class="panel-header">
        <button class="panel-toggle" on:click={toggleBinder} title={binderCollapsed ? 'Expand' : 'Collapse'}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            {#if binderCollapsed}
              <polyline points="9 18 15 12 9 6"></polyline>
            {:else}
              <polyline points="15 18 9 12 15 6"></polyline>
            {/if}
          </svg>
        </button>
        {#if !binderCollapsed}
          <span class="panel-title">BINDER</span>
          <span class="panel-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
          </span>
        {/if}
      </div>
      {#if !binderCollapsed}
        <div class="panel-content">
          <slot name="binder" />
        </div>
      {/if}
    </aside>

    <!-- CANVAS Panel (Center) -->
    <main class="panel panel-canvas">
      <slot name="canvas" />
    </main>

    <!-- THE FOREMAN Panel -->
    <aside class="panel panel-foreman {foremanCollapsed ? 'collapsed' : ''}">
      <div class="panel-header" style="--mode-color: {modeColors[$foremanMode] || modeColors.ARCHITECT}">
        <button class="panel-toggle" on:click={toggleForeman} title={foremanCollapsed ? 'Expand' : 'Collapse'}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            {#if foremanCollapsed}
              <polyline points="15 18 9 12 15 6"></polyline>
            {:else}
              <polyline points="9 18 15 12 9 6"></polyline>
            {/if}
          </svg>
        </button>
        {#if !foremanCollapsed}
          <span class="panel-title">THE FOREMAN</span>
          {#if $foremanMode}
            <span class="mode-badge" style="background: {modeColors[$foremanMode]}20; color: {modeColors[$foremanMode]}">
              {$foremanMode === 'VOICE_CALIBRATION' ? 'VOICE' : $foremanMode}
            </span>
          {/if}
          <span class="panel-actions">
            <button class="panel-action-btn" title="Expand">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 3 21 3 21 9"></polyline>
                <polyline points="9 21 3 21 3 15"></polyline>
                <line x1="21" y1="3" x2="14" y2="10"></line>
                <line x1="3" y1="21" x2="10" y2="14"></line>
              </svg>
            </button>
          </span>
        {/if}
      </div>
      {#if !foremanCollapsed}
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

  .window-controls {
    display: flex;
    gap: var(--space-1);
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

  /* ============================================
   * PANELS (Base Styles)
   * ============================================ */
  .panel {
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary);
    transition: width var(--transition-normal);
  }

  .panel-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    height: 36px;
    padding: 0 var(--space-2);
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border);
  }

  .panel-title {
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    color: var(--text-secondary);
    letter-spacing: 0.5px;
    flex: 1;
  }

  .panel-icon {
    display: flex;
    color: var(--text-muted);
  }

  .panel-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .panel-toggle:hover {
    background: var(--bg-elevated);
    border-color: var(--border-strong);
    color: var(--accent-cyan);
  }

  .panel-content {
    flex: 1;
    overflow: hidden;
  }

  .panel.collapsed {
    width: 36px !important;
  }

  .panel.collapsed .panel-header {
    justify-content: center;
    padding: 0;
  }

  .panel.collapsed .panel-content {
    display: none;
  }

  /* ============================================
   * BINDER PANEL (Left)
   * ============================================ */
  .panel-binder {
    width: var(--panel-binder-width);
    border-right: 1px solid var(--border);
  }

  /* ============================================
   * CANVAS PANEL (Center)
   * ============================================ */
  .panel-canvas {
    flex: 1;
    min-width: var(--panel-canvas-min);
    background: var(--bg-primary);
  }

  /* ============================================
   * FOREMAN PANEL (Right - Primary AI Interface)
   * ============================================ */
  .panel-foreman {
    width: var(--panel-foreman-width);
    border-left: 1px solid var(--border);
  }

  .panel-foreman .panel-header {
    border-left: 3px solid var(--mode-color, var(--accent-gold));
  }

  .mode-badge {
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    font-size: 9px;
    font-weight: var(--font-bold);
    letter-spacing: 0.5px;
  }

  .panel-actions {
    display: flex;
    gap: var(--space-1);
    margin-left: auto;
  }

  .panel-action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .panel-action-btn:hover {
    background: var(--bg-elevated);
    color: var(--text-secondary);
  }
</style>
