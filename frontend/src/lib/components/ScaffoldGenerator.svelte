<!--
  ScaffoldGenerator.svelte - 2-Stage Scaffold Generation Flow

  The entry point for Director Mode scene creation:
  - Stage 1: Draft Summary - Input scene details, get summary with enrichment suggestions
  - Stage 2: Enrichment (optional) - Query NotebookLM for additional context
  - Stage 3: Full Scaffold - Generate complete scaffold

  Uses Cyber-Noir design system with gold accents for Director Mode.
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    currentScaffold,
    scaffoldLoading,
    scaffoldStep,
    foremanProjectTitle,
    foremanProtagonist,
    registeredNotebooks,
    storyBibleStatus
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Form state
  let chapterNumber = 1;
  let sceneNumber = 1;
  let sceneTitle = '';
  let beatInfo = '';
  let characters = [];
  let characterInput = '';
  let sceneDescription = '';

  // Draft summary state
  let draftSummary = '';
  let enrichmentSuggestions = [];
  let contextUsed = null;

  // Enrichment state
  let selectedEnrichments = [];
  let enrichmentResults = [];
  let enrichmentLoading = false;

  // Final scaffold
  let generatedScaffold = '';

  // Error handling
  let error = null;

  // Get available beats from Story Bible
  $: availableBeats = $storyBibleStatus?.beat_sheet?.beats || [];

  // Get protagonist name
  $: protagonistName = $foremanProtagonist || $storyBibleStatus?.protagonist?.name || 'Protagonist';

  // Get available notebooks
  $: notebooks = $registeredNotebooks || [];

  // Handle character input
  function addCharacter() {
    if (characterInput.trim() && !characters.includes(characterInput.trim())) {
      characters = [...characters, characterInput.trim()];
      characterInput = '';
    }
  }

  function removeCharacter(char) {
    characters = characters.filter(c => c !== char);
  }

  function handleCharacterKeydown(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      addCharacter();
    }
  }

  // Stage 1: Generate Draft Summary
  async function generateDraftSummary() {
    if (!sceneDescription.trim()) {
      error = 'Please provide a scene description';
      return;
    }

    error = null;
    $scaffoldLoading = true;

    try {
      const result = await apiClient.generateDraftSummary(
        $foremanProjectTitle || 'untitled',
        chapterNumber,
        sceneNumber,
        beatInfo,
        characters.length > 0 ? characters : [protagonistName],
        sceneDescription
      );

      draftSummary = result.draft_summary;
      enrichmentSuggestions = result.enrichment_suggestions || [];
      contextUsed = result.context_used;
      $scaffoldStep = 1;
    } catch (err) {
      error = err.message || 'Failed to generate draft summary';
    } finally {
      $scaffoldLoading = false;
    }
  }

  // Stage 2: Fetch enrichment
  function toggleEnrichment(suggestion) {
    if (selectedEnrichments.includes(suggestion)) {
      selectedEnrichments = selectedEnrichments.filter(s => s !== suggestion);
    } else {
      selectedEnrichments = [...selectedEnrichments, suggestion];
    }
  }

  async function fetchEnrichments() {
    if (selectedEnrichments.length === 0) {
      // Skip to scaffold generation
      await generateFullScaffold();
      return;
    }

    enrichmentLoading = true;
    error = null;
    enrichmentResults = [];

    try {
      for (const suggestion of selectedEnrichments) {
        // Find notebook by role
        const notebook = notebooks.find(n => n.role === suggestion.notebook_role);
        if (notebook) {
          const result = await apiClient.enrichScaffold(notebook.id, suggestion.query);
          enrichmentResults = [...enrichmentResults, {
            query: suggestion.query,
            answer: result.answer,
            sources: result.sources
          }];
        }
      }
      $scaffoldStep = 2;
    } catch (err) {
      error = err.message || 'Failed to fetch enrichments';
    } finally {
      enrichmentLoading = false;
    }
  }

  // Stage 3: Generate Full Scaffold
  async function generateFullScaffold() {
    $scaffoldLoading = true;
    error = null;

    try {
      const result = await apiClient.generateScaffold(
        $foremanProjectTitle || 'untitled',
        chapterNumber,
        sceneNumber,
        sceneTitle || `Scene ${chapterNumber}.${sceneNumber}`,
        beatInfo,
        characters.length > 0 ? characters : [protagonistName],
        sceneDescription,
        enrichmentResults.length > 0 ? enrichmentResults : undefined
      );

      generatedScaffold = result.scaffold;
      $currentScaffold = {
        scene_id: result.scene_id,
        scaffold: result.scaffold,
        draft_summary: draftSummary,
        enrichment_used: result.enrichment_used,
        enrichment_data: enrichmentResults
      };
      $scaffoldStep = 3;

      dispatch('scaffoldGenerated', { scaffold: result.scaffold, sceneId: result.scene_id });
    } catch (err) {
      error = err.message || 'Failed to generate scaffold';
    } finally {
      $scaffoldLoading = false;
    }
  }

  // Navigation
  function goBack() {
    if ($scaffoldStep > 0) {
      $scaffoldStep = $scaffoldStep - 1;
    }
  }

  function proceedToStructure() {
    dispatch('proceed', { stage: 'structure', scaffold: generatedScaffold });
  }

  function reset() {
    $scaffoldStep = 0;
    draftSummary = '';
    enrichmentSuggestions = [];
    selectedEnrichments = [];
    enrichmentResults = [];
    generatedScaffold = '';
    error = null;
  }

  // Close handler
  function close() {
    dispatch('close');
  }
