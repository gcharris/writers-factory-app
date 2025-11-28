<!--
  MentionPicker.svelte - @mention picker for project files and entities

  Data sources:
  - Characters from Knowledge Graph
  - Files from content directory
  - Locations from Knowledge Graph
  - Themes from Knowledge Graph

  Triggered by @ button or typing @ in input.
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';

  const dispatch = createEventDispatcher();

  export let open = false;
  export let searchQuery = '';

  let pickerRef;
  let searchInput;
  let results = {
    characters: [],
    files: [],
    locations: [],
    themes: []
  };
  let isLoading = false;
  let expandedCategories = ['characters', 'files'];

  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    document.addEventListener('keydown', handleKeydown);
    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('keydown', handleKeydown);
    };
  });

  $: if (open && searchInput) {
    setTimeout(() => searchInput?.focus(), 10);
  }

  $: if (open) {
    searchMentions(searchQuery);
  }

  function handleClickOutside(e) {
    if (pickerRef && !pickerRef.contains(e.target)) {
      close();
    }
  }

  function handleKeydown(e) {
    if (!open) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      close();
    }
  }

  async function searchMentions(query) {
    isLoading = true;
    try {
      // Use the new unified mentions search endpoint
      const response = await apiClient.searchMentions(query || '', 20);

      // Group results by type
      results.characters = response.results
        .filter(r => r.type === 'character')
        .map(r => ({ id: r.id, label: r.name, name: r.name, path: r.file || r.path }));
      results.locations = response.results
        .filter(r => r.type === 'location')
        .map(r => ({ id: r.id, label: r.name, name: r.name, path: r.file || r.path }));
      results.themes = response.results
        .filter(r => r.type === 'theme')
        .map(r => ({ id: r.id, label: r.name, name: r.name, path: r.file || r.path }));
      results.files = response.results
        .filter(r => r.type === 'file')
        .map(r => ({ id: r.id, name: r.name, path: r.path || r.file }));

    } catch (e) {
      console.warn('Failed to search mentions:', e);
      // Reset results on error
      results = { characters: [], files: [], locations: [], themes: [] };
    } finally {
      isLoading = false;
    }
  }

  function selectMention(type, item) {
    dispatch('select', {
      type,
      id: item.id || item.path,
      name: item.name || item.label || item.path?.split('/').pop(),
      path: item.path
    });
    close();
  }

  function toggleCategory(category) {
    if (expandedCategories.includes(category)) {
      expandedCategories = expandedCategories.filter(c => c !== category);
    } else {
      expandedCategories = [...expandedCategories, category];
    }
  }

  function close() {
    open = false;
    searchQuery = '';
    dispatch('close');
  }

  function getCategoryIcon(category) {
    switch (category) {
      case 'characters': return 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2';
      case 'files': return 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z';
      case 'locations': return 'M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z';
      case 'themes': return 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5';
      default: return '';
    }
  }

  $: hasResults = results.characters.length > 0 ||
                  results.files.length > 0 ||
                  results.locations.length > 0 ||
                  results.themes.length > 0;
</script>

