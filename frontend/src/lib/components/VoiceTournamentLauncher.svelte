<!--
  VoiceTournamentLauncher.svelte - Tournament Configuration Interface

  Allows writers to:
  - View available AI agents (with API key status)
  - Select 3+ agents for the tournament
  - Choose writing strategies
  - Provide test prompt and context
  - Optionally describe their desired voice
  - Launch the tournament
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import {
    voiceAgents,
    voiceAgentsLoading,
    currentTournament,
    tournamentLoading,
    tournamentStatus,
    voiceTournamentStep,
    showVoiceTournament,
    foremanProjectTitle
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Tournament configuration
  let selectedAgentIds = [];
  let testPrompt = '';
  let testContext = '';
  let voiceDescription = '';
  let variantsPerAgent = 5;

  // Writing strategies
  const strategies = [
    { id: 'ACTION_EMPHASIS', name: 'Action', desc: 'Fast pacing, physical detail, external conflict' },
    { id: 'CHARACTER_DEPTH', name: 'Character', desc: 'Slower pacing, internal landscape, psychology' },
    { id: 'DIALOGUE_FOCUS', name: 'Dialogue', desc: 'Conversation-centered, subtext, conflict through words' },
    { id: 'BRAINSTORMING', name: 'Brainstorming', desc: 'Idea exploration, multiple perspectives, experimental' },
    { id: 'BALANCED', name: 'Balanced', desc: 'Mix of elements, standard structure' }
  ];

  // Sample prompts for inspiration
  const samplePrompts = [
    {
      name: 'Tense Discovery',
      prompt: 'A detective discovers a crucial piece of evidence that changes everything they thought they knew about the case.',
      context: 'Interior, late night. The detective is alone in their office, surrounded by case files.'
    },
    {
      name: 'Emotional Confrontation',
      prompt: 'Two characters who were once close meet again after a betrayal, forced to work together.',
      context: 'Public setting with witnesses. One character holds power over the other.'
    },
    {
      name: 'Action Sequence',
      prompt: 'The protagonist must escape from a dangerous situation using only their wits.',
      context: 'High stakes, time pressure, physical obstacles to overcome.'
    }
  ];

  // Computed
  $: readyAgents = $voiceAgents.filter(a => a.enabled && a.has_valid_key);
  $: unavailableAgents = $voiceAgents.filter(a => !a.enabled || !a.has_valid_key);
  $: canStartTournament = selectedAgentIds.length >= 3 && testPrompt.trim() && testContext.trim();
  $: expectedVariants = selectedAgentIds.length * variantsPerAgent;

  onMount(async () => {
    await loadAgents();
  });

  async function loadAgents() {
    $voiceAgentsLoading = true;
    try {
      const result = await apiClient.getVoiceCalibrationAgents();
      $voiceAgents = result.agents || [];

      // Auto-select all ready agents
      selectedAgentIds = readyAgents.map(a => a.id);
    } catch (error) {
      console.error('Failed to load agents:', error);
      addToast('Failed to load available agents', 'error');
    } finally {
      $voiceAgentsLoading = false;
    }
  }

  function toggleAgent(agentId) {
    if (selectedAgentIds.includes(agentId)) {
      selectedAgentIds = selectedAgentIds.filter(id => id !== agentId);
    } else {
      selectedAgentIds = [...selectedAgentIds, agentId];
    }
  }

  function useSamplePrompt(sample) {
    testPrompt = sample.prompt;
    testContext = sample.context;
  }

  async function startTournament() {
    if (!canStartTournament) return;

    $tournamentLoading = true;
    $tournamentStatus = 'running';

    try {
      const projectId = $foremanProjectTitle || 'default_project';

      const result = await apiClient.startVoiceTournament(
        projectId,
        testPrompt,
        testContext,
        selectedAgentIds,
        variantsPerAgent,
        voiceDescription || undefined
      );

      $currentTournament = result;
      $voiceTournamentStep = 1; // Move to running state

      addToast(`Tournament started with ${selectedAgentIds.length} agents`, 'success');
      dispatch('started', { tournamentId: result.tournament_id });

    } catch (error) {
      console.error('Failed to start tournament:', error);
      addToast(`Failed to start tournament: ${error.message}`, 'error');
      $tournamentStatus = 'failed';
    } finally {
      $tournamentLoading = false;
    }
  }

  function handleClose() {
    $showVoiceTournament = false;
    dispatch('close');
  }
</script>

<div class="launcher-container">
  <div class="launcher-header">
    <div class="header-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="22"/>
      </svg>
    </div>
    <div class="header-text">
      <h2>Voice Calibration Tournament</h2>
      <p>Discover your narrative voice through AI competition</p>
    </div>
  </div>

  <div class="launcher-content">
    <!-- Agent Selection -->
    <section class="config-section">
      <h3 class="section-title">
        <span class="section-icon">1</span>
        Select AI Agents
        <span class="badge">{selectedAgentIds.length} selected</span>
      </h3>
      <p class="section-desc">Choose 3 or more agents to compete. Each will generate {variantsPerAgent} voice variants.</p>

      {#if $voiceAgentsLoading}
        <div class="loading-state">
          <div class="spinner"></div>
          <span>Loading agents...</span>
        </div>
      {:else}
        <div class="agent-grid">
          {#each readyAgents as agent}
            <button
              class="agent-card"
              class:selected={selectedAgentIds.includes(agent.id)}
              on:click={() => toggleAgent(agent.id)}
            >
              <div class="agent-status ready"></div>
              <div class="agent-info">
                <span class="agent-name">{agent.name}</span>
                <span class="agent-model">{agent.model}</span>
              </div>
              <div class="agent-check">
                {#if selectedAgentIds.includes(agent.id)}
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                  </svg>
                {/if}
              </div>
            </button>
          {/each}
        </div>

        {#if unavailableAgents.length > 0}
          <details class="unavailable-agents">
            <summary>{unavailableAgents.length} agent(s) unavailable (missing API keys)</summary>
            <div class="agent-list">
              {#each unavailableAgents as agent}
                <div class="agent-item disabled">
                  <span class="agent-status offline"></span>
                  <span>{agent.name}</span>
                  <span class="missing-key">No API key</span>
                </div>
              {/each}
            </div>
          </details>
        {/if}

        {#if selectedAgentIds.length < 3}
          <div class="warning-message">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
            <span>Select at least 3 agents for meaningful competition</span>
          </div>
        {/if}
      {/if}
    </section>

    <!-- Test Prompt -->
    <section class="config-section">
      <h3 class="section-title">
        <span class="section-icon">2</span>
        Test Passage
      </h3>
      <p class="section-desc">Describe a scene for agents to write. This will reveal their voice capabilities.</p>

      <div class="sample-prompts">
        <span class="sample-label">Quick start:</span>
        {#each samplePrompts as sample}
          <button class="sample-btn" on:click={() => useSamplePrompt(sample)}>
            {sample.name}
          </button>
        {/each}
      </div>

      <div class="form-group">
        <label for="test-prompt">Scene Description</label>
        <textarea
          id="test-prompt"
          placeholder="Describe what should happen in the test passage..."
          bind:value={testPrompt}
          rows="4"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="test-context">Scene Context</label>
        <textarea
          id="test-context"
          placeholder="Setting, mood, characters involved, stakes..."
          bind:value={testContext}
          rows="3"
        ></textarea>
      </div>
    </section>

    <!-- Voice Description (Optional) -->
    <section class="config-section">
      <h3 class="section-title">
        <span class="section-icon">3</span>
        Voice Description
        <span class="optional-badge">Optional</span>
      </h3>
      <p class="section-desc">Describe your ideal voice. Leave blank to let agents surprise you.</p>

      <div class="form-group">
        <textarea
          id="voice-desc"
          placeholder="e.g., 'Noir-lyrical with boxing metaphors, short punchy sentences, morally ambiguous narrator...'"
          bind:value={voiceDescription}
          rows="3"
        ></textarea>
      </div>
    </section>

    <!-- Tournament Settings -->
    <section class="config-section">
      <h3 class="section-title">
        <span class="section-icon">4</span>
        Tournament Settings
      </h3>

      <div class="settings-row">
        <div class="form-group compact">
          <label for="variants">Variants per Agent</label>
          <select id="variants" bind:value={variantsPerAgent}>
            <option value={3}>3 variants</option>
            <option value={5}>5 variants (recommended)</option>
          </select>
        </div>

        <div class="preview-box">
          <span class="preview-label">Expected Output</span>
          <span class="preview-value">{expectedVariants} variants</span>
          <span class="preview-detail">({selectedAgentIds.length} agents x {variantsPerAgent} strategies)</span>
        </div>
      </div>

      <div class="strategies-preview">
        <span class="strategies-label">Writing Strategies:</span>
        <div class="strategy-chips">
          {#each strategies as strategy}
            <span class="strategy-chip" title={strategy.desc}>
              {strategy.name}
            </span>
          {/each}
        </div>
      </div>
    </section>
  </div>

  <!-- Footer Actions -->
  <div class="launcher-footer">
    <button class="btn secondary" on:click={handleClose}>
      Cancel
    </button>
    <button
      class="btn primary"
      on:click={startTournament}
      disabled={!canStartTournament || $tournamentLoading}
    >
      {#if $tournamentLoading}
        <span class="spinner small"></span>
        Starting...
      {:else}
        Launch Tournament
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      {/if}
    </button>
  </div>
</div>

<style>
  .launcher-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 80vh;
    background: var(--bg-secondary, #1a2027);
  }

  .launcher-header {
    display: flex;
    align-items: center;
    gap: var(--space-4, 16px);
    padding: var(--space-4, 16px) var(--space-5, 20px);
    background: linear-gradient(135deg, rgba(138, 43, 226, 0.1), rgba(88, 166, 255, 0.1));
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .header-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: var(--accent-cyan, #58a6ff);
    border-radius: var(--radius-lg, 8px);
    color: var(--bg-primary, #0f1419);
  }

  .header-icon svg {
    width: 24px;
    height: 24px;
  }

  .header-text h2 {
    margin: 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .header-text p {
    margin: 2px 0 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .launcher-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  .config-section {
    margin-bottom: var(--space-5, 20px);
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-md, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .section-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    background: var(--bg-tertiary, #242d38);
    border-radius: 50%;
    font-size: 11px;
    color: var(--accent-cyan, #58a6ff);
  }

  .badge {
    margin-left: auto;
    padding: 2px 8px;
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-full, 9999px);
    font-size: 11px;
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
  }

  .optional-badge {
    padding: 2px 6px;
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .section-desc {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    padding-left: 30px;
  }

  /* Agent Grid */
  .agent-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: var(--space-2, 8px);
    margin-bottom: var(--space-3, 12px);
  }

  .agent-card {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .agent-card:hover {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--accent-cyan, #58a6ff);
  }

  .agent-card.selected {
    background: rgba(88, 166, 255, 0.1);
    border-color: var(--accent-cyan, #58a6ff);
  }

  .agent-status {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .agent-status.ready {
    background: var(--success, #3fb950);
  }

  .agent-status.offline {
    background: var(--text-muted, #6e7681);
  }

  .agent-info {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 0;
  }

  .agent-name {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .agent-model {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .agent-check {
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .agent-check svg {
    width: 14px;
    height: 14px;
    color: var(--accent-cyan, #58a6ff);
  }

  /* Unavailable agents */
  .unavailable-agents {
    margin-top: var(--space-2, 8px);
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
  }

  .unavailable-agents summary {
    cursor: pointer;
    color: var(--text-secondary, #8b949e);
  }

  .agent-list {
    margin-top: var(--space-2, 8px);
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .agent-item {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-1, 4px) var(--space-2, 8px);
    color: var(--text-muted, #6e7681);
  }

  .missing-key {
    margin-left: auto;
    font-size: 10px;
    color: var(--warning, #d29922);
  }

  /* Warning message */
  .warning-message {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: rgba(210, 153, 34, 0.1);
    border: 1px solid rgba(210, 153, 34, 0.3);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    color: var(--warning, #d29922);
  }

  .warning-message svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  /* Sample prompts */
  .sample-prompts {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    margin-bottom: var(--space-3, 12px);
    flex-wrap: wrap;
  }

  .sample-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .sample-btn {
    padding: 4px 10px;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .sample-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--accent-cyan, #58a6ff);
    border-color: var(--accent-cyan, #58a6ff);
  }

  /* Form elements */
  .form-group {
    margin-bottom: var(--space-3, 12px);
  }

  .form-group.compact {
    margin-bottom: 0;
  }

  .form-group label {
    display: block;
    margin-bottom: var(--space-1, 4px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .form-group textarea,
  .form-group select {
    width: 100%;
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    font-family: inherit;
    resize: vertical;
  }

  .form-group textarea:focus,
  .form-group select:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
  }

  /* Settings row */
  .settings-row {
    display: flex;
    align-items: flex-end;
    gap: var(--space-4, 16px);
    margin-bottom: var(--space-3, 12px);
  }

  .preview-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: var(--space-2, 8px) var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
  }

  .preview-label {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .preview-value {
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--accent-cyan, #58a6ff);
  }

  .preview-detail {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  /* Strategies preview */
  .strategies-preview {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    flex-wrap: wrap;
  }

  .strategies-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .strategy-chips {
    display: flex;
    gap: var(--space-1, 4px);
    flex-wrap: wrap;
  }

  .strategy-chip {
    padding: 3px 8px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-full, 9999px);
    font-size: 10px;
    color: var(--text-secondary, #8b949e);
  }

  /* Loading state */
  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2, 8px);
    padding: var(--space-6, 24px);
    color: var(--text-secondary, #8b949e);
  }

  /* Footer */
  .launcher-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-2, 8px);
    padding: var(--space-4, 16px);
    border-top: 1px solid var(--border, #2d3a47);
    background: var(--bg-tertiary, #242d38);
  }

  .btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .btn.secondary {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-secondary, #8b949e);
  }

  .btn.secondary:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  .btn.primary {
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  .btn.primary:hover:not(:disabled) {
    filter: brightness(1.1);
  }

  .btn.primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn svg {
    width: 16px;
    height: 16px;
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .spinner.small {
    width: 14px;
    height: 14px;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
