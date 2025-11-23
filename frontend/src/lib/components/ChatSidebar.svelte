<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    foremanActive, foremanMode, foremanProjectTitle, foremanProtagonist,
    foremanWorkOrder, foremanChatHistory
  } from '$lib/stores';

  let messages = [];
  let input = "";
  let status = "checking...";
  let isLoading = false;
  let showStartProject = false;
  let projectTitle = "";
  let protagonistName = "";
  let kbStats = null; // KB decision stats

  // Sync messages with Foreman chat history
  $: {
    if ($foremanChatHistory.length > 0) {
      messages = $foremanChatHistory;
    }
  }

  onMount(async () => {
    // Check Foreman status on load
    await checkForemanStatus();

    // If no active project, show start form
    if (!$foremanActive) {
      showStartProject = true;
    }
  });

  /**
   * Check if Foreman has an active project
   */
  async function checkForemanStatus() {
    try {
      const result = await apiClient.foremanStatus();
      foremanActive.set(result.active);
      status = result.active ? "Online" : "Ready";

      if (result.active && result.work_order) {
        foremanMode.set(result.mode);
        foremanProjectTitle.set(result.work_order.project_title);
        foremanProtagonist.set(result.work_order.protagonist_name);

        // Transform templates to UI format
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

        // Store KB stats if available
        if (result.kb_stats) {
          kbStats = result.kb_stats;
        }
      }
    } catch (e) {
      console.warn('Failed to check Foreman status:', e);
      status = "Backend Offline";
    }
  }

  /**
   * Reset Foreman and start fresh
   */
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

  /**
   * Start a new Foreman project
   */
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

      // Add welcome message
      const welcomeMsg = {
        role: 'system',
        text: `Foreman initialized in ${result.mode.toUpperCase()} mode for "${result.project_title}" with protagonist ${result.protagonist_name}.`
      };
      messages = [welcomeMsg];
      foremanChatHistory.set(messages);

      // Check full status to get work order
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

    // Optimistic UI update
    const userMsg = { role: 'user', text: currentInput };
    messages = [...messages, userMsg];

    try {
      const data = await apiClient.foremanChat(currentInput);

      const assistantMsg = { role: 'assistant', text: data.response };
      messages = [...messages, assistantMsg];

      // Update work order status if provided
      if (data.work_order_status) {
        foremanWorkOrder.set(data.work_order_status);
      }

      // Show executed actions if any
      if (data.actions_executed && data.actions_executed.length > 0) {
        const actionsMsg = {
          role: 'system',
          text: `Actions: ${data.actions_executed.join(', ')}`
        };
        messages = [...messages, actionsMsg];
      }

      // Refresh KB stats after chat (Foreman may have saved decisions)
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
</script>

<div class="sidebar">
  <div class="header">
    <div class="header-row">
      <h3>Foreman</h3>
      <button class="new-btn" on:click={newProject} title="Start new project">New</button>
    </div>
    <div class="status">
      <span class="dot {status === 'Online' ? 'green' : status === 'Ready' ? 'yellow' : 'red'}"></span>
      <span>{status}</span>
      {#if $foremanMode}
        <span class="mode-badge">{$foremanMode.toUpperCase()}</span>
      {/if}
    </div>
    {#if $foremanProjectTitle}
      <div class="project-info">
        {$foremanProjectTitle} | {$foremanProtagonist}
      </div>
    {/if}
  </div>

  <!-- Work Order Status -->
  {#if $foremanWorkOrder}
    <div class="work-order">
      <div class="work-order-title">Work Order</div>
      {#each $foremanWorkOrder.templates || [] as template}
        <div class="template-item {template.status}">
          <span class="template-icon">
            {#if template.status === 'complete'}
              ✓
            {:else if template.status === 'partial'}
              ◐
            {:else}
              ○
            {/if}
          </span>
          <span class="template-name">{template.name}</span>
        </div>
      {/each}

      <!-- KB Stats -->
      {#if kbStats && kbStats.total_entries > 0}
        <div class="kb-stats">
          <span class="kb-label">KB Decisions:</span>
          <span class="kb-count">{kbStats.total_entries}</span>
          <span class="kb-breakdown">
            ({kbStats.by_category.character || 0} char,
            {kbStats.by_category.constraint || 0} const,
            {kbStats.by_category.world || 0} world)
          </span>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Start Project Form -->
  {#if showStartProject}
    <div class="start-project">
      <h4>Start New Project</h4>
      <input
        type="text"
        bind:value={projectTitle}
        placeholder="Project Title (e.g., Big Brain)"
        on:keydown={handleKeydown}
      />
      <input
        type="text"
        bind:value={protagonistName}
        placeholder="Protagonist Name (e.g., Mickey Bardot)"
        on:keydown={handleKeydown}
      />
      <button on:click={startProject} disabled={isLoading || !projectTitle.trim() || !protagonistName.trim()}>
        {isLoading ? 'Starting...' : 'Start Project'}
      </button>
    </div>
  {/if}

  <div class="chat-area">
    {#each messages as msg}
      <div class="message {msg.role}">
        <div class="bubble">{msg.text}</div>
      </div>
    {/each}
    {#if isLoading}
      <div class="message assistant">
        <div class="bubble loading">Foreman thinking...</div>
      </div>
    {/if}
  </div>

  {#if !showStartProject}
    <div class="input-area">
      <textarea
        bind:value={input}
        on:keydown={handleKeydown}
        placeholder="Chat with the Foreman..."
        disabled={isLoading}
      ></textarea>
      <button on:click={sendMessage} disabled={isLoading}>
        {isLoading ? '...' : 'Send'}
      </button>
    </div>
  {/if}
</div>

<style>
  .sidebar {
    width: 100%;
    height: 100%;
    background: #f8fafc;
    border-left: 1px solid #e5e7eb;
    display: flex;
    flex-direction: column;
    color: #111827;
    font-family: sans-serif;
  }

  .header {
    padding: 1rem;
    border-bottom: 1px solid #e5e7eb;
    background: #ffffff;
  }

  .header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #8b5cf6;
  }

  .new-btn {
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    cursor: pointer;
    color: #374151;
  }

  .new-btn:hover {
    background: #e5e7eb;
  }

  .status {
    font-size: 0.8rem;
    color: #6b7280;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .mode-badge {
    background: #8b5cf6;
    color: white;
    padding: 0.1rem 0.4rem;
    border-radius: 3px;
    font-size: 0.65rem;
    font-weight: 600;
  }

  .project-info {
    font-size: 0.75rem;
    color: #8b5cf6;
    margin-top: 0.25rem;
    font-family: monospace;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  .green { background: #4caf50; }
  .yellow { background: #f59e0b; }
  .red { background: #f44336; }

  /* Work Order Panel */
  .work-order {
    padding: 0.75rem 1rem;
    background: #faf5ff;
    border-bottom: 1px solid #e9d5ff;
    font-size: 0.8rem;
  }

  .work-order-title {
    font-weight: 600;
    color: #7c3aed;
    margin-bottom: 0.5rem;
  }

  .template-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0;
    color: #6b7280;
  }

  .template-item.complete {
    color: #059669;
  }

  .template-item.partial {
    color: #d97706;
  }

  .template-icon {
    font-size: 0.9rem;
  }

  /* KB Stats */
  .kb-stats {
    margin-top: 0.75rem;
    padding-top: 0.5rem;
    border-top: 1px dashed #e9d5ff;
    font-size: 0.7rem;
    color: #6b7280;
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    align-items: baseline;
  }

  .kb-label {
    color: #7c3aed;
    font-weight: 500;
  }

  .kb-count {
    font-weight: 600;
    color: #059669;
  }

  .kb-breakdown {
    font-size: 0.65rem;
    color: #9ca3af;
  }

  /* Start Project Form */
  .start-project {
    padding: 1rem;
    background: #faf5ff;
    border-bottom: 1px solid #e9d5ff;
  }

  .start-project h4 {
    margin: 0 0 0.75rem 0;
    color: #7c3aed;
    font-size: 0.9rem;
  }

  .start-project input {
    width: 100%;
    padding: 0.5rem;
    margin-bottom: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 0.85rem;
    box-sizing: border-box;
  }

  .start-project input:focus {
    outline: 1px solid #8b5cf6;
    border-color: #8b5cf6;
  }

  .start-project button {
    width: 100%;
    background: #8b5cf6;
    color: white;
    border: none;
    padding: 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
  }

  .start-project button:hover {
    background: #7c3aed;
  }

  .start-project button:disabled {
    background: #c4b5fd;
    cursor: not-allowed;
  }

  .chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .message {
    display: flex;
  }

  .message.user { justify-content: flex-end; }
  .message.assistant { justify-content: flex-start; }
  .message.system { justify-content: center; font-size: 0.8rem; color: #6b7280; }

  .bubble {
    max-width: 85%;
    padding: 0.8rem;
    border-radius: 8px;
    font-size: 0.9rem;
    line-height: 1.4;
    white-space: pre-wrap;
  }

  .bubble.loading {
    opacity: 0.7;
    animation: pulse 1s infinite;
  }

  .user .bubble { background: #8b5cf6; color: white; }
  .assistant .bubble { background: #e5e7eb; color: #111827; }

  .input-area {
    padding: 1rem;
    border-top: 1px solid #e5e7eb;
    display: flex;
    gap: 0.5rem;
    background: #ffffff;
  }

  textarea {
    flex: 1;
    background: #f9fafb;
    border: 1px solid #d1d5db;
    color: #111827;
    padding: 0.5rem;
    border-radius: 4px;
    resize: none;
    height: 40px;
    font-family: inherit;
  }

  textarea:focus { outline: 1px solid #8b5cf6; }
  textarea:disabled { opacity: 0.6; }

  button {
    background: #8b5cf6;
    color: white;
    border: none;
    padding: 0 1rem;
    border-radius: 4px;
    cursor: pointer;
  }

  button:hover { background: #7c3aed; }
  button:disabled { background: #c4b5fd; cursor: wait; }

  @keyframes pulse {
    0% { opacity: 0.7; }
    50% { opacity: 0.4; }
    100% { opacity: 0.7; }
  }
</style>
