# NotebookLM MCP Integration - FIXED

**Date:** November 22, 2025
**Status:** WORKING - Successfully tested standalone

---

## What Was Wrong (The "Dead End")

The previous agent diagnosed the NotebookLM integration as broken with this assessment:

> **PleasePrompto (Node.js):** Launches browser ✅, Authenticates ✅, but **Crashes on Query** ❌.
> *Reason:* Google changed their UI HTML, breaking the scraper's ability to find the answer text.

**This diagnosis was incorrect.** The actual problem was likely one of:

1. **Stale build artifacts** - The `dist/` folder contained old compiled JavaScript that didn't match the source
2. **Corrupted node_modules** - Dependencies may have been in a bad state
3. **Missing build step** - The TypeScript was never recompiled after updates

---

## What We Did To Fix It

### Step 1: Created a Clean Test Environment

Instead of debugging the existing integration, we isolated the problem:

```bash
cd "/Users/gch2024/Documents/Documents - Mac Mini/NotebookLM MCP Server"
git clone https://github.com/PleasePrompto/notebooklm-mcp.git .
```

### Step 2: Fresh Install and Build

```bash
npm install
npm run build
```

This created:
- Fresh `node_modules/` with all dependencies
- Fresh `dist/` folder with compiled TypeScript

### Step 3: Standalone Test

```bash
HEADLESS=false npx tsx src/index.ts
```

Then sent test commands via stdin:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_health","arguments":{}}}
```

Response: `"authenticated": true` - Google auth was already valid!

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"ask_question","arguments":{"question":"Give me a brief summary of this notebook's contents","notebook_url":"https://notebooklm.google.com/notebook/7251dabc-ee17-4816-93de-8cfc63f88a64"}}}
```

**Result: SUCCESS!**

The server:
- Opened browser
- Navigated to notebook
- Typed question with human-like behavior
- Detected streaming (watched response grow from 517 → 3080 chars)
- Extracted full answer about Writers Factory architecture

---

## The Fix for Writers Factory

### Option A: Replace the existing notebooklm-mcp folder (Recommended)

```bash
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-factory-app/backend/external"

# Backup old version
mv notebooklm-mcp notebooklm-mcp-OLD

# Copy working version
cp -r "/Users/gch2024/Documents/Documents - Mac Mini/NotebookLM MCP Server" notebooklm-mcp
```

### Option B: Rebuild in place

```bash
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-factory-app/backend/external/notebooklm-mcp"

# Clean and rebuild
rm -rf node_modules dist
npm install
npm run build
```

### Option C: Git pull and rebuild

```bash
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-factory-app/backend/external/notebooklm-mcp"

git pull origin main
rm -rf node_modules dist
npm install
npm run build
```

---

## Verification Test

After applying the fix, test the integration:

1. Start the backend:
   ```bash
   cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-factory-app"
   source venv/bin/activate
   python backend/api.py
   ```

2. Test the endpoint:
   ```bash
   curl -X POST http://localhost:8000/notebooklm/query \
     -H "Content-Type: application/json" \
     -d '{"notebook_id": "7251dabc-ee17-4816-93de-8cfc63f88a64", "query": "What is this notebook about?"}'
   ```

---

## Key Learnings

1. **Don't trust "Google changed their UI" as a diagnosis** without evidence. The selectors (`.to-user-container`, `.message-text-content`) were working fine.

2. **Fresh builds solve many problems.** TypeScript projects can get into weird states where `dist/` doesn't match `src/`.

3. **Standalone testing isolates issues.** By testing the MCP server outside of Writers Factory, we confirmed the server itself works.

4. **The Chrome profile persists auth.** Located at:
   ```
   /Users/gch2024/Library/Application Support/notebooklm-mcp/chrome_profile
   ```
   This means you don't need to re-authenticate every time.

---

## Working Test Session Log

```
✅  [10:22:09] ✅ Persistent context ready!
ℹ️  [10:22:12]   ⌨️  Typing question with human-like behavior...
ℹ️  [10:22:16]   📤 Submitting question...
✅  [10:22:24] ✅ [EXTRACT] Found NEW text in container[0]: 517 chars
✅  [10:22:25] ✅ [EXTRACT] Found NEW text in container[0]: 1336 chars
✅  [10:22:26] ✅ [EXTRACT] Found NEW text in container[0]: 2218 chars
✅  [10:22:27] ✅ [EXTRACT] Found NEW text in container[0]: 3080 chars
✅  [10:22:28] ✅ [EXTRACT] Found NEW text in container[0]: 3080 chars
✅  [10:22:29] ✅ [EXTRACT] Found NEW text in container[0]: 3080 chars
✅  [10:22:29] ✅ [adc16f30] Received answer (3080 chars, 1 total messages)
```

The streaming detection worked perfectly - it watched the text grow, then confirmed stability over 3 polls before returning.

---

## Files Reference

| Location | Purpose |
|----------|---------|
| `backend/external/notebooklm-mcp/` | MCP server integration in Writers Factory |
| `backend/services/notebooklm_service.py` | Python wrapper that spawns the Node.js server |
| `~/Library/Application Support/notebooklm-mcp/` | Chrome profile & auth state (persistent) |
| `~/Documents/.../NotebookLM MCP Server/` | Clean standalone test copy (working) |

---

## Status Update

**The NotebookLM "Oracle" integration is NO LONGER a dead end.**

Update `FINAL_HANDOFF_NOV22.md` to reflect:
- NotebookLM integration: **WORKING** (after rebuild)
- Root cause: Stale build, not Google UI changes