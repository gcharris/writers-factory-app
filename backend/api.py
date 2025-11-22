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

# --- Graph Ingestion ---
@app.post("/ingest")
async def run_ingestion():
    """Trigger manual graph ingestion from World Bible"""
    ingestor = GraphIngestor()
    await ingestor.run_ingestion()
    return {"status": "Ingestion complete"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

