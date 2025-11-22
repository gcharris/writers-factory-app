# File Synchronization Specification

**Version**: 1.0
**Status**: Draft
**Related**: ARCHITECTURE.md, Knowledge Graph

---

## Problem Statement

The Knowledge Graph is the "source of truth" for the Writers Factory. However, writers may edit markdown files using external editors (VS Code, Obsidian, etc.). When this happens, the graph becomes stale and out of sync with the actual content.

The system must:
1. Detect external file modifications
2. Trigger re-ingestion of changed files
3. Update the graph without losing chat-derived knowledge
4. Handle conflicts between graph state and file state

---

## Architecture

### File Watcher Service

```
┌─────────────────────────────────────────────────────────┐
│                    FILE WATCHER SERVICE                  │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   Watchdog   │───▶│  Event Queue │───▶│  Debouncer│ │
│  │   Observer   │    │              │    │  (500ms)  │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│                                                 │        │
│                                                 ▼        │
│                                          ┌───────────┐  │
│                                          │ Dispatcher│  │
│                                          └───────────┘  │
│                                                 │        │
│         ┌───────────────────┬──────────────────┤        │
│         ▼                   ▼                  ▼        │
│  ┌────────────┐     ┌────────────┐     ┌───────────┐   │
│  │ Story Bible│     │ Manuscript │     │   World   │   │
│  │  Handler   │     │  Handler   │     │  Handler  │   │
│  └────────────┘     └────────────┘     └───────────┘   │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Knowledge Graph │
                    │   Re-Ingestor   │
                    └─────────────────┘
```

---

## Implementation

### 1. Watchdog Observer (Python)

```python
# backend/services/file_watcher_service.py
import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

class ContentFileHandler(FileSystemEventHandler):
    """Handles file system events for content directory."""

    def __init__(self, event_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        self.event_queue = event_queue
        self.loop = loop
        self.watched_extensions = {'.md', '.markdown'}

    def on_modified(self, event):
        if self._should_process(event):
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(('modified', event.src_path)),
                self.loop
            )

    def on_created(self, event):
        if self._should_process(event):
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(('created', event.src_path)),
                self.loop
            )

    def on_deleted(self, event):
        if self._should_process(event):
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(('deleted', event.src_path)),
                self.loop
            )

    def _should_process(self, event) -> bool:
        if event.is_directory:
            return False
        path = Path(event.src_path)
        return path.suffix.lower() in self.watched_extensions


class FileWatcherService:
    """
    Watches content directory for changes and triggers graph updates.

    Uses debouncing to avoid rapid-fire re-ingestion during saves.
    """

    def __init__(self, content_path: Path, ingestor):
        self.content_path = content_path
        self.ingestor = ingestor
        self.event_queue = asyncio.Queue()
        self.pending_files = {}  # path -> timestamp
        self.debounce_delay = 0.5  # 500ms
        self.observer = None

    async def start(self):
        """Start watching for file changes."""
        loop = asyncio.get_event_loop()
        handler = ContentFileHandler(self.event_queue, loop)

        self.observer = Observer()
        self.observer.schedule(handler, str(self.content_path), recursive=True)
        self.observer.start()

        # Start event processor
        asyncio.create_task(self._process_events())

    async def stop(self):
        """Stop watching."""
        if self.observer:
            self.observer.stop()
            self.observer.join()

    async def _process_events(self):
        """Process file events with debouncing."""
        while True:
            try:
                event_type, file_path = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=0.1
                )
                self.pending_files[file_path] = asyncio.get_event_loop().time()
            except asyncio.TimeoutError:
                pass

            # Process debounced files
            await self._flush_pending()

    async def _flush_pending(self):
        """Process files that have passed debounce window."""
        now = asyncio.get_event_loop().time()
        ready = []

        for path, timestamp in list(self.pending_files.items()):
            if now - timestamp >= self.debounce_delay:
                ready.append(path)
                del self.pending_files[path]

        for path in ready:
            await self._handle_file_change(path)

    async def _handle_file_change(self, file_path: str):
        """Route file change to appropriate handler."""
        path = Path(file_path)
        relative = path.relative_to(self.content_path)

        # Determine file category
        category = self._categorize_file(relative)

        if category == 'story_bible':
            await self._reingest_story_bible_file(path)
        elif category == 'manuscript':
            await self._reingest_manuscript_file(path)
        elif category == 'world':
            await self._reingest_world_file(path)

    def _categorize_file(self, relative_path: Path) -> str:
        """Categorize file by its location in content hierarchy."""
        parts = relative_path.parts

        if len(parts) > 0:
            first = parts[0].lower()
            if first in ('story bible', 'story_bible'):
                return 'story_bible'
            elif first in ('characters',):
                return 'story_bible'
            elif first in ('structure',):
                return 'story_bible'
            elif first in ('world', 'world bible', 'world_bible'):
                return 'world'
            elif first.startswith('act') or parts[0][0].isdigit():
                return 'manuscript'

        return 'manuscript'  # Default

    async def _reingest_story_bible_file(self, path: Path):
        """Re-ingest a Story Bible file."""
        logger.info(f"Re-ingesting Story Bible file: {path.name}")
        await self.ingestor.ingest_file(path, source_type='story_bible')

    async def _reingest_manuscript_file(self, path: Path):
        """Re-ingest a manuscript/scene file."""
        logger.info(f"Re-ingesting manuscript file: {path.name}")
        await self.ingestor.ingest_file(path, source_type='manuscript')

    async def _reingest_world_file(self, path: Path):
        """Re-ingest a world-building file."""
        logger.info(f"Re-ingesting world file: {path.name}")
        await self.ingestor.ingest_file(path, source_type='world')
```