</script>

<div class="scaffold-generator">
  <!-- Header -->
  <div class="header">
    <div class="header-content">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="3" y1="9" x2="21" y2="9"></line>
          <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>
      </div>
      <div>
        <h2>Create Scene Scaffold</h2>
        <p class="subtitle">Strategic context for your scene</p>
      </div>
    </div>
    <button class="close-btn" on:click={close}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>

  <!-- Progress Steps -->
  <div class="progress-steps">
    <div class="step" class:active={$scaffoldStep >= 0} class:complete={$scaffoldStep > 0}>
      <span class="step-number">1</span>
      <span class="step-label">Scene Details</span>
    </div>
    <div class="step-connector" class:active={$scaffoldStep >= 1}></div>
    <div class="step" class:active={$scaffoldStep >= 1} class:complete={$scaffoldStep > 1}>
      <span class="step-number">2</span>
      <span class="step-label">Draft Summary</span>
    </div>
    <div class="step-connector" class:active={$scaffoldStep >= 2}></div>
    <div class="step" class:active={$scaffoldStep >= 2} class:complete={$scaffoldStep > 2}>
      <span class="step-number">3</span>
      <span class="step-label">Enrichment</span>
    </div>
    <div class="step-connector" class:active={$scaffoldStep >= 3}></div>
    <div class="step" class:active={$scaffoldStep >= 3}>
      <span class="step-number">4</span>
      <span class="step-label">Scaffold</span>
    </div>
  </div>

  <!-- Error display -->
  {#if error}
    <div class="error-banner">
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
      <span>{error}</span>
      <button on:click={() => error = null}>Dismiss</button>
    </div>
  {/if}

  <!-- Content -->
  <div class="content">
    <!-- Step 0: Scene Details Input -->
    {#if $scaffoldStep === 0}
      <div class="step-content">
        <div class="form-grid">
          <div class="form-row two-col">
            <div class="form-group">
              <label for="chapter">Chapter</label>
              <input
                type="number"
                id="chapter"
                bind:value={chapterNumber}
                min="1"
                placeholder="1"
              />
            </div>
            <div class="form-group">
              <label for="scene">Scene</label>
              <input
                type="number"
                id="scene"
                bind:value={sceneNumber}
                min="1"
                placeholder="1"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="title">Scene Title <span class="optional">(optional)</span></label>
            <input
              type="text"
              id="title"
              bind:value={sceneTitle}
              placeholder="e.g., The First Meeting"
            />
          </div>

          <div class="form-group">
            <label for="beat">Beat</label>
            {#if availableBeats.length > 0}
              <select id="beat" bind:value={beatInfo}>
                <option value="">Select a beat...</option>
                {#each availableBeats as beat}
                  <option value="{beat.name}: {beat.description}">
                    {beat.number}. {beat.name} ({beat.percentage}%)
                  </option>
                {/each}
              </select>
            {:else}
              <input
                type="text"
                id="beat"
                bind:value={beatInfo}
                placeholder="e.g., Setup - Establish the world"
              />
            {/if}
          </div>

          <div class="form-group">
            <label>Characters</label>
            <div class="character-input">
              <input
                type="text"
                bind:value={characterInput}
                on:keydown={handleCharacterKeydown}
                placeholder="Add character..."
              />
              <button class="add-btn" on:click={addCharacter} disabled={!characterInput.trim()}>
                Add
              </button>
            </div>
            {#if characters.length > 0}
              <div class="character-tags">
                {#each characters as char}
                  <span class="tag">
                    {char}
                    <button on:click={() => removeCharacter(char)}>×</button>
                  </span>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-group full-width">
            <label for="description">Scene Description <span class="required">*</span></label>
            <textarea
              id="description"
              bind:value={sceneDescription}
              rows="5"
              placeholder="Describe what happens in this scene. What's the goal? What conflict occurs? What changes by the end?"
            ></textarea>
          </div>
        </div>

        <div class="actions">
          <button class="secondary-btn" on:click={close}>Cancel</button>
          <button
            class="primary-btn"
            on:click={generateDraftSummary}
            disabled={$scaffoldLoading || !sceneDescription.trim()}
          >
            {#if $scaffoldLoading}
              <span class="spinner"></span>
              Generating...
            {:else}
              Generate Draft Summary
            {/if}
          </button>
        </div>
      </div>

    <!-- Step 1: Draft Summary Review -->
    {:else if $scaffoldStep === 1}
      <div class="step-content">
        <div class="draft-summary-section">
          <h3>Draft Summary</h3>
          <div class="summary-preview">
            <pre>{draftSummary}</pre>
          </div>

          {#if contextUsed}
            <div class="context-used">
              <h4>Context Applied</h4>
              <div class="context-tags">
                {#if contextUsed.protagonist}
                  <span class="context-tag">Protagonist</span>
                {/if}
                {#if contextUsed.theme}
                  <span class="context-tag">Theme</span>
                {/if}
                {#if contextUsed.voice_bundle}
                  <span class="context-tag">Voice Bundle</span>
                {/if}
              </div>
            </div>
          {/if}
        </div>

        {#if enrichmentSuggestions.length > 0 && notebooks.length > 0}
          <div class="enrichment-section">
            <h3>Enrichment Suggestions</h3>
            <p class="hint">Select queries to fetch additional context from NotebookLM</p>
            <div class="enrichment-list">
              {#each enrichmentSuggestions as suggestion}
                <button
                  class="enrichment-item"
                  class:selected={selectedEnrichments.includes(suggestion)}
                  on:click={() => toggleEnrichment(suggestion)}
                >
                  <div class="enrichment-check">
                    {#if selectedEnrichments.includes(suggestion)}
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                      </svg>
                    {/if}
                  </div>
                  <div class="enrichment-content">
                    <span class="enrichment-query">{suggestion.query}</span>
                    <span class="enrichment-role">{suggestion.notebook_role} notebook</span>
                  </div>
                </button>
              {/each}
            </div>
          </div>
        {:else if notebooks.length === 0}
          <div class="no-notebooks-hint">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p>No NotebookLM notebooks registered. Enrichment suggestions are available but cannot be fetched.</p>
          </div>
        {/if}

        <div class="actions">
          <button class="secondary-btn" on:click={goBack}>Back</button>
          <button
            class="primary-btn"
            on:click={fetchEnrichments}
            disabled={enrichmentLoading}
          >
            {#if enrichmentLoading}
              <span class="spinner"></span>
              Fetching...
            {:else if selectedEnrichments.length > 0}
              Fetch Enrichments ({selectedEnrichments.length})
            {:else}
              Skip to Scaffold
            {/if}
          </button>
        </div>
      </div>

    <!-- Step 2: Enrichment Results -->
    {:else if $scaffoldStep === 2}
      <div class="step-content">
        <div class="enrichment-results-section">
          <h3>Enrichment Results</h3>
          {#each enrichmentResults as result}
            <div class="enrichment-result">
              <h4>{result.query}</h4>
              <div class="result-answer">
                <p>{result.answer}</p>
              </div>
              {#if result.sources && result.sources.length > 0}
                <div class="result-sources">
                  <span class="sources-label">Sources:</span>
                  {#each result.sources as source}
                    <span class="source-tag">{source}</span>
                  {/each}
                </div>
              {/if}
            </div>
          {/each}
        </div>

        <div class="actions">
          <button class="secondary-btn" on:click={goBack}>Back</button>
          <button
            class="primary-btn"
            on:click={generateFullScaffold}
            disabled={$scaffoldLoading}
          >
            {#if $scaffoldLoading}
              <span class="spinner"></span>
              Generating Scaffold...
            {:else}
              Generate Full Scaffold
            {/if}
          </button>
        </div>
      </div>

    <!-- Step 3: Final Scaffold -->
    {:else if $scaffoldStep === 3}
      <div class="step-content">
        <div class="scaffold-section">
          <div class="scaffold-header">
            <h3>Scene Scaffold</h3>
            <div class="scaffold-actions">
              <button class="icon-btn" title="Copy to clipboard" on:click={() => navigator.clipboard.writeText(generatedScaffold)}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              </button>
            </div>
          </div>
          <div class="scaffold-preview">
            <pre>{generatedScaffold}</pre>
          </div>

          {#if $currentScaffold?.enrichment_used}
            <div class="enrichment-badge">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              <span>Enhanced with NotebookLM context</span>
            </div>
          {/if}
        </div>

        <div class="actions">
          <button class="secondary-btn" on:click={reset}>Start Over</button>
          <button class="primary-btn" on:click={proceedToStructure}>
            Proceed to Structure Selection
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .scaffold-generator {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 85vh;
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-lg, 8px);
    overflow: hidden;
  }

  /* Header */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .header-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.2));
    border-radius: var(--radius-md, 6px);
    color: var(--accent-gold, #d4a574);
  }

  .header-icon svg {
    width: 24px;
    height: 24px;
  }

  .header h2 {
    margin: 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .subtitle {
    margin: 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .close-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .close-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .close-btn svg {
    width: 18px;
    height: 18px;
  }

  /* Progress Steps */
  .progress-steps {
    display: flex;
    align-items: center;
    padding: var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .step {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    opacity: 0.5;
    transition: opacity var(--transition-fast, 100ms ease);
  }

  .step.active {
    opacity: 1;
  }

  .step-number {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 50%;
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-secondary, #8b949e);
    transition: all var(--transition-fast, 100ms ease);
  }

  .step.active .step-number {
    background: var(--accent-gold, #d4a574);
    border-color: var(--accent-gold, #d4a574);
    color: var(--bg-primary, #0f1419);
  }

  .step.complete .step-number {
    background: var(--success, #3fb950);
    border-color: var(--success, #3fb950);
    color: var(--bg-primary, #0f1419);
  }

  .step-label {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    white-space: nowrap;
  }

  .step.active .step-label {
    color: var(--text-primary, #e6edf3);
  }

  .step-connector {
    flex: 1;
    height: 1px;
    background: var(--border, #2d3a47);
    margin: 0 var(--space-2, 8px);
    transition: background var(--transition-fast, 100ms ease);
  }

  .step-connector.active {
    background: var(--accent-gold, #d4a574);
  }

  /* Error Banner */
  .error-banner {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--error-muted, rgba(248, 81, 73, 0.2));
    border-bottom: 1px solid var(--error, #f85149);
    color: var(--error, #f85149);
    font-size: var(--text-sm, 12px);
  }

  .error-banner svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .error-banner span {
    flex: 1;
  }

  .error-banner button {
    padding: 4px 8px;
    background: transparent;
    border: 1px solid var(--error, #f85149);
    border-radius: var(--radius-sm, 4px);
    color: var(--error, #f85149);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
  }

  /* Content */
  .content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  .step-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-4, 16px);
  }

  /* Form Styles */
  .form-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-4, 16px);
  }

  .form-row {
    display: grid;
    gap: var(--space-4, 16px);
  }

  .form-row.two-col {
    grid-template-columns: repeat(2, 1fr);
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .form-group.full-width {
    grid-column: 1 / -1;
  }

  .form-group label {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
  }

  .form-group label .required {
    color: var(--error, #f85149);
  }

  .form-group label .optional {
    color: var(--text-muted, #6e7681);
    font-weight: var(--font-normal, 400);
  }

  .form-group input,
  .form-group select,
  .form-group textarea {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-input, #161b22);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    transition: border-color var(--transition-fast, 100ms ease);
  }

  .form-group input:focus,
  .form-group select:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--accent-gold, #d4a574);
  }

  .form-group textarea {
    resize: vertical;
    min-height: 100px;
    font-family: var(--font-ui);
  }

  .form-group select {
    cursor: pointer;
  }

  /* Character Input */
  .character-input {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .character-input input {
    flex: 1;
  }

  .add-btn {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .add-btn:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .add-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .character-tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1, 4px);
    margin-top: var(--space-2, 8px);
  }

  .tag {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: 2px 8px;
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.2));
    border-radius: var(--radius-full, 9999px);
    font-size: var(--text-xs, 11px);
    color: var(--accent-gold, #d4a574);
  }

  .tag button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 14px;
    height: 14px;
    background: transparent;
    border: none;
    color: var(--accent-gold, #d4a574);
    cursor: pointer;
    font-size: 12px;
  }

  .tag button:hover {
    color: var(--error, #f85149);
  }

  /* Actions */
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3, 12px);
    padding-top: var(--space-4, 16px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .secondary-btn,
  .primary-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .secondary-btn {
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    color: var(--text-secondary, #8b949e);
  }

  .secondary-btn:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  .primary-btn {
    background: var(--accent-gold, #d4a574);
    border: none;
    color: var(--bg-primary, #0f1419);
  }

  .primary-btn:hover:not(:disabled) {
    background: var(--accent-gold-hover, #e0b585);
  }

  .primary-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .primary-btn svg {
    width: 16px;
    height: 16px;
  }

  /* Spinner */
  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Draft Summary Section */
  .draft-summary-section,
  .enrichment-section,
  .enrichment-results-section,
  .scaffold-section {
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
    padding: var(--space-4, 16px);
  }

  .draft-summary-section h3,
  .enrichment-section h3,
  .enrichment-results-section h3,
  .scaffold-section h3 {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .summary-preview,
  .scaffold-preview {
    background: var(--bg-input, #161b22);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    padding: var(--space-3, 12px);
    max-height: 200px;
    overflow-y: auto;
  }

  .summary-preview pre,
  .scaffold-preview pre {
    margin: 0;
    font-family: var(--font-mono);
    font-size: var(--text-xs, 11px);
    line-height: 1.5;
    color: var(--text-secondary, #8b949e);
    white-space: pre-wrap;
  }

  /* Context Used */
  .context-used {
    margin-top: var(--space-3, 12px);
    padding-top: var(--space-3, 12px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .context-used h4 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-muted, #6e7681);
  }

  .context-tags {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .context-tag {
    padding: 2px 8px;
    background: var(--success-muted, rgba(63, 185, 80, 0.2));
    border-radius: var(--radius-full, 9999px);
    font-size: 10px;
    color: var(--success, #3fb950);
  }

  /* Enrichment Section */
  .enrichment-section .hint {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .enrichment-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .enrichment-item {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: var(--bg-input, #161b22);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    text-align: left;
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .enrichment-item:hover {
    border-color: var(--accent-cyan, #58a6ff);
  }

  .enrichment-item.selected {
    border-color: var(--accent-gold, #d4a574);
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.1));
  }

  .enrichment-check {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    flex-shrink: 0;
  }

  .enrichment-item.selected .enrichment-check {
    background: var(--accent-gold, #d4a574);
    border-color: var(--accent-gold, #d4a574);
  }

  .enrichment-check svg {
    width: 12px;
    height: 12px;
    color: var(--bg-primary, #0f1419);
  }

  .enrichment-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .enrichment-query {
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
  }

  .enrichment-role {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    text-transform: capitalize;
  }

  /* No Notebooks Hint */
  .no-notebooks-hint {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: var(--warning-muted, rgba(210, 153, 34, 0.2));
    border: 1px solid var(--warning, #d29922);
    border-radius: var(--radius-md, 6px);
    margin-top: var(--space-4, 16px);
  }

  .no-notebooks-hint svg {
    width: 20px;
    height: 20px;
    color: var(--warning, #d29922);
    flex-shrink: 0;
  }

  .no-notebooks-hint p {
    margin: 0;
    font-size: var(--text-xs, 11px);
    color: var(--warning, #d29922);
  }

  /* Enrichment Results */
  .enrichment-result {
    background: var(--bg-input, #161b22);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    padding: var(--space-3, 12px);
    margin-bottom: var(--space-3, 12px);
  }

  .enrichment-result:last-child {
    margin-bottom: 0;
  }

  .enrichment-result h4 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--accent-cyan, #58a6ff);
  }

  .result-answer {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-relaxed, 1.7);
  }

  .result-answer p {
    margin: 0;
  }

  .result-sources {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-1, 4px);
    margin-top: var(--space-2, 8px);
    padding-top: var(--space-2, 8px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .sources-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .source-tag {
    padding: 2px 6px;
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-full, 9999px);
    font-size: 9px;
    color: var(--text-secondary, #8b949e);
  }

  /* Scaffold Section */
  .scaffold-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-3, 12px);
  }

  .scaffold-header h3 {
    margin: 0;
  }

  .scaffold-actions {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .icon-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-input, #161b22);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .icon-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .icon-btn svg {
    width: 14px;
    height: 14px;
  }

  .scaffold-preview {
    max-height: 300px;
  }

  .enrichment-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1, 4px);
    margin-top: var(--space-3, 12px);
    padding: 4px 10px;
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.2));
    border-radius: var(--radius-full, 9999px);
    font-size: var(--text-xs, 11px);
    color: var(--accent-gold, #d4a574);
  }

  .enrichment-badge svg {
    width: 12px;
    height: 12px;
  }
</style>
