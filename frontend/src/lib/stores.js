import { writable } from 'svelte/store';

// --- Editor State ---
export const editorContent = writable("");
export const activeFile = writable("");
export const isSaving = writable(false);

// --- File Tree State ---
export const expandedFolders = writable({});

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

// --- Onboarding State ---
// Track whether user has completed first-time Squad setup
export const hasCompletedOnboarding = persistentWritable('wf_onboarding_complete', false);

// --- Workspace State ---
// User-selected location for all writing projects
export const workspacePath = persistentWritable('wf_workspace_path', null);

// Currently active project within the workspace
export const activeProjectName = persistentWritable('wf_active_project', null);

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

// --- Assistant Panel State (Muse/Scribe) ---

// Configurable assistant name (default: "Muse")
export const assistantName = persistentWritable('wf_assistant_name', 'Muse');

// --- Chat Model Selection ---

// Default model set during onboarding (e.g., 'deepseek-chat')
export const defaultChatModel = persistentWritable('wf_default_chat_model', 'deepseek-chat');

// Currently selected model for next message (session only, not persisted)
export const selectedChatModel = writable(null); // null means use defaultChatModel

// Writing stage (auto-detected, manually overridable)
export const currentStage = persistentWritable('wf_current_stage', 'conception');

// Stage progress (tracks completion of each stage)
export const stageProgress = writable({
  conception: 0,
  voice: 0,
  execution: 0,
  polish: 0
});

// Assistant settings
export const assistantSettings = persistentWritable('wf_assistant_settings', {
  autoIncludeFile: true,
  showStage: true,
  confirmStageChange: false,
  // Voice input settings
  voiceEnabled: true,
  voiceLanguage: 'en-US',
  voiceContinuous: true
});

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

// --- Work Order State (Background Tasks) ---

/**
 * Work order structure:
 * {
 *   id: string,
 *   type: 'voice_tournament' | 'scene_generation' | 'story_bible' | 'health_check' | 'consolidation',
 *   name: string,
 *   status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled',
 *   progress: { current: number, total: number } | null,
 *   message: string | null,
 *   started_at: string | null,
 *   completed_at: string | null,
 *   result: any | null,
 *   error: string | null
 * }
 */

// All work orders (history + active)
export const workOrders = persistentWritable('wf_work_orders', []);

// Currently active work order (null if idle)
export const activeWorkOrder = writable(null);

// Work order history visibility
export const showWorkOrderHistory = writable(false);

/**
 * Helper: Create a new work order
 * @param {string} type - Work order type
 * @param {string} name - Human-readable name
 * @returns {object} New work order object
 */
export function createWorkOrder(type, name) {
  return {
    id: `wo_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
    type,
    name,
    status: 'pending',
    progress: null,
    message: null,
    started_at: null,
    completed_at: null,
    result: null,
    error: null
  };
}

/**
 * Helper: Update work order in store
 * @param {string} id - Work order ID
 * @param {object} updates - Fields to update
 */
export function updateWorkOrder(id, updates) {
  workOrders.update(orders => {
    const idx = orders.findIndex(o => o.id === id);
    if (idx >= 0) {
      orders[idx] = { ...orders[idx], ...updates };
    }
    return [...orders];
  });

  // Also update active work order if it matches
  activeWorkOrder.update(active => {
    if (active && active.id === id) {
      return { ...active, ...updates };
    }
    return active;
  });
}

/**
 * Helper: Start a work order
 * @param {object} workOrder - Work order to start
 */
export function startWorkOrder(workOrder) {
  const startedOrder = {
    ...workOrder,
    status: 'running',
    started_at: new Date().toISOString()
  };

  workOrders.update(orders => [startedOrder, ...orders]);
  activeWorkOrder.set(startedOrder);

  return startedOrder;
}

/**
 * Helper: Complete a work order
 * @param {string} id - Work order ID
 * @param {any} result - Result data
 */
export function completeWorkOrder(id, result = null) {
  const updates = {
    status: 'completed',
    completed_at: new Date().toISOString(),
    result
  };

  updateWorkOrder(id, updates);

  activeWorkOrder.update(active => {
    if (active && active.id === id) {
      return null;
    }
    return active;
  });
}

/**
 * Helper: Fail a work order
 * @param {string} id - Work order ID
 * @param {string} error - Error message
 */
export function failWorkOrder(id, error) {
  const updates = {
    status: 'failed',
    completed_at: new Date().toISOString(),
    error
  };

  updateWorkOrder(id, updates);

  activeWorkOrder.update(active => {
    if (active && active.id === id) {
      return null;
    }
    return active;
  });
}

/**
 * Helper: Cancel a work order
 * @param {string} id - Work order ID
 */
export function cancelWorkOrder(id) {
  const updates = {
    status: 'cancelled',
    completed_at: new Date().toISOString()
  };

  updateWorkOrder(id, updates);

  activeWorkOrder.update(active => {
    if (active && active.id === id) {
      return null;
    }
    return active;
  });
}

/**
 * Helper: Clear completed/failed work orders older than N days
 * @param {number} days - Days to keep (default 7)
 */
export function clearOldWorkOrders(days = 7) {
  const cutoff = Date.now() - (days * 24 * 60 * 60 * 1000);

  workOrders.update(orders =>
    orders.filter(o =>
      o.status === 'running' ||
      o.status === 'pending' ||
      (o.completed_at && new Date(o.completed_at).getTime() > cutoff)
    )
  );
}
