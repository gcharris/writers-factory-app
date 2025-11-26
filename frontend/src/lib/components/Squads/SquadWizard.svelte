<!--
  SquadWizard.svelte - Multi-step wizard for squad selection and setup

  Steps:
  1. Hardware Scan - Detect system capabilities
  2. Squad Selection - Choose Local/Hybrid/Pro
  3. Setup - Configure API keys or confirm local setup

  Usage:
    <SquadWizard onComplete={() => handleComplete()} />
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import type { HardwareInfo, SquadPreset } from '$lib/api_client';

  const BASE_URL = 'http://localhost:8000';
  const dispatch = createEventDispatcher();

  // Props
  export let onComplete: () => void = () => {};
  export let initialStep: number = 1;

  // Wizard state
  let currentStep = initialStep;
  let loading = false;
  let error = '';

  // Step 1: Hardware scan
  let hardwareInfo: HardwareInfo | null = null;
  let scanningHardware = false;
  let hardwareScanComplete = false;

  // Step 2: Squad selection
  let availableSquads: SquadPreset[] = [];
  let selectedSquad: SquadPreset | null = null;
  let expandedSquadId: string | null = null;

  // Step 3: Setup/Apply
  let apiKeyInputs: Record<string, string> = {};
  let validatingKeys = false;
  let keyValidationStatus: Record<string, 'pending' | 'valid' | 'invalid'> = {};
  let applyingSquad = false;
  let applySuccess = false;
  let appliedModels: {
    foreman_strategic: string;
    foreman_coordinator: string;
    tournament_defaults: string[];
  } | null = null;

  // Squad icons mapping
  const squadIcons: Record<string, string> = {
    local: '&#127968;',    // House emoji
    hybrid: '&#128142;',   // Gem emoji
    pro: '&#128640;'       // Rocket emoji
  };

  onMount(async () => {
    await scanHardware();
  });

  async function scanHardware() {
    scanningHardware = true;
    error = '';

    try {
      // Simulate scanning animation (minimum 1.5s for UX)
      const [response] = await Promise.all([
        fetch(`${BASE_URL}/system/hardware`),
        new Promise(resolve => setTimeout(resolve, 1500))
      ]);

      if (!response.ok) {
        throw new Error('Failed to detect hardware');
      }

      hardwareInfo = await response.json();
      hardwareScanComplete = true;

      // Auto-load squads after hardware scan
      await loadAvailableSquads();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Hardware detection failed';
    } finally {
      scanningHardware = false;
    }
  }

  async function loadAvailableSquads() {
    try {
      const response = await fetch(`${BASE_URL}/squad/available`);
      if (!response.ok) {
        throw new Error('Failed to load squad presets');
      }

      const data = await response.json();
      availableSquads = data.squads || [];

      // Pre-select recommended squad
      const recommended = availableSquads.find(s => s.recommended);
      if (recommended) {
        selectedSquad = recommended;
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load squads';
    }
  }

  function goToStep(step: number) {
    currentStep = step;
  }

  function selectSquad(squad: SquadPreset) {
    selectedSquad = squad;
  }

  function toggleSquadDetails(squadId: string) {
    expandedSquadId = expandedSquadId === squadId ? null : squadId;
  }

  async function validateApiKey(keyName: string, value: string) {
    if (!value || value.length < 10) {
      keyValidationStatus[keyName] = 'invalid';
      return;
    }

    keyValidationStatus[keyName] = 'pending';
    validatingKeys = true;

    try {
      // Test the key by making a health check request
      const response = await fetch(`${BASE_URL}/settings/validate-api-key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key_name: keyName, key_value: value })
      });

      if (response.ok) {
        const data = await response.json();
        keyValidationStatus[keyName] = data.valid ? 'valid' : 'invalid';
      } else {
        // If endpoint doesn't exist, assume valid for now (backend will validate on use)
        keyValidationStatus[keyName] = 'valid';
      }
    } catch {
      // Assume valid if we can't validate (endpoint may not exist)
      keyValidationStatus[keyName] = 'valid';
    } finally {
      validatingKeys = false;
    }
  }

  function areRequirementsMet(): boolean {
    if (!selectedSquad) return false;

    // Check for missing API keys
    const missingKeys = selectedSquad.missing_requirements.filter(r => r.includes('_API_KEY'));
    if (missingKeys.length === 0) return true;

    // Check if all missing keys have been provided and validated
    return missingKeys.every(key => {
      const inputValue = apiKeyInputs[key];
      return inputValue && inputValue.length >= 10 && keyValidationStatus[key] !== 'invalid';
    });
  }

  async function applySelectedSquad() {
    if (!selectedSquad) return;

    applyingSquad = true;
    error = '';

    try {
      // First, save any API keys that were entered
      const missingKeys = selectedSquad.missing_requirements.filter(r => r.includes('_API_KEY'));
      for (const keyName of missingKeys) {
        const keyValue = apiKeyInputs[keyName];
        if (keyValue) {
          await fetch(`${BASE_URL}/settings/api-key`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key_name: keyName, key_value: keyValue })
          });
        }
      }

      // Apply the squad
      const response = await fetch(`${BASE_URL}/squad/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ squad_id: selectedSquad.id })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to apply squad');
      }

      const data = await response.json();
      appliedModels = data.applied_models;
      applySuccess = true;

    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to apply squad configuration';
    } finally {
      applyingSquad = false;
    }
  }

  function finishWizard() {
    dispatch('complete');
    onComplete();
  }

  function formatModelName(modelId: string): string {
    // Convert model IDs to friendly names
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

  function getKeyDisplayName(keyName: string): string {
    const displayMap: Record<string, string> = {
      'DEEPSEEK_API_KEY': 'DeepSeek',
      'QWEN_API_KEY': 'Qwen (Alibaba)',
      'ZHIPU_API_KEY': 'Zhipu AI',
      'OPENAI_API_KEY': 'OpenAI',
      'ANTHROPIC_API_KEY': 'Anthropic',
      'GOOGLE_API_KEY': 'Google',
      'XAI_API_KEY': 'xAI (Grok)',
      'MISTRAL_API_KEY': 'Mistral'
    };
    return displayMap[keyName] || keyName.replace('_API_KEY', '');
  }
</script>

<div class="squad-wizard">
  <!-- Progress Steps -->
  <div class="wizard-progress">
    <div class="progress-step {currentStep >= 1 ? 'active' : ''} {currentStep > 1 ? 'complete' : ''}">
      <div class="step-number">1</div>
      <div class="step-label">System Scan</div>
    </div>
    <div class="progress-connector {currentStep > 1 ? 'active' : ''}"></div>
    <div class="progress-step {currentStep >= 2 ? 'active' : ''} {currentStep > 2 ? 'complete' : ''}">
      <div class="step-number">2</div>
      <div class="step-label">Choose Squad</div>
    </div>
    <div class="progress-connector {currentStep > 2 ? 'active' : ''}"></div>
    <div class="progress-step {currentStep >= 3 ? 'active' : ''} {applySuccess ? 'complete' : ''}">
      <div class="step-number">3</div>
      <div class="step-label">Setup</div>
    </div>
  </div>

  <!-- Step Content -->
  <div class="wizard-content">
    <!-- Step 1: Hardware Scan -->
    {#if currentStep === 1}
      <div class="step-content step-hardware">
        <h2>System Scan</h2>
        <p class="step-description">Detecting your hardware capabilities to recommend the best squad...</p>

        {#if scanningHardware}
          <div class="scanning-animation">
            <div class="scanner-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
                <rect x="9" y="9" width="6" height="6"></rect>
                <line x1="9" y1="1" x2="9" y2="4"></line>
                <line x1="15" y1="1" x2="15" y2="4"></line>
                <line x1="9" y1="20" x2="9" y2="23"></line>
                <line x1="15" y1="20" x2="15" y2="23"></line>
              </svg>
            </div>
            <p class="scanning-text">Scanning system...</p>
          </div>
        {:else if hardwareScanComplete && hardwareInfo}
          <div class="hardware-results">
            <div class="hardware-grid">
              <div class="hardware-item">
                <span class="hardware-icon">&#128190;</span>
                <span class="hardware-label">RAM</span>
                <span class="hardware-value">{hardwareInfo.ram_gb}GB</span>
                <span class="hardware-status success">&#10003;</span>
              </div>
              <div class="hardware-item">
                <span class="hardware-icon">&#128187;</span>
                <span class="hardware-label">CPU</span>
                <span class="hardware-value">{hardwareInfo.cpu_cores} cores</span>
                <span class="hardware-status success">&#10003;</span>
              </div>
              <div class="hardware-item">
                <span class="hardware-icon">&#127912;</span>
                <span class="hardware-label">GPU</span>
                <span class="hardware-value">{hardwareInfo.gpu_available ? (hardwareInfo.gpu_name || 'Available') : 'Not detected'}</span>
                <span class="hardware-status {hardwareInfo.gpu_available ? 'success' : 'warning'}">{hardwareInfo.gpu_available ? '&#10003;' : '&#9888;'}</span>
              </div>
              <div class="hardware-item">
                <span class="hardware-icon">&#129433;</span>
                <span class="hardware-label">Ollama</span>
                <span class="hardware-value">{hardwareInfo.ollama_installed ? `v${hardwareInfo.ollama_version}` : 'Not installed'}</span>
                <span class="hardware-status {hardwareInfo.ollama_installed ? 'success' : 'warning'}">{hardwareInfo.ollama_installed ? '&#10003;' : '&#9888;'}</span>
              </div>
            </div>

            {#if hardwareInfo.ollama_installed && hardwareInfo.ollama_models.length > 0}
              <div class="installed-models">
                <h4>Installed Local Models</h4>
                <div class="model-tags">
                  {#each hardwareInfo.ollama_models as model}
                    <span class="model-tag">{model}</span>
                  {/each}
                </div>
              </div>
            {/if}

            <div class="recommendation-box">
              <span class="rec-icon">&#128161;</span>
              <span class="rec-text">Recommended max model size: <strong>{hardwareInfo.recommended_max_params}</strong></span>
            </div>
          </div>
        {/if}

        {#if error}
          <div class="error-message">{error}</div>
        {/if}

        <div class="step-actions">
          <button
            class="btn-primary"
            on:click={() => goToStep(2)}
            disabled={!hardwareScanComplete}
          >
            Continue to Squad Selection
          </button>
        </div>
      </div>
    {/if}

    <!-- Step 2: Squad Selection -->
    {#if currentStep === 2}
      <div class="step-content step-selection">
        <h2>Choose Your Squad</h2>
        <p class="step-description">Select a squad that matches your needs and budget</p>

        <div class="squad-cards">
          {#each availableSquads as squad}
            <button
              class="squad-card {selectedSquad?.id === squad.id ? 'selected' : ''} {!squad.available ? 'unavailable' : ''}"
              on:click={() => selectSquad(squad)}
            >
              {#if squad.recommended}
                <div class="recommended-badge">Recommended</div>
              {/if}

              <div class="squad-icon">{@html squadIcons[squad.id] || '&#128736;'}</div>
              <h3 class="squad-name">{squad.name}</h3>
              <p class="squad-description">{squad.description}</p>

              <div class="squad-cost">
                {#if squad.cost_estimate.monthly_usd === 0}
                  <span class="cost-free">Free Forever</span>
                {:else}
                  <span class="cost-amount">${squad.cost_estimate.monthly_usd.toFixed(0)}/month</span>
                {/if}
              </div>

              <div class="squad-availability">
                {#if squad.available}
                  <span class="availability-tag available">&#10003; Available</span>
                {:else if squad.missing_requirements.length > 0}
                  <span class="availability-tag warning">&#9888; {squad.missing_requirements.length} requirement{squad.missing_requirements.length > 1 ? 's' : ''} needed</span>
                {:else}
                  <span class="availability-tag unavailable">&#10007; Unavailable</span>
                {/if}
              </div>

              <button
                class="btn-details"
                on:click|stopPropagation={() => toggleSquadDetails(squad.id)}
              >
                {expandedSquadId === squad.id ? '&#9660; Hide Details' : '&#9654; Show Details'}
              </button>

              {#if expandedSquadId === squad.id}
                <div class="squad-details">
                  <div class="detail-section">
                    <h4>Models Included</h4>
                    <ul class="model-list">
                      <li><span class="role">Strategic:</span> {formatModelName(squad.default_models.foreman_strategic)}</li>
                      <li><span class="role">Coordinator:</span> {formatModelName(squad.default_models.foreman_coordinator)}</li>
                      <li><span class="role">Tournament:</span> {squad.default_models.tournament.map(formatModelName).join(', ')}</li>
                    </ul>
                  </div>

                  {#if squad.missing_requirements.length > 0}
                    <div class="detail-section missing-reqs">
                      <h4>Missing Requirements</h4>
                      <ul class="missing-list">
                        {#each squad.missing_requirements as req}
                          <li class="missing-item">&#10007; {req.replace('_API_KEY', ' API Key')}</li>
                        {/each}
                      </ul>
                    </div>
                  {/if}

                  {#if squad.warnings.length > 0}
                    <div class="detail-section warnings">
                      <h4>Warnings</h4>
                      <ul class="warning-list">
                        {#each squad.warnings as warning}
                          <li class="warning-item">&#9888; {warning}</li>
                        {/each}
                      </ul>
                    </div>
                  {/if}
                </div>
              {/if}
            </button>
          {/each}
        </div>

        {#if error}
          <div class="error-message">{error}</div>
        {/if}

        <div class="step-actions">
          <button class="btn-secondary" on:click={() => goToStep(1)}>
            Back
          </button>
          <button
            class="btn-primary"
            on:click={() => goToStep(3)}
            disabled={!selectedSquad}
          >
            Continue with {selectedSquad?.name || 'Squad'}
          </button>
        </div>
      </div>
    {/if}

    <!-- Step 3: Setup/Apply -->
    {#if currentStep === 3}
      <div class="step-content step-setup">
        {#if applySuccess}
          <!-- Success State -->
          <div class="success-state">
            <div class="success-icon">&#10003;</div>
            <h2>{selectedSquad?.name} Activated!</h2>
            <p class="success-description">Your squad is now configured and ready to use.</p>

            {#if appliedModels}
              <div class="applied-config">
                <h4>Configuration Applied</h4>
                <div class="config-grid">
                  <div class="config-item">
                    <span class="config-label">Strategic Model</span>
                    <span class="config-value">{formatModelName(appliedModels.foreman_strategic)}</span>
                  </div>
                  <div class="config-item">
                    <span class="config-label">Coordinator Model</span>
                    <span class="config-value">{formatModelName(appliedModels.foreman_coordinator)}</span>
                  </div>
                  <div class="config-item">
                    <span class="config-label">Tournament Models</span>
                    <span class="config-value">{appliedModels.tournament_defaults.length} models</span>
                  </div>
                </div>
              </div>
            {/if}

            <div class="step-actions">
              <button class="btn-primary" on:click={finishWizard}>
                Finish Setup
              </button>
            </div>
          </div>
        {:else}
          <!-- Setup Form -->
          <h2>Setup {selectedSquad?.name}</h2>

          {#if selectedSquad && selectedSquad.missing_requirements.length > 0}
            <p class="step-description">Enter the required API keys to enable this squad</p>

            <div class="api-key-form">
              {#each selectedSquad.missing_requirements.filter(r => r.includes('_API_KEY')) as keyName}
                <div class="api-key-input-group">
                  <label for={keyName}>
                    <span class="key-provider">{getKeyDisplayName(keyName)}</span> API Key
                  </label>
                  <div class="input-with-status">
                    <input
                      type="password"
                      id={keyName}
                      bind:value={apiKeyInputs[keyName]}
                      placeholder="Enter your API key..."
                      on:blur={() => validateApiKey(keyName, apiKeyInputs[keyName])}
                    />
                    {#if keyValidationStatus[keyName] === 'pending'}
                      <span class="validation-status pending">&#8987;</span>
                    {:else if keyValidationStatus[keyName] === 'valid'}
                      <span class="validation-status valid">&#10003;</span>
                    {:else if keyValidationStatus[keyName] === 'invalid'}
                      <span class="validation-status invalid">&#10007;</span>
                    {/if}
                  </div>
                  <a
                    class="get-key-link"
                    href="https://platform.{getKeyDisplayName(keyName).toLowerCase().replace(' ', '')}.com"
                    target="_blank"
                    rel="noopener"
                  >
                    Get an API key &#8599;
                  </a>
                </div>
              {/each}
            </div>
          {:else}
            <p class="step-description">All requirements are met. Click below to apply the configuration.</p>

            <div class="ready-to-apply">
              <div class="ready-icon">{@html squadIcons[selectedSquad?.id || 'local']}</div>
              <p>Ready to configure <strong>{selectedSquad?.name}</strong></p>
              <ul class="config-preview">
                <li>Strategic: {formatModelName(selectedSquad?.default_models.foreman_strategic || '')}</li>
                <li>Coordinator: {formatModelName(selectedSquad?.default_models.foreman_coordinator || '')}</li>
                <li>Tournament: {selectedSquad?.default_models.tournament.length || 0} models</li>
              </ul>
            </div>
          {/if}

          {#if applyingSquad}
            <div class="applying-state">
              <div class="applying-spinner"></div>
              <p>Applying configuration...</p>
            </div>
          {/if}

          {#if error}
            <div class="error-message">{error}</div>
          {/if}

          <div class="step-actions">
            <button class="btn-secondary" on:click={() => goToStep(2)}>
              Back
            </button>
            <button
              class="btn-primary"
              on:click={applySelectedSquad}
              disabled={!areRequirementsMet() || applyingSquad}
            >
              {applyingSquad ? 'Applying...' : 'Apply Squad'}
            </button>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .squad-wizard {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
    color: #ffffff;
  }

  /* Progress Steps */
  .wizard-progress {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 2.5rem;
    padding: 0 1rem;
  }

  .progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .step-number {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #2d2d2d;
    border: 2px solid #404040;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1rem;
    color: #888;
    transition: all 0.3s;
  }

  .progress-step.active .step-number {
    border-color: #00d9ff;
    color: #00d9ff;
  }

  .progress-step.complete .step-number {
    background: #00d9ff;
    border-color: #00d9ff;
    color: #1a1a1a;
  }

  .step-label {
    font-size: 0.75rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .progress-step.active .step-label {
    color: #00d9ff;
  }

  .progress-connector {
    width: 80px;
    height: 2px;
    background: #404040;
    margin: 0 0.5rem;
    margin-bottom: 1.5rem;
    transition: background 0.3s;
  }

  .progress-connector.active {
    background: #00d9ff;
  }

  /* Step Content */
  .wizard-content {
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 12px;
    padding: 2rem;
  }

  .step-content h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #ffffff;
  }

  .step-description {
    color: #b0b0b0;
    margin: 0 0 1.5rem 0;
  }

  /* Hardware Scan */
  .scanning-animation {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 3rem;
  }

  .scanner-icon {
    color: #00d9ff;
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
  }

  .scanning-text {
    margin-top: 1rem;
    color: #00d9ff;
    font-weight: 500;
  }

  .hardware-results {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .hardware-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
  }

  .hardware-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 8px;
    border: 1px solid #404040;
  }

  .hardware-icon {
    font-size: 1.5rem;
  }

  .hardware-label {
    flex: 1;
    color: #888;
    font-size: 0.875rem;
  }

  .hardware-value {
    font-weight: 600;
    color: #ffffff;
  }

  .hardware-status {
    font-size: 1rem;
  }

  .hardware-status.success {
    color: #00ff88;
  }

  .hardware-status.warning {
    color: #ffb000;
  }

  .installed-models {
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 8px;
    border: 1px solid #404040;
  }

  .installed-models h4 {
    margin: 0 0 0.75rem 0;
    font-size: 0.875rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .model-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .model-tag {
    padding: 0.25rem 0.75rem;
    background: #2d2d2d;
    border-radius: 4px;
    font-size: 0.875rem;
    font-family: 'JetBrains Mono', monospace;
    color: #00d9ff;
  }

  .recommendation-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: #1a3a4a30;
    border: 1px solid #00d9ff40;
    border-radius: 8px;
  }

  .rec-icon {
    font-size: 1.5rem;
  }

  .rec-text {
    color: #b0b0b0;
  }

  .rec-text strong {
    color: #00d9ff;
  }

  /* Squad Cards */
  .squad-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .squad-card {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem;
    background: #1a1a1a;
    border: 2px solid #404040;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
  }

  .squad-card:hover:not(.unavailable) {
    border-color: #00d9ff;
    transform: translateY(-2px);
  }

  .squad-card.selected {
    border-color: #00d9ff;
    background: #1a3a4a;
  }

  .squad-card.unavailable {
    opacity: 0.6;
  }

  .recommended-badge {
    position: absolute;
    top: -10px;
    right: -10px;
    padding: 0.25rem 0.75rem;
    background: linear-gradient(135deg, #00d9ff, #00ff88);
    color: #1a1a1a;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    border-radius: 4px;
  }

  .squad-icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
  }

  .squad-name {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #ffffff;
  }

  .squad-description {
    font-size: 0.875rem;
    color: #888;
    margin: 0 0 1rem 0;
  }

  .squad-cost {
    margin-bottom: 0.75rem;
  }

  .cost-free {
    color: #00ff88;
    font-weight: 600;
    font-size: 1.125rem;
  }

  .cost-amount {
    color: #00d9ff;
    font-weight: 600;
    font-size: 1.125rem;
  }

  .squad-availability {
    margin-bottom: 0.75rem;
  }

  .availability-tag {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .availability-tag.available {
    background: #00ff8820;
    color: #00ff88;
  }

  .availability-tag.warning {
    background: #ffb00020;
    color: #ffb000;
  }

  .availability-tag.unavailable {
    background: #ff444420;
    color: #ff4444;
  }

  .btn-details {
    background: transparent;
    border: none;
    color: #888;
    font-size: 0.75rem;
    cursor: pointer;
    padding: 0.5rem;
    transition: color 0.2s;
  }

  .btn-details:hover {
    color: #00d9ff;
  }

  .squad-details {
    width: 100%;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #404040;
    text-align: left;
  }

  .detail-section {
    margin-bottom: 1rem;
  }

  .detail-section h4 {
    font-size: 0.75rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 0.5rem 0;
  }

  .model-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .model-list li {
    padding: 0.25rem 0;
    font-size: 0.875rem;
    color: #b0b0b0;
  }

  .model-list .role {
    color: #00d9ff;
    font-weight: 500;
  }

  .missing-list,
  .warning-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .missing-item {
    padding: 0.25rem 0;
    font-size: 0.875rem;
    color: #ff4444;
  }

  .warning-item {
    padding: 0.25rem 0;
    font-size: 0.875rem;
    color: #ffb000;
  }

  /* Setup Form */
  .api-key-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .api-key-input-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .api-key-input-group label {
    font-size: 0.875rem;
    color: #b0b0b0;
  }

  .key-provider {
    color: #00d9ff;
    font-weight: 600;
  }

  .input-with-status {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .input-with-status input {
    flex: 1;
    padding: 0.75rem 1rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 6px;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem;
  }

  .input-with-status input:focus {
    outline: none;
    border-color: #00d9ff;
  }

  .validation-status {
    font-size: 1.25rem;
    width: 24px;
    text-align: center;
  }

  .validation-status.pending {
    color: #888;
    animation: spin 1s linear infinite;
  }

  .validation-status.valid {
    color: #00ff88;
  }

  .validation-status.invalid {
    color: #ff4444;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .get-key-link {
    font-size: 0.75rem;
    color: #888;
    text-decoration: none;
    transition: color 0.2s;
  }

  .get-key-link:hover {
    color: #00d9ff;
  }

  .ready-to-apply {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    background: #1a1a1a;
    border-radius: 12px;
    margin-bottom: 1.5rem;
  }

  .ready-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .config-preview {
    list-style: none;
    padding: 0;
    margin: 1rem 0 0 0;
    text-align: left;
  }

  .config-preview li {
    padding: 0.25rem 0;
    font-size: 0.875rem;
    color: #888;
  }

  .applying-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .applying-spinner {
    width: 24px;
    height: 24px;
    border: 3px solid #404040;
    border-top-color: #00d9ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  /* Success State */
  .success-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 2rem;
  }

  .success-icon {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: #00ff8830;
    color: #00ff88;
    font-size: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
  }

  .success-description {
    color: #b0b0b0;
    margin-bottom: 2rem;
  }

  .applied-config {
    width: 100%;
    max-width: 400px;
    padding: 1.5rem;
    background: #1a1a1a;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .applied-config h4 {
    margin: 0 0 1rem 0;
    font-size: 0.875rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .config-grid {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .config-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #404040;
  }

  .config-item:last-child {
    border-bottom: none;
  }

  .config-label {
    color: #888;
    font-size: 0.875rem;
  }

  .config-value {
    color: #00d9ff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem;
  }

  /* Actions */
  .step-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #404040;
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.875rem;
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

  .btn-secondary:hover {
    background: #2d2d2d;
    color: #ffffff;
  }

  /* Error Message */
  .error-message {
    padding: 1rem;
    background: #ff444420;
    border: 1px solid #ff4444;
    border-radius: 6px;
    color: #ff4444;
    margin-bottom: 1rem;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .squad-wizard {
      padding: 1rem;
    }

    .wizard-progress {
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .progress-connector {
      width: 40px;
    }

    .squad-cards {
      grid-template-columns: 1fr;
    }

    .hardware-grid {
      grid-template-columns: 1fr;
    }

    .step-actions {
      flex-direction: column;
    }

    .btn-primary,
    .btn-secondary {
      width: 100%;
    }
  }
</style>
