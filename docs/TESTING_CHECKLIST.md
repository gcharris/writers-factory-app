# Writers Factory Testing Checklist

**Created**: December 5, 2025
**Purpose**: Systematic testing of all features before course demo

---

## How to Use This Checklist

1. Start the servers (if not running):
   - Backend: `cd backend && uvicorn api:app --reload --port 8000`
   - Frontend: `cd frontend && npm run dev`
   - Open: http://localhost:1420

2. Test each section in order
3. Mark items: ✅ Pass | ❌ Fail | ⏭️ Skip | 🔧 Needs Fix

---

## 1. Core Application Launch

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 1.1 | Backend starts | `curl http://localhost:8000/agents` returns agent list | |
| 1.2 | Frontend loads | Open http://localhost:1420 - see 3-panel layout | |
| 1.3 | Ollama connected | `curl http://localhost:11434/api/tags` returns models | |
| 1.4 | No console errors | Browser DevTools → Console (should be clean) | |

---

## 2. File System (Binder Panel - Left)

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 2.1 | File tree loads | See folders: Characters/, Story Bible/, World Bible/ | |
| 2.2 | Expand folders | Click folder → children appear | |
| 2.3 | Select file | Click .md file → opens in editor | |
| 2.4 | File icons | Different icons for folders vs files | |

---

## 3. Editor (Canvas - Center)

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 3.1 | Monaco loads | Editor appears with syntax highlighting | |
| 3.2 | File content | Selected file content displays correctly | |
| 3.3 | Edit text | Type in editor → changes appear | |
| 3.4 | Save file | Cmd+S or save button → file persists | |
| 3.5 | Markdown preview | Toggle preview mode (if available) | |

---

## 4. Foreman Chat (Right Panel)

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 4.1 | Chat input | Type message in input field | |
| 4.2 | Send message | Press Enter or click Send → message appears | |
| 4.3 | Foreman responds | AI response appears (may take a few seconds) | |
| 4.4 | Message history | Previous messages stay visible | |
| 4.5 | Copy to editor | Click copy icon → text goes to editor | |

---

## 5. Settings Panel

### 5.1 Open Settings
| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 5.1.1 | Open modal | Click gear icon in Foreman header | |
| 5.1.2 | Tabs visible | See tabs: General, Agents, Squad, Graph, etc. | |
| 5.1.3 | Close modal | Click X or outside modal | |

### 5.2 General Settings
| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 5.2.1 | Load settings | Settings appear with current values | |
| 5.2.2 | Toggle dark mode | Switch theme toggle | |
| 5.2.3 | Save changes | Click Save → settings persist | |

### 5.3 Agents Tab
| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 5.3.1 | Agent list | See all 17 configured agents | |
| 5.3.2 | Provider groups | Agents grouped by provider | |
| 5.3.3 | Enable/disable | Toggle agent enabled state | |

### 5.4 Squad Tab (Model Orchestrator)
| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 5.4.1 | Roles visible | See Editor, Researcher, Writer, Analyst | |
| 5.4.2 | Model assignment | Each role shows assigned model | |
| 5.4.3 | Change model | Select different model for role | |
| 5.4.4 | Health checks | Health check model config visible | |

### 5.5 Knowledge Graph Tab
| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 5.5.1 | Edge types | See MOTIVATES, HINDERS, CHALLENGES, etc. | |
| 5.5.2 | Toggle edges | Enable/disable edge types | |
| 5.5.3 | Extraction triggers | See on_manuscript_promote, etc. | |
| 5.5.4 | Verification level | Select minimal/standard/thorough | |
| 5.5.5 | Embedding provider | Select ollama/openai/cohere/none | |

---

## 6. Studio Tools Panel

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 6.1 | Open panel | Click Studio Tools in Foreman header | |
| 6.2 | Tabs visible | See available tool tabs | |
| 6.3 | Voice Tournament | Voice calibration interface loads | |
| 6.4 | Scaffold Generator | Scene scaffold tools load | |
| 6.5 | Health Dashboard | Narrative health checks load | |

---

## 7. Graph Viewer Modal

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 7.1 | Open modal | Click Graph icon in Foreman header | |
| 7.2 | Graph renders | See nodes and edges visualization | |
| 7.3 | Node types | Different colors for CHARACTER, LOCATION, etc. | |
| 7.4 | Click node | Node details appear | |
| 7.5 | Zoom/pan | Mouse wheel zoom, drag to pan | |

---

## 8. NotebookLM Integration

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 8.1 | Open panel | Click NotebookLM in Foreman header | |
| 8.2 | Notebooks list | See registered notebooks | |
| 8.3 | Query notebook | Send query → get grounded response | |

---

## 9. Session Management

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 9.1 | Open manager | Click Sessions in Foreman header | |
| 9.2 | Session list | See previous chat sessions | |
| 9.3 | Load session | Click session → history loads | |
| 9.4 | New session | Start new → clears chat | |
| 9.5 | Delete session | Remove old sessions | |

---

## 10. Onboarding Wizard

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 10.1 | First launch | Clear localStorage → wizard appears | |
| 10.2 | Steps work | Navigate through wizard steps | |
| 10.3 | Complete | Finish wizard → main app appears | |
| 10.4 | Skip option | Can skip onboarding | |

---

## 11. GraphRAG Features (NEW)

