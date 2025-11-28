<!--
  UsageIndicator.svelte - Cost tracking badge for status bar

  Features:
  - Shows estimated monthly cost (e.g., "~$3.42")
  - Color-coded based on threshold proximity
  - Click to expand breakdown by provider
  - Threshold notifications with dismiss

  Usage:
    <UsageIndicator />
-->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // State
  let totalCost = 0;
  let byProvider: Record<string, { cost: number; input_tokens: number; output_tokens: number }> = {};
  let loading = true;
  let error = '';
  let expanded = false;

  // Threshold alert
  let alert: {
    threshold_amount: number;
    current_cost: number;
    level: string;
    message: string;
    already_notified: boolean;
  } | null = null;
  let showAlert = false;

  // Current month
  let currentMonth = new Date().toISOString().slice(0, 7); // "2025-11"

  // Refresh interval
  let refreshInterval: ReturnType<typeof setInterval> | null = null;

  // Thresholds for color coding
  const thresholds = [
    { amount: 50, color: '#ff4444' },  // Critical - red
    { amount: 25, color: '#ff8844' },  // Warning - orange
    { amount: 10, color: '#ffbb00' },  // Caution - yellow
    { amount: 5, color: '#88cc00' },   // Info - yellow-green
    { amount: 0, color: '#00ff88' },   // Good - green
  ];

  onMount(() => {
    loadUsageSummary();
    checkThresholds();
    // Refresh every 60 seconds
    refreshInterval = setInterval(() => {
      loadUsageSummary();
      checkThresholds();
    }, 60000);
  });

  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  });

  async function loadUsageSummary() {
    try {
      const response = await fetch(`${BASE_URL}/usage/summary?month=${currentMonth}`);
      if (!response.ok) {
        throw new Error('Failed to load usage summary');
      }

      const data = await response.json();
      const summary = data.summary;

      totalCost = summary.total_cost || 0;
      byProvider = summary.by_provider || {};
      loading = false;

    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load usage';
      loading = false;
    }
  }

  async function checkThresholds() {
    try {
      const response = await fetch(`${BASE_URL}/usage/thresholds?month=${currentMonth}`);
      if (!response.ok) return;

      const data = await response.json();

      if (data.status === 'threshold_exceeded' && data.alert) {
        // Only show if not already notified
        if (!data.alert.already_notified) {
          alert = data.alert;
          showAlert = true;
        }
      }
    } catch {
      // Silently fail - thresholds are optional
    }
  }

  async function dismissAlert() {
    if (!alert) return;

    try {
      await fetch(`${BASE_URL}/usage/thresholds/dismiss`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          month: currentMonth,
          threshold_amount: alert.threshold_amount,
        }),
      });

      showAlert = false;
      alert = null;
    } catch {
      // Silently fail
    }
  }

  function getIndicatorColor(): string {
    for (const threshold of thresholds) {
      if (totalCost >= threshold.amount) {
        return threshold.color;
      }
    }
    return thresholds[thresholds.length - 1].color;
  }

  function formatCost(cost: number): string {
    if (cost === 0) return '$0';
    if (cost < 0.01) return '<$0.01';
    if (cost < 1) return `$${cost.toFixed(2)}`;
    return `$${cost.toFixed(2)}`;
  }

  function formatTokens(tokens: number): string {
    if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`;
    if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}K`;
    return tokens.toString();
  }

  function toggleExpanded() {
    expanded = !expanded;
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleExpanded();
    }
  }
</script>

