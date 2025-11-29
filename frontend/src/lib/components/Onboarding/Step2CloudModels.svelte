<!--
  Step2CloudModels.svelte - Cloud AI Models Overview

  Purpose: Honest explanation of which models are free (MVP subsidized) vs require user keys.
  This is an INFO screen - no configuration happens here.
-->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  // Model providers organized by region
  const regions = [
    {
      name: 'US',
      subtitle: 'Key Required',
      models: [
        { provider: 'OpenAI', model: 'GPT-4o', pricing: '$2.50/$10 per 1M tokens', status: 'key-required' },
        { provider: 'Anthropic', model: 'Claude', pricing: '$3/$15 per 1M tokens', status: 'key-required' },
        { provider: 'xAI', model: 'Grok', pricing: '$2/$10 per 1M tokens', status: 'key-required' },
        { provider: 'Google', model: 'Gemini', pricing: '$0.075/$0.30 per 1M tokens', status: 'key-required' }
      ]
    },
    {
      name: 'China / Asia',
      subtitle: 'Free for MVP',
      models: [
        { provider: 'DeepSeek', model: 'V3', pricing: '$0.27/$1.10 per 1M tokens', status: 'free-mvp' },
        { provider: 'Alibaba', model: 'Qwen', pricing: '$0.50/$2 per 1M tokens', status: 'free-mvp' },
        { provider: 'Moonshot', model: 'Kimi', pricing: '$0.20/$0.80 per 1M tokens', status: 'free-mvp' },
        { provider: 'Zhipu', model: 'ChatGLM', pricing: '$0.30/$1.20 per 1M tokens', status: 'free-mvp' },
        { provider: 'Tencent', model: 'Hunyuan', pricing: 'Free tier available', status: 'free-mvp' }
      ]
    },
    {
      name: 'Europe',
      subtitle: 'Free for MVP',
      models: [
        { provider: 'Mistral AI', model: 'Mistral Large', pricing: '$0.15/$0.45 per 1M tokens', status: 'free-mvp' }
      ]
    },
    {
      name: 'Russia',
      subtitle: 'Free for MVP',
      models: [
        { provider: 'Yandex', model: 'YandexGPT', pricing: 'Variable pricing', status: 'free-mvp' }
      ]
    },
    {
      name: 'Local',
      subtitle: 'Always Free',
      models: [
        { provider: 'Ollama', model: 'Various', pricing: 'Free (runs on your machine)', status: 'local' }
      ]
    }
  ];

  function handleBack() {
    dispatch('back');
  }

  function handleContinue() {
    dispatch('next');
  }
</script>

