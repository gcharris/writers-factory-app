<script lang="ts">
  import { onMount } from 'svelte';

  // API key state
  let apiKeys = {
    openai: '',
    anthropic: '',
    deepseek: '',
    qwen: ''
  };

  let savedKeys = {
    openai: false,
    anthropic: false,
    deepseek: false,
    qwen: false
  };

  let testingKeys = {
    openai: false,
    anthropic: false,
    deepseek: false,
    qwen: false
  };

  let testResults = {
    openai: null as boolean | null,
    anthropic: null as boolean | null,
    deepseek: null as boolean | null,
    qwen: null as boolean | null
  };

  let showKeys = {
    openai: false,
    anthropic: false,
    deepseek: false,
    qwen: false
  };

  let saveMessage = '';
  let isSaving = false;

  const BASE_URL = "http://localhost:8000";

  onMount(async () => {
    await loadApiKeys();
  });

  /**
   * Load existing API keys from settings
   */
  async function loadApiKeys() {
    try {
      const response = await fetch(`${BASE_URL}/settings/category/agents`);
      if (response.ok) {
        const data = await response.json();

        // Check which keys are saved (masked as '***')
        if (data.openai_api_key) {
          savedKeys.openai = true;
          apiKeys.openai = data.openai_api_key === '***' ? '' : data.openai_api_key;
        }
        if (data.anthropic_api_key) {
          savedKeys.anthropic = true;
          apiKeys.anthropic = data.anthropic_api_key === '***' ? '' : data.anthropic_api_key;
        }
        if (data.deepseek_api_key) {
          savedKeys.deepseek = true;
          apiKeys.deepseek = data.deepseek_api_key === '***' ? '' : data.deepseek_api_key;
        }
        if (data.qwen_api_key) {
          savedKeys.qwen = true;
          apiKeys.qwen = data.qwen_api_key === '***' ? '' : data.qwen_api_key;
        }
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
    }
  }

  /**
   * Save API keys to settings
   */
  async function saveApiKeys() {
    isSaving = true;
    saveMessage = '';

    try {
      const keysToSave = {} as any;

      // Only save non-empty keys
      if (apiKeys.openai) keysToSave.openai_api_key = apiKeys.openai;
      if (apiKeys.anthropic) keysToSave.anthropic_api_key = apiKeys.anthropic;
      if (apiKeys.deepseek) keysToSave.deepseek_api_key = apiKeys.deepseek;
      if (apiKeys.qwen) keysToSave.qwen_api_key = apiKeys.qwen;

      const response = await fetch(`${BASE_URL}/settings/category/agents`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(keysToSave)
      });

      if (response.ok) {
        saveMessage = '✅ API keys saved successfully';

        // Update saved status
        savedKeys.openai = !!apiKeys.openai;
        savedKeys.anthropic = !!apiKeys.anthropic;
        savedKeys.deepseek = !!apiKeys.deepseek;
        savedKeys.qwen = !!apiKeys.qwen;

        // Clear message after 3 seconds
        setTimeout(() => { saveMessage = ''; }, 3000);
      } else {
        saveMessage = '❌ Failed to save API keys';
      }
    } catch (error) {
      console.error('Failed to save API keys:', error);
      saveMessage = '❌ Error saving API keys';
    } finally {
      isSaving = false;
    }
  }

  /**
   * Test API key connection
   */
  async function testApiKey(provider: 'openai' | 'anthropic' | 'deepseek' | 'qwen') {
    testingKeys[provider] = true;
    testResults[provider] = null;

    try {
      // Simple test: try to get agent status
      const response = await fetch(`${BASE_URL}/agents`);

      if (response.ok) {
        const agents = await response.json();
        // Check if this provider's agent is available
        const isAvailable = agents.some((a: any) =>
          a.provider === provider && a.status === 'available'
        );
        testResults[provider] = isAvailable;
      } else {
        testResults[provider] = false;
      }
    } catch (error) {
      console.error(`Failed to test ${provider} API key:`, error);
      testResults[provider] = false;
    } finally {
      testingKeys[provider] = false;
    }
  }

  /**
   * Delete API key
   */
  async function deleteApiKey(provider: 'openai' | 'anthropic' | 'deepseek' | 'qwen') {
    if (!confirm(`Delete ${provider} API key?`)) return;

    apiKeys[provider] = '';
    savedKeys[provider] = false;
    testResults[provider] = null;

    await saveApiKeys();
  }

  function toggleShowKey(provider: 'openai' | 'anthropic' | 'deepseek' | 'qwen') {
    showKeys[provider] = !showKeys[provider];
  }
