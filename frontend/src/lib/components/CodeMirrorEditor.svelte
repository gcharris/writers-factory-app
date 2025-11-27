<!--
  CodeMirrorEditor.svelte - Professional Prose Editor for Writers Factory

  A distraction-free writing environment built on CodeMirror 6:
  - Native Markdown editing (no conversion)
  - Serif font (Georgia) for comfortable prose reading
  - Subtle syntax highlighting for headings, bold, italic
  - Dark theme matching Cyber-Noir aesthetic
  - Word count, line count, cursor position
  - Keyboard shortcuts (Cmd/Ctrl+S to save)
  - Spell checking enabled
-->
<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { EditorState } from '@codemirror/state';
  import { EditorView, keymap, lineNumbers, highlightActiveLine, drawSelection, rectangularSelection, highlightActiveLineGutter } from '@codemirror/view';
  import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands';
  import { markdown, markdownLanguage } from '@codemirror/lang-markdown';
  import { syntaxHighlighting, HighlightStyle } from '@codemirror/language';
  import { tags } from '@lezer/highlight';

  const dispatch = createEventDispatcher();

  // Props
  export let content = '';
  export let readonly = false;

  // Internal state
  let editorContainer;
  let editorView;
  let wordCount = 0;
  let lineCount = 0;
  let cursorLine = 1;
  let cursorCol = 1;

  // ============================================
  // CUSTOM THEME - Cyber-Noir Prose
  // ============================================

  // Color palette matching Writers Factory
  const colors = {
    bg: '#0f1419',
    bgSecondary: '#1a2027',
    bgTertiary: '#252d38',
    text: '#e6edf3',
    textMuted: '#8b949e',
    textSecondary: '#c9d1d9',
    border: '#2d3a47',
    accentGold: '#d4a574',
    accentCyan: '#58a6ff',
    accentPurple: '#a371f7',
    accentGreen: '#3fb950',
    selection: 'rgba(88, 166, 255, 0.2)',
    activeLine: 'rgba(255, 255, 255, 0.03)',
  };

  // Editor theme (visual styling)
  const cyberNoirTheme = EditorView.theme({
    '&': {
      color: colors.text,
      backgroundColor: colors.bg,
      fontSize: '18px',
      fontFamily: "'Georgia', 'Times New Roman', serif",
    },
    '.cm-content': {
      caretColor: colors.accentCyan,
      padding: '24px 32px',
      lineHeight: '1.8',
      maxWidth: '800px',
      margin: '0 auto',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: colors.accentCyan,
      borderLeftWidth: '2px',
    },
    '.cm-selectionBackground, .cm-content ::selection': {
      backgroundColor: colors.selection,
    },
    '&.cm-focused .cm-selectionBackground': {
      backgroundColor: colors.selection,
    },
    '.cm-activeLine': {
      backgroundColor: colors.activeLine,
    },
    '.cm-activeLineGutter': {
      backgroundColor: colors.activeLine,
    },
    '.cm-gutters': {
      backgroundColor: colors.bgSecondary,
      color: colors.textMuted,
      border: 'none',
      borderRight: `1px solid ${colors.border}`,
      fontFamily: "'SF Mono', 'Menlo', monospace",
      fontSize: '12px',
    },
    '.cm-lineNumbers .cm-gutterElement': {
      padding: '0 12px 0 8px',
      minWidth: '40px',
    },
    '.cm-scroller': {
      overflow: 'auto',
    },
    // Scrollbar styling
    '.cm-scroller::-webkit-scrollbar': {
      width: '8px',
      height: '8px',
    },
    '.cm-scroller::-webkit-scrollbar-track': {
      background: 'transparent',
    },
    '.cm-scroller::-webkit-scrollbar-thumb': {
      background: colors.border,
      borderRadius: '4px',
    },
    '.cm-scroller::-webkit-scrollbar-thumb:hover': {
      background: colors.textMuted,
    },
    // Placeholder
    '.cm-placeholder': {
      color: colors.textMuted,
      fontStyle: 'italic',
    },
  }, { dark: true });

  // Syntax highlighting for Markdown prose
  const proseHighlighting = HighlightStyle.define([
    // Headings - Gold accent, slightly larger
    { tag: tags.heading1, color: colors.accentGold, fontWeight: 'bold', fontSize: '1.5em' },
    { tag: tags.heading2, color: colors.accentGold, fontWeight: 'bold', fontSize: '1.3em' },
    { tag: tags.heading3, color: colors.accentGold, fontWeight: 'bold', fontSize: '1.1em' },
    { tag: tags.heading4, color: colors.accentGold, fontWeight: 'bold' },
    { tag: tags.heading5, color: colors.accentGold, fontWeight: 'bold' },
    { tag: tags.heading6, color: colors.accentGold, fontWeight: 'bold' },

    // Emphasis
    { tag: tags.emphasis, fontStyle: 'italic', color: colors.textSecondary },
    { tag: tags.strong, fontWeight: 'bold', color: colors.text },
    { tag: tags.strikethrough, textDecoration: 'line-through', color: colors.textMuted },

    // Links - Cyan accent
    { tag: tags.link, color: colors.accentCyan, textDecoration: 'underline' },
    { tag: tags.url, color: colors.accentCyan },

    // Code - Purple accent with background
    { tag: tags.monospace, fontFamily: "'SF Mono', 'Menlo', monospace", color: colors.accentPurple, fontSize: '0.9em' },

    // Lists
    { tag: tags.list, color: colors.textSecondary },

    // Quotes - Muted italic
    { tag: tags.quote, fontStyle: 'italic', color: colors.textMuted },

    // Meta (frontmatter, etc)
    { tag: tags.meta, color: colors.textMuted },

    // Processing instructions (like HTML in MD)
    { tag: tags.processingInstruction, color: colors.textMuted },

    // Comments
    { tag: tags.comment, color: colors.textMuted, fontStyle: 'italic' },
  ]);

  // ============================================
  // EDITOR SETUP
  // ============================================

  function createEditor() {
    if (!editorContainer) return;

    const startState = EditorState.create({
      doc: content || '',
      extensions: [
        // Core functionality
        history(),
        drawSelection(),
        rectangularSelection(),
        highlightActiveLine(),
        highlightActiveLineGutter(),

        // Line numbers (optional - can be toggled)
        lineNumbers(),

        // Keymaps
        keymap.of([
          ...defaultKeymap,
          ...historyKeymap,
          indentWithTab,
          // Save shortcut
          {
            key: 'Mod-s',
            run: () => {
              dispatch('save', { content: editorView.state.doc.toString() });
              return true;
            },
          },
        ]),

        // Markdown language support
        markdown({ base: markdownLanguage }),

        // Syntax highlighting
        syntaxHighlighting(proseHighlighting),

        // Theme
        cyberNoirTheme,

        // Read-only mode
        EditorState.readOnly.of(readonly),

        // Update listener for content changes
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            const doc = update.state.doc;
            const text = doc.toString();

            // Update stats
            updateStats(text, update.state);

            // Dispatch change event
            dispatch('change', { content: text });
          }

          // Update cursor position
          if (update.selectionSet) {
            const pos = update.state.selection.main.head;
            const line = update.state.doc.lineAt(pos);
            cursorLine = line.number;
            cursorCol = pos - line.from + 1;
          }
        }),

        // Placeholder text
        EditorView.contentAttributes.of({
          spellcheck: 'true',
          autocapitalize: 'sentences',
        }),
      ],
    });

    editorView = new EditorView({
      state: startState,
      parent: editorContainer,
    });

    // Initial stats
    updateStats(content || '', startState);
  }

  function updateStats(text, state) {
    // Word count - split by whitespace, filter empty
    const words = text.trim().split(/\s+/).filter(w => w.length > 0);
    wordCount = words.length;

    // Line count
    lineCount = state.doc.lines;
  }

  // ============================================
  // LIFECYCLE & REACTIVITY
  // ============================================

  onMount(() => {
    createEditor();
  });

  onDestroy(() => {
    if (editorView) {
      editorView.destroy();
    }
  });

  // Update editor content when prop changes (e.g., loading a new file)
  $: if (editorView && content !== editorView.state.doc.toString()) {
    editorView.dispatch({
      changes: {
        from: 0,
        to: editorView.state.doc.length,
        insert: content || '',
      },
    });
  }

  // ============================================
  // PUBLIC API
  // ============================================

  // Get current content
  export function getContent() {
    return editorView ? editorView.state.doc.toString() : content;
  }

  // Focus the editor
  export function focus() {
    if (editorView) {
      editorView.focus();
    }
  }

  // Insert text at cursor
  export function insertAtCursor(text) {
    if (editorView) {
      const pos = editorView.state.selection.main.head;
      editorView.dispatch({
        changes: { from: pos, insert: text },
        selection: { anchor: pos + text.length },
      });
      editorView.focus();
    }
  }

  // Get stats
  export function getStats() {
    return { wordCount, lineCount, cursorLine, cursorCol };
  }
