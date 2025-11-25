// frontend/src/lib/api_client.ts

const BASE_URL = "http://localhost:8000";

// --- Request Interfaces ---
export interface ProjectInitRequest {
    project_name: string;
    voice_sample: string;
    protagonist_name: string;
}

export interface TournamentRequest {
    scaffold: string;
}

export interface SceneSaveRequest {
    scene_id: number;
    winning_text: string;
}

// --- Response Interfaces ---
export interface TournamentScore {
    [dimension: string]: number;
}

export interface TournamentResult {
    agent_name: string;
    strategy_name: string;
    draft_text: string;
    scores: TournamentScore;
    total_score: number;
}

export interface SceneSaveResult {
    message: string;
    ingested_new_nodes: number;
}

export interface ScaffoldResult {
    scaffold: string;
}

// --- Session Interfaces ---
export interface SessionCreateRequest {
    scene_id?: string;
}

export interface SessionMessageRequest {
    role: 'user' | 'assistant' | 'system';
    content: string;
    scene_id?: string;
}

export interface SessionEvent {
    id: number;
    session_id: string;
    scene_id: string | null;
    role: string;
    content: string;
    token_count: number;
    is_committed: boolean;
    timestamp: string;
}

export interface SessionHistoryResponse {
    session_id: string;
    events: SessionEvent[];
}

export interface SessionCreateResponse {
    session_id: string;
    scene_id: string | null;
}

export interface SessionMessageResponse {
    status: string;
    event_id: number;
    token_count: number;
}

// --- Foreman Interfaces ---
export interface ForemanStartRequest {
    project_title: string;
    protagonist_name: string;
}

export interface ForemanChatRequest {
    message: string;
}

export interface ForemanNotebookRequest {
    notebook_id: string;
    role: 'world' | 'voice' | 'craft';
}

export interface ForemanTemplateRequirement {
    name: string;
    required_fields: string[];
    completed_fields: string[];
    status: 'pending' | 'partial' | 'complete';
}

export interface ForemanWorkOrder {
    project_title: string;
    protagonist_name: string;
    mode: 'ARCHITECT' | 'DIRECTOR' | 'EDITOR';
    templates: ForemanTemplateRequirement[];
}

export interface ForemanStartResponse {
    message: string;
    project_title: string;
    protagonist_name: string;
    mode: string;
}

export interface ForemanChatResponse {
    response: string;
    actions_executed: string[];
    work_order_status: ForemanWorkOrder;
}

export interface ForemanStatusWorkOrder {
    project_title: string;
    protagonist_name: string;
    mode: string;
    templates: Array<{
        name: string;
        file_path: string;
        status: string;
        required_fields: string[];
        missing_fields: string[];
        last_updated: string | null;
    }>;
    notebooks: Record<string, string>;
    completion_percentage: number;
    is_complete: boolean;
    created_at: string;
}

export interface ForemanStatusResponse {
    active: boolean;
    mode: string | null;
    work_order: ForemanStatusWorkOrder | null;
    conversation_length: number;
    kb_entries_pending: number;
}

/**
 * A TypeScript client for interacting with the Writers Factory Python backend.
 */
export class WritersFactoryAPI {
    private baseUrl: string;

    constructor(baseUrl: string = BASE_URL) {
        this.baseUrl = baseUrl;
    }

