<!--
  Editor.svelte - Main Editor Wrapper for Writers Factory

  Wraps CodeMirrorEditor with:
  - File toolbar (filename, save status)
  - Preview toggle (Edit / Split / Preview modes)
  - Font size controls (+/-)
  - Expand/fullscreen mode
  - Empty state when no file selected
  - Cmd/Ctrl+S save handling
  - Integration with Svelte stores
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { editorContent, activeFile, isSaving } from '$lib/stores';
  import CodeMirrorEditor from './CodeMirrorEditor.svelte';
  import EditorHelp from './EditorHelp.svelte';
  import { marked } from 'marked';

  const dispatch = createEventDispatcher();

  let editorRef;
  let lastSaved = '';
  let saveError = '';

  // View modes: 'edit' | 'split' | 'preview'
  let viewMode = 'edit';

  // Font size (14-24px range)
  let fontSize = 18;
  const MIN_FONT_SIZE = 14;
  const MAX_FONT_SIZE = 24;

  // Fullscreen/expanded mode
  let isExpanded = false;

  // Help overlay
  let showHelp = false;

  $: currentFile = $activeFile;

  // Render Markdown to HTML for preview
  $: previewHtml = $editorContent ? marked.parse($editorContent) : '';

  // ============================================
  // SAVE HANDLING
  // ============================================

  async function saveFile() {
    if (!currentFile) return;

    isSaving.set(true);
    saveError = '';

    try {
      const content = editorRef?.getContent() || $editorContent;

      const response = await fetch(`http://localhost:8000/files/${encodeURIComponent(currentFile)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });

      if (!response.ok) throw new Error('Backend failed to save file');

      lastSaved = new Date().toLocaleTimeString();
      // Update store with saved content
      editorContent.set(content);
    } catch (e) {
      saveError = e.message;
      console.error('Error saving:', e);
    } finally {
      isSaving.set(false);
    }
  }

  // Handle save event from CodeMirror (Cmd+S)
  function handleSave(event) {
    // Update store first
    editorContent.set(event.detail.content);
    saveFile();
  }

  // Handle content changes
  function handleChange(event) {
    editorContent.set(event.detail.content);
  }

  // ============================================
  // VIEW MODE CONTROLS
  // ============================================

  function setViewMode(mode) {
    viewMode = mode;
  }

  // Keyboard shortcut for preview toggle (Cmd+Shift+P)
  function handleKeydown(e) {
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'p') {
      e.preventDefault();
      // Cycle through modes: edit -> split -> preview -> edit
      if (viewMode === 'edit') viewMode = 'split';
      else if (viewMode === 'split') viewMode = 'preview';
      else viewMode = 'edit';
    }
    // Escape to exit fullscreen
    if (e.key === 'Escape' && isExpanded) {
      e.preventDefault();
      isExpanded = false;
    }
  }

  // ============================================
  // FONT SIZE CONTROLS
  // ============================================

  function increaseFontSize() {
    if (fontSize < MAX_FONT_SIZE) {
      fontSize = Math.min(fontSize + 1, MAX_FONT_SIZE);
    }
  }

  function decreaseFontSize() {
    if (fontSize > MIN_FONT_SIZE) {
      fontSize = Math.max(fontSize - 1, MIN_FONT_SIZE);
    }
  }

  // Handle font size event from CodeMirror keyboard shortcuts
  function handleFontSize(event) {
    const delta = event.detail.delta;
    if (delta > 0) {
      increaseFontSize();
    } else {
      decreaseFontSize();
    }
  }

  // ============================================
  // EXPAND/FULLSCREEN MODE
  // ============================================

  function toggleExpand() {
    isExpanded = !isExpanded;
    dispatch('expand', { expanded: isExpanded });
  }

  // ============================================
  // PUBLIC API (for external components like ForemanPanel)
  // ============================================

  // Insert text at cursor position
  export function insertAtCursor(text) {
    if (editorRef) {
      editorRef.insertAtCursor(text);
    }
  }

  // Focus the editor
  export function focus() {
    if (editorRef) {
      editorRef.focus();
    }
  }

  // Get current content
  export function getContent() {
    return editorRef?.getContent() || $editorContent;
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="editor-wrapper" class:expanded={isExpanded}>
  <!-- Editor Toolbar -->
  <div class="editor-toolbar">
    <div class="toolbar-left">
      <span class="file-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
      </span>
      <span class="filename">{currentFile ? currentFile.split('/').pop() : 'No file selected'}</span>
      {#if currentFile && currentFile.endsWith('.md')}
        <span class="file-type">Markdown</span>
      {/if}
    </div>

    <div class="toolbar-center">
      {#if currentFile && currentFile.endsWith('.md')}
        <!-- View Mode Toggle -->
        <div class="view-toggle">
          <button
            class="toggle-btn"
            class:active={viewMode === 'edit'}
            on:click={() => setViewMode('edit')}
            title="Edit only"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
          </button>
          <button
            class="toggle-btn"
            class:active={viewMode === 'split'}
            on:click={() => setViewMode('split')}
            title="Split view (Cmd+Shift+P)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="12" y1="3" x2="12" y2="21"></line>
            </svg>
          </button>
          <button
            class="toggle-btn"
            class:active={viewMode === 'preview'}
            on:click={() => setViewMode('preview')}
            title="Preview only"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </button>
        </div>

        <!-- Separator -->
        <span class="toolbar-sep"></span>

        <!-- Font Size Controls -->
        <div class="font-size-controls">
          <button
            class="font-btn"
            on:click={decreaseFontSize}
            disabled={fontSize <= MIN_FONT_SIZE}
            title="Decrease font size (Cmd+-)"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>
          <span class="font-size-label" title="Font size">{fontSize}px</span>
          <button
            class="font-btn"
            on:click={increaseFontSize}
            disabled={fontSize >= MAX_FONT_SIZE}
            title="Increase font size (Cmd++)"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>
        </div>
      {/if}
    </div>

    <div class="toolbar-right">
      {#if $isSaving}
        <span class="save-status saving">
          <svg class="spinner" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
          </svg>
          Saving...
        </span>
      {:else if saveError}
        <span class="save-status error" title={saveError}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          Error
        </span>
      {:else if lastSaved}
        <span class="save-status saved">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Saved {lastSaved}
        </span>
      {/if}

      <button class="toolbar-btn" on:click={saveFile} disabled={!currentFile || $isSaving} title="Save (Cmd+S)">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
          <polyline points="17 21 17 13 7 13 7 21"></polyline>
          <polyline points="7 3 7 8 15 8"></polyline>
        </svg>
      </button>

      <!-- Help Button -->
      <button class="toolbar-btn help-btn" on:click={() => showHelp = true} title="Editor Help">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
      </button>
    </div>
  </div>

  <!-- Writing Area -->
  <div class="writing-area" class:split-view={viewMode === 'split'}>
    {#if currentFile}
      <!-- Editor Pane -->
      {#if viewMode === 'edit' || viewMode === 'split'}
        <div class="editor-pane" class:half={viewMode === 'split'}>
          <CodeMirrorEditor
            bind:this={editorRef}
            content={$editorContent}
            {fontSize}
            on:save={handleSave}
            on:change={handleChange}
            on:fontsize={handleFontSize}
          />
        </div>
      {/if}

      <!-- Preview Pane -->
      {#if viewMode === 'preview' || viewMode === 'split'}
        <div class="preview-pane" class:half={viewMode === 'split'}>
          <div class="preview-header">
            <span class="preview-label">Preview</span>
          </div>
          <div class="preview-content prose">
            {@html previewHtml}
          </div>
        </div>
      {/if}
    {:else}
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="12" y1="18" x2="12" y2="12"></line>
            <line x1="9" y1="15" x2="15" y2="15"></line>
          </svg>
        </div>
        <h3 class="empty-title">No file selected</h3>
        <p class="empty-hint">Open a file from the Binder to start writing</p>
        <div class="empty-shortcuts">
          <div class="shortcut">
            <kbd>Cmd</kbd> + <kbd>S</kbd>
            <span>Save</span>
          </div>
          <div class="shortcut">
            <kbd>Cmd</kbd> + <kbd>Z</kbd>
            <span>Undo</span>
          </div>
          <div class="shortcut">
            <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>
            <span>Toggle Preview</span>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Expand Button (bottom right corner) -->
  {#if currentFile}
    <button
      class="expand-btn"
      on:click={toggleExpand}
      title={isExpanded ? 'Exit fullscreen (Esc)' : 'Expand editor'}
    >
      {#if isExpanded}
        <!-- Collapse icon -->
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="4 14 10 14 10 20"></polyline>
          <polyline points="20 10 14 10 14 4"></polyline>
          <line x1="14" y1="10" x2="21" y2="3"></line>
          <line x1="3" y1="21" x2="10" y2="14"></line>
        </svg>
      {:else}
        <!-- Expand icon -->
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 3 21 3 21 9"></polyline>
          <polyline points="9 21 3 21 3 15"></polyline>
          <line x1="21" y1="3" x2="14" y2="10"></line>
          <line x1="3" y1="21" x2="10" y2="14"></line>
        </svg>
      {/if}
    </button>
  {/if}
</div>

<!-- Help Overlay -->
<EditorHelp bind:open={showHelp} />

<style>
  .editor-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary, #0f1419);
    position: relative;
  }

  /* Expanded/Fullscreen Mode */
  .editor-wrapper.expanded {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
    border-radius: 0;
  }

  /* Toolbar */
  .editor-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 36px;
    padding: 0 var(--space-3, 12px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
    flex-shrink: 0;
  }

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .toolbar-center {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
  }

  .file-icon {
    display: flex;
    align-items: center;
    color: var(--text-muted, #8b949e);
  }

  .filename {
    font-size: var(--text-sm, 13px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  .file-type {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
    background: var(--bg-tertiary, #252d38);
    padding: 2px 6px;
    border-radius: var(--radius-sm, 4px);
  }

  /* View Toggle */
  .view-toggle {
    display: flex;
    background: var(--bg-tertiary, #252d38);
    border-radius: var(--radius-md, 6px);
    padding: 2px;
    gap: 2px;
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 24px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .toggle-btn:hover {
    color: var(--text-secondary, #c9d1d9);
    background: var(--bg-secondary, #1a2027);
  }

  .toggle-btn.active {
    background: var(--bg-primary, #0f1419);
    color: var(--accent-cyan, #58a6ff);
  }

  /* Toolbar Separator */
  .toolbar-sep {
    width: 1px;
    height: 16px;
    background: var(--border, #2d3a47);
    margin: 0 var(--space-2, 8px);
  }

  /* Font Size Controls */
  .font-size-controls {
    display: flex;
    align-items: center;
    gap: 4px;
    background: var(--bg-tertiary, #252d38);
    border-radius: var(--radius-md, 6px);
    padding: 2px 4px;
  }

  .font-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .font-btn:hover:not(:disabled) {
    color: var(--text-secondary, #c9d1d9);
    background: var(--bg-secondary, #1a2027);
  }

  .font-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .font-size-label {
    font-size: var(--text-xs, 11px);
    font-family: var(--font-mono, 'SF Mono', monospace);
    color: var(--text-muted, #8b949e);
    min-width: 32px;
    text-align: center;
  }

  .toolbar-right {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .save-status {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
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

  .spinner {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .toolbar-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .toolbar-btn:hover:not(:disabled) {
    background: var(--bg-tertiary, #252d38);
    border-color: var(--border, #2d3a47);
    color: var(--text-primary, #e6edf3);
  }

  .toolbar-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .toolbar-btn.help-btn {
    color: var(--accent-gold, #d4a574);
  }

  .toolbar-btn.help-btn:hover {
    color: var(--accent-gold, #d4a574);
    background: rgba(212, 165, 116, 0.15);
    border-color: var(--accent-gold, #d4a574);
  }

  /* Writing Area */
  .writing-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
  }

  .writing-area.split-view {
    flex-direction: row;
  }

  /* Editor Pane */
  .editor-pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
  }

  .editor-pane.half {
    flex: 0 0 50%;
    border-right: 1px solid var(--border, #2d3a47);
  }

  /* Preview Pane */
  .preview-pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-primary, #0f1419);
  }

  .preview-pane.half {
    flex: 0 0 50%;
  }

  .preview-header {
    display: flex;
    align-items: center;
    height: 24px;
    padding: 0 12px;
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .preview-label {
    font-size: 10px;
    font-weight: 600;
    color: var(--text-muted, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .preview-content {
    flex: 1;
    overflow-y: auto;
    padding: 24px 32px;
    max-width: 800px;
    margin: 0 auto;
  }

  /* Prose Styling for Preview */
  .prose {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 18px;
    line-height: 1.8;
    color: var(--text-primary, #e6edf3);
  }

  .prose :global(h1) {
    font-size: 2em;
    font-weight: bold;
    color: var(--accent-gold, #d4a574);
    margin: 1.5em 0 0.5em 0;
    line-height: 1.3;
  }

  .prose :global(h2) {
    font-size: 1.5em;
    font-weight: bold;
    color: var(--accent-gold, #d4a574);
    margin: 1.5em 0 0.5em 0;
    line-height: 1.3;
  }

  .prose :global(h3) {
    font-size: 1.25em;
    font-weight: bold;
    color: var(--accent-gold, #d4a574);
    margin: 1.5em 0 0.5em 0;
    line-height: 1.3;
  }

  .prose :global(h4),
  .prose :global(h5),
  .prose :global(h6) {
    font-size: 1em;
    font-weight: bold;
    color: var(--accent-gold, #d4a574);
    margin: 1.5em 0 0.5em 0;
  }

  .prose :global(p) {
    margin: 0 0 1em 0;
  }

  .prose :global(strong) {
    font-weight: bold;
    color: var(--text-primary, #e6edf3);
  }

  .prose :global(em) {
    font-style: italic;
    color: var(--text-secondary, #c9d1d9);
  }

  .prose :global(a) {
    color: var(--accent-cyan, #58a6ff);
    text-decoration: underline;
  }

  .prose :global(a:hover) {
    color: var(--accent-cyan-hover, #79b8ff);
  }

  .prose :global(code) {
    font-family: 'SF Mono', 'Menlo', monospace;
    font-size: 0.9em;
    color: var(--accent-purple, #a371f7);
    background: var(--bg-tertiary, #252d38);
    padding: 2px 6px;
    border-radius: 4px;
  }

  .prose :global(pre) {
    font-family: 'SF Mono', 'Menlo', monospace;
    font-size: 0.85em;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    margin: 1em 0;
  }

  .prose :global(pre code) {
    background: transparent;
    padding: 0;
    color: var(--text-primary, #e6edf3);
  }

  .prose :global(blockquote) {
    border-left: 4px solid var(--accent-gold, #d4a574);
    margin: 1em 0;
    padding: 0.5em 0 0.5em 1em;
    color: var(--text-muted, #8b949e);
    font-style: italic;
  }

  .prose :global(ul),
  .prose :global(ol) {
    margin: 1em 0;
    padding-left: 2em;
  }

  .prose :global(li) {
    margin: 0.25em 0;
  }

  .prose :global(hr) {
    border: none;
    border-top: 1px solid var(--border, #2d3a47);
    margin: 2em 0;
  }

  .prose :global(img) {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 1em 0;
  }

  .prose :global(table) {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
  }

  .prose :global(th),
  .prose :global(td) {
    border: 1px solid var(--border, #2d3a47);
    padding: 8px 12px;
    text-align: left;
  }

  .prose :global(th) {
    background: var(--bg-secondary, #1a2027);
    font-weight: bold;
  }

  /* Preview Scrollbar */
  .preview-content::-webkit-scrollbar {
    width: 8px;
  }

  .preview-content::-webkit-scrollbar-track {
    background: transparent;
  }

  .preview-content::-webkit-scrollbar-thumb {
    background: var(--border, #2d3a47);
    border-radius: 4px;
  }

  .preview-content::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted, #8b949e);
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
    opacity: 0.3;
    margin-bottom: var(--space-4, 16px);
  }

  .empty-title {
    font-size: var(--text-xl, 20px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-secondary, #c9d1d9);
    margin: 0 0 var(--space-2, 8px) 0;
  }

  .empty-hint {
    font-size: var(--text-sm, 13px);
    color: var(--text-muted, #8b949e);
    margin: 0 0 var(--space-6, 24px) 0;
  }

  .empty-shortcuts {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
    padding: var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-lg, 8px);
    border: 1px solid var(--border, #2d3a47);
  }

  .shortcut {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  kbd {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 20px;
    padding: 2px 6px;
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    font-family: var(--font-mono, 'SF Mono', monospace);
    font-size: 10px;
    color: var(--text-secondary, #c9d1d9);
  }

  /* Expand Button */
  .expand-btn {
    position: absolute;
    bottom: 12px;
    right: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
    z-index: 10;
    opacity: 0.7;
  }

  .expand-btn:hover {
    opacity: 1;
    background: var(--bg-tertiary, #252d38);
    color: var(--text-primary, #e6edf3);
    border-color: var(--accent-cyan, #58a6ff);
  }

  .editor-wrapper.expanded .expand-btn {
    opacity: 1;
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
    border-color: var(--accent-cyan, #58a6ff);
  }

  .editor-wrapper.expanded .expand-btn:hover {
    background: var(--accent-cyan-hover, #79b8ff);
  }
</style>
