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
}

// Export a singleton instance for easy use across the Svelte app
export const apiClient = new WritersFactoryAPI();
