<!--
  StatusBar.svelte - Application status bar (simplified)

  Shows:
  - Current Foreman mode (left)
  - Usage tracking with cost indicator (right)
-->
<script>
  import { foremanMode, foremanActive, foremanProjectTitle } from '$lib/stores';
  import ModeIndicator from './StatusBar/ModeIndicator.svelte';
  import UsageIndicator from './UsageIndicator.svelte';
</script>

<footer class="status-bar">
  <div class="status-left">
    <!-- Project Title -->
    <div class="status-item project-name">
      {$foremanProjectTitle || 'No Project'}
    </div>

    <!-- Foreman Mode -->
    <div class="status-item">
      <ModeIndicator />
    </div>
  </div>

  <div class="status-right">
    <!-- Usage Tracking -->
    <UsageIndicator />
  </div>
</footer>

<style>
  .status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: var(--status-bar-height, 32px);
    padding: 0 var(--space-4, 16px);
    background: var(--bg-primary, #0f1419);
    border-top: 1px solid var(--border, #2d3a47);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .status-left,
  .status-right {
    display: flex;
    align-items: center;
    gap: var(--space-4, 16px);
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .project-name {
    color: var(--text-muted, #6e7681);
    font-style: italic;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
