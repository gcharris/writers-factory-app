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

    // ==========================================
    // Voice Calibration (VOICE_CALIBRATION Mode)
    // ==========================================

    /**
     * Get available agents for voice tournament.
     */
    async getVoiceCalibrationAgents(): Promise<{
        agents: Array<{
            id: string;
            name: string;
            provider: string;
            model: string;
            role: string;
            enabled: boolean;
            has_valid_key: boolean;
            use_cases: string[];
        }>;
    }> {
        return this._request('/voice-calibration/agents');
    }

    /**
     * Start a voice calibration tournament.
     * @param projectId Project identifier
     * @param testPrompt The test passage prompt
     * @param testContext Context about the scene
     * @param agentIds List of agent IDs to include
     * @param variantsPerAgent Number of variants per agent (default 5)
     * @param voiceDescription Optional writer's voice description
     */
    async startVoiceTournament(
        projectId: string,
        testPrompt: string,
        testContext: string,
        agentIds: string[],
        variantsPerAgent: number = 5,
        voiceDescription?: string
    ): Promise<{
        tournament_id: string;
        project_id: string;
        status: string;
        selected_agents: string[];
    }> {
        return this._request('/voice-calibration/tournament/start', {
            method: 'POST',
            body: JSON.stringify({
                project_id: projectId,
                test_prompt: testPrompt,
                test_context: testContext,
                agent_ids: agentIds,
                variants_per_agent: variantsPerAgent,
                voice_description: voiceDescription
            }),
        });
    }

    /**
     * Get tournament status.
     * @param tournamentId The tournament ID
     */
    async getTournamentStatus(tournamentId: string): Promise<{
        tournament_id: string;
        status: string;
        selected_agents: string[];
        variant_count: number;
        created_at: string;
        completed_at: string | null;
    }> {
        return this._request(`/voice-calibration/tournament/${tournamentId}/status`);
    }

    /**
     * Get tournament variants.
     * @param tournamentId The tournament ID
     * @param agentId Optional filter by agent
     */
    async getTournamentVariants(tournamentId: string, agentId?: string): Promise<{
        variants: Array<{
            agent_id: string;
            agent_name: string;
            variant_number: number;
            strategy: string;
            content: string;
            word_count: number;
            generated_at: string;
        }>;
    }> {
        const params = agentId ? `?agent_id=${agentId}` : '';
        return this._request(`/voice-calibration/tournament/${tournamentId}/variants${params}`);
    }

    /**
     * Select winning variant and create voice calibration document.
     * @param tournamentId The tournament ID
     * @param winnerAgentId The winning agent's ID
     * @param winnerVariantIndex Index of winning variant
     * @param voiceConfig Voice configuration choices
     */
    async selectVoiceWinner(
        tournamentId: string,
        winnerAgentId: string,
        winnerVariantIndex: number,
        voiceConfig: {
            pov: string;
            tense: string;
            voice_type: string;
            metaphor_domains: string[];
            anti_patterns: string[];
            phase_evolution: Record<string, string>;
        }
    ): Promise<{
        message: string;
        voice_calibration: {
            project_id: string;
            pov: string;
            tense: string;
            voice_type: string;
            winning_agent: string;
        };
    }> {
        return this._request(`/voice-calibration/tournament/${tournamentId}/select`, {
            method: 'POST',
            body: JSON.stringify({
                winner_agent_id: winnerAgentId,
                winner_variant_index: winnerVariantIndex,
                voice_config: voiceConfig
            }),
        });
    }

    /**
     * Generate Voice Reference Bundle files.
     * @param projectId Project identifier
     */
    async generateVoiceBundle(projectId: string): Promise<{
        files: {
            gold_standard: string;
            anti_patterns: string;
            phase_evolution?: string;
        };
        message: string;
    }> {
        return this._request(`/voice-calibration/generate-bundle/${projectId}`, {
            method: 'POST',
        });
    }

    /**
     * Get existing voice calibration for project.
     * @param projectId Project identifier
     */
    async getVoiceCalibration(projectId: string): Promise<{
        calibration: {
            project_id: string;
            pov: string;
            tense: string;
            voice_type: string;
            metaphor_domains: string[];
            anti_patterns: string[];
            phase_evolution: Record<string, string>;
            winning_agent: string;
            reference_sample: string;
        } | null;
    }> {
        return this._request(`/voice-calibration/${projectId}`);
    }

    // ==========================================
    // Director Mode - Scene Creation Pipeline
    // ==========================================

    // --- Scaffold Generation ---

    /**
     * Generate draft summary for a scene scaffold (Stage 1).
     * @param projectId Project identifier
     * @param chapterNumber Chapter number
     * @param sceneNumber Scene number within chapter
     * @param beatInfo Beat this scene serves
     * @param characters Characters in scene
     * @param sceneDescription Writer's description of scene
     */
    async generateDraftSummary(
        projectId: string,
        chapterNumber: number,
        sceneNumber: number,
        beatInfo: string,
        characters: string[],
        sceneDescription: string
    ): Promise<{
        draft_summary: string;
        enrichment_suggestions: Array<{ query: string; notebook_role: string }>;
        context_used: {
            protagonist: any;
            theme: any;
            voice_bundle: any;
        };
    }> {
        return this._request('/director/scaffold/draft-summary', {
            method: 'POST',
            body: JSON.stringify({
                project_id: projectId,
                chapter_number: chapterNumber,
                scene_number: sceneNumber,
                beat_info: beatInfo,
                characters: characters,
                scene_description: sceneDescription
            }),
        });
    }

    /**
     * Fetch enrichment data from NotebookLM.
     * @param notebookId NotebookLM notebook ID
     * @param query Query to run
     */
    async enrichScaffold(notebookId: string, query: string): Promise<{
        answer: string;
        sources: string[];
    }> {
        return this._request('/director/scaffold/enrich', {
            method: 'POST',
            body: JSON.stringify({ notebook_id: notebookId, query }),
        });
    }

    /**
     * Generate full scaffold with optional enrichment (Stage 2).
     */
    async generateScaffold(
        projectId: string,
        chapterNumber: number,
        sceneNumber: number,
        title: string,
        beatInfo: string,
        characters: string[],
        sceneDescription: string,
        enrichmentData?: Array<{ query: string; answer: string }>
    ): Promise<{
        scaffold: string;
        scene_id: string;
        enrichment_used: boolean;
    }> {
        return this._request('/director/scaffold/generate', {
            method: 'POST',
            body: JSON.stringify({
                project_id: projectId,
                chapter_number: chapterNumber,
                scene_number: sceneNumber,
                title: title,
                beat_info: beatInfo,
                characters: characters,
                scene_description: sceneDescription,
                enrichment_data: enrichmentData
            }),
        });
    }

    // --- Scene Writing ---

    /**
     * Generate 5 structural approaches before writing prose.
     */
    async generateStructureVariants(
        sceneId: string,
        beatDescription: string,
        povCharacter: string,
        targetWordCount: number,
        scaffold?: string
    ): Promise<{
        variants: Array<{
            id: string;
            name: string;
            description: string;
            scenes: Array<{ title: string; word_count: number; beat: string }>;
            total_word_count: number;
            pacing: string;
        }>;
    }> {
        return this._request('/director/scene/structure-variants', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneId,
                beat_description: beatDescription,
                pov_character: povCharacter,
                target_word_count: targetWordCount,
                scaffold: scaffold
            }),
        });
    }

    /**
     * Run multi-model tournament with 5 strategies each.
     * @param sceneId Scene identifier
     * @param scaffold Scene scaffold
     * @param structureVariant Selected structure variant
     * @param voiceBundlePath Path to voice bundle
     * @param models Models to use (default: 3)
     * @param strategies Strategies per model (default: 5)
     */
    async generateSceneVariants(
        sceneId: string,
        scaffold: string,
        structureVariant: string,
        voiceBundlePath?: string,
        models?: string[],
        strategies?: string[]
    ): Promise<{
        tournament_id: string;
        variants: Array<{
            id: string;
            model: string;
            strategy: string;
            content: string;
            word_count: number;
            score?: number;
            scores?: { [category: string]: number };
        }>;
        total_variants: number;
    }> {
        return this._request('/director/scene/generate-variants', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneId,
                scaffold: scaffold,
                structure_variant: structureVariant,
                voice_bundle_path: voiceBundlePath,
                models: models,
                strategies: strategies
            }),
        });
    }

    /**
     * Create hybrid from multiple variants.
     */
    async createSceneHybrid(
        sceneId: string,
        variantIds: string[],
        sources: Array<{ section: string; variant_id: string }>,
        instructions?: string
    ): Promise<{
        hybrid: {
            id: string;
            content: string;
            word_count: number;
            source_variants: string[];
        };
    }> {
        return this._request('/director/scene/create-hybrid', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneId,
                variant_ids: variantIds,
                sources: sources,
                instructions: instructions
            }),
        });
    }

    /**
     * Fast single-model scene generation (no tournament).
     */
    async quickGenerateScene(
        sceneId: string,
        scaffold: string,
        strategy: string,
        targetWordCount: number,
        voiceBundlePath?: string
    ): Promise<{
        content: string;
        word_count: number;
        model_used: string;
        strategy: string;
    }> {
        return this._request('/director/scene/quick-generate', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneId,
                scaffold: scaffold,
                strategy: strategy,
                target_word_count: targetWordCount,
                voice_bundle_path: voiceBundlePath
            }),
        });
    }

    // --- Scene Analysis ---

    /**
     * Full 5-category analysis with scoring.
     */
    async analyzeScene(
        sceneId: string,
        sceneContent: string,
        povCharacter: string,
        phase: string,
        voiceBundlePath?: string,
        storyBible?: any
    ): Promise<{
        scene_id: string;
        total_score: number;
        scores: {
            voice_authenticity: number;
            character_consistency: number;
            metaphor_discipline: number;
            anti_pattern_compliance: number;
            phase_appropriateness: number;
        };
        details: {
            voice: { tests: Array<{ name: string; score: number; feedback: string }> };
            character: { issues: string[]; strengths: string[] };
            metaphors: { domains: Record<string, number>; violations: string[] };
            anti_patterns: { found: Array<{ pattern: string; line: number; text: string }> };
            phase: { current: string; appropriateness: string };
        };
        recommendation: string;
        enhancement_mode: 'action_prompt' | 'six_pass' | 'rewrite';
    }> {
        return this._request('/director/scene/analyze', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneId,
                scene_content: sceneContent,
                pov_character: povCharacter,
                phase: phase,
                voice_bundle_path: voiceBundlePath,
                story_bible: storyBible
            }),
        });
    }

    /**
     * Compare multiple scene variants.
     */
    async compareSceneVariants(
        variants: Record<string, string>,
        povCharacter: string,
        phase: string,
        voiceBundlePath?: string
    ): Promise<{
        rankings: Array<{
            model: string;
            total_score: number;
            scores: Record<string, number>;
        }>;
        recommendation: string;
        hybrid_suggestion?: {
            opening: string;
            middle: string;
            closing: string;
        };
    }> {
        return this._request('/director/scene/compare', {
            method: 'POST',
            body: JSON.stringify({
                variants: variants,
                pov_character: povCharacter,
                phase: phase,
                voice_bundle_path: voiceBundlePath
            }),
        });
    }

    /**
     * Quick anti-pattern detection (real-time feedback).
     */
    async detectPatterns(sceneContent: string): Promise<{
        patterns_found: Array<{
            type: string;
            severity: 'error' | 'warning' | 'info';
            line: number;
            text: string;
            suggestion: string;
        }>;
        total_violations: number;
        zero_tolerance_violations: number;
    }> {
        return this._request('/director/scene/detect-patterns', {
            method: 'POST',
            body: JSON.stringify({ scene_content: sceneContent }),
        });
    }

    /**
     * Quick metaphor domain analysis.
     */
    async analyzeMetaphors(
        sceneContent: string,
        voiceBundlePath?: string
    ): Promise<{
        domains: Record<string, { count: number; percentage: number; examples: string[] }>;
        saturation_warnings: string[];
        suggestions: string[];
    }> {
        return this._request('/director/scene/analyze-metaphors', {
            method: 'POST',
            body: JSON.stringify({
                scene_content: sceneContent,
                voice_bundle_path: voiceBundlePath
            }),
        });
    }

    // --- Scene Enhancement ---

    /**
     * Auto-select enhancement mode based on score.
     */
    async enhanceScene(
        sceneId: string,
        sceneContent: string,
        phase: string,
        voiceBundlePath?: string,
        storyBible?: any,
        forceMode?: 'action_prompt' | 'six_pass'
    ): Promise<{
        mode_used: 'action_prompt' | 'six_pass';
        enhanced_content: string;
        original_score: number;
        enhanced_score: number;
        changes_made: number;
        passes_completed?: number;
    }> {
        return this._request('/director/scene/enhance', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneId,
                scene_content: sceneContent,
                phase: phase,
                voice_bundle_path: voiceBundlePath,
                story_bible: storyBible,
                force_mode: forceMode
            }),
        });
    }

    /**
     * Generate surgical fixes (preview only).
     */
    async generateActionPrompt(
        sceneId: string,
        sceneContent: string,
        phase: string,
        voiceBundlePath?: string
    ): Promise<{
        fixes: Array<{
            id: string;
            category: string;
            line: number;
            old_text: string;
            new_text: string;
            reason: string;
            priority: 'critical' | 'high' | 'medium';
        }>;
        current_score: number;
        estimated_post_fix_score: number;
    }> {
        return this._request('/director/scene/action-prompt', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneId,
                scene_content: sceneContent,
                phase: phase,
                voice_bundle_path: voiceBundlePath
            }),
        });
    }

    /**
     * Apply selected OLD → NEW replacements.
     */
    async applyFixes(
        sceneId: string,
        sceneContent: string,
        fixes: Array<{ old_text: string; new_text: string }>
    ): Promise<{
        updated_content: string;
        fixes_applied: number;
        new_score: number;
    }> {
        return this._request('/director/scene/apply-fixes', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneId,
                scene_content: sceneContent,
                fixes: fixes
            }),
        });
    }

    /**
     * Run full 6-pass enhancement ritual.
     */
    async runSixPassEnhancement(
        sceneId: string,
        sceneContent: string,
        phase: string,
        voiceBundlePath?: string,
        storyBible?: any
    ): Promise<{
        passes: Array<{
            pass_number: number;
            pass_name: string;
            changes_made: number;
            content_after: string;
        }>;
        final_content: string;
        original_score: number;
        final_score: number;
        total_changes: number;
    }> {
        return this._request('/director/scene/six-pass', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneId,
                scene_content: sceneContent,
                phase: phase,
                voice_bundle_path: voiceBundlePath,
                story_bible: storyBible
            }),
        });
    }

    // ==========================================
    // Graph Health Service (Phase 3D)
    // ==========================================

    /**
     * Run a comprehensive health check on manuscript structure.
     * @param projectId Project identifier
     * @param scope Check scope: 'chapter', 'act', or 'manuscript'
     * @param chapterId Chapter ID (required for chapter scope)
     * @param actNumber Act number (required for act scope)
     */
    async runHealthCheck(
        projectId: string,
        scope: 'chapter' | 'act' | 'manuscript',
        chapterId?: string,
        actNumber?: number
    ): Promise<{
        status: string;
        report: HealthReport;
        markdown: string;
    }> {
        return this._request('/health/check', {
            method: 'POST',
            body: JSON.stringify({
                project_id: projectId,
                scope: scope,
                chapter_id: chapterId,
                act_number: actNumber
            }),
        });
    }

    /**
     * Retrieve a stored health report by ID.
     * @param reportId Report identifier
     */
    async getHealthReport(reportId: string): Promise<{
        status: string;
        report: HealthReport;
    }> {
        return this._request(`/health/report/${reportId}`);
    }

    /**
     * List all health reports with pagination.
     * @param projectId Project identifier
     * @param limit Max results (default 20)
     * @param offset Skip results (default 0)
     * @param scope Optional filter by scope
     */
    async listHealthReports(
        projectId: string,
        limit: number = 20,
        offset: number = 0,
        scope?: 'chapter' | 'act' | 'manuscript'
    ): Promise<{
        reports: HealthReportSummary[];
        total: number;
        limit: number;
        offset: number;
    }> {
        const params = new URLSearchParams({
            project_id: projectId,
            limit: limit.toString(),
            offset: offset.toString()
        });
        if (scope) params.append('scope', scope);
        return this._request(`/health/reports?${params.toString()}`);
    }

    /**
     * Get historical trend data for a health metric.
     * @param metric Metric name: 'overall_health', 'pacing_plateaus', 'beat_deviations', 'flaw_challenges', 'theme_resonance'
     * @param projectId Project identifier
     * @param startDate Optional start date (ISO format)
     * @param endDate Optional end date (ISO format)
     */
    async getHealthTrends(
        metric: string,
        projectId: string,
        startDate?: string,
        endDate?: string
    ): Promise<{
        metric: string;
        data: TrendDataPoint[];
        start_date: string | null;
        end_date: string | null;
    }> {
        const params = new URLSearchParams({ project_id: projectId });
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        return this._request(`/health/trends/${metric}?${params.toString()}`);
    }

    /**
     * Export a health report as JSON or markdown.
     * @param reportId Report identifier
     * @param format Export format: 'json' or 'markdown'
     */
    async exportHealthReport(
        reportId: string,
        format: 'json' | 'markdown' = 'json'
    ): Promise<{
        format: string;
        content: any;
    }> {
        return this._request(`/health/export/${reportId}?format=${format}`);
    }

    /**
     * Set a manual theme resonance score override.
     * @param projectId Project identifier
     * @param beatId Beat identifier
     * @param themeId Theme identifier
     * @param manualScore Manual score (0-10)
     * @param reason Writer's explanation
     */
    async setThemeOverride(
        projectId: string,
        beatId: string,
        themeId: string,
        manualScore: number,
        reason: string
    ): Promise<{
        success: boolean;
        beat_id: string;
        theme_id: string;
        manual_score: number;
    }> {
        return this._request('/health/theme/override', {
            method: 'POST',
            body: JSON.stringify({
                project_id: projectId,
                beat_id: beatId,
                theme_id: themeId,
                manual_score: manualScore,
                reason: reason
            }),
        });
    }

    /**
     * Get all manual theme score overrides for a project.
     * @param projectId Project identifier
     */
    async getThemeOverrides(projectId: string): Promise<{
        overrides: ThemeOverride[];
    }> {
        return this._request(`/health/theme/overrides?project_id=${projectId}`);
    }
}

// --- Health Report Interfaces ---
export interface HealthWarning {
    type: string;
    severity: 'error' | 'warning' | 'info';
    message: string;
    recommendation?: string;
    scenes?: string[];
    chapters?: string[];
    characters?: string[];
    data?: Record<string, any>;
}

export interface HealthReport {
    report_id: string;
    project_id: string;
    scope: 'chapter' | 'act' | 'manuscript';
    chapter_id?: string;
    act_number?: number;
    overall_score: number;
    warnings: HealthWarning[];
    timestamp: string;
}

export interface HealthReportSummary {
    report_id: string;
    project_id: string;
    scope: string;
    chapter_id?: string;
    act_number?: number;
    overall_score: number;
    warning_count: number;
    error_count: number;
    timestamp: string;
}

export interface TrendDataPoint {
    chapter_id?: string;
    act_number?: number;
    score?: number;
    timestamp: string;
    [key: string]: any;
}

export interface ThemeOverride {
    beat_id: string;
    theme_id: string;
    manual_score: number | null;
    llm_score: number | null;
    reason: string;
    timestamp: string | null;
}

// Export a singleton instance for easy use across the Svelte app
export const apiClient = new WritersFactoryAPI();
