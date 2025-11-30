<!--
  FileTree.svelte - Simple IDE-style File Explorer (Binder Panel)

  Just like VS Code, Mac Finder, or Windows Explorer:
  - Shows actual folder structure
  - Click folder → expand/collapse
  - Click file → open in editor
  - No automatic categorization - trust the writer to organize their files
-->
<script>
  import { editorContent, activeFile, workspacePath } from '$lib/stores';
  import { onMount } from 'svelte';
  import TreeNode from './TreeNode.svelte';

  // Dynamically import Tauri APIs (only available in Tauri runtime)
  let tauriDialog = null;
  let tauriFs = null;
  let isTauriAvailable = false;

  export let selectedFile = "";
  let fileTree = null;
  let currentPath = "";
  let errorMsg = "";
  let isLoadingFile = false;  // Loading state for file operations

  // Track expanded folders by path (use object for Svelte reactivity)
  let expandedFolders = {};

  $: selectedFile = $activeFile;

  onMount(async () => {
    // Check if we're actually running in Tauri (not just browser)
    // @ts-ignore - __TAURI_INTERNALS__ only exists in Tauri runtime
    const inTauriRuntime = typeof window !== 'undefined' && window.__TAURI_INTERNALS__;

    if (!inTauriRuntime) {
      console.log('Not in Tauri runtime - running in browser mode');
      isTauriAvailable = false;
      return;  // Don't try to load Tauri APIs or saved projects
    }

    // We're in Tauri - load the APIs
    try {
      tauriDialog = await import('@tauri-apps/plugin-dialog');
      tauriFs = await import('@tauri-apps/plugin-fs');
      isTauriAvailable = true;

      // Load saved project if available (check workspacePath store first, then legacy key)
      const savedPath = $workspacePath || localStorage.getItem('last_project_path');
      if (savedPath) {
        await loadProject(savedPath);
      }
    } catch (e) {
      console.log('Failed to load Tauri APIs:', e);
      isTauriAvailable = false;
    }
  });

  // React to workspace path changes (e.g., from onboarding wizard)
  $: if ($workspacePath && isTauriAvailable && $workspacePath !== currentPath) {
    loadProject($workspacePath);
  }

  async function openProjectDialog() {
    if (!isTauriAvailable || !tauriDialog) {
      errorMsg = "File dialog requires the desktop app. Run: npm run tauri dev";
      return;
    }

    try {
      const selected = await tauriDialog.open({ directory: true, multiple: false });
      if (selected) {
        await loadProject(selected);
      }
    } catch (e) {
      errorMsg = "Failed to open dialog: " + e;
    }
  }

  async function loadProject(path) {
    if (!isTauriAvailable || !tauriFs) {
      errorMsg = "File access requires the desktop app. Run: npm run tauri dev";
      return;
    }

    currentPath = path;
    errorMsg = "";
    // Sync to workspacePath store (this also persists to localStorage via persistentWritable)
    workspacePath.set(path);

    try {
      const entries = await tauriFs.readDir(path, { recursive: true });
      fileTree = buildTree(entries, path);
      // Auto-expand root
      expandedFolders = { ...expandedFolders, [path]: true };
      console.log('[FileTree] Loaded project:', path, 'with', entries.length, 'entries');
    } catch (e) {
      console.error('[FileTree] Failed to load project:', e);
      errorMsg = "Cannot read folder. Check permissions.";
      fileTree = null;
    }
  }

  // Build hierarchical tree from Tauri readDir entries
  function buildTree(entries, basePath) {
    const root = {
      name: basePath.split('/').pop() || 'Project',
      path: basePath,
      isDirectory: true,
      children: []
    };

    // Process entries recursively
    function processEntries(entries, parentPath) {
      const nodes = [];

      for (const entry of entries) {
        const fullPath = `${parentPath}/${entry.name}`;
        const isDir = entry.isDirectory || entry.children;

        // Filter: only show directories, .md, and .txt files
        if (!isDir && !entry.name.endsWith('.md') && !entry.name.endsWith('.txt')) {
          continue;
        }

        const node = {
          name: entry.name,
          path: fullPath,
          isDirectory: isDir,
          children: isDir && entry.children ? processEntries(entry.children, fullPath) : []
        };

        nodes.push(node);
      }

      // Sort: folders first, then alphabetically
      return nodes.sort((a, b) => {
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        return a.name.localeCompare(b.name);
      });
    }

    root.children = processEntries(entries, basePath);
    return root;
  }

  function toggleFolder(node) {
    if (!node.isDirectory) return;

    console.log('[FileTree] toggleFolder called:', node.path, 'currently expanded:', !!expandedFolders[node.path]);

    if (expandedFolders[node.path]) {
      const { [node.path]: _, ...rest } = expandedFolders;
      expandedFolders = rest;
      console.log('[FileTree] Collapsed folder, expandedFolders now:', Object.keys(expandedFolders));
    } else {
      expandedFolders = { ...expandedFolders, [node.path]: true };
      console.log('[FileTree] Expanded folder, expandedFolders now:', Object.keys(expandedFolders));
    }
  }

  async function openFile(node) {
    if (node.isDirectory) {
      toggleFolder(node);
      return;
    }

    // Prevent double-clicks while loading
    if (isLoadingFile) return;

    try {
      isLoadingFile = true;
      selectedFile = node.path;
      errorMsg = ""; // Clear any previous error

      // Note: We don't use encodeURIComponent on the full path because FastAPI's
      // {filepath:path} expects the slashes to be preserved. We only need to handle
      // special characters in individual path segments if any.
      const response = await fetch(`http://localhost:8000/files/${node.path}`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || "Backend failed to read file");
      }

      const data = await response.json();
      editorContent.set(data.content);
      activeFile.set(node.path);
    } catch (e) {
      console.error("FileTree: Failed to open file:", e);
      errorMsg = `Failed to read file: ${e.message}`;
      // Reset selection on error
      selectedFile = "";
    } finally {
      isLoadingFile = false;
    }
  }
