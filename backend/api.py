import os
import sys
import shutil
import logging
import yaml
import json
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Path Setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- App Imports ---
# Load environment variables from root .env
from dotenv import load_dotenv
load_dotenv()  # Loads from project root

from backend.agents.wizard.setup import generate_project_config
from backend.agents.registry import AgentRegistry
from backend.agents.specialists.scaffold import SmartScaffoldAgent
from backend.agents.orchestrator import SceneTournament, DraftCritic
from backend.graph.graph_service import KnowledgeGraphService
from backend.graph.schema import Base, Node
from backend.graph.ner_extractor import NERExtractor, SPACY_AVAILABLE
from backend.ingestor import GraphIngestor
from backend.services.notebooklm_service import get_notebooklm_client
from backend.services.session_service import SessionService, get_session_service
from backend.services.consolidator_service import ConsolidatorService, get_consolidator_service
from backend.services.story_bible_service import StoryBibleService
from backend.services.settings_service import SettingsService, settings_service

# --- SQLAlchemy Imports ---
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# --- Logging & Constants ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
PROJECT_ROOT = "workspace"
PROJECT_NAME = "student_project"
PROJECT_PATH = os.path.join(PROJECT_ROOT, PROJECT_NAME)
CONFIG_PATH = os.path.join(PROJECT_PATH, "config")
SCENES_PATH = os.path.join(PROJECT_PATH, "scenes")
DB_FILE = os.path.join(PROJECT_PATH, "graph.db")
DB_URL = f"sqlite:///{DB_FILE}"
BASE_TEMPLATE_PATH = "backend/templates/reference_skills"
AGENTS_CONFIG_PATH = "agents.yaml"
NOTEBOOK_CONFIG_PATH = "backend/notebooklm_config.json"

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Writers Factory API",
    description="API for orchestrating the AI writing pipeline.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://127.0.0.1:1420", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Service Initialization (Global Instances) ---
# In a production app, use FastAPI's Depends for better lifecycle management.
agent_registry = AgentRegistry(config_path=AGENTS_CONFIG_PATH)
notebooklm_client = get_notebooklm_client()

# Database session management
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Models ---
class ProjectInitRequest(BaseModel):
    project_name: str
    voice_sample: str
    protagonist_name: str

class TournamentRequest(BaseModel):
    scaffold: str

class SceneSaveRequest(BaseModel):
    scene_id: int
    winning_text: str

class FileUpdateRequest(BaseModel):
    content: str

class NotebookQueryRequest(BaseModel):
    query: str
    notebook_id: str

class CharacterProfileRequest(BaseModel):
    character_name: str
    notebook_id: str

class WorldBuildingRequest(BaseModel):
    aspect: str
    notebook_id: str

class ContextRequest(BaseModel):
    entity_name: str
    entity_type: str
    notebook_id: str

class StoryBibleScaffoldRequest(BaseModel):
    project_title: str
    protagonist_name: str
    pre_filled: dict = None

class SmartScaffoldRequest(BaseModel):
    notebook_id: str
    project_title: str
    protagonist_name: str

class SessionCreateRequest(BaseModel):
    scene_id: str = None

class SessionMessageRequest(BaseModel):
    role: str
    content: str
    scene_id: str = None


# --- Phase 4 Tournament Models ---

class TournamentAgentConfig(BaseModel):
    """Configuration for a tournament agent."""
    agent_id: str
    provider: str
    model: str
    quality_tier: str = "balanced"
    enabled: bool = True


class CreateTournamentRequest(BaseModel):
    """Request to create a new tournament."""
    tournament_type: str  # "structure_variant" or "scene_variant"
    project_id: str
    agents: List[TournamentAgentConfig]
    strategies: Optional[List[str]] = None  # ["action", "character", "dialogue", "brainstorming", "balanced"]
    source_material: str
    source_context: str = ""
    voice_bundle_path: Optional[str] = None
    max_variants_per_agent: int = 5
    parallel_execution: bool = True
    auto_score: bool = True


class RunTournamentRoundRequest(BaseModel):
    """Request to run a tournament round."""
    tournament_id: str
    round_number: int = 1


class SelectWinnerRequest(BaseModel):
    """Request to select tournament winner."""
    tournament_id: str
    winner_variant_id: str


class CreateHybridRequest(BaseModel):
    """Request to create hybrid scene from variants."""
    tournament_id: str
    selected_variant_ids: List[str]
    merge_strategy: str = "paragraph"  # "paragraph" | "section" | "sentence"
    preserve_voice_from: Optional[str] = None
    target_word_count: Optional[int] = None
    maintain_pacing: bool = True
    smooth_transitions: bool = True


# --- API Endpoints ---

@app.get("/agents", summary="List available agents")
def list_agents():
    """Return list of configured agents"""
    agents = agent_registry.list_enabled_agents()
    return {"agents": agents}

@app.get("/manager/status", summary="Check Manager status")
def manager_status():
    """Simple heartbeat for the Manager agent"""
    # Since manager is embedded, if API is up, Manager is 'ready'
    return {"status": "online"}

