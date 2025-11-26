# Simplify FileTree (Binder Panel)

**Task**: Remove smart categorization, make it work like VS Code / IDE file explorer
**Date**: 2025-11-26
**Priority**: High
**Estimated Effort**: 1-2 hours

## Problem Statement

The current FileTree tries to be "smart" by automatically categorizing files into:
- "Story Bible" section
- "Manuscript" section
- "World Database" section
- "Other Files" section

**This is confusing and restrictive!**

Writers need a simple, predictable file tree like VS Code, Mac Finder, or Windows Explorer:
- See the actual folder structure
- Click folder → expand/collapse
- Click file → open in editor
- No automatic categorization
- Trust the writer to organize their own files

## Current Implementation

**File**: `frontend/src/lib/components/FileTree.svelte`

**Current Logic** (lines ~106-130):
```javascript
function organizeFiles() {
  storyBible = files.filter(f =>
    f.path.includes('/Story Bible/') ||
    f.name.includes('Story_Bible') ||
    f.name.match(/character|setting|theme/i)
  );

  manuscript = files.filter(f =>
    f.path.includes('/Manuscript/') ||
    f.name.match(/chapter|scene|act/i)
  );

  worldDatabase = files.filter(f =>
    f.path.includes('/World Database/') ||
    f.name.match(/world|location|history/i)
  );

  otherFiles = files.filter(f =>
    !storyBible.includes(f) &&
    !manuscript.includes(f) &&
    !worldDatabase.includes(f)
  );
}
```

**This needs to be completely removed!**

## Target Implementation

### Example: VS Code File Tree

```
📁 my-novel/
├─ 📁 Story Bible/
│  ├─ 📄 characters.md
│  ├─ 📄 world-building.md
│  └─ 📄 themes.md
├─ 📁 Manuscript/
│  ├─ 📁 Act 1/
│  │  ├─ 📄 chapter-01.md
│  │  └─ 📄 chapter-02.md
│  └─ 📁 Act 2/
│     └─ 📄 chapter-03.md
├─ 📄 README.md
└─ 📄 notes.txt
```

**Behavior**:
- Click "📁 Story Bible/" → expands/collapses folder
- Click "📄 characters.md" → opens file in editor
- No special sections, badges, or categorization
- Just a clean hierarchical tree

## Implementation Steps

### Step 1: Remove Categorization Logic

**Delete** these variables (lines ~22-26):
```javascript
// DELETE:
let storyBible = [];
let manuscript = [];
let worldDatabase = [];
let otherFiles = [];
```

**Delete** section collapse state (lines ~28-34):
```javascript
// DELETE:
let expandedSections = {
  storyBible: true,
  manuscript: true,
  worldDatabase: false,
  other: false
};
```

**Delete** `organizeFiles()` function entirely (lines ~106-130)

### Step 2: Restructure File Data

Instead of flat list with categorization, build a proper tree structure:

```javascript
// NEW: Build hierarchical tree from flat file list
function buildFileTree(files, rootPath) {
  const tree = {
    name: rootPath.split('/').pop() || 'Project',
    path: rootPath,
    isDirectory: true,
    children: [],
    expanded: true
  };

  // Group files by parent directory
  const dirMap = new Map();
  dirMap.set(rootPath, tree);

  // Sort files by path depth to process parents before children
  const sorted = [...files].sort((a, b) =>
    a.path.split('/').length - b.path.split('/').length
  );

  for (const file of sorted) {
    const parentPath = file.path.substring(0, file.path.lastIndexOf('/'));
    const parent = dirMap.get(parentPath) || tree;

    const node = {
      name: file.name,
      path: file.path,
      isDirectory: file.isDirectory,
      children: file.isDirectory ? [] : undefined,
      expanded: false
    };

    parent.children.push(node);

    if (file.isDirectory) {
      dirMap.set(file.path, node);
    }
  }

  return tree;
}

// Update loadProject to use tree structure
async function loadProject(path) {
  currentPath = path;
  errorMsg = "";
  localStorage.setItem(STORAGE_KEY, path);

  try {
    const entries = await readDir(path, { recursive: true });
    const flatFiles = flattenEntries(entries, path);
    fileTree = buildFileTree(flatFiles, path); // NEW: tree instead of flat list
  } catch (e) {
    console.error(e);
    errorMsg = "Cannot read folder. Check permissions.";
    fileTree = null;
  }
}
```