### 11.1 Semantic Search
| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 11.1.1 | Embedding status | `curl http://localhost:8000/graph/embedding-status` | |
| 11.1.2 | Semantic search | `curl -X POST http://localhost:8000/graph/semantic-search -d '{"query":"character motivation"}'` | |
| 11.1.3 | Knowledge query | `curl -X POST http://localhost:8000/graph/knowledge-query -d '{"query":"What motivates the protagonist?"}'` | |

### 11.2 Narrative Extraction
| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 11.2.1 | Edge types | `curl http://localhost:8000/graph/edge-types` | |
| 11.2.2 | Extract narrative | `curl -X POST http://localhost:8000/graph/extract-narrative -d '{"content":"Scene text here","scene_id":"test"}'` | |
| 11.2.3 | Entities created | Response shows entities and relationships | |

### 11.3 Verification
| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 11.3.1 | Fast verification | `curl -X POST http://localhost:8000/verification/run -d '{"content":"Scene text","tier":"fast"}'` | |
| 11.3.2 | Response time | Fast tier < 500ms | |
| 11.3.3 | Notifications | VerificationNotification appears in UI | |

### 11.4 Analysis
| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 11.4.1 | Tension | `curl http://localhost:8000/graph/analysis/tension` | |
| 11.4.2 | Communities | `curl http://localhost:8000/graph/analysis/communities` | |
| 11.4.3 | Pacing | `curl http://localhost:8000/graph/analysis/pacing` | |
| 11.4.4 | Summary | `curl http://localhost:8000/graph/analysis/summary` | |
| 11.4.5 | Bridge characters | `curl http://localhost:8000/graph/analysis/bridges` | |

---

## 12. Story Bible System

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 12.1 | Status check | `curl http://localhost:8000/story-bible/status` | |
| 12.2 | Required files | Protagonist.md, Beat_Sheet.md, Theme.md exist | |
| 12.3 | Validation | Missing fields reported | |
| 12.4 | Phase gating | Director mode locked until Story Bible complete | |

---

## 13. Voice Calibration

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 13.1 | Tournament start | Start voice tournament | |
| 13.2 | Sample comparison | Compare two voice samples | |
| 13.3 | Winner selection | Select preferred voice | |
| 13.4 | Calibration save | Voice profile saved | |

---

## 14. Director Mode (Scene Creation)

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 14.1 | Scaffold generate | Create scene scaffold | |
| 14.2 | Structure variants | Generate structure options | |
| 14.3 | Scene write | Generate scene from scaffold | |
| 14.4 | Enhancement | Polish/enhance scene | |
| 14.5 | Analysis | Analyze scene quality | |

---

## 15. Model Orchestrator

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 15.1 | Tier routing | `curl http://localhost:8000/orchestrator/route -d '{"task":"scene_generation","tier":"premium"}'` | |
| 15.2 | Model selection | Returns appropriate model for tier | |
| 15.3 | Fallback | Falls back if primary unavailable | |

---

## 16. The Foreman Modes

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 16.1 | ARCHITECT mode | Story Bible building conversations | |
| 16.2 | VOICE mode | Voice calibration assistance | |
| 16.3 | DIRECTOR mode | Scene creation guidance | |
| 16.4 | EDITOR mode | Polish and refinement help | |
| 16.5 | Mode switching | Context updates on mode change | |

---

## 17. API Health & Performance

| # | Test | How to Test | Status |
|---|------|-------------|--------|
| 17.1 | Agent list | `curl http://localhost:8000/agents` | |
| 17.2 | Graph stats | `curl http://localhost:8000/graph/stats` | |
| 17.3 | Settings get | `curl http://localhost:8000/settings/all` | |
| 17.4 | File read | `curl http://localhost:8000/files/read?path=content/Characters/Protagonist.md` | |

---

## Quick Test Commands

```bash
# Backend health
curl http://localhost:8000/agents | python3 -m json.tool | head -20

# Graph stats
curl http://localhost:8000/graph/stats

# Story Bible status
curl http://localhost:8000/story-bible/status

# GraphRAG tension
curl http://localhost:8000/graph/analysis/tension

# Settings
curl http://localhost:8000/settings/all

# Verification
curl -X POST http://localhost:8000/verification/run \
  -H "Content-Type: application/json" \
  -d '{"content": "Test scene content", "tier": "fast"}'

# Narrative extraction
curl -X POST http://localhost:8000/graph/extract-narrative \
  -H "Content-Type: application/json" \
  -d '{"content": "Sarah confronted Mickey about the missing documents.", "scene_id": "test-1"}'
```

---

## Known Issues

| Issue | Status | Notes |
|-------|--------|-------|
| 1147 TypeScript warnings | Known | Pre-existing, doesn't affect runtime |
| Empty graph on first run | Expected | Need to ingest content first |

---

## Test Results Summary

| Section | Pass | Fail | Skip | Total |
|---------|------|------|------|-------|
| 1. Core Launch | | | | 4 |
| 2. File System | | | | 4 |
| 3. Editor | | | | 5 |
| 4. Foreman Chat | | | | 5 |
| 5. Settings | | | | 14 |
| 6. Studio Tools | | | | 5 |
| 7. Graph Viewer | | | | 5 |
| 8. NotebookLM | | | | 3 |
| 9. Sessions | | | | 5 |
| 10. Onboarding | | | | 4 |
| 11. GraphRAG | | | | 13 |
| 12. Story Bible | | | | 4 |
| 13. Voice | | | | 4 |
| 14. Director | | | | 5 |
| 15. Orchestrator | | | | 3 |
| 16. Foreman Modes | | | | 5 |
| 17. API Health | | | | 4 |
| **TOTAL** | | | | **92** |

---

*Last updated: December 5, 2025*