### 2. Incremental Re-Ingestion

```python
# backend/services/incremental_ingestor.py

class IncrementalIngestor:
    """
    Re-ingests individual files without rebuilding entire graph.

    Key principle: Nodes from file ingestion are tagged with source_file.
    On re-ingestion, we remove old nodes from that file, then add new ones.
    """

    def __init__(self, graph_path: Path, ollama_url: str):
        self.graph_path = graph_path
        self.ollama_url = ollama_url

    async def ingest_file(self, file_path: Path, source_type: str):
        """
        Re-ingest a single file.

        1. Extract entities from file content
        2. Remove existing nodes sourced from this file
        3. Add new nodes with source_file tag
        4. Preserve edges where possible
        """
        # Read file
        content = file_path.read_text(encoding='utf-8')

        # Extract entities
        extracted = await self._extract_entities(content, source_type)

        # Update graph
        with locked_file(self.graph_path, 'r+') as f:
            graph = json.load(f)

            # Remove old nodes from this file
            source_file_str = str(file_path)
            graph['nodes'] = [
                n for n in graph['nodes']
                if n.get('source_file') != source_file_str
            ]

            # Add new nodes with source tracking
            for node in extracted.get('nodes', []):
                node['source_file'] = source_file_str
                node['ingested_at'] = datetime.now(timezone.utc).isoformat()
                graph['nodes'].append(node)

            # Add new edges
            existing_edge_sigs = {
                (e['source'], e['target'], e['relation'])
                for e in graph['edges']
            }
            for edge in extracted.get('edges', []):
                sig = (edge['source'], edge['target'], edge['relation'])
                if sig not in existing_edge_sigs:
                    graph['edges'].append(edge)

            # Save
            f.seek(0)
            f.truncate()
            json.dump(graph, f, indent=2)

        return {
            'status': 'success',
            'file': str(file_path),
            'nodes_added': len(extracted.get('nodes', [])),
            'edges_added': len(extracted.get('edges', []))
        }
```

---

## Tauri Integration (Frontend)

For the desktop app, Tauri provides native file watching that's more efficient than polling:

```rust
// src-tauri/src/file_watcher.rs
use notify::{Watcher, RecursiveMode, watcher};
use std::sync::mpsc::channel;

#[tauri::command]
pub fn start_file_watcher(content_path: String) -> Result<(), String> {
    let (tx, rx) = channel();
    let mut watcher = watcher(tx, Duration::from_millis(500))
        .map_err(|e| e.to_string())?;

    watcher.watch(&content_path, RecursiveMode::Recursive)
        .map_err(|e| e.to_string())?;

    // Emit events to frontend
    std::thread::spawn(move || {
        loop {
            match rx.recv() {
                Ok(event) => {
                    // Send to frontend via Tauri event
                    app_handle.emit_all("file-changed", event);
                }
                Err(e) => break,
            }
        }
    });

    Ok(())
}
```

