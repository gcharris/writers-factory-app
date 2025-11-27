<!--
  AgentDropdown.svelte - Select AI agent to route message to

  Shows Squad-configured agents with a link to configure more.
  Selection persists for session only.
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { assistantName } from '$lib/stores';

  const dispatch = createEventDispatcher();

  export let selectedAgent = 'default';

  let isOpen = false;
  let availableAgents = [];
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
      // Load from Squad configuration
      const response = await fetch('http://localhost:8000/settings/category/squad');
      if (response.ok) {
        const data = await response.json();
        // Extract agents from squad config
        const agentIds = [
          data.architect_agent,
          data.voice_agent,
          data.scene_writer_agent,
          data.enhancement_agent,
          data.analysis_agent
        ].filter(Boolean);

        // Get unique agents and fetch their details
        const uniqueIds = [...new Set(agentIds)];

        // Also get all available agents for names
        const agentsResponse = await fetch('http://localhost:8000/agents');
        if (agentsResponse.ok) {
          const allAgents = await agentsResponse.json();
          availableAgents = uniqueIds.map(id => {
            const agent = allAgents.find(a => a.id === id);
            return {
              id,
              name: agent?.name || id,
              description: agent?.description || ''
            };
          });
        }
      }
    } catch (e) {
      console.warn('Failed to load agents:', e);
    } finally {
      isLoading = false;
    }

    // Always include default as first option
    if (!availableAgents.find(a => a.id === 'default')) {
      availableAgents = [
        { id: 'default', name: $assistantName, description: 'Your writing assistant' },
        ...availableAgents
      ];
    }
  }

  function selectAgent(agent) {
    selectedAgent = agent.id;
    isOpen = false;
    dispatch('change', { agent: agent.id, name: agent.name });
  }

  function openSettings() {
    isOpen = false;
    dispatch('configure');
  }

  function toggle() {
    isOpen = !isOpen;
  }

  $: currentAgent = availableAgents.find(a => a.id === selectedAgent) || { name: $assistantName };
</script>

<div class="agent-dropdown" bind:this={dropdownRef}>
  <button class="dropdown-trigger" on:click={toggle} title="Select agent">
    <span class="trigger-icon">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="3"></circle>
        <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"></path>
      </svg>
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
        {#each availableAgents as agent}
          <button
            class="dropdown-item"
            class:selected={selectedAgent === agent.id}
            on:click={() => selectAgent(agent)}
          >
            <span class="item-indicator">
              {#if selectedAgent === agent.id}
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <circle cx="12" cy="12" r="6"></circle>
                </svg>
              {:else}
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="6"></circle>
                </svg>
              {/if}
            </span>
            <span class="item-content">
              <span class="item-name">{agent.name}</span>
              {#if agent.description}
                <span class="item-desc">{agent.description}</span>
              {/if}
            </span>
          </button>
        {/each}

        <div class="dropdown-divider"></div>

        <button class="dropdown-item configure" on:click={openSettings}>
          <span class="item-indicator">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </span>
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
    color: var(--accent-cyan, #58a6ff);
  }

  .trigger-text {
    max-width: 100px;
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
    min-width: 200px;
    max-width: 280px;
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
    color: var(--accent-cyan, #58a6ff);
  }

  .item-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    margin-top: 1px;
  }

  .dropdown-item.selected .item-indicator {
    color: var(--accent-cyan, #58a6ff);
  }

  .item-content {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
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
