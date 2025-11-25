<!--
  StoryBibleWizard.svelte - Main Story Bible creation interface

  Multi-step wizard for creating the Story Bible:
  Step 0: Project setup (title, protagonist name)
  Step 1: Protagonist definition (Fatal Flaw, The Lie, Arc)
  Step 2: Beat Sheet (15-beat structure)
  Step 3: Theme definition
  Step 4: World Rules

  Features:
  - Smart scaffold option (AI-powered from NotebookLM)
  - Manual entry for each template
  - Progress tracking
  - NotebookLM integration for research
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import {
    foremanProjectTitle,
    foremanProtagonist,
    showStoryBibleWizard,
    wizardStep,
    storyBibleStatus,
    registeredNotebooks
  } from '$lib/stores';
  import NotebookRegistration from './NotebookRegistration.svelte';

  const dispatch = createEventDispatcher();

  // Form state
  let projectTitle = $foremanProjectTitle || '';
  let protagonistName = $foremanProtagonist || '';

  // Protagonist fields
  let protagonist = {
    fatalFlaw: '',
    theLie: '',
    trueCharacter: '',
    characterization: '',
    arcStart: '',
    arcMidpoint: '',
    arcResolution: ''
  };

  // Beat sheet (simplified for wizard)
  let beats = {
    openingImage: '',
    themeStated: '',
    catalyst: '',
    midpoint: '',
    allIsLost: '',
    finale: ''
  };
  let midpointType = 'false_victory';

  // Theme fields
  let theme = {
    central: '',
    statement: '',
    thesis: '',
    antithesis: ''
  };

  // World rules
  let world = {
    fundamentalRules: '',
    systemRules: '',
    socialRules: ''
  };

  // UI state
  let isLoading = false;
  let useSmartScaffold = false;
  let showNotebooks = false;

  // Steps configuration
  const steps = [
    { id: 0, name: 'Project', icon: 'folder' },
    { id: 1, name: 'Protagonist', icon: 'user' },
    { id: 2, name: 'Beats', icon: 'list' },
    { id: 3, name: 'Theme', icon: 'lightbulb' },
    { id: 4, name: 'World', icon: 'globe' }
  ];

  function nextStep() {
    if ($wizardStep < steps.length - 1) {
      $wizardStep = $wizardStep + 1;
    }
  }

  function prevStep() {
    if ($wizardStep > 0) {
      $wizardStep = $wizardStep - 1;
    }
  }

  function goToStep(step) {
    $wizardStep = step;
  }

  // Create story bible scaffolding
  async function createScaffold() {
    if (!projectTitle.trim() || !protagonistName.trim()) {
      addToast('Please enter project title and protagonist name', 'error');
      return;
    }

    isLoading = true;
    try {
      if (useSmartScaffold && $registeredNotebooks.length > 0) {
        // Use AI-powered scaffold with NotebookLM
        const notebook = $registeredNotebooks.find(n => n.role === 'world') || $registeredNotebooks[0];
        const result = await apiClient.runSmartScaffold(projectTitle, protagonistName, notebook?.id);
        addToast(`Created ${result.created_files.length} template files with AI enrichment`, 'success');
      } else {
        // Create basic scaffold
        const result = await apiClient.scaffoldStoryBible(projectTitle, protagonistName, {
          protagonist: {
            fatal_flaw: protagonist.fatalFlaw,
            the_lie: protagonist.theLie,
            true_character: protagonist.trueCharacter,
            characterization: protagonist.characterization,
            arc_start: protagonist.arcStart,
            arc_midpoint: protagonist.arcMidpoint,
            arc_resolution: protagonist.arcResolution
          },
          beat_sheet: {
            beat_1: beats.openingImage,
            beat_2: beats.themeStated,
            beat_4: beats.catalyst,
            midpoint_type: midpointType,
            beat_9: beats.midpoint,
            beat_11: beats.allIsLost,
            beat_14: beats.finale
          }
        });
        addToast(`Created ${result.created_files.length} template files`, 'success');
      }

      // Update stores
      $foremanProjectTitle = projectTitle;
      $foremanProtagonist = protagonistName;

      // Refresh status
      const status = await apiClient.getStoryBibleStatus();
      $storyBibleStatus = status;

      dispatch('complete', { projectTitle, protagonistName });
    } catch (error) {
      console.error('Failed to create scaffold:', error);
      addToast(`Failed to create Story Bible: ${error.message}`, 'error');
    } finally {
      isLoading = false;
    }
  }

  // Save current step data
  async function saveStep() {
    // For now, just advance - actual saving happens on complete
    nextStep();
  }

  // Complete the wizard
  async function completeWizard() {
    await createScaffold();
    $showStoryBibleWizard = false;
  }

  function handleClose() {
    $showStoryBibleWizard = false;
    dispatch('close');
  }

  // Load existing data if available
  onMount(async () => {
    if ($storyBibleStatus?.protagonist) {
      protagonist.fatalFlaw = $storyBibleStatus.protagonist.fatal_flaw || '';
      protagonist.theLie = $storyBibleStatus.protagonist.the_lie || '';
      protagonist.trueCharacter = $storyBibleStatus.protagonist.true_character || '';
      protagonist.characterization = $storyBibleStatus.protagonist.characterization || '';
      protagonist.arcStart = $storyBibleStatus.protagonist.arc_start || '';
      protagonist.arcMidpoint = $storyBibleStatus.protagonist.arc_midpoint || '';
      protagonist.arcResolution = $storyBibleStatus.protagonist.arc_resolution || '';
    }
  });
