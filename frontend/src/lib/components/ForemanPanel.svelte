<!--
  ForemanPanel.svelte - Foreman Chat + Live Knowledge Graph (Split View)

  Matches the mockup with:
  - Top 60%: Chat interface with work order display
  - Bottom 40%: Live Knowledge Graph with force-directed layout
  - Draggable splitter between sections
-->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    foremanActive, foremanMode, foremanProjectTitle, foremanProtagonist,
    foremanWorkOrder, foremanChatHistory
  } from '$lib/stores';
  import LiveGraph from './LiveGraph.svelte';

  let messages = [];
  let input = "";
  let status = "checking...";
  let isLoading = false;
  let showStartProject = false;
  let projectTitle = "";
  let protagonistName = "";
  let kbStats = null;

  // Splitter state
  let chatHeight = 60; // percentage
  let isDragging = false;
  let containerRef;

  // Sync messages with Foreman chat history
  $: {
    if ($foremanChatHistory.length > 0) {
      messages = $foremanChatHistory;
    }
  }

  onMount(async () => {
    await checkForemanStatus();
    if (!$foremanActive) {
      showStartProject = true;
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
      status = "Offline";
    }
  }

  async function newProject() {
    try {
      await apiClient.foremanReset();
      foremanActive.set(false);
      foremanMode.set(null);
      foremanProjectTitle.set(null);
      foremanProtagonist.set(null);
      foremanWorkOrder.set(null);
      messages = [];
      foremanChatHistory.set([]);
      showStartProject = true;
    } catch (e) {
      console.error('Failed to reset Foreman:', e);
    }
  }

  async function startProject() {
    if (!projectTitle.trim() || !protagonistName.trim()) return;

    isLoading = true;
    try {
      const result = await apiClient.foremanStart(projectTitle, protagonistName);
      foremanActive.set(true);
      foremanMode.set(result.mode);
      foremanProjectTitle.set(result.project_title);
      foremanProtagonist.set(result.protagonist_name);

      showStartProject = false;
      projectTitle = "";
      protagonistName = "";

      const welcomeMsg = {
        role: 'system',
        text: `Foreman initialized in ${result.mode} mode for "${result.project_title}" with protagonist ${result.protagonist_name}.`
      };
      messages = [welcomeMsg];
      foremanChatHistory.set(messages);

      await checkForemanStatus();
    } catch (e) {
      const errorMsg = { role: 'system', text: `Failed to start project: ${e.message}` };
      messages = [errorMsg];
    } finally {
      isLoading = false;
    }
  }

  async function sendMessage() {
    if (!input.trim() || isLoading) return;

    isLoading = true;
    const currentInput = input;
    input = "";

    const userMsg = { role: 'user', text: currentInput };
    messages = [...messages, userMsg];

    try {
      const data = await apiClient.foremanChat(currentInput);
      const assistantMsg = { role: 'assistant', text: data.response };
      messages = [...messages, assistantMsg];

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
    } catch (e) {
      const errorMsg = { role: 'system', text: `Error: ${e.message}` };
      messages = [...messages, errorMsg];
    } finally {
      isLoading = false;
      foremanChatHistory.set(messages);
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (showStartProject) {
        startProject();
      } else {
        sendMessage();
      }
    }
  }

  // Splitter drag handlers
  function startDrag(e) {
    isDragging = true;
    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', stopDrag);
    e.preventDefault();
  }

  function onDrag(e) {
    if (!isDragging || !containerRef) return;
    const rect = containerRef.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const percentage = (y / rect.height) * 100;
    chatHeight = Math.max(30, Math.min(80, percentage));
  }

  function stopDrag() {
    isDragging = false;
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', stopDrag);
  }

  // Template status icons
  function getStatusIcon(status) {
    switch (status) {
      case 'complete': return '✓';
      case 'partial': return '◐';
      default: return '○';
    }
  }
</script>

<div class="foreman-panel" bind:this={containerRef}>
  <!-- Chat Section (Top) -->
  <div class="chat-section" style="height: {chatHeight}%">
    <!-- The Foreman Header -->
    <div class="foreman-header">
      <div class="header-title">
        <span class="foreman-avatar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <circle cx="12" cy="10" r="3"></circle>
            <path d="M7 20.662V19a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v1.662"></path>
          </svg>
        </span>
        <span>The Foreman</span>
      </div>
      <div class="header-status">
        <span class="status-dot {status === 'Online' ? 'online' : status === 'Ready' ? 'ready' : 'offline'}"></span>
        <span class="status-text">{status}</span>
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

    <!-- Start Project Form -->
    {#if showStartProject}
      <div class="start-project">
        <div class="start-project-header">Start New Project</div>
        <div class="form-group">
          <label>Project Title</label>
          <input
            type="text"
            bind:value={projectTitle}
            placeholder="e.g., Big Brain"
            on:keydown={handleKeydown}
          />
        </div>
        <div class="form-group">
          <label>Protagonist Name</label>
          <input
            type="text"
            bind:value={protagonistName}
            placeholder="e.g., Mickey Bardot"
            on:keydown={handleKeydown}
          />
        </div>
        <button class="start-btn" on:click={startProject} disabled={isLoading || !projectTitle.trim() || !protagonistName.trim()}>
          {isLoading ? 'Starting...' : 'Start Project'}
        </button>
      </div>
    {:else}
      <!-- Chat Messages -->
      <div class="chat-messages">
        {#each messages as msg}
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
            <div class="message-bubble">{msg.text}</div>
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

      <!-- Chat Input -->
      <div class="chat-input">
        <textarea
          bind:value={input}
          on:keydown={handleKeydown}
          placeholder="Ask the Foreman..."
          disabled={isLoading}
          rows="1"
        ></textarea>
        <button class="send-btn" on:click={sendMessage} disabled={isLoading || !input.trim()}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    {/if}
  </div>

  <!-- Splitter -->
  <div
    class="splitter"
    on:mousedown={startDrag}
    class:dragging={isDragging}
  >
    <div class="splitter-handle"></div>
  </div>

  <!-- Live Graph Section (Bottom) -->
  <div class="graph-section" style="height: {100 - chatHeight}%">
    <div class="graph-header">
      <span class="graph-title">Live Graph</span>
      <span class="graph-actions">
        <button class="graph-action" title="Expand">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 3 21 3 21 9"></polyline>
            <polyline points="9 21 3 21 3 15"></polyline>
            <line x1="21" y1="3" x2="14" y2="10"></line>
            <line x1="3" y1="21" x2="10" y2="14"></line>
          </svg>
        </button>
      </span>
    </div>
    <div class="graph-container">
      <LiveGraph />
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

  .header-title {
    display: flex;
    align-items: center;
    gap: var(--space-2);
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

  /* Start Project Form */
  .start-project {
    padding: var(--space-4);
    background: var(--bg-primary);
    flex: 1;
  }

  .start-project-header {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--accent-gold);
    margin-bottom: var(--space-4);
  }

  .form-group {
    margin-bottom: var(--space-3);
  }

  .form-group label {
    display: block;
    font-size: var(--text-xs);
    color: var(--text-secondary);
    margin-bottom: var(--space-1);
  }

  .form-group input {
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    font-family: var(--font-ui);
  }

  .form-group input:focus {
    outline: none;
    border-color: var(--accent-gold);
    box-shadow: 0 0 0 2px var(--accent-gold-muted);
  }

  .form-group input::placeholder {
    color: var(--text-muted);
  }

  .start-btn {
    width: 100%;
    padding: var(--space-2) var(--space-4);
    background: var(--accent-gold);
    border: none;
    border-radius: var(--radius-md);
    color: var(--bg-primary);
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .start-btn:hover:not(:disabled) {
    background: var(--accent-gold-hover);
  }

  .start-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
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

  /* Chat Input */
  .chat-input {
    display: flex;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--bg-tertiary);
    border-top: 1px solid var(--border);
  }

  .chat-input textarea {
    flex: 1;
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

  .chat-input textarea:focus {
    outline: none;
    border-color: var(--accent-cyan);
  }

  .chat-input textarea::placeholder {
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

  /* ============================================
   * SPLITTER
   * ============================================ */
  .splitter {
    height: 6px;
    background: var(--bg-tertiary);
    cursor: row-resize;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background var(--transition-fast);
  }

  .splitter:hover,
  .splitter.dragging {
    background: var(--bg-elevated);
  }

  .splitter-handle {
    width: 40px;
    height: 3px;
    background: var(--border);
    border-radius: var(--radius-full);
  }

  .splitter:hover .splitter-handle,
  .splitter.dragging .splitter-handle {
    background: var(--accent-cyan);
  }

  /* ============================================
   * GRAPH SECTION
   * ============================================ */
  .graph-section {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .graph-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-tertiary);
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
  }

  .graph-title {
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    color: var(--text-secondary);
    letter-spacing: 0.5px;
  }

  .graph-actions {
    display: flex;
    gap: var(--space-1);
  }

  .graph-action {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .graph-action:hover {
    background: var(--bg-elevated);
    color: var(--text-secondary);
  }

  .graph-container {
    flex: 1;
    background: var(--bg-primary);
    overflow: hidden;
  }
</style>
