# Session Manager Redesign

**Status**: Ready for Implementation
**Priority**: High
**Component**: `frontend/src/lib/components/SessionManagerModal.svelte`
**Backend Impact**: Yes - new endpoints required

---

## Problem Statement

The current Session Manager is unusable because:

1. **Hex IDs instead of meaningful names**: Sessions display as `abc12345...` which tells users nothing about the conversation content
2. **No session naming**: Users cannot give sessions descriptive names like "Chapter 3 planning" or "Mickey character development"
3. **Poor preview**: Only shows truncated messages, no overview or summary
4. **No search by content**: Can only search by session ID or scene ID - useless for finding past conversations
5. **Missing session snippets**: No quick preview of what was discussed

---

## Required Changes

### 1. Auto-Generated Session Names (Backend + Frontend)

**Backend changes** (`backend/api.py` and `backend/services/session_service.py`):

Add a `name` field to sessions that auto-generates from:
- First user message (truncated to ~50 chars)
- Or: LLM-generated summary (one-line description of conversation)

```python
# New endpoint needed
POST /session/{session_id}/rename
{
    "name": "Chapter 3 - Mickey meets the Chairman"
}

# Modified response for /sessions/active
{
    "sessions": [
        {
            "session_id": "abc123...",
            "name": "Chapter 3 - Mickey meets Chairman",  # NEW
            "preview": "We discussed Mickey's motivations...",  # NEW
            "scene_id": "optional",
            "event_count": 15,
            "last_activity": "2024-11-29T..."
        }
    ]
}
```

**Database schema change** (SQLite):
```sql
ALTER TABLE sessions ADD COLUMN name TEXT;
ALTER TABLE sessions ADD COLUMN preview TEXT;  -- First ~200 chars of conversation
```

### 2. Frontend Session List Redesign

Replace current display:
```
abc12345...
Scene: chapter-3
15 msgs | 2h ago
```

With:
```
Chapter 3 - Mickey meets Chairman    ✏️
"We discussed Mickey's motivations and how he would approach..."
15 messages | 2 hours ago
```

**Component changes**:
- Show `name` prominently (editable via pencil icon)
- Show `preview` text below name
- Keep message count and relative time
- Remove hex ID from main display (show in tooltip or detail view only)

### 3. Session Rename UI

Add inline rename capability:
- Click pencil icon next to session name
- Transforms to input field
- Enter to save, Escape to cancel
- Calls `POST /session/{id}/rename`

### 4. Improved Search

Current search only matches session_id and scene_id.

Enhanced search should match:
- Session name
- Preview text
- Optionally: full message content (backend search)

```javascript
// Update filter function
$: filteredSessions = sessions.filter(s => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
        s.name?.toLowerCase().includes(q) ||
        s.preview?.toLowerCase().includes(q) ||
        s.scene_id?.toLowerCase().includes(q)
    );
});
```

### 5. Better Preview Panel

Current: Shows list of truncated messages.

Improved:
- **Header**: Full session name (editable), creation date, last activity
- **Summary**: Auto-generated or first message excerpt
- **Key Topics**: Tags/keywords extracted from conversation (future)
- **Messages**: Scrollable list with better formatting

### 6. Session Grouping (Future Enhancement)

Group sessions by:
- Today / Yesterday / This Week / Older
- Or by project/scene

---

## Implementation Tasks

### Phase 1: Backend Updates (Required First)

- [ ] Add `name` and `preview` columns to sessions table
- [ ] Update `SessionService` to auto-generate names from first user message
- [ ] Add `POST /session/{id}/rename` endpoint
- [ ] Update `/sessions/active` response to include name and preview
- [ ] Backfill existing sessions (generate names from stored messages)

### Phase 2: Frontend Updates

- [ ] Update `SessionManagerModal.svelte` to display session names
- [ ] Add inline rename functionality (pencil icon → input field)
- [ ] Update search to filter by name and preview
- [ ] Improve preview panel layout
- [ ] Add tooltip with full session ID for debugging

### Phase 3: Polish

- [ ] Add loading states for rename operation
- [ ] Add error handling for rename failures
- [ ] Test with 50+ sessions for performance
- [ ] Add keyboard navigation (arrow keys to select sessions)

---

## Files to Modify

### Backend
- `backend/services/session_service.py` - Add name/preview fields, auto-generation
- `backend/api.py` - Add rename endpoint, update list response
- Database migration (inline or alembic)

### Frontend
- `frontend/src/lib/components/SessionManagerModal.svelte` - Main redesign
- `frontend/src/lib/api_client.ts` - Add rename API method

---

## UI Mockup (ASCII)

```
┌─────────────────────────────────────────────────────────────────────┐
│  💬 Session Manager                                      X Close    │
│     42 sessions                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  [🔍 Search sessions...        ] [Sort: Recent ▼]                   │
├────────────────────────┬────────────────────────────────────────────┤
│                        │                                            │
│  Chapter 3 Planning ✏️ │  Chapter 3 Planning                        │
│  "We discussed Mickey" │  ──────────────────                        │
│  15 msgs | 2h ago      │  Created: Nov 29, 2024 2:30 PM             │
│  ────────────────────  │  Last Activity: 2 hours ago                │
│                        │  Messages: 15                              │
│  Voice Calibration ✏️  │                                            │
│  "Running tournament"  │  Preview:                                  │
│  8 msgs | Yesterday    │  "We discussed Mickey's motivations        │
│  ────────────────────  │  and how he would approach the Chairman    │
│                        │  meeting. Key decision: Mickey will..."    │
│  World Building ✏️     │                                            │
│  "Q-space rules and"   │  ┌─────────────────────────────────────┐   │
│  23 msgs | 3 days ago  │  │ YOU: I need help planning chapter 3 │   │
│                        │  │                                     │   │
│                        │  │ FOREMAN: I'd be happy to help...    │   │
│                        │  │                                     │   │
│                        │  │ YOU: Let's focus on Mickey          │   │
│                        │  └─────────────────────────────────────┘   │
│                        │                                            │
│                        │  [ 📥 Export ▼ ] [ 🗑️ Delete ]              │
│                        │                                            │
│                        │  [        Load into Chat        ]          │
├────────────────────────┴────────────────────────────────────────────┤
```

---

## Acceptance Criteria

1. Sessions display meaningful names, not hex IDs
2. Users can rename any session with inline editing
3. Search finds sessions by name and preview content
4. Preview pane shows useful overview before loading
5. Existing sessions get auto-generated names on first load

---

## Notes for Implementing Agent

- Read `backend/services/session_service.py` first to understand current data model
- The SQLite schema is defined in `backend/graph/schema.py`
- Test with existing sessions - ensure backward compatibility
- Keep hex ID available (tooltip, debug mode) for technical troubleshooting
- Name generation: prefer first user message truncated to 50 chars, strip common prefixes like "Help me with" or "I need to"

---

*Created: November 29, 2024*
