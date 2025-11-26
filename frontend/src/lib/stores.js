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
export const activeModal = writable(null); // 'story-bible' | 'notebook-registration' | 'template-editor' | 'voice-tournament' | null
export const modalData = writable(null); // Data passed to modal (e.g., which template to edit)

// --- Voice Calibration State (VOICE_CALIBRATION Mode) ---

// Available agents for tournament
export const voiceAgents = writable([]);
export const voiceAgentsLoading = writable(false);

// Current tournament state
export const currentTournament = writable(null); // { tournament_id, status, selected_agents, variants }
export const tournamentLoading = writable(false);
export const tournamentStatus = writable(null); // 'not_started' | 'running' | 'awaiting_selection' | 'complete' | 'failed'

// Tournament variants
export const tournamentVariants = writable([]); // Array of variants from all agents
export const selectedVariants = writable([]); // Variants selected for comparison

// Voice configuration (set during winner selection)
export const voiceConfig = writable({
    pov: 'third_limited',
    tense: 'past',
    voice_type: 'character_voice',
    metaphor_domains: [],
    anti_patterns: [],
    phase_evolution: {
        'Act 1': '',
        'Act 2A': '',
        'Act 2B': '',
        'Act 3': ''
    }
});

// Voice calibration result
export const voiceCalibration = writable(null); // Final voice calibration document
export const voiceBundleGenerated = writable(false);

// UI state for voice calibration
export const showVoiceTournament = writable(false);
export const voiceTournamentStep = writable(0); // 0: Configure, 1: Running, 2: Review Variants, 3: Select Winner, 4: Generate Bundle

// --- Director Mode State (DIRECTOR Mode) ---

// Current scaffold state
export const currentScaffold = writable(null); // { scene_id, scaffold, draft_summary, enrichment_data }
export const scaffoldLoading = writable(false);
export const scaffoldStep = writable(0); // 0: Input, 1: Draft Summary, 2: Enrichment, 3: Full Scaffold

// Structure variants
export const structureVariants = writable([]); // Array of structure variants
export const selectedStructure = writable(null); // Selected structure variant

// Scene variants (from tournament)
export const sceneVariants = writable([]); // Array of { id, model, strategy, content, word_count, score, scores }
export const sceneVariantsLoading = writable(false);
export const selectedSceneVariants = writable([]); // Selected for comparison/hybrid

// Scene analysis
export const currentSceneAnalysis = writable(null); // Full analysis result
export const sceneAnalysisLoading = writable(false);

// Enhancement state
export const enhancementMode = writable(null); // 'action_prompt' | 'six_pass' | null
export const actionPromptFixes = writable([]); // Array of fixes from action prompt
export const selectedFixes = writable([]); // Fixes selected for application
export const sixPassProgress = writable(null); // { current_pass, passes_completed, total_changes }
export const enhancementLoading = writable(false);

// Current scene content (working draft)
export const currentSceneContent = writable('');
export const currentSceneId = writable(null);
export const currentSceneScore = writable(null);

// Scene version history
export const sceneVersions = writable([]); // Array of { version, content, score, timestamp }

// Director UI state
export const showScaffoldGenerator = writable(false);
export const showSceneGenerator = writable(false);
export const showEnhancementPanel = writable(false);
export const directorStep = writable(0); // 0: Scaffold, 1: Structure, 2: Generate, 3: Compare, 4: Enhance, 5: Complete

// Beat progress tracking
export const currentBeat = writable(null); // { number, name, percentage, description }
export const manuscriptProgress = writable(0); // 0-100 percentage through manuscript

// --- Knowledge Graph State ---

// Selected node in graph explorer
export const selectedNode = writable(null);

// Graph filter settings
export const graphFilters = writable({
  enabledTypes: ['CHARACTER', 'LOCATION', 'THEME', 'EVENT', 'OBJECT', 'CONCEPT'],
  searchQuery: ''
});

// Search query (also available separately for convenience)
export const searchQuery = writable('');

// Pinned nodes (nodes locked in position)
export const pinnedNodes = writable(new Set());