<div class="usage-indicator">
  <button
    class="indicator-badge"
    style="--indicator-color: {getIndicatorColor()}"
    on:click={toggleExpanded}
    on:keydown={handleKeydown}
    aria-expanded={expanded}
    aria-label="Monthly AI usage cost"
  >
    {#if loading}
      <span class="loading-dots">...</span>
    {:else}
      <span class="cost-icon">$</span>
      <span class="cost-value">{formatCost(totalCost)}</span>
    {/if}
  </button>

  {#if expanded}
    <div class="usage-dropdown">
      <div class="dropdown-header">
        <h4>AI Usage This Month</h4>
        <span class="month-label">{currentMonth}</span>
      </div>

      <div class="total-section">
        <span class="total-label">Total Estimated Cost</span>
        <span class="total-value" style="color: {getIndicatorColor()}">{formatCost(totalCost)}</span>
      </div>

      {#if Object.keys(byProvider).length > 0}
        <div class="provider-breakdown">
          <h5>By Provider</h5>
          {#each Object.entries(byProvider) as [provider, data]}
            <div class="provider-row">
              <span class="provider-name">{provider}</span>
              <span class="provider-tokens">
                {formatTokens(data.input_tokens + data.output_tokens)} tokens
              </span>
              <span class="provider-cost">{formatCost(data.cost)}</span>
            </div>
          {/each}
        </div>
      {:else}
        <div class="no-usage">
          <span>No usage recorded yet</span>
        </div>
      {/if}

      <div class="dropdown-footer">
        <span class="footer-note">
          Costs are estimates based on provider pricing
        </span>
      </div>
    </div>
  {/if}

  <!-- Threshold Alert -->
  {#if showAlert && alert}
    <div class="alert-overlay" role="alert">
      <div class="alert-content alert-{alert.level}">
        <div class="alert-header">
          <span class="alert-icon">
            {#if alert.level === 'critical'}
              &#9888;
            {:else if alert.level === 'warning'}
              &#9888;
            {:else}
              &#8505;
            {/if}
          </span>
          <span class="alert-title">Usage Alert</span>
        </div>
        <p class="alert-message">{alert.message}</p>
        <div class="alert-details">
          Current: <strong>{formatCost(alert.current_cost)}</strong> this month
        </div>
        <button class="alert-dismiss" on:click={dismissAlert}>
          Got it
        </button>
      </div>
    </div>
  {/if}
</div>

<!-- Click outside to close dropdown -->
{#if expanded}
  <div
    class="backdrop"
    on:click={() => expanded = false}
    on:keydown={(e) => e.key === 'Escape' && (expanded = false)}
    role="button"
    tabindex="-1"
    aria-label="Close usage dropdown"
  ></div>
{/if}

<style>
  .usage-indicator {
    position: relative;
    display: flex;
    align-items: center;
  }

  .indicator-badge {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--indicator-color, #00ff88);
    border-radius: 4px;
    color: var(--indicator-color, #00ff88);
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    cursor: pointer;
    transition: all 0.2s;
  }

  .indicator-badge:hover {
    background: var(--bg-tertiary, #242d38);
  }

  .cost-icon {
    opacity: 0.7;
  }

  .cost-value {
    font-weight: 600;
  }

  .loading-dots {
    animation: blink 1s infinite;
  }

  @keyframes blink {
    0%, 50% { opacity: 1; }
    25%, 75% { opacity: 0.3; }
  }

  /* Dropdown */
  .usage-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 0.5rem;
    width: 280px;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 100;
    overflow: hidden;
  }

  .dropdown-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .dropdown-header h4 {
    margin: 0;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-primary, #e6edf3);
  }

  .month-label {
    font-size: 0.7rem;
    color: var(--text-secondary, #8b949e);
    padding: 0.125rem 0.375rem;
    background: var(--bg-primary, #0f1419);
    border-radius: 3px;
  }

  .total-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .total-label {
    font-size: 0.8rem;
    color: var(--text-secondary, #8b949e);
  }

  .total-value {
    font-size: 1.25rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
  }

  .provider-breakdown {
    padding: 0.75rem 1rem;
  }

  .provider-breakdown h5 {
    margin: 0 0 0.5rem 0;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .provider-row {
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 0.5rem;
    align-items: center;
    padding: 0.375rem 0;
    font-size: 0.8rem;
  }

  .provider-name {
    color: var(--accent-cyan, #58a6ff);
    font-weight: 500;
    text-transform: capitalize;
  }

  .provider-tokens {
    color: var(--text-secondary, #8b949e);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
  }

  .provider-cost {
    color: var(--text-primary, #e6edf3);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
  }

  .no-usage {
    padding: 1.5rem;
    text-align: center;
    color: var(--text-secondary, #8b949e);
    font-size: 0.8rem;
  }

  .dropdown-footer {
    padding: 0.5rem 1rem;
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .footer-note {
    font-size: 0.65rem;
    color: var(--text-secondary, #8b949e);
  }

  /* Alert */
  .alert-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .alert-content {
    background: var(--bg-secondary, #1a2027);
    border-radius: 12px;
    padding: 1.5rem;
    max-width: 400px;
    width: 90%;
    text-align: center;
  }

  .alert-content.alert-info {
    border: 2px solid #88cc00;
  }

  .alert-content.alert-warning {
    border: 2px solid #ffbb00;
  }

  .alert-content.alert-critical {
    border: 2px solid #ff4444;
  }

  .alert-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .alert-icon {
    font-size: 1.5rem;
  }

  .alert-info .alert-icon { color: #88cc00; }
  .alert-warning .alert-icon { color: #ffbb00; }
  .alert-critical .alert-icon { color: #ff4444; }

  .alert-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary, #e6edf3);
  }

  .alert-message {
    color: var(--text-secondary, #8b949e);
    margin: 0 0 1rem 0;
    line-height: 1.5;
  }

  .alert-details {
    font-size: 0.9rem;
    color: var(--text-primary, #e6edf3);
    margin-bottom: 1.5rem;
  }

  .alert-details strong {
    color: var(--accent-cyan, #58a6ff);
    font-family: 'JetBrains Mono', monospace;
  }

  .alert-dismiss {
    padding: 0.625rem 1.5rem;
    background: var(--accent-cyan, #58a6ff);
    color: #000;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .alert-dismiss:hover {
    background: #79b8ff;
  }

  /* Backdrop for closing dropdown */
  .backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 99;
  }
</style>
