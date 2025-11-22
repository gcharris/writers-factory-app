# Troubleshooting Report: Writers Factory Desktop (State @ Nov 22)

## 1. System Status

| Component | Status | Notes |
| :--- | :--- | :--- |
| **Backend API** | ✅ Online | Running on port 8000 from repo root. |
| **Frontend** | ✅ Online | File Tree & Editor fully functional (CORS fixed). |
| **Squad/Agents** | ✅ Online | `agents.yaml` loading correctly. Endpoints `/agents` verified. |
| **Manager** | ✅ Online | Heartbeat endpoint `/manager/status` verified. |
| **NotebookLM MCP** | ⚠️ Partial | Server launches, but query fails with 500/Timeout. |

## 2. Recent Repairs & Changes

### A. Git & Environment "Split Brain"
- **Issue:** Worktree `wpJ1a` vs Main Repo confusion caused file mismatches.
- **Fix:** Merged all worktree changes to `main`. Restored `backend/api.py` to full functionality.
- **Env:** Moved `.env` to root so `python-dotenv` loads keys automatically.

### B. NotebookLM Integration (The Current Bottleneck)
- **Architecture:** Python `api.py` -> `notebooklm_service.py` -> Subprocess `node dist/index.js` (MCP Server).
- **Actions Taken:**
    1.  **Missing Code:** Re-cloned `notebooklm-mcp` into `backend/external/`.
    2.  **Protocol Mismatch:** Rewrote Python service to use standard MCP `tools/call` instead of custom JSON-RPC.
    3.  **Headless Auth:** Forced `HEADLESS=false` so you can see the browser to sign in.
    4.  **Output Parsing:** Updated Python reader to ignore Node.js startup banners/logs in `stdout`.

## 3. Current Error: NotebookLM 500
- **Symptom:** Clicking "Run Research Query" spins, then returns 500.
- **Logs:** "MCP STDOUT (ignored)" messages appear, followed by a crash or timeout.
- **Root Cause Hypothesis:** The Python script sends the JSON request `{"method": "tools/call", ...}` but the Node server might be consuming it *before* it's ready, or the response is being printed to `stderr` (which Python treats as a crash) instead of `stdout`.
- **Authentication:** The browser launch is the critical step. If it doesn't launch, the server waits indefinitely for auth, causing a timeout in the Python client.

## 4. Next Steps for Gemini Architect

1.  **Verify Node Process:** Run `node dist/index.js` manually in `backend/external/notebooklm-mcp` and pipe a raw JSON request to see if it hangs.
2.  **Check Auth State:** Inspect `~/Library/Application Support/notebooklm-mcp/` to see if a session file exists.
3.  **Timeout Handling:** Increase the read timeout in `notebooklm_service.py` (currently blocking `readline()`).
4.  **Alternative Bridge:** If the Node MCP remains unstable, consider a direct Python Playwright bridge (removing the Node.js dependency entirely) to simplify the stack.

## 5. Full Architecture Plan (Reference)
*See `docs/MASTER_ARCHITECTURE.md` for the finalized vision of how these components interact.*