    private async _request(endpoint: string, options: RequestInit = {}): Promise<any> {
        const url = `${this.baseUrl}${endpoint}`;
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API request failed for endpoint: ${endpoint}`, error);
            throw error;
        }
    }

    /**
     * Runs the Setup Wizard to create a new project configuration.
     * @param data The project initialization data.
     */
    async initProject(data: ProjectInitRequest): Promise<{ message: string }> {
        return this._request('/project/init', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * Generates and returns the ACE scaffold for a given scene ID.
     * @param sceneId The ID of the scene to scaffold.
     */
    async getScaffold(sceneId: number): Promise<ScaffoldResult> {
        return this._request(`/graph/context/${sceneId}`);
    }

    /**
     * Accepts a scaffold, runs a tournament, and returns the scored drafts.
     * @param data The tournament request data containing the scaffold.
     */
    async runTournament(data: TournamentRequest): Promise<TournamentResult[]> {
        return this._request('/tournament/run', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * Saves the winning text of a scene and triggers graph ingestion.
     * @param data The scene save request data.
     */
    async saveScene(data: SceneSaveRequest): Promise<SceneSaveResult> {
        return this._request('/scene/save', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // ==========================================
    // Session Management (The Workbench)
    // ==========================================

    /**
     * Create a new chat session.
     * @param sceneId Optional scene ID to link this session to.
     */
    async createSession(sceneId?: string): Promise<SessionCreateResponse> {
        const body: SessionCreateRequest = {};
        if (sceneId) body.scene_id = sceneId;

        return this._request('/session/new', {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    /**
     * Log a message to a session.
     * Called BEFORE sending to LLM (for user) and AFTER receiving (for assistant).
     * @param sessionId The session UUID.
     * @param role Message role: 'user', 'assistant', or 'system'.
     * @param content The message content.
     * @param sceneId Optional scene ID for context.
     */
    async logMessage(
        sessionId: string,
        role: 'user' | 'assistant' | 'system',
        content: string,
        sceneId?: string
    ): Promise<SessionMessageResponse> {
        const body: SessionMessageRequest = { role, content };
        if (sceneId) body.scene_id = sceneId;

        return this._request(`/session/${sessionId}/message`, {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    /**
     * Get chat history for a session.
     * Used to restore UI state on page refresh.
     * @param sessionId The session UUID.
     * @param limit Max number of events to return (default 50).
     */
    async getSessionHistory(sessionId: string, limit: number = 50): Promise<SessionHistoryResponse> {
        return this._request(`/session/${sessionId}/history?limit=${limit}`);
    }

    /**
     * Get session statistics (for compaction decisions).
     * @param sessionId The session UUID.
     */
    async getSessionStats(sessionId: string): Promise<any> {
        return this._request(`/session/${sessionId}/stats`);
    }

    // ==========================================
    // The Foreman (Intelligent Creative Partner)
    // ==========================================

    /**
     * Start a new Foreman project.
     * @param projectTitle The project/novel title.
     * @param protagonistName The protagonist's name.
     */
    async foremanStart(projectTitle: string, protagonistName: string): Promise<ForemanStartResponse> {
        const body: ForemanStartRequest = {
            project_title: projectTitle,
            protagonist_name: protagonistName,
        };
        return this._request('/foreman/start', {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    /**
     * Chat with the Foreman.
     * @param message The user's message.
     */
    async foremanChat(message: string): Promise<ForemanChatResponse> {
        const body: ForemanChatRequest = { message };
        return this._request('/foreman/chat', {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    /**
     * Register a NotebookLM notebook with a role.
     * @param notebookId The NotebookLM notebook ID.
     * @param role The role: 'world', 'voice', or 'craft'.
     */
    async foremanRegisterNotebook(notebookId: string, role: 'world' | 'voice' | 'craft'): Promise<{ message: string }> {
        const body: ForemanNotebookRequest = { notebook_id: notebookId, role };
        return this._request('/foreman/notebook', {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    /**
     * Get Foreman status (work order, mode, etc.)
     */
    async foremanStatus(): Promise<ForemanStatusResponse> {
        return this._request('/foreman/status');
    }

    /**
     * Reset the Foreman for a new project.
     */
    async foremanReset(): Promise<{ message: string }> {
        return this._request('/foreman/reset', {
            method: 'POST',
        });
    }

    // ==========================================
    // Settings Management (Phase 3C)
    // ==========================================

    /**
     * Get a setting value.
     * @param key The setting key (e.g., "scoring.voice_authenticity_weight")
     * @param projectId Optional project ID for project-specific overrides
     */
    async getSetting(key: string, projectId?: string): Promise<{ key: string; value: any; source: string }> {
        const params = projectId ? `?project_id=${projectId}` : '';
        return this._request(`/settings/${key}${params}`);
    }

    /**
     * Set a setting value.
     * @param key The setting key
     * @param value The value to set
     * @param projectId Optional project ID for project-specific override
     */
    async setSetting(key: string, value: any, projectId?: string): Promise<{ message: string }> {
        return this._request('/settings', {
            method: 'POST',
            body: JSON.stringify({ key, value, project_id: projectId }),
        });
    }

    /**
     * Reset a setting to default.
     * @param key The setting key
     * @param projectId Optional project ID to reset project override only
     */
    async resetSetting(key: string, projectId?: string): Promise<{ message: string }> {
        const params = projectId ? `?project_id=${projectId}` : '';
        return this._request(`/settings/${key}${params}`, { method: 'DELETE' });
    }

    /**
     * Get all settings in a category.
     * @param category The category name (e.g., "scoring", "foreman", "orchestrator")
     * @param projectId Optional project ID
     */
    async getSettingsCategory(category: string, projectId?: string): Promise<{ [key: string]: any }> {
        const params = projectId ? `?project_id=${projectId}` : '';
        return this._request(`/settings/category/${category}${params}`);
    }

    /**
     * Export all settings as dictionary.
     */
    async exportSettings(projectId?: string): Promise<{ [key: string]: any }> {
        const params = projectId ? `?project_id=${projectId}` : '';
        return this._request(`/settings/export${params}`);
    }

    /**
     * Get default settings.
     */
    async getDefaultSettings(): Promise<{ [key: string]: any }> {
        return this._request('/settings/defaults');
    }

    // ==========================================
    // Model Orchestrator (Phase 3E)
    // ==========================================

    /**
     * Get model capabilities registry.
     */
    async getModelCapabilities(): Promise<{
        models: Array<{
            model_id: string;
            provider: string;
            display_name: string;
            strengths: string[];
            quality_score: number;
            speed: string;
            cost_per_1m_input: number;
            cost_per_1m_output: number;
            requires_api_key: boolean;
            local_only: boolean;
            api_key_env_var: string | null;
        }>;
        available_providers: { [provider: string]: boolean };
    }> {
        return this._request('/orchestrator/capabilities');
    }

    /**
     * Estimate monthly cost for a quality tier.
     * @param qualityTier "budget" | "balanced" | "premium"
     * @param tasksPerMonth Estimated number of tasks
     */
    async estimateCost(qualityTier: string, tasksPerMonth: number = 100): Promise<{
        quality_tier: string;
        estimated_monthly_cost_usd: number;
        cost_breakdown: { [task: string]: number };
    }> {
        return this._request('/orchestrator/estimate-cost', {
            method: 'POST',
            body: JSON.stringify({ quality_tier: qualityTier, tasks_per_month: tasksPerMonth }),
        });
    }

    /**
     * Get model recommendations for a task type.
     * @param taskType The task type (e.g., "coordinator", "health_check_review")
     * @param qualityTier Optional quality tier override
     */
    async getModelRecommendations(taskType: string, qualityTier?: string): Promise<{
        task_type: string;
        recommendations: {
            budget: string;
            balanced: string;
            premium: string;
        };
        selected: string;
        reason: string;
    }> {
        const params = qualityTier ? `?quality_tier=${qualityTier}` : '';
        return this._request(`/orchestrator/recommendations/${taskType}${params}`);
    }

    /**
     * Get current month spending.
     */
    async getCurrentSpend(): Promise<{
        month: string;
        total_spend_usd: number;
        budget_usd: number | null;
        remaining_usd: number | null;
        percentage_used: number | null;
    }> {
        return this._request('/orchestrator/current-spend');
    }

    // ==========================================
    // Story Bible System (ARCHITECT Mode)
    // ==========================================

    /**
     * Get Story Bible validation status.
     */
    async getStoryBibleStatus(): Promise<{
        phase2_complete: boolean;
        completion_score: number;
        checks: Array<{
            name: string;
            passed: boolean;
            status: string;
        }>;
        protagonist: {
            name: string;
            fatal_flaw: string;
            the_lie: string;
            true_character: string;
            characterization: string;
            arc_start: string;
            arc_midpoint: string;
            arc_resolution: string;
        } | null;
        beat_sheet: {
            title: string | null;
            completion: number;
            current_beat: number | null;
            midpoint_type: string | null;
        };
        can_proceed_to_execution: boolean;
        blocking_issues: string[];
    }> {
        return this._request('/story-bible/status');
    }

    /**
     * Create Story Bible scaffolding.
     * @param projectTitle The project/novel title
     * @param protagonistName The protagonist's name
     * @param preFilled Optional pre-filled data for templates
     */
    async scaffoldStoryBible(
        projectTitle: string,
        protagonistName: string,
        preFilled?: Record<string, any>
    ): Promise<{
        created_files: string[];
        project_title: string;
        protagonist_name: string;
    }> {
        return this._request('/story-bible/scaffold', {
            method: 'POST',
            body: JSON.stringify({
                project_title: projectTitle,
                protagonist_name: protagonistName,
                pre_filled: preFilled
            }),
        });
    }

    /**
     * Get parsed protagonist data.
     */
    async getProtagonistData(): Promise<{
        name: string;
        fatal_flaw: string;
        the_lie: string;
        true_character: string;
        characterization: string;
        arc_start: string;
        arc_midpoint: string;
        arc_resolution: string;
        relationships: Array<{ character: string; function: string }>;
        contradiction_score: number;
        is_valid: boolean;
    }> {
        return this._request('/story-bible/protagonist');
    }

    /**
     * Get parsed beat sheet data.
     */
    async getBeatSheetData(): Promise<{
        title: string;
        beats: Array<{
            number: number;
            name: string;
            percentage: string;
            description: string;
            scene_link: string;
            is_complete: boolean;
        }>;
        current_beat: number;
        midpoint_type: string;
        theme_stated: string;
        is_valid: boolean;
        completion_percentage: number;
    }> {
        return this._request('/story-bible/beat-sheet');
    }

    /**
     * Ensure Story Bible directory structure exists.
     */
    async ensureStoryBibleStructure(): Promise<{
        directories: Record<string, string>;
        created: string[];
    }> {
        return this._request('/story-bible/ensure-structure', { method: 'POST' });
    }

    /**
     * Check if ready for Phase 3 (Execution).
     */
    async canExecute(): Promise<{
        ready: boolean;
        blocking_issues: string[];
        completion_percentage: number;
    }> {
        return this._request('/story-bible/can-execute');
    }

    /**
     * Run AI-powered Story Bible generation from NotebookLM.
     * @param projectTitle The project/novel title
     * @param protagonistName The protagonist's name
     * @param notebookId Optional NotebookLM notebook ID
     */
    async runSmartScaffold(
        projectTitle: string,
        protagonistName: string,
        notebookId?: string
    ): Promise<{
        status: string;
        created_files: string[];
        enrichment_used: boolean;
        project_title: string;
        protagonist_name: string;
    }> {
        return this._request('/story-bible/smart-scaffold', {
            method: 'POST',
            body: JSON.stringify({
                project_title: projectTitle,
                protagonist_name: protagonistName,
                notebook_id: notebookId
            }),
        });
    }

    // ==========================================
    // NotebookLM Integration
    // ==========================================

    /**
     * Get NotebookLM connection status.
     */
    async getNotebookLMStatus(): Promise<{
        connected: boolean;
        message: string;
    }> {
        return this._request('/notebooklm/status');
    }

    /**
     * Get list of configured NotebookLM notebooks.
     */
    async getNotebookLMList(): Promise<{
        notebooks: Array<{
            id: string;
            name: string;
            role: string | null;
        }>;
    }> {
        return this._request('/notebooklm/notebooks');
    }

    /**
     * Query a NotebookLM notebook.
     * @param notebookId The notebook ID
     * @param query The query text
     */
    async queryNotebook(notebookId: string, query: string): Promise<{
        answer: string;
        sources: string[];
    }> {
        return this._request('/notebooklm/query', {
            method: 'POST',
            body: JSON.stringify({ notebook_id: notebookId, query }),
        });
    }
}

// Export a singleton instance for easy use across the Svelte app
export const apiClient = new WritersFactoryAPI();
