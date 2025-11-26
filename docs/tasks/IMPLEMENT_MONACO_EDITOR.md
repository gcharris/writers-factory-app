# Implement Monaco Editor for Prose Writing

**Task**: Replace plain textarea with Monaco Editor configured for prose/markdown
**Date**: 2025-11-26
**Priority**: High
**Estimated Effort**: 2-3 hours

## Problem Statement

The current Editor component uses a simple `<textarea>` (line 82-86 in `Editor.svelte`):

```svelte
<textarea
  bind:value={$editorContent}
  placeholder="Start writing..."
  spellcheck="true"
></textarea>
```

**This is inadequate for serious writing!**

Writers need:
- ✅ Markdown support with syntax highlighting
- ✅ Serif font for prose (Georgia, not monospace)
- ✅ Line numbers (optional toggle)
- ✅ Word wrap
- ✅ Distraction-free mode
- ✅ Preview toggle (optional)
- ✅ Professional editing features (find/replace, multi-cursor, etc.)

**We already have `@monaco-editor/react` installed** - we just need to use it!

## Background Research

According to previous agent discussions, Monaco Editor was chosen because:
- Powers VS Code - battle-tested
- Excellent markdown support
- Highly customizable (can make it look like a prose editor)
- Already installed in package.json
- Works well in Svelte with wrapper component

## Implementation Steps

### Step 1: Install Monaco for Svelte

We have `@monaco-editor/react` but need a Svelte wrapper or direct integration.

**Option A: Use React wrapper in Svelte** (quick)
```bash
# Already installed:
# @monaco-editor/react": "^4.7.0"
```

**Option B: Direct Monaco integration** (better for Svelte)
```bash
npm install monaco-editor
```

For this task, use **Option B** (direct integration) for better Svelte compatibility.

### Step 2: Create MonacoEditor Component

Create new file: `frontend/src/lib/components/MonacoEditor.svelte`

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import * as monaco from 'monaco-editor';
  import { editorContent } from '$lib/stores';

  export let language = 'markdown';
  export let theme = 'vs-dark';

  let editorContainer;
  let editor;

  onMount(() => {
    // Configure Monaco for prose writing
    editor = monaco.editor.create(editorContainer, {
      value: $editorContent || '',
      language: language,
      theme: theme,

      // Prose-friendly settings
      wordWrap: 'on',
      lineNumbers: 'on', // Can toggle off for distraction-free
      minimap: { enabled: false }, // No minimap for prose
      scrollBeyondLastLine: true,
      fontSize: 16,
      lineHeight: 28,
      fontFamily: "'Georgia', 'Times New Roman', serif",
      fontLigatures: false,

      // Editing enhancements
      suggestOnTriggerCharacters: false, // No autocomplete for prose
      quickSuggestions: false,
      parameterHints: { enabled: false },
      folding: false, // No code folding in prose
      glyphMargin: false,

      // Smooth scrolling
      smoothScrolling: true,
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: 'on',

      // Padding for comfortable writing
      padding: { top: 20, bottom: 20 },
    });

    // Sync Monaco content to store
    editor.onDidChangeModelContent(() => {
      editorContent.set(editor.getValue());
    });

    // Sync store changes to Monaco (e.g., when loading new file)
    const unsubscribe = editorContent.subscribe(value => {
      if (editor && value !== editor.getValue()) {
        editor.setValue(value);
      }
    });

    return () => {
      unsubscribe();
    };
  });

  onDestroy(() => {
    if (editor) {
      editor.dispose();
    }
  });

  // Public methods for parent component
  export function getValue() {
    return editor?.getValue() || '';
  }

  export function setValue(value) {
    if (editor) {
      editor.setValue(value);
    }
  }

  export function toggleLineNumbers() {
    if (editor) {
      const current = editor.getOption(monaco.editor.EditorOption.lineNumbers);
      editor.updateOptions({
        lineNumbers: current === 'on' ? 'off' : 'on'
      });
    }
  }

  export function toggleMinimap() {
    if (editor) {
      const current = editor.getOption(monaco.editor.EditorOption.minimap);
      editor.updateOptions({
        minimap: { enabled: !current.enabled }
      });
    }
  }

  export function focus() {
    editor?.focus();
  }
