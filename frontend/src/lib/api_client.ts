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
}

// Export a singleton instance for easy use across the Svelte app
export const apiClient = new WritersFactoryAPI();
