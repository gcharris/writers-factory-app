<script lang="ts">
  import { onMount } from 'svelte';
  import { foremanActive, foremanMode, foremanWorkOrder } from '$lib/stores';

  const BASE_URL = 'http://localhost:8000';

  let currentMode: 'ARCHITECT' | 'VOICE' | 'DIRECTOR' | 'IDLE' = 'IDLE';

  // Sync with store
  $: currentMode = $foremanMode || 'IDLE';

  function getModeColor(mode: string): string {
    switch (mode) {
      case 'ARCHITECT': return '#ffb000';
      case 'VOICE': return '#00ff88';
      case 'DIRECTOR': return '#00d9ff';
      default: return '#888888';
    }
  }

  function getModeIcon(mode: string): string {
    switch (mode) {
      case 'ARCHITECT': return '📐';
      case 'VOICE': return '🎤';
      case 'DIRECTOR': return '🎬';
      default: return '💤';
    }
  }

  // Quick action handlers
  function handleQuickAction(action: string) {
    console.log(`Quick action: ${action}`);
    // These will integrate with actual components in future weeks
    alert(`Quick action: ${action}\n\nThis will open the corresponding panel/modal in future weeks.`);
  }

  // Check if work order template is complete
  function isTemplateComplete(templateName: string): boolean {
    if (!$foremanWorkOrder || !$foremanWorkOrder.templates) return false;
    const template = $foremanWorkOrder.templates.find(t => t.name === templateName);
    return template?.status === 'complete';
  }

  // Get template progress
  function getTemplateProgress(templateName: string): string {
    if (!$foremanWorkOrder || !$foremanWorkOrder.templates) return '0/0';
    const template = $foremanWorkOrder.templates.find(t => t.name === templateName);
    if (!template) return '0/0';
    return `${template.completed_fields?.length || 0}/${template.required_fields?.length || 0}`;
  }
</script>

