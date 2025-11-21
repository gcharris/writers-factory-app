<script>
  import FileTree from '$lib/components/FileTree.svelte';
  import Editor from '$lib/components/Editor.svelte';
  import AgentPanel from '$lib/components/AgentPanel.svelte';
  import ChatSidebar from '$lib/components/ChatSidebar.svelte';
</script>

<div class="app-container">
  <aside class="left-sidebar">
    <FileTree />
  </aside>

  <main class="main-content">
    <Editor />
  </main>

  <aside class="right-sidebar">
    <!-- Top half: Tournament Squad -->
    <div class="agent-panel-wrapper">
      <AgentPanel />
    </div>
    
    <!-- Bottom half: The Manager (Cursor) -->
    <div class="manager-wrapper">
      <ChatSidebar />
    </div>
  </aside>
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background: #1e1e1e;
    color: #ccc;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    height: 100vh;
    overflow: hidden;
  }

  .app-container {
    display: flex;
    height: 100vh;
    width: 100vw;
  }

  .left-sidebar {
    width: 250px;
    background: #252526;
    border-right: 1px solid #333;
    flex-shrink: 0;
  }

  .main-content {
    flex: 1;
    background: #1e1e1e;
    display: flex;
    flex-direction: column;
  }

  .right-sidebar {
    width: 320px;
    background: #252526;
    border-left: 1px solid #333;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
  }

  .agent-panel-wrapper {
    flex: 1; /* Takes top 50% roughly */
    border-bottom: 1px solid #333;
    overflow-y: auto;
  }

  .manager-wrapper {
    flex: 1; /* Takes bottom 50% roughly */
    display: flex;
    flex-direction: column;
  }
</style>
