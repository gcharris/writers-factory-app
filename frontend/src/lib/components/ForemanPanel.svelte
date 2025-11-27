<!--
  ForemanPanel.svelte - The Assistant Chat Interface (Muse/Scribe)

  IDE-style chat interface with:
  - Immediate chat access (no project gate)
  - Configurable assistant name
  - Header buttons: Notebook, Studio, Graph, Sessions, Settings
  - Enhanced input with @mention and attachments
  - Optional project context display
-->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    foremanActive, foremanMode, foremanProjectTitle, foremanProtagonist,
    foremanWorkOrder, foremanChatHistory, activeModal, activeFile,
    assistantName, currentStage, assistantSettings,
    showWorkOrderHistory, cancelWorkOrder
  } from '$lib/stores';
  import AgentDropdown from './chat/AgentDropdown.svelte';
  import StageDropdown from './chat/StageDropdown.svelte';
  import MentionPicker from './chat/MentionPicker.svelte';
  import AttachButton from './chat/AttachButton.svelte';
  import ContextBadge from './chat/ContextBadge.svelte';
  import VoiceInput from './chat/VoiceInput.svelte';
  import StatusBar from './chat/StatusBar.svelte';
  import WorkOrderHistory from './chat/WorkOrderHistory.svelte';

  const dispatch = createEventDispatcher();

  let messages = [];
  let input = "";
  let status = "Ready";
  let isLoading = false;
  let kbStats = null;
  let hasProject = false;

  // Enhanced input state
  let showMentionMenu = false;
  let selectedAgent = 'default';
  let contextItems = []; // Array of { type, name, id?, path?, content? }
  let inputRef;

  // Sync messages with Foreman chat history
  $: {
    if ($foremanChatHistory.length > 0) {
      messages = $foremanChatHistory;
    }
  }

  // Track if we have an active project
  $: hasProject = $foremanActive && $foremanProjectTitle;

  onMount(async () => {
    await checkForemanStatus();
    // Add welcome message if chat is empty
    if (messages.length === 0) {
      messages = [{
        role: 'system',
        text: `Hello! I'm ${$assistantName}, your writing assistant. How can I help you today?`
      }];
    }
  });

  async function checkForemanStatus() {
    try {
      const result = await apiClient.foremanStatus();
      foremanActive.set(result.active);
      status = result.active ? "Online" : "Ready";

      if (result.active && result.work_order) {
        foremanMode.set(result.mode);
        foremanProjectTitle.set(result.work_order.project_title);
        foremanProtagonist.set(result.work_order.protagonist_name);

        const uiTemplates = result.work_order.templates.map(t => ({
          name: t.name,
          required_fields: t.required_fields,
          completed_fields: t.required_fields.filter(f => !t.missing_fields.includes(f)),
          status: t.status === 'not_started' ? 'pending' : t.status === 'complete' ? 'complete' : 'partial'
        }));
        foremanWorkOrder.set({
          project_title: result.work_order.project_title,
          protagonist_name: result.work_order.protagonist_name,
          mode: result.work_order.mode,
          templates: uiTemplates
        });

        if (result.kb_stats) {
          kbStats = result.kb_stats;
        }
      }
    } catch (e) {
      console.warn('Failed to check Foreman status:', e);
      // Even if backend is down, chat should work (degraded mode)
      status = "Ready";
    }
  }

  // Reset project context (but keep chat available)
  async function resetProject() {
    try {
      await apiClient.foremanReset();
      foremanActive.set(false);
      foremanMode.set(null);
      foremanProjectTitle.set(null);
      foremanProtagonist.set(null);
      foremanWorkOrder.set(null);
      // Don't clear messages - keep chat history
      const systemMsg = {
        role: 'system',
        text: 'Project context cleared. I\'m still here to help!'
      };
      messages = [...messages, systemMsg];
      foremanChatHistory.set(messages);
    } catch (e) {
      console.error('Failed to reset project:', e);
    }
  }

  async function sendMessage() {
    if (!input.trim() || isLoading) return;

    isLoading = true;
    status = "Thinking...";
    const currentInput = input;
    input = "";

    const userMsg = { role: 'user', text: currentInput };
    messages = [...messages, userMsg];

    try {
      console.log('[ForemanPanel] Sending message:', currentInput);
      const data = await apiClient.foremanChat(currentInput);
      console.log('[ForemanPanel] Response:', data);

      if (data.response) {
        const assistantMsg = { role: 'assistant', text: data.response };
        messages = [...messages, assistantMsg];
      } else if (data.error) {
        const errorMsg = { role: 'system', text: `Backend error: ${data.error}` };
        messages = [...messages, errorMsg];
      } else {
        // Response exists but has unexpected format
        const infoMsg = { role: 'system', text: `Unexpected response format: ${JSON.stringify(data)}` };
        messages = [...messages, infoMsg];
      }

      if (data.work_order_status) {
        foremanWorkOrder.set(data.work_order_status);
      }

      if (data.actions_executed && data.actions_executed.length > 0) {
        const actionsMsg = {
          role: 'system',
          text: `Actions: ${data.actions_executed.join(', ')}`
        };
        messages = [...messages, actionsMsg];
      }

      await checkForemanStatus();
      status = "Ready";
    } catch (e) {
      console.error('[ForemanPanel] Error:', e);
      let errorText = e.message || 'Unknown error';

      // Provide helpful hints for common errors
      if (errorText.includes('fetch') || errorText.includes('NetworkError')) {
        errorText = 'Cannot reach backend. Is the server running on port 8000?';
      } else if (errorText.includes('500')) {
        errorText = 'Backend error. Check if Ollama is running: `ollama serve`';
      }

      const errorMsg = { role: 'system', text: `Error: ${errorText}` };
      messages = [...messages, errorMsg];
      status = "Error";
    } finally {
      isLoading = false;
      foremanChatHistory.set(messages);
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  // Template status icons
  function getStatusIcon(status) {
    switch (status) {
      case 'complete': return '✓';
      case 'partial': return '◐';
      default: return '○';
    }
  }

  // ============================================
  // Header Button Functions
  // ============================================
  function openNotebook() {
    activeModal.set('notebooklm');
  }

  function openStudio() {
    activeModal.set('studio-tools');
  }

  function openGraph() {
    activeModal.set('graph-viewer');
  }

  function openSettings() {
    activeModal.set('settings');
  }

  function openSessions() {
    activeModal.set('session-manager');
  }

  // Handle loading a session from session manager
  export function loadSession(sessionId, history) {
    // Convert session history to our message format
    messages = history
      .filter(e => e.role !== 'system')
      .map(e => ({
        role: e.role,
        text: e.content
      }));
    foremanChatHistory.set(messages);
  }

  // ============================================
  // Message Action Functions
  // ============================================
  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      // TODO: Show toast notification "Copied to clipboard"
      console.log('Copied to clipboard');
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }

  function insertToEditor(text) {
    // Dispatch event to parent to insert text at cursor position in Monaco editor
    dispatch('insert-to-editor', { text });
  }

  async function regenerateMessage(msgIndex) {
    // Find the user message before this assistant message and re-submit
    if (msgIndex > 0) {
      const userMsg = messages[msgIndex - 1];
      if (userMsg && userMsg.role === 'user') {
        // Remove the AI response and re-submit
        messages = messages.slice(0, msgIndex);
        foremanChatHistory.set(messages);

        // Re-send the user message
        input = userMsg.text;
        messages = messages.slice(0, msgIndex - 1); // Also remove the user message since sendMessage will add it
        await sendMessage();
      }
    }
  }

  // ============================================
  // Enhanced Input Functions
  // ============================================

  // Auto-include active file as context (if enabled)
  $: if ($assistantSettings.autoIncludeFile && $activeFile) {
    const fileName = $activeFile.split('/').pop();
    const existingFile = contextItems.find(c => c.type === 'active-file');
    if (!existingFile) {
      // Add as non-removable active file indicator
      contextItems = [
        { type: 'active-file', name: fileName, path: $activeFile, removable: false },
        ...contextItems.filter(c => c.type !== 'active-file')
      ];
    } else if (existingFile.path !== $activeFile) {
      // Update to new file
      contextItems = contextItems.map(c =>
        c.type === 'active-file' ? { ...c, name: fileName, path: $activeFile } : c
      );
    }
  } else if (!$assistantSettings.autoIncludeFile) {
    // Remove auto-included file if setting disabled
    contextItems = contextItems.filter(c => c.type !== 'active-file');
  }

  function handleAttachment(e) {
    const attachment = e.detail;
    // Add attachment to context
    contextItems = [...contextItems, {
      type: attachment.type,
      name: attachment.name,
      content: attachment.content,
      size: attachment.size,
      mimeType: attachment.mimeType,
      removable: true
    }];
  }

  function handleMentionSelect(e) {
    const mention = e.detail;
    // Add mention to context items
    contextItems = [...contextItems, {
      type: mention.type,
      name: mention.name,
      id: mention.id,
      path: mention.path,
      removable: true
    }];
    // Also insert into input
    input = input + `@${mention.name} `;
    inputRef?.focus();
  }

  function removeContextItem(e) {
    const { index } = e.detail;
    contextItems = contextItems.filter((_, i) => i !== index);
  }

  function handleAgentChange(e) {
    selectedAgent = e.detail.agent;
  }

  function openAgentSettings() {
    activeModal.set('settings');
    // TODO: Navigate to Squad tab
  }

  // Voice input handlers
  function handleVoiceResult(e) {
    const { transcript } = e.detail;
    if (transcript) {
      // Append to existing input with a space
      input = input ? `${input} ${transcript}` : transcript;
      inputRef?.focus();
    }
  }

  function handleVoiceInterim(e) {
    // Could show live preview - for now just log
    // console.log('Interim:', e.detail.transcript);
  }

  function handleVoiceError(e) {
    const { error } = e.detail;
    // Show error as system message
    const errorMsg = { role: 'system', text: `Voice input: ${error}` };
    messages = [...messages, errorMsg];
  }

  function toggleMentionMenu() {
    showMentionMenu = !showMentionMenu;
  }

  // Work order handlers
  function openWorkOrderHistory() {
    showWorkOrderHistory.set(true);
  }

  function handleCancelTask(e) {
    const { id } = e.detail;
    if (confirm('Cancel this task?')) {
      cancelWorkOrder(id);
    }
  }

  function closeWorkOrderHistory() {
    showWorkOrderHistory.set(false);
  }
</script>

<div class="foreman-panel">
  <!-- Chat Section (Full Height) -->
  <div class="chat-section">
    <!-- Assistant Header -->
    <div class="foreman-header">
      <div class="header-left">
        <span class="foreman-avatar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
          </svg>
        </span>
        <span class="header-title">{$assistantName}</span>
        <div class="header-status">
          <span class="status-dot {status === 'Online' ? 'online' : 'ready'}"></span>
          <span class="status-text">{status}</span>
        </div>
      </div>

      <div class="header-right">
        <!-- Icon-only buttons with hover tooltips -->
        <button class="header-btn" on:click={openNotebook} title="NotebookLM Research">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
        </button>

        <button class="header-btn" on:click={openStudio} title="Studio Tools">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
          </svg>
        </button>

        <button class="header-btn" on:click={openGraph} title="Knowledge Graph">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <circle cx="4" cy="6" r="2"></circle>
            <circle cx="20" cy="6" r="2"></circle>
            <circle cx="4" cy="18" r="2"></circle>
            <circle cx="20" cy="18" r="2"></circle>
            <line x1="6" y1="6" x2="9.5" y2="10"></line>
            <line x1="18" y1="6" x2="14.5" y2="10"></line>
            <line x1="6" y1="18" x2="9.5" y2="14"></line>
            <line x1="18" y1="18" x2="14.5" y2="14"></line>
          </svg>
        </button>

        <button class="header-btn" on:click={openSessions} title="Chat Sessions">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </button>

        <button class="header-btn settings" on:click={openSettings} title="Settings">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Project Info -->
    {#if $foremanProjectTitle}
      <div class="project-info">
        <span class="project-badge">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          </svg>
          {$foremanProjectTitle}
        </span>
        <span class="protagonist-badge">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
          {$foremanProtagonist}
        </span>
      </div>
    {/if}

    <!-- Work Order Display -->
    {#if $foremanWorkOrder && $foremanWorkOrder.templates}
      <div class="work-order">
        <div class="work-order-header">
          <span class="work-order-title">Work Order</span>
          <span class="work-order-progress">
            {$foremanWorkOrder.templates.filter(t => t.status === 'complete').length}/{$foremanWorkOrder.templates.length}
          </span>
        </div>
        <div class="template-list">
          {#each $foremanWorkOrder.templates as template}
            <div class="template-item {template.status}">
              <span class="template-status">{getStatusIcon(template.status)}</span>
              <span class="template-name">{template.name}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Chat Messages -->
      <div class="chat-messages">
        {#each messages as msg, i}
          <div class="message {msg.role}">
            {#if msg.role === 'user'}
              <div class="message-avatar user">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
            {:else if msg.role === 'assistant'}
              <div class="message-avatar assistant">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="10" rx="2"></rect>
                  <circle cx="12" cy="5" r="2"></circle>
                  <path d="M12 7v4"></path>
                </svg>
              </div>
            {/if}
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
                    on:click={() => regenerateMessage(i)}
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
        {/each}
        {#if isLoading}
          <div class="message assistant">
            <div class="message-avatar assistant">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="10" rx="2"></rect>
                <circle cx="12" cy="5" r="2"></circle>
                <path d="M12 7v4"></path>
              </svg>
            </div>
            <div class="message-bubble typing">
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
            </div>
          </div>
        {/if}
      </div>

      <!-- Enhanced Chat Input -->
      <div class="chat-input-enhanced">
        <!-- Top Row: Dropdowns -->
        <div class="input-controls">
          <AgentDropdown
            {selectedAgent}
            on:change={handleAgentChange}
            on:configure={openAgentSettings}
          />
          {#if $assistantSettings.showStage}
            <StageDropdown on:change />
          {/if}
        </div>

        <!-- Context Badges -->
        <ContextBadge items={contextItems} on:remove={removeContextItem} />

        <!-- Input Row -->
        <div class="input-row">
          <div class="input-toolbar">
            <button
              class="toolbar-btn mention-btn"
              class:active={showMentionMenu}
              on:click={toggleMentionMenu}
              title="@mention files or context"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="4"></circle>
                <path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94"></path>
              </svg>
            </button>

            <AttachButton on:attach={handleAttachment} />
          </div>

          <div class="input-field-wrapper">
            <textarea
              bind:this={inputRef}
              bind:value={input}
              on:keydown={handleKeydown}
              placeholder="Ask {$assistantName}..."
              disabled={isLoading}
              rows="1"
            ></textarea>

            <!-- Mention Picker (positioned above input) -->
            <MentionPicker
              bind:open={showMentionMenu}
              on:select={handleMentionSelect}
              on:close={() => showMentionMenu = false}
            />
          </div>

          <div class="input-actions">
            <VoiceInput
              disabled={isLoading}
              on:result={handleVoiceResult}
              on:interim={handleVoiceInterim}
              on:error={handleVoiceError}
            />

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
      </div>

      <!-- Status Bar (bottom of panel) -->
      <StatusBar
        on:open-history={openWorkOrderHistory}
        on:cancel-task={handleCancelTask}
      />
  </div>
</div>

<!-- Work Order History Modal -->
{#if $showWorkOrderHistory}
  <WorkOrderHistory on:close={closeWorkOrderHistory} />
{/if}

<style>
  .foreman-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-secondary);
    font-family: var(--font-ui);
  }

  /* ============================================
   * CHAT SECTION
   * ============================================ */
  .chat-section {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
  }

  .foreman-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-tertiary);
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

  .header-title {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
  }

  .foreman-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: var(--accent-gold-muted);
    border-radius: var(--radius-full);
    color: var(--accent-gold);
  }

  .header-status {
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: var(--radius-full);
  }

  .status-dot.online { background: var(--success); }
  .status-dot.ready { background: var(--warning); }
  .status-dot.offline { background: var(--error); }

  .status-text {
    font-size: var(--text-xs);
    color: var(--text-muted);
  }

  /* Header Buttons */
  .header-btn {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-2);
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .header-btn:hover {
    background: var(--bg-elevated);
    border-color: var(--border-strong);
    color: var(--text-primary);
  }

  .header-btn.settings {
    padding: var(--space-1);
  }

  /* Project Info */
  .project-info {
    display: flex;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border);
  }

  .project-badge,
  .protagonist-badge {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: 2px var(--space-2);
    background: var(--bg-tertiary);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    color: var(--text-secondary);
  }

  .project-badge svg,
  .protagonist-badge svg {
    color: var(--accent-gold);
  }

  /* Work Order */
  .work-order {
    padding: var(--space-2) var(--space-3);
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border);
  }

  .work-order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-2);
  }

  .work-order-title {
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    color: var(--text-secondary);
    letter-spacing: 0.5px;
  }

  .work-order-progress {
    font-size: var(--text-xs);
    color: var(--accent-cyan);
    font-weight: var(--font-semibold);
  }

  .template-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .template-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-1) var(--space-2);
    background: var(--bg-secondary);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
  }

  .template-status {
    font-size: 10px;
  }

  .template-item.complete .template-status { color: var(--success); }
  .template-item.partial .template-status { color: var(--warning); }
  .template-item.pending .template-status { color: var(--text-muted); }

  .template-name {
    color: var(--text-secondary);
  }

  .template-item.complete .template-name {
    color: var(--success);
  }

  /* Chat Messages */
  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-3);
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .message {
    display: flex;
    gap: var(--space-2);
    align-items: flex-start;
  }

  .message.user {
    flex-direction: row-reverse;
  }

  .message.system {
    justify-content: center;
  }

  .message-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: var(--radius-full);
    flex-shrink: 0;
  }

  .message-avatar.user {
    background: var(--accent-cyan-muted);
    color: var(--accent-cyan);
  }

  .message-avatar.assistant {
    background: var(--accent-gold-muted);
    color: var(--accent-gold);
  }

  .message-bubble {
    max-width: 85%;
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-lg);
    font-size: var(--text-sm);
    line-height: var(--leading-relaxed);
    white-space: pre-wrap;
  }

  .message.user .message-bubble {
    background: var(--accent-cyan-muted);
    color: var(--text-primary);
  }

  .message.assistant .message-bubble {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .message.system .message-bubble {
    background: transparent;
    color: var(--text-muted);
    font-size: var(--text-xs);
    font-style: italic;
  }

  /* Typing indicator */
  .message-bubble.typing {
    display: flex;
    gap: 4px;
    padding: var(--space-3);
  }

  .typing-dot {
    width: 6px;
    height: 6px;
    background: var(--text-muted);
    border-radius: var(--radius-full);
    animation: typing 1.4s infinite ease-in-out;
  }

  .typing-dot:nth-child(2) { animation-delay: 0.2s; }
  .typing-dot:nth-child(3) { animation-delay: 0.4s; }

  @keyframes typing {
    0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
    40% { opacity: 1; transform: scale(1); }
  }

  /* Message Content & Actions */
  .message-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    max-width: 85%;
  }

  .message.user .message-content {
    align-items: flex-end;
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

  /* Enhanced Chat Input */
  .chat-input-enhanced {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--bg-tertiary);
    border-top: 1px solid var(--border);
  }

  .input-controls {
    display: flex;
    gap: var(--space-2);
  }

  .input-row {
    display: flex;
    align-items: flex-end;
    gap: var(--space-2);
  }

  .input-toolbar,
  .input-actions {
    display: flex;
    gap: var(--space-1);
  }

  .input-field-wrapper {
    flex: 1;
    position: relative;
  }

  .toolbar-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-muted);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .toolbar-btn:hover {
    background: var(--bg-secondary);
    border-color: var(--border-strong);
    color: var(--text-secondary);
  }

  .toolbar-btn.mention-btn.active {
    background: var(--accent-cyan-muted);
    border-color: var(--accent-cyan);
    color: var(--accent-cyan);
  }

  .chat-input-enhanced textarea {
    width: 100%;
    padding: var(--space-2);
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    font-family: var(--font-ui);
    resize: none;
    min-height: 36px;
    max-height: 100px;
  }

  .chat-input-enhanced textarea:focus {
    outline: none;
    border-color: var(--accent-cyan);
  }

  .chat-input-enhanced textarea::placeholder {
    color: var(--text-muted);
  }

  .send-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: var(--accent-cyan);
    border: none;
    border-radius: var(--radius-md);
    color: white;
    cursor: pointer;
    transition: all var(--transition-fast);
    flex-shrink: 0;
  }

  .send-btn:hover:not(:disabled) {
    background: var(--accent-cyan-hover);
  }

  .send-btn:disabled {
    background: var(--bg-elevated);
    color: var(--text-muted);
    cursor: not-allowed;
  }

</style>
