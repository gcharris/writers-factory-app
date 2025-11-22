# Writers Factory - Final Handoff Report
**Date:** November 22, 2025 (13:20)
**Status:** INFRASTRUCTURE COMPLETE | NOTEBOOKLM STALLED

## 1. Where We Are (Successes)
The core application "Body" and "Brain" are fully functional and backed up.
*   **Backend (FastAPI):** ✅ **Online.** Serving files, running agents, and hosting the API on Port 8000.
*   **Frontend (Tauri):** ✅ **Online.** The UI is connected, file editing works, and the Sidebar is active.
*   **Agents (Ollama/Llama 3.2):** ✅ **Online.** The "Squad" (Orchestrator, Director, etc.) is responsive.
*   **Git Repository:** ✅ **Clean.** All messy submodules fixed. Private data (Chrome Profile) is ignored but preserved locally.

## 2. The "Dead End" (NotebookLM Integration)
We hit a wall with the NotebookLM "Oracle" integration due to external tool breakages.

| Implementation | Status | Why it Failed (Dead End) |
|:---|:---|:---|
| **PleasePrompto (Node.js)** | **Active** | Launches browser ✅, Authenticates ✅, but **Crashes on Query** ❌. <br> *Reason:* Google changed their UI HTML, breaking the scraper's ability to find the answer text. Needs an upstream code update. |
| **Khengyun (Python)** | **Backed Up** | **Crashes on Launch** ❌. <br> *Reason:* The `undetected-chromedriver` library conflicts with your specific version of Chrome/macOS, preventing the browser from even starting. |

**Current Strategy:**
We are using the **PleasePrompto** version. It is installed and ready. We are simply waiting for the open-source maintainers to fix the "scraper selector" bug.

## 3. How to Resume Work
**Start the Factory:**
```bash
# Terminal 1: Backend
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-factory-app"
source venv/bin/activate
python backend/api.py

# Terminal 2: Frontend
cd frontend
npm run tauri dev
```

**Fixing the Dead End (When ready):**
Monitor the [PleasePrompto GitHub Issues](https://github.com/PleasePrompto/notebooklm-mcp/issues). When a fix is posted:
1. `cd backend/external/notebooklm-mcp`
2. `git pull`
3. `npm run build`

## 4. Project Structure Reference
*   `backend/api.py` - Main entry point.
*   `backend/notebooklm_config.json` - Stores your Notebook IDs.
*   `backend/external/notebooklm-mcp/` - The Active Node.js MCP server.
*   `backend/external/khengyun-mcp/` - The Inactive Python MCP server (kept for reference).
