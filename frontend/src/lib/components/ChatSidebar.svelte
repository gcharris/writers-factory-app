<script>
  import { onMount } from 'svelte';

  let messages = [
    { role: 'system', text: 'Manager online. I have access to your local files.' }
  ];
  let input = "";
  let status = "checking...";
  let modelName = "";
  const API_URL = "http://127.0.0.1:8000";

  onMount(async () => {
    try {
      const res = await fetch(`${API_URL}/manager/status`);
      const data = await res.json();
      status = data.status === "active" ? "Online" : "Offline (Check Ollama)";
      modelName = data.model || "";
    } catch (e) {
      status = "Backend Offline";
    }
  });

  async function sendMessage() {
    if (!input.trim()) return;
    
    // Optimistic UI update
    const userMsg = { role: 'user', text: input };
    messages = [...messages, userMsg];
    const currentInput = input;
    input = "";

    try {
      const res = await fetch(`${API_URL}/manager/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput })
      });
      const data = await res.json();
      
      messages = [...messages, { role: 'assistant', text: data.response }];
    } catch (e) {
      messages = [...messages, { role: 'system', text: `Error: ${e.message}` }];
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
    <h3>Manager</h3>
    <div class="status">
      <span class="dot {status === 'Online' ? 'green' : 'red'}"></span>
      <span>{status} {modelName ? `(${modelName})` : ''}</span>
    </div>
  </div>

  <div class="chat-area">
    {#each messages as msg}
      <div class="message {msg.role}">
        <div class="bubble">{msg.text}</div>
      </div>
    {/each}
  </div>

  <div class="input-area">
    <textarea 
      bind:value={input} 
      on:keydown={handleKeydown}
      placeholder="Ask the Manager..."
    ></textarea>
    <button on:click={sendMessage}>Send</button>
  </div>
</div>

<style>
  .sidebar {
    width: 300px;
    background: #1e1e1e;
    border-left: 1px solid #333;
    display: flex;
    flex-direction: column;
    color: #fff;
    font-family: sans-serif;
    height: 100%;
  }

  .header {
    padding: 1rem;
    border-bottom: 1px solid #333;
    background: #252526;
  }

  h3 { margin: 0 0 0.5rem 0; font-size: 1rem; }

  .status {
    font-size: 0.8rem;
    color: #aaa;
    display: flex;
    align-items: center;
    gap: 0.5rem;
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
  .message.system { justify-content: center; font-size: 0.8rem; color: #666; }

  .bubble {
    max-width: 85%;
    padding: 0.8rem;
    border-radius: 8px;
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .user .bubble { background: #007acc; color: white; }
  .assistant .bubble { background: #333; color: #ddd; }

  .input-area {
    padding: 1rem;
    border-top: 1px solid #333;
    display: flex;
    gap: 0.5rem;
    background: #252526;
  }

  textarea {
    flex: 1;
    background: #3c3c3c;
    border: 1px solid #555;
    color: white;
    padding: 0.5rem;
    border-radius: 4px;
    resize: none;
    height: 40px;
    font-family: inherit;
  }

  textarea:focus { outline: 1px solid #007acc; }

  button {
    background: #007acc;
    color: white;
    border: none;
    padding: 0 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
  
  button:hover { background: #0062a3; }
</style>

