<!--
  SettingsOrchestrator.svelte - AI Model Quality Tier Selection

  P0 CRITICAL: This component enables intelligent model selection.

  Quality Tiers:
  - Budget ($0/month): Local models only (Mistral, Llama)
  - Balanced (~$0.50-1/month): Mix of local + cheap cloud (DeepSeek, Qwen)
  - Premium (~$3-5/month): Best models for each task (Claude, GPT-4o)
-->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';

  // Current settings
  let enabled = false;
  let qualityTier = 'budget';
  let monthlyBudget = null;
  let preferLocal = false;

  // Spend tracking
  let currentSpend = 0;
  let currentMonth = '';

  // Cost estimates
  let costEstimates = {
    budget: 0,
    balanced: 0.50,
    premium: 3.00
  };

  // Model recommendations preview
  let recommendations = {};

  let isLoading = true;
  let isSaving = false;

  // Tier descriptions
  const tierInfo = {
    budget: {
      name: 'Budget',
      cost: '$0/month',
      description: 'Local models only (Mistral, Llama). Fast but limited quality.',
      icon: 'leaf',
      color: 'var(--success, #3fb950)',
      features: [
        'Free forever',
        'No API keys needed',
        'Fast local inference',
        'Quality score: 6/10'
      ]
    },
    balanced: {
      name: 'Balanced',
      cost: '~$0.50-1/month',
      description: 'Mix of local + affordable cloud models. Best value.',
      icon: 'scale',
      color: 'var(--accent-cyan, #58a6ff)',
      features: [
        'DeepSeek V3 for complex tasks',
        'Qwen for coordination',
        'Local fallback available',
        'Quality score: 8/10'
      ]
    },
    premium: {
      name: 'Premium',
      cost: '~$3-5/month',
      description: 'Best models for each task type. Maximum quality.',
      icon: 'crown',
      color: 'var(--accent-gold, #d4a574)',
      features: [
        'Claude 3.5 for narrative',
        'GPT-4o for analysis',
        'Optimal model per task',
        'Quality score: 10/10'
      ]
    }
  };

  const tierIcons = {
    leaf: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path>
      <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path>
    </svg>`,
    scale: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"></path>
      <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"></path>
      <path d="M7 21h10"></path>
      <path d="M12 3v18"></path>
      <path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"></path>
    </svg>`,
    crown: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="m2 4 3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"></path>
    </svg>`
  };

  onMount(async () => {
    await loadSettings();
    await loadCostEstimates();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const settings = await apiClient.getSettingsCategory('orchestrator');
      enabled = settings.enabled || false;
      qualityTier = settings.quality_tier || 'budget';
      monthlyBudget = settings.monthly_budget;
      preferLocal = settings.prefer_local || false;
      currentMonth = settings.current_month || '';
      currentSpend = settings.current_month_spend || 0;
    } catch (e) {
      console.error('Failed to load orchestrator settings:', e);
    } finally {
      isLoading = false;
    }
  }

  async function loadCostEstimates() {
    try {
      // Get estimates for each tier
      for (const tier of ['budget', 'balanced', 'premium']) {
        const estimate = await apiClient.estimateCost(tier, 100);
        costEstimates[tier] = estimate.estimated_monthly_cost_usd;
      }
    } catch (e) {
      console.error('Failed to load cost estimates:', e);
    }
  }

  async function selectTier(tier) {
    qualityTier = tier;
    await saveSettings();
  }

  async function toggleEnabled() {
    enabled = !enabled;
    await saveSettings();
  }

  async function saveSettings() {
    isSaving = true;
    try {
      await apiClient.setSetting('orchestrator.enabled', enabled);
      await apiClient.setSetting('orchestrator.quality_tier', qualityTier);
      if (monthlyBudget !== null) {
        await apiClient.setSetting('orchestrator.monthly_budget', monthlyBudget);
      }
      await apiClient.setSetting('orchestrator.prefer_local', preferLocal);

      addToast({ type: 'success', message: 'Orchestrator settings saved!' });
    } catch (e) {
      console.error('Failed to save settings:', e);
      addToast({ type: 'error', message: 'Failed to save settings' });
    } finally {
      isSaving = false;
    }
  }

  async function setBudget(value) {
    monthlyBudget = value;
    await saveSettings();
  }

  // Calculate spend percentage
  $: spendPercentage = monthlyBudget ? Math.min(100, (currentSpend / monthlyBudget) * 100) : 0;
  $: spendStatus = spendPercentage >= 100 ? 'over' : spendPercentage >= 80 ? 'warning' : 'ok';
</script>

<div class="settings-orchestrator">
  <header class="section-header">
    <div class="header-title">
      <h2>AI Model Selection</h2>
      <label class="toggle-switch">
        <input type="checkbox" checked={enabled} on:change={toggleEnabled} />
        <span class="toggle-slider"></span>
        <span class="toggle-label">{enabled ? 'Enabled' : 'Disabled'}</span>
      </label>
    </div>
    <p class="section-description">
      The Model Orchestrator automatically selects the best AI model for each task based on your quality tier.
      {#if !enabled}
        <strong>Enable to use intelligent model selection.</strong>
      {/if}
    </p>
  </header>

  {#if isLoading}
    <div class="loading-state">
      <div class="spinner"></div>
      <span>Loading settings...</span>
    </div>
  {:else}
    <!-- Quality Tier Selection -->
    <div class="tier-selection">
      <h3>Quality Tier</h3>
      <div class="tier-cards">
        {#each Object.entries(tierInfo) as [tierId, info]}
          <button
            class="tier-card {qualityTier === tierId ? 'selected' : ''}"
            on:click={() => selectTier(tierId)}
            disabled={!enabled}
            style="--tier-color: {info.color}"
          >
            <div class="tier-icon">{@html tierIcons[info.icon]}</div>
            <div class="tier-header">
              <span class="tier-name">{info.name}</span>
              <span class="tier-cost">{info.cost}</span>
            </div>
            <p class="tier-description">{info.description}</p>
            <ul class="tier-features">
              {#each info.features as feature}
                <li>{feature}</li>
              {/each}
            </ul>
            {#if qualityTier === tierId}
              <div class="tier-selected-badge">Selected</div>
            {/if}
          </button>
        {/each}
      </div>
    </div>

    <!-- Budget Controls -->
    <div class="budget-section">
      <h3>Monthly Budget</h3>
      <div class="budget-controls">
        <div class="budget-presets">
          <button
            class="preset-btn {monthlyBudget === null ? 'active' : ''}"
            on:click={() => setBudget(null)}
            disabled={!enabled}
          >
            No Limit
          </button>
          <button
            class="preset-btn {monthlyBudget === 1 ? 'active' : ''}"
            on:click={() => setBudget(1)}
            disabled={!enabled}
          >
            $1
          </button>
          <button
            class="preset-btn {monthlyBudget === 2 ? 'active' : ''}"
            on:click={() => setBudget(2)}
            disabled={!enabled}
          >
            $2
          </button>
          <button
            class="preset-btn {monthlyBudget === 5 ? 'active' : ''}"
            on:click={() => setBudget(5)}
            disabled={!enabled}
          >
            $5
          </button>
        </div>

        {#if monthlyBudget !== null}
          <div class="spend-tracker">
            <div class="spend-header">
              <span class="spend-label">Current Month Spend</span>
              <span class="spend-amount ${spendStatus}">
                ${currentSpend.toFixed(2)} / ${monthlyBudget.toFixed(2)}
              </span>
            </div>
            <div class="spend-bar">
              <div
                class="spend-fill {spendStatus}"
                style="width: {spendPercentage}%"
              ></div>
            </div>
            {#if spendPercentage >= 80}
              <p class="spend-warning">
                {#if spendPercentage >= 100}
                  Budget exceeded! Orchestrator will use local models only.
                {:else}
                  Approaching budget limit. Consider increasing budget.
                {/if}
              </p>
            {/if}
          </div>
        {/if}
      </div>
    </div>

    <!-- Preferences -->
    <div class="preferences-section">
      <h3>Preferences</h3>
      <label class="checkbox-option" class:disabled={!enabled}>
        <input
          type="checkbox"
          checked={preferLocal}
          on:change={() => { preferLocal = !preferLocal; saveSettings(); }}
          disabled={!enabled}
        />
        <span class="checkbox-label">
          <strong>Prefer Local Models</strong>
          <span class="checkbox-description">
            Use local models when quality difference is small (saves cost)
          </span>
        </span>
      </label>
    </div>

    <!-- Cost Estimation -->
    <div class="cost-estimation">
      <h3>Estimated Monthly Costs</h3>
      <p class="estimation-note">Based on typical usage (~100 tasks/month)</p>
      <div class="cost-comparison">
        {#each Object.entries(tierInfo) as [tierId, info]}
          <div class="cost-item">
            <span class="cost-tier" style="color: {info.color}">{info.name}</span>
            <span class="cost-value">${costEstimates[tierId].toFixed(2)}</span>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .settings-orchestrator {
    max-width: 800px;
  }

  .section-header {
    margin-bottom: var(--space-6, 24px);
  }

  .header-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-2, 8px);
  }

  .header-title h2 {
    margin: 0;
    font-size: var(--text-xl, 18px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .section-description {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-relaxed, 1.7);
  }

  .section-description strong {
    color: var(--warning, #d29922);
  }

  /* Toggle Switch */
  .toggle-switch {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    cursor: pointer;
  }

  .toggle-switch input {
    display: none;
  }

  .toggle-slider {
    position: relative;
    width: 40px;
    height: 22px;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-full, 9999px);
    transition: all var(--transition-normal, 200ms ease);
  }

  .toggle-slider::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 16px;
    height: 16px;
    background: var(--text-muted, #6e7681);
    border-radius: 50%;
    transition: all var(--transition-normal, 200ms ease);
  }

  .toggle-switch input:checked + .toggle-slider {
    background: var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
    border-color: var(--accent-cyan, #58a6ff);
  }

  .toggle-switch input:checked + .toggle-slider::after {
    transform: translateX(18px);
    background: var(--accent-cyan, #58a6ff);
  }

  .toggle-label {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  /* Loading State */
  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-3, 12px);
    padding: var(--space-8, 32px);
    color: var(--text-secondary, #8b949e);
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border, #2d3a47);
    border-top-color: var(--accent-cyan, #58a6ff);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Tier Selection */
  .tier-selection {
    margin-bottom: var(--space-6, 24px);
  }

  .tier-selection h3,
  .budget-section h3,
  .preferences-section h3,
  .cost-estimation h3 {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-base, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .tier-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4, 16px);
  }

  .tier-card {
    position: relative;
    display: flex;
    flex-direction: column;
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 2px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    text-align: left;
    cursor: pointer;
    transition: all var(--transition-normal, 200ms ease);
  }

  .tier-card:hover:not(:disabled) {
    border-color: var(--tier-color);
    box-shadow: 0 0 16px color-mix(in srgb, var(--tier-color) 20%, transparent);
  }

  .tier-card.selected {
    border-color: var(--tier-color);
    background: color-mix(in srgb, var(--tier-color) 10%, var(--bg-tertiary));
  }

  .tier-card:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .tier-icon {
    width: 32px;
    height: 32px;
    margin-bottom: var(--space-3, 12px);
    color: var(--tier-color);
  }

  .tier-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: var(--space-2, 8px);
  }

  .tier-name {
    font-size: var(--text-base, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .tier-cost {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--tier-color);
  }

  .tier-description {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-normal, 1.5);
  }

  .tier-features {
    list-style: none;
    margin: 0;
    padding: 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .tier-features li {
    padding: var(--space-1, 4px) 0;
    padding-left: var(--space-4, 16px);
    position: relative;
  }

  .tier-features li::before {
    content: '✓';
    position: absolute;
    left: 0;
    color: var(--tier-color);
  }

  .tier-selected-badge {
    position: absolute;
    top: var(--space-2, 8px);
    right: var(--space-2, 8px);
    padding: 2px 8px;
    background: var(--tier-color);
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--bg-primary, #0f1419);
  }

  /* Budget Section */
  .budget-section {
    margin-bottom: var(--space-6, 24px);
  }

  .budget-controls {
    display: flex;
    flex-direction: column;
    gap: var(--space-4, 16px);
  }

  .budget-presets {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .preset-btn {
    padding: var(--space-2, 8px) var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-sm, 12px);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .preset-btn:hover:not(:disabled) {
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--text-primary, #e6edf3);
  }

  .preset-btn.active {
    background: var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--accent-cyan, #58a6ff);
  }

  .preset-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .spend-tracker {
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
  }

  .spend-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--space-2, 8px);
  }

  .spend-label {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .spend-amount {
    font-family: var(--font-mono, monospace);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
  }

  .spend-amount.ok { color: var(--success, #3fb950); }
  .spend-amount.warning { color: var(--warning, #d29922); }
  .spend-amount.over { color: var(--error, #f85149); }

  .spend-bar {
    height: 6px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-full, 9999px);
    overflow: hidden;
  }

  .spend-fill {
    height: 100%;
    border-radius: var(--radius-full, 9999px);
    transition: width var(--transition-normal, 200ms ease);
  }

  .spend-fill.ok { background: var(--success, #3fb950); }
  .spend-fill.warning { background: var(--warning, #d29922); }
  .spend-fill.over { background: var(--error, #f85149); }

  .spend-warning {
    margin: var(--space-2, 8px) 0 0 0;
    font-size: var(--text-xs, 11px);
    color: var(--warning, #d29922);
  }

  /* Preferences */
  .preferences-section {
    margin-bottom: var(--space-6, 24px);
  }

  .checkbox-option {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    cursor: pointer;
  }

  .checkbox-option.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .checkbox-option input {
    margin-top: 2px;
  }

  .checkbox-label {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .checkbox-label strong {
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
  }

  .checkbox-description {
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  /* Cost Estimation */
  .cost-estimation {
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
  }

  .estimation-note {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .cost-comparison {
    display: flex;
    gap: var(--space-6, 24px);
  }

  .cost-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .cost-tier {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
  }

  .cost-value {
    font-family: var(--font-mono, monospace);
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-bold, 700);
    color: var(--text-primary, #e6edf3);
  }
</style>