</script>

<div class="binder">
  <!-- Header -->
  <div class="binder-header">
    <div class="header-title">
      <span class="label">BINDER</span>
      <strong class="project-name" title={currentPath}>
        {currentPath ? currentPath.split('/').pop() : "No Project"}
      </strong>
    </div>
    <button class="header-btn" on:click={openProjectDialog} title="Open Project">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
      </svg>
    </button>
  </div>

  {#if errorMsg}
    <div class="error">{errorMsg}</div>
  {/if}

  <!-- File Tree -->
  {#if fileTree}
    <div class="tree-container" class:loading={isLoadingFile}>
      {#each fileTree.children as node (node.path)}
        <TreeNode
          {node}
          depth={0}
          {expandedFolders}
          {openFile}
          {toggleFolder}
          loadingFile={isLoadingFile ? selectedFile : null}
        />
      {/each}
    </div>
  {:else if !currentPath}
    <!-- Empty State -->
    <div class="empty-state">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
      {#if isTauriAvailable}
        <button class="open-btn" on:click={openProjectDialog}>
          Open Project Folder
        </button>
        <p class="empty-hint">Select your content folder to begin</p>
      {:else}
        <!-- Browser mode: file browser disabled, chat still works -->
        <p class="empty-hint">Desktop app required</p>
      {/if}
    </div>
  {/if}
</div>

<style>
  .binder {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-secondary, #1a2027);
    color: var(--text-primary, #e6edf3);
    font-family: var(--font-sans);
    user-select: none;
  }

  /* Header */
  .binder-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-3, 12px);
    border-bottom: 1px solid var(--border, #2d3a47);
    background: var(--bg-tertiary, #252d38);
  }

  .header-title {
    display: flex;
    flex-direction: column;
    gap: 2px;
    overflow: hidden;
  }

  .label {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-muted, #8b949e);
    letter-spacing: 0.1em;
  }

  .project-name {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .header-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .header-btn:hover {
    background: var(--bg-elevated, #2d3a47);
    border-color: var(--border-strong, #3d4a57);
    color: var(--text-primary);
  }

  /* Tree Container */
  .tree-container {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-2, 8px) 0;
  }

  .tree-container.loading {
    opacity: 0.8;
    pointer-events: none;
  }

  /* Empty State */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    padding: var(--space-6, 24px);
    text-align: center;
  }

  .empty-icon {
    color: var(--text-muted, #6e7681);
    margin-bottom: var(--space-4, 16px);
    opacity: 0.5;
  }

  .open-btn {
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .open-btn:hover {
    background: var(--accent-cyan-hover, #79b8ff);
    transform: translateY(-1px);
  }

  .empty-hint {
    margin-top: var(--space-3, 12px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  /* Error State */
  .error {
    margin: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--error-bg, rgba(248, 81, 73, 0.15));
    border: 1px solid var(--error, #f85149);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-xs, 11px);
    color: var(--error, #f85149);
  }

  /* Scrollbar */
  .tree-container::-webkit-scrollbar {
    width: 6px;
  }

  .tree-container::-webkit-scrollbar-track {
    background: transparent;
  }

  .tree-container::-webkit-scrollbar-thumb {
    background: var(--border, #2d3a47);
    border-radius: 3px;
  }

  .tree-container::-webkit-scrollbar-thumb:hover {
    background: var(--border-strong, #3d4a57);
  }
</style>
