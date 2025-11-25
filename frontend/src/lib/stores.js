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
export const foremanMode = writable(null); // 'ARCHITECT' | 'VOICE_CALIBRATION' | 'DIRECTOR' | 'EDITOR'
export const foremanProjectTitle = writable(null);
export const foremanProtagonist = writable(null);
export const foremanWorkOrder = writable(null);

// Foreman chat history (separate from manager)
export const foremanChatHistory = writable([]);

// --- Story Bible State (ARCHITECT Mode) ---

// Story Bible status from /story-bible/status endpoint
export const storyBibleStatus = writable(null);
export const storyBibleLoading = writable(false);

// Template tracking - maps to Work Order templates
export const templateStatus = writable({
    protagonist: { status: 'pending', completion: 0 },
    beat_sheet: { status: 'pending', completion: 0 },
    theme: { status: 'pending', completion: 0 },
    world_rules: { status: 'pending', completion: 0 }
});

// Story Bible wizard state
export const showStoryBibleWizard = writable(false);
export const wizardStep = writable(0); // 0: Start, 1: Protagonist, 2: Beats, 3: Theme, 4: World

// --- NotebookLM Integration State ---
export const notebookLMConnected = writable(false);
export const registeredNotebooks = writable([]); // Array of { id, name, role }
export const showNotebookRegistration = writable(false);

// --- UI Modal State ---
export const activeModal = writable(null); // 'story-bible' | 'notebook-registration' | 'template-editor' | null
export const modalData = writable(null); // Data passed to modal (e.g., which template to edit)
