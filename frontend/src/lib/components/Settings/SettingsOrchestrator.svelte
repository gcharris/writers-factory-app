<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Quality tier state
  let qualityTier: 'budget' | 'balanced' | 'premium' = 'balanced';
  let orchestratorEnabled = true;
  let preferLocal = false;
  let monthlyBudget: number | null = null;

  // Cost estimation state
  let currentSpend = 0.0;
  let estimatedMonthlyCost = 0.0;
  let budgetRemaining = 0.0;
  let loadingCost = false;

  // Recommendations state
  let recommendations: Record<string, { budget: string; balanced: string; premium: string }> = {};
  let showRecommendations = false;

  // UI state
  let saveMessage = '';
  let errorMessage = '';

  // Typical usage scenarios for cost estimation
  const TYPICAL_USAGE = {
    light: {
      health_check_review: 20,
      theme_analysis: 10,
      coordinator: 100,
      structural_planning: 15,
      sentence_craft_review: 30,
    },
    medium: {
      health_check_review: 50,
      theme_analysis: 30,
      coordinator: 200,
      structural_planning: 40,
      sentence_craft_review: 80,
    },
    heavy: {
      health_check_review: 100,
      theme_analysis: 60,
      coordinator: 400,
      structural_planning: 80,
      sentence_craft_review: 150,
    },
  };

  let usageScenario: 'light' | 'medium' | 'heavy' = 'medium';

  onMount(() => {
    loadSettings();
    loadCurrentSpend();
    loadRecommendations();
  });

  async function loadSettings() {
    try {
      const response = await fetch(`${BASE_URL}/settings/category/orchestrator`);
      if (response.ok) {
        const data = await response.json();
        qualityTier = data.quality_tier || 'balanced';
        orchestratorEnabled = data.enabled !== false;
        preferLocal = data.prefer_local || false;
        monthlyBudget = data.monthly_budget || null;

        // Estimate cost for current tier
        await estimateCost();
      }
    } catch (error) {
      console.error('Failed to load orchestrator settings:', error);
      errorMessage = 'Failed to load settings';
    }
  }

  async function loadCurrentSpend() {
    try {
      const response = await fetch(`${BASE_URL}/orchestrator/current-spend`);
      if (response.ok) {
        const data = await response.json();
        currentSpend = data.spend || 0.0;
        budgetRemaining = data.budget_remaining || 0.0;
      }
    } catch (error) {
      console.error('Failed to load current spend:', error);
    }
  }

  async function loadRecommendations() {
    try {
      const taskTypes = ['health_check_review', 'theme_analysis', 'coordinator', 'structural_planning', 'sentence_craft_review'];

      for (const taskType of taskTypes) {
        const response = await fetch(`${BASE_URL}/orchestrator/recommendations/${taskType}`);
        if (response.ok) {
          const data = await response.json();
          recommendations[taskType] = data.recommendations;
        }
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    }
  }

  async function estimateCost() {
    if (loadingCost) return;

    loadingCost = true;
    try {
      const response = await fetch(`${BASE_URL}/orchestrator/estimate-cost`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quality_tier: qualityTier,
          estimated_usage: TYPICAL_USAGE[usageScenario],
        }),
      });

      if (response.ok) {
        const data = await response.json();
        estimatedMonthlyCost = data.estimated_cost || 0.0;
      }
    } catch (error) {
      console.error('Failed to estimate cost:', error);
    } finally {
      loadingCost = false;
    }
  }

  async function saveSettings() {
    saveMessage = '';
    errorMessage = '';

    try {
      const settings = {
        quality_tier: qualityTier,
        enabled: orchestratorEnabled,
        prefer_local: preferLocal,
        monthly_budget: monthlyBudget,
      };

      const response = await fetch(`${BASE_URL}/settings/category/orchestrator`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        saveMessage = '✅ Orchestrator settings saved successfully';
        setTimeout(() => (saveMessage = ''), 3000);
      } else {
        const error = await response.json();
        errorMessage = `Failed to save: ${error.detail || 'Unknown error'}`;
      }
    } catch (error) {
      console.error('Failed to save orchestrator settings:', error);
      errorMessage = 'Failed to save settings';
    }
  }

  function handleTierChange(tier: 'budget' | 'balanced' | 'premium') {
    qualityTier = tier;
    estimateCost();
  }

  function handleUsageChange() {
    estimateCost();
  }

  function getBudgetPercentage(): number {
    if (!monthlyBudget || monthlyBudget === 0) return 0;
    return (currentSpend / monthlyBudget) * 100;
  }

  function getBudgetColor(): string {
    const percentage = getBudgetPercentage();
    if (percentage >= 100) return '#ff4444'; // Red
    if (percentage >= 80) return '#ffb000'; // Amber
    return '#00ff88'; // Green
  }

  function formatTaskName(taskType: string): string {
    return taskType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
</script>

<div class="settings-orchestrator">
  <div class="header">
    <h2>Model Orchestrator</h2>
    <p class="subtitle">Intelligent model selection based on quality tiers and budget constraints</p>
  </div>

  <!-- Enable Toggle -->
  <div class="section">
    <div class="toggle-group">
      <label class="toggle-label">
        <input
          type="checkbox"
          bind:checked={orchestratorEnabled}
          class="toggle-input"
        />
        <span class="toggle-switch"></span>
        <span class="toggle-text">Enable Automatic Model Selection</span>
      </label>
      <p class="help-text">
        When enabled, the orchestrator overrides manual model assignments and selects optimal models based on your quality tier.
      </p>
    </div>
  </div>

  <!-- Quality Tier Selection -->
  <div class="section">
    <h3>Quality Tier</h3>
    <div class="tier-cards">
      <button
        class="tier-card {qualityTier === 'budget' ? 'active' : ''}"
        on:click={() => handleTierChange('budget')}
        disabled={!orchestratorEnabled}
      >
        <div class="tier-icon">💰</div>
        <div class="tier-name">Budget</div>
        <div class="tier-cost">~$0/month</div>
        <div class="tier-description">Free local models only (Ollama)</div>
      </button>

      <button
        class="tier-card {qualityTier === 'balanced' ? 'active' : ''}"
        on:click={() => handleTierChange('balanced')}
        disabled={!orchestratorEnabled}
      >
        <div class="tier-icon">⚖️</div>
        <div class="tier-name">Balanced</div>
        <div class="tier-cost">~$0.50-1/month</div>
        <div class="tier-description">Best quality per dollar (DeepSeek + local)</div>
      </button>

      <button
        class="tier-card {qualityTier === 'premium' ? 'active' : ''}"
        on:click={() => handleTierChange('premium')}
        disabled={!orchestratorEnabled}
      >
        <div class="tier-icon">💎</div>
        <div class="tier-name">Premium</div>
        <div class="tier-cost">~$3-5/month</div>
        <div class="tier-description">Optimal model per task (Claude + GPT-4o + DeepSeek)</div>
      </button>
    </div>
  </div>

  <!-- Cost Estimator -->
  <div class="section">
    <h3>Cost Estimation</h3>

    <div class="usage-selector">
      <label>
        <span>Usage Scenario:</span>
        <select bind:value={usageScenario} on:change={handleUsageChange} disabled={!orchestratorEnabled}>
          <option value="light">Light (~200 calls/month)</option>
          <option value="medium">Medium (~400 calls/month)</option>
          <option value="heavy">Heavy (~800 calls/month)</option>
        </select>
      </label>
    </div>

    <div class="cost-display">
      <div class="cost-row">
        <span class="cost-label">Estimated Monthly Cost:</span>
        <span class="cost-value">${estimatedMonthlyCost.toFixed(2)}</span>
      </div>
      <div class="cost-row">
        <span class="cost-label">Current Month Spend:</span>
        <span class="cost-value">${currentSpend.toFixed(2)}</span>
      </div>
    </div>
  </div>

  <!-- Monthly Budget -->
  <div class="section">
    <h3>Monthly Budget (Optional)</h3>
    <div class="budget-input-group">
      <input
        type="number"
        bind:value={monthlyBudget}
        placeholder="No limit"
        min="0"
        max="100"
        step="0.50"
        class="budget-input {monthlyBudget && getBudgetPercentage() >= 80 ? 'warning' : ''}"
        disabled={!orchestratorEnabled}
      />
      <span class="currency">USD</span>
    </div>

    {#if monthlyBudget && monthlyBudget > 0}
      <div class="budget-progress">
        <div class="progress-bar">
          <div
            class="progress-fill"
            style="width: {Math.min(getBudgetPercentage(), 100)}%; background-color: {getBudgetColor()};"
          ></div>
        </div>
        <div class="progress-text">
          ${currentSpend.toFixed(2)} / ${monthlyBudget.toFixed(2)}
          ({monthlyBudget && currentSpend < monthlyBudget ? `$${(monthlyBudget - currentSpend).toFixed(2)} remaining` : 'Budget exceeded'})
        </div>

        {#if getBudgetPercentage() >= 100}
          <div class="budget-warning error">
            🚫 Budget exceeded - using free local models only
          </div>
        {:else if getBudgetPercentage() >= 80}
          <div class="budget-warning">
            ⚠️ Approaching budget limit
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Prefer Local Toggle -->
  <div class="section">
    <div class="toggle-group">
      <label class="toggle-label">
        <input
          type="checkbox"
          bind:checked={preferLocal}
          class="toggle-input"
          disabled={!orchestratorEnabled}
        />
        <span class="toggle-switch"></span>
        <span class="toggle-text">Prefer Local Models</span>
      </label>
      <p class="help-text">
        Use free Ollama models when quality difference is &lt; 1 point (saves costs)
      </p>
    </div>
  </div>

  <!-- Recommendations Preview -->
  <div class="section">
    <button
      class="recommendations-toggle"
      on:click={() => (showRecommendations = !showRecommendations)}
      disabled={!orchestratorEnabled}
    >
      <span>{showRecommendations ? '▼' : '▶'} Model Recommendations</span>
    </button>

    {#if showRecommendations}
      <div class="recommendations">
        <p class="recommendations-intro">
          Models selected for key tasks based on your <strong>{qualityTier}</strong> tier:
        </p>
        <div class="recommendations-table">
          {#each Object.entries(recommendations) as [taskType, models]}
            <div class="recommendation-row">
              <div class="task-name">{formatTaskName(taskType)}</div>
              <div class="model-name">{models[qualityTier]}</div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>

  <!-- Info Panel -->
  <div class="info-panel">
    <h4>ℹ️ How It Works</h4>
    <ul>
      <li><strong>Budget:</strong> Uses only free Ollama models (Mistral, Qwen, DeepSeek R1)</li>
      <li><strong>Balanced:</strong> Mixes DeepSeek ($0.14/$0.28 per 1M tokens) with free local models</li>
      <li><strong>Premium:</strong> Uses Claude Sonnet 3.5, GPT-4o, and DeepSeek for optimal quality</li>
      <li>The orchestrator automatically selects the best model for each task type</li>
      <li>Set a monthly budget to prevent overspending (optional)</li>
    </ul>
  </div>

  <!-- Save Button -->
  <div class="actions">
    <button class="btn-save" on:click={saveSettings}>
      Save Orchestrator Settings
    </button>
  </div>

  <!-- Messages -->
  {#if saveMessage}
    <div class="message success">{saveMessage}</div>
  {/if}
  {#if errorMessage}
    <div class="message error">{errorMessage}</div>
  {/if}
</div>

<style>
  .settings-orchestrator {
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

  /* Toggle styles */
  .toggle-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .toggle-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    user-select: none;
  }

  .toggle-input {
    display: none;
  }

  .toggle-switch {
    position: relative;
    width: 48px;
    height: 24px;
    background: #404040;
    border-radius: 12px;
    transition: background 0.2s;
  }

  .toggle-switch::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 20px;
    height: 20px;
    background: #ffffff;
    border-radius: 50%;
    transition: transform 0.2s;
  }

  .toggle-input:checked + .toggle-switch {
    background: #00d9ff;
  }

  .toggle-input:checked + .toggle-switch::after {
    transform: translateX(24px);
  }

  .toggle-text {
    font-size: 1rem;
    font-weight: 500;
  }

  .help-text {
    margin: 0;
    font-size: 0.875rem;
    color: #888888;
    padding-left: 3.25rem;
  }

  /* Tier cards */
  .tier-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }

  .tier-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem;
    background: #1a1a1a;
    border: 2px solid #404040;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .tier-card:hover:not(:disabled) {
    border-color: #00d9ff;
    transform: translateY(-2px);
  }

  .tier-card.active {
    border-color: #00d9ff;
    background: #1a3a4a;
  }

  .tier-card:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .tier-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  .tier-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.25rem;
  }

  .tier-cost {
    font-size: 1rem;
    color: #00d9ff;
    font-weight: 500;
    margin-bottom: 0.5rem;
  }

  .tier-description {
    font-size: 0.875rem;
    color: #b0b0b0;
    text-align: center;
  }

  /* Usage selector */
  .usage-selector {
    margin-bottom: 1rem;
  }

  .usage-selector label {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .usage-selector select {
    flex: 1;
    padding: 0.5rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
  }

  .usage-selector select:focus {
    outline: none;
    border-color: #00d9ff;
  }

  .usage-selector select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Cost display */
  .cost-display {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .cost-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: #1a1a1a;
    border-radius: 4px;
  }

  .cost-label {
    color: #b0b0b0;
  }

  .cost-value {
    font-size: 1.25rem;
    font-weight: 600;
    color: #00d9ff;
    font-family: 'JetBrains Mono', monospace;
  }

  /* Budget input */
  .budget-input-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .budget-input {
    flex: 1;
    padding: 0.75rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
  }

  .budget-input:focus {
    outline: none;
    border-color: #00d9ff;
  }

  .budget-input.warning {
    border-color: #ffb000;
  }

  .budget-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .currency {
    color: #b0b0b0;
    font-weight: 500;
  }

  /* Budget progress */
  .budget-progress {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .progress-bar {
    width: 100%;
    height: 8px;
    background: #404040;
    border-radius: 4px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    transition: width 0.3s, background-color 0.3s;
  }

  .progress-text {
    font-size: 0.875rem;
    color: #b0b0b0;
    font-family: 'JetBrains Mono', monospace;
  }

  .budget-warning {
    padding: 0.75rem;
    background: #ffb00020;
    border: 1px solid #ffb000;
    border-radius: 4px;
    color: #ffb000;
    font-weight: 500;
  }

  .budget-warning.error {
    background: #ff444420;
    border-color: #ff4444;
    color: #ff4444;
  }

  /* Recommendations */
  .recommendations-toggle {
    width: 100%;
    padding: 0.75rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #00d9ff;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    transition: background 0.2s;
  }

  .recommendations-toggle:hover:not(:disabled) {
    background: #252525;
  }

  .recommendations-toggle:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .recommendations {
    margin-top: 1rem;
  }

  .recommendations-intro {
    margin: 0 0 1rem 0;
    color: #b0b0b0;
  }

  .recommendations-table {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .recommendation-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: #1a1a1a;
    border-radius: 4px;
  }

  .task-name {
    color: #b0b0b0;
  }

  .model-name {
    color: #00d9ff;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
  }

  /* Info panel */
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

  /* Actions */
  .actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
  }

  .btn-save {
    padding: 0.75rem 2rem;
    background: #00d9ff;
    color: #1a1a1a;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-save:hover {
    background: #00b8d9;
  }

  /* Messages */
  .message {
    margin-top: 1rem;
    padding: 0.75rem;
    border-radius: 4px;
    font-weight: 500;
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
</style>
