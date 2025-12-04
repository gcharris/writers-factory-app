<!--
  SettingsSquad.svelte - Squad settings tab with role assignments and tournament model picker

  Features:
  - Shows active squad with "Change Squad" button
  - Role-specific model assignment (Strategic, Coordinator)
  - Health check model configuration
  - Tournament model picker with checkboxes
  - Real-time cost estimation (Fixed + Variable)
  - Reset to defaults functionality

  Usage:
    <SettingsSquad />
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import type { SquadPreset, TournamentModel, TournamentCostEstimate } from '$lib/api_client';
  import SquadWizard from '../Squads/SquadWizard.svelte';
  import RoleModelSelector from './RoleModelSelector.svelte';
  import HealthCheckModelConfig from './HealthCheckModelConfig.svelte';

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

  // Role assignments state
  let roleAssignments = {
    strategic: '',
    coordinator: '',
    health_checks: {} as Record<string, string>
  };
  let loadingRoles = false;

  // Cost estimation state
  let costEstimate: TournamentCostEstimate | null = null;
  let fixedCostEstimate = 0;
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
    await loadRoleAssignments();
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

  async function loadRoleAssignments() {
    loadingRoles = true;
    try {
      // Fetch foreman settings
      const foremanRes = await fetch(`${BASE_URL}/settings/category/foreman`);
      const foremanData = foremanRes.ok ? await foremanRes.json() : {};

      // Fetch health check settings
      const healthRes = await fetch(`${BASE_URL}/settings/category/health_checks`);
      const healthData = healthRes.ok ? await healthRes.json() : {};

      roleAssignments = {
        strategic: foremanData['task_models.strategic'] || activeSquad?.default_models.foreman_strategic || 'deepseek-chat',
        coordinator: foremanData['task_models.coordinator'] || activeSquad?.default_models.foreman_coordinator || 'deepseek-chat',
        health_checks: {
          default_model: healthData['models.default_model'] || 'llama3.2',
          timeline_consistency: healthData['models.timeline_consistency'],
          theme_resonance: healthData['models.theme_resonance'],
          flaw_challenges: healthData['models.flaw_challenges'],
          cast_function: healthData['models.cast_function'],
          pacing_analysis: healthData['models.pacing_analysis'],
          beat_progress: healthData['models.beat_progress'],
          symbolic_layering: healthData['models.symbolic_layering']
        }
      };
    } catch (e) {
      console.error('Failed to load role assignments:', e);
    } finally {
      loadingRoles = false;
    }
  }

  async function estimateCost() {
    const selectedModels = tournamentModels.filter(m => m.selected).map(m => m.id);
    
    // Calculate Fixed Costs (Role Assignments)
    // Formula: (Strategic * 50) + (Coordinator * 200)
    const strategicModel = tournamentModels.find(m => m.id === roleAssignments.strategic);
    const coordinatorModel = tournamentModels.find(m => m.id === roleAssignments.coordinator);
    
    const strategicCost = (strategicModel?.cost_per_1m_tokens || 0) * (50 / 1000); // 50 calls, assuming 1k tokens/call avg? No, cost is per 1M. 
    // Let's assume 1 call = 2k tokens (input+output) for estimation
    const TOKENS_PER_CALL = 2000;
    const strategicMonthlyCost = (strategicModel?.cost_per_1m_tokens || 0) * (50 * TOKENS_PER_CALL / 1000000);
    const coordinatorMonthlyCost = (coordinatorModel?.cost_per_1m_tokens || 0) * (200 * TOKENS_PER_CALL / 1000000);
    
    fixedCostEstimate = strategicMonthlyCost + coordinatorMonthlyCost;

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

  async function handleRoleChange(role: 'strategic' | 'coordinator', modelId: string) {
    roleAssignments[role] = modelId;
    await saveSettings('foreman', { [`task_models.${role}`]: modelId });
    await estimateCost();
  }

  async function handleHealthCheckChange(newConfig: Record<string, string>) {
    roleAssignments.health_checks = newConfig;
    
    // Flatten config for API
    const flatConfig: Record<string, string> = {};
    for (const [key, value] of Object.entries(newConfig)) {
      if (value) flatConfig[`models.${key}`] = value;
    }
    
    await saveSettings('health_checks', flatConfig);
  }

  async function saveSettings(category: string, settings: Record<string, any>) {
    try {
      const response = await fetch(`${BASE_URL}/settings/category/${category}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      
      if (!response.ok) throw new Error('Failed to save settings');
      
      // Show subtle success indicator if needed, or just rely on UI update
    } catch (e) {
      errorMessage = `Failed to save ${category} settings`;
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
      // Reset tournament models
      const response = await fetch(`${BASE_URL}/squad/tournament-models/custom`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to reset tournament selection');

      // Reset roles to squad defaults
      if (activeSquad) {
        await handleRoleChange('strategic', activeSquad.default_models.foreman_strategic);
        await handleRoleChange('coordinator', activeSquad.default_models.foreman_coordinator);
        // Reset health checks (implementation depends on if we want to reset to squad defaults or just clear overrides)
        // For now, let's just reload to get fresh state
      }

      // Reload all
      await loadTournamentModels();
      await loadRoleAssignments();
      
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
    loadRoleAssignments();
  }

  function formatModelName(modelId: string): string {
    const model = tournamentModels.find(m => m.id === modelId);
    return model ? model.name : modelId;
  }

  function formatCost(cost: number): string {
    if (cost === 0) return 'Free';
    if (cost < 0.001) return '<$0.001';
    if (cost < 0.01) return `$${cost.toFixed(4)}`;
    return `$${cost.toFixed(3)}`;
  }

  function getTierColor(tier: string): string {
    switch (tier?.toLowerCase()) {
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
    <p class="subtitle">Manage your AI model squad, role assignments, and tournament settings</p>
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

        <div class="squad-cost">
          <span class="cost-label">Total Estimated Monthly Cost:</span>
          <span class="cost-value">
            {formatCost(fixedCostEstimate + (costEstimate?.total_cost || 0))}
          </span>
          <span class="cost-detail">
            (Fixed: {formatCost(fixedCostEstimate)} + Tournament: {formatCost(costEstimate?.total_cost || 0)})
          </span>
        </div>
      </div>
    {/if}
  </div>

  <!-- Model Assignments Section -->
  {#if activeSquadId && setupComplete}
    <div class="section">
      <div class="section-header">
        <div>
          <h3>Model Assignments</h3>
          <p class="help-text">Assign specific models to key roles in your squad.</p>
        </div>
        <button class="btn-secondary btn-sm" on:click={resetToDefaults}>
          Use Squad Defaults
        </button>
      </div>

      <div class="assignments-container">
        <RoleModelSelector
          role="strategic"
          label="Strategic Lead"
          description="High-level planning, outlining, and decision making."
          currentModel={roleAssignments.strategic}
          availableModels={tournamentModels}
          on:select={(e) => handleRoleChange('strategic', e.detail.modelId)}
        />
        
        <RoleModelSelector
          role="coordinator"
          label="Coordinator"
          description="Task management, context assembly, and file operations."
          currentModel={roleAssignments.coordinator}
          availableModels={tournamentModels}
          on:select={(e) => handleRoleChange('coordinator', e.detail.modelId)}
        />

        <HealthCheckModelConfig
          config={roleAssignments.health_checks}
          availableModels={tournamentModels}
          on:change={(e) => handleHealthCheckChange(e.detail)}
        />
      </div>
    </div>
  {/if}

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

  .squad-cost {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-top: 1rem;
    border-top: 1px solid #404040;
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

  .cost-detail {
    font-size: 0.8rem;
    color: #666;
  }

  .cost-value.free {
    color: #00ff88;
  }

  /* Assignments Container */
  .assignments-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .btn-sm {
    padding: 0.25rem 0.75rem;
    font-size: 0.8rem;
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
    font-size: 0.9rem;
    color: #b0b0b0;
    font-weight: 500;
  }

  .cost-details {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #404040;
  }

  .cost-row {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .cost-row span:first-child {
    font-size: 0.75rem;
    color: #888;
  }

  .cost-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    color: #ffffff;
  }

  .cost-number.highlight {
    color: #00d9ff;
  }

  .cost-breakdown summary {
    font-size: 0.75rem;
    color: #888;
    cursor: pointer;
    user-select: none;
  }

  .breakdown-list {
    margin-top: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .breakdown-item {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #b0b0b0;
  }

  /* Actions */
  .model-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .btn-primary {
    padding: 0.75rem 1.5rem;
    background: #00d9ff;
    color: #1a1a1a;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    padding: 0.75rem 1.5rem;
    background: transparent;
    border: 1px solid #404040;
    color: #b0b0b0;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover:not(:disabled) {
    border-color: #00d9ff;
    color: #00d9ff;
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
    padding: 1rem;
    border-radius: 4px;
    margin-top: 1rem;
    text-align: center;
  }

  .message.success {
    background: #00d9ff20;
    color: #00d9ff;
    border: 1px solid #00d9ff40;
  }

  .message.error {
    background: #ff444420;
    color: #ff4444;
    border: 1px solid #ff444440;
  }

  /* Wizard Modal */
  .wizard-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .wizard-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(4px);
  }

  .wizard-container {
    position: relative;
    width: 90%;
    max-width: 1000px;
    height: 90vh;
    background: #1a1a1a;
    border-radius: 12px;
    border: 1px solid #404040;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    z-index: 1001;
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
    z-index: 1002;
    padding: 0.5rem;
    line-height: 1;
  }

  .wizard-close:hover {
    color: #ffffff;
  }
</style>
