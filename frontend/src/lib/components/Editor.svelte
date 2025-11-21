<script>
  import { editorContent } from '$lib/stores';
  import { writeTextFile } from '@tauri-apps/plugin-fs';
  
  export let activeFile = ""; 
  let lastSaved = "";

  async function saveFile() {
    if (!activeFile) return;
    try {
      await writeTextFile(activeFile, $editorContent);
      lastSaved = new Date().toLocaleTimeString();
      console.log("Saved locally!");
    } catch (e) {
      alert("Error saving: " + e);
    }
  }

  function handleKeydown(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      saveFile();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown}/>

<div class="editor-container">
  <div class="toolbar">
    <!-- Display only the filename, no button -->
    <span class="filename">{activeFile ? activeFile.split('/').pop() : "No file selected"}</span>
    {#if lastSaved}
      <span class="saved-indicator">Saved {lastSaved}</span>
    {/if}
  </div>
  <textarea bind:value={$editorContent} placeholder="Open a folder to start writing..."></textarea>
</div>

<style>
  .editor-container { flex: 1; display: flex; flex-direction: column; height: 100%; background: white; }
  .toolbar { padding: 0.5rem 1rem; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; font-family: sans-serif; font-size: 0.9rem; color: #6b7280; background: #f9fafb; min-height: 32px;}
  .filename { font-weight: 600; color: #374151; }
  .saved-indicator { font-size: 0.75rem; color: #10b981; transition: opacity 0.5s; }
  textarea { flex: 1; padding: 2rem; border: none; resize: none; font-size: 1.1rem; line-height: 1.6; outline: none; font-family: 'Georgia', serif; color: #1f2937; }
</style>