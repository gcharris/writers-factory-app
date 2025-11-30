<!--
  EditorHelp.svelte - Editor Quick Reference Guide

  A help overlay showing keyboard shortcuts and features
  for first-time users of the Writers Factory editor.
-->
<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  export let open = false;

  function close() {
    open = false;
    dispatch('close');
  }

  // Close on escape
  function handleKeydown(e) {
    if (e.key === 'Escape' && open) {
      e.preventDefault();
      close();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
  <div class="help-overlay" on:click={close} on:keydown={() => {}} role="button" tabindex="-1">
    <div class="help-modal" on:click|stopPropagation on:keydown={() => {}} role="dialog" aria-modal="true">
      <div class="help-header">
        <h2>Editor Quick Reference</h2>
        <button class="close-btn" on:click={close} title="Close (Esc)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="help-content">
        <!-- View Modes Section -->
        <section class="help-section">
          <h3>
            <span class="section-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="12" y1="3" x2="12" y2="21"></line>
              </svg>
            </span>
            View Modes
          </h3>
          <p class="section-desc">Switch between editing and preview modes using the toolbar buttons.</p>
          <div class="feature-list">
            <div class="feature">
              <span class="feature-icon edit-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 20h9"></path>
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                </svg>
              </span>
              <div class="feature-info">
                <strong>Edit Mode</strong>
                <span>Full-screen Markdown editor with syntax highlighting</span>
              </div>
            </div>
            <div class="feature">
              <span class="feature-icon split-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="12" y1="3" x2="12" y2="21"></line>
                </svg>
              </span>
              <div class="feature-info">
                <strong>Split View</strong>
                <span>Side-by-side editor and live preview</span>
              </div>
            </div>
            <div class="feature">
              <span class="feature-icon preview-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </span>
              <div class="feature-info">
                <strong>Preview Mode</strong>
                <span>Rendered Markdown with full prose styling</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Font Size Section -->
        <section class="help-section">
          <h3>
            <span class="section-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="4 7 4 4 20 4 20 7"></polyline>
                <line x1="9" y1="20" x2="15" y2="20"></line>
                <line x1="12" y1="4" x2="12" y2="20"></line>
              </svg>
            </span>
            Font Size
          </h3>
          <p class="section-desc">Adjust text size for comfortable reading and writing.</p>
          <div class="control-demo">
            <div class="font-controls-demo">
              <span class="demo-btn">−</span>
              <span class="demo-label">18px</span>
              <span class="demo-btn">+</span>
            </div>
            <span class="demo-hint">Range: 14px to 24px</span>
          </div>
        </section>

        <!-- Fullscreen Section -->
        <section class="help-section">
          <h3>
            <span class="section-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 3 21 3 21 9"></polyline>
                <polyline points="9 21 3 21 3 15"></polyline>
                <line x1="21" y1="3" x2="14" y2="10"></line>
                <line x1="3" y1="21" x2="10" y2="14"></line>
              </svg>
            </span>
            Fullscreen Mode
          </h3>
          <p class="section-desc">Expand the editor to fill your entire screen for distraction-free writing.</p>
          <div class="feature-list">
            <div class="feature">
              <span class="feature-icon expand-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="15 3 21 3 21 9"></polyline>
                  <polyline points="9 21 3 21 3 15"></polyline>
                  <line x1="21" y1="3" x2="14" y2="10"></line>
                  <line x1="3" y1="21" x2="10" y2="14"></line>
                </svg>
              </span>
              <div class="feature-info">
                <strong>Expand Button</strong>
                <span>Click the button in the bottom-right corner</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Keyboard Shortcuts Section -->
        <section class="help-section shortcuts-section">
          <h3>
            <span class="section-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="4" width="20" height="16" rx="2" ry="2"></rect>
                <path d="M6 8h.001"></path>
                <path d="M10 8h.001"></path>
                <path d="M14 8h.001"></path>
                <path d="M18 8h.001"></path>
                <path d="M8 12h.001"></path>
                <path d="M12 12h.001"></path>
                <path d="M16 12h.001"></path>
                <path d="M7 16h10"></path>
              </svg>
            </span>
            Keyboard Shortcuts
          </h3>

          <!-- Formatting Shortcuts -->
          <h4 class="shortcut-category">Formatting</h4>
          <div class="shortcuts-grid">
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>B</kbd>
              </div>
              <span class="shortcut-desc">Bold</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>I</kbd>
              </div>
              <span class="shortcut-desc">Italic</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>⇧</kbd><span class="key-sep">+</span><kbd>X</kbd>
              </div>
              <span class="shortcut-desc">Strikethrough</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>⇧</kbd><span class="key-sep">+</span><kbd>K</kbd>
              </div>
              <span class="shortcut-desc">Inline code</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>⇧</kbd><span class="key-sep">+</span><kbd>Q</kbd>
              </div>
              <span class="shortcut-desc">Blockquote</span>
            </div>
          </div>

          <!-- Heading Shortcuts -->
          <h4 class="shortcut-category">Headings</h4>
          <div class="shortcuts-grid">
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>1</kbd>
              </div>
              <span class="shortcut-desc">Heading 1</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>2</kbd>
              </div>
              <span class="shortcut-desc">Heading 2</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>3</kbd>
              </div>
              <span class="shortcut-desc">Heading 3</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>0</kbd>
              </div>
              <span class="shortcut-desc">Normal text</span>
            </div>
          </div>

          <!-- General Shortcuts -->
          <h4 class="shortcut-category">General</h4>
          <div class="shortcuts-grid">
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>S</kbd>
              </div>
              <span class="shortcut-desc">Save file</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>Z</kbd>
              </div>
              <span class="shortcut-desc">Undo</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>⇧</kbd><span class="key-sep">+</span><kbd>Z</kbd>
              </div>
              <span class="shortcut-desc">Redo</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>⇧</kbd><span class="key-sep">+</span><kbd>P</kbd>
              </div>
              <span class="shortcut-desc">Cycle view modes</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>=</kbd>
              </div>
              <span class="shortcut-desc">Increase font size</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>⌘</kbd><span class="key-sep">+</span><kbd>-</kbd>
              </div>
              <span class="shortcut-desc">Decrease font size</span>
            </div>
            <div class="shortcut-item">
              <div class="keys">
                <kbd>Esc</kbd>
              </div>
              <span class="shortcut-desc">Exit fullscreen</span>
            </div>
          </div>
          <p class="platform-note">On Windows/Linux, use <kbd>Ctrl</kbd> instead of <kbd>⌘</kbd></p>
        </section>

        <!-- Markdown Tips Section -->
        <section class="help-section">
          <h3>
            <span class="section-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </span>
            Markdown Quick Reference
          </h3>
          <div class="markdown-examples">
            <div class="md-example">
              <code># Heading 1</code>
              <span class="md-result">Chapter title</span>
            </div>
            <div class="md-example">
              <code>## Heading 2</code>
              <span class="md-result">Section title</span>
            </div>
            <div class="md-example">
              <code>**bold text**</code>
              <span class="md-result"><strong>bold text</strong></span>
            </div>
            <div class="md-example">
              <code>*italic text*</code>
              <span class="md-result"><em>italic text</em></span>
            </div>
            <div class="md-example">
              <code>> Quote text</code>
              <span class="md-result">Blockquote</span>
            </div>
            <div class="md-example">
              <code>---</code>
              <span class="md-result">Horizontal rule (scene break)</span>
            </div>
          </div>
        </section>
      </div>

      <div class="help-footer">
        <span class="footer-tip">Press <kbd>Esc</kbd> or click outside to close</span>
      </div>
    </div>
  </div>
{/if}

<style>
  .help-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    backdrop-filter: blur(4px);
  }

  .help-modal {
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 12px);
    width: 90%;
    max-width: 600px;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  }

  .help-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px) var(--space-5, 20px);
    border-bottom: 1px solid var(--border, #2d3a47);
    flex-shrink: 0;
  }

  .help-header h2 {
    margin: 0;
    font-size: var(--text-lg, 18px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: transparent;
    border: none;
    border-radius: var(--radius-md, 6px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .close-btn:hover {
    background: var(--bg-tertiary, #252d38);
    color: var(--text-primary, #e6edf3);
  }

  .help-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px) var(--space-5, 20px);
  }

  .help-section {
    margin-bottom: var(--space-5, 20px);
  }

  .help-section:last-child {
    margin-bottom: 0;
  }

  .help-section h3 {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-sm, 13px);
    font-weight: var(--font-semibold, 600);
    color: var(--accent-gold, #d4a574);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .section-icon {
    display: flex;
    align-items: center;
    color: var(--accent-gold, #d4a574);
  }

  .section-desc {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-sm, 13px);
    color: var(--text-muted, #8b949e);
    line-height: 1.5;
  }

  .feature-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .feature {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-md, 6px);
  }

  .feature-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: var(--bg-tertiary, #252d38);
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #8b949e);
    flex-shrink: 0;
  }

  .feature-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .feature-info strong {
    font-size: var(--text-sm, 13px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .feature-info span {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  /* Font Size Demo */
  .control-demo {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-md, 6px);
  }

  .font-controls-demo {
    display: flex;
    align-items: center;
    gap: 4px;
    background: var(--bg-tertiary, #252d38);
    border-radius: var(--radius-md, 6px);
    padding: 4px 6px;
  }

  .demo-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #8b949e);
    font-size: 14px;
    font-weight: bold;
  }

  .demo-label {
    font-size: var(--text-xs, 11px);
    font-family: var(--font-mono, 'SF Mono', monospace);
    color: var(--text-muted, #8b949e);
    min-width: 32px;
    text-align: center;
  }

  .demo-hint {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  /* Shortcuts Grid */
  .shortcuts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-2, 8px);
  }

  .shortcut-category {
    font-size: var(--text-xs, 11px);
    font-weight: 600;
    color: var(--text-muted, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: var(--space-3, 12px) 0 var(--space-2, 8px) 0;
  }

  .shortcut-category:first-of-type {
    margin-top: 0;
  }

  .shortcut-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-md, 6px);
  }

  .keys {
    display: flex;
    align-items: center;
    gap: 2px;
  }

  .key-sep {
    color: var(--text-muted, #8b949e);
    font-size: 10px;
    margin: 0 2px;
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
    font-size: 11px;
    color: var(--text-secondary, #c9d1d9);
  }

  .shortcut-desc {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  .platform-note {
    margin: var(--space-3, 12px) 0 0 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
    text-align: center;
  }

  .platform-note kbd {
    font-size: 10px;
    padding: 1px 4px;
  }

  /* Markdown Examples */
  .markdown-examples {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-2, 8px);
  }

  .md-example {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-md, 6px);
  }

  .md-example code {
    font-family: var(--font-mono, 'SF Mono', monospace);
    font-size: var(--text-xs, 11px);
    color: var(--accent-purple, #a371f7);
  }

  .md-result {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  .md-result strong {
    font-weight: bold;
    color: var(--text-primary, #e6edf3);
  }

  .md-result em {
    font-style: italic;
    color: var(--text-secondary, #c9d1d9);
  }

  /* Footer */
  .help-footer {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-3, 12px) var(--space-5, 20px);
    border-top: 1px solid var(--border, #2d3a47);
    flex-shrink: 0;
  }

  .footer-tip {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  .footer-tip kbd {
    font-size: 10px;
    padding: 1px 4px;
  }

  /* Scrollbar */
  .help-content::-webkit-scrollbar {
    width: 8px;
  }

  .help-content::-webkit-scrollbar-track {
    background: transparent;
  }

  .help-content::-webkit-scrollbar-thumb {
    background: var(--border, #2d3a47);
    border-radius: 4px;
  }

  .help-content::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted, #8b949e);
  }

  /* Responsive */
  @media (max-width: 600px) {
    .shortcuts-grid,
    .markdown-examples {
      grid-template-columns: 1fr;
    }
  }
</style>
