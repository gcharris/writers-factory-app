<!--
  Writers Factory - Main Application Page

  3-Panel IDE Layout (Cyber-Noir Theme):
  ┌────────────┬─────────────────────────────┬──────────────────────────┐
  │  BINDER    │           CANVAS            │      THE FOREMAN         │
  │  (240px)   │      (flex, min 500px)      │        (400px)           │
  │            │                             │                          │
  │  FileTree  │   Monaco Editor             │  Chat Interface          │
  └────────────┴─────────────────────────────┴──────────────────────────┘

  Modals accessible from Foreman header:
  - NotebookLM: Research queries grounded in uploaded sources
  - Studio Tools: Tabbed panel with Voice Tournament, Scaffold, Health, etc.
  - Graph Viewer: Knowledge Graph visualization
  - Settings: Configuration panels
-->
<script>
  import MainLayout from '$lib/components/MainLayout.svelte';
  import FileTree from '$lib/components/FileTree.svelte';
  import Editor from '$lib/components/Editor.svelte';
  import ForemanPanel from '$lib/components/ForemanPanel.svelte';
  import Modal from '$lib/components/Modal.svelte';
  import SettingsPanel from '$lib/components/SettingsPanel.svelte';
  import StudioToolsPanel from '$lib/components/StudioToolsPanel.svelte';
  import GraphModal from '$lib/components/GraphModal.svelte';
  import NotebookLMPanel from '$lib/components/NotebookLMPanel.svelte';
  import SessionManagerModal from '$lib/components/SessionManagerModal.svelte';
  import { activeFile, activeModal } from '$lib/stores';

  // Breadcrumb from active file
  $: breadcrumb = $activeFile
    ? $activeFile.split('/').slice(-3).join(' / ')
    : 'No file selected';

  // Modal open state derived from store
  $: settingsOpen = $activeModal === 'settings';
  $: studioOpen = $activeModal === 'studio-tools';
  $: graphOpen = $activeModal === 'graph-viewer';
  $: notebookOpen = $activeModal === 'notebooklm';
  $: sessionsOpen = $activeModal === 'session-manager';

  // Reference to ForemanPanel for loading sessions
  let foremanPanelRef;

  function closeModal() {
    activeModal.set(null);
  }
</script>

<MainLayout>
  <!-- BINDER Panel: File Tree organized by category -->
  <svelte:fragment slot="binder">
    <FileTree />
  </svelte:fragment>

  <!-- CANVAS Panel: Editor with file breadcrumb -->
  <svelte:fragment slot="canvas">
    <div class="canvas-container">
      <!-- Breadcrumb bar -->
      <div class="breadcrumb-bar">
        <span class="breadcrumb-path">{breadcrumb}</span>
        <div class="breadcrumb-actions">
          <button class="breadcrumb-btn" title="Split view">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="12" y1="3" x2="12" y2="21"></line>
            </svg>
          </button>
          <button class="breadcrumb-btn" title="More options">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="1"></circle>
              <circle cx="19" cy="12" r="1"></circle>
              <circle cx="5" cy="12" r="1"></circle>
            </svg>
          </button>
        </div>
      </div>

      <!-- Editor area -->
      <div class="editor-container">
        <Editor />
      </div>
    </div>
  </svelte:fragment>

  <!-- THE FOREMAN Panel: Chat with header buttons -->
  <svelte:fragment slot="foreman">
    <ForemanPanel bind:this={foremanPanelRef} />
  </svelte:fragment>
</MainLayout>

<!-- Settings Modal -->
<Modal bind:open={settingsOpen} title="Settings" size="large" on:close={closeModal}>
  <SettingsPanel />
</Modal>

<!-- Studio Tools Modal -->
<Modal bind:open={studioOpen} title="Studio Tools" size="large" on:close={closeModal}>
  <StudioToolsPanel />
</Modal>

<!-- Graph Viewer Modal -->
<Modal bind:open={graphOpen} title="Knowledge Graph" size="large" on:close={closeModal}>
  <GraphModal />
</Modal>

<!-- NotebookLM Modal -->
<Modal bind:open={notebookOpen} title="NotebookLM Research" size="large" on:close={closeModal}>
  <NotebookLMPanel />
</Modal>

<!-- Session Manager Modal -->
<Modal bind:open={sessionsOpen} title="Chat Sessions" size="large" on:close={closeModal}>
  <SessionManagerModal
    on:load-session={(e) => {
      foremanPanelRef?.loadSession(e.detail.sessionId, e.detail.history);
    }}
    on:close={closeModal}
  />
</Modal>

<style>
  /* Canvas Container */
  .canvas-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary, #0f1419);
  }

  /* Breadcrumb Bar */
  .breadcrumb-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 32px;
    padding: 0 var(--space-3, 12px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .breadcrumb-path {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
    font-family: var(--font-mono, 'SF Mono', monospace);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .breadcrumb-actions {
    display: flex;
    gap: var(--space-1, 4px);
  }

  .breadcrumb-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .breadcrumb-btn:hover {
    background: var(--bg-tertiary, #252d38);
    color: var(--text-secondary, #c9d1d9);
  }

  /* Editor Container */
  .editor-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
  }
</style>
