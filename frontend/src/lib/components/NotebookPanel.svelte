<script>
  import { onMount } from 'svelte';
  import {
    notebookStatus,
    notebookList,
    selectedNotebookId,
    notebookLoading,
    notebookError,
    notebookResult
  } from '$lib/stores';
  import { get } from 'svelte/store';

  const API_URL = 'http://127.0.0.1:8000';

  let queryText = 'Summarize the most important craft guidance I should keep in mind.';
  let characterName = '';
  let worldAspect = '';
  let entityName = '';
  let entityType = 'character';

  let status = 'checking';
  let notebooks = [];
  let currentNotebook = '';
  let isLoading = false;
  let errorMsg = '';
  let result = null;

  $: status = $notebookStatus;
  $: notebooks = $notebookList;
  $: currentNotebook = $selectedNotebookId;
  $: isLoading = $notebookLoading;
  $: errorMsg = $notebookError;
  $: result = $notebookResult;

  onMount(async () => {
    await Promise.all([fetchStatus(), fetchConfiguredNotebooks()]);
  });

  async function fetchStatus() {
    try {
      const res = await fetch(`${API_URL}/notebooklm/status`);
      const data = await res.json();
      notebookStatus.set(data.status || 'unknown');
    } catch (err) {
      notebookStatus.set('offline');
      notebookError.set('NotebookLM backend offline');
    }
  }

  async function fetchConfiguredNotebooks() {
    try {
      const res = await fetch(`${API_URL}/notebooklm/notebooks`);
      const data = await res.json();
      const list = data.configured || [];
      notebookList.set(list);
      if (list.length > 0 && !get(selectedNotebookId)) {
        selectedNotebookId.set(list[0].id);
      }
    } catch (err) {
      notebookError.set('Failed to load notebooks');
    }
  }

  function selectNotebook(event) {
    selectedNotebookId.set(event.target.value);
  }

  async function runAction(endpoint, payloadBuilder) {
    if (!currentNotebook) {
      notebookError.set('Select a notebook first.');
      return;
    }

    notebookError.set('');
    notebookLoading.set(true);
    notebookResult.set(null);

    try {
      const body = payloadBuilder();
      body.notebook_id = currentNotebook;
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (!res.ok) throw new Error(`Request failed (${res.status})`);

      const data = await res.json();
      notebookResult.set(data);
    } catch (err) {
      notebookError.set(err.message);
    } finally {
      notebookLoading.set(false);
    }
  }
</script>

