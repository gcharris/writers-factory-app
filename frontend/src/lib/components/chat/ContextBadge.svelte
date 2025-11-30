<!--
  ContextBadge.svelte - Shows attached context items

  Displays:
  - Active file (from editor, if auto-include enabled)
  - Mentioned files/entities (@mentions)
  - Attached files (uploads)

  Each badge has a remove button.
-->
<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  export let items = []; // Array of { type, name, id?, path?, removable? }
  export let compact = false; // Compact mode for inline display in input box

  function getIcon(type) {
    switch (type) {
      case 'file':
      case 'active-file':
        return `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>`;
      case 'character':
        return `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>`;
      case 'location':
        return `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
          <circle cx="12" cy="10" r="3"></circle>
        </svg>`;
      case 'theme':
        return `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
        </svg>`;
      case 'image':
        return `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>`;
      case 'pdf':
        return `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>`;
      default:
        return `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
        </svg>`;
    }
  }

  function getTypeClass(type) {
    switch (type) {
      case 'active-file': return 'active-file';
      case 'file': return 'file';
      case 'character': return 'character';
      case 'location': return 'location';
      case 'theme': return 'theme';
      case 'image': return 'image';
      case 'pdf': return 'pdf';
      default: return 'attachment';
    }
  }

  function removeItem(item, index) {
    dispatch('remove', { item, index });
  }

  function truncateName(name, maxLength = 20) {
    if (name.length <= maxLength) return name;
    return name.substring(0, maxLength - 3) + '...';
  }
</script>

{#if items.length > 0}
  <div class="context-badges" class:compact>
    {#each items as item, i}
      <div class="badge {getTypeClass(item.type)}" title={item.name}>
        <span class="badge-icon">{@html getIcon(item.type)}</span>
        <span class="badge-name">{truncateName(item.name)}</span>
        {#if item.removable !== false}
          <button
            class="badge-remove"
            on:click={() => removeItem(item, i)}
            title="Remove"
          >
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        {/if}
      </div>
    {/each}
  </div>
{/if}

<style>
  .context-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 8px 0;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #c9d1d9);
  }

  .badge-icon {
    display: flex;
    align-items: center;
  }

  /* Type-specific colors */
  .badge.active-file {
    background: rgba(88, 166, 255, 0.15);
    border-color: rgba(88, 166, 255, 0.3);
  }
  .badge.active-file .badge-icon { color: var(--accent-cyan, #58a6ff); }

  .badge.file {
    background: rgba(212, 165, 116, 0.15);
    border-color: rgba(212, 165, 116, 0.3);
  }
  .badge.file .badge-icon { color: var(--accent-gold, #d4a574); }

  .badge.character {
    background: rgba(88, 166, 255, 0.15);
    border-color: rgba(88, 166, 255, 0.3);
  }
  .badge.character .badge-icon { color: var(--accent-cyan, #58a6ff); }

  .badge.location {
    background: rgba(163, 113, 247, 0.15);
    border-color: rgba(163, 113, 247, 0.3);
  }
  .badge.location .badge-icon { color: var(--accent-purple, #a371f7); }

  .badge.theme {
    background: rgba(63, 185, 80, 0.15);
    border-color: rgba(63, 185, 80, 0.3);
  }
  .badge.theme .badge-icon { color: var(--success, #3fb950); }

  .badge.image {
    background: rgba(163, 113, 247, 0.15);
    border-color: rgba(163, 113, 247, 0.3);
  }
  .badge.image .badge-icon { color: var(--accent-purple, #a371f7); }

  .badge.pdf {
    background: rgba(248, 81, 73, 0.15);
    border-color: rgba(248, 81, 73, 0.3);
  }
  .badge.pdf .badge-icon { color: var(--error, #f85149); }

  .badge.attachment {
    background: var(--bg-tertiary, #252d38);
  }

  .badge-name {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .badge-remove {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 14px;
    height: 14px;
    padding: 0;
    margin-left: 2px;
    background: transparent;
    border: none;
    border-radius: 50%;
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .badge-remove:hover {
    background: var(--bg-elevated, #2d3748);
    color: var(--error, #f85149);
  }

  /* Compact mode for inline display */
  .context-badges.compact {
    padding: 0;
    gap: 4px;
  }

  .context-badges.compact .badge {
    padding: 2px 6px;
  }

  .context-badges.compact .badge-name {
    max-width: 100px;
  }
</style>
