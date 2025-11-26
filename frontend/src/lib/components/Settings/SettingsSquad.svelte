<!--
  SettingsSquad.svelte - Squad settings tab with tournament model picker

  Features:
  - Shows active squad with "Change Squad" button
  - Tournament model picker with checkboxes
  - Real-time cost estimation
  - Reset to defaults functionality

  Usage:
    <SettingsSquad />
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import type { SquadPreset, TournamentModel, TournamentCostEstimate } from '$lib/api_client';
  import SquadWizard from '../Squads/SquadWizard.svelte';

  const BASE_URL = 'http://localhost:8000';
  const dispatch = createEventDispatcher();

  // Active squad state
  let activeSquadId: string | null = null;
  let activeSquad: SquadPreset | null = null;
  let setupComplete = false;
  let loadingSquad = true;

  // Tournament models state
  let tournamentModels: TournamentModel[] = [];
  let loadingModels = false;
  let hasCustomSelection = false;

  // Cost estimation state
  let costEstimate: TournamentCostEstimate | null = null;
  let loadingCost = false;

  // UI state
  let showWizard = false;
  let saveMessage = '';
  let errorMessage = '';

  // Squad icons mapping
  const squadIcons: Record<string, string> = {
    local: '&#127968;',    // House emoji
    hybrid: '&#128142;',   // Gem emoji
    pro: '&#128640;'       // Rocket emoji
  };

  onMount(async () => {
    await loadActiveSquad();
    await loadTournamentModels();
  });

  async function loadActiveSquad() {
    loadingSquad = true;
    errorMessage = '';

    try {
      // Get active squad
      const response = await fetch(`${BASE_URL}/squad/active`);
      if (!response.ok) {
        throw new Error('Failed to load active squad');
      }

      const data = await response.json();
      activeSquadId = data.squad;
      setupComplete = data.setup_complete;

      // Get squad details
      if (activeSquadId) {
        const squadsResponse = await fetch(`${BASE_URL}/squad/available`);
        if (squadsResponse.ok) {
          const squadsData = await squadsResponse.json();
          activeSquad = squadsData.squads.find((s: SquadPreset) => s.id === activeSquadId) || null;
        }
      }
    } catch (e) {
      errorMessage = e instanceof Error ? e.message : 'Failed to load squad info';
    } finally {
      loadingSquad = false;
    }
  }

  async function loadTournamentModels() {
    loadingModels = true;

    try {
      const response = await fetch(`${BASE_URL}/squad/tournament-models?include_unavailable=true`);
      if (!response.ok) {
        throw new Error('Failed to load tournament models');
      }

      const data = await response.json();
      tournamentModels = data.models || [];

      // Check if there's a custom selection
      const selectedIds = tournamentModels.filter(m => m.selected).map(m => m.id);
      const defaultIds = activeSquad?.default_models.tournament || [];
      hasCustomSelection = JSON.stringify(selectedIds.sort()) !== JSON.stringify(defaultIds.sort());

      // Estimate cost for selected models
      await estimateCost();
    } catch (e) {
      console.error('Failed to load tournament models:', e);
    } finally {
      loadingModels = false;
    }
  }

  async function estimateCost() {
    const selectedModels = tournamentModels.filter(m => m.selected).map(m => m.id);
    if (selectedModels.length === 0) {
      costEstimate = null;
      return;
    }

    loadingCost = true;

    try {
      const response = await fetch(`${BASE_URL}/squad/estimate-cost`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          models: selectedModels,
          num_strategies: 5,
          avg_tokens_per_variant: 2000
        })
      });

      if (response.ok) {
        costEstimate = await response.json();
      }
    } catch (e) {
      console.error('Failed to estimate cost:', e);
    } finally {
      loadingCost = false;
    }
  }

  async function toggleModel(modelId: string) {
    const model = tournamentModels.find(m => m.id === modelId);
    if (!model || !model.available) return;

    model.selected = !model.selected;
    tournamentModels = [...tournamentModels]; // Trigger reactivity
    hasCustomSelection = true;

    // Re-estimate cost
    await estimateCost();
  }

  async function saveCustomSelection() {
    const selectedModels = tournamentModels.filter(m => m.selected).map(m => m.id);
    saveMessage = '';
    errorMessage = '';

    try {
      const response = await fetch(`${BASE_URL}/squad/tournament-models`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ models: selectedModels })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save selection');
      }

      saveMessage = 'Tournament models saved successfully';
      setTimeout(() => saveMessage = '', 3000);
    } catch (e) {
      errorMessage = e instanceof Error ? e.message : 'Failed to save selection';
    }
  }

  async function resetToDefaults() {
    saveMessage = '';
    errorMessage = '';

    try {
      const response = await fetch(`${BASE_URL}/squad/tournament-models/custom`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to reset selection');
      }

      // Reload models
      await loadTournamentModels();
      hasCustomSelection = false;
      saveMessage = 'Reset to squad defaults';
      setTimeout(() => saveMessage = '', 3000);
    } catch (e) {
      errorMessage = e instanceof Error ? e.message : 'Failed to reset';
    }
  }

  function openWizard() {
    showWizard = true;
  }

  function closeWizard() {
    showWizard = false;
    // Reload squad info
    loadActiveSquad();
    loadTournamentModels();
  }

  function formatModelName(modelId: string): string {
    const nameMap: Record<string, string> = {
      'deepseek-chat': 'DeepSeek V3',
      'qwen-plus': 'Qwen Plus',
      'glm-4-flash': 'Zhipu GLM-4',
      'gemini-2.0-flash': 'Gemini 2.0 Flash',
      'claude-sonnet-4-20250514': 'Claude Sonnet 4',
      'gpt-4o': 'GPT-4o',
      'mistral:7b': 'Mistral 7B',
      'llama3.2:3b': 'Llama 3.2 3B',
      'ollama-mistral-7b': 'Mistral 7B (Local)',
      'ollama-llama-3.2': 'Llama 3.2 (Local)',
      'ollama-deepseek-r1-7b': 'DeepSeek R1 7B (Local)',
      'ollama-qwen2.5-7b': 'Qwen 2.5 7B (Local)'
    };
    return nameMap[modelId] || modelId;
  }

  function formatCost(cost: number): string {
    if (cost === 0) return 'Free';
    if (cost < 0.001) return '<$0.001';
    if (cost < 0.01) return `$${cost.toFixed(4)}`;
    return `$${cost.toFixed(3)}`;
  }

  function getTierColor(tier: string): string {
    switch (tier.toLowerCase()) {
      case 'budget': return 'var(--success, #3fb950)';
      case 'balanced': return 'var(--accent-cyan, #58a6ff)';
      case 'premium': return '#a371f7';
      default: return 'var(--text-secondary, #8b949e)';
    }
  }
