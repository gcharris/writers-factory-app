<!--
  Writers Factory - Main Application Page

  Phase 5 Track 1: Critical UI Implementation
  - 4-panel IDE layout with Cyber-Noir theme
  - Settings Panel for API keys and orchestrator
  - Mode-aware Studio Panel with action cards
  - Foreman Chat integration
-->
<script>
  import MainLayout from '$lib/components/MainLayout.svelte';
  import StudioPanel from '$lib/components/StudioPanel.svelte';
  import FileTree from '$lib/components/FileTree.svelte';
  import Editor from '$lib/components/Editor.svelte';
  import ChatSidebar from '$lib/components/ChatSidebar.svelte';
  import AgentPanel from '$lib/components/AgentPanel.svelte';
</script>

<MainLayout>
  <!-- Studio Panel: Mode-aware action cards -->
  <svelte:fragment slot="studio">
    <StudioPanel />
  </svelte:fragment>

  <!-- Canvas Panel: File Tree + Editor -->
  <svelte:fragment slot="canvas">
    <div class="canvas-layout">
      <aside class="file-browser">
        <FileTree />
      </aside>
      <main class="editor-area">
        <Editor />
      </main>
    </div>
  </svelte:fragment>

  <!-- Graph Panel: Agent Panel (placeholder for Knowledge Graph) -->
  <svelte:fragment slot="graph">
    <div class="graph-placeholder">
      <AgentPanel />
    </div>
  </svelte:fragment>

  <!-- Foreman Panel: Chat Interface -->
  <svelte:fragment slot="foreman">
    <ChatSidebar />
  </svelte:fragment>
</MainLayout>

<style>
  /* Canvas Layout: File Browser + Editor */
  .canvas-layout {
    display: flex;
    height: 100%;
    background: var(--bg-primary, #0f1419);
  }

  .file-browser {
    width: 200px;
    flex-shrink: 0;
    background: var(--bg-secondary, #1a2027);
    border-right: 1px solid var(--border, #2d3a47);
    overflow-y: auto;
  }

  .editor-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  /* Graph Panel Placeholder */
  .graph-placeholder {
    height: 100%;
    overflow-y: auto;
  }
</style>
