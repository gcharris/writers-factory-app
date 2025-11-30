<script lang="ts">
  import { assistantName, assistantSettings } from '$lib/stores';

  // Preset name options
  const presetNames = ['Muse', 'Scribe', 'Quill', 'Ghost', 'Companion'];

  let selectedPreset = $assistantName;
  let customName = '';
  let useCustomName = !presetNames.includes($assistantName);

  // Initialize custom name if not using a preset
  if (useCustomName) {
    customName = $assistantName;
    selectedPreset = '';
  }

  let saveMessage = '';

  // Settings from store
  let autoIncludeFile = $assistantSettings.autoIncludeFile;
  let showStage = $assistantSettings.showStage;
  let confirmStageChange = $assistantSettings.confirmStageChange;
  let voiceEnabled = $assistantSettings.voiceEnabled ?? true;
  let voiceLanguage = $assistantSettings.voiceLanguage ?? 'en-US';
  let voiceContinuous = $assistantSettings.voiceContinuous ?? true;

  // Available voice languages
  const voiceLanguages = [
    { code: 'en-US', name: 'English (US)' },
    { code: 'en-GB', name: 'English (UK)' },
    { code: 'en-AU', name: 'English (Australia)' },
    { code: 'es-ES', name: 'Spanish (Spain)' },
    { code: 'es-MX', name: 'Spanish (Mexico)' },
    { code: 'fr-FR', name: 'French (France)' },
    { code: 'de-DE', name: 'German' },
    { code: 'it-IT', name: 'Italian' },
    { code: 'pt-BR', name: 'Portuguese (Brazil)' },
    { code: 'pt-PT', name: 'Portuguese (Portugal)' },
    { code: 'nl-NL', name: 'Dutch' },
    { code: 'ru-RU', name: 'Russian' },
    { code: 'ja-JP', name: 'Japanese' },
    { code: 'ko-KR', name: 'Korean' },
    { code: 'zh-CN', name: 'Chinese (Simplified)' },
    { code: 'zh-TW', name: 'Chinese (Traditional)' },
  ];

  // Check if Web Speech API is supported
  let speechSupported = typeof window !== 'undefined' &&
    (window.SpeechRecognition || window.webkitSpeechRecognition);

  function selectPreset(name: string) {
    selectedPreset = name;
    useCustomName = false;
    customName = '';
  }

  function enableCustomName() {
    useCustomName = true;
    selectedPreset = '';
  }

  function saveSettings() {
    // Determine the name to save
    const nameToSave = useCustomName && customName.trim()
      ? customName.trim()
      : selectedPreset || 'Muse';

    // Update stores
    assistantName.set(nameToSave);
    assistantSettings.set({
      autoIncludeFile,
      showStage,
      confirmStageChange,
      voiceEnabled,
      voiceLanguage,
      voiceContinuous
    });

    saveMessage = 'Settings saved!';
    setTimeout(() => saveMessage = '', 3000);
  }

  function resetToDefault() {
    selectedPreset = 'Muse';
    customName = '';
    useCustomName = false;
    autoIncludeFile = true;
    showStage = true;
    confirmStageChange = false;
    voiceEnabled = true;
    voiceLanguage = 'en-US';
    voiceContinuous = true;
  }
</script>

