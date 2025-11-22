<script>
  import { onMount } from "svelte";
  import { editorContent } from '$lib/stores';

  let agents = [];
  let selectedNames = new Set();
  let isSetupMode = false;
  let topic = "A cyberpunk detective checks his coffee maker";
  let status = "idle"; 
  let error = "";

  const API_URL = "http://127.0.0.1:8000";

  onMount(async () => {
    try {
      const res = await fetch(`${API_URL}/agents`, { mode: 'cors' }); // Force CORS mode
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      agents = data.agents.map(a => ({ ...a, status: 'ready' }));
      
      // Select first 3 by default if nothing selected
      if (agents.length > 0 && selectedNames.size === 0) {
        agents.slice(0, 3).forEach(a => selectedNames.add(a.name));
        selectedNames = selectedNames;
      }
    } catch (e) {
      console.error("Agent fetch failed:", e);
      error = `Backend offline (${e.message}). Is api.py running?`;
    }
  });

  function toggleAgent(name) {
    if (selectedNames.has(name)) selectedNames.delete(name);
    else selectedNames.add(name);
    selectedNames = selectedNames;
  }

  async function runTournament() {
    if (selectedNames.size === 0) { error = "Select at least one agent."; return; }
    status = "running";
    
    agents = agents.map(a => ({ ...a, status: selectedNames.has(a.name) ? 'working' : 'ready' }));

    try {
      const res = await fetch(`${API_URL}/tournament`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, selected_agents: Array.from(selectedNames) })
      });

      if (!res.ok) throw new Error("Tournament failed");
      const result = await res.json();
      
      const report = `🏆 TOURNAMENT REPORT: ${topic}\n` +
                     `-----------------------------------\n` +
                     `${result.verdict}\n\n` +
                     `-----------------------------------\n` +
                     `       FULL SUBMISSIONS\n` +
                     `-----------------------------------\n\n` +
                     (result.full_story || "No text returned.");
      
      editorContent.set(report);
      status = "finished";
      agents = agents.map(a => ({ ...a, status: 'ready' }));
    } catch (e) {
      error = e.message;
      status = "idle";
    }
  }
</script>

<div class="agent-panel">
  <div class="header-row">
    <div class="title-group">
      <h3>{isSetupMode ? "Setup Squad" : "Your Squad"}</h3>
      <!-- Debug Counter to confirm data exists -->
      <span class="badge">{isSetupMode ? agents.length : selectedNames.size}</span>
    </div>
    <button class="icon-btn" on:click={() => isSetupMode = !isSetupMode}>
      {isSetupMode ? "✅ Done" : "⚙️ Setup"}
    </button>
  </div>
  
  {#if error} <div class="error">{error}</div> {/if}

  <div class="agent-list">
    {#each agents as agent}
      <button
        type="button"
        disabled={!isSetupMode}
        class={`agent-card ${selectedNames.has(agent.name) ? 'selected' : ''} ${isSetupMode ? 'clickable' : ''}`} 
        on:click={() => isSetupMode && toggleAgent(agent.name)}>
        
        <div class="icon-area">
          {#if isSetupMode}
            <div class="checkbox">{selectedNames.has(agent.name) ? '☑️' : '⬜'}</div>
          {:else}
            <div class="status-indicator {agent.status}"></div>
          {/if}
        </div>

        <div class="info">
          <strong>{agent.nickname || agent.name}</strong>
          <span class="provider">{agent.provider}</span>
          {#if agent.role}
            <small>{agent.role}</small>
          {/if}
        </div>
      </button>
    {/each}
  </div>

  {#if !isSetupMode}
    <div class="controls">
      <label>Topic: <input bind:value={topic} placeholder="Enter a prompt..." /></label>
      <button class="run-btn" on:click={runTournament} disabled={status === 'running'}>
        {status === 'running' ? 'Agents Writing...' : 'Run Tournament'}
      </button>
    </div>
  {/if}
</div>

<style>
  .agent-panel { 
    width: 300px; 
    background: #f9fafb; 
    border-left: 1px solid #e5e7eb; 
    display: flex; 
    flex-direction: column; 
    height: 100vh; /* Force full height */
    font-family: sans-serif; 
  }

  .header-row { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    padding: 1rem; 
    border-bottom: 1px solid #e5e7eb; 
    background: white;
    flex-shrink: 0;
  }
  
  .title-group { display: flex; align-items: center; gap: 0.5rem; }
  h3 { margin: 0; font-size: 0.9rem; color: #374151; }
  .badge { background: #e5e7eb; padding: 2px 6px; border-radius: 10px; font-size: 0.75rem; font-weight: bold; color: #4b5563; }

  .icon-btn { background: none; border: 1px solid #e5e7eb; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
  .icon-btn:hover { background: #f3f4f6; }

  .error { margin: 0.5rem; color: #ef4444; font-size: 0.8rem; background: #fee2e2; padding: 0.5rem; border-radius: 4px;}

  /* The scrollable list area */
  .agent-list { 
    flex: 1; 
    overflow-y: auto; 
    padding: 0.5rem; 
    min-height: 0; /* Crucial for flex scrolling */
  }

  .agent-card { 
    background: white; 
    padding: 0.75rem; 
    border-radius: 6px; 
    border: 1px solid #e5e7eb; 
    display: flex; 
    align-items: center; 
    gap: 0.75rem; 
    margin-bottom: 0.5rem; 
  }
  
  .agent-card { width: 100%; text-align: left; border: 1px solid #e5e7eb; }
  .agent-card:disabled { cursor: default; opacity: 1; }
  .agent-card:focus-visible { outline: 2px solid #2563eb; }
  .agent-card.clickable { cursor: pointer; }
  .agent-card.clickable:hover { border-color: #93c5fd; }
  .agent-card.selected { border-color: #2563eb; background-color: #eff6ff; }

  .icon-area { width: 24px; display: flex; justify-content: center; flex-shrink: 0; }
  
  .status-indicator { width: 8px; height: 8px; border-radius: 50%; background: #d1d5db; }
  .status-indicator.ready { background: #10b981; }
  .status-indicator.working { background: #fbbf24; animation: pulse 1s infinite; }
  
  .checkbox { font-size: 1.1rem; }

  .info { display: flex; flex-direction: column; font-size: 0.85rem; overflow: hidden; }
  .info strong { font-weight: 600; color: #111827; }
  .info span.provider { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; }
  .info small { font-size: 0.65rem; color: #9ca3af; }

  .controls { 
    padding: 1rem; 
    border-top: 1px solid #e5e7eb; 
    background: white; 
    display: flex; 
    flex-direction: column; 
    gap: 0.75rem; 
    flex-shrink: 0; 
  }
  
  label { font-size: 0.85rem; font-weight: bold; color: #374151; display: flex; flex-direction: column; gap: 0.25rem; }
  input { padding: 0.6rem; border: 1px solid #d1d5db; border-radius: 4px; width: 100%; box-sizing: border-box; margin-top: 0.25rem;}
  
  .run-btn { background: #2563eb; color: white; border: none; padding: 0.75rem; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; }
  .run-btn:hover { background: #1d4ed8; }
  .run-btn:disabled { background: #93c5fd; cursor: wait; }

  @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>