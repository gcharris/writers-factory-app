<!--
  AttachButton.svelte - Upload external files as context

  Opens file picker for files outside the project.
  Dispatches event with file content for the message.
-->
<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let fileInput;
  let isLoading = false;

  // Supported file types
  const acceptedTypes = [
    '.txt', '.md', '.markdown',
    '.pdf',
    '.doc', '.docx',
    '.json',
    '.csv',
    '.png', '.jpg', '.jpeg', '.gif', '.webp'
  ].join(',');

  function openFilePicker() {
    fileInput?.click();
  }

  async function handleFileSelect(e) {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    isLoading = true;

    try {
      for (const file of files) {
        const attachment = await processFile(file);
        if (attachment) {
          dispatch('attach', attachment);
        }
      }
    } catch (err) {
      console.error('Failed to process file:', err);
      dispatch('error', { message: 'Failed to process file' });
    } finally {
      isLoading = false;
      // Reset input so same file can be selected again
      if (fileInput) fileInput.value = '';
    }
  }

  async function processFile(file) {
    const isImage = file.type.startsWith('image/');
    const isPDF = file.type === 'application/pdf';
    const isText = file.type.startsWith('text/') ||
                   file.name.endsWith('.md') ||
                   file.name.endsWith('.markdown') ||
                   file.name.endsWith('.json') ||
                   file.name.endsWith('.csv');

    if (isImage) {
      // Convert image to base64
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          resolve({
            type: 'image',
            name: file.name,
            size: file.size,
            mimeType: file.type,
            content: reader.result // base64 data URL
          });
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    } else if (isText) {
      // Read text content
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          resolve({
            type: 'text',
            name: file.name,
            size: file.size,
            mimeType: file.type,
            content: reader.result
          });
        };
        reader.onerror = reject;
        reader.readAsText(file);
      });
    } else if (isPDF) {
      // For PDFs, just track the file reference (backend handles extraction)
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          resolve({
            type: 'pdf',
            name: file.name,
            size: file.size,
            mimeType: file.type,
            content: reader.result // base64
          });
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    } else {
      // Unsupported type - still allow but warn
      return {
        type: 'unknown',
        name: file.name,
        size: file.size,
        mimeType: file.type,
        content: null
      };
    }
  }

  function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
</script>

<input
  bind:this={fileInput}
  type="file"
  accept={acceptedTypes}
  multiple
  on:change={handleFileSelect}
  style="display: none;"
/>

<button
  class="attach-btn"
  on:click={openFilePicker}
  disabled={isLoading}
  title="Attach external file"
>
  {#if isLoading}
    <svg class="spinner" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
    </svg>
  {:else}
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
    </svg>
  {/if}
</button>

<style>
  .attach-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .attach-btn:hover:not(:disabled) {
    background: var(--bg-tertiary, #252d38);
    border-color: var(--border-strong, #444c56);
    color: var(--text-secondary, #c9d1d9);
  }

  .attach-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .spinner {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
