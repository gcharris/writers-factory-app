<!--
  AgentDropdown.svelte - Select AI agent to route message to

  Shows agents from the Agent Instruction System (agents.yaml).
  Selection persists across sessions.
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { selectedAgent as selectedAgentStore, availableAgents as availableAgentsStore } from '$lib/stores';
  import { apiClient } from '$lib/api_client';

  const dispatch = createEventDispatcher();

  // Bind to stores
  let localSelectedAgent;
  selectedAgentStore.subscribe(v => localSelectedAgent = v);

  let localAvailableAgents = [];
  availableAgentsStore.subscribe(v => localAvailableAgents = v);

  let isOpen = false;
  let isLoading = true;

  // Close on click outside
  let dropdownRef;

  onMount(async () => {
    await loadAgents();
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  });

  function handleClickOutside(e) {
    if (dropdownRef && !dropdownRef.contains(e.target)) {
      isOpen = false;
    }
  }

  async function loadAgents() {
    isLoading = true;
    try {
      // Load from Agent Instruction System API
      const agents = await apiClient.getAvailableAgents();

      // Format for dropdown display
      localAvailableAgents = agents.map(a => ({
        id: a.id,
        name: a.name,
        description: a.description,
        icon: a.icon,
        has_modes: a.has_modes,
        capabilities: a.capabilities
      }));

      // Update store
      availableAgentsStore.set(localAvailableAgents);
    } catch (e) {
      console.warn('Failed to load agents:', e);
      // Fallback to default foreman
      localAvailableAgents = [{
        id: 'foreman',
        name: 'The Foreman',
        description: 'Your structural editor and creative partner',
        icon: '🏗️',
        has_modes: true,
        capabilities: []
      }];
      availableAgentsStore.set(localAvailableAgents);
    } finally {
      isLoading = false;
    }
  }

  function selectAgent(agent) {
    selectedAgentStore.set(agent.id);
    isOpen = false;
    dispatch('change', { agent: agent.id, name: agent.name, icon: agent.icon });
  }

  function openSettings() {
    isOpen = false;
    dispatch('configure');
  }

  function toggle() {
    isOpen = !isOpen;
  }

  $: currentAgent = localAvailableAgents.find(a => a.id === localSelectedAgent) || {
    name: 'The Foreman',
    icon: '🏗️'
  };
</script>

<div class="agent-dropdown" bind:this={dropdownRef}>
  <button class="dropdown-trigger" on:click={toggle} title="Select agent">
    <span class="trigger-icon">
      {currentAgent.icon || '🤖'}
    </span>
    <span class="trigger-text">{currentAgent.name}</span>
    <span class="trigger-arrow" class:open={isOpen}>
      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </span>
  </button>

  {#if isOpen}
    <div class="dropdown-menu">
      {#if isLoading}
        <div class="dropdown-loading">Loading agents...</div>
      {:else}
        {#each localAvailableAgents as agent}
          <button
            class="dropdown-item"
            class:selected={localSelectedAgent === agent.id}
            on:click={() => selectAgent(agent)}
          >
            <span class="item-icon">{agent.icon || '🤖'}</span>
            <span class="item-content">
              <span class="item-name">{agent.name}</span>
              {#if agent.description}
                <span class="item-desc">{agent.description}</span>
              {/if}
            </span>
            {#if localSelectedAgent === agent.id}
              <span class="item-check">✓</span>
            {/if}
          </button>
        {/each}

        <div class="dropdown-divider"></div>

        <button class="dropdown-item configure" on:click={openSettings}>
          <span class="item-icon">⚙️</span>
          <span class="item-content">
            <span class="item-name configure-text">Configure agents...</span>
          </span>
        </button>
      {/if}
    </div>
  {/if}
</div>

<style>
  .agent-dropdown {
    position: relative;
  }

  .dropdown-trigger {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #c9d1d9);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .dropdown-trigger:hover {
    background: var(--bg-elevated, #2d3748);
    border-color: var(--border-strong, #444c56);
    color: var(--text-primary, #e6edf3);
  }

  .trigger-icon {
    display: flex;
    align-items: center;
    font-size: 14px;
  }

  .trigger-text {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .trigger-arrow {
    display: flex;
    align-items: center;
    transition: transform 0.15s ease;
  }

  .trigger-arrow.open {
    transform: rotate(180deg);
  }

  .dropdown-menu {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    min-width: 240px;
    max-width: 320px;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    z-index: 100;
    overflow: hidden;
  }

  .dropdown-loading {
    padding: 12px 16px;
    color: var(--text-muted, #8b949e);
    font-size: var(--text-xs, 11px);
  }

  .dropdown-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    width: 100%;
    padding: 10px 12px;
    background: transparent;
    border: none;
    color: var(--text-secondary, #c9d1d9);
    font-size: var(--text-sm, 12px);
    text-align: left;
    cursor: pointer;
    transition: background 0.1s ease;
  }

  .dropdown-item:hover {
    background: var(--bg-tertiary, #252d38);
  }

  .dropdown-item.selected {
    background: var(--bg-tertiary, #252d38);
    color: var(--accent-cyan, #58a6ff);
  }

  .item-icon {
    font-size: 16px;
    flex-shrink: 0;
    margin-top: 1px;
  }

  .item-content {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
    flex: 1;
  }

  .item-name {
    font-weight: 500;
  }

  .item-desc {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .item-check {
    color: var(--accent-cyan, #58a6ff);
    font-size: 12px;
    margin-left: auto;
  }

  .dropdown-divider {
    height: 1px;
    background: var(--border, #2d3a47);
    margin: 4px 0;
  }

  .dropdown-item.configure {
    color: var(--text-muted, #8b949e);
  }

  .dropdown-item.configure:hover {
    color: var(--text-secondary, #c9d1d9);
  }

  .configure-text {
    font-style: italic;
  }
</style>