<div class="studio-panel">
  {#if currentMode === 'IDLE'}
    <!-- Idle State: No active project -->
    <div class="idle-state">
      <div class="idle-icon">💤</div>
      <h3>Studio Idle</h3>
      <p>Start a new project with Foreman to begin your writing journey.</p>
      <div class="mode-previews">
        <div class="mode-preview-card" style="border-color: {getModeColor('ARCHITECT')};">
          <span class="preview-icon">{getModeIcon('ARCHITECT')}</span>
          <span class="preview-name">ARCHITECT</span>
          <p class="preview-description">Build Story Bible foundations</p>
        </div>
        <div class="mode-preview-card" style="border-color: {getModeColor('VOICE')};">
          <span class="preview-icon">{getModeIcon('VOICE')}</span>
          <span class="preview-name">VOICE</span>
          <p class="preview-description">Discover authentic character voice</p>
        </div>
        <div class="mode-preview-card" style="border-color: {getModeColor('DIRECTOR')};">
          <span class="preview-icon">{getModeIcon('DIRECTOR')}</span>
          <span class="preview-name">DIRECTOR</span>
          <p class="preview-description">Draft scenes with precision</p>
        </div>
      </div>
    </div>
  {:else if currentMode === 'ARCHITECT'}
    <!-- ARCHITECT Mode: Story Bible Building -->
    <div class="mode-section">
      <div class="mode-header" style="border-color: {getModeColor('ARCHITECT')};">
        <span class="mode-icon">{getModeIcon('ARCHITECT')}</span>
        <h3>ARCHITECT Mode</h3>
      </div>

      <p class="mode-description">
        Build your Story Bible foundations. Complete templates to establish world rules, character arcs, and narrative structure.
      </p>

      <div class="quick-actions">
        <button
          class="action-card"
          on:click={() => handleQuickAction('View Story Bible')}
        >
          <div class="action-icon">📖</div>
          <div class="action-content">
            <div class="action-title">View Story Bible</div>
            <div class="action-subtitle">Browse completed templates</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Edit Character Fatal Flaw')}
          class:completed={isTemplateComplete('character_fatal_flaw')}
        >
          <div class="action-icon">⚠️</div>
          <div class="action-content">
            <div class="action-title">Character Fatal Flaw</div>
            <div class="action-subtitle">
              {isTemplateComplete('character_fatal_flaw') ? 'Complete ✓' : `Progress: ${getTemplateProgress('character_fatal_flaw')}`}
            </div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Edit The Lie')}
          class:completed={isTemplateComplete('the_lie')}
        >
          <div class="action-icon">🎭</div>
          <div class="action-content">
            <div class="action-title">The Lie</div>
            <div class="action-subtitle">
              {isTemplateComplete('the_lie') ? 'Complete ✓' : `Progress: ${getTemplateProgress('the_lie')}`}
            </div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Edit 15-Beat Structure')}
          class:completed={isTemplateComplete('15_beat_structure')}
        >
          <div class="action-icon">📊</div>
          <div class="action-content">
            <div class="action-title">15-Beat Structure</div>
            <div class="action-subtitle">
              {isTemplateComplete('15_beat_structure') ? 'Complete ✓' : `Progress: ${getTemplateProgress('15_beat_structure')}`}
            </div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Edit World Rules')}
          class:completed={isTemplateComplete('world_rules')}
        >
          <div class="action-icon">🌍</div>
          <div class="action-content">
            <div class="action-title">World Rules</div>
            <div class="action-subtitle">
              {isTemplateComplete('world_rules') ? 'Complete ✓' : `Progress: ${getTemplateProgress('world_rules')}`}
            </div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('View Knowledge Base')}
        >
          <div class="action-icon">🧠</div>
          <div class="action-content">
            <div class="action-title">Knowledge Base</div>
            <div class="action-subtitle">Browse saved decisions</div>
          </div>
          <div class="action-arrow">→</div>
        </button>
      </div>
    </div>
  {:else if currentMode === 'VOICE'}
    <!-- VOICE Mode: Voice Calibration -->
    <div class="mode-section">
      <div class="mode-header" style="border-color: {getModeColor('VOICE')};">
        <span class="mode-icon">{getModeIcon('VOICE')}</span>
        <h3>VOICE Mode</h3>
      </div>

      <p class="mode-description">
        Discover your character's authentic voice through multi-agent tournaments. Generate variants, compare results, and create your Voice Bundle.
      </p>

      <div class="quick-actions">
        <button
          class="action-card primary"
          on:click={() => handleQuickAction('Launch Voice Tournament')}
        >
          <div class="action-icon">🏆</div>
          <div class="action-content">
            <div class="action-title">Launch Tournament</div>
            <div class="action-subtitle">Generate 15-25 voice variants</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('View Voice Variants')}
        >
          <div class="action-icon">📊</div>
          <div class="action-content">
            <div class="action-title">View Variants</div>
            <div class="action-subtitle">Compare generated samples</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Create Gold Standard')}
        >
          <div class="action-icon">⭐</div>
          <div class="action-content">
            <div class="action-title">Gold Standard</div>
            <div class="action-subtitle">Define perfect voice example</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Define Anti-Patterns')}
        >
          <div class="action-icon">🚫</div>
          <div class="action-content">
            <div class="action-title">Anti-Patterns</div>
            <div class="action-subtitle">What NOT to write</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('View Phase Evolution')}
        >
          <div class="action-icon">📈</div>
          <div class="action-content">
            <div class="action-title">Phase Evolution</div>
            <div class="action-subtitle">Voice changes over story</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card success"
          on:click={() => handleQuickAction('Generate Voice Bundle')}
        >
          <div class="action-icon">📦</div>
          <div class="action-content">
            <div class="action-title">Generate Voice Bundle</div>
            <div class="action-subtitle">Finalize and transition to DIRECTOR</div>
          </div>
          <div class="action-arrow">→</div>
        </button>
      </div>
    </div>
  {:else if currentMode === 'DIRECTOR'}
    <!-- DIRECTOR Mode: Scene Drafting -->
    <div class="mode-section">
      <div class="mode-header" style="border-color: {getModeColor('DIRECTOR')};">
        <span class="mode-icon">{getModeIcon('DIRECTOR')}</span>
        <h3>DIRECTOR Mode</h3>
      </div>

      <p class="mode-description">
        Draft scenes with precision. Use the full pipeline: Scaffold → Structure → Write → Enhance.
      </p>

      <div class="quick-actions">
        <button
          class="action-card primary"
          on:click={() => handleQuickAction('Create New Scene')}
        >
          <div class="action-icon">➕</div>
          <div class="action-content">
            <div class="action-title">Create New Scene</div>
            <div class="action-subtitle">Start scene drafting pipeline</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Generate Scaffold')}
        >
          <div class="action-icon">🏗️</div>
          <div class="action-content">
            <div class="action-title">Scaffold Generator</div>
            <div class="action-subtitle">Draft → Enrich → Generate</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('View Scene Variants')}
        >
          <div class="action-icon">🎬</div>
          <div class="action-content">
            <div class="action-title">Scene Variants</div>
            <div class="action-subtitle">15 variants from tournament</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Compare Scenes')}
        >
          <div class="action-icon">⚖️</div>
          <div class="action-content">
            <div class="action-title">Compare Variants</div>
            <div class="action-subtitle">Side-by-side analysis</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Create Hybrid')}
        >
          <div class="action-icon">🔀</div>
          <div class="action-content">
            <div class="action-title">Hybrid Creator</div>
            <div class="action-subtitle">Combine best parts</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Enhance Scene')}
        >
          <div class="action-icon">✨</div>
          <div class="action-content">
            <div class="action-title">Enhancement Panel</div>
            <div class="action-subtitle">Action Prompt or 6-Pass</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('View Score Breakdown')}
        >
          <div class="action-icon">📊</div>
          <div class="action-content">
            <div class="action-title">Score Breakdown</div>
            <div class="action-subtitle">Voice 30, Character 20, Metaphor 20...</div>
          </div>
          <div class="action-arrow">→</div>
        </button>

        <button
          class="action-card"
          on:click={() => handleQuickAction('Quick Scene Generate')}
        >
          <div class="action-icon">⚡</div>
          <div class="action-content">
            <div class="action-title">Quick Generate</div>
            <div class="action-subtitle">Fast single-model draft</div>
          </div>
          <div class="action-arrow">→</div>
        </button>
      </div>
    </div>
  {/if}

  <!-- Help Section -->
  <div class="help-section">
    <div class="help-icon">💡</div>
    <div class="help-content">
      <h4>Tips</h4>
      {#if currentMode === 'IDLE'}
        <p>Click "Start Project" in the Chat Panel to begin your writing journey with Foreman.</p>
      {:else if currentMode === 'ARCHITECT'}
        <p>Complete all Story Bible templates to unlock VOICE mode. Chat with Foreman to fill in template fields.</p>
      {:else if currentMode === 'VOICE'}
        <p>Launch tournaments to generate voice variants, then select the best samples to create your Voice Bundle.</p>
      {:else if currentMode === 'DIRECTOR'}
        <p>Follow the full pipeline: Scaffold → Structure → Write → Enhance. Foreman will guide you through each step.</p>
      {/if}
    </div>
  </div>
</div>

<style>
  .studio-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 1rem;
    overflow-y: auto;
    background: #1a1a1a;
    color: #ffffff;
  }

  /* Idle State */
  .idle-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
    flex: 1;
  }

  .idle-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
  }

  .idle-state h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #888888;
  }

  .idle-state p {
    margin: 0 0 2rem 0;
    color: #666666;
    max-width: 300px;
  }

  .mode-previews {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
    max-width: 400px;
  }

  .mode-preview-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #2d2d2d;
    border: 2px solid;
    border-radius: 8px;
  }

  .preview-icon {
    font-size: 2rem;
  }

  .preview-name {
    font-weight: 600;
    color: #ffffff;
    min-width: 100px;
  }

  .preview-description {
    margin: 0;
    font-size: 0.875rem;
    color: #888888;
    flex: 1;
  }

  /* Mode Section */
  .mode-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .mode-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: #2d2d2d;
    border-left: 4px solid;
    border-radius: 4px;
  }

  .mode-icon {
    font-size: 1.5rem;
  }

  .mode-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .mode-description {
    margin: 0;
    padding: 0 1rem;
    color: #b0b0b0;
    line-height: 1.6;
  }

  /* Quick Actions */
  .quick-actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .action-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
  }

  .action-card:hover {
    background: #353535;
    border-color: #00d9ff;
    transform: translateX(4px);
  }

  .action-card.primary {
    border-color: #00d9ff;
    border-width: 2px;
  }

  .action-card.primary:hover {
    background: #00d9ff10;
  }

  .action-card.success {
    border-color: #00ff88;
    border-width: 2px;
  }

  .action-card.success:hover {
    background: #00ff8810;
  }

  .action-card.completed {
    border-color: #00ff88;
    background: #00ff8810;
  }

  .action-icon {
    font-size: 1.75rem;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1a1a1a;
    border-radius: 8px;
    flex-shrink: 0;
  }

  .action-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .action-title {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
  }

  .action-subtitle {
    font-size: 0.875rem;
    color: #888888;
  }

  .action-arrow {
    font-size: 1.5rem;
    color: #404040;
    transition: color 0.2s;
  }

  .action-card:hover .action-arrow {
    color: #00d9ff;
  }

  /* Help Section */
  .help-section {
    display: flex;
    gap: 1rem;
    margin-top: auto;
    padding: 1rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
  }

  .help-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
  }

  .help-content {
    flex: 1;
  }

  .help-content h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: #00d9ff;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .help-content p {
    margin: 0;
    font-size: 0.875rem;
    color: #888888;
    line-height: 1.6;
  }

  /* Scrollbar */
  .studio-panel::-webkit-scrollbar {
    width: 8px;
  }

  .studio-panel::-webkit-scrollbar-track {
    background: #1a1a1a;
  }

  .studio-panel::-webkit-scrollbar-thumb {
    background: #404040;
    border-radius: 4px;
  }

  .studio-panel::-webkit-scrollbar-thumb:hover {
    background: #505050;
  }
</style>
