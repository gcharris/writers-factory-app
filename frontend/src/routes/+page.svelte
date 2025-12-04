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
  import { onMount } from 'svelte';
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
  import OnboardingWizard from '$lib/components/Onboarding/OnboardingWizard.svelte';
  import { activeModal, hasCompletedOnboarding } from '$lib/stores';

  // Modal open state derived from store
  $: settingsOpen = $activeModal === 'settings';
  $: studioOpen = $activeModal === 'studio-tools';
  $: graphOpen = $activeModal === 'graph-viewer';
  $: notebookOpen = $activeModal === 'notebooklm';
  $: sessionsOpen = $activeModal === 'session-manager';

  // First-time onboarding wizard
  let showOnboardingWizard = false;

  // Reference to ForemanPanel for loading sessions
  let foremanPanelRef;
  // Reference to Editor for inserting text
  let editorRef;

  function closeModal() {
    activeModal.set(null);
  }

  // Check if first-time user on mount
  onMount(() => {
    // Show onboarding wizard only if user hasn't completed it
    if (!$hasCompletedOnboarding) {
      showOnboardingWizard = true;
    }
  });

  function completeOnboarding() {
    hasCompletedOnboarding.set(true);
    showOnboardingWizard = false;
  }
</script>

<MainLayout>
  <!-- BINDER Panel: File Tree organized by category -->
  <svelte:fragment slot="binder">
    <FileTree />
  </svelte:fragment>

  <!-- CANVAS Panel: Editor -->
  <svelte:fragment slot="canvas">
    <Editor
      bind:this={editorRef}
      on:copyToChat={(e) => foremanPanelRef?.insertTextToChat(e.detail.text)}
    />
  </svelte:fragment>

  <!-- THE FOREMAN Panel: Chat with header buttons -->
  <svelte:fragment slot="foreman">
    <ForemanPanel
      bind:this={foremanPanelRef}
      on:insert-to-editor={(e) => editorRef?.insertAtCursor(e.detail.text)}
    />
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

<!-- First-Time Onboarding Wizard -->
{#if showOnboardingWizard}
  <div class="onboarding-overlay">
    <div class="onboarding-container">
      <OnboardingWizard on:complete={completeOnboarding} on:close={completeOnboarding} />
    </div>
  </div>
{/if}

<style>
  /* Page styles are handled by MainLayout and child components */

  /* Onboarding wizard overlay - high z-index to be above everything */
  /* Uses semi-transparent background so user can see app behind wizard */
  .onboarding-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    backdrop-filter: blur(4px);
  }

  .onboarding-container {
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-lg, 12px);
    border: 1px solid var(--border, #2d3a47);
    max-width: 900px;
    max-height: 90vh;
    width: 90%;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  }
</style>
