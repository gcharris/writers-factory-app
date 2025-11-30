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
  } from '$lib/stores';
  import ModelSelector from './chat/ModelSelector.svelte';
  import MentionPicker from './chat/MentionPicker.svelte';
  import ContextBadge from './chat/ContextBadge.svelte';
  import VoiceInput from './chat/VoiceInput.svelte';

  const dispatch = createEventDispatcher();

  let messages = [];
  let input = "";
  let status = "Ready";
  let isLoading = false;
  let kbStats = null;
  let hasProject = false;

  // Enhanced input state
  let showMentionMenu = false;
  let contextItems = []; // Array of { type, name, id?, path?, content? }
  let isDragOver = false; // For drag-drop file support
  let inputRef;
  let fileInputRef; // Hidden file input for + button
  let interimTranscript = ""; // Live voice preview
  let chatMessagesRef; // Reference to chat container for auto-scroll

  // Auto-scroll to bottom when messages change
  function scrollToBottom() {
    if (chatMessagesRef) {
      // Use setTimeout to ensure DOM has updated
      setTimeout(() => {
        chatMessagesRef.scrollTop = chatMessagesRef.scrollHeight;
      }, 0);
    }
  }

  // Sync messages with Foreman chat history
  $: {
    if ($foremanChatHistory.length > 0) {
      messages = $foremanChatHistory;
    }
  }

  // Auto-scroll when messages array changes
  $: if (messages.length > 0) {
    scrollToBottom();
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
    // Scroll to bottom after initial load
    scrollToBottom();

    // DEBUG: Log focus/blur events for dictation troubleshooting
    if (inputRef) {
      inputRef.addEventListener('focus', () => {
        console.log('[Dictation Debug] Input FOCUSED');
        console.log('[Dictation Debug] contenteditable:', inputRef.getAttribute('contenteditable'));
        console.log('[Dictation Debug] computed styles:', {
          userSelect: getComputedStyle(inputRef).userSelect,
          webkitUserSelect: getComputedStyle(inputRef).webkitUserSelect,
          webkitUserModify: getComputedStyle(inputRef).webkitUserModify,
          pointerEvents: getComputedStyle(inputRef).pointerEvents,
        });
      });
      inputRef.addEventListener('blur', () => {
        console.log('[Dictation Debug] Input BLURRED');
      });
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
    // Clear the contenteditable div
    if (inputRef) {
      inputRef.textContent = '';
    }

    const userMsg = { role: 'user', text: currentInput };
    messages = [...messages, userMsg];

    try {
      console.log('[ForemanPanel] Sending message:', currentInput);

      // Convert contextItems to backend format
      const context = contextItems.map(item => {
        if (item.type === 'active-file' || item.type === 'file') {
          return { type: 'file', path: item.path };
        } else if (item.type === 'mention') {
          return { type: 'mention', id: item.id };
        } else if (item.type === 'attachment') {
          return { type: 'attachment', content: item.content, filename: item.name };
        }
        return null;
      }).filter(Boolean);

      // Use context-aware chat if we have context items
      const data = context.length > 0
        ? await apiClient.foremanChatWithContext(currentInput, context)
        : await apiClient.foremanChat(currentInput);

      console.log('[ForemanPanel] Response:', data);

      // Clear context items after successful send
      contextItems = [];

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

  // Handle input from contenteditable div
  function handleContentEditableInput(e) {
    // Get text content from contenteditable div
    input = e.target.textContent || '';

    // Detect @ to trigger mention menu (Cursor-style)
    if (e.inputType === 'insertText' && e.data === '@') {
      showMentionMenu = true;
    }
  }

  // Handle paste in contenteditable - strip formatting
  function handlePaste(e) {
    e.preventDefault();
    const text = e.clipboardData?.getData('text/plain') || '';
    document.execCommand('insertText', false, text);
  }

  // Handle keydown for Enter to send
  function handleKeydown(e) {
    // Skip if composing (IME/dictation)
    if (e.isComposing) return;

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
      // Clear the contenteditable div
      if (inputRef) {
        inputRef.textContent = '';
      }
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

  function openSessions() {
    activeModal.set('session-manager');
  }

  function clearChat() {
    messages = [{
      role: 'system',
      text: `Hello! I'm ${$assistantName}, your writing assistant. How can I help you today?`
    }];
    foremanChatHistory.set(messages);
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

  // Drag-drop handlers for files from binder
  function handleDragOver(e) {
    e.preventDefault();
    isDragOver = true;
  }

  function handleDragLeave(e) {
    e.preventDefault();
    isDragOver = false;
  }

  function handleDrop(e) {
    e.preventDefault();
    isDragOver = false;

    // First try: Get file data from binder (FileTree component)
    const fileData = e.dataTransfer?.getData('application/json');
    if (fileData) {
      try {
        const file = JSON.parse(fileData);
        contextItems = [...contextItems, {
          type: 'file',
          name: file.name,
          path: file.path,
          removable: true
        }];
        return;
      } catch (err) {
        console.warn('Failed to parse binder file data:', err);
      }
    }

    // Second try: Native file drop from Finder
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      for (const file of files) {
        contextItems = [...contextItems, {
          type: 'file',
          name: file.name,
          path: file.path || file.name, // file.path may not be available in browser
          removable: true
        }];
      }
    }
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
    // Also insert into input (contenteditable)
    const mentionText = `@${mention.name} `;
    input = input + mentionText;
    if (inputRef) {
      inputRef.textContent = input;
      // Move cursor to end
      const range = document.createRange();
      const sel = window.getSelection();
      range.selectNodeContents(inputRef);
      range.collapse(false);
      sel?.removeAllRanges();
      sel?.addRange(range);
    }
    inputRef?.focus();
  }

  function removeContextItem(e) {
    const { index } = e.detail;
    contextItems = contextItems.filter((_, i) => i !== index);
  }

  // Voice input handlers
  function handleVoiceResult(e) {
    const { transcript } = e.detail;
    if (transcript) {
      // Append to existing input with a space
      input = input ? `${input} ${transcript}` : transcript;
      // Clear interim and update contenteditable div
      interimTranscript = "";
      if (inputRef) {
        inputRef.textContent = input;
      }
      inputRef?.focus();
    }
  }

  function handleVoiceInterim(e) {
    // Show live preview of what's being spoken
    interimTranscript = e.detail.transcript;
    // Update contenteditable with current input + interim
    if (inputRef) {
      inputRef.textContent = input + (interimTranscript ? ' ' + interimTranscript : '');
    }
  }

  function handleVoiceError(e) {
    const { error } = e.detail;
    // Show error as system message
    const errorMsg = { role: 'system', text: `Voice input: ${error}` };
    messages = [...messages, errorMsg];
  }

  // File picker functions
  function openFilePicker() {
    fileInputRef?.click();
  }

  function handleFileSelect(e) {
    const files = e.target.files;
    if (files && files.length > 0) {
      for (const file of files) {
        contextItems = [...contextItems, {
          type: 'file',
          name: file.name,
          path: file.name, // Browser doesn't expose full path for security
          removable: true
        }];
      }
    }
    // Reset input so same file can be selected again
    e.target.value = '';
  }

  // Slash commands - insert "/" and focus input
  function openSlashMenu() {
    // Insert "/" into the input field
    input = '/';
    if (inputRef) {
      inputRef.textContent = '/';
      inputRef.focus();
      // Move cursor to end
      const range = document.createRange();
      const sel = window.getSelection();
      range.selectNodeContents(inputRef);
      range.collapse(false);
      sel?.removeAllRanges();
      sel?.addRange(range);
    }
    // TODO: Could show a command picker menu here in the future
  }
</script>

<div class="foreman-panel">
  <!-- Chat Section (Full Height) -->
  <div class="chat-section">
    <!-- Minimal Chat Header -->
    <div class="foreman-header">
      <div class="header-left">
        <span class="header-title">I'm {$assistantName}</span>
        <span class="header-subtitle">your writing assistant</span>
      </div>

      <div class="header-right">
        <!-- New Chat Button -->
        <button class="header-btn new-chat-btn" on:click={clearChat} title="Start New Chat">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span class="btn-label">New</span>
        </button>

        <!-- Chat History Button -->
        <button class="header-btn" on:click={openSessions} title="Chat History">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </button>

        <!-- Separator -->
        <span class="header-separator"></span>

        <!-- NotebookLM Button -->
        <button class="header-btn" on:click={openNotebook} title="NotebookLM Research">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
        </button>

        <!-- Studio Tools Button -->
        <button class="header-btn" on:click={openStudio} title="Studio Tools">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
            <polyline points="2 17 12 22 22 17"></polyline>
            <polyline points="2 12 12 17 22 12"></polyline>
          </svg>
        </button>

        <!-- Graph Button -->
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

        <!-- Settings Button -->
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
      <div class="chat-messages" bind:this={chatMessagesRef}>
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

      <!-- Chat Input (Cursor-style: full-width box with controls below) -->
      <div class="chat-input-area">
        <!-- Main Input Box - clicking anywhere focuses input -->
        <div
          class="chat-input-box"
          class:drag-over={isDragOver}
          on:dragover={handleDragOver}
          on:dragleave={handleDragLeave}
          on:drop={handleDrop}
          on:click={() => inputRef?.focus()}
        >
          <!-- Context badges row (only if files attached) -->
          {#if contextItems.length > 0}
            <div class="badges-row">
              <ContextBadge items={contextItems} on:remove={removeContextItem} compact />
            </div>
          {/if}

          <!-- Text input - starts at top left -->
          <div
            bind:this={inputRef}
            class="chat-input-editable"
            contenteditable={!isLoading}
            role="textbox"
            aria-multiline="true"
            aria-label="Message input"
            data-placeholder="Type your message..."
            on:input={handleContentEditableInput}
            on:keydown={handleKeydown}
            on:paste={handlePaste}
            spellcheck="true"
          ></div>

          <!-- Actions floating top-right -->
          <div class="input-actions-float">
            <VoiceInput
              disabled={isLoading}
              on:result={handleVoiceResult}
              on:interim={handleVoiceInterim}
              on:error={handleVoiceError}
            />
            <button
              class="send-btn"
              on:click|stopPropagation={sendMessage}
              disabled={isLoading || !input.trim()}
              title="Send message"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>

          <!-- Mention Picker -->
          <MentionPicker
            bind:open={showMentionMenu}
            on:select={handleMentionSelect}
            on:close={() => showMentionMenu = false}
          />
        </div>

        <!-- Controls row BELOW the input box -->
        <div class="input-controls-row">
          <ModelSelector />
          <button class="control-btn" on:click={() => showMentionMenu = true} title="Add context (@)">
            <span class="control-icon">@</span>
          </button>
          <button class="control-btn" on:click={openSlashMenu} title="Commands (/)">
            <span class="control-icon">/</span>
          </button>
          <button class="control-btn" on:click={openFilePicker} title="Attach file from disk">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>
          <!-- Hidden file input -->
          <input
            type="file"
            bind:this={fileInputRef}
            on:change={handleFileSelect}
            style="display: none;"
            multiple
          />
        </div>
      </div>
  </div>
</div>

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

  .header-subtitle {
    font-size: var(--text-xs);
    color: var(--text-muted);
  }

  .header-btn.new-chat-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
  }

  .header-btn.new-chat-btn:hover {
    background: var(--accent-cyan);
    border-color: var(--accent-cyan);
    color: white;
  }

  .btn-label {
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
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

  .header-separator {
    width: 1px;
    height: 16px;
    background: var(--border);
    margin: 0 var(--space-1);
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

  /* ============================================
   * CHAT INPUT AREA (Cursor-style)
   * ============================================ */
  .chat-input-area {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--bg-tertiary);
    border-top: 1px solid var(--border);
  }

  /* Main input box with border - shallow, expands as needed */
  .chat-input-box {
    position: relative;
    display: flex;
    flex-direction: column;
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: var(--space-2);
    padding-right: 80px; /* Space for floating actions */
    min-height: 40px;
    cursor: text;
    transition: border-color 0.2s, background-color 0.2s;
  }

  .chat-input-box:focus-within {
    border-color: var(--accent-cyan);
  }

  .chat-input-box.drag-over {
    border-color: var(--accent-cyan);
    background: var(--bg-elevated);
  }

  /* Badges row - only shown when items present */
  .badges-row {
    margin-bottom: var(--space-1);
  }

  /* Actions floating top-right */
  .input-actions-float {
    position: absolute;
    top: var(--space-2);
    right: var(--space-2);
    display: flex;
    gap: var(--space-1);
  }

  /* Contenteditable div for better Mac dictation support */
  .chat-input-editable {
    width: 100%;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: var(--text-sm);
    font-family: var(--font-ui);
    min-height: 20px;
    max-height: 120px;
    overflow-y: auto;
    outline: none;
    /* Critical for dictation support */
    -webkit-user-select: text;
    user-select: text;
    -webkit-user-modify: read-write;
    cursor: text;
  }

  /* Placeholder via data attribute */
  .chat-input-editable:empty::before {
    content: attr(data-placeholder);
    color: var(--text-muted);
    pointer-events: none;
  }

  .chat-input-editable[contenteditable="false"] {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Controls row below the input box */
  .input-controls-row {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding-top: var(--space-1);
  }

  .control-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-muted);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .control-btn:hover {
    background: var(--bg-elevated);
    border-color: var(--border-strong);
    color: var(--text-secondary);
  }

  .control-icon {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
  }

  /* Send button */
  .send-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
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
