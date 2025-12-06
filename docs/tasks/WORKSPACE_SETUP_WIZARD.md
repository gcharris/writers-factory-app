# Task: Workspace Location Setup (Onboarding Step 0)

## Overview
Add a new **Step 0** to the onboarding wizard where users choose where to store their writing projects. This runs BEFORE the existing Local AI step.

## Why This Matters
- Users should know where their writing is stored (not hidden in app data)
- Supports cloud sync (Dropbox, iCloud, Google Drive)
- Enables multiple projects on the same machine
- Professional workflow expectation

---

## Current State

### Existing Files (DO NOT create duplicates)
```
frontend/src/lib/components/Onboarding/
├── OnboardingWizard.svelte     ← MODIFY THIS (add Step 0, change totalSteps to 4)
├── Step1LocalAI.svelte         ← Reference for component pattern
├── Step2CloudModels.svelte     ← Reference for styling
└── Step3NameAssistant.svelte   ← Reference for completion event
```

### Existing Onboarding Flow
1. Step 1: Local AI Setup (Ollama + llama3.2:3b)
2. Step 2: Cloud Models (API key configuration)
3. Step 3: Name Your Assistant

### New Onboarding Flow (After This Task)
1. **Step 1: Workspace Location** ← NEW (was Step 0 conceptually, but render as Step 1)
2. Step 2: Local AI Setup
3. Step 3: Cloud Models
4. Step 4: Name Your Assistant

---

## Requirements

### Part 1: New Component - Step1WorkspaceLocation.svelte

**File Location**: `frontend/src/lib/components/Onboarding/Step1WorkspaceLocation.svelte`

**UI Elements**:
1. **Title**: "Where should we store your writing projects?"
2. **Subtitle**: "Choose a folder on your computer. You can use cloud-synced folders like Dropbox or iCloud."
3. **Current Selection Display**: Show the selected path (or "No folder selected")
4. **Browse Button**: Opens native folder picker dialog
5. **Default Suggestion**: Button to use `~/Documents/Writers Factory/`
6. **Next Button**: Enabled only when a valid folder is selected

**Behavior**:
- On mount: Check if `workspacePath` store already has a value (returning user)
- Browse button: Use Tauri's dialog plugin to open folder picker
- Validate selected folder is writable
- Dispatch `complete` event with selected path
- Dispatch `next` event to advance wizard

**Tauri Dialog Usage** (plugin already installed):
```typescript
import { open } from '@tauri-apps/plugin-dialog';

async function browseFolder() {
  const selected = await open({
    directory: true,
    multiple: false,
    title: 'Choose Writers Factory Folder'
  });

  if (selected) {
    selectedPath = selected as string;
  }
}
```

**Events to dispatch**:
- `on:complete` with `{ path: string }` when folder is selected
- `on:next` to advance to next step

### Part 2: Modify OnboardingWizard.svelte

**File**: `frontend/src/lib/components/Onboarding/OnboardingWizard.svelte`

**Changes Required**:

1. **Import the new component** (line ~16):
```typescript
import Step1WorkspaceLocation from './Step1WorkspaceLocation.svelte';
```

2. **Rename existing imports** - DO NOT rename files, just update step numbers in logic:
   - Existing Step1LocalAI becomes rendered at step 2
   - Existing Step2CloudModels becomes rendered at step 3
   - Existing Step3NameAssistant becomes rendered at step 4

3. **Update totalSteps** (line 22):
```typescript
const totalSteps = 4;  // Was 3
```

4. **Add step completion tracking** (line ~25):
```typescript
let step0Complete = false;  // Workspace location
let step1Complete = false;  // Local AI
let step2Complete = true;   // Cloud models (always completable)
let step3Complete = false;  // Name assistant
```

5. **Update progress bar** to show 4 steps with labels:
   - Step 1: "Workspace"
   - Step 2: "Local AI"
   - Step 3: "Cloud Models"
   - Step 4: "Name Assistant"

6. **Update step content rendering**:
```svelte
{#if currentStep === 1}
  <Step1WorkspaceLocation
    on:complete={handleStep0Complete}
    on:next={nextStep}
  />
{:else if currentStep === 2}
  <Step1LocalAI
    on:complete={handleStep1Complete}
    on:next={nextStep}
    on:back={prevStep}
  />
{:else if currentStep === 3}
  <Step2CloudModels
    on:back={prevStep}
    on:next={nextStep}
  />
{:else if currentStep === 4}
  <Step3NameAssistant
    on:back={prevStep}
    on:complete={handleStep3Complete}
  />
{/if}
```

7. **Add handler for workspace step**:
```typescript
function handleStep0Complete(event: CustomEvent<{ path: string }>) {
  step0Complete = true;
  workspacePath.set(event.detail.path);
}
```

8. **Import workspacePath store**:
```typescript
import { workspacePath } from '$lib/stores';
```

### Part 3: Update stores.js

**File**: `frontend/src/lib/stores.js`

