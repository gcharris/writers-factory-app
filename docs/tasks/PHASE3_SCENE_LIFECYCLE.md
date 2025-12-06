# Phase 3: Scene Lifecycle

> Track scene status from draft to complete.

## Scene States

```
DRAFT → IN_REVIEW → COMPLETE → LOCKED
```

| State | Location | Editable | Ingested to KG |
|-------|----------|----------|----------------|
| Draft | `workspace/drafts/` | Yes | No |
| In Review | `workspace/drafts/` | Yes | No |
| Complete | `manuscript/` | Yes (tracked) | Yes |
| Locked | `manuscript/` | No | Yes |

---

## Implementation Tasks

### 1. Scene Status Frontmatter

All scene files include:

```yaml
---
title: "Chapter 1: The Opening"
scene_id: ch01_opening
status: draft  # draft | in_review | complete | locked
beat: opening_image  # Link to Beat Sheet
created: 2024-12-06
modified: 2024-12-06
word_count: 1247
---
```

### 2. Status Transition Service

**New file**: `backend/services/scene_lifecycle_service.py`

```python
class SceneLifecycleService:
    async def mark_for_review(self, scene_path: str) -> bool:
        """Move scene to IN_REVIEW status."""

    async def mark_complete(self, scene_path: str) -> bool:
        """
        Move scene to COMPLETE status.
        - Update frontmatter
        - Move file from workspace/drafts/ to manuscript/
        - Trigger Knowledge Graph ingestion
        """

    async def lock_scene(self, scene_path: str) -> bool:
        """Make scene read-only."""

    async def unlock_scene(self, scene_path: str) -> bool:
        """Return locked scene to complete (editable)."""
```

### 3. File Tree Status Badges

**Modify**: `FileTree.svelte`

Show status indicators:
- 📝 Draft (default icon)
- 🔍 In Review (magnifying glass)
- ✅ Complete (checkmark)
- 🔒 Locked (padlock)

### 4. Context Menu Actions

Right-click on scene file:
- "Mark for Review" (draft → in_review)
- "Mark Complete" (in_review → complete)
- "Lock Scene" (complete → locked)
- "Unlock Scene" (locked → complete)

### 5. Move to Manuscript

When status → COMPLETE:
1. Move file from `workspace/drafts/ch01.md` to `manuscript/Part_1/ch01.md`
2. Update any internal links
3. Trigger Knowledge Graph ingestion for continuity tracking

### 6. Foreman Review Integration

When status = IN_REVIEW, Foreman can:
- Analyze for voice consistency
- Check beat alignment
- Flag continuity issues

This integrates with existing Director Mode analysis services.

---

## API Endpoints

```python
# Get scene status
GET /scene/{scene_id}/status

# Update scene status
POST /scene/{scene_id}/status
Request: { status: "in_review" | "complete" | "locked" }

# List scenes by status
GET /scenes?status=draft
GET /scenes?status=in_review

# Foreman review
POST /scene/{scene_id}/review
Response: { voice_score, beat_alignment, continuity_issues }
```

---

## Directory Structure After Implementation

```
workspace/
└── drafts/
    ├── ch01_opening.md       # status: draft
    └── ch02_inciting.md      # status: in_review

manuscript/
├── Part_1/
│   └── ch03_catalyst.md      # status: complete
└── Part_2/
    └── ch10_climax.md        # status: locked
```

---

## Testing

1. Create new scene in workspace/drafts/
2. Mark for review → verify badge updates
3. Mark complete → verify file moves to manuscript/
4. Verify Knowledge Graph updated with scene entities
5. Lock scene → verify read-only in editor
6. Unlock → verify editable again

---

## Acceptance Criteria

- [ ] Scene frontmatter includes status field
- [ ] Status badges display in File Tree
- [ ] Context menu actions for status transitions
- [ ] Complete scenes move to manuscript/
- [ ] Locked scenes are read-only in editor
- [ ] Knowledge Graph ingests complete scenes

---

## Dependencies

- **Phase 1 must be complete** (file-based approach)

---

*Parent spec: [WORKSPACE_FILE_SYSTEM.md](./WORKSPACE_FILE_SYSTEM.md)*
*Priority: MEDIUM - Workflow improvement*