</script>

<div bind:this={editorContainer} class="monaco-container"></div>

<style>
  .monaco-container {
    width: 100%;
    height: 100%;
    min-height: 400px;
  }

  /* Override Monaco's default monospace with serif for prose */
  :global(.monaco-editor .view-line) {
    font-family: 'Georgia', 'Times New Roman', serif !important;
  }
</style>
```

### Step 3: Update Editor.svelte to Use Monaco

Replace the `<textarea>` section with Monaco:

```svelte
<script>
  import { editorContent, activeFile, isSaving } from '$lib/stores';
  import MonacoEditor from './MonacoEditor.svelte';

  let monacoEditor; // Reference to Monaco component
  let currentFile = "";
  let lastSaved = "";
  let saveError = "";

  // Preview mode toggle
  let showPreview = false;
  let renderedMarkdown = "";

  $: currentFile = $activeFile;

  // Render markdown preview (optional)
  $: if (showPreview) {
    renderedMarkdown = renderMarkdown($editorContent);
  }

  function renderMarkdown(text) {
    // Simple markdown rendering (or use a library like 'marked')
    // For now, just return as-is; TODO: implement proper markdown rendering
    return text;
  }

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

  function togglePreview() {
    showPreview = !showPreview;
  }

  function toggleDistractionFree() {
    monacoEditor?.toggleLineNumbers();
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
    <div class="toolbar-center">
      <!-- Preview toggle -->
      <button
        class="toolbar-btn"
        on:click={togglePreview}
        class:active={showPreview}
        title="Toggle markdown preview"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
          <circle cx="12" cy="12" r="3"></circle>
        </svg>
        Preview
      </button>

      <!-- Distraction-free mode -->
      <button
        class="toolbar-btn"
        on:click={toggleDistractionFree}
        title="Toggle line numbers"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="8" y1="6" x2="21" y2="6"></line>
          <line x1="8" y1="12" x2="21" y2="12"></line>
          <line x1="8" y1="18" x2="21" y2="18"></line>
          <line x1="3" y1="6" x2="3.01" y2="6"></line>
          <line x1="3" y1="12" x2="3.01" y2="12"></line>
          <line x1="3" y1="18" x2="3.01" y2="18"></line>
        </svg>
      </button>
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
      {#if showPreview}
        <!-- Split view: Editor + Preview -->
        <div class="split-view">
          <div class="editor-pane">
            <MonacoEditor bind:this={monacoEditor} />
          </div>
          <div class="preview-pane">
            <div class="markdown-preview">
              {@html renderedMarkdown}
            </div>
          </div>
        </div>
      {:else}
        <!-- Full-width editor -->
        <MonacoEditor bind:this={monacoEditor} />
      {/if}
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
  /* Keep existing styles */
  .editor-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary);
  }

  .editor-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
  }

  .toolbar-center {
    display: flex;
    gap: var(--space-1);
  }

  .toolbar-btn {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: 4px var(--space-2);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: var(--text-xs);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .toolbar-btn:hover {
    background: var(--bg-elevated);
    border-color: var(--border-strong);
    color: var(--text-secondary);
  }

  .toolbar-btn.active {
    background: var(--accent-cyan);
    border-color: var(--accent-cyan);
    color: var(--bg-primary);
  }

  .writing-area {
    flex: 1;
    display: flex;
    min-height: 0;
    overflow: hidden;
  }

  .split-view {
    display: flex;
    width: 100%;
    gap: 1px;
    background: var(--border);
  }

  .editor-pane,
  .preview-pane {
    flex: 1;
    background: var(--bg-primary);
  }

  .markdown-preview {
    padding: var(--space-4);
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 16px;
    line-height: 1.8;
    color: var(--text-primary);
  }

  /* Existing styles for word count, save status, etc. */
  /* ... keep all the existing CSS ... */
</style>
```

### Step 4: Configure Monaco Workers

Monaco needs web workers for syntax highlighting. Add to `vite.config.js`:

```javascript
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],

  optimizeDeps: {
    include: ['monaco-editor']
  },

  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          monaco: ['monaco-editor']
        }
      }
    }
  },

  // Monaco worker configuration
  worker: {
    format: 'es'
  }
});
```

### Step 5: Optional - Add Markdown Rendering

For preview mode, install a markdown renderer:

```bash
npm install marked
```

Then update the `renderMarkdown` function:

```javascript
import { marked } from 'marked';

