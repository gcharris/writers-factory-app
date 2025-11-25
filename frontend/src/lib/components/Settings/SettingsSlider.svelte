<!--
  SettingsSlider.svelte - Reusable slider component for settings

  Features:
  - Label with current value display
  - Min/max range indicators
  - Optional tooltip on hover
  - Optional unit suffix
  - Keyboard accessible
-->
<script>
  export let label = '';
  export let value = 0;
  export let min = 0;
  export let max = 100;
  export let step = 1;
  export let tooltip = '';
  export let unit = '';
  export let disabled = false;

  // Calculate percentage for visual fill
  $: percentage = ((value - min) / (max - min)) * 100;
</script>

<div class="settings-slider" class:disabled>
  <div class="slider-header">
    <label title={tooltip}>{label}</label>
    <span class="value">{value}{unit}</span>
  </div>

  <div class="slider-container">
    <input
      type="range"
      bind:value
      {min}
      {max}
      {step}
      {disabled}
      title={tooltip}
      style="--percentage: {percentage}%"
    />
  </div>

  <div class="slider-labels">
    <span class="min-label">{min}{unit}</span>
    <span class="max-label">{max}{unit}</span>
  </div>
</div>

<style>
  .settings-slider {
    margin-bottom: 1.5rem;
  }

  .settings-slider.disabled {
    opacity: 0.5;
    pointer-events: none;
  }

  .slider-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  label {
    font-size: 0.875rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 500;
    cursor: help;
  }

  .value {
    font-size: 0.875rem;
    color: var(--accent-gold, #d4a574);
    font-weight: 600;
    font-family: 'Courier New', monospace;
  }

  .slider-container {
    position: relative;
    width: 100%;
    height: 24px;
    display: flex;
    align-items: center;
  }

  input[type="range"] {
    width: 100%;
    height: 4px;
    -webkit-appearance: none;
    appearance: none;
    background: linear-gradient(
      to right,
      var(--accent-gold, #d4a574) 0%,
      var(--accent-gold, #d4a574) var(--percentage),
      var(--bg-tertiary, #242d38) var(--percentage),
      var(--bg-tertiary, #242d38) 100%
    );
    border-radius: 2px;
    outline: none;
    cursor: pointer;
  }

  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    background: var(--accent-gold, #d4a574);
    border: 2px solid var(--bg-primary, #0f1419);
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  input[type="range"]::-moz-range-thumb {
    width: 16px;
    height: 16px;
    background: var(--accent-gold, #d4a574);
    border: 2px solid var(--bg-primary, #0f1419);
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  input[type="range"]:hover::-webkit-slider-thumb {
    transform: scale(1.2);
    box-shadow: 0 0 0 4px rgba(212, 165, 116, 0.2);
  }

  input[type="range"]:hover::-moz-range-thumb {
    transform: scale(1.2);
    box-shadow: 0 0 0 4px rgba(212, 165, 116, 0.2);
  }

  input[type="range"]:focus::-webkit-slider-thumb {
    box-shadow: 0 0 0 4px rgba(212, 165, 116, 0.3);
  }

  input[type="range"]:focus::-moz-range-thumb {
    box-shadow: 0 0 0 4px rgba(212, 165, 116, 0.3);
  }

  .slider-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 0.25rem;
    font-size: 0.75rem;
    color: var(--text-muted, #6e7681);
  }
</style>
