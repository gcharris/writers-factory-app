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
}

// Export a singleton instance for easy use across the Svelte app
export const apiClient = new WritersFactoryAPI();
