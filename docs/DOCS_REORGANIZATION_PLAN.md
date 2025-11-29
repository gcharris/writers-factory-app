# Documentation Reorganization Plan

**Created**: 2025-11-27
**Purpose**: Clean up and organize `/docs` folder structure
**Status**: 📋 PLAN - Awaiting approval before execution

---

## 📊 Current State Analysis

### Root Level Files (30+ files)
**Issues:**
- Mix of critical architecture docs with status reports
- Some files are duplicates or superseded
- Status/progress reports scattered
- Reference materials mixed with active docs

### Subfolders Status
- ✅ `/archive` - Well organized (has drafts/ and superseded/)
- ✅ `/dev_logs` - Good organization (chronological)
- ✅ `/specs` - Good organization (by feature)
- ✅ `/claude-skills` - Reference materials (clear purpose)
- ✅ `/tasks` - Task specifications (clear purpose)

---

## 🎯 Proposed Organization

### Keep in Root (Core Active Documentation - 12 files)

**Architecture & Planning:**
1. `ARCHITECTURE.md` - Main architecture spec ✅ KEEP
2. `04_roadmap.md` - Development roadmap ✅ KEEP
3. `WORKFLOWS.md` - User workflows ✅ KEEP
4. `NARRATIVE PROTOCOL.md` - Writing standards ✅ KEEP
5. `manifesto.md` - Project philosophy ✅ KEEP
6. `index.md` - Documentation homepage ✅ KEEP

**Backend Documentation:**
7. `BACKEND_SERVICES.md` - Service layer docs ✅ KEEP
8. `API_REFERENCE.md` - API endpoints ✅ KEEP

**Configuration Guides:**
9. `CONFIGURABLE_MODEL_ASSIGNMENTS.md` - Model config ✅ KEEP
10. `PHASE_3E_QUICK_START.md` - Quick start guide ✅ KEEP

**Documentation Index:**
11. `DOCS_INDEX.md` - Documentation index ✅ KEEP
12. `DOCS_INVENTORY.md` - Documentation inventory ✅ KEEP

---

### Move to `/status` (New Folder - Status & Progress Reports - 6 files)

**Purpose**: Centralize all status, progress, and accomplishment reports

1. `PROJECT_STATUS.md` → `/status/PROJECT_STATUS.md`
2. `RECENT_ACCOMPLISHMENTS.md` → `/status/RECENT_ACCOMPLISHMENTS.md`
3. `CURRENT_UI_ISSUES.md` → `/status/CURRENT_UI_ISSUES.md`
4. `IMPLEMENTATION_REVIEW_REPORT.md` → `/status/IMPLEMENTATION_REVIEW_REPORT.md`
5. `SQUAD_SYSTEM_TEST_REPORT.md` → `/status/SQUAD_SYSTEM_TEST_REPORT.md`
6. `PHASE_3E_TO_3F_MIGRATION_REPORT.md` → `/status/PHASE_3E_TO_3F_MIGRATION_REPORT.md`

---

### Move to `/guides` (New Folder - User & Developer Guides - 8 files)

**Purpose**: User-facing guides and tutorials

1. `SETTINGS_QUICK_START.md` → `/guides/SETTINGS_QUICK_START.md`
2. `SETTINGS_UI_GUIDE.md` → `/guides/SETTINGS_UI_GUIDE.md`
3. `SETTINGS_SYSTEM.md` → `/guides/SETTINGS_SYSTEM.md`
4. `USER_MIGRATION_GUIDE.md` → `/guides/USER_MIGRATION_GUIDE.md`
5. `UI_ARCHITECTURE_TOUR.md` → `/guides/UI_ARCHITECTURE_TOUR.md`
6. `CODEBASE_PIPELINE_WALKTHROUGH.md` → `/guides/CODEBASE_PIPELINE_WALKTHROUGH.md`
7. `TESTING.md` → `/guides/TESTING.md`
8. `BACKEND_TESTING.md` → `/guides/BACKEND_TESTING.md`

---

### Move to `/reference` (New Folder - Reference Materials - 4 files)

**Purpose**: Reference materials that aren't active specs

1. `AI Self-Review Document for Creative Prose.md` → `/reference/AI_SELF_REVIEW.md`
2. `Guidance for Scene-Level Agent Refinement.md` → `/reference/SCENE_AGENT_REFINEMENT.md`
3. `Writer's Factory App - Complete Agent Roster.md` → `/reference/AGENT_ROSTER.md`
4. `CONTRIBUTING.md` → `/reference/CONTRIBUTING.md`

---

### Move to `/archive` (Superseded/Duplicate Files - 3 files)

1. `SYSTEM_ARCHITECTURE_DEEP_DIVE.md` → `/archive/SYSTEM_ARCHITECTURE_DEEP_DIVE.md`
   - **Reason**: Superseded by `ARCHITECTURE.md` (v2.1)

2. `LIVE_SQUAD_ARCHITECTURE.md` → `/archive/LIVE_SQUAD_ARCHITECTURE.md`
   - **Reason**: Superseded by `ARCHITECTURE.md` section on Squad System