</script>

<div class="codemirror-wrapper">
  <div class="editor-container" bind:this={editorContainer}></div>

  <!-- Status bar -->
  <div class="status-bar">
    <div class="status-left">
      <span class="stat">Ln {cursorLine}, Col {cursorCol}</span>
    </div>
    <div class="status-right">
      <span class="stat">{wordCount.toLocaleString()} words</span>
      <span class="stat-divider">|</span>
      <span class="stat">{lineCount.toLocaleString()} lines</span>
    </div>
  </div>
</div>

<style>
  .codemirror-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary, #0f1419);
  }

  .editor-container {
    flex: 1;
    overflow: hidden;
  }

  /* Ensure CodeMirror fills the container */
  .editor-container :global(.cm-editor) {
    height: 100%;
  }

  .editor-container :global(.cm-scroller) {
    overflow: auto;
  }

  /* Status bar */
  .status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 24px;
    padding: 0 12px;
    background: var(--bg-secondary, #1a2027);
    border-top: 1px solid var(--border, #2d3a47);
    font-family: 'SF Mono', 'Menlo', monospace;
    font-size: 11px;
    color: var(--text-muted, #8b949e);
  }

  .status-left,
  .status-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .stat {
    color: var(--text-muted, #8b949e);
  }

  .stat-divider {
    color: var(--border, #2d3a47);
  }
</style>
