<!-- src/lib/components/FileTree.svelte -->
<script lang="ts">
    import { apiClient } from '$lib/api_client';

    type Status = 'idle' | 'running' | 'complete' | 'error';
    let initStatus: Status = 'idle';
    let initError: string | null = null;

    const dummyFiles = [
        { id: 1, name: 'Chapter 1.md' },
        { id: 2, name: 'Chapter 2.md' },
        { id: 3, name: 'Notes.md' },
        { id: 4, name: 'Characters/Alice.md' },
        { id: 5, name: 'Characters/Bob.md' },
    ];

    async function handleInit() {
        initStatus = 'running';
        initError = null;
        try {
            const response = await apiClient.initProject({
                project_name: "student_project",
                voice_sample: "A gritty, noir voice for a detective who has seen too much.",
                protagonist_name: "Alice"
            });
            console.log(response.message);
            initStatus = 'complete';
        } catch (e: any) {
            initError = e.message || "Failed to initialize project.";
            initStatus = 'error';
        }
    }
</script>

<div class="file-tree">
    <div class="project-actions">
        <button on:click={handleInit} disabled={initStatus === 'running'}>
            {#if initStatus === 'running'}
                Initializing...
            {:else}
                Initialize Project
            {/if}
        </button>
        {#if initStatus === 'complete'}
            <p class="success-message">Project initialized successfully!</p>
        {/if}
        {#if initStatus === 'error'}
            <p class="error-message">{initError}</p>
        {/if}
    </div>

    <h2>Project Files</h2>
    <ul>
        {#each dummyFiles as file}
            <li>{file.name}</li>
        {/each}
    </ul>
</div>

<style>
    .file-tree {
        background-color: #2a2a2a;
        color: #e0e0e0;
        padding: 1rem;
        height: 100%;
        overflow-y: auto;
    }
    .project-actions {
        padding-bottom: 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #444;
    }
    button {
        background-color: #3e8e41;
        color: white;
        border: none;
        padding: 0.7rem 1rem;
        font-size: 0.9rem;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        transition: background-color 0.2s;
    }
    button:hover:not(:disabled) {
        background-color: #2e6b31;
    }
    button:disabled {
        background-color: #555;
        cursor: not-allowed;
    }
    .success-message {
        color: #4caf50;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    .error-message {
        color: #f44336;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    h2 {
        font-size: 1.1rem;
        margin-top: 0;
        border-bottom: 1px solid #444;
        padding-bottom: 0.5rem;
    }
    ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }
    li {
        padding: 0.5rem 0.25rem;
        cursor: pointer;
        border-radius: 4px;
    }
    li:hover {
        background-color: #3c3c3c;
    }
</style>