{#if open}
  <div class="mention-picker" bind:this={pickerRef}>
    <div class="picker-header">
      <div class="search-box">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input
          bind:this={searchInput}
          bind:value={searchQuery}
          type="text"
          placeholder="Search files, characters..."
          on:input={() => searchMentions(searchQuery)}
        />
      </div>
    </div>

    <div class="picker-content">
      {#if isLoading}
        <div class="loading">Searching...</div>
      {:else if !hasResults}
        <div class="empty">
          <span>No results found</span>
          <span class="empty-hint">Try a different search term</span>
        </div>
      {:else}
        <!-- Characters -->
        {#if results.characters.length > 0}
          <div class="category">
            <button class="category-header" on:click={() => toggleCategory('characters')}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span>Characters</span>
              <span class="category-count">{results.characters.length}</span>
              <span class="category-arrow" class:expanded={expandedCategories.includes('characters')}>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </span>
            </button>
            {#if expandedCategories.includes('characters')}
              <div class="category-items">
                {#each results.characters as char}
                  <button class="mention-item" on:click={() => selectMention('character', char)}>
                    <span class="item-icon character">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                      </svg>
                    </span>
                    <span class="item-name">@{char.label || char.name}</span>
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        {/if}

        <!-- Files -->
        {#if results.files.length > 0}
          <div class="category">
            <button class="category-header" on:click={() => toggleCategory('files')}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
              </svg>
              <span>Files</span>
              <span class="category-count">{results.files.length}</span>
              <span class="category-arrow" class:expanded={expandedCategories.includes('files')}>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </span>
            </button>
            {#if expandedCategories.includes('files')}
              <div class="category-items">
                {#each results.files as file}
                  <button class="mention-item" on:click={() => selectMention('file', file)}>
                    <span class="item-icon file">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                      </svg>
                    </span>
                    <span class="item-name">@{file.name || file.path?.split('/').pop()}</span>
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        {/if}

        <!-- Locations -->
        {#if results.locations.length > 0}
          <div class="category">
            <button class="category-header" on:click={() => toggleCategory('locations')}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              <span>Locations</span>
              <span class="category-count">{results.locations.length}</span>
              <span class="category-arrow" class:expanded={expandedCategories.includes('locations')}>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </span>
            </button>
            {#if expandedCategories.includes('locations')}
              <div class="category-items">
                {#each results.locations as loc}
                  <button class="mention-item" on:click={() => selectMention('location', loc)}>
                    <span class="item-icon location">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                        <circle cx="12" cy="10" r="3"></circle>
                      </svg>
                    </span>
                    <span class="item-name">@{loc.label || loc.name}</span>
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        {/if}

        <!-- Themes -->
        {#if results.themes.length > 0}
          <div class="category">
            <button class="category-header" on:click={() => toggleCategory('themes')}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
              </svg>
              <span>Themes</span>
              <span class="category-count">{results.themes.length}</span>
              <span class="category-arrow" class:expanded={expandedCategories.includes('themes')}>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </span>
            </button>
            {#if expandedCategories.includes('themes')}
              <div class="category-items">
                {#each results.themes as theme}
                  <button class="mention-item" on:click={() => selectMention('theme', theme)}>
                    <span class="item-icon theme">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                      </svg>
                    </span>
                    <span class="item-name">@{theme.label || theme.name}</span>
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        {/if}
      {/if}
    </div>
  </div>
{/if}

<style>
  .mention-picker {
    position: absolute;
    bottom: calc(100% + 8px);
    left: 0;
    width: 280px;
    max-height: 360px;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    z-index: 100;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .picker-header {
    padding: 8px;
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-muted, #8b949e);
  }

  .search-box input {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-primary, #e6edf3);
    font-size: var(--text-sm, 12px);
    outline: none;
  }

  .search-box input::placeholder {
    color: var(--text-muted, #8b949e);
  }

  .picker-content {
    flex: 1;
    overflow-y: auto;
    padding: 4px 0;
  }

  .loading,
  .empty {
    padding: 24px;
    text-align: center;
    color: var(--text-muted, #8b949e);
    font-size: var(--text-sm, 12px);
  }

  .empty {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .empty-hint {
    font-size: var(--text-xs, 11px);
  }

  .category {
    margin-bottom: 2px;
  }

  .category-header {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 8px 12px;
    background: var(--bg-tertiary, #252d38);
    border: none;
    color: var(--text-secondary, #c9d1d9);
    font-size: var(--text-xs, 11px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: left;
    cursor: pointer;
    transition: background 0.1s ease;
  }

  .category-header:hover {
    background: var(--bg-elevated, #2d3748);
  }

  .category-count {
    color: var(--text-muted, #8b949e);
    font-weight: normal;
  }

  .category-arrow {
    margin-left: auto;
    display: flex;
    align-items: center;
    transition: transform 0.15s ease;
  }

  .category-arrow.expanded {
    transform: rotate(180deg);
  }

  .category-items {
    padding: 4px 0;
  }

  .mention-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 8px 12px 8px 20px;
    background: transparent;
    border: none;
    color: var(--text-secondary, #c9d1d9);
    font-size: var(--text-sm, 12px);
    text-align: left;
    cursor: pointer;
    transition: background 0.1s ease;
  }

  .mention-item:hover {
    background: var(--bg-tertiary, #252d38);
    color: var(--text-primary, #e6edf3);
  }

  .item-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: var(--radius-sm, 4px);
    flex-shrink: 0;
  }

  .item-icon.character {
    background: rgba(88, 166, 255, 0.2);
    color: var(--accent-cyan, #58a6ff);
  }

  .item-icon.file {
    background: rgba(212, 165, 116, 0.2);
    color: var(--accent-gold, #d4a574);
  }

  .item-icon.location {
    background: rgba(163, 113, 247, 0.2);
    color: var(--accent-purple, #a371f7);
  }

  .item-icon.theme {
    background: rgba(63, 185, 80, 0.2);
    color: var(--success, #3fb950);
  }

  .item-name {
    color: var(--accent-cyan, #58a6ff);
    font-weight: 500;
  }
</style>
