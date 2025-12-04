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

  // Format menu state
  let showFormatMenu = false;
  let showHeadingSubmenu = false;
  let formatMenuRef;

  // Selection popup state
  let showSelectionPopup = false;
  let selectionPopupPos = { x: 0, y: 0 };
  let selectedText = '';

  $: currentFile = $activeFile;

  // Close format menu when clicking outside
  function handleClickOutside(event) {
    if (formatMenuRef && !formatMenuRef.contains(event.target)) {
      showFormatMenu = false;
      showHeadingSubmenu = false;
    }
    // Don't hide selection popup here - let the selection event handle it
    // The popup should stay visible as long as there's a selection
  }

  // Handle mousedown to hide popup when clicking outside both popup AND editor
  function handleMouseDown(event) {
    // If clicking inside the selection popup, don't hide it
    if (event.target.closest('.selection-popup')) {
      return;
    }
    // If clicking inside the editor, don't hide - selection event will handle it
    if (event.target.closest('.editor-pane')) {
      return;
    }
    // Clicking outside both - hide the popup
    showSelectionPopup = false;
  }

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

      // Note: Don't use encodeURIComponent on full path - FastAPI's {filepath:path}
      // expects slashes to be preserved
      const response = await fetch(`http://localhost:8000/files/${currentFile}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Backend failed to save file');
      }

      lastSaved = new Date().toLocaleTimeString();
      // Update store with saved content
      editorContent.set(content);
    } catch (e) {
      saveError = e.message;
      console.error('Editor: Error saving file:', e);
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
    // Toggle behavior: clicking same mode returns to 'edit'
    if (viewMode === mode) {
      viewMode = 'edit';
    } else {
      viewMode = mode;
    }
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
  // FORMAT MENU ACTIONS
  // ============================================

  function toggleFormatMenu() {
    showFormatMenu = !showFormatMenu;
    if (!showFormatMenu) {
      showHeadingSubmenu = false;
    }
  }

  function applyHeading(level) {
    if (editorRef) {
      editorRef.applyHeading(level);
    }
    showFormatMenu = false;
    showHeadingSubmenu = false;
  }

  function applyBold() {
    if (editorRef) {
      editorRef.applyBold();
    }
    showFormatMenu = false;
  }

  function applyItalic() {
    if (editorRef) {
      editorRef.applyItalic();
    }
    showFormatMenu = false;
  }

  function applyStrikethrough() {
    if (editorRef) {
      editorRef.applyStrikethrough();
    }
    showFormatMenu = false;
  }

  function applyCode() {
    if (editorRef) {
      editorRef.applyCode();
    }
    showFormatMenu = false;
  }

  function applyQuote() {
    if (editorRef) {
      editorRef.applyQuote();
    }
    showFormatMenu = false;
  }

  function applyBulletList() {
    if (editorRef) {
      editorRef.applyBulletList();
    }
    showFormatMenu = false;
  }

  function applyNumberedList() {
    if (editorRef) {
      editorRef.applyNumberedList();
    }
    showFormatMenu = false;
  }

  function insertHorizontalRule() {
    if (editorRef) {
      editorRef.insertHorizontalRule();
    }
    showFormatMenu = false;
  }

  // ============================================
  // SELECTION POPUP & COPY TO CHAT
  // ============================================

  function handleEditorSelection(event) {
    // Check property exists (not truthiness - empty string '' is falsy!)
    if (event.detail && 'selectedText' in event.detail) {
      selectedText = event.detail.selectedText;
      if (selectedText && selectedText.length > 0) {
        // Position popup near selection
        selectionPopupPos = { x: event.detail.x || 100, y: event.detail.y || 100 };
        showSelectionPopup = true;
      } else {
        showSelectionPopup = false;
      }
    }
  }

  function copyToClipboard() {
    if (selectedText) {
      navigator.clipboard.writeText(selectedText);
    }
    showSelectionPopup = false;
  }

  function copyToChat() {
    if (selectedText) {
      // Dispatch event to parent to insert into Foreman chat
      dispatch('copyToChat', { text: selectedText });
    }
    showSelectionPopup = false;
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

<svelte:window on:keydown={handleKeydown} on:click={handleClickOutside} on:mousedown={handleMouseDown} />

<div class="editor-wrapper" class:expanded={isExpanded}>
  <!-- Editor Toolbar -->
  <div class="editor-toolbar">
    <div class="toolbar-left">
      {#if currentFile && currentFile.endsWith('.md')}
        <!-- View Mode Toggle (eye=preview, split=side-by-side) -->
        <div class="view-toggle">
          <button
            class="toggle-btn"
            class:active={viewMode === 'preview'}
            on:click={() => setViewMode('preview')}
            title="Toggle preview (click again to return to edit)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
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
        </div>
        <span class="file-type" class:preview-mode={viewMode === 'preview'}>{viewMode === 'preview' ? 'PREVIEW' : 'MARKDOWN'}</span>
      {/if}
    </div>

    <div class="toolbar-center">
      {#if currentFile && currentFile.endsWith('.md') && viewMode !== 'preview'}
        <!-- Heading Dropdown -->
        <div class="format-dropdown" bind:this={formatMenuRef}>
          <button
            class="format-btn heading-btn"
            on:click={() => showHeadingSubmenu = !showHeadingSubmenu}
            title="Paragraph style"
          >
            <span class="heading-label">P</span>
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
          {#if showHeadingSubmenu}
            <div class="dropdown-menu heading-menu">
              <button class="dropdown-item" on:click={() => applyHeading(0)}>
                <span class="item-label">Normal Text</span>
                <span class="item-shortcut">⌘0</span>
              </button>
              <button class="dropdown-item" on:click={() => applyHeading(1)}>
                <span class="item-label heading-1">Heading 1</span>
                <span class="item-shortcut">⌘1</span>
              </button>
              <button class="dropdown-item" on:click={() => applyHeading(2)}>
                <span class="item-label heading-2">Heading 2</span>
                <span class="item-shortcut">⌘2</span>
              </button>
              <button class="dropdown-item" on:click={() => applyHeading(3)}>
                <span class="item-label heading-3">Heading 3</span>
                <span class="item-shortcut">⌘3</span>
              </button>
            </div>
          {/if}
        </div>

        <!-- Separator -->
        <span class="toolbar-sep"></span>

        <!-- Inline Formatting Buttons -->
        <button class="format-btn" on:click={applyBold} title="Bold (⌘B)">
          <strong>B</strong>
        </button>
        <button class="format-btn italic-btn" on:click={applyItalic} title="Italic (⌘I)">
          <em>I</em>
        </button>
        <button class="format-btn" on:click={applyStrikethrough} title="Strikethrough (⌘⇧X)">
          <span style="text-decoration: line-through">S</span>
        </button>
        <button class="format-btn code-btn" on:click={applyCode} title="Inline Code (⌘⇧K)">
          <code>&lt;/&gt;</code>
        </button>

        <!-- Separator -->
        <span class="toolbar-sep"></span>

        <!-- Block Formatting Buttons -->
        <button class="format-btn" on:click={applyQuote} title="Blockquote (⌘⇧Q)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"></path>
            <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"></path>
          </svg>
        </button>
        <button class="format-btn" on:click={applyBulletList} title="Bullet List">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="8" y1="6" x2="21" y2="6"></line>
            <line x1="8" y1="12" x2="21" y2="12"></line>
            <line x1="8" y1="18" x2="21" y2="18"></line>
            <circle cx="3" cy="6" r="1" fill="currentColor"></circle>
            <circle cx="3" cy="12" r="1" fill="currentColor"></circle>
            <circle cx="3" cy="18" r="1" fill="currentColor"></circle>
          </svg>
        </button>
        <button class="format-btn" on:click={applyNumberedList} title="Numbered List">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="10" y1="6" x2="21" y2="6"></line>
            <line x1="10" y1="12" x2="21" y2="12"></line>
            <line x1="10" y1="18" x2="21" y2="18"></line>
            <text x="2" y="8" font-size="8" fill="currentColor">1</text>
            <text x="2" y="14" font-size="8" fill="currentColor">2</text>
            <text x="2" y="20" font-size="8" fill="currentColor">3</text>
          </svg>
        </button>
        <button class="format-btn" on:click={insertHorizontalRule} title="Horizontal Rule">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="12" x2="21" y2="12"></line>
          </svg>
        </button>

        <!-- Separator -->
        <span class="toolbar-sep"></span>

        <!-- Font Size Controls (compact) -->
        <div class="font-size-controls">
          <button
            class="font-btn"
            on:click={decreaseFontSize}
            disabled={fontSize <= MIN_FONT_SIZE}
            title="Decrease font size (Cmd+-)"
          >
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>
          <span class="font-size-label" title="Font size">{fontSize}</span>
          <button
            class="font-btn"
            on:click={increaseFontSize}
            disabled={fontSize >= MAX_FONT_SIZE}
            title="Increase font size (Cmd++)"
          >
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
            on:selection={handleEditorSelection}
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

</div>

<!-- Selection Popup -->
{#if showSelectionPopup && selectedText}
  <div
    class="selection-popup"
    style="left: {selectionPopupPos.x}px; top: {selectionPopupPos.y - 40}px;"
    on:mousedown|stopPropagation
  >
    <button class="popup-btn" on:click|stopPropagation={applyBold} title="Bold">
      <strong>B</strong>
    </button>
    <button class="popup-btn italic" on:click|stopPropagation={applyItalic} title="Italic">
      <em>I</em>
    </button>
    <span class="popup-sep"></span>
    <button class="popup-btn" on:click|stopPropagation={copyToClipboard} title="Copy">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
    </button>
    <button class="popup-btn chat-btn" on:click|stopPropagation={copyToChat} title="Copy to Chat">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
      <span>Chat</span>
    </button>
  </div>
{/if}

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

  .file-type {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
    background: var(--bg-tertiary, #252d38);
    padding: 2px 6px;
    border-radius: var(--radius-sm, 4px);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
  }

  .file-type.preview-mode {
    color: var(--accent-cyan, #58a6ff);
    background: rgba(88, 166, 255, 0.15);
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
    min-width: 20px;
    text-align: center;
  }

  /* Format Buttons */
  .format-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 26px;
    height: 26px;
    padding: 0 4px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
    font-size: 13px;
    font-weight: 600;
  }

  .format-btn:hover {
    color: var(--text-primary, #e6edf3);
    background: var(--bg-tertiary, #252d38);
  }

  .format-btn strong {
    font-weight: 700;
  }

  .format-btn em {
    font-style: italic;
    font-family: Georgia, 'Times New Roman', serif;
  }

  .format-btn.code-btn {
    font-family: var(--font-mono, 'SF Mono', monospace);
    font-size: 10px;
    font-weight: 500;
  }

  .format-btn.code-btn code {
    background: transparent;
    padding: 0;
    color: inherit;
  }

  .format-btn.heading-btn {
    gap: 2px;
  }

  .heading-label {
    font-weight: 600;
  }

  /* Format Dropdown */
  .format-dropdown {
    position: relative;
  }

  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    margin-top: 4px;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    padding: 4px;
    min-width: 160px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    z-index: 100;
  }

  .dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 6px 10px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-secondary, #c9d1d9);
    cursor: pointer;
    transition: all 0.15s ease;
    text-align: left;
  }

  .dropdown-item:hover {
    background: var(--bg-tertiary, #252d38);
    color: var(--text-primary, #e6edf3);
  }

  .item-label {
    font-size: 13px;
  }

  .item-label.heading-1 {
    font-size: 16px;
    font-weight: 700;
    color: var(--accent-gold, #d4a574);
  }

  .item-label.heading-2 {
    font-size: 14px;
    font-weight: 600;
    color: var(--accent-gold, #d4a574);
  }

  .item-label.heading-3 {
    font-size: 13px;
    font-weight: 600;
    color: var(--accent-gold, #d4a574);
  }

  .item-shortcut {
    font-size: 11px;
    font-family: var(--font-mono, 'SF Mono', monospace);
    color: var(--text-muted, #8b949e);
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

  /* Selection Popup */
  .selection-popup {
    position: fixed;
    display: flex;
    align-items: center;
    gap: 2px;
    padding: 4px;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    z-index: 200;
  }

  .popup-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    min-width: 28px;
    height: 28px;
    padding: 0 6px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
    font-size: 13px;
    font-weight: 600;
  }

  .popup-btn:hover {
    color: var(--text-primary, #e6edf3);
    background: var(--bg-tertiary, #252d38);
  }

  .popup-btn strong {
    font-weight: 700;
  }

  .popup-btn.italic em {
    font-style: italic;
    font-family: Georgia, 'Times New Roman', serif;
  }

  .popup-btn.chat-btn {
    color: var(--accent-cyan, #58a6ff);
  }

  .popup-btn.chat-btn span {
    font-size: 11px;
    font-weight: 500;
  }

  .popup-btn.chat-btn:hover {
    color: var(--accent-cyan, #58a6ff);
    background: rgba(88, 166, 255, 0.15);
  }

  .popup-sep {
    width: 1px;
    height: 16px;
    background: var(--border, #2d3a47);
    margin: 0 4px;
  }
</style>
