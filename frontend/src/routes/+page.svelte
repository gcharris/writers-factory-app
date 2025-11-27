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
  import { activeModal } from '$lib/stores';

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

  <!-- CANVAS Panel: Editor -->
  <svelte:fragment slot="canvas">
    <Editor />
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
  /* Page styles are handled by MainLayout and child components */
</style>
