<!--
  Editor.svelte - Monaco-style Prose Editor (Cyber-Noir Theme)

  A clean, distraction-free writing environment matching the mockup:
  - Dark theme background
  - Serif font for prose (Georgia)
  - Minimal toolbar with filename and save indicator
  - Cmd/Ctrl+S to save
-->
<script>
  import { editorContent, activeFile, isSaving } from '$lib/stores';

  let currentFile = "";
  let lastSaved = "";
  let saveError = "";

  $: currentFile = $activeFile;

  async function saveFile() {
    if (!currentFile) return;

    isSaving.set(true);
    saveError = "";

    try {
      const response = await fetch(`http://localhost:8000/files/${encodeURIComponent(currentFile)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: $editorContent })
      });

      if (!response.ok) throw new Error("Backend failed to save file");

      lastSaved = new Date().toLocaleTimeString();
    } catch (e) {
      saveError = e.message;
      console.error("Error saving:", e);
    } finally {
      isSaving.set(false);
    }
  }

  function handleKeydown(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      saveFile();
    }
  }

  // Word count
  $: wordCount = $editorContent
    ? $editorContent.trim().split(/\s+/).filter(w => w.length > 0).length
    : 0;
</script>

<svelte:window on:keydown={handleKeydown}/>

<div class="editor-wrapper">
  <!-- Editor Toolbar -->
  <div class="editor-toolbar">
    <div class="toolbar-left">
      <span class="filename">{currentFile ? currentFile.split('/').pop() : "No file selected"}</span>
    </div>
    <div class="toolbar-right">
      {#if wordCount > 0}
        <span class="word-count">{wordCount.toLocaleString()} words</span>
      {/if}
      {#if $isSaving}
        <span class="save-status saving">Saving...</span>
      {:else if lastSaved}
        <span class="save-status saved">Saved {lastSaved}</span>
      {/if}
      {#if saveError}
        <span class="save-status error">Error: {saveError}</span>
      {/if}
    </div>
  </div>

  <!-- Writing Area -->
  <div class="writing-area">
    {#if currentFile}
      <textarea
        bind:value={$editorContent}
        placeholder="Start writing..."
        spellcheck="true"
      ></textarea>
    {:else}
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="12" y1="18" x2="12" y2="12"></line>
            <line x1="9" y1="15" x2="15" y2="15"></line>
          </svg>
        </div>
        <p class="empty-title">No file selected</p>
        <p class="empty-hint">Open a file from the Binder to start writing</p>
      </div>
    {/if}
  </div>
</div>

<style>
  .editor-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary, #0f1419);
  }

  /* Toolbar */
  .editor-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 36px;
    padding: 0 var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .filename {
    font-size: var(--text-sm, 13px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  .toolbar-right {
    display: flex;
    align-items: center;
    gap: var(--space-4, 16px);
  }

  .word-count {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  .save-status {
    font-size: var(--text-xs, 11px);
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  .save-status.saving {
    color: var(--accent-gold, #d4a574);
  }

  .save-status.saved {
    color: var(--success, #3fb950);
  }

  .save-status.error {
    color: var(--error, #f85149);
  }

  /* Writing Area */
  .writing-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  textarea {
    flex: 1;
    width: 100%;
    padding: var(--space-8, 32px);
    padding-top: var(--space-6, 24px);
    background: var(--bg-primary, #0f1419);
    border: none;
    resize: none;
    outline: none;

    /* Typography for prose */
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 18px;
    line-height: 1.8;
    color: var(--text-primary, #e6edf3);

    /* Subtle text shadow for readability */
    text-shadow: 0 0 0 transparent;
  }

  textarea::placeholder {
    color: var(--text-muted, #8b949e);
    font-style: italic;
  }

  textarea:focus {
    outline: none;
  }

  /* Scrollbar */
  textarea::-webkit-scrollbar {
    width: 8px;
  }

  textarea::-webkit-scrollbar-track {
    background: transparent;
  }

  textarea::-webkit-scrollbar-thumb {
    background: var(--border, #2d3a47);
    border-radius: 4px;
  }

  textarea::-webkit-scrollbar-thumb:hover {
    background: var(--border-strong, #3d4a57);
  }

  /* Empty State */
  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-8, 32px);
    text-align: center;
  }

  .empty-icon {
    color: var(--text-muted, #8b949e);
    opacity: 0.5;
    margin-bottom: var(--space-4, 16px);
  }

  .empty-title {
    font-size: var(--text-lg, 18px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #c9d1d9);
    margin: 0 0 var(--space-2, 8px) 0;
  }

  .empty-hint {
    font-size: var(--text-sm, 13px);
    color: var(--text-muted, #8b949e);
    margin: 0;
  }
</style>