**Add after line 60** (after `hasCompletedOnboarding`):
```javascript
// --- Workspace State ---
// User-selected location for all writing projects
export const workspacePath = persistentWritable('wf_workspace_path', null);

// Currently active project within the workspace
export const activeProjectName = persistentWritable('wf_active_project', null);
```

### Part 4: Backend Endpoint (Optional but Recommended)

**File**: `backend/api.py`

Add endpoint to create workspace folder structure:

```python
class WorkspaceInitRequest(BaseModel):
    path: str
    project_name: str = "my-project"

@app.post("/workspace/init")
async def init_workspace(request: WorkspaceInitRequest):
    """Initialize workspace with project folder structure."""
    import os

    base_path = request.path
    project_path = os.path.join(base_path, "projects", request.project_name, "content")

    folders = [
        os.path.join(project_path, "Characters"),
        os.path.join(project_path, "Story Bible", "Structure"),
        os.path.join(project_path, "Story Bible", "Themes_and_Philosophy"),
        os.path.join(project_path, "World Bible"),
    ]

    try:
        for folder in folders:
            os.makedirs(folder, exist_ok=True)

        return {
            "success": True,
            "workspace_path": base_path,
            "project_path": project_path,
            "folders_created": len(folders)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workspace/status")
async def get_workspace_status(path: str = Query(...)):
    """Check if workspace path exists and is writable."""
    import os

    exists = os.path.exists(path)
    is_dir = os.path.isdir(path) if exists else False
    writable = os.access(path, os.W_OK) if exists else False

    # Check for existing projects
    projects = []
    projects_dir = os.path.join(path, "projects")
    if os.path.exists(projects_dir):
        projects = [d for d in os.listdir(projects_dir)
                   if os.path.isdir(os.path.join(projects_dir, d))]

    return {
        "exists": exists,
        "is_directory": is_dir,
        "writable": writable,
        "projects": projects
    }
```

---

## Visual Design

Match existing onboarding style (dark theme, cyan accent). Reference `Step2CloudModels.svelte` for:
- Card/panel styling
- Button styles (`.btn-primary`, `.btn-secondary`)
- Icon usage
- Responsive layout

**Layout suggestion**:
```
┌─────────────────────────────────────────────────────────────┐
│  📁  Where should we store your writing projects?           │
│                                                             │
│  Choose a folder on your computer. You can use cloud-synced │
│  folders like Dropbox or iCloud.                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ~/Documents/Writers Factory                         │   │
│  │  ✓ Folder exists and is writable                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [ Browse... ]    [ Use Default: ~/Documents/Writers Factory ]│
│                                                             │
│                                          [ Next → ]         │
└─────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

- [x] New Step1WorkspaceLocation.svelte component created
- [x] OnboardingWizard.svelte updated to 4 steps
- [x] Progress bar shows all 4 steps with correct labels
- [x] Tauri folder picker dialog works
- [x] Selected path displayed in UI
- [x] "Use Default" button sets `~/Documents/Writers Factory/`
- [x] Next button disabled until folder selected
- [x] workspacePath store persists selection to localStorage
- [x] Backend /workspace/init endpoint creates folder structure
- [x] Existing Step1/2/3 components still work (no regressions)
- [x] `npm run check` passes with no TypeScript errors

**STATUS: COMPLETE** (Implemented December 2024)

---

## Testing Steps

1. Clear localStorage (`localStorage.clear()` in console)
2. Restart app - should show onboarding
3. Step 1 should now be "Workspace" (not "Local AI")
4. Click Browse, select a folder
5. Click Next - should advance to Local AI step
6. Complete remaining steps
7. Verify workspace path persisted in localStorage

---

## Files Summary

| Action | File |
|--------|------|
| CREATE | `frontend/src/lib/components/Onboarding/Step1WorkspaceLocation.svelte` |
| MODIFY | `frontend/src/lib/components/Onboarding/OnboardingWizard.svelte` |
| MODIFY | `frontend/src/lib/stores.js` |
| MODIFY | `backend/api.py` (add 2 endpoints) |

---

## Common Mistakes to Avoid

1. **DO NOT rename existing Step files** - just change where they render in the wizard
2. **DO NOT create ChatInput.svelte** - this file doesn't exist in this project
3. **Match existing event patterns** - use `createEventDispatcher` like other steps
4. **Use Tauri plugin-dialog** - it's already installed (`@tauri-apps/plugin-dialog`)
5. **Import from correct paths** - stores are in `$lib/stores`, not `$lib/stores.js`
6. **Test in Tauri** - dialog won't work in browser-only mode

---

## Reference Code

### Event Dispatcher Pattern (from Step1LocalAI.svelte)
```typescript
import { createEventDispatcher } from 'svelte';
const dispatch = createEventDispatcher();

// Dispatch completion
dispatch('complete', { complete: true });

// Dispatch navigation
dispatch('next');
```

### persistentWritable Pattern (from stores.js)
```javascript
export const workspacePath = persistentWritable('wf_workspace_path', null);
```

---

## Priority
**High** - This is the first thing users see and sets up their entire workflow.
