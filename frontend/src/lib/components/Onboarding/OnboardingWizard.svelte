<!--
  OnboardingWizard.svelte - 5-step first-time setup flow for Writers Factory

  Steps:
  1. Workspace Location - Choose where projects are stored
  2. Local AI Setup - Ensure Ollama is installed and working
  3. Cloud Models Overview - Information about available models
  4. API Keys - Optional configuration of API keys
  5. Name Your Assistant - Personalization

  Usage:
    <OnboardingWizard on:complete={handleComplete} />
-->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Step1WorkspaceLocation from './Step1WorkspaceLocation.svelte';
  import Step2LocalAI from './Step1LocalAI.svelte';
  import Step3CloudModels from './Step2CloudModels.svelte';
  import Step4ApiKeys from './Step3ApiKeys.svelte';
  import Step5NameAssistant from './Step4NameAssistant.svelte';

  const dispatch = createEventDispatcher();

  // Wizard state
  let currentStep = 1;
  const totalSteps = 5;

  // Step completion tracking
  let step1Complete = false; // Workspace location
  let step2Complete = false; // Local AI
  let step3Complete = false; // Info step - always completable
  let step4Complete = true;  // Optional - always completable
  let step5Complete = false;

  function goToStep(step: number) {
    if (step >= 1 && step <= totalSteps) {
      currentStep = step;
    }
  }

  function nextStep() {
    if (currentStep < totalSteps) {
      currentStep++;
    }
  }

  function prevStep() {
    if (currentStep > 1) {
      currentStep--;
    }
  }

  function handleStep1Complete(event: CustomEvent<{ path: string }>) {
    step1Complete = true;
  }

  function handleStep2Complete(event: CustomEvent<{ complete: boolean }>) {
    step2Complete = event.detail.complete;
  }

  function handleStep5Complete(event: CustomEvent<{ name: string }>) {
    step5Complete = true;
    // Complete the wizard
    dispatch('complete', { assistantName: event.detail.name });
  }

  function closeWizard() {
    dispatch('close');
  }

  function finishWizard() {
    dispatch('complete');
  }
</script>

<div class="onboarding-wizard">
  <!-- Header with close button -->
  <div class="wizard-header">
    <h1>Welcome to Writers Factory</h1>
    <button class="close-btn" on:click={closeWizard} title="Close">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>

  <!-- Progress Steps -->
  <div class="wizard-progress">
    <div class="progress-step {currentStep >= 1 ? 'active' : ''} {currentStep > 1 ? 'complete' : ''}">
      <div class="step-number">1</div>
      <div class="step-label">Workspace</div>
    </div>
    <div class="progress-connector {currentStep > 1 ? 'active' : ''}"></div>
    <div class="progress-step {currentStep >= 2 ? 'active' : ''} {currentStep > 2 ? 'complete' : ''}">
      <div class="step-number">2</div>
      <div class="step-label">Local AI</div>
    </div>
    <div class="progress-connector {currentStep > 2 ? 'active' : ''}"></div>
    <div class="progress-step {currentStep >= 3 ? 'active' : ''} {currentStep > 3 ? 'complete' : ''}">
      <div class="step-number">3</div>
      <div class="step-label">Cloud Models</div>
    </div>
    <div class="progress-connector {currentStep > 3 ? 'active' : ''}"></div>
    <div class="progress-step {currentStep >= 4 ? 'active' : ''} {currentStep > 4 ? 'complete' : ''}">
      <div class="step-number">4</div>
      <div class="step-label">API Keys</div>
    </div>
    <div class="progress-connector {currentStep > 4 ? 'active' : ''}"></div>
    <div class="progress-step {currentStep >= 5 ? 'active' : ''} {step5Complete ? 'complete' : ''}">
      <div class="step-number">5</div>
      <div class="step-label">Assistant</div>
    </div>
  </div>

  <!-- Step Content -->
  <div class="wizard-content">
    {#if currentStep === 1}
      <Step1WorkspaceLocation
        on:complete={handleStep1Complete}
        on:next={nextStep}
      />
    {:else if currentStep === 2}
      <Step2LocalAI
        on:complete={handleStep2Complete}
        on:next={nextStep}
      />
    {:else if currentStep === 3}
      <Step3CloudModels
        on:back={prevStep}
        on:next={nextStep}
      />
    {:else if currentStep === 4}
      <Step4ApiKeys
        on:back={prevStep}
        on:next={nextStep}
      />
    {:else if currentStep === 5}
      <Step5NameAssistant
        on:back={prevStep}
        on:complete={handleStep5Complete}
      />
    {/if}
  </div>
</div>

<style>
  .onboarding-wizard {
    display: flex;
    flex-direction: column;
    max-height: 90vh;
    color: #ffffff;
  }

  /* Header */
  .wizard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .wizard-header h1 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0;
    color: #ffffff;
  }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 4px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close-btn:hover {
    background: var(--bg-tertiary, #242d38);
    color: #ffffff;
  }

  /* Progress Steps */
  .wizard-progress {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem 2rem;
    background: var(--bg-primary, #0f1419);
    border-bottom: 1px solid var(--border, #2d3a47);
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
    background: var(--bg-secondary, #1a2027);
    border: 2px solid var(--border, #2d3a47);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1rem;
    color: var(--text-secondary, #8b949e);
    transition: all 0.3s;
  }

  .progress-step.active .step-number {
    border-color: var(--accent-cyan, #00d9ff);
    color: var(--accent-cyan, #00d9ff);
  }

  .progress-step.complete .step-number {
    background: var(--accent-cyan, #00d9ff);
    border-color: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
  }

  .step-label {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }

  .progress-step.active .step-label {
    color: var(--accent-cyan, #00d9ff);
  }

  .progress-connector {
    width: 60px;
    height: 2px;
    background: var(--border, #2d3a47);
    margin: 0 0.5rem;
    margin-bottom: 1.5rem;
    transition: background 0.3s;
  }

  .progress-connector.active {
    background: var(--accent-cyan, #00d9ff);
  }

  /* Content */
  .wizard-content {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .wizard-header {
      padding: 1rem 1.5rem;
    }

    .wizard-header h1 {
      font-size: 1.25rem;
    }

    .wizard-progress {
      padding: 1rem;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .progress-connector {
      width: 30px;
    }

    .step-label {
      font-size: 0.65rem;
    }

    .wizard-content {
      padding: 1.5rem;
    }
  }
</style>
