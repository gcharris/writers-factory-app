<script>
  import NotebookPanel from './NotebookPanel.svelte';
  import HealthDashboard from './HealthDashboard.svelte';

  let activeTab = 'notebook';
</script>

<div class="tabbed-panel">
  <div class="tab-bar">
    <button
      class="tab"
      class:active={activeTab === 'notebook'}
      on:click={() => activeTab = 'notebook'}
    >
      NotebookLM
    </button>
    <button
      class="tab"
      class:active={activeTab === 'health'}
      on:click={() => activeTab = 'health'}
    >
      Metabolism
    </button>
  </div>

  <div class="tab-content">
    {#if activeTab === 'notebook'}
      <NotebookPanel />
    {:else if activeTab === 'health'}
      <HealthDashboard />
    {/if}
  </div>
</div>

<style>
  .tabbed-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #ffffff;
  }

  .tab-bar {
    display: flex;
    background: #f3f4f6;
    border-bottom: 1px solid #e5e7eb;
    flex-shrink: 0;
  }

  .tab {
    flex: 1;
    padding: 0.5rem 0.75rem;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 0.8rem;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .tab:hover {
    color: #374151;
    background: #e5e7eb;
  }

  .tab.active {
    color: #2563eb;
    border-bottom-color: #2563eb;
    background: #ffffff;
  }

  .tab-content {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }
</style>