<div class="notebook-panel">
  <div class="nb-header">
    <div class="title-group">
      <h3>NotebookLM</h3>
      <span class={`status-dot ${status === 'ready' ? 'green' : 'red'}`}></span>
      <span class="status-label">{status}</span>
    </div>
    <button class="refresh-btn" on:click={() => { fetchStatus(); fetchConfiguredNotebooks(); }}>⟳</button>
  </div>

  {#if notebooks.length === 0}
    <div class="empty-state">
      <p>No notebooks configured.</p>
      <p>Add them via backend/notebooklm_config.json</p>
    </div>
  {:else}
    <div class="section">
      <label>
        Notebook
        <select on:change={selectNotebook} bind:value={currentNotebook}>
          {#each notebooks as nb}
            <option value={nb.id}>{nb.label} ({nb.category})</option>
          {/each}
        </select>
      </label>
      {#if notebooks.find(nb => nb.id === currentNotebook)?.description}
        <small class="description">
          {notebooks.find(nb => nb.id === currentNotebook)?.description}
        </small>
      {/if}
    </div>

    <div class="section">
      <label>
        Research Prompt
        <textarea bind:value={queryText}></textarea>
      </label>
      <button class="action-btn" disabled={isLoading} on:click={() => runAction('/notebooklm/query', () => ({ query: queryText }))}>
        {isLoading ? 'Searching…' : 'Run Research Query'}
      </button>
    </div>

    <div class="section two-col">
      <div>
        <label>
          Character Name
          <input bind:value={characterName} placeholder="e.g. Azeem" />
        </label>
        <button disabled={isLoading || !characterName.trim()} on:click={() => runAction('/notebooklm/character-profile', () => ({ character_name: characterName }))}>
          Character Profile
        </button>
      </div>
      <div>
        <label>
          World Aspect
          <input bind:value={worldAspect} placeholder="e.g. AI regulation in 2035" />
        </label>
        <button disabled={isLoading || !worldAspect.trim()} on:click={() => runAction('/notebooklm/world-building', () => ({ aspect: worldAspect }))}>
          World Building
        </button>
      </div>
    </div>

    <div class="section two-col">
      <div>
        <label>
          Entity Name
          <input bind:value={entityName} placeholder="Entity to lookup" />
        </label>
      </div>
      <div>
        <label>
          Entity Type
          <select bind:value={entityType}>
            <option value="character">Character</option>
            <option value="location">Location</option>
            <option value="object">Object</option>
            <option value="other">Other</option>
          </select>
        </label>
      </div>
      <button class="full-btn" disabled={isLoading || !entityName.trim()} on:click={() => runAction('/notebooklm/context', () => ({ entity_name: entityName, entity_type: entityType }))}>
        Quick Context
      </button>
    </div>
  {/if}

  {#if errorMsg}
    <div class="error-box">{errorMsg}</div>
  {/if}

  {#if result}
    <div class="result-box">
      <h4>Response</h4>
      {#if result.answer}
        <p class="answer-text">{result.answer}</p>
      {:else if result.profile}
        <p class="answer-text">{result.profile}</p>
      {:else if result.details}
        <p class="answer-text">{result.details}</p>
      {/if}

      {#if result.sources && result.sources.length}
        <div class="sources">
          <h5>Sources</h5>
          <ul>
            {#each result.sources as src}
              <li>{src.title || src.notebook_id || src.aspects || JSON.stringify(src)}</li>
            {/each}
          </ul>
        </div>
      {/if}

      <details>
        <summary>Raw JSON</summary>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </div>
  {/if}
</div>

<style>
  .notebook-panel {
    background: #ffffff;
    border-top: 1px solid #e5e7eb;
    border-bottom: 1px solid #e5e7eb;
    padding: 1rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    gap: 1rem;
    font-family: sans-serif;
    color: #1f2937;
  }

  .nb-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .title-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  h3 {
    margin: 0;
    font-size: 0.95rem;
    color: #111827;
  }
  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }
  .status-dot.green { background: #10b981; }
  .status-dot.red { background: #ef4444; }
  .status-label {
    font-size: 0.8rem;
    color: #6b7280;
  }
  .refresh-btn {
    background: none;
    border: 1px solid #d1d5db;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
  }

  .section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  label {
    display: flex;
    flex-direction: column;
    font-size: 0.85rem;
    font-weight: 600;
    gap: 0.35rem;
  }

  select, textarea, input {
    border: 1px solid #d1d5db;
    border-radius: 4px;
    padding: 0.5rem;
    font-family: inherit;
  }

  textarea {
    min-height: 60px;
    resize: vertical;
  }

  .action-btn,
  .section button,
  .full-btn {
    background: #2563eb;
    color: white;
    border: none;
    padding: 0.6rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
  }
  .action-btn:disabled,
  .section button:disabled,
  .full-btn:disabled {
    background: #93c5fd;
    cursor: not-allowed;
  }

  .two-col {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.75rem;
  }

  .full-btn {
    grid-column: 1 / -1;
  }

  .error-box {
    background: #fee2e2;
    color: #b91c1c;
    padding: 0.75rem;
    border-radius: 4px;
    font-size: 0.85rem;
  }

  .result-box {
    background: #f3f4f6;
    border-radius: 6px;
    padding: 0.75rem;
    font-size: 0.85rem;
  }
  .result-box h4 { margin: 0 0 0.5rem 0; }
  .answer-text {
    white-space: pre-line;
    margin-bottom: 0.5rem;
  }
  .sources h5 { margin: 0.5rem 0 0 0; }
  .sources ul {
    padding-left: 1.25rem;
    margin: 0.25rem 0;
  }
  .sources li {
    font-size: 0.8rem;
  }

  .empty-state {
    text-align: center;
    color: #6b7280;
    font-size: 0.85rem;
  }

  details {
    margin-top: 0.5rem;
  }
  pre {
    background: #111827;
    color: #fefefe;
    padding: 0.5rem;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 0.75rem;
  }
</style>