# --- File Management ---
@app.get("/files/{filepath:path}")
async def read_file(filepath: str):
    """Read a specific file"""
    # Security check: ensure path is within allowed directories or absolute path if permitted
    # For this dev tool, we allow reading project files
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/files/{filepath:path}")
async def save_file(filepath: str, request: FileUpdateRequest):
    """Save content to a file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(request.content)
        return {"status": "success", "message": "File saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Graph Ingestion & Viewing ---
@app.post("/ingest")
async def run_ingestion_legacy():
    """Legacy endpoint - use /graph/ingest instead"""
    return await run_graph_ingestion()

@app.post("/graph/ingest")
async def run_graph_ingestion(max_files: int = None):
    """
    Trigger manual graph ingestion from content folder.
    Uses LOCAL Llama 3.2 via Ollama (zero cost).

    Args:
        max_files: Optional limit on files to process (for quick testing)
    """
    try:
        ingestor = GraphIngestor(max_files=max_files)
        result = await ingestor.run_ingestion()
        return {
            "status": "Ingestion complete",
            "engine": "ollama/llama3.2",
            "nodes_extracted": len(result.get("nodes", [])),
            "edges_extracted": len(result.get("edges", [])),
            "metadata": result.get("metadata", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/graph/ingest/test")
async def run_graph_ingestion_test():
    """
    Quick test: Ingest just 2 files to verify the pipeline works.
    """
    try:
        ingestor = GraphIngestor(max_files=2)
        result = await ingestor.run_ingestion()
        return {
            "status": "Test ingestion complete",
            "engine": "ollama/llama3.2",
            "nodes_extracted": len(result.get("nodes", [])),
            "edges_extracted": len(result.get("edges", [])),
            "files_processed": result.get("metadata", {}).get("files_processed", "unknown"),
            "message": "This was a quick test. Use POST /graph/ingest for full ingestion."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test ingestion failed: {str(e)}")

@app.get("/graph/view")
async def view_knowledge_graph():
    """
    Returns the current state of the knowledge graph.
    """
    graph_path = os.path.join(os.path.dirname(__file__), "knowledge_graph.json")

    if not os.path.exists(graph_path):
        return {
            "status": "empty",
            "message": "No knowledge graph exists yet. Run POST /graph/ingest first.",
            "nodes": [],
            "edges": []
        }

    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
        return {
            "status": "ok",
            "nodes": graph_data.get("nodes", []),
            "edges": graph_data.get("edges", []),
            "metadata": graph_data.get("metadata", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read graph: {str(e)}")

# --- Session Management (The Workbench) ---
@app.post("/session/new", summary="Create a new chat session")
async def create_session(request: SessionCreateRequest = None):
    """
    Create a new persistent chat session.
    Optionally link it to a scene_id for context.
    """
    try:
        with get_session_service() as service:
            scene_id = request.scene_id if request else None
            session_id = service.create_session(scene_id=scene_id)
            return {"session_id": session_id, "scene_id": scene_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/session/{session_id}/message", summary="Log a message to session")
async def log_session_message(session_id: str, request: SessionMessageRequest):
    """
    Log a message (user, assistant, or system) to a session.
    This is called BEFORE sending to the LLM, creating the audit trail.
    """
    if request.role not in ('user', 'assistant', 'system'):
        raise HTTPException(status_code=400, detail="Role must be 'user', 'assistant', or 'system'")

    try:
        with get_session_service() as service:
            event = service.log_event(
                session_id=session_id,
                role=request.role,
                content=request.content,
                scene_id=request.scene_id
            )
            return {
                "status": "logged",
                "event_id": event.id,
                "token_count": event.token_count
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log message: {str(e)}")

@app.get("/session/{session_id}/history", summary="Get session chat history")
async def get_session_history(session_id: str, limit: int = 50):
    """
    Retrieve the chat history for a session.
    Used to restore UI state on page reload.
    """
    try:
        with get_session_service() as service:
            events = service.get_session_history(session_id, limit=limit)
            return {
                "session_id": session_id,
                "events": [e.to_dict() for e in events]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/session/{session_id}/stats", summary="Get session statistics")
async def get_session_stats(session_id: str):
    """
    Get statistics for a session (for compaction decisions).
    """
    try:
        with get_session_service() as service:
            stats = service.get_session_stats(session_id)
            return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/sessions/active", summary="List active sessions")
async def list_active_sessions(limit: int = 20):
    """
    Get recently active sessions.
    """
    try:
        with get_session_service() as service:
            sessions = service.get_active_sessions(limit=limit)
            return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@app.get("/session/{session_id}/uncommitted", summary="Get uncommitted events for Consolidator")
async def get_uncommitted_events(session_id: str):
    """
    Get events that haven't been digested by the Consolidator yet.
    This is used by the Consolidator to find new content to process.
    """
    try:
        with get_session_service() as service:
            events = service.get_uncommitted_events(session_id=session_id)
            return {
                "session_id": session_id,
                "uncommitted_count": len(events),
                "events": [e.to_dict() for e in events]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get uncommitted: {str(e)}")

@app.post("/session/commit", summary="Mark events as digested")
async def commit_session_events(event_ids: List[int]):
    """
    Mark events as committed (digested by the Consolidator).
    Called after successful graph ingestion from session data.
    """
    try:
        with get_session_service() as service:
            count = service.mark_as_committed(event_ids)
            return {"committed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to commit: {str(e)}")

# --- Consolidator (The Liver) ---
@app.post("/graph/consolidate/{session_id}", summary="Digest session into knowledge graph")
async def consolidate_session(session_id: str, dry_run: bool = False):
    """
    Run the Consolidator on a specific session.

    This extracts entities from uncommitted chat events and merges them
    into the knowledge graph using local Llama 3.2.

    Args:
        session_id: The session UUID to consolidate
        dry_run: If True, extract but don't save (for testing)
    """
    try:
        consolidator = get_consolidator_service()
        result = await consolidator.digest_session(session_id, dry_run=dry_run)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consolidation failed: {str(e)}")

@app.post("/graph/consolidate", summary="Digest all uncommitted events")
async def consolidate_all(dry_run: bool = False):
    """
    Run the Consolidator on ALL uncommitted events across all sessions.

    This is useful for batch processing after multiple chat sessions.
    """
    try:
        consolidator = get_consolidator_service()
        result = await consolidator.digest_all_uncommitted(dry_run=dry_run)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consolidation failed: {str(e)}")

@app.get("/graph/conflicts", summary="View detected conflicts")
async def get_graph_conflicts():
    """
    Get any conflicts detected during consolidation.

    Conflicts occur when new information contradicts existing graph data.
    These are flagged for manual review.
    """
    conflicts_path = os.path.join(os.path.dirname(__file__), "graph_conflicts.json")

    if not os.path.exists(conflicts_path):
        return {"conflicts": [], "count": 0}

    try:
        with open(conflicts_path, "r") as f:
            conflicts = json.load(f)
        return {"conflicts": conflicts, "count": len(conflicts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read conflicts: {str(e)}")

# --- Health Dashboard (Combined Status) ---
@app.get("/health/status", summary="Get system health status")
async def get_health_status():
    """
    Combined health endpoint for the dashboard.

    Returns graph stats, conflicts, and uncommitted event counts in one call.
    """
    try:
        # 1. Graph stats from knowledge_graph.json
        graph_path = os.path.join(os.path.dirname(__file__), "knowledge_graph.json")
        graph_stats = {"node_count": 0, "edge_count": 0, "recent_nodes": []}

        if os.path.exists(graph_path):
            with open(graph_path, "r") as f:
                graph_data = json.load(f)
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            graph_stats = {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "recent_nodes": nodes[-5:] if nodes else []  # Last 5 nodes
            }

        # 2. Conflicts from graph_conflicts.json
        conflicts_path = os.path.join(os.path.dirname(__file__), "graph_conflicts.json")
        conflicts = []
        if os.path.exists(conflicts_path):
            with open(conflicts_path, "r") as f:
                conflicts = json.load(f)

        # 3. Uncommitted events count (across all sessions)
        uncommitted_count = 0
        with get_session_service() as service:
            events = service.get_uncommitted_events()
            uncommitted_count = len(events)

        return {
            "graph_stats": graph_stats,
            "conflicts": conflicts[-10:],  # Last 10 conflicts
            "conflict_count": len(conflicts),
            "uncommitted_count": uncommitted_count,
            "timestamp": datetime.now().isoformat() if 'datetime' in dir() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")

# --- NotebookLM Integration ---
@app.get("/notebooklm/status")
async def get_notebooklm_status():
    is_up = await notebooklm_client.is_available()
    return {"status": "ready" if is_up else "offline"}

@app.get("/notebooklm/auth")
async def trigger_auth():
    try:
        await notebooklm_client.setup_auth()
        return {"status": "Auth flow triggered. Check for browser window."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notebooklm/notebooks")
async def list_notebooks():
    try:
        if os.path.exists(NOTEBOOK_CONFIG_PATH):
            with open(NOTEBOOK_CONFIG_PATH, "r") as f:
                data = json.load(f)
                return {"configured": data.get("notebooks", [])}
        return {"configured": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notebooklm/query")
async def query_notebook(req: NotebookQueryRequest):
    try:
        return await notebooklm_client.query_notebook(req.notebook_id, req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notebooklm/character-profile")
async def extract_character_profile(req: CharacterProfileRequest):
    try:
        return await notebooklm_client.extract_character_profile(req.notebook_id, req.character_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notebooklm/world-building")
async def extract_world_building(req: WorldBuildingRequest):
    try:
        return await notebooklm_client.extract_world_building(req.notebook_id, req.aspect)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notebooklm/context")
async def get_context(req: ContextRequest):
    try:
        answer = await notebooklm_client.query_for_context(req.notebook_id, req.entity_name, req.entity_type)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Original Endpoints ---

@app.post("/project/init", summary="Initialize a new student project")
def init_project(request: ProjectInitRequest):
    """
    Runs the Setup Wizard to create a new project configuration.
    """
    try:
        generate_project_config(
            project_name=request.project_name,
            voice_sample=request.voice_sample,
            user_answers={"protagonist_name": request.protagonist_name},
            base_template_path=BASE_TEMPLATE_PATH,
            project_root=PROJECT_ROOT
        )
        return {"message": f"Project '{request.project_name}' initialized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/context/{scene_id}", summary="Get scaffold data for a scene")
def get_scaffold(scene_id: int):
    """
    Generates and returns the ACE scaffold for a given scene ID.
    """
    db = next(get_db())
    graph_service = KnowledgeGraphService(session=db)
    
    # Mock MCP client for scaffold generation
    class MockMCPClient:
        def get_context_for_scene(self, scene_id: int) -> str:
            return "API-retrieved research notes: The character feels remorse."

    scaffold_agent = SmartScaffoldAgent(
        graph_service=graph_service,
        mcp_client=MockMCPClient(),
        template_path="backend/templates/ace_structure.md"
    )
    
    # Ensure the scene node exists for the demo
    if not graph_service.get_node(scene_id):
        graph_service.add_node(Node(id=scene_id, name=f"Scene {scene_id}", node_type="scene"))

    scaffold = scaffold_agent.generate_scaffold(scene_id=scene_id)
    db.close()
    if "Error" in scaffold:
        raise HTTPException(status_code=404, detail=scaffold)
    return {"scaffold": scaffold}

@app.post("/tournament/run", summary="Run a scene drafting tournament")
def run_tournament(request: TournamentRequest):
    """
    Accepts a scaffold, runs a tournament, and returns the scored drafts.
    """
    # Load project-specific strategies
    multiplier_path = os.path.join(CONFIG_PATH, "multiplier.yaml")
    if not os.path.exists(multiplier_path):
        raise HTTPException(status_code=404, detail="Project config not found. Run /project/init first.")
        
    with open(multiplier_path, 'r') as f:
        strategies = yaml.safe_load(f).get('strategies', [])

    tournament_agents = [
        agent['id'] for agent in agent_registry.list_enabled_agents()
        if "tournament" in agent.get('use_cases', [])
    ]
    if not tournament_agents:
        raise HTTPException(status_code=500, detail="No tournament agents configured.")

    tournament = SceneTournament(agent_registry)
    drafts = tournament.run_tournament(request.scaffold, tournament_agents, strategies)
    
    critic = DraftCritic()
    results = critic.evaluate_drafts(drafts)
    
    return results

@app.post("/scene/save", summary="Save a scene and ingest its data")
def save_scene(request: SceneSaveRequest):
    """
    Saves the winning text of a scene and triggers graph ingestion.
    """
    # Save the winning text to a file
    os.makedirs(SCENES_PATH, exist_ok=True)
    scene_file_path = os.path.join(SCENES_PATH, f"Chapter_{request.scene_id}.md")
    with open(scene_file_path, 'w') as f:
        f.write(request.winning_text)
    
    # Trigger graph ingestion
    if not SPACY_AVAILABLE:
        raise HTTPException(status_code=501, detail="spaCy not installed, cannot run ingestion.")

    db = next(get_db())
    graph_service = KnowledgeGraphService(session=db)
    ner_extractor = NERExtractor()
    
    extracted_nodes = ner_extractor.extract_nodes(request.winning_text, scene_id=str(request.scene_id))
    
    ingested_count = 0
    for node in extracted_nodes:
        if not graph_service.find_node_by_name(node.name):
            graph_service.add_node(node)
            ingested_count += 1
            
    db.close()
    return {
        "message": f"Scene saved to {scene_file_path}",
        "ingested_new_nodes": ingested_count
    }

# --- Story Bible System (Phase 2) ---

# Content path for Story Bible service
from pathlib import Path
CONTENT_PATH = Path(os.path.dirname(__file__)).parent / "content"

def get_story_bible_service() -> StoryBibleService:
    """Factory for Story Bible service."""
    return StoryBibleService(CONTENT_PATH)

@app.get("/story-bible/status", summary="Get Story Bible validation status")
async def get_story_bible_status():
    """
    Run Level 2 Health Checks on Story Bible.

    Returns completion status, parsed data, and blocking issues
    that prevent proceeding to Phase 3 (Execution).
    """
    try:
        service = get_story_bible_service()
        report = service.get_validation_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.post("/story-bible/scaffold", summary="Create Story Bible scaffolding")
async def scaffold_story_bible(request: StoryBibleScaffoldRequest):
    """
    Create the complete Story Bible directory structure and template files.

    This is the first step of Phase 2 - creates all required artifacts
    as empty templates ready to be filled in or synthesized from NotebookLM.
    """
    try:
        service = get_story_bible_service()
        result = service.scaffold_story_bible(
            project_title=request.project_title,
            protagonist_name=request.protagonist_name,
            pre_filled=request.pre_filled
        )
        return {
            "status": "success",
            "message": f"Story Bible scaffolding created for '{request.project_title}'",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scaffolding failed: {str(e)}")

@app.get("/story-bible/protagonist", summary="Get parsed protagonist data")
async def get_protagonist_data():
    """
    Parse and return structured protagonist data.

    Extracts Fatal Flaw, The Lie, Arc, and relationships from
    existing character files.
    """
    try:
        service = get_story_bible_service()
        data = service.parse_protagonist()

        if not data.name:
            return {
                "status": "not_found",
                "message": "No protagonist file found. Create one with POST /story-bible/scaffold"
            }

        return {
            "status": "ok",
            "protagonist": {
                "name": data.name,
                "true_character": data.true_character,
                "characterization": data.characterization,
                "fatal_flaw": data.fatal_flaw,
                "the_lie": data.the_lie,
                "arc": {
                    "start": data.arc_start,
                    "midpoint": data.arc_midpoint,
                    "resolution": data.arc_resolution,
                },
                "relationships": data.relationships,
                "contradiction_score": data.contradiction_score,
                "is_valid": data.is_valid,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse failed: {str(e)}")

@app.get("/story-bible/beat-sheet", summary="Get parsed beat sheet data")
async def get_beat_sheet_data():
    """
    Parse and return structured beat sheet data.

    Extracts all 15 beats, current progress, midpoint type,
    and theme statement.
    """
    try:
        service = get_story_bible_service()
        data = service.parse_beat_sheet()

        if not data.title and not data.beats:
            return {
                "status": "not_found",
                "message": "No beat sheet found. Create one with POST /story-bible/scaffold"
            }

        return {
            "status": "ok",
            "beat_sheet": {
                "title": data.title,
                "current_beat": data.current_beat,
                "midpoint_type": data.midpoint_type,
                "theme_stated": data.theme_stated,
                "completion_percentage": data.completion_percentage,
                "is_valid": data.is_valid,
                "beats": [
                    {
                        "number": b.number,
                        "name": b.name,
                        "percentage": b.percentage,
                        "description": b.description[:200] + "..." if len(b.description) > 200 else b.description,
                        "scene_link": b.scene_link,
                        "is_complete": b.is_complete,
                    }
                    for b in data.beats
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse failed: {str(e)}")

@app.post("/story-bible/ensure-structure", summary="Ensure directory structure exists")
async def ensure_story_bible_structure():
    """
    Create the Story Bible directory structure if it doesn't exist.

    Creates: Characters/, Story Bible/Structure/, Story Bible/Themes_and_Philosophy/,
    World Bible/, Story Bible/Research/
    """
    try:
        service = get_story_bible_service()
        result = service.ensure_directory_structure()
        return {
            "status": "success",
            "directories": {k: str(v) for k, v in result['directories'].items()},
            "created": result['created']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create structure: {str(e)}")

@app.get("/story-bible/can-execute", summary="Check if ready for Phase 3")
async def can_execute():
    """
    Simple boolean check: Can we proceed to the Execution Phase?

    Returns True only if all blocking requirements are met:
    - Protagonist has Fatal Flaw
    - Protagonist has The Lie
    - Beat Sheet has all 15 beats
    """
    try:
        service = get_story_bible_service()
        status = service.validate_story_bible()
        return {
            "can_execute": status.phase2_complete,
            "completion_score": status.completion_score,
            "blocking_issues": [] if status.phase2_complete else [
                "Missing Fatal Flaw" if not status.protagonist_has_flaw else None,
                "Missing The Lie" if not status.protagonist_has_lie else None,
                "Beat Sheet incomplete" if not status.beat_sheet_complete else None,
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check failed: {str(e)}")

# --- Smart Scaffold Workflow (AI Scaffolding Agent) ---

@app.post("/story-bible/smart-scaffold", summary="AI-powered Story Bible generation from NotebookLM")
async def run_smart_scaffold(request: SmartScaffoldRequest):
    """
    Run the Smart Scaffold workflow to generate Story Bible from NotebookLM.

    This is the "AI Scaffolding Agent" that:
    1. Queries NotebookLM for protagonist data (Fatal Flaw, The Lie, Arc)
    2. Queries NotebookLM for 15-beat structure
    3. Queries NotebookLM for themes and world rules
    4. Synthesizes responses into Story Bible templates
    5. Validates completeness

    Requires:
    - NotebookLM to be authenticated (run /notebooklm/auth first)
    - A notebook_id with uploaded research materials
    """
    from backend.workflows.smart_scaffold import SmartScaffoldWorkflow

    try:
        # Get services
        nlm_client = get_notebooklm_client()
        story_bible_svc = get_story_bible_service()

        # Create and run workflow
        workflow = SmartScaffoldWorkflow(
            notebooklm_client=nlm_client,
            story_bible_service=story_bible_svc,
        )

        result = await workflow.run(
            notebook_id=request.notebook_id,
            project_title=request.project_title,
            protagonist_name=request.protagonist_name,
        )

        return {
            "status": "success" if result.success else "failed",
            "workflow": result.to_dict(),
            "message": "Story Bible generated from NotebookLM" if result.success else result.error,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart scaffold failed: {str(e)}")

# --- The Foreman (Intelligent Creative Partner) ---

from backend.agents.foreman import Foreman, create_foreman

# Global Foreman instance (stateful)
_foreman_instance: Foreman = None

def get_foreman() -> Foreman:
    """Get or create the Foreman instance."""
    global _foreman_instance
    if _foreman_instance is None:
        _foreman_instance = create_foreman(
            notebooklm_client=notebooklm_client,
            story_bible_service=get_story_bible_service(),
            content_path=CONTENT_PATH,
        )
    return _foreman_instance


class ForemanStartRequest(BaseModel):
    project_title: str
    protagonist_name: str
    notebooks: dict = None  # {notebook_id: role}


class ForemanChatRequest(BaseModel):
    message: str


class ForemanNotebookRequest(BaseModel):
    notebook_id: str
    role: str  # "world", "voice", "craft"


# --- Settings API Models ---
class SettingGetRequest(BaseModel):
    key: str
    project_id: Optional[str] = None


class SettingSetRequest(BaseModel):
    key: str
    value: Any
    project_id: Optional[str] = None
    category: str = "general"


class SettingResetRequest(BaseModel):
    key: str
    project_id: Optional[str] = None


class SettingsCategoryRequest(BaseModel):
    category: str
    project_id: Optional[str] = None


class SettingsImportRequest(BaseModel):
    settings: Dict[str, Any]
    project_id: Optional[str] = None


@app.post("/foreman/start", summary="Start a new project with the Foreman")
async def foreman_start(request: ForemanStartRequest):
    """
    Initialize the Foreman for a new project.

    The Foreman will track the work order (Story Bible templates)
    and guide the writer through completion.
    """
    try:
        foreman = get_foreman()
        result = foreman.start_project(
            project_title=request.project_title,
            protagonist_name=request.protagonist_name,
            notebooks=request.notebooks,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start project: {str(e)}")


@app.post("/foreman/chat", summary="Chat with the Foreman")
async def foreman_chat(request: ForemanChatRequest):
    """
    Send a message to the Foreman and get a response.

    The Foreman will:
    - Consider the work order status
    - Review relevant KB entries
    - Respond with craft-aware guidance
    - Optionally take actions (query NotebookLM, write templates, etc.)
    """
    try:
        foreman = get_foreman()
        result = await foreman.chat(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/foreman/notebook", summary="Register a NotebookLM notebook")
async def foreman_register_notebook(request: ForemanNotebookRequest):
    """
    Register a NotebookLM notebook with the Foreman.

    Roles:
    - "world": World-building, setting, factions
    - "voice": Character voice samples
    - "craft": Narrative technique references
    """
    try:
        foreman = get_foreman()
        result = foreman.register_notebook(request.notebook_id, request.role)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register notebook: {str(e)}")


@app.get("/foreman/status", summary="Get Foreman status")
async def foreman_status():
    """
    Get the current Foreman state.

    Returns work order status, conversation length, KB stats (SQLite-backed).
    """
    try:
        foreman = get_foreman()
        state = foreman.get_state()

        # Get SQLite KB stats if project is active
        kb_stats = None
        if foreman.work_order:
            kb_stats = foreman.get_kb_stats()

        return {
            "active": foreman.work_order is not None,
            "mode": foreman.mode.value,
            "work_order": state.get("work_order"),
            "conversation_length": len(foreman.conversation),
            "kb_entries_pending": len(foreman.kb_entries),
            "kb_stats": kb_stats,  # SQLite-backed stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@app.post("/foreman/flush-kb", summary="Flush KB entries for persistence")
async def foreman_flush_kb():
    """
    Flush in-memory KB cache and get SQLite stats.

    With SQLite persistence, entries are already saved immediately.
    This clears the in-memory cache and returns persistence stats.
    """
    try:
        foreman = get_foreman()
        result = foreman.flush_kb_entries()
        return {
            "status": "flushed",
            **result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to flush KB: {str(e)}")


@app.post("/foreman/reset", summary="Reset the Foreman")
async def foreman_reset():
    """
    Reset the Foreman to initial state.

    Clears the current project, conversation, KB entries (both in-memory and SQLite).
    """
    global _foreman_instance

    # Clear SQLite KB for current project before resetting
    kb_deleted = 0
    if _foreman_instance and _foreman_instance.work_order:
        kb_deleted = _foreman_instance.clear_project_kb()

    _foreman_instance = None
    return {
        "status": "reset",
        "message": "Foreman has been reset",
        "kb_entries_deleted": kb_deleted,
    }


@app.get("/foreman/mode", summary="Get current Foreman mode")
async def foreman_get_mode():
    """
    Get the current Foreman mode and transition eligibility.
    """
    foreman = _get_or_create_foreman()
    if not foreman.work_order:
        return {
            "mode": None,
            "message": "No active project"
        }

    return {
        "mode": foreman.mode.value,
        "work_order_complete": foreman.work_order.is_complete,
        "can_advance_to_voice_calibration": foreman.can_advance_to_voice_calibration(),
        "can_advance_to_director": foreman.can_advance_to_director(),
    }


@app.post("/foreman/mode/voice-calibration", summary="Advance to Voice Calibration mode")
async def foreman_advance_to_voice_calibration():
    """
    Advance from ARCHITECT to VOICE_CALIBRATION mode.

    Requires Story Bible to be complete (all templates marked COMPLETE).
    """
    foreman = _get_or_create_foreman()
    if not foreman.work_order:
        raise HTTPException(status_code=400, detail="No active project")

    result = await foreman._handle_advance_to_voice_calibration({})
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)

    return result


@app.post("/foreman/mode/director", summary="Advance to Director mode")
async def foreman_advance_to_director():
    """
    Advance from VOICE_CALIBRATION to DIRECTOR mode.

    Requires voice calibration to be complete:
    - Tournament has been run
    - Winner has been selected
    - Voice Bundle has been generated
    """
    foreman = _get_or_create_foreman()
    if not foreman.work_order:
        raise HTTPException(status_code=400, detail="No active project")

    result = await foreman._handle_advance_to_director({"confirm": True})
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)

    return result


# =============================================================================
# Metabolism (Phase 3) - KB Consolidation Endpoints
# =============================================================================

@app.post("/metabolism/consolidate-kb", summary="Consolidate Foreman KB to knowledge graph")
async def consolidate_foreman_kb(
    project_id: Optional[str] = None,
    dry_run: bool = False
):
    """
    Promote unpromoted Foreman KB entries to the knowledge graph.

    This is the "Living Brain" loop:
    1. Foreman saves crystallized decisions to foreman_kb (SQLite)
    2. This endpoint reads unpromoted entries and adds them to knowledge_graph.json
    3. Entries are marked as promoted so they won't be processed again

    Args:
        project_id: Optional - consolidate a specific project. If not provided,
                    consolidates all projects with unpromoted entries.
        dry_run: If True, shows what would be done without saving.

    Returns:
        Stats about nodes added, edges created, entries promoted.
    """
    from backend.services.consolidator_service import get_consolidator_service

    try:
        consolidator = get_consolidator_service()

        if project_id:
            result = await consolidator.digest_foreman_kb(project_id, dry_run=dry_run)
        else:
            result = await consolidator.digest_all_foreman_kb(dry_run=dry_run)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KB consolidation failed: {str(e)}")


@app.post("/metabolism/consolidate-kb/{project_id}", summary="Consolidate KB for specific project")
async def consolidate_project_kb(
    project_id: str,
    dry_run: bool = False
):
    """
    Consolidate Foreman KB entries for a specific project.

    Shorthand for POST /metabolism/consolidate-kb?project_id=...
    """
    from backend.services.consolidator_service import get_consolidator_service

    try:
        consolidator = get_consolidator_service()
        result = await consolidator.digest_foreman_kb(project_id, dry_run=dry_run)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KB consolidation failed: {str(e)}")


# =============================================================================
# Voice Calibration (Phase 2B) - Tournament Endpoints
# =============================================================================

@app.get("/voice-calibration/agents", summary="Get available agents for tournament")
async def get_available_agents(use_case: str = "tournament"):
    """
    Get list of agents available for voice calibration tournaments.

    Returns agents with their availability status (enabled, has valid API key).
    Writers can only select agents that are both enabled AND have valid keys.

    Args:
        use_case: Filter by use case (default: "tournament")

    Returns:
        List of agents with availability info
    """
    from backend.services.voice_calibration_service import get_voice_calibration_service

    try:
        service = get_voice_calibration_service()
        all_agents = service.get_available_agents(use_case)
        ready_agents = service.get_ready_agents(use_case)

        return {
            "all_agents": [a.to_dict() for a in all_agents],
            "ready_agents": [a.to_dict() for a in ready_agents],
            "ready_count": len(ready_agents),
            "total_count": len(all_agents),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")


@app.post("/voice-calibration/tournament/start", summary="Start a voice calibration tournament")
async def start_voice_tournament(
    project_id: str,
    test_prompt: str,
    test_context: str,
    agent_ids: List[str],
    variants_per_agent: int = 5,
    voice_description: Optional[str] = None,
):
    """
    Start a voice calibration tournament.

    Multiple agents will each generate multiple variants of the test passage,
    using different creative strategies (Action, Character, Dialogue, Atmospheric, Balanced).

    Args:
        project_id: The project identifier
        test_prompt: The test scene/passage to write (describe what should happen)
        test_context: Context about the scene (setting, characters, mood)
        agent_ids: List of agent IDs to include (use /voice-calibration/agents to see available)
        variants_per_agent: Number of variants per agent (1-5, default 5)
        voice_description: Optional description of desired voice from writer

    Returns:
        Tournament ID and initial status
    """
    from backend.services.voice_calibration_service import get_voice_calibration_service

    try:
        service = get_voice_calibration_service()

        # Validate agent_ids
        ready_agents = service.get_ready_agents()
        ready_ids = {a.id for a in ready_agents}
        invalid_ids = [aid for aid in agent_ids if aid not in ready_ids]
        if invalid_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid or unavailable agents: {invalid_ids}"
            )

        # Clamp variants
        variants_per_agent = max(1, min(5, variants_per_agent))

        result = await service.start_tournament(
            project_id=project_id,
            test_prompt=test_prompt,
            test_context=test_context,
            agent_ids=agent_ids,
            variants_per_agent=variants_per_agent,
            voice_description=voice_description,
        )

        return {
            "tournament_id": result.tournament_id,
            "status": result.status.value,
            "agents": result.selected_agents,
            "expected_variants": len(agent_ids) * variants_per_agent,
            "message": "Tournament started. Poll /voice-calibration/tournament/{id}/status for progress.",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start tournament: {str(e)}")


@app.get("/voice-calibration/tournament/{tournament_id}/status", summary="Get tournament status")
async def get_tournament_status(tournament_id: str):
    """
    Get the current status of a voice calibration tournament.

    Returns:
        Tournament status, variant count, and variants if complete
    """
    from backend.services.voice_calibration_service import get_voice_calibration_service

    try:
        service = get_voice_calibration_service()
        result = service.get_tournament_status(tournament_id)

        if not result:
            raise HTTPException(status_code=404, detail=f"Tournament {tournament_id} not found")

        response = {
            "tournament_id": result.tournament_id,
            "project_id": result.project_id,
            "status": result.status.value,
            "agents": result.selected_agents,
            "variant_count": len(result.variants),
            "created_at": result.created_at,
        }

        if result.status.value in ["awaiting_selection", "complete"]:
            response["variants"] = [v.to_dict() for v in result.variants]

        if result.status.value == "complete":
            response["winner_agent_id"] = result.winner_agent_id
            response["winner_variant_index"] = result.winner_variant_index
            response["completed_at"] = result.completed_at

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@app.get("/voice-calibration/tournament/{tournament_id}/variants", summary="Get tournament variants")
async def get_tournament_variants(
    tournament_id: str,
    agent_id: Optional[str] = None,
):
    """
    Get variants from a tournament, optionally filtered by agent.

    Args:
        tournament_id: The tournament
        agent_id: Optional filter by specific agent

    Returns:
        List of variants with content
    """
    from backend.services.voice_calibration_service import get_voice_calibration_service

    try:
        service = get_voice_calibration_service()
        variants = service.get_tournament_variants(tournament_id, agent_id)

        if not variants:
            result = service.get_tournament_status(tournament_id)
            if not result:
                raise HTTPException(status_code=404, detail=f"Tournament {tournament_id} not found")
            if result.status.value == "running":
                return {"message": "Tournament still running", "variants": []}

        return {
            "tournament_id": tournament_id,
            "variant_count": len(variants),
            "variants": [v.to_dict() for v in variants],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get variants: {str(e)}")


@app.post("/voice-calibration/tournament/{tournament_id}/select", summary="Select winning variant")
async def select_tournament_winner(
    tournament_id: str,
    winner_agent_id: str,
    winner_variant_index: int,
    pov: str = "third_limited",
    tense: str = "past",
    voice_type: str = "character_voice",
    metaphor_domains: List[str] = [],
    anti_patterns: List[str] = [],
    characteristic_phrases: List[str] = [],
    sentence_rhythm: str = "varied",
    vocabulary_level: str = "literary",
    phase_evolution: Dict[str, str] = {},
):
    """
    Select the winning variant and generate Voice Calibration Document.

    Args:
        tournament_id: The tournament
        winner_agent_id: The winning agent's ID
        winner_variant_index: Index of winning variant (0-based within agent's variants)
        pov: Point of view - "first_person", "third_limited", "third_omniscient"
        tense: "past" or "present"
        voice_type: "character_voice" or "author_voice"
        metaphor_domains: List of metaphor domains (e.g., ["gambling", "addiction", "martial_arts"])
        anti_patterns: List of patterns to avoid (e.g., ["similes", "computer_metaphors"])
        characteristic_phrases: Example phrases that capture the voice
        sentence_rhythm: Description of rhythm (e.g., "short punchy", "long flowing", "varied")
        vocabulary_level: "colloquial", "literary", "technical"
        phase_evolution: Dict mapping act/phase to voice description

    Returns:
        Voice Calibration Document
    """
    from backend.services.voice_calibration_service import get_voice_calibration_service

    try:
        service = get_voice_calibration_service()

        voice_config = {
            "pov": pov,
            "tense": tense,
            "voice_type": voice_type,
            "metaphor_domains": metaphor_domains,
            "anti_patterns": anti_patterns,
            "characteristic_phrases": characteristic_phrases,
            "sentence_rhythm": sentence_rhythm,
            "vocabulary_level": vocabulary_level,
            "phase_evolution": phase_evolution,
        }

        voice_doc = await service.select_winner(
            tournament_id=tournament_id,
            winner_agent_id=winner_agent_id,
            winner_variant_index=winner_variant_index,
            voice_config=voice_config,
        )

        return {
            "status": "complete",
            "message": "Voice calibration complete. Document saved to KB.",
            "voice_calibration": voice_doc.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to select winner: {str(e)}")


@app.post("/voice-calibration/generate-bundle/{project_id}", summary="Generate Voice Reference Bundle")
async def generate_voice_bundle(project_id: str):
    """
    Generate Voice Reference Bundle files for Director Mode.

    These markdown files travel with every agent call during scene writing:
    - Voice-Gold-Standard.md - Main voice reference
    - Voice-Anti-Pattern-Sheet.md - Patterns to avoid
    - Phase-Evolution-Guide.md - How voice changes through story

    Args:
        project_id: The project with completed voice calibration

    Returns:
        Paths to generated files
    """
    from backend.services.voice_calibration_service import get_voice_calibration_service
    from pathlib import Path

    try:
        service = get_voice_calibration_service()

        # Output to project-specific directory
        output_dir = Path("projects") / project_id / "voice_references"

        files = await service.generate_voice_bundle(project_id, output_dir)

        return {
            "status": "complete",
            "message": "Voice Reference Bundle generated",
            "files": {k: str(v) for k, v in files.items()},
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate bundle: {str(e)}")


@app.get("/voice-calibration/{project_id}", summary="Get voice calibration for project")
async def get_voice_calibration(project_id: str):
    """
    Get the stored voice calibration document for a project.

    Returns:
        Voice Calibration Document if exists
    """
    from backend.services.foreman_kb_service import get_foreman_kb_service
    import json

    try:
        kb = get_foreman_kb_service()
        voice_json = await kb.get(project_id, "voice_calibration")

        if not voice_json:
            raise HTTPException(
                status_code=404,
                detail=f"No voice calibration found for project {project_id}"
            )

        return {
            "project_id": project_id,
            "voice_calibration": json.loads(voice_json),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voice calibration: {str(e)}")


# =============================================================================
# Scaffold Generator Endpoints (Director Mode - Phase 3B)
# =============================================================================

class BeatInfoRequest(BaseModel):
    """Beat information for scaffold generation."""
    beat_number: int
    beat_name: str
    beat_percentage: str = "50%"
    description: str
    beat_type: Optional[str] = None


class CharacterContextRequest(BaseModel):
    """Character context for scaffold generation."""
    name: str
    role: str  # "protagonist", "antagonist", "supporting"
    fatal_flaw: Optional[str] = None
    the_lie: Optional[str] = None
    arc_state: Optional[str] = None


class DraftSummaryRequest(BaseModel):
    """Request for Stage 1: Draft Summary."""
    project_id: str
    chapter_number: int
    scene_number: int
    beat_info: BeatInfoRequest
    characters: List[CharacterContextRequest]
    scene_description: str
    available_notebooks: Optional[List[Dict[str, str]]] = None


class EnrichmentRequest(BaseModel):
    """Request to fetch enrichment from NotebookLM."""
    notebook_id: str
    query: str


class FullScaffoldRequest(BaseModel):
    """Request for Stage 2: Full Scaffold."""
    project_id: str
    chapter_number: int
    scene_number: int
    title: str
    beat_info: BeatInfoRequest
    characters: List[CharacterContextRequest]
    scene_description: str
    voice_state: str
    phase: str
    target_word_count: str = "1500-2000"
    theme: Optional[str] = None
    enrichment_data: Optional[List[Dict[str, str]]] = None


@app.post("/director/scaffold/draft-summary", summary="Generate draft summary (Stage 1)")
async def generate_draft_summary(request: DraftSummaryRequest):
    """
    Generate a draft summary with enrichment suggestions.

    This is the checkpoint where the writer decides whether to
    add NotebookLM enrichment before generating the full scaffold.

    Returns:
        - Narrative summary of what happens
        - Available context (what we know)
        - Enrichment suggestions (optional queries)
    """
    from backend.services.scaffold_generator_service import (
        get_scaffold_generator_service,
        BeatInfo,
        CharacterContext,
    )

    try:
        service = get_scaffold_generator_service()

        # Convert request models to service models
        beat_info = BeatInfo(
            beat_number=request.beat_info.beat_number,
            beat_name=request.beat_info.beat_name,
            beat_percentage=request.beat_info.beat_percentage,
            description=request.beat_info.description,
            beat_type=request.beat_info.beat_type,
        )

        characters = [
            CharacterContext(
                name=c.name,
                role=c.role,
                fatal_flaw=c.fatal_flaw,
                the_lie=c.the_lie,
                arc_state=c.arc_state,
            )
            for c in request.characters
        ]

        result = await service.generate_draft_summary(
            project_id=request.project_id,
            chapter_number=request.chapter_number,
            scene_number=request.scene_number,
            beat_info=beat_info,
            characters=characters,
            scene_description=request.scene_description,
            available_notebooks=request.available_notebooks,
        )

        return result.to_dict()

    except Exception as e:
        logging.error(f"Draft summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Draft summary failed: {str(e)}")


@app.post("/director/scaffold/enrich", summary="Fetch enrichment from NotebookLM")
async def fetch_scaffold_enrichment(request: EnrichmentRequest):
    """
    Fetch enrichment data from a NotebookLM notebook.

    Call this between Stage 1 and Stage 2 if the writer
    wants to add context from their research notebooks.
    """
    from backend.services.scaffold_generator_service import get_scaffold_generator_service
    from backend.services.notebooklm_service import get_notebooklm_client

    try:
        notebooklm = get_notebooklm_client()
        service = get_scaffold_generator_service(notebooklm_client=notebooklm)

        result = await service.fetch_enrichment(
            notebook_id=request.notebook_id,
            query=request.query,
        )

        return {
            "notebook_id": result.notebook_id,
            "query": result.query,
            "answer": result.answer,
            "retrieved_at": result.retrieved_at,
        }

    except Exception as e:
        logging.error(f"Enrichment fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@app.post("/director/scaffold/generate", summary="Generate full scaffold (Stage 2)")
async def generate_full_scaffold(request: FullScaffoldRequest):
    """
    Generate the full scaffold document.

    Call this after Stage 1 (draft summary), optionally with
    enrichment data from NotebookLM queries.

    Returns:
        - Complete scaffold document
        - Markdown version for display/export
    """
    from backend.services.scaffold_generator_service import (
        get_scaffold_generator_service,
        BeatInfo,
        CharacterContext,
        EnrichmentData,
    )

    try:
        service = get_scaffold_generator_service()

        # Convert request models
        beat_info = BeatInfo(
            beat_number=request.beat_info.beat_number,
            beat_name=request.beat_info.beat_name,
            beat_percentage=request.beat_info.beat_percentage,
            description=request.beat_info.description,
            beat_type=request.beat_info.beat_type,
        )

        characters = [
            CharacterContext(
                name=c.name,
                role=c.role,
                fatal_flaw=c.fatal_flaw,
                the_lie=c.the_lie,
                arc_state=c.arc_state,
            )
            for c in request.characters
        ]

        # Convert enrichment data if provided
        enrichment_data = None
        if request.enrichment_data:
            enrichment_data = [
                EnrichmentData(
                    notebook_id=e.get("notebook_id", ""),
                    query=e.get("query", ""),
                    answer=e.get("answer", ""),
                )
                for e in request.enrichment_data
            ]

        result = await service.generate_full_scaffold(
            project_id=request.project_id,
            chapter_number=request.chapter_number,
            scene_number=request.scene_number,
            title=request.title,
            beat_info=beat_info,
            characters=characters,
            scene_description=request.scene_description,
            voice_state=request.voice_state,
            phase=request.phase,
            target_word_count=request.target_word_count,
            enrichment_data=enrichment_data,
            theme=request.theme,
        )

        return {
            "scaffold": result.to_dict(),
            "markdown": result.to_markdown(),
        }

    except Exception as e:
        logging.error(f"Scaffold generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scaffold generation failed: {str(e)}")


# =============================================================================
# Scene Writer Endpoints (Director Mode - Phase 3B)
# =============================================================================

class StructureVariantRequest(BaseModel):
    """Request for structure variant generation."""
    scene_id: str
    beat_description: str
    scaffold: Optional[Dict[str, Any]] = None
    pov_character: str = "protagonist"
    target_word_count: str = "1500-2000"


class SceneVariantRequest(BaseModel):
    """Request for scene variant generation."""
    scene_id: str
    scaffold: Dict[str, Any]
    structure_variant: Dict[str, Any]
    voice_bundle_path: Optional[str] = None
    story_bible: Optional[Dict[str, Any]] = None
    models: Optional[List[Dict[str, str]]] = None
    strategies: Optional[List[str]] = None
    target_word_count: int = 1500


class HybridSceneRequest(BaseModel):
    """Request to create a hybrid scene."""
    scene_id: str
    variant_ids: List[str]
    sources: List[Dict[str, str]]  # [{"variant_id": "A", "section": "opening"}, ...]
    instructions: str


class QuickSceneRequest(BaseModel):
    """Request for quick single-model scene generation."""
    scene_id: str
    scaffold: Dict[str, Any]
    voice_bundle_path: Optional[str] = None
    strategy: str = "balanced"
    target_word_count: int = 1500


@app.post("/director/scene/structure-variants", summary="Generate structure variants (Stage 1)")
async def generate_structure_variants(request: StructureVariantRequest):
    """
    Generate 5 different structural approaches to a scene.

    This is the creative exploration phase - explore different
    chapter layouts BEFORE writing prose.

    Returns:
        - 5 structure variants (A-E) with different approaches
        - Recommendation for which seems strongest
    """
    from backend.services.scene_writer_service import get_scene_writer_service
    from backend.services.scaffold_generator_service import Scaffold

    try:
        service = get_scene_writer_service()

        # Convert scaffold dict if provided
        scaffold = None
        if request.scaffold:
            scaffold = Scaffold(**request.scaffold)

        result = await service.generate_structure_variants(
            scene_id=request.scene_id,
            beat_description=request.beat_description,
            scaffold=scaffold,
            pov_character=request.pov_character,
            target_word_count=request.target_word_count,
        )

        return result.to_dict()

    except Exception as e:
        logging.error(f"Structure variant generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Structure variants failed: {str(e)}")


@app.post("/director/scene/generate-variants", summary="Generate scene variants (Stage 2)")
async def generate_scene_variants(request: SceneVariantRequest):
    """
    Generate scene variants using multiple models and strategies.

    Each model generates one variant per strategy, all scored by SceneAnalyzerService.

    Returns:
        - All variants with scores and grades
        - Rankings (sorted by score)
        - Winner (highest scoring variant)
    """
    from backend.services.scene_writer_service import (
        get_scene_writer_service,
        WritingStrategy,
    )
    from backend.services.scaffold_generator_service import Scaffold
    from backend.services.scene_analyzer_service import (
        VoiceBundleContext,
        StoryBibleContext,
    )
    from pathlib import Path

    try:
        service = get_scene_writer_service()

        # Convert scaffold
        scaffold = Scaffold(**request.scaffold)

        # Convert structure variant
        from backend.services.scene_writer_service import StructureVariant
        structure = StructureVariant(**request.structure_variant)

        # Load voice bundle if path provided
        voice_bundle = None
        if request.voice_bundle_path:
            voice_bundle = VoiceBundleContext.from_directory(Path(request.voice_bundle_path))

        # Build story bible context
        story_bible = None
        if request.story_bible:
            story_bible = StoryBibleContext(
                protagonist_name=request.story_bible.get("protagonist_name", "protagonist"),
                fatal_flaw=request.story_bible.get("fatal_flaw", ""),
                the_lie=request.story_bible.get("the_lie", ""),
                theme=request.story_bible.get("theme", ""),
                current_phase=request.story_bible.get("phase", "act2"),
            )

        # Convert strategies
        strategies = None
        if request.strategies:
            strategies = [WritingStrategy(s) for s in request.strategies]

        result = await service.generate_scene_variants(
            scene_id=request.scene_id,
            scaffold=scaffold,
            structure_variant=structure,
            voice_bundle=voice_bundle,
            story_bible=story_bible,
            models=request.models,
            strategies=strategies,
            target_word_count=request.target_word_count,
        )

        return result.to_dict()

    except Exception as e:
        logging.error(f"Scene variant generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scene variants failed: {str(e)}")


@app.post("/director/scene/create-hybrid", summary="Create hybrid scene")
async def create_hybrid_scene(request: HybridSceneRequest):
    """
    Create a hybrid scene by combining the best elements from multiple variants.

    After reviewing the generated variants, the writer can select
    specific sections from different variants to combine.

    Returns:
        - New hybrid scene variant
        - Automatically scored
    """
    from backend.services.scene_writer_service import (
        get_scene_writer_service,
        HybridRequest,
        SceneVariant,
    )

    try:
        service = get_scene_writer_service()

        # Note: In production, variants would be retrieved from storage
        # For now, this endpoint expects the frontend to track variants
        hybrid_request = HybridRequest(
            scene_id=request.scene_id,
            sources=request.sources,
            instructions=request.instructions,
        )

        # This would need variants passed in or retrieved from session storage
        # For MVP, return a placeholder indicating the hybrid creation flow
        return {
            "status": "hybrid_creation_requested",
            "scene_id": request.scene_id,
            "sources": request.sources,
            "instructions": request.instructions,
            "note": "Full hybrid creation requires variant storage - coming in next iteration",
        }

    except Exception as e:
        logging.error(f"Hybrid creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hybrid creation failed: {str(e)}")


@app.post("/director/scene/quick-generate", summary="Quick single-model generation")
async def quick_generate_scene(request: QuickSceneRequest):
    """
    Quick scene generation with a single model (no tournament).

    Useful for drafts or when speed matters more than variety.

    Returns:
        - Single scene variant
        - Automatically scored
    """
    from backend.services.scene_writer_service import (
        get_scene_writer_service,
        WritingStrategy,
    )
    from backend.services.scaffold_generator_service import Scaffold
    from backend.services.scene_analyzer_service import VoiceBundleContext
    from pathlib import Path

    try:
        service = get_scene_writer_service()

        # Convert scaffold
        scaffold = Scaffold(**request.scaffold)

        # Load voice bundle
        voice_bundle = None
        if request.voice_bundle_path:
            voice_bundle = VoiceBundleContext.from_directory(Path(request.voice_bundle_path))

        # Convert strategy
        strategy = WritingStrategy(request.strategy)

        variant = await service.generate_single_scene(
            scene_id=request.scene_id,
            scaffold=scaffold,
            voice_bundle=voice_bundle,
            strategy=strategy,
            target_word_count=request.target_word_count,
        )

        # Score the variant
        if voice_bundle:
            analysis = await service.analyzer_service.analyze_scene(
                scene_id=variant.variant_id,
                scene_content=variant.content,
                voice_bundle=voice_bundle,
                phase=scaffold.phase,
            )
            variant.score = analysis.total_score
            variant.grade = analysis.grade
            variant.analysis = analysis

        return variant.to_dict()

    except Exception as e:
        logging.error(f"Quick scene generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quick generation failed: {str(e)}")


# =============================================================================
# Scene Analyzer Endpoints (Director Mode - Phase 3B)
# =============================================================================

class SceneAnalyzeRequest(BaseModel):
    """Request to analyze a scene draft."""
    scene_id: str
    scene_content: str
    pov_character: str = "protagonist"
    phase: str = "act2"
    voice_bundle_path: Optional[str] = None
    story_bible: Optional[Dict[str, Any]] = None


class SceneCompareRequest(BaseModel):
    """Request to compare multiple scene variants."""
    variants: Dict[str, str]  # model_name -> scene_content
    pov_character: str = "protagonist"
    phase: str = "act2"
    voice_bundle_path: Optional[str] = None


@app.post("/director/scene/analyze", summary="Analyze a scene draft")
async def analyze_scene(request: SceneAnalyzeRequest):
    """
    Analyze a scene draft against the 5-category scoring rubric.

    Returns:
        - Total score (0-100)
        - Grade (A to F)
        - Category breakdown with subcategories
        - Detected violations
        - Metaphor analysis
        - Enhancement recommendation
    """
    from backend.services.scene_analyzer_service import (
        get_scene_analyzer_service,
        VoiceBundleContext,
        StoryBibleContext,
    )
    from pathlib import Path

    try:
        service = get_scene_analyzer_service()

        # Load voice bundle if path provided
        voice_bundle = None
        if request.voice_bundle_path:
            voice_bundle = VoiceBundleContext.from_directory(Path(request.voice_bundle_path))

        # Build story bible context if provided
        story_bible = None
        if request.story_bible:
            story_bible = StoryBibleContext(
                protagonist_name=request.story_bible.get("protagonist_name", "protagonist"),
                fatal_flaw=request.story_bible.get("fatal_flaw", ""),
                the_lie=request.story_bible.get("the_lie", ""),
                theme=request.story_bible.get("theme", ""),
                current_phase=request.phase,
                character_capabilities=request.story_bible.get("capabilities", []),
                relationships=request.story_bible.get("relationships", {}),
            )

        result = await service.analyze_scene(
            scene_id=request.scene_id,
            scene_content=request.scene_content,
            voice_bundle=voice_bundle,
            story_bible=story_bible,
            pov_character=request.pov_character,
            phase=request.phase,
        )

        return result.to_dict()

    except Exception as e:
        logging.error(f"Scene analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scene analysis failed: {str(e)}")


@app.post("/director/scene/compare", summary="Compare multiple scene variants")
async def compare_scene_variants(request: SceneCompareRequest):
    """
    Analyze and rank multiple scene variants.

    Returns:
        - Winner (model with highest score)
        - Rankings with scores and grades
        - Individual analysis for each variant
    """
    from backend.services.scene_analyzer_service import (
        get_scene_analyzer_service,
        VoiceBundleContext,
    )
    from pathlib import Path

    try:
        service = get_scene_analyzer_service()

        # Load voice bundle if path provided
        voice_bundle = None
        if request.voice_bundle_path:
            voice_bundle = VoiceBundleContext.from_directory(Path(request.voice_bundle_path))

        # Analyze each variant
        results = {}
        for model_name, content in request.variants.items():
            result = await service.analyze_scene(
                scene_id=f"variant-{model_name}",
                scene_content=content,
                voice_bundle=voice_bundle,
                pov_character=request.pov_character,
                phase=request.phase,
            )
            results[model_name] = result

        # Rank by total score
        ranked = sorted(
            results.items(),
            key=lambda x: x[1].total_score,
            reverse=True
        )

        return {
            "winner": ranked[0][0] if ranked else None,
            "rankings": [
                {
                    "rank": i + 1,
                    "model": model,
                    "score": result.total_score,
                    "grade": result.grade,
                    "enhancement_needed": result.enhancement_needed,
                    "recommended_mode": result.recommended_mode,
                }
                for i, (model, result) in enumerate(ranked)
            ],
            "details": {
                model: result.to_dict()
                for model, result in results.items()
            },
        }

    except Exception as e:
        logging.error(f"Scene comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scene comparison failed: {str(e)}")


@app.post("/director/scene/detect-patterns", summary="Detect anti-patterns only")
async def detect_anti_patterns(scene_content: str):
    """
    Quick endpoint to detect anti-patterns without full analysis.

    Useful for real-time feedback during writing.
    """
    from backend.services.scene_analyzer_service import get_scene_analyzer_service

    try:
        service = get_scene_analyzer_service()
        violations = service._detect_anti_patterns(scene_content)

        return {
            "violation_count": len(violations),
            "zero_tolerance_count": sum(1 for v in violations if v.pattern_type == "zero_tolerance"),
            "formulaic_count": sum(1 for v in violations if v.pattern_type == "formulaic"),
            "violations": [v.to_dict() for v in violations],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern detection failed: {str(e)}")


@app.post("/director/scene/analyze-metaphors", summary="Analyze metaphor usage only")
async def analyze_metaphors(scene_content: str, voice_bundle_path: Optional[str] = None):
    """
    Quick endpoint to analyze metaphor domain usage.

    Returns domain distribution and saturation warnings.
    """
    from backend.services.scene_analyzer_service import (
        get_scene_analyzer_service,
        VoiceBundleContext,
    )
    from pathlib import Path

    try:
        service = get_scene_analyzer_service()

        voice_bundle = None
        if voice_bundle_path:
            voice_bundle = VoiceBundleContext.from_directory(Path(voice_bundle_path))

        analysis = service._analyze_metaphors(scene_content, voice_bundle)

        return analysis.to_dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metaphor analysis failed: {str(e)}")


# =============================================================================
# Scene Enhancement Endpoints (Director Mode - Phase 3B)
# =============================================================================

class SceneEnhanceRequest(BaseModel):
    """Request to enhance a scene."""
    scene_id: str
    scene_content: str
    pov_character: str = "protagonist"
    phase: str = "act2"
    voice_bundle_path: Optional[str] = None
    story_bible: Optional[Dict[str, Any]] = None
    force_mode: Optional[str] = None  # "action_prompt", "six_pass", "rewrite"


class ActionPromptRequest(BaseModel):
    """Request to generate action prompt only (without applying)."""
    scene_id: str
    scene_content: str
    pov_character: str = "protagonist"
    phase: str = "act2"
    voice_bundle_path: Optional[str] = None


class ApplyFixesRequest(BaseModel):
    """Request to apply surgical fixes from action prompt."""
    scene_id: str
    scene_content: str
    fixes: List[Dict[str, Any]]  # List of {old_text, new_text, ...}


@app.post("/director/scene/enhance", summary="Enhance a scene (auto-selects mode)")
async def enhance_scene(request: SceneEnhanceRequest):
    """
    Enhance a scene based on its score.

    Automatically selects enhancement mode:
    - Score 85+: Action Prompt (surgical fixes)
    - Score 70-84: 6-Pass Enhancement (full ritual)
    - Score <70: Returns rewrite recommendation

    Returns:
        - Enhanced content
        - Original and final scores
        - Mode used and details (fixes or passes)
    """
    from backend.services.scene_enhancement_service import (
        get_scene_enhancement_service,
        EnhancementMode,
    )
    from backend.services.scene_analyzer_service import (
        get_scene_analyzer_service,
        VoiceBundleContext,
        StoryBibleContext,
    )
    from pathlib import Path

    try:
        enhancement_service = get_scene_enhancement_service()
        analyzer_service = get_scene_analyzer_service()

        # Load voice bundle if path provided
        voice_bundle = None
        if request.voice_bundle_path:
            voice_bundle = VoiceBundleContext.from_directory(Path(request.voice_bundle_path))

        # Build story bible context if provided
        story_bible = None
        if request.story_bible:
            story_bible = StoryBibleContext(
                protagonist_name=request.story_bible.get("protagonist_name", "protagonist"),
                fatal_flaw=request.story_bible.get("fatal_flaw", ""),
                the_lie=request.story_bible.get("the_lie", ""),
                theme=request.story_bible.get("theme", ""),
                current_phase=request.phase,
                character_capabilities=request.story_bible.get("capabilities", []),
                relationships=request.story_bible.get("relationships", {}),
            )

        # First, analyze the scene to get current score
        analysis = await analyzer_service.analyze_scene(
            scene_id=request.scene_id,
            scene_content=request.scene_content,
            voice_bundle=voice_bundle,
            story_bible=story_bible,
            pov_character=request.pov_character,
            phase=request.phase,
        )

        # Determine forced mode if specified
        force_mode = None
        if request.force_mode:
            force_mode = EnhancementMode(request.force_mode)

        # Enhance the scene
        result = await enhancement_service.enhance_scene(
            scene_id=request.scene_id,
            scene_content=request.scene_content,
            analysis=analysis,
            voice_bundle=voice_bundle,
            story_bible=story_bible,
            force_mode=force_mode,
        )

        return {
            "status": "enhanced" if result.mode != EnhancementMode.REWRITE else "rewrite_needed",
            "result": result.to_dict(),
            "analysis_before": analysis.to_dict(),
        }

    except Exception as e:
        logging.error(f"Scene enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scene enhancement failed: {str(e)}")


@app.post("/director/scene/action-prompt", summary="Generate action prompt only")
async def generate_action_prompt(request: ActionPromptRequest):
    """
    Generate an action prompt with surgical fixes WITHOUT applying them.

    Use this to preview fixes before applying, or to manually edit
    the suggested fixes before application.

    Returns:
        - Action prompt document with OLD → NEW fixes
        - Preservation notes
        - Expected score improvement
    """
    from backend.services.scene_enhancement_service import get_scene_enhancement_service
    from backend.services.scene_analyzer_service import (
        get_scene_analyzer_service,
        VoiceBundleContext,
    )
    from pathlib import Path

    try:
        enhancement_service = get_scene_enhancement_service()
        analyzer_service = get_scene_analyzer_service()

        # Load voice bundle if path provided
        voice_bundle = None
        if request.voice_bundle_path:
            voice_bundle = VoiceBundleContext.from_directory(Path(request.voice_bundle_path))

        # Analyze the scene
        analysis = await analyzer_service.analyze_scene(
            scene_id=request.scene_id,
            scene_content=request.scene_content,
            voice_bundle=voice_bundle,
            pov_character=request.pov_character,
            phase=request.phase,
        )

        # Generate action prompt
        action_prompt = await enhancement_service._generate_action_prompt(
            scene_id=request.scene_id,
            scene_content=request.scene_content,
            analysis=analysis,
            voice_bundle=voice_bundle,
        )

        return {
            "action_prompt": action_prompt.to_dict(),
            "markdown": action_prompt.to_markdown(),
            "analysis": analysis.to_dict(),
        }

    except Exception as e:
        logging.error(f"Action prompt generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Action prompt failed: {str(e)}")


@app.post("/director/scene/apply-fixes", summary="Apply surgical fixes from action prompt")
async def apply_surgical_fixes(request: ApplyFixesRequest):
    """
    Apply surgical fixes to a scene.

    Use this after generating/editing an action prompt to apply
    the OLD → NEW replacements.

    Returns:
        - Enhanced content
        - List of applied and skipped fixes
    """
    try:
        enhanced_content = request.scene_content
        fixes_applied = []

        for fix in request.fixes:
            old_text = fix.get("old_text", "")
            new_text = fix.get("new_text", "")
            fix_number = fix.get("fix_number", 0)
            description = fix.get("description", "")

            if old_text and old_text in enhanced_content:
                enhanced_content = enhanced_content.replace(old_text, new_text, 1)
                fixes_applied.append({
                    "fix_number": fix_number,
                    "description": description,
                    "status": "applied",
                })
            else:
                fixes_applied.append({
                    "fix_number": fix_number,
                    "description": description,
                    "status": "not_found",
                    "old_text_preview": old_text[:50] + "..." if len(old_text) > 50 else old_text,
                })

        applied_count = sum(1 for f in fixes_applied if f["status"] == "applied")

        return {
            "scene_id": request.scene_id,
            "enhanced_content": enhanced_content,
            "fixes_applied": fixes_applied,
            "applied_count": applied_count,
            "total_fixes": len(request.fixes),
        }

    except Exception as e:
        logging.error(f"Fix application failed: {e}")
        raise HTTPException(status_code=500, detail=f"Fix application failed: {str(e)}")


@app.post("/director/scene/six-pass", summary="Run 6-pass enhancement")
async def run_six_pass_enhancement(request: SceneEnhanceRequest):
    """
    Force 6-pass enhancement regardless of score.

    Use this when you want the full enhancement ritual
    even if the score would normally trigger action prompt mode.

    Returns:
        - Enhanced content
        - All 6 pass results with changes
        - Final score
    """
    from backend.services.scene_enhancement_service import (
        get_scene_enhancement_service,
        EnhancementMode,
    )
    from backend.services.scene_analyzer_service import (
        get_scene_analyzer_service,
        VoiceBundleContext,
        StoryBibleContext,
    )
    from pathlib import Path

    try:
        enhancement_service = get_scene_enhancement_service()
        analyzer_service = get_scene_analyzer_service()

        # Load voice bundle if path provided
        voice_bundle = None
        if request.voice_bundle_path:
            voice_bundle = VoiceBundleContext.from_directory(Path(request.voice_bundle_path))

        # Build story bible context if provided
        story_bible = None
        if request.story_bible:
            story_bible = StoryBibleContext(
                protagonist_name=request.story_bible.get("protagonist_name", "protagonist"),
                fatal_flaw=request.story_bible.get("fatal_flaw", ""),
                the_lie=request.story_bible.get("the_lie", ""),
                theme=request.story_bible.get("theme", ""),
                current_phase=request.phase,
            )

        # Analyze the scene
        analysis = await analyzer_service.analyze_scene(
            scene_id=request.scene_id,
            scene_content=request.scene_content,
            voice_bundle=voice_bundle,
            story_bible=story_bible,
            pov_character=request.pov_character,
            phase=request.phase,
        )

        # Force 6-pass mode
        result = await enhancement_service.enhance_scene(
            scene_id=request.scene_id,
            scene_content=request.scene_content,
            analysis=analysis,
            voice_bundle=voice_bundle,
            story_bible=story_bible,
            force_mode=EnhancementMode.SIX_PASS,
        )

        return {
            "status": "enhanced",
            "result": result.to_dict(),
            "passes": [p.to_dict() for p in result.passes_completed],
            "score_improvement": (result.final_score or 0) - result.original_score,
        }

    except Exception as e:
        logging.error(f"6-pass enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=f"6-pass enhancement failed: {str(e)}")


# ============================================================================
# SETTINGS API
# ============================================================================

@app.get("/settings/{key}", summary="Get a setting value")
async def get_setting(key: str, project_id: Optional[str] = None):
    """
    Get a setting value using 3-tier resolution.

    Resolution order:
    1. Project-specific override (if project_id provided)
    2. Global user setting
    3. Default value

    Examples:
        GET /settings/scoring.voice_authenticity_weight
        GET /settings/scoring.voice_authenticity_weight?project_id=proj_123
    """
    try:
        value = settings_service.get(key, project_id)
        return {
            "key": key,
            "value": value,
            "project_id": project_id,
        }
    except Exception as e:
        logging.error(f"Failed to get setting {key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get setting: {str(e)}")


@app.post("/settings", summary="Set a setting value")
async def set_setting(request: SettingSetRequest):
    """
    Set a setting value.

    If project_id is provided, sets project-specific override.
    Otherwise, sets global setting.

    Examples:
        POST /settings
        {
            "key": "scoring.voice_authenticity_weight",
            "value": 40,
            "project_id": "proj_123"
        }
    """
    try:
        success = settings_service.set(
            key=request.key,
            value=request.value,
            project_id=request.project_id,
            category=request.category
        )

        if not success:
            raise HTTPException(status_code=400, detail="Setting validation failed")

        return {
            "status": "success",
            "key": request.key,
            "value": request.value,
            "project_id": request.project_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to set setting {request.key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set setting: {str(e)}")


@app.delete("/settings/{key}", summary="Reset a setting to default")
async def reset_setting(key: str, project_id: Optional[str] = None):
    """
    Reset a setting to its default value.

    If project_id is provided, removes the project-specific override.
    If project_id is None, removes the global setting.

    Examples:
        DELETE /settings/scoring.voice_authenticity_weight
        DELETE /settings/scoring.voice_authenticity_weight?project_id=proj_123
    """
    try:
        success = settings_service.reset(key, project_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset setting")

        return {
            "status": "success",
            "key": key,
            "project_id": project_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to reset setting {key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset setting: {str(e)}")


@app.get("/settings/category/{category}", summary="Get all settings in a category")
async def get_settings_category(category: str, project_id: Optional[str] = None):
    """
    Get all settings for a category.

    Categories: scoring, anti_patterns, enhancement, tournament, foreman, context, health_checks, orchestrator, tournament_consensus

    Examples:
        GET /settings/category/scoring
        GET /settings/category/scoring?project_id=proj_123
    """
    try:
        settings = settings_service.get_category(category, project_id)
        return {
            "category": category,
            "settings": settings,
            "project_id": project_id,
        }
    except Exception as e:
        logging.error(f"Failed to get category {category}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get category: {str(e)}")


@app.get("/settings/project/{project_id}/overrides", summary="Get all project overrides")
async def get_project_overrides(project_id: str):
    """
    Get all project-specific setting overrides.

    Examples:
        GET /settings/project/proj_123/overrides
    """
    try:
        overrides = settings_service.get_all_project_overrides(project_id)
        return {
            "project_id": project_id,
            "overrides": overrides,
        }
    except Exception as e:
        logging.error(f"Failed to get project overrides for {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get project overrides: {str(e)}")


@app.get("/settings/export", summary="Export settings as YAML-ready dictionary")
async def export_settings(project_id: Optional[str] = None):
    """
    Export settings to a dictionary suitable for YAML export.

    If project_id is provided, exports project-specific settings.
    Otherwise, exports global settings.

    Examples:
        GET /settings/export
        GET /settings/export?project_id=proj_123
    """
    try:
        settings_dict = settings_service.export_settings(project_id)
        return settings_dict
    except Exception as e:
        logging.error(f"Failed to export settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export settings: {str(e)}")


@app.post("/settings/import", summary="Import settings from dictionary")
async def import_settings(request: SettingsImportRequest):
    """
    Import settings from a dictionary (typically from YAML).

    If project_id is provided, imports as project-specific settings.
    Otherwise, imports as global settings.

    Examples:
        POST /settings/import
        {
            "settings": {
                "scoring": {"voice_authenticity_weight": 40, ...},
                "enhancement": {...}
            },
            "project_id": "proj_123"
        }
    """
    try:
        success = settings_service.import_settings(request.settings, request.project_id)

        if not success:
            raise HTTPException(status_code=400, detail="Settings import failed")

        return {
            "status": "success",
            "project_id": request.project_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to import settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import settings: {str(e)}")


@app.get("/settings/defaults", summary="Get all default values")
async def get_defaults():
    """
    Get all default setting values.

    Useful for understanding the baseline configuration.
    """
    try:
        defaults = settings_service.defaults.get_flat_dict()
        return {
            "defaults": defaults,
        }
    except Exception as e:
        logging.error(f"Failed to get defaults: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get defaults: {str(e)}")


# =============================================================================
# Model Orchestrator API (Phase 3E)
# =============================================================================

@app.get("/orchestrator/capabilities", summary="Get model capabilities registry")
async def get_model_capabilities():
    """
    Get full model capabilities registry with costs, strengths, and quality scores.

    Returns detailed information about all available models for intelligent selection.

    Example:
        GET /orchestrator/capabilities
    """
    try:
        from backend.services.model_capabilities import MODEL_REGISTRY

        models = [
            {
                "model_id": m.model_id,
                "provider": m.provider,
                "display_name": m.display_name,
                "strengths": [s.value for s in m.strengths],
                "quality_score": m.quality_score,
                "speed": m.speed,
                "cost_per_1m_input": m.cost_per_1m_input,
                "cost_per_1m_output": m.cost_per_1m_output,
                "requires_api_key": m.requires_api_key,
                "local_only": m.local_only,
            }
            for m in MODEL_REGISTRY
        ]

        return {"models": models}
    except Exception as e:
        logging.error(f"Failed to get model capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model capabilities: {str(e)}")


@app.post("/orchestrator/estimate-cost", summary="Estimate monthly cost for quality tier")
async def estimate_monthly_cost(request: Dict[str, Any]):
    """
    Estimate monthly cost for a quality tier based on typical usage.

    Request body:
        {
            "quality_tier": "balanced",
            "estimated_usage": {
                "health_check_review": 50,  // 50 calls/month
                "theme_analysis": 30,
                "coordinator": 200
            }
        }

    Example:
        POST /orchestrator/estimate-cost
    """
    try:
        from backend.services.model_orchestrator import orchestrator

        quality_tier = request.get("quality_tier", "balanced")
        usage = request.get("estimated_usage", {})

        cost_estimate = orchestrator.estimate_monthly_cost(quality_tier, usage)
        return cost_estimate
    except Exception as e:
        logging.error(f"Failed to estimate cost: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to estimate cost: {str(e)}")


@app.get("/orchestrator/recommendations/{task_type}", summary="Get model recommendations for task")
async def get_model_recommendations(task_type: str):
    """
    Get recommended models for a task across all quality tiers.

    Args:
        task_type: Task type (e.g., "health_check_review", "theme_analysis")

    Returns:
        {
            "task_type": "health_check_review",
            "recommendations": {
                "budget": "mistral",
                "balanced": "deepseek-chat",
                "premium": "claude-3-5-sonnet-20241022"
            }
        }

    Example:
        GET /orchestrator/recommendations/health_check_review
    """
    try:
        from backend.services.model_orchestrator import orchestrator

        recommendations = orchestrator.get_model_recommendations(task_type)
        return {
            "task_type": task_type,
            "recommendations": recommendations
        }
    except Exception as e:
        logging.error(f"Failed to get recommendations for {task_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@app.get("/orchestrator/current-spend", summary="Get current month spending")
async def get_current_spend():
    """
    Get current month's AI spending and budget status.

    Returns:
        {
            "current_month": "2025-11",
            "spend": 0.47,
            "budget": 2.00,
            "budget_remaining": 1.53
        }

    Example:
        GET /orchestrator/current-spend
    """
    try:
        orchestrator_settings = settings_service.get_category("orchestrator")

        budget = orchestrator_settings.get("monthly_budget")
        spend = orchestrator_settings.get("current_month_spend", 0.0)

        return {
            "current_month": orchestrator_settings.get("current_month"),
            "spend": spend,
            "budget": budget,
            "budget_remaining": (budget - spend) if budget is not None else None
        }
    except Exception as e:
        logging.error(f"Failed to get current spend: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get current spend: {str(e)}")


# =============================================================================
# Graph Health Check API (Phase 3D)
# =============================================================================

class HealthCheckRequest(BaseModel):
    """Request to run a health check."""
    project_id: str
    scope: str  # "chapter", "act", "manuscript"
    chapter_id: Optional[str] = None
    act_number: Optional[int] = None


class ThemeOverrideRequest(BaseModel):
    """Request to manually override a theme resonance score."""
    project_id: str
    beat_id: str
    theme_id: str
    manual_score: float
    reason: str


@app.post("/health/check", summary="Run health check on chapter/act/manuscript")
async def run_health_check(request: HealthCheckRequest):
    """
    Run a comprehensive health check on manuscript structure.

    Scope options:
    - "chapter": Run checks on a specific chapter (requires chapter_id)
    - "act": Run checks on an entire act (requires act_number)
    - "manuscript": Run checks on the full manuscript

    Returns:
        - Health report with overall score (0-100)
        - Warnings categorized by severity (error, warning, info)
        - Recommendations for fixes
        - Stored report_id for later retrieval

    Health Checks:
    - Pacing Plateau Detection: Detects flat tension across consecutive chapters
    - Beat Progress Validation: Ensures 15-beat structure compliance
    - Timeline Consistency: LLM-powered semantic analysis of timeline conflicts
    - Fatal Flaw Challenge Monitoring: Tracks protagonist's flaw testing frequency
    - Cast Function Verification: Ensures supporting characters appear regularly
    - Symbolic Layering: Tracks symbol recurrence and evolution
    - Theme Resonance: Hybrid LLM + manual override for theme scoring at beats
    """
    from backend.services.graph_health_service import get_graph_health_service

    try:
        service = get_graph_health_service(request.project_id)

        # Route to appropriate check based on scope
        if request.scope == "chapter":
            if not request.chapter_id:
                raise HTTPException(
                    status_code=400,
                    detail="chapter_id required for chapter scope"
                )
            report = await service.run_chapter_health_check(request.chapter_id)

        elif request.scope == "act":
            if not request.act_number:
                raise HTTPException(
                    status_code=400,
                    detail="act_number required for act scope"
                )
            report = await service.run_act_health_check(request.act_number)

        elif request.scope == "manuscript":
            report = await service.run_full_manuscript_check()

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scope: {request.scope}. Must be 'chapter', 'act', or 'manuscript'"
            )

        return {
            "status": "complete",
            "report": report.to_dict(),
            "markdown": report.to_markdown(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/health/report/{report_id}", summary="Retrieve a stored health report")
async def get_health_report(report_id: str):
    """
    Retrieve a previously stored health report.

    Returns:
        - Full health report with warnings and recommendations
        - Markdown formatted version for display
    """
    from backend.services.graph_health_service import get_graph_health_service
    from backend.graph.schema import HealthReportHistory
    from sqlalchemy.orm import Session

    try:
        # Query database for report
        db: Session = next(get_db())
        report_row = db.query(HealthReportHistory).filter(
            HealthReportHistory.report_id == report_id
        ).first()

        if not report_row:
            raise HTTPException(
                status_code=404,
                detail=f"Report {report_id} not found"
            )

        return {
            "status": "found",
            "report": report_row.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to retrieve report {report_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")


@app.post("/health/export", summary="Export health report as markdown or JSON")
async def export_health_report(report_id: str, format: str = "markdown"):
    """
    Export a health report in the specified format.

    Formats:
    - "markdown": Human-readable markdown with sections
    - "json": Machine-readable JSON

    Returns:
        - Exported content as string
        - Content-Type header set appropriately
    """
    from backend.services.graph_health_service import get_graph_health_service
    from backend.graph.schema import HealthReportHistory
    from sqlalchemy.orm import Session

    try:
        if format not in ["markdown", "json"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {format}. Must be 'markdown' or 'json'"
            )

        # Query database for report
        db: Session = next(get_db())
        report_row = db.query(HealthReportHistory).filter(
            HealthReportHistory.report_id == report_id
        ).first()

        if not report_row:
            raise HTTPException(
                status_code=404,
                detail=f"Report {report_id} not found"
            )

        if format == "json":
            return {
                "format": "json",
                "content": report_row.to_dict(),
            }
        else:
            # Reconstruct HealthReport from stored data
            from backend.services.graph_health_service import HealthReport, HealthWarning
            from dataclasses import asdict

            warnings_data = report_row.warnings or []
            warnings = [HealthWarning(**w) for w in warnings_data]

            report = HealthReport(
                report_id=report_row.report_id,
                project_id=report_row.project_id,
                scope=report_row.scope,
                chapter_id=report_row.chapter_id,
                act_number=report_row.act_number,
                overall_score=report_row.overall_score,
                warnings=warnings,
                timestamp=report_row.timestamp.isoformat() if report_row.timestamp else None,
            )

            markdown_content = report.to_markdown()

            return {
                "format": "markdown",
                "content": markdown_content,
            }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to export report {report_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")


@app.get("/health/trends/{metric}", summary="Get historical trend data for a metric")
async def get_health_trends(
    metric: str,
    project_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Get historical trend data for longitudinal analysis.

    Metrics:
    - "overall_score": Overall health score over time
    - "pacing_issues": Count of pacing warnings over time
    - "beat_deviations": Beat structure deviation over time
    - "flaw_challenge_gaps": Fatal Flaw challenge gap frequency
    - "timeline_conflicts": Timeline consistency violations over time

    Date format: ISO 8601 (e.g., "2025-01-01T00:00:00")

    Returns:
        - Time series data with timestamps and values
        - Trend direction (improving, declining, stable)
        - Comparison to baseline
    """
    from backend.services.graph_health_service import get_graph_health_service
    from datetime import datetime

    try:
        service = get_graph_health_service(project_id)

        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        trend_data = service.get_trend_data(metric, start_dt, end_dt)

        if not trend_data:
            return {
                "metric": metric,
                "project_id": project_id,
                "data": [],
                "message": "No historical data available for this metric",
            }

        return {
            "metric": metric,
            "project_id": project_id,
            "data": trend_data,
            "count": len(trend_data),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Failed to get trends for {metric}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")


@app.get("/health/reports", summary="List all health reports with pagination")
async def list_health_reports(
    project_id: str,
    limit: int = 20,
    offset: int = 0,
):
    """
    List all health reports for a project with pagination.

    Returns:
        - List of reports with summary info (id, timestamp, score, warning count)
        - Total count for pagination
        - Reports ordered by timestamp (newest first)
    """
    from backend.graph.schema import HealthReportHistory
    from sqlalchemy.orm import Session
    from sqlalchemy import func

    try:
        db: Session = next(get_db())

        # Get total count
        total = db.query(func.count(HealthReportHistory.id)).filter(
            HealthReportHistory.project_id == project_id
        ).scalar()

        # Get paginated results
        reports = db.query(HealthReportHistory).filter(
            HealthReportHistory.project_id == project_id
        ).order_by(HealthReportHistory.timestamp.desc()).offset(offset).limit(limit).all()

        reports_list = []
        for report in reports:
            warning_count = len(report.warnings) if report.warnings else 0
            reports_list.append({
                "report_id": report.report_id,
                "timestamp": report.timestamp.isoformat() if report.timestamp else None,
                "scope": report.scope,
                "chapter_id": report.chapter_id,
                "act_number": report.act_number,
                "overall_score": report.overall_score,
                "warning_count": warning_count,
                "overall_health": (
                    "excellent" if report.overall_score >= 90 else
                    "good" if report.overall_score >= 80 else
                    "fair" if report.overall_score >= 70 else
                    "poor"
                )
            })

        return {
            "reports": reports_list,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        logging.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@app.get("/health/export/{report_id}", summary="Export health report as JSON or markdown")
async def export_health_report_get(
    report_id: str,
    format: str = "json",
):
    """
    Export a health report in the specified format (Phase 3D API).

    Formats:
    - "json": Full report object as JSON
    - "markdown": Formatted markdown report ready for reading

    Returns:
        - Export content in requested format
        - Filename suggestion for downloads
    """
    from backend.graph.schema import HealthReportHistory
    from sqlalchemy.orm import Session

    try:
        if format not in ["markdown", "json"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {format}. Must be 'markdown' or 'json'"
            )

        # Query database for report
        db: Session = next(get_db())
        report_row = db.query(HealthReportHistory).filter(
            HealthReportHistory.report_id == report_id
        ).first()

        if not report_row:
            raise HTTPException(
                status_code=404,
                detail=f"Report {report_id} not found"
            )

        if format == "json":
            return {
                "format": "json",
                "filename": f"health_report_{report_id}.json",
                "content": report_row.to_dict(),
            }
        else:
            # Reconstruct HealthReport from stored data for markdown generation
            from backend.services.graph_health_service import HealthReport, HealthWarning

            warnings_data = report_row.warnings or []
            warnings = [HealthWarning(**w) for w in warnings_data]

            report = HealthReport(
                report_id=report_row.report_id,
                project_id=report_row.project_id,
                scope=report_row.scope,
                chapter_id=report_row.chapter_id,
                act_number=report_row.act_number,
                overall_score=report_row.overall_score,
                warnings=warnings,
                timestamp=report_row.timestamp.isoformat() if report_row.timestamp else None,
            )

            markdown_content = report.to_markdown()

            return {
                "format": "markdown",
                "filename": f"health_report_{report_id}.md",
                "content": markdown_content,
            }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to export report {report_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")


@app.post("/health/theme/override", summary="Manually override LLM theme score")
async def set_theme_override(request: ThemeOverrideRequest):
    """
    Manually override an LLM-generated theme resonance score.

    Strategic Decision 2: Hybrid LLM + Manual Override
    - LLM auto-scores theme resonance at critical beats
    - Writers can override scores when LLM misses subtle intent
    - Future health checks respect manual overrides

    Args:
        project_id: The project
        beat_id: The beat where theme resonates (e.g., "beat_7")
        theme_id: The theme being scored (e.g., "redemption")
        manual_score: Writer's score (0-10 scale)
        reason: Explanation for override

    Returns:
        - Confirmation of override
        - Previous LLM score for comparison
    """
    from backend.services.graph_health_service import get_graph_health_service

    try:
        service = get_graph_health_service(request.project_id)

        # Validate score range
        if not 0 <= request.manual_score <= 10:
            raise HTTPException(
                status_code=400,
                detail="manual_score must be between 0 and 10"
            )

        service.set_theme_override(
            beat_id=request.beat_id,
            theme_id=request.theme_id,
            manual_score=request.manual_score,
            reason=request.reason,
        )

        return {
            "status": "override_set",
            "project_id": request.project_id,
            "beat_id": request.beat_id,
            "theme_id": request.theme_id,
            "manual_score": request.manual_score,
            "message": "Theme score override saved. Future health checks will use this value.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to set theme override: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set override: {str(e)}")


@app.get("/health/theme/overrides", summary="Get all theme overrides for a project")
async def get_theme_overrides(project_id: str):
    """
    Get all manual theme score overrides for a project.

    Returns:
        - List of all overrides with beat, theme, scores, and reasons
        - Comparison between LLM and manual scores
    """
    from backend.services.graph_health_service import get_graph_health_service

    try:
        service = get_graph_health_service(project_id)
        overrides = service.get_all_overrides()

        return {
            "project_id": project_id,
            "overrides": overrides,
            "count": len(overrides),
        }

    except Exception as e:
        logging.error(f"Failed to get theme overrides: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get overrides: {str(e)}")


# =============================================================================
# Phase 4: Multi-Model Tournament Endpoints
# =============================================================================

@app.post("/tournament/structure/create", summary="Create structure variant tournament")
async def create_structure_tournament(request: CreateTournamentRequest):
    """
    Create a new structure variant tournament (STEP 2 automation).

    Generates 15 parallel variants (3 models × 5 strategies) for structural
    approaches to a scene or chapter.

    Returns:
        - Tournament ID for tracking
        - Configuration summary
    """
    from backend.services.tournament_service import get_tournament_service
    from backend.models.tournament import (
        TournamentConfig,
        TournamentType,
        AgentConfig,
        VariantStrategy,
    )

    try:
        service = get_tournament_service()

        # Build agent configs
        agents = [
            AgentConfig(
                agent_id=a.agent_id,
                provider=a.provider,
                model=a.model,
                quality_tier=a.quality_tier,
                enabled=a.enabled,
            )
            for a in request.agents
        ]

        # Parse strategies
        strategies = None
        if request.strategies:
            strategies = [VariantStrategy(s) for s in request.strategies]

        config = TournamentConfig(
            tournament_type=TournamentType.STRUCTURE_VARIANT,
            project_id=request.project_id,
            agents=agents,
            strategies=strategies or list(VariantStrategy),
            source_material=request.source_material,
            source_context=request.source_context,
            voice_bundle_path=request.voice_bundle_path,
            max_variants_per_agent=request.max_variants_per_agent,
            parallel_execution=request.parallel_execution,
            auto_score=request.auto_score,
        )

        tournament = service.create_tournament(config)

        return {
            "status": "created",
            "tournament_id": tournament.id,
            "tournament_type": tournament.tournament_type.value,
            "config": config.to_dict(),
            "expected_variants": len(agents) * len(config.strategies),
        }

    except Exception as e:
        logging.error(f"Failed to create structure tournament: {e}")
        raise HTTPException(status_code=500, detail=f"Tournament creation failed: {str(e)}")


@app.post("/tournament/scene/create", summary="Create scene variant tournament")
async def create_scene_tournament(request: CreateTournamentRequest):
    """
    Create a new scene variant tournament (STEP 3 automation).

    Generates 15-25 parallel scene variants across multiple models and
    strategies for comparison and selection.

    Returns:
        - Tournament ID for tracking
        - Configuration summary
    """
    from backend.services.tournament_service import get_tournament_service
    from backend.models.tournament import (
        TournamentConfig,
        TournamentType,
        AgentConfig,
        VariantStrategy,
    )

    try:
        service = get_tournament_service()

        # Build agent configs
        agents = [
            AgentConfig(
                agent_id=a.agent_id,
                provider=a.provider,
                model=a.model,
                quality_tier=a.quality_tier,
                enabled=a.enabled,
            )
            for a in request.agents
        ]

        # Parse strategies
        strategies = None
        if request.strategies:
            strategies = [VariantStrategy(s) for s in request.strategies]

        config = TournamentConfig(
            tournament_type=TournamentType.SCENE_VARIANT,
            project_id=request.project_id,
            agents=agents,
            strategies=strategies or list(VariantStrategy),
            source_material=request.source_material,
            source_context=request.source_context,
            voice_bundle_path=request.voice_bundle_path,
            max_variants_per_agent=request.max_variants_per_agent,
            parallel_execution=request.parallel_execution,
            auto_score=request.auto_score,
        )

        tournament = service.create_tournament(config)

        return {
            "status": "created",
            "tournament_id": tournament.id,
            "tournament_type": tournament.tournament_type.value,
            "config": config.to_dict(),
            "expected_variants": len(agents) * len(config.strategies),
        }

    except Exception as e:
        logging.error(f"Failed to create scene tournament: {e}")
        raise HTTPException(status_code=500, detail=f"Tournament creation failed: {str(e)}")


@app.post("/tournament/{tournament_id}/run", summary="Run tournament round")
async def run_tournament_round(tournament_id: str, request: RunTournamentRoundRequest):
    """
    Run a tournament round - generate and score all variants.

    Executes parallel variant generation across all configured agents
    and strategies, then scores each variant.

    Returns:
        - Round results with all variants
        - Scores and rankings
        - Consensus analysis
    """
    from backend.services.tournament_service import get_tournament_service

    try:
        service = get_tournament_service()

        round_result = await service.run_round(
            tournament_id=tournament_id,
            round_number=request.round_number,
        )

        # Get full results
        results = service.get_tournament_results(tournament_id)

        return {
            "status": "round_complete",
            "tournament_id": tournament_id,
            "round_number": round_result.round_number,
            "variant_count": len(round_result.variants),
            "consensus_score": round_result.consensus_score,
            **results,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Tournament round failed: {e}")
        raise HTTPException(status_code=500, detail=f"Tournament round failed: {str(e)}")


@app.get("/tournament/{tournament_id}/results", summary="Get tournament results")
async def get_tournament_results(tournament_id: str):
    """
    Get complete tournament results including rankings and consensus.

    Returns:
        - Tournament details
        - All variants with scores
        - Ranked results by score
        - Consensus report
    """
    from backend.services.tournament_service import get_tournament_service

    try:
        service = get_tournament_service()
        results = service.get_tournament_results(tournament_id)

        if "error" in results:
            raise HTTPException(status_code=404, detail=results["error"])

        return results

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get tournament results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@app.get("/tournament/{tournament_id}/variants", summary="Get tournament variants")
async def get_tournament_variants(
    tournament_id: str,
    agent_id: Optional[str] = None,
    strategy: Optional[str] = None,
):
    """
    Get variants from a tournament with optional filters.

    Args:
        tournament_id: Tournament ID
        agent_id: Filter by agent (optional)
        strategy: Filter by strategy (optional)

    Returns:
        - List of variants matching filters
    """
    from backend.services.tournament_service import get_tournament_service

    try:
        service = get_tournament_service()
        tournament = service.get_tournament(tournament_id)

        if not tournament:
            raise HTTPException(status_code=404, detail=f"Tournament {tournament_id} not found")

        variants = tournament.all_variants

        # Apply filters
        if agent_id:
            variants = [v for v in variants if v.agent_id == agent_id]
        if strategy:
            variants = [v for v in variants if v.strategy.value == strategy]

        return {
            "tournament_id": tournament_id,
            "variant_count": len(variants),
            "variants": [v.to_dict() for v in variants],
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get variants: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get variants: {str(e)}")


@app.get("/tournament/{tournament_id}/consensus", summary="Get consensus analysis")
async def get_tournament_consensus(tournament_id: str):
    """
    Get consensus analysis for tournament variants.

    Analyzes where variants agree (high confidence) and diverge
    (areas needing human review).

    Returns:
        - Overall consensus score
        - High-agreement areas
        - Divergent areas needing review
        - Per-variant alignment scores
        - Recommendation
    """
    from backend.services.tournament_service import get_tournament_service

    try:
        service = get_tournament_service()
        tournament = service.get_tournament(tournament_id)

        if not tournament:
            raise HTTPException(status_code=404, detail=f"Tournament {tournament_id} not found")

        consensus = service.detect_consensus(tournament.all_variants)

        return {
            "tournament_id": tournament_id,
            "consensus": consensus.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get consensus: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get consensus: {str(e)}")


@app.post("/tournament/{tournament_id}/select-winner", summary="Select tournament winner")
async def select_tournament_winner(tournament_id: str, request: SelectWinnerRequest):
    """
    Select the winning variant for a tournament.

    Marks the tournament as complete with the selected winner.

    Returns:
        - Updated tournament status
        - Winner details
    """
    from backend.services.tournament_service import get_tournament_service

    try:
        service = get_tournament_service()

        tournament = service.select_winner(
            tournament_id=tournament_id,
            winner_variant_id=request.winner_variant_id,
        )

        winner = tournament.get_variant_by_id(request.winner_variant_id)

        return {
            "status": "winner_selected",
            "tournament_id": tournament_id,
            "winner_variant_id": request.winner_variant_id,
            "winner_score": winner.scores.total_score if winner and winner.scores else None,
            "winner_grade": winner.scores.grade if winner and winner.scores else None,
            "tournament_status": tournament.status.value,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Failed to select winner: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to select winner: {str(e)}")


@app.post("/tournament/{tournament_id}/hybrid", summary="Create hybrid from variants")
async def create_tournament_hybrid(tournament_id: str, request: CreateHybridRequest):
    """
    Create a hybrid scene by merging selected variants.

    Uses intelligent paragraph-level merging to combine the best
    elements from multiple variants.

    Returns:
        - Hybrid scene content
        - Source variants used
    """
    from backend.services.tournament_service import get_tournament_service
    from backend.models.tournament import HybridSceneConfig

    try:
        service = get_tournament_service()

        config = HybridSceneConfig(
            tournament_id=tournament_id,
            selected_variant_ids=request.selected_variant_ids,
            merge_strategy=request.merge_strategy,
            preserve_voice_from=request.preserve_voice_from,
            target_word_count=request.target_word_count,
            maintain_pacing=request.maintain_pacing,
            smooth_transitions=request.smooth_transitions,
        )

        hybrid_content = await service.create_hybrid(config)

        return {
            "status": "hybrid_created",
            "tournament_id": tournament_id,
            "hybrid_content": hybrid_content,
            "word_count": len(hybrid_content.split()),
            "source_variants": request.selected_variant_ids,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Hybrid creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hybrid creation failed: {str(e)}")


@app.get("/tournaments", summary="List tournaments")
async def list_tournaments(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
):
    """
    List all tournaments with optional filters.

    Args:
        project_id: Filter by project (optional)
        status: Filter by status (optional): pending, running, scoring, awaiting_selection, complete, failed

    Returns:
        - List of tournaments matching filters
    """
    from backend.services.tournament_service import get_tournament_service
    from backend.models.tournament import TournamentStatus

    try:
        service = get_tournament_service()

        status_filter = None
        if status:
            try:
                status_filter = TournamentStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}. Valid values: {[s.value for s in TournamentStatus]}"
                )

        tournaments = service.list_tournaments(
            project_id=project_id,
            status=status_filter,
        )

        return {
            "tournaments": [t.to_dict() for t in tournaments],
            "count": len(tournaments),
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to list tournaments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tournaments: {str(e)}")


@app.get("/tournament/{tournament_id}", summary="Get tournament details")
async def get_tournament(tournament_id: str):
    """
    Get detailed information about a specific tournament.

    Returns:
        - Tournament configuration
        - Current status
        - All rounds and variants
        - Cost tracking
    """
    from backend.services.tournament_service import get_tournament_service

    try:
        service = get_tournament_service()
        tournament = service.get_tournament(tournament_id)

        if not tournament:
            raise HTTPException(status_code=404, detail=f"Tournament {tournament_id} not found")

        return {
            "tournament": tournament.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get tournament: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tournament: {str(e)}")


# ==================== SQUAD SYSTEM ENDPOINTS (Phase 3F) ====================

# --- Pydantic Models for Squad System ---
class ApplySquadRequest(BaseModel):
    squad_id: str
    project_id: Optional[str] = None


class SetTournamentModelsRequest(BaseModel):
    models: List[str]
    project_id: Optional[str] = None


class EstimateCostRequest(BaseModel):
    models: List[str]
    num_strategies: int = 5
    avg_tokens_per_variant: int = 2000


class VoiceRecommendationRequest(BaseModel):
    tournament_results: List[Dict[str, Any]]
    current_squad: str
    project_id: Optional[str] = None


class GenreRecommendationRequest(BaseModel):
    genre: str


# --- Squad Service Initialization ---
def get_squad_service():
    """Get or create the squad service singleton."""
    from backend.services.hardware_service import HardwareService
    from backend.services.squad_service import SquadService

    hardware_service = HardwareService()
    return SquadService(settings_service, hardware_service)


@app.get("/system/hardware", summary="Detect system hardware")
async def get_hardware_info():
    """
    Detect system hardware capabilities.

    Returns:
        - RAM (total and available)
        - CPU cores
        - GPU availability and specs
        - Ollama installation status
        - Installed Ollama models
        - Recommended maximum model size
    """
    from backend.services.hardware_service import HardwareService

    try:
        hardware_service = HardwareService()
        info = hardware_service.detect()
        return info.to_dict()
    except Exception as e:
        logging.error(f"Hardware detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hardware detection failed: {str(e)}")


@app.get("/system/local-models", summary="Get recommended local models")
async def get_recommended_local_models():
    """
    Get recommended local models based on hardware.

    Returns list of models that can run on this system,
    with installation status and recommended purposes.
    """
    from backend.services.hardware_service import HardwareService

    try:
        hardware_service = HardwareService()
        models = hardware_service.get_recommended_local_models()
        return {
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logging.error(f"Local model detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Local model detection failed: {str(e)}")


@app.get("/squad/available", summary="Get available squads")
async def get_available_squads():
    """
    Get squads available based on hardware and API keys.

    Returns all three squad presets with availability status,
    missing requirements, and warnings for optional features.
    """
    try:
        squad_service = get_squad_service()
        squads = squad_service.get_available_squads()
        return {
            "squads": squads,
            "count": len(squads)
        }
    except Exception as e:
        logging.error(f"Squad availability check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Squad availability check failed: {str(e)}")


@app.post("/squad/apply", summary="Apply a squad configuration")
async def apply_squad(request: ApplySquadRequest):
    """
    Apply a squad's configuration to settings.

    This updates:
    - Foreman task models
    - Health check models
    - Tournament defaults
    - Squad metadata

    Args:
        squad_id: "local" | "hybrid" | "pro"
        project_id: Optional project-specific override

    Returns:
        Applied configuration summary
    """
    try:
        squad_service = get_squad_service()
        result = squad_service.apply_squad(request.squad_id, request.project_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Squad application failed: {e}")
        raise HTTPException(status_code=500, detail=f"Squad application failed: {str(e)}")


@app.get("/squad/active", summary="Get active squad")
async def get_active_squad(project_id: Optional[str] = None):
    """
    Get the currently active squad ID.

    Args:
        project_id: Optional project-specific settings

    Returns:
        Current squad ID and setup status
    """
    try:
        squad_service = get_squad_service()
        active = squad_service.get_active_squad(project_id)
        setup_complete = settings_service.get("squad.setup_complete", project_id) or False
        course_mode = settings_service.get("squad.course_mode", project_id) or False

        return {
            "squad": active,
            "setup_complete": setup_complete,
            "course_mode": course_mode
        }
    except Exception as e:
        logging.error(f"Failed to get active squad: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active squad: {str(e)}")


@app.get("/squad/tournament-models", summary="Get tournament models")
async def get_tournament_models(
    project_id: Optional[str] = None,
    include_unavailable: bool = False
):
    """
    Get models available for tournament selection.

    Returns list of models with tier, availability, cost, and selection status.
    Models are grouped by tier (free, budget, premium).

    Args:
        project_id: For project-specific settings
        include_unavailable: Include models without API keys

    Returns:
        List of model dicts with metadata and selection status
    """
    try:
        squad_service = get_squad_service()
        models = squad_service.get_tournament_models(project_id, include_unavailable)
        return {
            "models": models,
            "count": len(models),
            "selected_count": len([m for m in models if m["selected"]])
        }
    except Exception as e:
        logging.error(f"Failed to get tournament models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tournament models: {str(e)}")


@app.post("/squad/tournament-models", summary="Set tournament models")
async def set_tournament_models(request: SetTournamentModelsRequest):
    """
    Set custom tournament model selection.

    This overrides the squad's default tournament models.
    Clear with DELETE /squad/tournament-models/custom to revert to defaults.

    Args:
        models: List of model IDs to use in tournaments
        project_id: For project-specific override
    """
    try:
        squad_service = get_squad_service()
        squad_service.set_tournament_models(request.models, request.project_id)
        return {
            "status": "success",
            "models": request.models,
            "count": len(request.models)
        }
    except Exception as e:
        logging.error(f"Failed to set tournament models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set tournament models: {str(e)}")


@app.delete("/squad/tournament-models/custom", summary="Clear custom tournament models")
async def clear_custom_tournament_models(project_id: Optional[str] = None):
    """
    Clear custom tournament model selection.

    Reverts to the active squad's default tournament models.
    """
    try:
        squad_service = get_squad_service()
        squad_service.clear_custom_tournament_models(project_id)
        return {"status": "success", "message": "Reverted to squad defaults"}
    except Exception as e:
        logging.error(f"Failed to clear custom tournament models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear custom models: {str(e)}")


@app.post("/squad/estimate-cost", summary="Estimate tournament cost")
async def estimate_tournament_cost(request: EstimateCostRequest):
    """
    Estimate cost for a tournament run with selected models.

    Args:
        models: List of model IDs
        num_strategies: Number of writing strategies (default 5)
        avg_tokens_per_variant: Average tokens per variant

    Returns:
        Cost estimate with breakdown by model
    """
    try:
        squad_service = get_squad_service()
        estimate = squad_service.estimate_tournament_cost(
            request.models,
            request.num_strategies,
            request.avg_tokens_per_variant
        )
        return estimate
    except Exception as e:
        logging.error(f"Cost estimation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cost estimation failed: {str(e)}")


@app.get("/squad/voice-recommendation", summary="Get voice recommendation")
async def get_voice_recommendation(project_id: Optional[str] = None):
    """
    Get the voice-based squad recommendation.

    This is populated after a voice tournament is completed and analyzed.

    Returns:
        Recommendation with top model, score, and reasoning
    """
    try:
        recommendation = settings_service.get("squad.voice_recommendation", project_id)
        return recommendation or {
            "recommended_squad": None,
            "reason": "No voice tournament has been run yet"
        }
    except Exception as e:
        logging.error(f"Failed to get voice recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice recommendation: {str(e)}")


@app.post("/squad/voice-recommendation", summary="Generate voice recommendation")
async def generate_voice_recommendation(request: VoiceRecommendationRequest):
    """
    Generate squad recommendation from voice tournament results.

    Analyzes which models best matched the author's target voice
    and recommends the appropriate squad.

    Args:
        tournament_results: List of {model, score, strategy} from voice tournament
        current_squad: User's current squad selection
        project_id: Optional project-specific settings

    Returns:
        Recommendation with reasoning and alternatives
    """
    try:
        squad_service = get_squad_service()
        recommendation = squad_service.generate_voice_recommendation(
            request.tournament_results,
            request.current_squad,
            request.project_id
        )
        return recommendation
    except Exception as e:
        logging.error(f"Voice recommendation generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice recommendation failed: {str(e)}")


@app.post("/squad/genre-recommendation", summary="Get genre-based recommendation")
async def get_genre_recommendation(request: GenreRecommendationRequest):
    """
    Get squad recommendation based on genre.

    Different genres may benefit from different model strengths.
    For example, literary fiction benefits from Claude's nuance,
    while thrillers benefit from DeepSeek's structural thinking.

    Args:
        genre: Genre name (e.g., "cyberpunk", "romance", "literary")

    Returns:
        Recommendation with squad, key models, and reasoning
    """
    try:
        squad_service = get_squad_service()
        recommendation = squad_service.get_squad_for_genre(request.genre)
        return recommendation
    except Exception as e:
        logging.error(f"Genre recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Genre recommendation failed: {str(e)}")


@app.post("/squad/course-mode", summary="Toggle course mode")
async def toggle_course_mode(
    enabled: bool,
    project_id: Optional[str] = None
):
    """
    Toggle course mode on/off.

    Course mode:
    - When enabled, uses instructor-provided API keys
    - Hybrid Squad available to all students at no cost
    - Pro Squad still requires student BYOK

    Args:
        enabled: True to enable course mode
        project_id: Optional project-specific setting
    """
    try:
        settings_service.set("squad.course_mode", enabled, project_id)
        return {
            "course_mode": enabled,
            "message": "Course mode enabled" if enabled else "Course mode disabled"
        }
    except Exception as e:
        logging.error(f"Failed to toggle course mode: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle course mode: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

