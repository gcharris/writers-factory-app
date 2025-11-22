# Agent Prompt: Fix NotebookLM Integration in Writers Factory

**Copy and paste this prompt to the agent that needs to fix the integration:**

---

## Context

You previously diagnosed the NotebookLM MCP integration as a "dead end" because you believed Google changed their UI HTML, breaking the scraper selectors.

**That diagnosis was wrong.**

I tested the NotebookLM MCP server standalone and it works perfectly. The real problem was likely stale build artifacts in the `backend/external/notebooklm-mcp/` folder.

## Proof It Works

I cloned a fresh copy to `/Users/gch2024/Documents/Documents - Mac Mini/NotebookLM MCP Server/`, ran `npm install && npm run build`, and tested it:

```
✅ [10:22:29] ✅ [adc16f30] Received answer (3080 chars, 1 total messages)
✅ [TOOL] ask_question completed successfully
```

The server successfully:
- Opened browser and navigated to notebook
- Typed question with human-like behavior
- Detected streaming response (517 → 3080 chars over several seconds)
- Extracted the full answer

The selectors (`.to-user-container`, `.message-text-content`) work fine.

## Your Task

Fix the Writers Factory integration by doing ONE of these:

### Option A: Replace with working copy (Safest)

```bash
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-factory-app/backend/external"
mv notebooklm-mcp notebooklm-mcp-OLD
cp -r "/Users/gch2024/Documents/Documents - Mac Mini/NotebookLM MCP Server" notebooklm-mcp
```

### Option B: Clean rebuild in place

```bash
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-factory-app/backend/external/notebooklm-mcp"
rm -rf node_modules dist
npm install
npm run build
```

## Then Verify

1. Start backend: `python backend/api.py`
2. Test endpoint:
   ```bash
   curl -X POST http://localhost:8000/notebooklm/query \
     -H "Content-Type: application/json" \
     -d '{"notebook_id": "7251dabc-ee17-4816-93de-8cfc63f88a64", "query": "What is this notebook about?"}'
   ```

## Update Documentation

After confirming it works, update `docs/FINAL_HANDOFF_NOV22.md`:
- Change NotebookLM status from "STALLED" to "WORKING"
- Note that the fix was a clean rebuild, not waiting for upstream patches

## Reference

Full details of the debugging session are in:
- `docs/NOTEBOOKLM_FIX_NOV22.md`

---

**End of prompt**