</script>

<div class="settings-squad">
  <div class="header">
    <h2>Squad Configuration</h2>
    <p class="subtitle">Manage your AI model squad and tournament settings</p>
  </div>

  <!-- Active Squad Section -->
  <div class="section">
    <h3>Active Squad</h3>

    {#if loadingSquad}
      <div class="loading-state">
        <div class="spinner"></div>
        <span>Loading squad info...</span>
      </div>
    {:else if !activeSquadId || !setupComplete}
      <div class="no-squad-state">
        <div class="no-squad-icon">&#128736;</div>
        <h4>No Squad Selected</h4>
        <p>Set up your AI model squad to get started with intelligent model selection.</p>
        <button class="btn-primary" on:click={openWizard}>
          Get Started
        </button>
      </div>
    {:else if activeSquad}
      <div class="active-squad-card">
        <div class="squad-header">
          <div class="squad-icon">{@html squadIcons[activeSquad.id] || '&#128736;'}</div>
          <div class="squad-info">
            <h4 class="squad-name">{activeSquad.name}</h4>
            <p class="squad-description">{activeSquad.description}</p>
          </div>
          <button class="btn-change" on:click={openWizard}>
            Change Squad
          </button>
        </div>

        <div class="squad-models">
          <div class="model-row">
            <span class="model-role">Strategic</span>
            <span class="model-value">{formatModelName(activeSquad.default_models.foreman_strategic)}</span>
          </div>
          <div class="model-row">
            <span class="model-role">Coordinator</span>
            <span class="model-value">{formatModelName(activeSquad.default_models.foreman_coordinator)}</span>
          </div>
          <div class="model-row">
            <span class="model-role">Tournament</span>
            <span class="model-value">{activeSquad.default_models.tournament.length} models</span>
          </div>
        </div>

        <div class="squad-cost">
          <span class="cost-label">Estimated</span>
          {#if activeSquad.cost_estimate.monthly_usd === 0}
            <span class="cost-value free">Free</span>
          {:else}
            <span class="cost-value">${activeSquad.cost_estimate.monthly_usd.toFixed(2)}/month</span>
          {/if}
        </div>
      </div>
    {/if}
  </div>

  <!-- Tournament Models Section -->
  {#if activeSquadId && setupComplete}
    <div class="section">
      <div class="section-header">
        <div>
          <h3>Tournament Models</h3>
          <p class="help-text">
            Select which models compete in scene tournaments. More models = more variety, higher cost.
          </p>
        </div>
        {#if hasCustomSelection}
          <span class="custom-badge">Custom</span>
        {/if}
      </div>

      {#if loadingModels}
        <div class="loading-state">
          <div class="spinner"></div>
          <span>Loading models...</span>
        </div>
      {:else}
        <div class="models-grid">
          {#each tournamentModels as model}
            <button
              class="model-card {model.selected ? 'selected' : ''} {!model.available ? 'unavailable' : ''}"
              on:click={() => toggleModel(model.id)}
              disabled={!model.available}
            >
              <div class="model-checkbox">
                {#if model.selected}
                  <span class="checkbox-checked">&#10003;</span>
                {:else}
                  <span class="checkbox-empty"></span>
                {/if}
              </div>
              <div class="model-details">
                <span class="model-name">{model.name}</span>
                <span class="model-provider">{model.provider}</span>
              </div>
              <div class="model-meta">
                <span class="model-cost">{formatCost(model.cost_per_1m_input)}/1M</span>
                <span class="model-tier" style="background: {getTierColor(model.tier)}">{model.tier}</span>
              </div>
              {#if !model.available}
                <span class="unavailable-reason">Missing API key</span>
              {/if}
            </button>
          {/each}
        </div>

        <!-- Cost Estimate -->
        {#if costEstimate}
          <div class="cost-estimate">
            <div class="cost-header">
              <span class="cost-title">Tournament Cost Estimate</span>
              {#if loadingCost}
                <div class="mini-spinner"></div>
              {/if}
            </div>
            <div class="cost-details">
              <div class="cost-row">
                <span>Total variants</span>
                <span class="cost-number">{costEstimate.total_variants}</span>
              </div>
              <div class="cost-row">
                <span>Per tournament</span>
                <span class="cost-number highlight">{formatCost(costEstimate.total_cost)}</span>
              </div>
            </div>
            <div class="cost-breakdown">
              <details>
                <summary>Cost breakdown</summary>
                <div class="breakdown-list">
                  {#each costEstimate.breakdown as item}
                    <div class="breakdown-item">
                      <span>{item.model_name}</span>
                      <span>{item.variants} variants</span>
                      <span>{formatCost(item.cost)}</span>
                    </div>
                  {/each}
                </div>
              </details>
            </div>
          </div>
        {/if}

        <!-- Actions -->
        <div class="model-actions">
          <button
            class="btn-secondary"
            on:click={resetToDefaults}
            disabled={!hasCustomSelection}
          >
            Reset to Defaults
          </button>
          <button
            class="btn-primary"
            on:click={saveCustomSelection}
            disabled={!hasCustomSelection}
          >
            Save Custom Selection
          </button>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Info Panel -->
  <div class="info-panel">
    <h4>How Squads Work</h4>
    <ul>
      <li><strong>Local Squad:</strong> Uses free Ollama models - zero ongoing costs, complete privacy</li>
      <li><strong>Hybrid Squad:</strong> Mixes affordable cloud models with local - best value</li>
      <li><strong>Pro Squad:</strong> Premium models (Claude, GPT-4o) for maximum quality</li>
      <li>Tournament models compete to generate the best scene variants</li>
      <li>You can customize which models compete without changing your squad</li>
    </ul>
  </div>

  <!-- Messages -->
  {#if saveMessage}
    <div class="message success">{saveMessage}</div>
  {/if}
  {#if errorMessage}
    <div class="message error">{errorMessage}</div>
  {/if}
</div>

<!-- Squad Wizard Modal -->
{#if showWizard}
  <div class="wizard-modal">
    <div class="wizard-backdrop" on:click={closeWizard} on:keydown={(e) => e.key === 'Escape' && closeWizard()} role="button" tabindex="0"></div>
    <div class="wizard-container">
      <button class="wizard-close" on:click={closeWizard}>&#10005;</button>
      <SquadWizard onComplete={closeWizard} />
    </div>
  </div>
{/if}

<style>
  .settings-squad {
    padding: 2rem;
    max-width: 1200px;
    color: #ffffff;
  }

  .header {
    margin-bottom: 2rem;
  }

  .header h2 {
    font-size: 1.75rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0 0 0.5rem 0;
  }

  .subtitle {
    color: #b0b0b0;
    margin: 0;
  }

  .section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
  }

  .section h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #00d9ff;
    margin: 0 0 1rem 0;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }

  .section-header h3 {
    margin-bottom: 0.25rem;
  }

  .help-text {
    font-size: 0.875rem;
    color: #888;
    margin: 0;
  }

  .custom-badge {
    padding: 0.25rem 0.5rem;
    background: #ffb00030;
    color: #ffb000;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  /* Loading State */
  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 2rem;
    color: #888;
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #404040;
    border-top-color: #00d9ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .mini-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid #404040;
    border-top-color: #00d9ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* No Squad State */
  .no-squad-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 2rem;
  }

  .no-squad-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  .no-squad-state h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    color: #ffffff;
  }

  .no-squad-state p {
    margin: 0 0 1.5rem 0;
    color: #888;
    max-width: 300px;
  }

  /* Active Squad Card */
  .active-squad-card {
    background: #1a1a1a;
    border-radius: 8px;
    padding: 1.25rem;
  }

  .squad-header {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .squad-icon {
    font-size: 2rem;
  }

  .squad-info {
    flex: 1;
  }

  .squad-name {
    margin: 0 0 0.25rem 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #ffffff;
  }

  .squad-description {
    margin: 0;
    font-size: 0.875rem;
    color: #888;
  }

  .btn-change {
    padding: 0.5rem 1rem;
    background: transparent;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #b0b0b0;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-change:hover {
    background: #2d2d2d;
    border-color: #00d9ff;
    color: #00d9ff;
  }

  .squad-models {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem 0;
    border-top: 1px solid #404040;
    border-bottom: 1px solid #404040;
    margin-bottom: 1rem;
  }

  .model-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .model-role {
    font-size: 0.875rem;
    color: #888;
  }

  .model-value {
    font-size: 0.875rem;
    color: #00d9ff;
    font-family: 'JetBrains Mono', monospace;
  }

  .squad-cost {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .cost-label {
    font-size: 0.875rem;
    color: #888;
  }

  .cost-value {
    font-size: 1rem;
    font-weight: 600;
    color: #00d9ff;
  }

  .cost-value.free {
    color: #00ff88;
  }

  /* Tournament Models Grid */
  .models-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  .model-card {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 0.75rem;
    align-items: center;
    padding: 0.875rem 1rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    position: relative;
  }

  .model-card:hover:not(:disabled) {
    border-color: #00d9ff;
  }

  .model-card.selected {
    border-color: #00d9ff;
    background: #1a3a4a;
  }

  .model-card.unavailable {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .model-checkbox {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .checkbox-empty {
    width: 16px;
    height: 16px;
    border: 2px solid #404040;
    border-radius: 3px;
  }

  .checkbox-checked {
    width: 16px;
    height: 16px;
    background: #00d9ff;
    border-radius: 3px;
    color: #1a1a1a;
    font-size: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .model-details {
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
    min-width: 0;
  }

  .model-card .model-name {
    font-size: 0.875rem;
    font-weight: 500;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .model-provider {
    font-size: 0.75rem;
    color: #888;
  }

  .model-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.25rem;
  }

  .model-cost {
    font-size: 0.75rem;
    color: #888;
    font-family: 'JetBrains Mono', monospace;
  }

  .model-tier {
    padding: 0.125rem 0.375rem;
    border-radius: 3px;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    color: #1a1a1a;
  }

  .unavailable-reason {
    position: absolute;
    bottom: 0.5rem;
    right: 0.5rem;
    font-size: 0.65rem;
    color: #ff4444;
  }

  /* Cost Estimate */
  .cost-estimate {
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .cost-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .cost-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .cost-details {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .cost-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.875rem;
    color: #b0b0b0;
  }

  .cost-number {
    font-family: 'JetBrains Mono', monospace;
    color: #ffffff;
  }

  .cost-number.highlight {
    color: #00d9ff;
    font-weight: 600;
    font-size: 1rem;
  }

  .cost-breakdown details {
    font-size: 0.8rem;
  }

  .cost-breakdown summary {
    color: #888;
    cursor: pointer;
    padding: 0.5rem 0;
  }

  .cost-breakdown summary:hover {
    color: #00d9ff;
  }

  .breakdown-list {
    padding-top: 0.5rem;
  }

  .breakdown-item {
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 1rem;
    padding: 0.25rem 0;
    color: #888;
  }

  .breakdown-item span:last-child {
    font-family: 'JetBrains Mono', monospace;
    color: #b0b0b0;
  }

  /* Actions */
  .model-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.625rem 1.25rem;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #00d9ff;
    color: #1a1a1a;
    border: none;
  }

  .btn-primary:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: transparent;
    color: #b0b0b0;
    border: 1px solid #404040;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #2d2d2d;
    color: #ffffff;
  }

  .btn-secondary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Info Panel */
  .info-panel {
    padding: 1.5rem;
    background: #1a3a4a20;
    border: 1px solid #00d9ff40;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .info-panel h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #00d9ff;
    margin: 0 0 0.75rem 0;
  }

  .info-panel ul {
    margin: 0;
    padding-left: 1.5rem;
  }

  .info-panel li {
    color: #b0b0b0;
    line-height: 1.6;
    margin-bottom: 0.5rem;
  }

  .info-panel li strong {
    color: #ffffff;
  }

  /* Messages */
  .message {
    padding: 0.75rem;
    border-radius: 4px;
    font-weight: 500;
    margin-top: 1rem;
  }

  .message.success {
    background: #00ff8820;
    color: #00ff88;
    border: 1px solid #00ff88;
  }

  .message.error {
    background: #ff444420;
    color: #ff4444;
    border: 1px solid #ff4444;
  }

  /* Wizard Modal */
  .wizard-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .wizard-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
  }

  .wizard-container {
    position: relative;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 12px;
    width: 95%;
    max-width: 960px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .wizard-close {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: transparent;
    border: none;
    color: #888;
    font-size: 1.5rem;
    cursor: pointer;
    z-index: 10;
    transition: color 0.2s;
  }

  .wizard-close:hover {
    color: #ffffff;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .settings-squad {
      padding: 1rem;
    }

    .squad-header {
      flex-direction: column;
    }

    .btn-change {
      width: 100%;
    }

    .models-grid {
      grid-template-columns: 1fr;
    }

    .model-actions {
      flex-direction: column;
    }

    .btn-primary,
    .btn-secondary {
      width: 100%;
    }
  }
</style>
