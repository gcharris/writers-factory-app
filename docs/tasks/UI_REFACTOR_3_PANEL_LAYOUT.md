# UI Refactor: 3-Panel Layout with Enhanced Chat UX

**Task for Claude Cloud**
**Date**: 2025-11-26
**Priority**: High
**Estimated Effort**: 2-3 hours

## Executive Summary

Transform the Writers Factory UI from a 4-panel layout to a 3-panel layout, making The Foreman (AI agent) the primary interface on the right side. This follows the Cursor AI / IDE pattern where the AI chat panel is prominent and tools are accessed through compact menus rather than dedicated panels.

## Problem Statement

### Current Issues
1. **Studio Panel wastes valuable space** (280px) with large tool cards
2. **Tools are accessed 2-3 times per session** - don't warrant permanent UI
3. **The Foreman is squeezed** - should be the star of the interface
4. **Missing critical chat UX features** - copy, insert to editor, regenerate
5. **Branding inconsistency** - "Antigravity" instead of "Writers Factory"

### Current Layout (4 panels)
```
┌────────────┬─────────────────┬──────────────────┬───────────────┐
│  BINDER    │     CANVAS      │   THE FOREMAN    │   STUDIO      │
│  (240px)   │  (flex)         │     (320px)      │   (280px)     │
│            │                 │                  │               │
│  FileTree  │  Monaco Editor  │  Chat + Graph    │  Tool Cards   │
└────────────┴─────────────────┴──────────────────┴───────────────┘
```

### Target Layout (3 panels)
```
┌────────────┬─────────────────────────┬──────────────────────────┐
│  BINDER    │       CANVAS            │      THE FOREMAN         │
│  (240px)   │    (flex, min 500px)    │        (400px)           │
│            │                         │                          │
│  FileTree  │   Monaco Editor         │  [Studio ▼] [⚙️]         │
│            │   + Breadcrumbs         │  ┌────────────────────┐  │
│            │                         │  │  Chat Interface    │  │
│            │                         │  │  (Primary, 70%)    │  │
│            │                         │  │                    │  │
│            │                         │  ├────────────────────┤  │
│            │                         │  │  Live Graph        │  │
│            │                         │  │  (Collapsible 30%) │  │
│            │                         │  └────────────────────┘  │
└────────────┴─────────────────────────┴──────────────────────────┘
```

## IMPORTANT: Keep Live Graph in Foreman Panel

**The Live Graph (knowledge graph visualization) should remain in the Foreman panel!**

It's currently in a split-view configuration with the chat:
- **Top 60%**: Chat interface (primary)
- **Draggable splitter**: User can resize
- **Bottom 40%**: Live Graph (collapsible)

**Do NOT remove the Live Graph** - it's a key feature that visualizes the story's knowledge graph (characters, locations, themes, relationships) in real-time as the writer works with The Foreman.

The existing `LiveGraph.svelte` component and splitter functionality should be preserved exactly as-is in the current `ForemanPanel.svelte`.

## Reference: Cursor AI Chat Panel

**See screenshots**:
- `Screenshot 2025-11-26 at 20.46.16.png` - Cursor AI chat panel with message actions
- Shows critical UX patterns we need to implement

**Key Features to Replicate**:

### 1. Message Action Buttons (bottom-right of each AI response)
- **Copy** (📋) - Copy entire response to clipboard
- **Insert at cursor** (📝) - Paste directly into editor at cursor position
- **Regenerate** (🔄) - Get alternative response from AI

### 2. Enhanced Input Box Features
- **@ symbol** - Context/file references
- **Attachment** (📎) - Add files/images to conversation
- **Voice input** (🎤) - Speak instead of type
- **Model selector** - Switch between AI models (future: DeepSeek, Claude, GPT-4, etc.)

## Implementation Tasks

### Task 1: Update MainLayout.svelte (3-Panel Design)

**File**: `frontend/src/lib/components/MainLayout.svelte`

**Changes**:

1. **Remove Studio panel** from layout (lines 237-267 approximately)
2. **Update CSS variables** for panel widths:

```css
/* CSS Variables to update */
:root {
  --panel-binder-width: 240px;
  --panel-foreman-width: 400px;  /* Changed from 320px */
  /* REMOVE: --panel-studio-width: 280px; */
}
```

3. **Remove panel-studio styles** (lines 575-583 approximately)

4. **Remove Studio collapse toggle**:
```javascript
// DELETE from script section:
let studioCollapsed = false;

function toggleStudio() {
  studioCollapsed = !studioCollapsed;
}
```

5. **Remove Studio panel HTML**:
```svelte
<!-- DELETE this entire section (lines ~237-267): -->
<aside class="panel panel-studio {studioCollapsed ? 'collapsed' : ''}">
  <div class="panel-header">
    <div class="panel-title-group">
      <div class="panel-icon">...</div>
      <h2 class="panel-title">STUDIO</h2>
    </div>
    <button class="collapse-btn" on:click={toggleStudio}>...</button>
  </div>
  <div class="panel-content">
    <slot name="studio" />
  </div>
</aside>
```

