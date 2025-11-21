import os
import sys
import shutil
import logging

from fastapi.testclient import TestClient

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api import app

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Test Client ---
client = TestClient(app)

def setup_test_environment():
    """Ensures the workspace is clean before a test run."""
    if os.path.exists("workspace"):
        shutil.rmtree("workspace")
        logging.info("Cleaned up old workspace directory for a fresh test run.")

def test_tournament_endpoint():
    """
    Tests the full flow required to hit the /tournament/run endpoint.
    1. Initializes a project using the /project/init endpoint.
    2. Runs a tournament using the /tournament/run endpoint.
    3. Verifies the response.
    """
    logging.info("--- Starting API Test for /tournament/run ---")
    
    # --- Step 1: Initialize the project first ---
    # This is required because the tournament endpoint needs the config files.
    logging.info("Calling /project/init to set up the test project...")
    init_response = client.post(
        "/project/init",
        json={
            "project_name": "student_project",
            "voice_sample": "A test voice sample.",
            "protagonist_name": "Tester"
        }
    )
    assert init_response.status_code == 200, f"Project init failed: {init_response.text}"
    logging.info("Project initialization successful.")

    # --- Step 2: Call the tournament endpoint ---
    logging.info("Calling /tournament/run with a mock scaffold...")
    mock_scaffold = "# Test Scaffold\n\nThis is the context for the scene."
    
    response = client.post(
        "/tournament/run",
        json={"scaffold": mock_scaffold}
    )
    
    # --- Step 3: Verify the response ---
    logging.info(f"Received status code: {response.status_code}")
    assert response.status_code == 200, f"Request failed: {response.text}"
    
    data = response.json()
    logging.info(f"Received {len(data)} drafts in the response.")
    assert isinstance(data, list), "Response should be a list."
    assert len(data) > 0, "Response list should not be empty."
    
    first_result = data[0]
    logging.info(f"First result keys: {first_result.keys()}")
    expected_keys = ["agent_name", "strategy_name", "draft_text", "scores", "total_score"]
    for key in expected_keys:
        assert key in first_result, f"Key '{key}' is missing from the tournament result."
        
    logging.info("All assertions passed. Response format is correct.")
    logging.info("--- API Test for /tournament/run PASSED ---")


if __name__ == "__main__":
    setup_test_environment()
    test_tournament_endpoint()
