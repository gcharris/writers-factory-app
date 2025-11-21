import os
import sys
import shutil
import logging
import yaml
import asyncio
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- App Imports ---
# Fix path to allow importing from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.wizard.setup import generate_project_config
from backend.agents.registry import AgentRegistry
from backend.agents.specialists.scaffold import SmartScaffoldAgent
from backend.agents.orchestrator import SceneTournament, DraftCritic
from backend.graph.graph_service import KnowledgeGraphService
from backend.graph.schema import Base, Node
from backend.graph.ner_extractor import NERExtractor, SPACY_AVAILABLE
from backend.services.llm_service import LLMService
from backend.services.manager_service import ManagerService

# Initialize Services
try:
    llm_service = LLMService()
    manager_service = ManagerService(model="llama3.2") # Make sure you have this model pulled
except Exception as e:
    print(f"Error initializing services: {e}")
    llm_service = None
    manager_service = None

# Load Agents
# Agents config lives at repo root (../agents.yaml)
AGENTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents.yaml")
AGENTS = []
if os.path.exists(AGENTS_PATH):
    with open(AGENTS_PATH, "r") as f:
        data = yaml.safe_load(f)
        AGENTS = data.get("agents", [])

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class TournamentRequest(BaseModel):
    topic: str

class ManagerChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

# --- API Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Writers Factory API is running"}

@app.get("/agents")
def get_agents():
    """Return the list of configured agents."""
    return {"agents": AGENTS}

@app.post("/tournament")
async def run_tournament(req: TournamentRequest):
    """
    Run the actual tournament logic.
    """
    return await run_tournament_logic(req.topic)

@app.post("/tournament/run")
async def run_tournament_alias(req: TournamentRequest):
    """Alias for /tournament to match frontend requests"""
    return await run_tournament_logic(req.topic)

async def run_tournament_logic(topic: str):
    if not llm_service:
        raise HTTPException(status_code=500, detail="LLM Service not active. Check server logs.")

    print(f"🎬 Starting tournament on topic: {topic}")
    submissions: List[str] = []
    full_text_log = ""  # New variable to hold raw text
    
    # 1. Drafting Phase
    for agent in AGENTS:
        print(f"   Drafting: {agent['name']}...")
        try:
            content = await llm_service.generate_response(
                provider=agent["provider"],
                model=agent["model"],
                system_role=agent.get("role", "You are a helpful writing assistant."),
                prompt=f"Write a short, compelling scene (approx 150 words) about: {topic}",
            )
            entry = f"--- Candidate: {agent['name']} ---\n{content}\n"
            submissions.append(entry)
            full_text_log += entry + "\n"
        except Exception as e:
            print(f"❌ {agent['name']} failed: {e}")

    if not submissions:
        return {"topic": topic, "verdict": "All agents failed to write. Check API Keys."}

    # 2. Judging Phase
    print("⚖️  Judging...")
    judge_prompt = (
        f"Topic: {topic}\n\n"
        + "\n".join(submissions)
        + "\n\nEvaluate these scenes. Select the best one based on creativity and voice. "
        "Format output as: 'WINNER: [Agent Name]\nREASON: [1-sentence reason]'"
    )

    try:
        verdict = await llm_service.generate_response(
            provider="openai",
            model="gpt-4o",
            system_role="You are an impartial literary critic.",
            prompt=judge_prompt,
        )
    except Exception as e:
        verdict = f"Judge failed to decide. Error: {e}"

    return {
        "topic": topic,
        "verdict": verdict,
        "full_story": full_text_log
    }

# --- Manager Endpoints ---

@app.get("/manager/status")
async def get_manager_status():
    """Check if local Ollama is running."""
    is_running = manager_service.check_status()
    return {"status": "active" if is_running else "offline", "model": manager_service.model}

@app.post("/manager/chat")
async def chat_with_manager(req: ManagerChatRequest):
    """Send a message to the local Manager agent."""
    response = manager_service.chat(req.message, req.context)
    return {"response": response}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=False)