</script>

<div class="wizard-container">
  <!-- Progress steps -->
  <div class="wizard-progress">
    {#each steps as step, i}
      <button
        class="progress-step"
        class:active={$wizardStep === i}
        class:completed={$wizardStep > i}
        on:click={() => goToStep(i)}
      >
        <span class="step-number">{i + 1}</span>
        <span class="step-name">{step.name}</span>
      </button>
      {#if i < steps.length - 1}
        <div class="step-connector" class:active={$wizardStep > i}></div>
      {/if}
    {/each}
  </div>

  <!-- Step content -->
  <div class="wizard-content">
    {#if $wizardStep === 0}
      <!-- Step 0: Project Setup -->
      <div class="step-panel">
        <h3 class="step-title">Project Setup</h3>
        <p class="step-description">Enter your project details to get started.</p>

        <div class="form-group">
          <label for="project-title">Project Title</label>
          <input
            id="project-title"
            type="text"
            placeholder="e.g., The Midnight Cipher"
            bind:value={projectTitle}
          />
        </div>

        <div class="form-group">
          <label for="protagonist-name">Protagonist Name</label>
          <input
            id="protagonist-name"
            type="text"
            placeholder="e.g., Mickey Bardot"
            bind:value={protagonistName}
          />
        </div>

        <div class="smart-scaffold-option">
          <label class="checkbox-label">
            <input type="checkbox" bind:checked={useSmartScaffold} />
            <span>Use AI-powered scaffold (requires NotebookLM)</span>
          </label>
          {#if useSmartScaffold}
            <button class="link-btn" on:click={() => showNotebooks = !showNotebooks}>
              {showNotebooks ? 'Hide' : 'Configure'} Notebooks
            </button>
          {/if}
        </div>

        {#if showNotebooks}
          <div class="notebook-section">
            <NotebookRegistration />
          </div>
        {/if}
      </div>

    {:else if $wizardStep === 1}
      <!-- Step 1: Protagonist -->
      <div class="step-panel">
        <h3 class="step-title">Build Your Protagonist</h3>
        <p class="step-description">Define the core elements that drive your character.</p>

        <div class="form-group">
          <label for="fatal-flaw">Fatal Flaw</label>
          <p class="field-hint">The internal weakness that blocks their success</p>
          <textarea
            id="fatal-flaw"
            placeholder="e.g., Pride that blinds them to needing others..."
            bind:value={protagonist.fatalFlaw}
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="the-lie">The Lie</label>
          <p class="field-hint">The mistaken belief that drives the Fatal Flaw</p>
          <textarea
            id="the-lie"
            placeholder="e.g., 'I can only trust myself because everyone betrays you eventually...'"
            bind:value={protagonist.theLie}
            rows="3"
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="arc-start">Arc Start</label>
            <textarea
              id="arc-start"
              placeholder="Where they begin..."
              bind:value={protagonist.arcStart}
              rows="2"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="arc-resolution">Arc Resolution</label>
            <textarea
              id="arc-resolution"
              placeholder="How they change..."
              bind:value={protagonist.arcResolution}
              rows="2"
            ></textarea>
          </div>
        </div>
      </div>

    {:else if $wizardStep === 2}
      <!-- Step 2: Beat Sheet -->
      <div class="step-panel">
        <h3 class="step-title">Define Your Beat Sheet</h3>
        <p class="step-description">Key structural beats of your story (Save the Cat! methodology).</p>

        <div class="form-group">
          <label for="opening">Opening Image (1%)</label>
          <textarea
            id="opening"
            placeholder="Visual snapshot of the 'before' state..."
            bind:value={beats.openingImage}
            rows="2"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="theme">Theme Stated (5%)</label>
          <textarea
            id="theme"
            placeholder="Where the theme is hinted..."
            bind:value={beats.themeStated}
            rows="2"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="catalyst">Catalyst (10%)</label>
          <textarea
            id="catalyst"
            placeholder="The inciting incident..."
            bind:value={beats.catalyst}
            rows="2"
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="midpoint">Midpoint (50%)</label>
            <textarea
              id="midpoint"
              placeholder="False victory or defeat..."
              bind:value={beats.midpoint}
              rows="2"
            ></textarea>
          </div>
          <div class="form-group">
            <label>Midpoint Type</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" value="false_victory" bind:group={midpointType} />
                <span>False Victory</span>
              </label>
              <label class="radio-label">
                <input type="radio" value="false_defeat" bind:group={midpointType} />
                <span>False Defeat</span>
              </label>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="all-is-lost">All Is Lost (75%)</label>
          <textarea
            id="all-is-lost"
            placeholder="Lowest point - whiff of death..."
            bind:value={beats.allIsLost}
            rows="2"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="finale">Finale (80-99%)</label>
          <textarea
            id="finale"
            placeholder="Final confrontation..."
            bind:value={beats.finale}
            rows="2"
          ></textarea>
        </div>
      </div>

    {:else if $wizardStep === 3}
      <!-- Step 3: Theme -->
      <div class="step-panel">
        <h3 class="step-title">Define Your Theme</h3>
        <p class="step-description">The core idea your story explores.</p>

        <div class="form-group">
          <label for="central-theme">Central Theme</label>
          <textarea
            id="central-theme"
            placeholder="e.g., The cost of pursuing truth in a world that profits from lies..."
            bind:value={theme.central}
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="theme-statement">Theme Statement</label>
          <p class="field-hint">One sentence encapsulation (often stated in Beat 2)</p>
          <input
            id="theme-statement"
            type="text"
            placeholder="e.g., 'Some truths are worth any price.'"
            bind:value={theme.statement}
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="thesis">Thesis</label>
            <p class="field-hint">What the story argues is true</p>
            <textarea
              id="thesis"
              placeholder="The positive argument..."
              bind:value={theme.thesis}
              rows="2"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="antithesis">Antithesis</label>
            <p class="field-hint">The counter-argument</p>
            <textarea
              id="antithesis"
              placeholder="What antagonist embodies..."
              bind:value={theme.antithesis}
              rows="2"
            ></textarea>
          </div>
        </div>
      </div>

    {:else if $wizardStep === 4}
      <!-- Step 4: World Rules -->
      <div class="step-panel">
        <h3 class="step-title">Define World Rules</h3>
        <p class="step-description">The non-negotiable laws of your story world.</p>

        <div class="form-group">
          <label for="fundamental-rules">Fundamental Rules</label>
          <p class="field-hint">Laws that cannot be broken in your world</p>
          <textarea
            id="fundamental-rules"
            placeholder="e.g., Magic always has a price. The dead stay dead. Information is currency..."
            bind:value={world.fundamentalRules}
            rows="4"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="system-rules">Technology/Magic System</label>
          <textarea
            id="system-rules"
            placeholder="How special capabilities work..."
            bind:value={world.systemRules}
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="social-rules">Social Structure</label>
          <textarea
            id="social-rules"
            placeholder="How society is organized..."
            bind:value={world.socialRules}
            rows="3"
          ></textarea>
        </div>
      </div>
    {/if}
  </div>

  <!-- Navigation -->
  <div class="wizard-nav">
    <button class="nav-btn secondary" on:click={handleClose}>
      Cancel
    </button>

    <div class="nav-right">
      {#if $wizardStep > 0}
        <button class="nav-btn secondary" on:click={prevStep}>
          Back
        </button>
      {/if}

      {#if $wizardStep < steps.length - 1}
        <button class="nav-btn primary" on:click={nextStep}>
          Continue
        </button>
      {:else}
        <button class="nav-btn primary" on:click={completeWizard} disabled={isLoading}>
          {#if isLoading}
            <span class="spinner"></span>
            Creating...
          {:else}
            Create Story Bible
          {/if}
        </button>
      {/if}
    </div>
  </div>
</div>

<style>
  .wizard-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 80vh;
  }

  .wizard-progress {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-4, 16px);
    border-bottom: 1px solid var(--border, #2d3a47);
    background: var(--bg-tertiary, #242d38);
  }

  .progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: var(--space-2, 8px);
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .step-number {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--bg-elevated, #2d3640);
    border: 2px solid var(--border, #2d3a47);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-muted, #6e7681);
    transition: all var(--transition-fast, 100ms ease);
  }

  .progress-step.active .step-number {
    background: var(--accent-cyan, #58a6ff);
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  .progress-step.completed .step-number {
    background: var(--success, #3fb950);
    border-color: var(--success, #3fb950);
    color: var(--bg-primary, #0f1419);
  }

  .step-name {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .progress-step.active .step-name {
    color: var(--accent-cyan, #58a6ff);
  }

  .progress-step.completed .step-name {
    color: var(--success, #3fb950);
  }

  .step-connector {
    width: 40px;
    height: 2px;
    background: var(--border, #2d3a47);
    margin: 0 var(--space-1, 4px);
  }

  .step-connector.active {
    background: var(--success, #3fb950);
  }

  .wizard-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  .step-panel {
    max-width: 600px;
    margin: 0 auto;
  }

  .step-title {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .step-description {
    margin: 0 0 var(--space-4, 16px) 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .form-group {
    margin-bottom: var(--space-4, 16px);
  }

  .form-group label {
    display: block;
    margin-bottom: var(--space-1, 4px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .field-hint {
    margin: 0 0 var(--space-1, 4px) 0;
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .form-group input,
  .form-group textarea {
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

  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3, 12px);
  }

  .smart-scaffold-option {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
    margin-bottom: var(--space-4, 16px);
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
  }

  .checkbox-label input {
    width: auto;
    margin: 0;
  }

  .link-btn {
    background: transparent;
    border: none;
    color: var(--accent-cyan, #58a6ff);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
    text-decoration: underline;
  }

  .notebook-section {
    margin-top: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-md, 6px);
  }

  .radio-group {
    display: flex;
    gap: var(--space-3, 12px);
  }

  .radio-label {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
  }

  .radio-label input {
    margin: 0;
  }

  .wizard-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    border-top: 1px solid var(--border, #2d3a47);
    background: var(--bg-tertiary, #242d38);
  }

  .nav-right {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .nav-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .nav-btn.secondary {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-secondary, #8b949e);
  }

  .nav-btn.secondary:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  .nav-btn.primary {
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  .nav-btn.primary:hover:not(:disabled) {
    filter: brightness(1.1);
  }

  .nav-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
