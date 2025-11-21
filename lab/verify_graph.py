import os
import sys
import logging
import shutil

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.graph.schema import Base, Node, Edge
from backend.graph.graph_service import KnowledgeGraphService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_FILE = "lab/graph.db"
DB_URL = f"sqlite:///{DB_FILE}"

def setup_database():
    """Initializes a clean SQLite database and returns a session."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        logging.info(f"Removed old database file: {DB_FILE}")

    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    logging.info("Database tables created.")

    Session = sessionmaker(bind=engine)
    return Session()

def main():
    """
    Runs a test to verify the refactored KnowledgeGraphService by adding
    two nodes and an edge, then querying the result.
    """
    logging.info("--- Starting Graph Refactor Verification (Task G) ---")
    
    session = setup_database()

    try:
        # 1. Initialize the GraphService
        logging.info("Initializing KnowledgeGraphService...")
        graph_service = KnowledgeGraphService(session)
        assert graph_service.get_stats()['nodes'] == 0, "Graph should be empty."

        # 2. Add a character node
        logging.info("Adding character node: 'Mickey'.")
        char_node = Node(name="Mickey", node_type="character", description="A writer.")
        saved_char = graph_service.add_node(char_node)
        assert saved_char.id is not None, "Character node was not saved."
        logging.info(f"Node 'Mickey' saved with ID: {saved_char.id}")

        # 3. Add a location node
        logging.info("Adding location node: 'Dojo'.")
        loc_node = Node(name="Dojo", node_type="location", description="A place of training.")
        saved_loc = graph_service.add_node(loc_node)
        assert saved_loc.id is not None, "Location node was not saved."
        logging.info(f"Node 'Dojo' saved with ID: {saved_loc.id}")

        # 4. Add an edge between them
        logging.info("Adding edge: Mickey 'LOCATED_IN' Dojo.")
        edge = Edge(
            source_id=saved_char.id,
            target_id=saved_loc.id,
            relation_type="LOCATED_IN"
        )
        saved_edge = graph_service.add_edge(edge)
        assert saved_edge.id is not None, "Edge was not saved."
        logging.info(f"Edge 'LOCATED_IN' saved with ID: {saved_edge.id}")

        # 5. Verify the graph state
        logging.info("Verifying final graph state...")
        stats = graph_service.get_stats()
        assert stats['nodes'] == 2, f"Expected 2 nodes, but found {stats['nodes']}"
        assert stats['edges'] == 1, f"Expected 1 edge, but found {stats['edges']}"
        logging.info(f"Graph state correct: {stats['nodes']} nodes, {stats['edges']} edges.")

        # 6. Query the graph to prove the connection
        mickey_edges = graph_service.get_edges(source_id=saved_char.id)
        assert len(mickey_edges) == 1, "Failed to query the edge from the source node."
        retrieved_edge = mickey_edges[0]
        assert retrieved_edge.target_id == saved_loc.id, "Edge does not point to the correct target."
        assert retrieved_edge.relation_type == "LOCATED_IN", "Edge has incorrect relation type."
        logging.info("Successfully queried and verified the edge from the database.")

        logging.info("--- Graph Refactor Verification PASSED ---")

    except Exception as e:
        logging.error("--- Graph Refactor Verification FAILED ---", exc_info=True)
    finally:
        session.close()
        logging.info("Database session closed.")

if __name__ == "__main__":
    main()