### Task 2: Update +page.svelte

**File**: `frontend/src/routes/+page.svelte`

**Changes**:

1. **Remove StudioPanel import**:
```svelte
// DELETE:
import StudioPanel from '$lib/components/StudioPanel.svelte';
```

2. **Remove studio slot**:
```svelte
<!-- DELETE: -->
<svelte:fragment slot="studio">
  <StudioPanel />
</svelte:fragment>
```

**Result**: Should have only 3 slots: `binder`, `canvas`, `foreman`

### Task 3: Add Studio Dropdown to ForemanPanel

**File**: `frontend/src/lib/components/ForemanPanel.svelte`

**Location**: Add to header section (after line ~237 in the header)

**New Code**:

```svelte
<script>
  // Add to script section
  let showStudioMenu = false;

  function toggleStudioMenu() {
    showStudioMenu = !showStudioMenu;
  }

  function openTool(toolId) {
    showStudioMenu = false;
    // Dispatch event to open modal with tool
    dispatch('open-tool', { tool: toolId });
  }
</script>

<!-- Add to header, replacing mode tabs area -->
<div class="foreman-header">
  <div class="header-left">
    <div class="foreman-avatar">F</div>
    <h2 class="foreman-title">The Foreman</h2>
    <div class="header-status">
      <span class="status-dot {status}"></span>
      <span class="status-text">{statusText}</span>
    </div>
  </div>

  <div class="header-right">
    <!-- Studio Dropdown -->
    <div class="studio-dropdown">
      <button
        class="dropdown-btn"
        on:click={toggleStudioMenu}
        aria-expanded={showStudioMenu}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
        </svg>
        Studio
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      {#if showStudioMenu}
        <div class="studio-menu" on:click|stopPropagation>
          <button class="menu-item" on:click={() => openTool('voice-tournament')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            </svg>
            Voice Tournament
          </button>

          <button class="menu-item" on:click={() => openTool('scaffold-generator')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
            </svg>
            Scaffold Generator
          </button>

          <button class="menu-item" on:click={() => openTool('health-dashboard')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
            Health Dashboard
          </button>

          <button class="menu-item" on:click={() => openTool('metabolism')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            Metabolism
          </button>

          <div class="menu-divider"></div>

          <button class="menu-item" on:click={() => openTool('scene-multiplier')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Scene Multiplier (×5)
          </button>
        </div>
      {/if}
    </div>

    <!-- Settings Button -->
    <button class="icon-btn" on:click={() => dispatch('open-settings')} title="Settings">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="3"></circle>
        <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24"></path>
      </svg>
    </button>
  </div>
</div>
```

**Styles to Add**:

```css
/* Foreman Header */
.foreman-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

/* Studio Dropdown */
.studio-dropdown {
  position: relative;
}

.dropdown-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dropdown-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--border-strong);
}

.studio-menu {
  position: absolute;
  top: calc(100% + var(--space-1));
  right: 0;
  min-width: 220px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 100;
  padding: var(--space-1);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.menu-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.menu-divider {
  height: 1px;
  background: var(--border);
  margin: var(--space-1) 0;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-1);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--border);
  color: var(--text-secondary);
}
```

### Task 4: Add Message Action Buttons

**File**: `frontend/src/lib/components/ForemanPanel.svelte`

**Location**: Update message rendering (lines ~296-316)

**Replace**:
```svelte
<!-- BEFORE: -->
<div class="message {msg.role}">
  <div class="message-avatar {msg.role}">...</div>
  <div class="message-bubble">{msg.text}</div>
</div>
```

**With**:
```svelte
<!-- AFTER: -->
<div class="message {msg.role}">
  <div class="message-avatar {msg.role}">...</div>
  <div class="message-content">
    <div class="message-bubble">{msg.text}</div>

    {#if msg.role === 'assistant'}
      <div class="message-actions">
        <button
          class="action-btn"
          on:click={() => copyToClipboard(msg.text)}
          title="Copy to clipboard"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        </button>

        <button
          class="action-btn"
          on:click={() => insertToEditor(msg.text)}
          title="Insert to editor"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 20h9"></path>
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
          </svg>
        </button>

        <button
          class="action-btn"
          on:click={() => regenerateMessage(msg.id)}
          title="Regenerate response"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
        </button>
      </div>
    {/if}
  </div>
</div>
```

**Add to script section**:
```javascript
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    // TODO: Show toast notification "Copied to clipboard"
  } catch (err) {
    console.error('Failed to copy:', err);
  }
}

function insertToEditor(text) {
  // Dispatch event to parent to insert text at cursor position in Monaco editor
  dispatch('insert-to-editor', { text });
}

async function regenerateMessage(messageId) {
  // Find the message and re-submit the previous user message
  const msgIndex = messages.findIndex(m => m.id === messageId);
  if (msgIndex > 0) {
    const userMsg = messages[msgIndex - 1];
    if (userMsg.role === 'user') {
      // Remove the AI response and re-submit
      messages = messages.slice(0, msgIndex);
      await sendMessage(userMsg.text);
    }
  }
}
```

