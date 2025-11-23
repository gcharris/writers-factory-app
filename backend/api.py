import os
import sys
import shutil
import logging
import yaml
import json
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Path Setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- App Imports ---
# [RESTORED CODE] Force load the .env file from the backend folder or root
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path) # Load backend/.env
load_dotenv() # Load root .env if exists

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

    Returns work order status, conversation length, and pending KB entries.
    """
    try:
        foreman = get_foreman()
        state = foreman.get_state()
        return {
            "active": foreman.work_order is not None,
            "mode": foreman.mode.value,
            "work_order": state.get("work_order"),
            "conversation_length": len(foreman.conversation),
            "kb_entries_pending": len(foreman.kb_entries),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@app.post("/foreman/flush-kb", summary="Flush KB entries for persistence")
async def foreman_flush_kb():
    """
    Flush pending KB entries.

    Returns the entries and clears the pending list.
    Caller should persist these to the Knowledge Graph.
    """
    try:
        foreman = get_foreman()
        entries = foreman.flush_kb_entries()
        return {
            "status": "flushed",
            "entries": entries,
            "count": len(entries),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to flush KB: {str(e)}")


@app.post("/foreman/reset", summary="Reset the Foreman")
async def foreman_reset():
    """
    Reset the Foreman to initial state.

    Clears the current project, conversation, and KB entries.
    """
    global _foreman_instance
    _foreman_instance = None
    return {"status": "reset", "message": "Foreman has been reset"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

