import os
import sys
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.graph.schema import Base, Node
from backend.graph.graph_service import KnowledgeGraphService

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_FILE = "lab/test_graph.db"
DB_URL = f"sqlite:///{DB_FILE}"

def setup_database():
    """Initializes a clean SQLite database and returns a session."""
    # Clean up old database file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        logging.info(f"Removed old database file: {DB_FILE}")

    engine = create_engine(DB_URL)
    
    # Create all tables defined in the schema
    Base.metadata.create_all(engine)
    logging.info("Database tables created.")

    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def main():
    """
    Runs a test to verify the refactored KnowledgeGraphService.
    """
    logging.info("--- Starting Graph Engine Test ---")
    
    # 1. Set up the database
    session = setup_database()

    try:
        # 2. Initialize the KnowledgeGraphService
        logging.info("Initializing KnowledgeGraphService...")
        graph_service = KnowledgeGraphService(session)
        
        # Verify initial state
        initial_stats = graph_service.get_stats()
        logging.info(f"Initial graph state: {initial_stats['nodes']} nodes, {initial_stats['edges']} edges.")
        assert initial_stats['nodes'] == 0, "Graph should be empty initially."

        # 3. Create and save a new node
        logging.info("Creating a new node: 'Alice'.")
        new_node = Node(
            name="Alice",
            node_type="character",
            description="A curious and determined protagonist."
        )
        
        # Add the node via the service
        saved_node = graph_service.add_node(new_node)
        logging.info(f"Service call to add_node completed. Node assigned ID: {saved_node.id}")
        assert saved_node.id is not None, "Saved node must have an ID."

        # 4. Verify the node was saved
        logging.info(f"Verifying node persistence by retrieving it from the database...")
        retrieved_node = graph_service.get_node(saved_node.id)
        
        assert retrieved_node is not None, "Failed to retrieve the node from the database."
        assert retrieved_node.name == "Alice", "Retrieved node has incorrect data."
        logging.info(f"Successfully retrieved node '{retrieved_node.name}' (ID: {retrieved_node.id}).")

        # 5. Verify in-memory graph was also updated
        final_stats = graph_service.get_stats()
        logging.info(f"Final graph state: {final_stats['nodes']} nodes, {final_stats['edges']} edges.")
        assert final_stats['nodes'] == 1, "In-memory graph was not updated correctly."
        
        logging.info("--- Graph Engine Test PASSED ---")

    except Exception as e:
        logging.error(f"--- Graph Engine Test FAILED ---")
        logging.error(f"An error occurred: {e}", exc_info=True)
    finally:
        # Clean up the session
        session.close()
        logging.info("Database session closed.")

if __name__ == "__main__":
    main()