function renderMarkdown(text) {
  try {
    return marked.parse(text);
  } catch (e) {
    console.error('Markdown rendering error:', e);
    return text;
  }
}
```

## Configuration Options

### Prose-Friendly Monaco Settings

```javascript
{
  // Typography
  fontFamily: "'Georgia', 'Times New Roman', serif",
  fontSize: 16,
  lineHeight: 28,
  fontLigatures: false,

  // Layout
  wordWrap: 'on',
  lineNumbers: 'on', // or 'off' for distraction-free
  minimap: { enabled: false },
  scrollBeyondLastLine: true,
  padding: { top: 20, bottom: 20 },

  // Disable code-centric features
  suggestOnTriggerCharacters: false,
  quickSuggestions: false,
  parameterHints: { enabled: false },
  folding: false,
  glyphMargin: false,

  // Smooth UX
  smoothScrolling: true,
  cursorBlinking: 'smooth',
  cursorSmoothCaretAnimation: 'on',

  // Theme
  theme: 'vs-dark', // Or create custom theme
}
```

### Custom Dark Theme (Optional)

```javascript
monaco.editor.defineTheme('prose-dark', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'emphasis', fontStyle: 'italic' },
    { token: 'strong', fontStyle: 'bold' },
    { token: 'header', foreground: 'd4a574', fontStyle: 'bold' },
  ],
  colors: {
    'editor.background': '#0f1419',
    'editor.foreground': '#c9d1d9',
    'editor.lineHighlightBackground': '#1a2027',
    'editorCursor.foreground': '#58a6ff',
  }
});
```

## Testing Checklist

After implementation, verify:

- [ ] **Monaco loads** - Editor renders without errors
- [ ] **File content loads** - Clicking file in Binder loads in Monaco
- [ ] **Typing works** - Can write and edit text
- [ ] **Save works** - Cmd/Ctrl+S saves file
- [ ] **Markdown highlighting** - Headers, bold, italic, etc. are colored
- [ ] **Word wrap** - Long lines wrap instead of scroll
- [ ] **Serif font** - Text uses Georgia, not monospace
- [ ] **No minimap** - Code minimap is disabled
- [ ] **Preview toggle** - Button shows/hides markdown preview
- [ ] **Line numbers toggle** - Can hide line numbers for distraction-free mode
- [ ] **Word count** - Updates as you type
- [ ] **Performance** - Smooth typing, no lag
- [ ] **Dark theme** - Matches app's cyber-noir aesthetic

## Files to Create/Modify

1. **NEW**: `frontend/src/lib/components/MonacoEditor.svelte`
2. **MODIFY**: `frontend/src/lib/components/Editor.svelte`
3. **MODIFY**: `frontend/vite.config.js` (Monaco workers)
4. **INSTALL**: `monaco-editor`, optionally `marked`

## Common Issues & Solutions

### Issue 1: Monaco workers not loading
**Solution**: Ensure `vite.config.js` has worker configuration

### Issue 2: Monospace font instead of serif
**Solution**: Add CSS override in MonacoEditor.svelte styles

### Issue 3: Monaco too complex for prose
**Solution**: Disable all code-centric features in config (see settings above)

### Issue 4: Preview not rendering markdown
**Solution**: Install `marked` library and implement `renderMarkdown()`

## Future Enhancements (Not in this task)

- Spell check integration
- Thesaurus/dictionary lookup
- Focus mode (hide all UI except editor)
- Typewriter scrolling
- Reading time estimate
- Export to PDF/DOCX

## Reference

- Monaco Editor docs: https://microsoft.github.io/monaco-editor/
- Monaco in Svelte example: https://github.com/microsoft/monaco-editor/issues/2481
- Prose editor inspiration: iA Writer, Ulysses, Scrivener

The goal: **Professional writing experience** that feels like a dedicated prose editor, not a code editor.
