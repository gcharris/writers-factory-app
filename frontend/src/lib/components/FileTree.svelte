<!--
  FileTree.svelte - Binder Panel (Cyber-Noir Theme)

  Matching the mockup with:
  - Hierarchical sections: Story Bible, Manuscript, World Database
  - Status badges (Complete, Partial, etc.)
  - Collapsible folder groups
  - Dark theme styling consistent with the rest of the app
-->
<script>
  import { open } from '@tauri-apps/plugin-dialog';
  import { readDir } from '@tauri-apps/plugin-fs';
  import { editorContent, activeFile, storyBibleStatus } from '$lib/stores';
  import { onMount } from 'svelte';

  export let selectedFile = "";
  let files = [];
  let currentPath = "";
  let errorMsg = "";
  const STORAGE_KEY = "last_project_path";

  // Organized file structure
  let storyBible = [];
  let manuscript = [];
  let worldDatabase = [];
  let otherFiles = [];

  // Collapse state
  let expandedSections = {
    storyBible: true,
    manuscript: true,
    worldDatabase: false,
    other: false
  };

  $: selectedFile = $activeFile;

  onMount(async () => {
    const savedPath = localStorage.getItem(STORAGE_KEY);
    if (savedPath) {
      await loadProject(savedPath);
    }
    // Fetch Story Bible status from API
    await fetchStoryBibleStatus();
  });

  async function fetchStoryBibleStatus() {
    try {
      const res = await fetch('http://localhost:8000/story-bible/status');
      if (res.ok) {
        const data = await res.json();
        storyBibleStatus.set(data);
      }
    } catch (e) {
      console.warn('Failed to fetch Story Bible status:', e);
    }
  }

  async function openProjectDialog() {
    try {
      const selected = await open({ directory: true, multiple: false });
      if (selected) {
        await loadProject(selected);
      }
    } catch (e) {
      errorMsg = "Failed to open dialog: " + e;
    }
  }

  async function loadProject(path) {
    currentPath = path;
    errorMsg = "";
    localStorage.setItem(STORAGE_KEY, path);

    try {
      const entries = await readDir(path, { recursive: true });
      files = flattenEntries(entries, path);
      organizeFiles();
    } catch (e) {
      console.error(e);
      errorMsg = "Cannot read folder. Check permissions.";
      files = [];
    }
  }

  function flattenEntries(entries, basePath, depth = 0) {
    let result = [];
    for (const entry of entries) {
      const isDir = entry.isDirectory || entry.children;
      const fullPath = `${basePath}/${entry.name}`;

      result.push({
        name: entry.name,
        path: fullPath,
        isDirectory: isDir,
        depth
      });

      if (isDir && entry.children) {
        result = result.concat(flattenEntries(entry.children, fullPath, depth + 1));
      }
    }
    return result.filter(f => f.isDirectory || f.name.endsWith('.md') || f.name.endsWith('.txt'));
  }

  function organizeFiles() {
    storyBible = files.filter(f =>
      f.path.includes('/Story Bible/') ||
      f.path.includes('/Characters/') ||
      f.name === 'Protagonist.md' ||
      f.name === 'Beat_Sheet.md' ||
      f.name === 'Theme.md'
    );

    manuscript = files.filter(f =>
      f.path.includes('/Manuscript/') ||
      f.path.includes('/Chapters/') ||
      f.path.includes('/Scenes/')
    );

    worldDatabase = files.filter(f =>
      f.path.includes('/World Bible/') ||
      f.path.includes('/World Database/') ||
      f.name === 'World Rules.md'
    );

    // Everything else
    const categorized = new Set([...storyBible, ...manuscript, ...worldDatabase].map(f => f.path));
    otherFiles = files.filter(f => !categorized.has(f.path) && !f.isDirectory);
  }

  async function openFile(file) {
    if (file.isDirectory) return;

    try {
      selectedFile = file.path;

      const response = await fetch(`http://localhost:8000/files/${encodeURIComponent(file.path)}`);
      if (!response.ok) throw new Error("Backend failed to read file");

      const data = await response.json();
      editorContent.set(data.content);
      activeFile.set(file.path);
    } catch (e) {
      console.error(e);
      errorMsg = "Failed to read file: " + e;
    }
  }

  function toggleSection(section) {
    expandedSections[section] = !expandedSections[section];
  }

  function getFileStatus(file) {
    // Check against Story Bible status
    if ($storyBibleStatus?.artifacts) {
      const artifact = $storyBibleStatus.artifacts.find(a =>
        file.name.toLowerCase().includes(a.name.toLowerCase())
      );
      if (artifact) {
        return artifact.status;
      }
    }
    return null;
  }

  // Icons
  const icons = {
    folder: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
    </svg>`,
    file: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
    </svg>`,
    chevronDown: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="6 9 12 15 18 9"></polyline>
    </svg>`,
    chevronRight: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="9 18 15 12 9 6"></polyline>
    </svg>`,
    book: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
    </svg>`,
    edit: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
    </svg>`,
    globe: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="2" y1="12" x2="22" y2="12"></line>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
    </svg>`,
    openFolder: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
    </svg>`
  };
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
      {@html icons.openFolder}
    </button>
  </div>

  {#if errorMsg}
    <div class="error">{errorMsg}</div>
  {/if}

  <!-- File Sections -->
  <div class="sections">
    <!-- Story Bible Section -->
    <div class="section">
      <button class="section-header" on:click={() => toggleSection('storyBible')}>
        <span class="section-chevron">
          {@html expandedSections.storyBible ? icons.chevronDown : icons.chevronRight}
        </span>
        <span class="section-icon story-bible">{@html icons.book}</span>
        <span class="section-title">Story Bible</span>
        {#if $storyBibleStatus?.complete_count !== undefined}
          <span class="section-badge {$storyBibleStatus.is_complete ? 'complete' : 'partial'}">
            {$storyBibleStatus.complete_count}/{$storyBibleStatus.total_count}
          </span>
        {/if}
      </button>

      {#if expandedSections.storyBible}
        <div class="section-content">
          {#if storyBible.length > 0}
            {#each storyBible as file}
              <button
                class="file-item {selectedFile === file.path ? 'active' : ''}"
                style="padding-left: {12 + (file.depth || 0) * 12}px"
                on:click={() => openFile(file)}
              >
                <span class="file-icon">
                  {@html file.isDirectory ? icons.folder : icons.file}
                </span>
                <span class="file-name">{file.name}</span>
                {#if getFileStatus(file)}
                  <span class="file-status {getFileStatus(file)}">
                    {getFileStatus(file) === 'complete' ? '✓' : '◐'}
                  </span>
                {/if}
              </button>
            {/each}
          {:else}
            <div class="empty-section">No Story Bible files</div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Manuscript Section -->
    <div class="section">
      <button class="section-header" on:click={() => toggleSection('manuscript')}>
        <span class="section-chevron">
          {@html expandedSections.manuscript ? icons.chevronDown : icons.chevronRight}
        </span>
        <span class="section-icon manuscript">{@html icons.edit}</span>
        <span class="section-title">Manuscript</span>
        {#if manuscript.length > 0}
          <span class="section-count">{manuscript.length}</span>
        {/if}
      </button>

      {#if expandedSections.manuscript}
        <div class="section-content">
          {#if manuscript.length > 0}
            {#each manuscript as file}
              <button
                class="file-item {selectedFile === file.path ? 'active' : ''}"
                style="padding-left: {12 + (file.depth || 0) * 12}px"
                on:click={() => openFile(file)}
              >
                <span class="file-icon">
                  {@html file.isDirectory ? icons.folder : icons.file}
                </span>
                <span class="file-name">{file.name}</span>
              </button>
            {/each}
          {:else}
            <div class="empty-section">No manuscripts yet</div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- World Database Section -->
    <div class="section">
      <button class="section-header" on:click={() => toggleSection('worldDatabase')}>
        <span class="section-chevron">
          {@html expandedSections.worldDatabase ? icons.chevronDown : icons.chevronRight}
        </span>
        <span class="section-icon world">{@html icons.globe}</span>
        <span class="section-title">World Database</span>
        {#if worldDatabase.length > 0}
          <span class="section-count">{worldDatabase.length}</span>
        {/if}
      </button>

      {#if expandedSections.worldDatabase}
        <div class="section-content">
          {#if worldDatabase.length > 0}
            {#each worldDatabase as file}
              <button
                class="file-item {selectedFile === file.path ? 'active' : ''}"
                style="padding-left: {12 + (file.depth || 0) * 12}px"
                on:click={() => openFile(file)}
              >
                <span class="file-icon">
                  {@html file.isDirectory ? icons.folder : icons.file}
                </span>
                <span class="file-name">{file.name}</span>
              </button>
            {/each}
          {:else}
            <div class="empty-section">No world files</div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Other Files Section -->
    {#if otherFiles.length > 0}
      <div class="section">
        <button class="section-header" on:click={() => toggleSection('other')}>
          <span class="section-chevron">
            {@html expandedSections.other ? icons.chevronDown : icons.chevronRight}
          </span>
          <span class="section-icon other">{@html icons.folder}</span>
          <span class="section-title">Other Files</span>
          <span class="section-count">{otherFiles.length}</span>
        </button>

        {#if expandedSections.other}
          <div class="section-content">
            {#each otherFiles as file}
              <button
                class="file-item {selectedFile === file.path ? 'active' : ''}"
                on:click={() => openFile(file)}
              >
                <span class="file-icon">
                  {@html icons.file}
                </span>
                <span class="file-name">{file.name}</span>
              </button>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Empty State -->
  {#if !currentPath}
    <div class="empty-state">
      <div class="empty-icon">{@html icons.openFolder}</div>
      <button class="open-btn" on:click={openProjectDialog}>
        Open Project Folder
      </button>
      <p class="empty-hint">Select your content folder to begin</p>
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
    padding: var(--space-3);
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
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    color: var(--text-muted, #8b949e);
    letter-spacing: 0.1em;
  }

  .project-name {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
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
    border-radius: var(--radius-md);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .header-btn:hover {
    background: var(--bg-elevated, #2d3a47);
    border-color: var(--border-strong, #3d4a57);
    color: var(--text-primary);
  }

  /* Sections */
  .sections {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-2) 0;
  }

  .section {
    margin-bottom: var(--space-1);
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: background var(--transition-fast);
  }

  .section-header:hover {
    background: var(--bg-tertiary, #252d38);
  }

  .section-chevron {
    display: flex;
    align-items: center;
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .section-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .section-icon.story-bible { color: var(--accent-gold, #d4a574); }
  .section-icon.manuscript { color: var(--accent-cyan, #58a6ff); }
  .section-icon.world { color: var(--accent-purple, #a371f7); }
  .section-icon.other { color: var(--text-muted); }

  .section-title {
    flex: 1;
    text-align: left;
  }

  .section-badge {
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
  }

  .section-badge.complete {
    background: var(--success-bg, rgba(59, 130, 246, 0.2));
    color: var(--success, #3fb950);
  }

  .section-badge.partial {
    background: var(--warning-bg, rgba(212, 165, 116, 0.2));
    color: var(--warning, #d29922);
  }

  .section-count {
    font-size: var(--text-xs);
    color: var(--text-muted);
    background: var(--bg-elevated);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
  }

  .section-content {
    padding-left: var(--space-2);
  }

  /* File Items */
  .file-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    width: 100%;
    padding: var(--space-1) var(--space-3);
    background: transparent;
    border: none;
    border-left: 2px solid transparent;
    color: var(--text-secondary);
    font-size: var(--text-sm);
    cursor: pointer;
    transition: all var(--transition-fast);
    text-align: left;
  }

  .file-item:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .file-item.active {
    background: var(--bg-elevated);
    border-left-color: var(--accent-cyan);
    color: var(--accent-cyan);
  }

  .file-icon {
    display: flex;
    align-items: center;
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .file-item.active .file-icon {
    color: var(--accent-cyan);
  }

  .file-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .file-status {
    font-size: var(--text-xs);
    flex-shrink: 0;
  }

  .file-status.complete { color: var(--success); }
  .file-status.partial { color: var(--warning); }

  .empty-section {
    padding: var(--space-2) var(--space-3);
    padding-left: calc(var(--space-3) + 24px);
    font-size: var(--text-xs);
    color: var(--text-muted);
    font-style: italic;
  }

  /* Empty State */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    padding: var(--space-6);
    text-align: center;
  }

  .empty-icon {
    color: var(--text-muted);
    margin-bottom: var(--space-4);
    opacity: 0.5;
  }

  .empty-icon :global(svg) {
    width: 48px;
    height: 48px;
  }

  .open-btn {
    background: var(--accent-cyan);
    color: var(--bg-primary);
    border: none;
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .open-btn:hover {
    background: var(--accent-cyan-hover, #79b8ff);
    transform: translateY(-1px);
  }

  .empty-hint {
    margin-top: var(--space-3);
    font-size: var(--text-xs);
    color: var(--text-muted);
  }

  /* Error State */
  .error {
    margin: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--error-bg, rgba(248, 81, 73, 0.15));
    border: 1px solid var(--error, #f85149);
    border-radius: var(--radius-md);
    font-size: var(--text-xs);
    color: var(--error);
  }

  /* Scrollbar */
  .sections::-webkit-scrollbar {
    width: 6px;
  }

  .sections::-webkit-scrollbar-track {
    background: transparent;
  }

  .sections::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
  }

  .sections::-webkit-scrollbar-thumb:hover {
    background: var(--border-strong);
  }
</style>
