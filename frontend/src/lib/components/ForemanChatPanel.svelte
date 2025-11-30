<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    foremanActive, foremanMode, foremanProjectTitle, foremanProtagonist,
    foremanWorkOrder, foremanChatHistory, selectedChatModel, defaultChatModel
  } from '$lib/stores';
  import ModelSelector from './chat/ModelSelector.svelte';
  import ForemanAction from './chat/ForemanAction.svelte';

  const BASE_URL = 'http://localhost:8000';

  let messages = [];
  let input = "";
  let status = "checking...";
  let isLoading = false;
  let showStartProject = false;
  let projectTitle = "";
  let protagonistName = "";
  let kbStats = null;

  // Model routing display
  let showModelRouting = false;
  let currentModelUsed: string | null = null;
  let routingReason: string | null = null;

  // Orchestrator status
  let orchestratorEnabled = false;
  let qualityTier: string | null = null;

  // Sync messages with Foreman chat history
  $: {
    if ($foremanChatHistory.length > 0) {
      messages = $foremanChatHistory;
    }
  }

  onMount(async () => {
    await checkForemanStatus();
    await checkOrchestratorStatus();

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
      status = "Backend Offline";
    }
  }

  async function checkOrchestratorStatus() {
    try {
      const response = await fetch(`${BASE_URL}/settings/category/orchestrator`);
      if (response.ok) {
        const data = await response.json();
        orchestratorEnabled = data.enabled || false;
        qualityTier = data.quality_tier || 'balanced';
      }
    } catch (e) {
      console.warn('Failed to check orchestrator status:', e);
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
      currentModelUsed = null;
      routingReason = null;
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
        text: `Foreman initialized in ${result.mode.toUpperCase()} mode for "${result.project_title}" with protagonist ${result.protagonist_name}.`
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

    // Get the model to use for this message
    const modelToUse = $selectedChatModel || $defaultChatModel;

    const userMsg = { role: 'user', text: currentInput, modelRequested: modelToUse };
    messages = [...messages, userMsg];

    // Reset selected model after sending (per-message selection)
    selectedChatModel.set(null);

    try {
      const data = await apiClient.foremanChat(currentInput, modelToUse);

      // Extract model routing information if available
      if (data.model_used) {
        currentModelUsed = data.model_used;
        routingReason = data.routing_reason || null;
      }

      const assistantMsg = {
        role: 'assistant',
        text: data.response,
        modelUsed: data.model_used,
        // Store full action objects for rich rendering
        actions: data.actions || [],
      };
      messages = [...messages, assistantMsg];

      if (data.work_order_status) {
        foremanWorkOrder.set(data.work_order_status);
      }

      // Note: We now render actions inline with the assistant message
      // using the ForemanAction component, instead of as a separate system message

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

  function getModeColor(mode: string): string {
    switch (mode) {
      case 'ARCHITECT': return '#ffb000';
      case 'VOICE': return '#00ff88';
      case 'DIRECTOR': return '#00d9ff';
      default: return '#888888';
    }
  }

  function getModeIcon(mode: string): string {
    switch (mode) {
      case 'ARCHITECT': return '📐';
      case 'VOICE': return '🎤';
      case 'DIRECTOR': return '🎬';
      default: return '💤';
    }
  }

  function getTierBadgeColor(tier: string): string {
    switch (tier) {
      case 'budget': return '#888888';
      case 'balanced': return '#00d9ff';
      case 'premium': return '#ffb000';
      default: return '#888888';
    }
  }

  function formatModelName(modelName: string): string {
    // Shorten long model names for display
    if (modelName.length > 30) {
      return modelName.substring(0, 27) + '...';
    }
    return modelName;
  }
</script>

<div class="foreman-chat-panel">
  <!-- Header -->
  <div class="panel-header">
    <div class="header-top">
      <div class="title-section">
        <h3>
          {#if $foremanMode}
            <span class="mode-icon" style="color: {getModeColor($foremanMode)};">
              {getModeIcon($foremanMode)}
            </span>
          {/if}
          Foreman
        </h3>
        {#if $foremanMode}
          <span class="mode-badge" style="background-color: {getModeColor($foremanMode)}20; border-color: {getModeColor($foremanMode)}; color: {getModeColor($foremanMode)};">
            {$foremanMode}
          </span>
        {/if}
      </div>

      <div class="header-actions">
        <button
          class="icon-button"
          on:click={() => showModelRouting = !showModelRouting}
          title="Toggle Model Routing"
        >
          <span class="icon">{showModelRouting ? '📊' : '🤖'}</span>
        </button>
        <button
          class="icon-button"
          on:click={newProject}
          title="Start New Project"
        >
          <span class="icon">🔄</span>
        </button>
      </div>
    </div>

    <div class="status-bar">
      <div class="status-indicator">
        <span class="dot {status === 'Online' ? 'green' : status === 'Ready' ? 'yellow' : 'red'}"></span>
        <span class="status-text">{status}</span>
      </div>

      {#if orchestratorEnabled && qualityTier}
        <div class="tier-indicator" style="border-color: {getTierBadgeColor(qualityTier)};">
          <span class="tier-icon">⚡</span>
          <span class="tier-text" style="color: {getTierBadgeColor(qualityTier)};">
            {qualityTier.charAt(0).toUpperCase() + qualityTier.slice(1)}
          </span>
        </div>
      {/if}
    </div>

    {#if $foremanProjectTitle}
      <div class="project-info">
        <span class="project-icon">📁</span>
        <span class="project-title">{$foremanProjectTitle}</span>
        <span class="separator">|</span>
        <span class="protagonist-name">{$foremanProtagonist}</span>
      </div>
    {/if}
  </div>

  <!-- Model Routing Panel (collapsible) -->
  {#if showModelRouting && currentModelUsed}
    <div class="model-routing-panel">
      <div class="routing-header">
        <span class="routing-icon">🎯</span>
        <span class="routing-title">Model Routing</span>
      </div>
      <div class="routing-info">
        <div class="routing-row">
          <span class="routing-label">Model:</span>
          <span class="routing-value">{formatModelName(currentModelUsed)}</span>
        </div>
        {#if routingReason}
          <div class="routing-row">
            <span class="routing-label">Reason:</span>
            <span class="routing-reason">{routingReason}</span>
          </div>
        {/if}
        {#if orchestratorEnabled}
          <div class="routing-note">
            ⚡ Orchestrator is active - automatic model selection based on {qualityTier} tier
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- Work Order Status -->
  {#if $foremanWorkOrder}
    <div class="work-order">
      <div class="work-order-header">
        <span class="work-order-icon">📋</span>
        <span class="work-order-title">Work Order</span>
      </div>

      <div class="templates-list">
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
            {#if template.completed_fields}
              <span class="template-progress">
                ({template.completed_fields.length}/{template.required_fields.length})
              </span>
            {/if}
          </div>
        {/each}
      </div>

      {#if kbStats && kbStats.total_entries > 0}
        <div class="kb-stats">
          <span class="kb-icon">🧠</span>
          <span class="kb-label">KB Decisions:</span>
          <span class="kb-count">{kbStats.total_entries}</span>
          <div class="kb-breakdown">
            <span class="kb-category">
              <span class="kb-cat-icon">👤</span>
              {kbStats.by_category.character || 0}
            </span>
            <span class="kb-category">
              <span class="kb-cat-icon">⚠️</span>
              {kbStats.by_category.constraint || 0}
            </span>
            <span class="kb-category">
              <span class="kb-cat-icon">🌍</span>
              {kbStats.by_category.world || 0}
            </span>
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Start Project Form -->
  {#if showStartProject}
    <div class="start-project">
      <h4>Start New Project</h4>
      <p class="start-hint">Begin your journey with the Foreman</p>

      <input
        type="text"
        bind:value={projectTitle}
        placeholder="Project Title (e.g., Big Brain)"
        class="form-input"
        on:keydown={handleKeydown}
        disabled={isLoading}
      />

      <input
        type="text"
        bind:value={protagonistName}
        placeholder="Protagonist Name (e.g., Tobias)"
        class="form-input"
        on:keydown={handleKeydown}
        disabled={isLoading}
      />

      <button
        class="btn-start"
        on:click={startProject}
        disabled={isLoading || !projectTitle.trim() || !protagonistName.trim()}
      >
        {isLoading ? 'Starting...' : 'Start Project'}
      </button>
    </div>
  {/if}

  <!-- Chat Messages -->
  <div class="messages-container">
    {#each messages as msg}
      <div class="message {msg.role}">
        <div class="message-header">
          <span class="message-role">
            {#if msg.role === 'user'}
              👤 You
            {:else if msg.role === 'assistant'}
              🤖 Foreman
            {:else}
              ℹ️ System
            {/if}
          </span>
          {#if msg.role === 'user' && msg.modelRequested}
            <span class="message-model user-model" title="Model requested for this message">
              → {formatModelName(msg.modelRequested)}
            </span>
          {:else if msg.modelUsed}
            <span class="message-model" title="Model used for this response">
              {formatModelName(msg.modelUsed)}
            </span>
          {/if}
        </div>
        <div class="message-content">{msg.text}</div>

        <!-- Render Foreman actions if present -->
        {#if msg.role === 'assistant' && msg.actions && msg.actions.length > 0}
          <div class="message-actions">
            {#each msg.actions as action}
              <ForemanAction {action} />
            {/each}
          </div>
        {/if}
      </div>
    {/each}

    {#if isLoading}
      <div class="message assistant loading">
        <div class="message-header">
          <span class="message-role">🤖 Foreman</span>
        </div>
        <div class="message-content">
          <span class="typing-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </span>
        </div>
      </div>
    {/if}
  </div>

  <!-- Chat Input -->
  {#if !showStartProject}
    <div class="chat-input">
      <div class="input-row">
        <ModelSelector />
        <textarea
          bind:value={input}
          on:keydown={handleKeydown}
          placeholder="Chat with Foreman..."
          class="input-field"
          disabled={isLoading}
          rows="2"
        />
        <button
          class="btn-send"
          on:click={sendMessage}
          disabled={isLoading || !input.trim()}
        >
          <span class="icon">➤</span>
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .foreman-chat-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #1a1a1a;
    color: #ffffff;
  }

  /* Header */
  .panel-header {
    flex-shrink: 0;
    background: #2d2d2d;
    border-bottom: 1px solid #404040;
  }

  .header-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
  }

  .title-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .title-section h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .mode-icon {
    font-size: 1.25rem;
  }

  .mode-badge {
    padding: 0.25rem 0.75rem;
    border: 1px solid;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
  }

  .icon-button {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .icon-button:hover {
    background: #252525;
    border-color: #00d9ff;
  }

  .icon {
    font-size: 1rem;
  }

  .status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    background: #252525;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .dot.green {
    background: #00ff88;
    box-shadow: 0 0 8px #00ff8860;
  }

  .dot.yellow {
    background: #ffb000;
    box-shadow: 0 0 8px #ffb00060;
  }

  .dot.red {
    background: #ff4444;
    box-shadow: 0 0 8px #ff444460;
  }

  .status-text {
    font-size: 0.875rem;
    color: #b0b0b0;
  }

  .tier-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.75rem;
    background: #1a1a1a;
    border: 1px solid;
    border-radius: 4px;
  }

  .tier-icon {
    font-size: 0.875rem;
  }

  .tier-text {
    font-size: 0.75rem;
    font-weight: 600;
  }

  .project-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #1a1a1a;
    font-size: 0.875rem;
    color: #b0b0b0;
  }

  .project-icon {
    font-size: 1rem;
  }

  .project-title {
    color: #00d9ff;
    font-weight: 500;
  }

  .separator {
    color: #404040;
  }

  .protagonist-name {
    color: #ffffff;
  }

  /* Model Routing Panel */
  .model-routing-panel {
    background: #2d2d2d;
    border-bottom: 1px solid #404040;
    padding: 0.75rem 1rem;
  }

  .routing-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .routing-icon {
    font-size: 1rem;
  }

  .routing-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #00d9ff;
  }

  .routing-info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .routing-row {
    display: flex;
    gap: 0.5rem;
    font-size: 0.875rem;
  }

  .routing-label {
    color: #888888;
    min-width: 60px;
  }

  .routing-value {
    color: #00d9ff;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
  }

  .routing-reason {
    color: #b0b0b0;
    flex: 1;
  }

  .routing-note {
    font-size: 0.75rem;
    color: #888888;
    font-style: italic;
    margin-top: 0.25rem;
  }

  /* Work Order */
  .work-order {
    background: #2d2d2d;
    border-bottom: 1px solid #404040;
    padding: 0.75rem 1rem;
  }

  .work-order-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .work-order-icon {
    font-size: 1rem;
  }

  .work-order-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #00d9ff;
  }

  .templates-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .template-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: #1a1a1a;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .template-item.complete {
    border-left: 3px solid #00ff88;
  }

  .template-item.partial {
    border-left: 3px solid #ffb000;
  }

  .template-item.pending {
    border-left: 3px solid #404040;
  }

  .template-icon {
    font-size: 1rem;
  }

  .template-name {
    flex: 1;
    color: #ffffff;
  }

  .template-progress {
    color: #888888;
    font-size: 0.75rem;
  }

  .kb-stats {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: #1a1a1a;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .kb-icon {
    font-size: 1rem;
  }

  .kb-label {
    color: #888888;
  }

  .kb-count {
    color: #00d9ff;
    font-weight: 600;
  }

  .kb-breakdown {
    display: flex;
    gap: 0.75rem;
    margin-left: auto;
  }

  .kb-category {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    color: #b0b0b0;
  }

  .kb-cat-icon {
    font-size: 0.875rem;
  }

  /* Start Project Form */
  .start-project {
    padding: 1.5rem;
    background: #2d2d2d;
    border-bottom: 1px solid #404040;
  }

  .start-project h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #00d9ff;
  }

  .start-hint {
    margin: 0 0 1rem 0;
    font-size: 0.875rem;
    color: #888888;
  }

  .form-input {
    width: 100%;
    padding: 0.75rem;
    margin-bottom: 0.75rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
    font-size: 0.875rem;
  }

  .form-input:focus {
    outline: none;
    border-color: #00d9ff;
  }

  .form-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-start {
    width: 100%;
    padding: 0.75rem;
    background: #00d9ff;
    color: #1a1a1a;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-start:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-start:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Messages */
  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .message {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.75rem;
    border-radius: 8px;
  }

  .message.user {
    background: #00d9ff20;
    border-left: 3px solid #00d9ff;
    margin-left: 1rem;
  }

  .message.assistant {
    background: #2d2d2d;
    border-left: 3px solid #00ff88;
  }

  .message.system {
    background: #1a1a1a;
    border-left: 3px solid #ffb000;
    font-size: 0.875rem;
  }

  .message-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .message-role {
    color: #b0b0b0;
  }

  .message-model {
    color: #888888;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
  }

  .message-model.user-model {
    color: #00d9ff;
  }

  .message-content {
    color: #ffffff;
    line-height: 1.6;
    white-space: pre-wrap;
  }

  .message-actions {
    margin-top: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .typing-indicator {
    display: flex;
    gap: 0.25rem;
  }

  .typing-indicator .dot {
    width: 8px;
    height: 8px;
    background: #00ff88;
    border-radius: 50%;
    animation: typing 1.4s infinite;
  }

  .typing-indicator .dot:nth-child(2) {
    animation-delay: 0.2s;
  }

  .typing-indicator .dot:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes typing {
    0%, 60%, 100% {
      opacity: 0.3;
      transform: scale(0.8);
    }
    30% {
      opacity: 1;
      transform: scale(1);
    }
  }

  /* Chat Input */
  .chat-input {
    padding: 0.75rem 1rem;
    background: #2d2d2d;
    border-top: 1px solid #404040;
    flex-shrink: 0;
  }

  .input-row {
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;
  }

  .input-field {
    flex: 1;
    padding: 0.75rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
    font-family: inherit;
    font-size: 0.875rem;
    resize: none;
  }

  .input-field:focus {
    outline: none;
    border-color: #00d9ff;
  }

  .input-field:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-send {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #00d9ff;
    border: none;
    border-radius: 4px;
    color: #1a1a1a;
    font-size: 1.25rem;
    cursor: pointer;
    transition: background 0.2s;
    flex-shrink: 0;
  }

  .btn-send:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-send:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Scrollbar */
  .messages-container::-webkit-scrollbar {
    width: 8px;
  }

  .messages-container::-webkit-scrollbar-track {
    background: #1a1a1a;
  }

  .messages-container::-webkit-scrollbar-thumb {
    background: #404040;
    border-radius: 4px;
  }

  .messages-container::-webkit-scrollbar-thumb:hover {
    background: #505050;
  }
</style>