3. `SQUAD_ARCHITECTURE_IMPLEMENTATION.md` → `/archive/SQUAD_ARCHITECTURE_IMPLEMENTATION.md`
   - **Reason**: Implementation complete, details now in `ARCHITECTURE.md`

---

### Delete (Accidental/Redundant Files - 2 files)

1. `CNAME` - **DELETE**
   - **Reason**: GitHub Pages config file, shouldn't be in docs

2. `CNAME 2` - **DELETE** (if exists)
   - **Reason**: Duplicate/accidental file

---

## 📁 Final Structure

```
/docs
├── ROOT (12 files) - Core active documentation
│   ├── ARCHITECTURE.md
│   ├── 04_roadmap.md
│   ├── WORKFLOWS.md
│   ├── NARRATIVE PROTOCOL.md
│   ├── manifesto.md
│   ├── index.md
│   ├── BACKEND_SERVICES.md
│   ├── API_REFERENCE.md
│   ├── CONFIGURABLE_MODEL_ASSIGNMENTS.md
│   ├── PHASE_3E_QUICK_START.md
│   ├── DOCS_INDEX.md
│   └── DOCS_INVENTORY.md
│
├── /status (6 files) - Status & progress reports
│   ├── PROJECT_STATUS.md
│   ├── RECENT_ACCOMPLISHMENTS.md
│   ├── CURRENT_UI_ISSUES.md
│   ├── IMPLEMENTATION_REVIEW_REPORT.md
│   ├── SQUAD_SYSTEM_TEST_REPORT.md
│   └── PHASE_3E_TO_3F_MIGRATION_REPORT.md
│
├── /guides (8 files) - User & developer guides
│   ├── SETTINGS_QUICK_START.md
│   ├── SETTINGS_UI_GUIDE.md
│   ├── SETTINGS_SYSTEM.md
│   ├── USER_MIGRATION_GUIDE.md
│   ├── UI_ARCHITECTURE_TOUR.md
│   ├── CODEBASE_PIPELINE_WALKTHROUGH.md
│   ├── TESTING.md
│   └── BACKEND_TESTING.md
│
├── /reference (4 files) - Reference materials
│   ├── AI_SELF_REVIEW.md
│   ├── SCENE_AGENT_REFINEMENT.md
│   ├── AGENT_ROSTER.md
│   └── CONTRIBUTING.md
│
├── /archive (existing + 3 new) - Historical docs
│   ├── /drafts
│   ├── /superseded
│   └── (3 new files moved here)
│
├── /dev_logs (existing) - Implementation logs ✅ NO CHANGES
├── /specs (existing) - Technical specifications ✅ NO CHANGES
├── /claude-skills (existing) - Reference skills ✅ NO CHANGES
└── /tasks (existing) - Task specifications ✅ NO CHANGES
```

---

## ✅ Benefits

1. **Cleaner Root**: Only 12 core files (down from 30+)
2. **Better Organization**: Status reports, guides, and references grouped logically
3. **Easier Navigation**: Clear purpose for each folder
4. **Maintained History**: All files preserved, just reorganized
5. **No Breaking Changes**: All content remains accessible

---

## 📋 Execution Steps

### Phase 1: Create New Folders
1. Create `/docs/status/` folder
2. Create `/docs/guides/` folder
3. Create `/docs/reference/` folder

### Phase 2: Move Files
1. Move 6 status files → `/status/`
2. Move 8 guide files → `/guides/`
3. Move 4 reference files → `/reference/`
4. Move 3 archive files → `/archive/`

### Phase 3: Clean Up
1. Delete `CNAME` and `CNAME 2` (if exists)
2. Rename files with spaces to underscores in `/reference/`:
   - `AI Self-Review Document for Creative Prose.md` → `AI_SELF_REVIEW.md`
   - `Guidance for Scene-Level Agent Refinement.md` → `SCENE_AGENT_REFINEMENT.md`
   - `Writer's Factory App - Complete Agent Roster.md` → `AGENT_ROSTER.md`

### Phase 4: Update Index Files
1. Update `DOCS_INDEX.md` with new structure
2. Create `/status/README.md` explaining status folder
3. Create `/guides/README.md` explaining guides folder
4. Create `/reference/README.md` explaining reference folder

### Phase 5: Update Cross-References
1. Search for broken links in moved files
2. Update any hardcoded paths in documentation
3. Verify `index.md` links still work

---

## ⚠️ Considerations

1. **Git History**: Moving files preserves history, but may break some links
2. **Cross-References**: Need to update any hardcoded paths
3. **External Links**: If docs are linked externally, may need redirects
4. **Search**: Some tools may need re-indexing

---

## 🎯 Approval Required

**Before executing:**
- ✅ Review this plan
- ✅ Confirm file categorizations
- ✅ Approve folder structure
- ✅ Confirm file renames

**After approval:**
- Execute phases 1-5
- Test all links
- Update `DOCS_INDEX.md`
- Commit changes

---

**Status**: 📋 PLAN - Awaiting approval
**Next Step**: Review and approve before execution

