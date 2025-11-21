import os
import sys
import shutil
import logging
import yaml

# --- Path Setup ---
# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# --- Imports from our application ---
from backend.agents.wizard.setup import generate_project_config
from backend.agents.registry import AgentRegistry
from backend.agents.specialists.scaffold import SmartScaffoldAgent
from backend.agents.orchestrator import SceneTournament, DraftCritic
from backend.graph.graph_service import KnowledgeGraphService
from backend.graph.schema import Base, Node
from backend.graph.ner_extractor import NERExtractor, SPACY_AVAILABLE

# --- SQLAlchemy Imports ---
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
PROJECT_ROOT = "workspace"
PROJECT_NAME = "student_project"
PROJECT_PATH = os.path.join(PROJECT_ROOT, PROJECT_NAME)
CONFIG_PATH = os.path.join(PROJECT_PATH, "config")
SCENES_PATH = os.path.join(PROJECT_PATH, "scenes")
DB_FILE = os.path.join(PROJECT_PATH, "graph.db")
DB_URL = f"sqlite:///{DB_FILE}"
BASE_TEMPLATE_PATH = "backend/templates/reference_skills"
AGENTS_CONFIG_PATH = "agents.yaml"

def main():
    """
    Orchestrates the full pipeline from setup to scene generation and graph ingestion.
    """
    logging.info("--- 🚀 STARTING MASTER PIPELINE 🚀 ---")

    # --- Setup on Demand ---
    if not os.path.exists(CONFIG_PATH):
        logging.warning(f"Project '{PROJECT_NAME}' not found. Running Setup Wizard...")
        mock_voice_sample = "The city was a gritty mess, a real noir landscape. I knew the facts were out there, but the shadows held them tight."
        mock_user_answers = {"genre": "detective_noir", "protagonist_name": "Alice"}
        generate_project_config(
            project_name=PROJECT_NAME,
            voice_sample=mock_voice_sample,
            user_answers=mock_user_answers,
            base_template_path=BASE_TEMPLATE_PATH,
            project_root=PROJECT_ROOT
        )
    else:
        logging.info(f"Found existing project '{PROJECT_NAME}'.")

    # --- Initialize Services ---
    logging.info("--- Initializing Core Services ---")
    # Database
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    # Core Services
    graph_service = KnowledgeGraphService(session=db_session)
    agent_registry = AgentRegistry(config_path=AGENTS_CONFIG_PATH)
    logging.info("Graph Service and Agent Registry are online.")

    # --- Pre-populate Graph for Demo ---
    # The scaffold agent needs a scene node to exist in the DB.
    # We'll create one here for this pipeline run.
    if not graph_service.get_node(1):
        logging.info("Pre-populating graph with 'Chapter 1' scene node.")
        scene_node = Node(id=1, name="Chapter 1", node_type="scene", description="The first chapter.")
        graph_service.add_node(scene_node)
    else:
        logging.info("'Chapter 1' scene node already exists.")

    # --- Step 1: Generate Scaffold ---
    logging.info("\n--- STEP 1: Generating Scene Scaffold ---")
    # Mock MCP client for scaffold generation
    class MockMCPClient:
        def get_context_for_scene(self, scene_id: int) -> str:
            return "Research notes: The package is a decoy. The real data is on a hidden microdot."
    
    scaffold_agent = SmartScaffoldAgent(
        graph_service=graph_service, # Note: The scaffold agent uses a mock graph service internally for now
        mcp_client=MockMCPClient(),
        template_path=os.path.join(CONFIG_PATH, '..', '..', '..', 'backend', 'templates', 'ace_structure.md')
    )
    scene_scaffold = scaffold_agent.generate_scaffold(scene_id=1)
    logging.info("Scaffold for 'Chapter 1' generated.")
    print(scene_scaffold)

    # --- Step 2: Run Tournament ---
    logging.info("\n--- STEP 2: Running Scene Tournament ---")
    with open(os.path.join(CONFIG_PATH, "multiplier.yaml"), 'r') as f:
        strategies = yaml.safe_load(f).get('strategies', [])
    
    tournament_agents = [
        agent['id'] for agent in agent_registry.list_enabled_agents() 
        if "tournament" in agent.get('use_cases', [])
    ]
    
    if not tournament_agents:
        logging.error("No agents available for a tournament. Aborting.")
        return
    
    logging.info(f"Found {len(tournament_agents)} agents for the tournament: {', '.join(tournament_agents)}")

    tournament = SceneTournament(agent_registry)
    drafts = tournament.run_tournament(scene_scaffold, tournament_agents, strategies)

    # --- Step 3: Critique and Select Winner ---
    logging.info("\n--- STEP 3: Critiquing Drafts ---")
    critic = DraftCritic()
    results = critic.evaluate_drafts(drafts)
    winner = results[0]
    logging.info(f"🏆 Winner is '{winner['agent_name']}' with strategy '{winner['strategy_name']}'.")
    print(f"Winning Draft Text:\n---\n{winner['draft_text']}\n---")

    # --- Step 4: Save and Ingest ---
    logging.info("\n--- STEP 4: Saving Scene and Ingesting to Graph ---")
    os.makedirs(SCENES_PATH, exist_ok=True)
    scene_file_path = os.path.join(SCENES_PATH, "Chapter_1.md")
    with open(scene_file_path, 'w') as f:
        f.write(winner['draft_text'])
    logging.info(f"Winning scene saved to '{scene_file_path}'.")

    if not SPACY_AVAILABLE:
        logging.warning("spaCy not available, skipping graph ingestion.")
    else:
        logging.info("Ingesting new entities from winning text into Knowledge Graph...")
        ner_extractor = NERExtractor()
        extracted_nodes = ner_extractor.extract_nodes(winner['draft_text'], scene_id="Chapter_1")
        
        if not extracted_nodes:
            logging.info("No new nodes found to ingest.")
        else:
            for node in extracted_nodes:
                # Check if node already exists
                existing_node = graph_service.find_node_by_name(node.name)
                if not existing_node:
                    graph_service.add_node(node)
                else:
                    logging.info(f"Node '{node.name}' already exists. Skipping.")
    
    logging.info("Final graph state:")
    print(graph_service.get_stats())
    
    db_session.close()
    logging.info("\n--- 🚀 MASTER PIPELINE FINISHED 🚀 ---")


if __name__ == "__main__":
    # Clean up workspace for a fresh run
    if os.path.exists(PROJECT_ROOT):
        shutil.rmtree(PROJECT_ROOT)
        logging.info("Cleaned up old workspace.")
    main()