</script>

<div class="settings-agents">
  <div class="header">
    <h2>API Keys & Agent Configuration</h2>
    <p class="description">
      Configure cloud AI provider API keys to unlock Voice Calibration, Director Mode, and Model Orchestrator features.
    </p>
  </div>

  <div class="api-keys-grid">
    <!-- OpenAI -->
    <div class="api-key-card">
      <div class="card-header">
        <h3>OpenAI (GPT-4o)</h3>
        {#if savedKeys.openai}
          <span class="badge badge-success">✓ Configured</span>
        {:else}
          <span class="badge badge-warning">Not configured</span>
        {/if}
      </div>

      <div class="key-input-group">
        <div class="input-wrapper">
          <input
            type={showKeys.openai ? 'text' : 'password'}
            bind:value={apiKeys.openai}
            placeholder="sk-..."
            class="key-input"
          />
          <button
            type="button"
            class="toggle-visibility"
            on:click={() => toggleShowKey('openai')}
          >
            {showKeys.openai ? '👁️' : '👁️‍🗨️'}
          </button>
        </div>

        <div class="button-group">
          <button
            type="button"
            class="btn-test"
            on:click={() => testApiKey('openai')}
            disabled={!apiKeys.openai || testingKeys.openai}
          >
            {testingKeys.openai ? 'Testing...' : 'Test'}
          </button>

          {#if savedKeys.openai}
            <button
              type="button"
              class="btn-delete"
              on:click={() => deleteApiKey('openai')}
            >
              Delete
            </button>
          {/if}
        </div>
      </div>

      {#if testResults.openai !== null}
        <div class="test-result {testResults.openai ? 'success' : 'error'}">
          {testResults.openai ? '✓ Connection successful' : '✗ Connection failed'}
        </div>
      {/if}

      <p class="help-text">
        Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI Platform</a>
      </p>
    </div>

    <!-- Anthropic (Claude) -->
    <div class="api-key-card">
      <div class="card-header">
        <h3>Anthropic (Claude)</h3>
        {#if savedKeys.anthropic}
          <span class="badge badge-success">✓ Configured</span>
        {:else}
          <span class="badge badge-warning">Not configured</span>
        {/if}
      </div>

      <div class="key-input-group">
        <div class="input-wrapper">
          <input
            type={showKeys.anthropic ? 'text' : 'password'}
            bind:value={apiKeys.anthropic}
            placeholder="sk-ant-..."
            class="key-input"
          />
          <button
            type="button"
            class="toggle-visibility"
            on:click={() => toggleShowKey('anthropic')}
          >
            {showKeys.anthropic ? '👁️' : '👁️‍🗨️'}
          </button>
        </div>

        <div class="button-group">
          <button
            type="button"
            class="btn-test"
            on:click={() => testApiKey('anthropic')}
            disabled={!apiKeys.anthropic || testingKeys.anthropic}
          >
            {testingKeys.anthropic ? 'Testing...' : 'Test'}
          </button>

          {#if savedKeys.anthropic}
            <button
              type="button"
              class="btn-delete"
              on:click={() => deleteApiKey('anthropic')}
            >
              Delete
            </button>
          {/if}
        </div>
      </div>

      {#if testResults.anthropic !== null}
        <div class="test-result {testResults.anthropic ? 'success' : 'error'}">
          {testResults.anthropic ? '✓ Connection successful' : '✗ Connection failed'}
        </div>
      {/if}

      <p class="help-text">
        Get your API key from <a href="https://console.anthropic.com/settings/keys" target="_blank">Anthropic Console</a>
      </p>
    </div>

    <!-- DeepSeek -->
    <div class="api-key-card">
      <div class="card-header">
        <h3>DeepSeek (Budget)</h3>
        {#if savedKeys.deepseek}
          <span class="badge badge-success">✓ Configured</span>
        {:else}
          <span class="badge badge-warning">Not configured</span>
        {/if}
      </div>

      <div class="key-input-group">
        <div class="input-wrapper">
          <input
            type={showKeys.deepseek ? 'text' : 'password'}
            bind:value={apiKeys.deepseek}
            placeholder="sk-..."
            class="key-input"
          />
          <button
            type="button"
            class="toggle-visibility"
            on:click={() => toggleShowKey('deepseek')}
          >
            {showKeys.deepseek ? '👁️' : '👁️‍🗨️'}
          </button>
        </div>

        <div class="button-group">
          <button
            type="button"
            class="btn-test"
            on:click={() => testApiKey('deepseek')}
            disabled={!apiKeys.deepseek || testingKeys.deepseek}
          >
            {testingKeys.deepseek ? 'Testing...' : 'Test'}
          </button>

          {#if savedKeys.deepseek}
            <button
              type="button"
              class="btn-delete"
              on:click={() => deleteApiKey('deepseek')}
            >
              Delete
            </button>
          {/if}
        </div}
      </div>

      {#if testResults.deepseek !== null}
        <div class="test-result {testResults.deepseek ? 'success' : 'error'}">
          {testResults.deepseek ? '✓ Connection successful' : '✗ Connection failed'}
        </div>
      {/if}

      <p class="help-text">
        Get your API key from <a href="https://platform.deepseek.com/api_keys" target="_blank">DeepSeek Platform</a>
      </p>
    </div>

    <!-- Qwen -->
    <div class="api-key-card">
      <div class="card-header">
        <h3>Qwen (Budget)</h3>
        {#if savedKeys.qwen}
          <span class="badge badge-success">✓ Configured</span>
        {:else}
          <span class="badge badge-warning">Not configured</span>
        {/if}
      </div>

      <div class="key-input-group">
        <div class="input-wrapper">
          <input
            type={showKeys.qwen ? 'text' : 'password'}
            bind:value={apiKeys.qwen}
            placeholder="sk-..."
            class="key-input"
          />
          <button
            type="button"
            class="toggle-visibility"
            on:click={() => toggleShowKey('qwen')}
          >
            {showKeys.qwen ? '👁️' : '👁️‍🗨️'}
          </button>
        </div>

        <div class="button-group">
          <button
            type="button"
            class="btn-test"
            on:click={() => testApiKey('qwen')}
            disabled={!apiKeys.qwen || testingKeys.qwen}
          >
            {testingKeys.qwen ? 'Testing...' : 'Test'}
          </button>

          {#if savedKeys.qwen}
            <button
              type="button"
              class="btn-delete"
              on:click={() => deleteApiKey('qwen')}
            >
              Delete
            </button>
          {/if}
        </div>
      </div>

      {#if testResults.qwen !== null}
        <div class="test-result {testResults.qwen ? 'success' : 'error'}">
          {testResults.qwen ? '✓ Connection successful' : '✗ Connection failed'}
        </div>
      {/if}

      <p class="help-text">
        Get your API key from <a href="https://dashscope.console.aliyun.com/apiKey" target="_blank">Qwen DashScope</a>
      </p>
    </div>
  </div>

  <!-- Save button -->
  <div class="actions">
    <button
      type="button"
      class="btn-save"
      on:click={saveApiKeys}
      disabled={isSaving}
    >
      {isSaving ? 'Saving...' : 'Save API Keys'}
    </button>

    {#if saveMessage}
      <div class="save-message {saveMessage.includes('✅') ? 'success' : 'error'}">
        {saveMessage}
      </div>
    {/if}
  </div>

  <!-- Info panel -->
  <div class="info-panel">
    <h4>💡 Which keys do I need?</h4>
    <ul>
      <li><strong>Minimum</strong>: Any 1 cloud provider (OpenAI, Anthropic, or DeepSeek)</li>
      <li><strong>Recommended</strong>: OpenAI + Anthropic (enables voice tournaments)</li>
      <li><strong>Optimal</strong>: All 4 providers (full multi-model tournament capability)</li>
    </ul>

    <p class="cost-note">
      <strong>Cost estimate</strong>: Most writers spend $0.50-1/month (Balanced tier). Budget tier available at $0/month using local models only.
    </p>
  </div>
</div>

<style>
  .settings-agents {
    padding: 2rem;
    max-width: 1200px;
  }

  .header {
    margin-bottom: 2rem;
  }

  .header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.5rem;
  }

  .description {
    color: #a0a0a0;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .api-keys-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .api-key-card {
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
    padding: 1.5rem;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .card-header h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
  }

  .badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: 500;
  }

  .badge-success {
    background: #00ff8820;
    color: #00ff88;
  }

  .badge-warning {
    background: #ffb00020;
    color: #ffb000;
  }

  .key-input-group {
    margin-bottom: 1rem;
  }

  .input-wrapper {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .key-input {
    flex: 1;
    background: #1a1a1a;
    border: 1px solid #404040;
    color: #ffffff;
    padding: 0.5rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem;
  }

  .key-input:focus {
    outline: none;
    border-color: #00d9ff;
  }

  .toggle-visibility {
    background: #1a1a1a;
    border: 1px solid #404040;
    color: #ffffff;
    padding: 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  .toggle-visibility:hover {
    border-color: #00d9ff;
  }

  .button-group {
    display: flex;
    gap: 0.5rem;
  }

  .btn-test, .btn-delete {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-test {
    background: #00d9ff20;
    border: 1px solid #00d9ff;
    color: #00d9ff;
  }

  .btn-test:hover:not(:disabled) {
    background: #00d9ff40;
  }

  .btn-test:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-delete {
    background: #ff336620;
    border: 1px solid #ff3366;
    color: #ff3366;
  }

  .btn-delete:hover {
    background: #ff336640;
  }

  .test-result {
    font-size: 0.875rem;
    padding: 0.5rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  .test-result.success {
    background: #00ff8820;
    color: #00ff88;
  }

  .test-result.error {
    background: #ff336620;
    color: #ff3366;
  }

  .help-text {
    font-size: 0.75rem;
    color: #666666;
    margin: 0;
  }

  .help-text a {
    color: #00d9ff;
    text-decoration: none;
  }

  .help-text a:hover {
    text-decoration: underline;
  }

  .actions {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .btn-save {
    background: #00d9ff;
    border: none;
    color: #1a1a1a;
    padding: 0.75rem 2rem;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-save:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-save:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .save-message {
    font-size: 0.875rem;
    font-weight: 500;
  }

  .save-message.success {
    color: #00ff88;
  }

  .save-message.error {
    color: #ff3366;
  }

  .info-panel {
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
    padding: 1.5rem;
  }

  .info-panel h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 1rem;
  }

  .info-panel ul {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem 0;
  }

  .info-panel li {
    color: #a0a0a0;
    font-size: 0.875rem;
    line-height: 1.8;
    padding-left: 1rem;
    position: relative;
  }

  .info-panel li::before {
    content: "•";
    position: absolute;
    left: 0;
    color: #00d9ff;
  }

  .cost-note {
    color: #a0a0a0;
    font-size: 0.875rem;
    margin: 0;
    padding-top: 1rem;
    border-top: 1px solid #404040;
  }
</style>
