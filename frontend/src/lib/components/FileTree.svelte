<script>
  import { open } from '@tauri-apps/plugin-dialog';
  import { readDir, readTextFile } from '@tauri-apps/plugin-fs';
  import { editorContent, activeFile } from '$lib/stores';
  import { onMount } from 'svelte';

  export let selectedFile = ""; 
  let files = [];
  let currentPath = "";
  let errorMsg = "";
  const STORAGE_KEY = "last_project_path";

  $: selectedFile = $activeFile;

  onMount(async () => {
    // 1. Auto-restore previous project
    const savedPath = localStorage.getItem(STORAGE_KEY);
    if (savedPath) {
      await loadProject(savedPath);
    }
  });

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
    localStorage.setItem(STORAGE_KEY, path); // Remember for next time
    
    try {
      const entries = await readDir(path);
      // Sort: Folders first, then Markdown/Text files
      files = entries
        .filter(f => f.isDirectory || f.name.endsWith('.md') || f.name.endsWith('.txt'))
        .sort((a, b) => (a.isDirectory === b.isDirectory ? 0 : a.isDirectory ? -1 : 1));
    } catch (e) {
      console.error(e);
      errorMsg = "Cannot read folder. Check permissions.";
      files = [];
    }
  }

  async function openFile(file) {
    if (file.isDirectory) return; // Ignore folders for now
    
    try {
      const separator = currentPath.endsWith("/") ? "" : "/";
      const fullPath = `${currentPath}${separator}${file.name}`;
      selectedFile = fullPath; 
      const text = await readTextFile(fullPath);
      editorContent.set(text);
      activeFile.set(fullPath);
    } catch (e) {
      console.error(e);
      alert("Failed to read file: " + e);
    }
  }
</script>

<div class="file-tree">
  <!-- Header: Project Name & Switch Button -->
  <div class="project-header">
    <div class="project-info">
      <span class="label">PROJECT</span>
      <strong class="project-name" title={currentPath}>
        {currentPath ? currentPath.split('/').pop() : "No Project"}
      </strong>
    </div>
    <button class="icon-btn" on:click={openProjectDialog} title="Open Project">
      📂
    </button>
  </div>
  
  {#if errorMsg}
    <div class="error">{errorMsg}</div>
  {/if}

  <!-- File List -->
  <div class="file-list">
    {#if files.length > 0}
      <ul>
        {#each files as file}
          <li>
            <button 
              class="file-item {selectedFile.endsWith(file.name) ? 'active' : ''}" 
              on:click={() => openFile(file)}
            >
              <span class="icon">{file.isDirectory ? '📁' : '📄'}</span>
              <span class="name">{file.name}</span>
            </button>
          </li>
        {/each}
      </ul>
    {:else if currentPath}
      <div class="empty-state">Folder is empty</div>
    {:else}
      <div class="empty-state">
        <button class="text-btn" on:click={openProjectDialog}>Open a folder to start</button>
      </div>
    {/if}
  </div>
</div>

<style>
  .file-tree { 
    background: #f8f9fa; 
    height: 100%; 
    display: flex; 
    flex-direction: column; 
    border-right: 1px solid #e5e7eb;
    font-family: sans-serif; 
    user-select: none;
  }

  .project-header {
    padding: 1rem;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f3f4f6;
  }

  .project-info { display: flex; flex-direction: column; overflow: hidden; }
  .label { font-size: 0.65rem; color: #6b7280; font-weight: bold; letter-spacing: 0.05em; }
  .project-name { font-size: 0.9rem; color: #1f2937; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  .icon-btn {
    background: transparent;
    border: 1px solid transparent;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    font-size: 1rem;
  }
  .icon-btn:hover { background: #e5e7eb; border-color: #d1d5db; }

  .file-list { flex: 1; overflow-y: auto; padding: 0.5rem 0; }
  
  ul { list-style: none; padding: 0; margin: 0; }
  li { margin-bottom: 1px; }

  .file-item {
    width: 100%;
    text-align: left;
    background: none;
    border: none;
    padding: 6px 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    color: #4b5563;
    transition: background 0.1s;
  }
  
  .file-item:hover { background: #e5e7eb; color: #111827; }
  .file-item.active { background: #e0e7ff; color: #4338ca; font-weight: 500; border-right: 3px solid #4338ca; }
  
  .icon { opacity: 0.6; font-size: 0.9rem; }
  
  .empty-state { 
    padding: 2rem 1rem; 
    text-align: center; 
    color: #9ca3af; 
    font-size: 0.85rem; 
    font-style: italic; 
  }
  
  .text-btn { color: #2563eb; background: none; border: none; cursor: pointer; text-decoration: underline; }
  .error { font-size: 0.8rem; color: #dc2626; background: #fee2e2; padding: 0.5rem; margin: 0.5rem; border-radius: 4px; }
</style>