---

## Conflict Resolution

### Scenario: Graph has chat-derived knowledge, file changes

```
Graph State:
  - Node: "Mickey" (from chat: "Mickey is afraid of heights")
  - Node: "Mickey" (from file: "Mickey is a pilot")

File Changes:
  - Mickey_Character.md updated: "Mickey overcame her fear of heights"
```

### Resolution Strategy

1. **Chat-derived nodes are preserved** - Never delete nodes from chat sessions
2. **File-derived nodes are replaced** - On re-ingestion, old file nodes are removed
3. **Conflicts are flagged** - If file and chat disagree, log to `graph_conflicts.json`

```python
def _detect_conflicts(self, existing_nodes, new_nodes, source_file):
    """Detect potential conflicts between file and chat-derived knowledge."""
    conflicts = []

    file_node_ids = {n['id'] for n in new_nodes}

    for existing in existing_nodes:
        if existing['id'] in file_node_ids:
            # Same entity exists
            if existing.get('source_file') is None:
                # Existing is chat-derived, new is file-derived
                new_node = next(n for n in new_nodes if n['id'] == existing['id'])
                if existing.get('desc', '').lower() != new_node.get('desc', '').lower():
                    conflicts.append({
                        'node_id': existing['id'],
                        'chat_desc': existing.get('desc'),
                        'file_desc': new_node.get('desc'),
                        'source_file': source_file,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

    return conflicts
```

---

## API Endpoints

```python
# In api.py

@app.post("/files/resync")
async def resync_file(file_path: str):
    """Manually trigger re-ingestion of a file."""
    ingestor = get_incremental_ingestor()
    result = await ingestor.ingest_file(Path(file_path))
    return result

@app.post("/files/resync-all")
async def resync_all():
    """Re-ingest all content files."""
    # Full re-ingestion
    ingestor = GraphIngestor()
    result = await ingestor.run_ingestion()
    return result

@app.get("/files/watch-status")
async def get_watch_status():
    """Get file watcher status."""
    return {
        "watching": file_watcher.is_running(),
        "content_path": str(file_watcher.content_path),
        "pending_files": len(file_watcher.pending_files)
    }
```

---

## Configuration

```yaml
# config/file_sync.yaml
file_watcher:
  enabled: true
  debounce_ms: 500
  watched_extensions:
    - .md
    - .markdown
  ignored_patterns:
    - ".*"        # Hidden files
    - "_*"        # Temp files
    - "*.tmp"

  # Paths relative to content/
  watched_directories:
    - "Story Bible"
    - "Characters"
    - "Structure"
    - "World"
    - "Act *"
```

---

## Testing Strategy

### Unit Tests

```python
def test_debounce_rapid_saves():
    """Multiple rapid saves should result in single re-ingestion."""
    watcher = FileWatcherService(...)

    # Simulate rapid saves
    for _ in range(10):
        watcher._handle_event('modified', 'test.md')
        time.sleep(0.1)

    time.sleep(1)  # Wait for debounce

    assert ingestor.ingest_file.call_count == 1

def test_categorize_story_bible():
    """Story Bible files should be categorized correctly."""
    watcher = FileWatcherService(...)

    assert watcher._categorize_file(Path('Story Bible/Protagonist.md')) == 'story_bible'
    assert watcher._categorize_file(Path('Characters/Mickey.md')) == 'story_bible'

def test_conflict_detection():
    """Conflicts between chat and file should be flagged."""
    ingestor = IncrementalIngestor(...)

    existing = [{'id': 'Mickey', 'desc': 'fears heights', 'source_file': None}]
    new = [{'id': 'Mickey', 'desc': 'loves flying'}]

    conflicts = ingestor._detect_conflicts(existing, new, 'Mickey.md')

    assert len(conflicts) == 1
    assert conflicts[0]['node_id'] == 'Mickey'
```

---

## Success Criteria

- [ ] External file edits detected within 1 second
- [ ] Debouncing prevents redundant re-ingestion during rapid saves
- [ ] Chat-derived knowledge is never lost during file re-ingestion
- [ ] Conflicts between file and chat are logged, not silently overwritten
- [ ] File watcher survives content directory moves/renames
- [ ] Tauri integration provides native performance on desktop