**Styles to Add**:
```css
.message-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.message-actions {
  display: flex;
  gap: var(--space-1);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.message:hover .message-actions {
  opacity: 1;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--border-strong);
  color: var(--text-secondary);
}
```

### Task 5: Enhance Chat Input

**File**: `frontend/src/lib/components/ForemanPanel.svelte`

**Location**: Replace chat-input section (lines ~336-350)

**Replace**:
```svelte
<!-- BEFORE: -->
<div class="chat-input">
  <textarea ... ></textarea>
  <button class="send-btn" ...>...</button>
</div>
```

**With**:
```svelte
<!-- AFTER: -->
<div class="chat-input-enhanced">
  <div class="input-toolbar">
    <button
      class="toolbar-btn"
      on:click={() => showMentionMenu = !showMentionMenu}
      title="@mention files or context"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M16 8v5a3 3 0 0 1-6 0v-1a10 10 0 1 0 3 7 3 3 0 0 0-3-3h-1"></path>
      </svg>
    </button>

    <button
      class="toolbar-btn"
      on:click={handleAttachment}
      title="Attach files"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
      </svg>
    </button>
  </div>

  <textarea
    bind:value={input}
    on:keydown={handleKeydown}
    placeholder="Ask the Foreman..."
    disabled={isLoading}
    rows="1"
  ></textarea>

  <div class="input-actions">
    <button
      class="toolbar-btn"
      on:click={handleVoiceInput}
      title="Voice input"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      </svg>
    </button>

    <button
      class="send-btn"
      on:click={sendMessage}
      disabled={isLoading || !input.trim()}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
    </button>
  </div>
</div>
```

**Add to script**:
```javascript
let showMentionMenu = false;

async function handleAttachment() {
  // Use Tauri dialog to select files
  // TODO: Implement file attachment
  console.log('Attachment feature coming soon');
}

function handleVoiceInput() {
  // TODO: Implement voice input with Web Speech API
  console.log('Voice input feature coming soon');
}
```

**Styles to Add**:
```css
.chat-input-enhanced {
  display: flex;
  gap: var(--space-1);
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-top: 1px solid var(--border);
}

.input-toolbar,
.input-actions {
  display: flex;
  gap: var(--space-1);
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-1);
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toolbar-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--border-strong);
  color: var(--text-secondary);
}

.chat-input-enhanced textarea {
  flex: 1;
  padding: var(--space-2);
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  resize: none;
  min-height: 40px;
  max-height: 120px;
}
```

### Task 6: Fix Branding

**Files to Update**:
1. `frontend/src/lib/components/StudioPanel.svelte` (line ~253)
2. Any other instances of "Antigravity"

**Find and Replace**:
```
Find: "Antigravity"
Replace: "Writers Factory"
```

**Specific Fix in StudioPanel.svelte**:
```svelte
<!-- BEFORE (line ~253): -->
<span class="footer-label">Antigravity</span>

<!-- AFTER: -->
<span class="footer-label">Writers Factory</span>
```

## Testing Checklist

After implementation, verify:

- [ ] **Layout**: Only 3 panels visible (Binder, Canvas, Foreman)
- [ ] **Width**: Foreman panel is 400px wide
- [ ] **Studio Dropdown**:
  - [ ] Clicks to open (stays open)
  - [ ] Shows all 5+ tools
  - [ ] Clicking outside closes menu
- [ ] **Message Actions**:
  - [ ] Copy button copies text to clipboard
  - [ ] Insert button triggers event (implementation in +page.svelte needed)
  - [ ] Regenerate button re-submits previous message
  - [ ] Actions only show on hover
- [ ] **Enhanced Input**:
  - [ ] @mention button present (functionality placeholder)
  - [ ] Attachment button present (functionality placeholder)
  - [ ] Voice input button present (functionality placeholder)
  - [ ] Send button works as before
- [ ] **Branding**: "Writers Factory" appears instead of "Antigravity"
- [ ] **Responsive**: Panel collapse/expand still works
- [ ] **No regressions**: Existing chat, graph, project init still work

## Files Modified Summary

1. **MainLayout.svelte** - Remove Studio panel, update CSS
2. **+page.svelte** - Remove Studio slot
3. **ForemanPanel.svelte** - Add dropdown, message actions, enhanced input
4. **StudioPanel.svelte** - Fix branding (keep file for future modal overlays)

## Future Enhancements (Not in this task)

- Implement @mention file/context picker
- Implement file attachment handling
- Implement voice input with Web Speech API
- Add model selector dropdown
- Connect "Insert to Editor" to Monaco editor cursor position
- Create modal overlays for Studio tool cards

## Questions?

If anything is unclear or you encounter issues, check:
- Cursor AI screenshot reference for UX patterns
- Existing Svelte components for styling consistency
- Console for any errors during testing

Good luck! This will significantly improve the writer's experience with The Foreman.
