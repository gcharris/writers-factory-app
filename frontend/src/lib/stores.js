import { writable } from 'svelte/store';

// --- Editor State ---
export const editorContent = writable("");
export const activeFile = writable("");
export const isSaving = writable(false);

// --- NotebookLM State ---
export const notebookStatus = writable("checking");
export const notebookList = writable([]);
export const selectedNotebookId = writable("");
export const notebookLoading = writable(false);
export const notebookError = writable("");
export const notebookResult = writable(null);

// --- Session State (The Workbench) ---
// These stores persist chat history across page refreshes

/**
 * Helper: Create a store that syncs with localStorage
 * @param {string} key - localStorage key
 * @param {any} initialValue - default value if not in localStorage
 * @returns {import('svelte/store').Writable<any>}
 */
function persistentWritable(key, initialValue) {
    // Check if we're in browser environment
    const isBrowser = typeof window !== 'undefined' && typeof localStorage !== 'undefined';

    // Try to get from localStorage first
    let storedValue = initialValue;
    if (isBrowser) {
        try {
            const item = localStorage.getItem(key);
            if (item !== null) {
                storedValue = JSON.parse(item);
            }
        } catch (e) {
            console.warn(`Failed to read ${key} from localStorage:`, e);
        }
    }

    const store = writable(storedValue);

    // Subscribe to changes and sync to localStorage
    if (isBrowser) {
        store.subscribe(value => {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.warn(`Failed to write ${key} to localStorage:`, e);
            }
        });
    }

    return store;
}

// Session ID - persists across refreshes
export const sessionId = persistentWritable('wf_session_id', null);

// Chat history - mirrors backend but also cached locally for fast UI
export const chatHistory = writable([]);

// Session metadata
export const sessionSceneId = persistentWritable('wf_session_scene_id', null);
export const sessionInitialized = writable(false);
export const sessionError = writable(null);

// --- Foreman State (The Creative Partner) ---

// Foreman project state
export const foremanActive = writable(false);
export const foremanMode = writable(null); // 'ARCHITECT' | 'DIRECTOR' | 'EDITOR'
export const foremanProjectTitle = writable(null);
export const foremanProtagonist = writable(null);
export const foremanWorkOrder = writable(null);

// Foreman chat history (separate from manager)
export const foremanChatHistory = writable([]);
