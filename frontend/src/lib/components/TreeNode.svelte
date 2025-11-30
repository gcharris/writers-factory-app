<!--
  TreeNode.svelte - Recursive tree node for FileTree

  Renders a single file/folder with:
  - Chevron for folders (expand/collapse)
  - File/folder icon
  - Name
  - Recursive children for expanded folders
-->
<script>
  import { activeFile } from '$lib/stores';

  export let node;
  export let depth = 0;
  export let expandedFolders;
  export let openFile;
  export let toggleFolder;
  export let loadingFile = null;  // Path of file currently being loaded

  $: isExpanded = !!expandedFolders[node.path];
  $: isActive = $activeFile === node.path;
  $: isLoading = loadingFile === node.path;

  // Get file extension for icon styling
  function getFileType(name) {
    if (name.endsWith('.md')) return 'markdown';
    if (name.endsWith('.txt')) return 'text';
    return 'default';
  }

  function handleClick() {
    openFile(node);
  }
</script>

<div class="tree-node">
  <button
    class="node-row {node.isDirectory ? 'folder' : 'file'} {isActive ? 'active' : ''} {isLoading ? 'loading' : ''}"
    style="padding-left: {8 + depth * 16}px"
    on:click={handleClick}
    disabled={isLoading}
  >
    <!-- Chevron for folders -->
    {#if node.isDirectory}
      <span class="chevron" class:expanded={isExpanded}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </span>
    {:else}
      <span class="chevron-spacer"></span>
    {/if}

    <!-- Icon -->
    <span class="node-icon {node.isDirectory ? 'folder-icon' : 'file-icon'} {getFileType(node.name)}">
      {#if isLoading}
        <!-- Loading spinner -->
        <svg class="spinner" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
        </svg>
      {:else if node.isDirectory}
        {#if isExpanded}
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            <line x1="2" y1="10" x2="22" y2="10"></line>
          </svg>
        {:else}
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
        {/if}
      {:else}
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
      {/if}
    </span>

    <!-- Name -->
    <span class="node-name">{node.name}</span>
  </button>

  <!-- Children (if folder is expanded) -->
  {#if node.isDirectory && isExpanded && node.children?.length}
    {#each node.children as child (child.path)}
      <svelte:self
        node={child}
        depth={depth + 1}
        {expandedFolders}
        {openFile}
        {toggleFolder}
        {loadingFile}
      />
    {/each}
  {/if}
</div>

<style>
  .tree-node {
    /* Container for each node and its children */
  }

  .node-row {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    width: 100%;
    height: 26px;
    padding-right: var(--space-2, 8px);
    background: transparent;
    border: none;
    border-left: 2px solid transparent;
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-sm, 12px);
    cursor: pointer;
    transition: all 0.1s ease;
    text-align: left;
  }

  .node-row:hover {
    background: var(--bg-tertiary, #252d38);
    color: var(--text-primary);
  }

  .node-row.active {
    background: var(--bg-elevated, #2d3a47);
    border-left-color: var(--accent-cyan, #58a6ff);
    color: var(--text-primary);
  }

  .node-row.loading {
    opacity: 0.7;
    cursor: wait;
  }

  .node-row:disabled {
    pointer-events: none;
  }

  /* Spinner animation */
  .spinner {
    animation: spin 1s linear infinite;
    color: var(--accent-cyan, #58a6ff);
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  /* Chevron */
  .chevron {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    color: var(--text-muted, #6e7681);
    transition: transform 0.15s ease;
    flex-shrink: 0;
  }

  .chevron.expanded {
    transform: rotate(90deg);
  }

  .chevron-spacer {
    width: 16px;
    flex-shrink: 0;
  }

  /* Icons */
  .node-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .folder-icon {
    color: var(--accent-gold, #d4a574);
  }

  .file-icon {
    color: var(--text-muted, #6e7681);
  }

  .file-icon.markdown {
    color: var(--accent-cyan, #58a6ff);
  }

  .file-icon.text {
    color: var(--text-secondary, #8b949e);
  }

  .node-row.active .node-icon {
    color: var(--accent-cyan, #58a6ff);
  }

  /* Name */
  .node-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