<div class="settings-assistant">
  <div class="header">
    <h2>Assistant</h2>
    <p class="subtitle">Personalize your writing assistant and chat experience.</p>
  </div>

  <!-- Name Section -->
  <div class="section">
    <h3>Assistant Name</h3>
    <p class="section-desc">Give your writing assistant a name that inspires you.</p>

    <div class="preset-selector">
      {#each presetNames as name}
        <button
          class="preset-btn {selectedPreset === name && !useCustomName ? 'active' : ''}"
          on:click={() => selectPreset(name)}
        >
          {name}
        </button>
      {/each}
      <button
        class="preset-btn custom {useCustomName ? 'active' : ''}"
        on:click={enableCustomName}
      >
        Custom
      </button>
    </div>

    {#if useCustomName}
      <div class="custom-name-input">
        <input
          type="text"
          bind:value={customName}
          placeholder="Enter a custom name..."
          maxlength="20"
        />
        <span class="char-count">{customName.length}/20</span>
      </div>
    {/if}

    <div class="preview">
      <span class="preview-label">Preview:</span>
      <span class="preview-name">
        {useCustomName && customName.trim() ? customName.trim() : selectedPreset || 'Muse'}
      </span>
    </div>
  </div>

  <!-- Chat Behavior Section -->
  <div class="section">
    <h3>Chat Behavior</h3>
    <p class="section-desc">Control how context is included in your conversations.</p>

    <div class="toggle-group">
      <label class="toggle-label">
        <input
          type="checkbox"
          bind:checked={autoIncludeFile}
          class="toggle-input"
        />
        <span class="toggle-switch"></span>
        <span class="toggle-text">Auto-include open file as context</span>
      </label>
      <p class="toggle-desc">
        When enabled, the currently open file in the editor will be automatically included as context for your messages.
      </p>
    </div>

    <div class="toggle-group">
      <label class="toggle-label">
        <input
          type="checkbox"
          bind:checked={showStage}
          class="toggle-input"
        />
        <span class="toggle-switch"></span>
        <span class="toggle-text">Show writing stage indicator</span>
      </label>
      <p class="toggle-desc">
        Display a dropdown showing your current writing stage (Conception, Voice, Execution, Polish).
      </p>
    </div>

    <div class="toggle-group">
      <label class="toggle-label">
        <input
          type="checkbox"
          bind:checked={confirmStageChange}
          class="toggle-input"
        />
        <span class="toggle-switch"></span>
        <span class="toggle-text">Confirm before changing stage</span>
      </label>
      <p class="toggle-desc">
        Ask for confirmation when manually switching between writing stages.
      </p>
    </div>
  </div>

  <!-- Voice Input Section -->
  <div class="section">
    <h3>Voice Input</h3>
    <p class="section-desc">Dictate your messages using your device's speech recognition.</p>

    {#if !speechSupported}
      <div class="warning-panel">
        <span class="warning-icon">⚠️</span>
        <span>Voice input is not supported in your current browser. Try using Chrome, Edge, or Safari.</span>
      </div>
    {:else}
      <div class="toggle-group">
        <label class="toggle-label">
          <input
            type="checkbox"
            bind:checked={voiceEnabled}
            class="toggle-input"
          />
          <span class="toggle-switch"></span>
          <span class="toggle-text">Enable voice input button</span>
        </label>
        <p class="toggle-desc">
          Show the microphone button in the chat input bar.
        </p>
      </div>

      {#if voiceEnabled}
        <div class="voice-options">
          <div class="option-group">
            <label class="option-label">Recognition Language</label>
            <select bind:value={voiceLanguage} class="select-input">
              {#each voiceLanguages as lang}
                <option value={lang.code}>{lang.name}</option>
              {/each}
            </select>
            <p class="option-desc">
              The language used for speech recognition. Choose the language you'll be speaking.
            </p>
          </div>

          <div class="toggle-group">
            <label class="toggle-label">
              <input
                type="checkbox"
                bind:checked={voiceContinuous}
                class="toggle-input"
              />
              <span class="toggle-switch"></span>
              <span class="toggle-text">Continuous listening</span>
            </label>
            <p class="toggle-desc">
              Keep listening until you click stop. When disabled, recognition stops after each pause.
            </p>
          </div>
        </div>
      {/if}
    {/if}
  </div>

  <!-- Info Panel -->
  <div class="info-panel">
    <h4>About Your Assistant</h4>
    <p>
      Your writing assistant is powered by AI and adapts to your current writing stage. It can help with:
    </p>
    <ul>
      <li><strong>Conception</strong> - Building your Story Bible, characters, and plot structure</li>
      <li><strong>Voice</strong> - Calibrating and refining your narrative voice</li>
      <li><strong>Execution</strong> - Drafting scenes with beat awareness</li>
      <li><strong>Polish</strong> - Editing for consistency, pacing, and continuity</li>
    </ul>
  </div>

  <!-- Actions -->
  <div class="actions">
    <button class="btn-secondary" on:click={resetToDefault}>
      Reset to Default
    </button>
    <button class="btn-save" on:click={saveSettings}>
      Save Settings
    </button>
  </div>

  {#if saveMessage}
    <div class="message success">{saveMessage}</div>
  {/if}
</div>

<style>
  .settings-assistant {
    padding: 0.75rem 1rem;
    max-width: 800px;
    color: #ffffff;
  }

  .header {
    margin-bottom: 0.75rem;
  }

  .header h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 0.25rem 0;
  }

  .subtitle {
    color: #b0b0b0;
    margin: 0;
    font-size: 0.8125rem;
  }

  .section {
    margin-bottom: 0.75rem;
    padding: 0.75rem 1rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 6px;
  }

  .section h3 {
    font-size: 0.9375rem;
    font-weight: 600;
    color: #d4a574;
    margin: 0 0 0.125rem 0;
  }

  .section-desc {
    color: #888888;
    margin: 0 0 0.5rem 0;
    font-size: 0.75rem;
  }

  /* Preset selector */
  .preset-selector {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .preset-btn {
    padding: 0.5rem 1rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 6px;
    color: #ffffff;
    font-weight: 500;
    font-size: 0.8125rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .preset-btn:hover {
    border-color: #d4a574;
  }

  .preset-btn.active {
    border-color: #d4a574;
    background: #3a2a1a;
  }

  .preset-btn.custom {
    font-style: italic;
    color: #b0b0b0;
  }

  .preset-btn.custom.active {
    color: #d4a574;
  }

  /* Custom name input */
  .custom-name-input {
    position: relative;
    margin-bottom: 0.5rem;
  }

  .custom-name-input input {
    width: 100%;
    padding: 0.5rem 0.75rem;
    padding-right: 3rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 6px;
    color: #ffffff;
    font-size: 0.875rem;
    transition: border-color 0.2s;
  }

  .custom-name-input input:focus {
    outline: none;
    border-color: #d4a574;
  }

  .custom-name-input input::placeholder {
    color: #666666;
  }

  .char-count {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.75rem;
    color: #666666;
  }

  /* Preview */
  .preview {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: #1a1a1a;
    border-radius: 6px;
  }

  .preview-label {
    color: #888888;
    font-size: 0.75rem;
  }

  .preview-name {
    color: #d4a574;
    font-weight: 600;
    font-size: 0.9375rem;
  }

  /* Toggle styles */
  .toggle-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-bottom: 0.625rem;
  }

  .toggle-group:last-child {
    margin-bottom: 0;
  }

  .toggle-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    user-select: none;
  }

  .toggle-input {
    display: none;
  }

  .toggle-switch {
    position: relative;
    width: 36px;
    height: 18px;
    background: #404040;
    border-radius: 9px;
    transition: background 0.2s;
    flex-shrink: 0;
  }

  .toggle-switch::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 14px;
    height: 14px;
    background: #ffffff;
    border-radius: 50%;
    transition: transform 0.2s;
  }

  .toggle-input:checked + .toggle-switch {
    background: #d4a574;
  }

  .toggle-input:checked + .toggle-switch::after {
    transform: translateX(18px);
  }

  .toggle-text {
    font-size: 0.8125rem;
    font-weight: 500;
  }

  .toggle-desc {
    margin: 0;
    padding-left: 2.5rem;
    font-size: 0.6875rem;
    color: #888888;
  }

  /* Info panel */
  .info-panel {
    padding: 0.75rem 1rem;
    background: #3a2a1a20;
    border: 1px solid #d4a57440;
    border-radius: 6px;
    margin-bottom: 0.75rem;
  }

  .info-panel h4 {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #d4a574;
    margin: 0 0 0.25rem 0;
  }

  .info-panel p {
    color: #b0b0b0;
    margin: 0 0 0.375rem 0;
    font-size: 0.75rem;
  }

  .info-panel ul {
    margin: 0;
    padding-left: 1.25rem;
  }

  .info-panel li {
    color: #b0b0b0;
    line-height: 1.4;
    margin-bottom: 0.125rem;
    font-size: 0.75rem;
  }

  .info-panel li strong {
    color: #ffffff;
  }

  /* Actions */
  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
  }

  .btn-secondary {
    padding: 0.5rem 1rem;
    background: transparent;
    color: #b0b0b0;
    border: 1px solid #404040;
    border-radius: 4px;
    font-weight: 500;
    font-size: 0.8125rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    border-color: #d4a574;
    color: #d4a574;
  }

  .btn-save {
    padding: 0.5rem 1.25rem;
    background: #d4a574;
    color: #1a1a1a;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.8125rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-save:hover {
    background: #c49464;
  }

  .message {
    margin-top: 0.5rem;
    padding: 0.5rem;
    border-radius: 4px;
    font-weight: 500;
    font-size: 0.75rem;
  }

  .message.success {
    background: #00ff8820;
    color: #00ff88;
    border: 1px solid #00ff88;
  }

  /* Voice settings styles */
  .warning-panel {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: #3a2a1a40;
    border: 1px solid #d4a57460;
    border-radius: 6px;
    color: #d4a574;
    font-size: 0.75rem;
  }

  .warning-icon {
    font-size: 1rem;
  }

  .voice-options {
    margin-top: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: #1a1a1a;
    border-radius: 6px;
  }

  .option-group {
    margin-bottom: 0.625rem;
  }

  .option-group:last-child {
    margin-bottom: 0;
  }

  .option-label {
    display: block;
    font-size: 0.75rem;
    font-weight: 500;
    color: #ffffff;
    margin-bottom: 0.25rem;
  }

  .select-input {
    width: 100%;
    padding: 0.375rem 0.5rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
    font-size: 0.75rem;
    cursor: pointer;
    transition: border-color 0.2s;
  }

  .select-input:focus {
    outline: none;
    border-color: #d4a574;
  }

  .select-input option {
    background: #2d2d2d;
    color: #ffffff;
  }

  .option-desc {
    margin: 0.25rem 0 0 0;
    font-size: 0.6875rem;
    color: #888888;
  }
</style>
