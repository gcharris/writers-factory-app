# Writers Factory - Troubleshooting & Handoff Report
**Date:** November 22, 2025
**Status:** STABLE (with caveats)

## 1. System Status
| Component | Status | Notes |
|-----------|--------|-------|
| **Backend (FastAPI)** | ✅ Online | Running on Port 8000. Serving all endpoints. |
| **Frontend (Tauri)** | ✅ Online | Running on Port 1420. Connected to Backend. |
| **Agents (Ollama)** | ✅ Online | `llama3.2:3b` verified. Squad is operational. |
| **Graph (NetworkX)** | ✅ Online | Database connected. Visualization works. |
| **NotebookLM (MCP)** | ⚠️ Partial | **Auth works**, **Handshake works**. **Query Fails** due to upstream scraper bug (`substring` error). |

## 2. Recent Repairs
1.  **Git Split-Brain Fixed:** Merged worktree changes back to main. Removed problematic submodules.
2.  **MCP Client Architecture:** Rewrote `notebooklm_service.py` to support full MCP Handshake and robust stream reading.
3.  **Path Correction:** Fixed `backend/external/notebooklm-mcp` location issues that were causing "File not found" errors.
4.  **Auth Flow:** Implemented dedicated `/notebooklm/auth` endpoint and UI button to trigger Google Login.

## 3. Known Issues
### The NotebookLM Scraper Bug
The external tool (`notebooklm-mcp`) crashes when parsing the NotebookLM website because Google likely changed the HTML structure.
- **Error:** `Cannot read properties of undefined (reading 'substring')`
- **Location:** Inside the Node.js MCP server (not our Python code).
- **Impact:** You can log in, but you cannot query notebooks yet.
- **Solution:** Wait for upstream fix or replace with a different research provider.

## 4. How to Run
### Backend
```bash
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-factory-app"
source venv/bin/activate
python backend/api.py
```

### Frontend
```bash
cd frontend
npm run tauri dev
```

## 5. Next Steps (Recommended)
1.  **Focus on Agents:** The "Metabolism" phase (Agent Orchestration) is fully functional. Proceed with drafting scenes.
2.  **Monitor MCP:** Check the `notebooklm-mcp` GitHub repo for updates regarding the scraper fix.
3.  **Backup:** A full git backup was performed (Commit `c4572f0`).
