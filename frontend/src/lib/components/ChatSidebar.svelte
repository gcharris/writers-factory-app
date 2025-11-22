<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { sessionId, chatHistory, sessionSceneId, sessionInitialized, sessionError, activeFile } from '$lib/stores';

  let messages = [];
  let input = "";
  let status = "checking...";
  let modelName = "";
  let isLoading = false;
  const API_URL = "http://127.0.0.1:8000";

  // Subscribe to stores
  $: currentSessionId = $sessionId;
  $: currentSceneId = $sessionSceneId;

  // Sync messages with chatHistory store
  $: {
    if ($chatHistory.length > 0) {
      messages = $chatHistory;
    }
  }

  onMount(async () => {
    // Check backend status
    try {
      const res = await fetch(`${API_URL}/manager/status`);
      const data = await res.json();
      status = data.status === "online" ? "Online" : "Offline (Check Ollama)";
      modelName = data.model || "";
    } catch (e) {
      status = "Backend Offline";
    }

    // Initialize or restore session
    await initializeSession();
  });

  /**
   * Initialize session: either restore existing or create new
   */
  async function initializeSession() {
    try {
      if (currentSessionId) {
        // Existing session - load history from backend
        console.log(`Restoring session: ${currentSessionId}`);
        const historyData = await apiClient.getSessionHistory(currentSessionId);

        // Convert backend events to UI format
        const loadedMessages = historyData.events
          .filter(e => e.role !== 'system' || e.content !== 'Session started')
          .map(e => ({
            role: e.role,
            text: e.content,
            id: e.id
          }));

        if (loadedMessages.length > 0) {
          messages = loadedMessages;
          chatHistory.set(loadedMessages);
        } else {
          // Session exists but empty, add welcome message
          messages = [{ role: 'system', text: 'Manager online. Session restored.' }];
        }

        sessionInitialized.set(true);
        console.log(`Loaded ${loadedMessages.length} messages from session`);
      } else {
        // No session - create new one
        await createNewSession();
      }
    } catch (e) {
      console.error('Session initialization failed:', e);
      sessionError.set(e.message);

      // Graceful degradation: still allow chat even if session API fails
      messages = [{ role: 'system', text: 'Manager online. (Session persistence unavailable)' }];
      sessionInitialized.set(true);
    }
  }

  /**
   * Create a new session and store the ID
   */
  async function createNewSession() {
    try {
      // Get scene context from active file if available
      let sceneContext = null;
      if ($activeFile && $activeFile.includes('scene')) {
        sceneContext = $activeFile;
      }

      const result = await apiClient.createSession(sceneContext);
      sessionId.set(result.session_id);
      if (result.scene_id) {
        sessionSceneId.set(result.scene_id);
      }

      messages = [{ role: 'system', text: 'Manager online. New session created.' }];
      chatHistory.set(messages);
      sessionInitialized.set(true);

      console.log(`Created new session: ${result.session_id}`);
    } catch (e) {
      console.error('Failed to create session:', e);
      sessionError.set(e.message);
      messages = [{ role: 'system', text: 'Manager online. (Offline mode)' }];
      sessionInitialized.set(true);
    }
  }

  /**
   * Start a fresh session (clear history)
   */
  async function newSession() {
    sessionId.set(null);
    sessionSceneId.set(null);
    messages = [];
    chatHistory.set([]);
    await createNewSession();
  }

  async function sendMessage() {
    if (!input.trim() || isLoading) return;

    isLoading = true;
    const currentInput = input;
    input = "";

    // Optimistic UI update
    const userMsg = { role: 'user', text: currentInput };
    messages = [...messages, userMsg];

    // Log user message to backend (fire and forget for speed)
    if (currentSessionId) {
      apiClient.logMessage(currentSessionId, 'user', currentInput, currentSceneId)
        .catch(e => console.warn('Failed to log user message:', e));
    }

    try {
      const res = await fetch(`${API_URL}/manager/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput })
      });
      const data = await res.json();

      const assistantMsg = { role: 'assistant', text: data.response };
      messages = [...messages, assistantMsg];

      // Log assistant message to backend
      if (currentSessionId) {
        apiClient.logMessage(currentSessionId, 'assistant', data.response, currentSceneId)
          .catch(e => console.warn('Failed to log assistant message:', e));
      }
    } catch (e) {
      const errorMsg = { role: 'system', text: `Error: ${e.message}` };
      messages = [...messages, errorMsg];
    } finally {
      isLoading = false;
      // Sync to store
      chatHistory.set(messages);
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }
</script>

<div class="sidebar">
  <div class="header">
    <div class="header-row">
      <h3>Manager</h3>
      <button class="new-btn" on:click={newSession} title="Start new session">New</button>
    </div>
    <div class="status">
      <span class="dot {status === 'Online' ? 'green' : 'red'}"></span>
      <span>{status} {modelName ? `(${modelName})` : ''}</span>
    </div>
    {#if currentSessionId}
      <div class="session-info">Session: {currentSessionId.substring(0, 8)}...</div>
    {/if}
  </div>

  <div class="chat-area">
    {#each messages as msg}
      <div class="message {msg.role}">
        <div class="bubble">{msg.text}</div>
      </div>
    {/each}
    {#if isLoading}
      <div class="message assistant">
        <div class="bubble loading">Thinking...</div>
      </div>
    {/if}
  </div>

  <div class="input-area">
    <textarea
      bind:value={input}
      on:keydown={handleKeydown}
      placeholder="Ask the Manager..."
      disabled={isLoading}
    ></textarea>
    <button on:click={sendMessage} disabled={isLoading}>
      {isLoading ? '...' : 'Send'}
    </button>
  </div>
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

  h3 { margin: 0 0 0.5rem 0; font-size: 1rem; }

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

  .session-info {
    font-size: 0.7rem;
    color: #9ca3af;
    margin-top: 0.25rem;
    font-family: monospace;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  .green { background: #4caf50; }
  .red { background: #f44336; }

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
  }

  .bubble.loading {
    opacity: 0.7;
    animation: pulse 1s infinite;
  }

  .user .bubble { background: #2563eb; color: white; }
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

  textarea:focus { outline: 1px solid #2563eb; }
  textarea:disabled { opacity: 0.6; }

  button {
    background: #2563eb;
    color: white;
    border: none;
    padding: 0 1rem;
    border-radius: 4px;
    cursor: pointer;
  }

  button:hover { background: #1d4ed8; }
  button:disabled { background: #93c5fd; cursor: wait; }

  @keyframes pulse {
    0% { opacity: 0.7; }
    50% { opacity: 0.4; }
    100% { opacity: 0.7; }
  }
</style>