<div class="step-cloud-models">
  <div class="step-header">
    <h2>Cloud AI Models</h2>
    <p class="step-description">
      For serious writing, we recommend cloud AI models. Here's what's available.
    </p>
  </div>

  <div class="intro-note">
    <p>
      The first 4 US providers require your own API keys (pay-per-use, no monthly fee - you only pay for tokens you actually use).
      All other models are <strong>FREE for MVP early users</strong>.
    </p>
  </div>

  <!-- Model Regions -->
  <div class="regions-container">
    {#each regions as region}
      <div class="region-section">
        <div class="region-header">
          <h3 class="region-name">{region.name}</h3>
          <span class="region-subtitle {region.models[0].status}">{region.subtitle}</span>
        </div>

        <div class="models-list">
          {#each region.models as model}
            <div class="model-row">
              <div class="model-info">
                <span class="provider-name">{model.provider}</span>
                <span class="model-name">{model.model}</span>
              </div>
              <div class="model-pricing">{model.pricing}</div>
              <div class="model-status">
                {#if model.status === 'key-required'}
                  <span class="status-badge key-required">Key required</span>
                {:else if model.status === 'free-mvp'}
                  <span class="status-badge free-mvp">Free for MVP</span>
                {:else if model.status === 'local'}
                  <span class="status-badge local">Local</span>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/each}
  </div>

  <!-- Why Get Keys Info Box -->
  <div class="info-box">
    <h4>Why Get Your Own Keys?</h4>
    <ul>
      <li>No monthly subscription - pay only for what you use</li>
      <li>Premium models write better prose for final drafts</li>
      <li>Use cheap models for brainstorming, premium for polishing</li>
      <li>Our "tournament" feature lets you compare outputs from multiple models to find YOUR voice</li>
    </ul>
    <div class="cost-note">
      Even with all 4 US keys, your monthly cost will probably not be more than you'd pay for one chatbot subscription.
    </div>
  </div>

  <!-- Skip Note -->
  <p class="skip-note">
    You can add keys later in Settings.
  </p>

  <!-- Navigation -->
  <div class="step-actions">
    <button class="btn-secondary" on:click={handleBack}>
      <span class="arrow">←</span>
      Back
    </button>
    <button class="btn-primary" on:click={handleContinue}>
      Continue
      <span class="arrow">→</span>
    </button>
  </div>
</div>

<style>
  .step-cloud-models {
    max-width: 800px;
    margin: 0 auto;
  }

  .step-header {
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .step-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #ffffff;
  }

  .step-description {
    color: var(--text-secondary, #8b949e);
    margin: 0;
    font-size: 1rem;
  }

  /* Intro Note */
  .intro-note {
    padding: 1rem;
    background: var(--bg-primary, #0f1419);
    border-radius: 8px;
    border: 1px solid var(--border, #2d3a47);
    margin-bottom: 1.5rem;
  }

  .intro-note p {
    margin: 0;
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    line-height: 1.6;
  }

  .intro-note strong {
    color: var(--success, #3fb950);
  }

  /* Regions Container */
  .regions-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .region-section {
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 8px;
    overflow: hidden;
  }

  .region-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .region-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .region-subtitle {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }

  .region-subtitle.key-required {
    background: rgba(210, 153, 34, 0.2);
    color: var(--warning, #d29922);
  }

  .region-subtitle.free-mvp {
    background: rgba(63, 185, 80, 0.2);
    color: var(--success, #3fb950);
  }

  .region-subtitle.local {
    background: rgba(88, 166, 255, 0.2);
    color: #58a6ff;
  }

  /* Models List */
  .models-list {
    padding: 0.5rem;
  }

  .model-row {
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    gap: 1rem;
    align-items: center;
    padding: 0.5rem 0.5rem;
    border-radius: 4px;
    transition: background 0.2s;
  }

  .model-row:hover {
    background: var(--bg-secondary, #1a2027);
  }

  .model-info {
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
  }

  .provider-name {
    font-weight: 600;
    color: #ffffff;
    font-size: 0.875rem;
  }

  .model-name {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
  }

  .model-pricing {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    font-family: 'JetBrains Mono', monospace;
  }

  .model-status {
    text-align: right;
  }

  .status-badge {
    font-size: 0.65rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .status-badge.key-required {
    background: rgba(210, 153, 34, 0.2);
    color: var(--warning, #d29922);
  }

  .status-badge.free-mvp {
    background: rgba(63, 185, 80, 0.2);
    color: var(--success, #3fb950);
  }

  .status-badge.local {
    background: rgba(88, 166, 255, 0.2);
    color: #58a6ff;
  }

  /* Info Box */
  .info-box {
    padding: 1.25rem;
    background: rgba(0, 217, 255, 0.05);
    border: 1px solid rgba(0, 217, 255, 0.3);
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .info-box h4 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--accent-cyan, #00d9ff);
    margin: 0 0 0.75rem 0;
  }

  .info-box ul {
    margin: 0 0 1rem 0;
    padding-left: 1.25rem;
  }

  .info-box li {
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    line-height: 1.8;
    margin-bottom: 0.25rem;
  }

  .cost-note {
    padding-top: 0.75rem;
    border-top: 1px solid var(--border, #2d3a47);
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    font-style: italic;
  }

  /* Skip Note */
  .skip-note {
    text-align: center;
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    margin: 0 0 1.5rem 0;
  }

  /* Navigation */
  .step-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-primary:hover {
    background: #00b8d9;
  }

  .btn-secondary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: var(--text-secondary, #8b949e);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 6px;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    background: var(--bg-tertiary, #242d38);
    border-color: var(--accent-cyan, #00d9ff);
    color: var(--accent-cyan, #00d9ff);
  }

  .arrow {
    font-size: 1.25rem;
  }

  /* Responsive */
  @media (max-width: 600px) {
    .model-row {
      grid-template-columns: 1fr auto;
      gap: 0.5rem;
    }

    .model-pricing {
      grid-column: 1 / -1;
      text-align: left;
    }

    .step-actions {
      flex-direction: column;
      gap: 1rem;
    }

    .btn-primary, .btn-secondary {
      width: 100%;
      justify-content: center;
    }
  }
</style>
