# Writers Factory - Final Handoff Report
**Date:** November 22, 2025 (13:10)
**Status:** STABLE INFRASTRUCTURE (NotebookLM Logic Pending Upstream Fix)

## 1. System Status
| Component | Status | Notes |
|-----------|--------|-------|
| **Backend (FastAPI)** | ✅ Online | Running on Port 8000. All endpoints functional. |
| **Frontend (Tauri)** | ✅ Online | Running on Port 1420. UI connected. |
| **Agents (Ollama)** | ✅ Online | Squad fully operational. |
| **NotebookLM Integration** | ⚠️ Partial | **Server Launches:** ✅ **Auth Triggers:** ✅ **Query:** ❌ (Crashes due to upstream scraper/browser bugs). |

## 2. The MCP Saga
We attempted two different MCP server implementations to fix the "Oracle":
1.  **PleasePrompto (Node.js):** Launches browser successfully but crashes when parsing the NotebookLM page (Google UI change). **Current Active Version.**
2.  **Khengyun (Python):** Has updated logic but crashes on macOS due to `undetected-chromedriver` incompatibilities ("session not created").

**Decision:** We reverted to **PleasePrompto** because it is structurally sound and will likely be the first to get a scraper fix from the community.

## 3. How to Run
```bash
# 1. Start Backend
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-factory-app"
source venv/bin/activate
python backend/api.py

# 2. Start Frontend (New Terminal)
cd frontend
npm run tauri dev
```

## 4. Next Steps (The "Metabolism")
Now that the "Body" (App) is built and the "Brain" (Agents) is online, you can proceed to:
1.  **Orchestrate Agents:** Use the `Orchestrator` to assign tasks to `CreativeDirector` and `Editor`.
2.  **Write Scenes:** The file system and editor are fully wired.
3.  **Monitor MCP:** Watch the [PleasePrompto/notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp) repo for a fix to the `substring` error. When they push a fix, simply run `git pull` in `backend/external/notebooklm-mcp` and `npm run build`.

**The Factory is Open.**