### Step 3: Simplify Rendering (Recursive Component)

Replace the sectioned rendering with a simple recursive tree:

```svelte
<script>
  let fileTree = null; // Root of tree

  function toggleFolder(node) {
    node.expanded = !node.expanded;
    fileTree = fileTree; // Trigger reactivity
  }

  async function openFile(node) {
    if (node.isDirectory) {
      toggleFolder(node);
    } else {
      // Load file content
      try {
        const response = await fetch(`http://localhost:8000/files/${encodeURIComponent(node.path)}`);
        if (response.ok) {
          const data = await response.json();
          editorContent.set(data.content);
          activeFile.set(node.path);
        }
      } catch (e) {
        console.error('Failed to load file:', e);
      }
    }
  }
</script>

<!-- Recursive Tree Component -->
{#if fileTree}
  <div class="file-tree">
    <TreeNode node={fileTree} {openFile} {toggleFolder} depth={0} />
  </div>
{/if}

<!-- TreeNode component (recursive) -->
<script context="module">
  export function TreeNode({ node, openFile, toggleFolder, depth }) {
    const indent = depth * 16; // 16px per level

    return `
      <div class="tree-node" style="padding-left: ${indent}px">
        <div
          class="node-label {node.isDirectory ? 'folder' : 'file'} {$activeFile === node.path ? 'active' : ''}"
          on:click={() => openFile(node)}
        >
          {#if node.isDirectory}
            <span class="folder-icon">{node.expanded ? '📂' : '📁'}</span>
          {:else}
            <span class="file-icon">📄</span>
          {/if}
          <span class="node-name">{node.name}</span>
        </div>

        {#if node.isDirectory && node.expanded && node.children?.length}
          {#each node.children as child}
            <svelte:self node={child} {openFile} {toggleFolder} depth={depth + 1} />
          {/each}
        {/if}
      </div>
    `;
  }
</script>
```

### Step 4: Update Styles

Replace sectioned styles with simple tree styles:

```css
.file-tree {
  padding: var(--space-2);
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  color: var(--text-secondary);
}

.tree-node {
  user-select: none;
}

.node-label {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: 4px var(--space-2);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.node-label:hover {
  background: var(--bg-tertiary);
}

.node-label.active {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.folder-icon,
.file-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.node-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Remove all section-specific styles */
/* DELETE: .section-header, .section-title, .section-badge, etc. */
```

## Alternative: Use Existing Library

If building from scratch is too complex, consider using a Svelte tree component library:

**Option 1: svelte-tree-view**
```bash
npm install svelte-tree-view
```

**Option 2: Custom but simpler**
Keep current flat list, but render as indented tree without sections:

```svelte
{#each files as file}
  <div
    class="file-item"
    style="padding-left: {file.depth * 16}px"
    on:click={() => openFile(file)}
  >
    {#if file.isDirectory}
      <span>{file.expanded ? '📂' : '📁'}</span>
    {:else}
      <span>📄</span>
    {/if}
    {file.name}
  </div>
{/each}
```

## Testing Checklist

After implementation, verify:

- [ ] **No automatic categorization** - Files appear in actual folder structure
- [ ] **Folder expand/collapse works** - Click folder toggles children
- [ ] **File selection works** - Click file opens in editor
- [ ] **Indentation shows hierarchy** - Nested folders/files are indented
- [ ] **Active file highlighted** - Currently open file is visually distinct
- [ ] **Performance** - Tree renders quickly with 100+ files
- [ ] **Persistence** - Folder expanded/collapsed state remembered during session
- [ ] **No regressions** - File loading, saving, project switching still work

## Files to Modify

1. **FileTree.svelte** - Complete rewrite of rendering logic
2. Keep `flattenEntries()` for reading filesystem
3. Keep file loading/API integration

## Reference Examples

Check these for inspiration:
- VS Code file explorer (left sidebar)
- Mac Finder in column view
- Windows Explorer tree view
- Tauri file-browser example: https://github.com/tauri-apps/tauri/tree/dev/examples/file-browser

## Questions?

If unclear:
- Test current behavior by clicking files/folders
- Reference VS Code file tree interaction
- Ask for clarification on specific edge cases

The goal: **Simple, predictable, fast file navigation** like every other IDE.
