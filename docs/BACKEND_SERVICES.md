# Backend Services Documentation

> Technical documentation for all backend services in Writers Factory.

---

## Architecture Overview

```
backend/
├── api.py                      # FastAPI application & endpoints
├── ingestor.py                 # Graph ingestion from markdown files
├── agents/
│   ├── foreman.py              # THE FOREMAN - Ollama-powered creative partner
│   ├── orchestrator.py         # SceneTournament, DraftCritic
│   ├── registry.py             # AgentRegistry - loads agents.yaml
│   └── specialists/
│       └── scaffold.py         # SmartScaffoldAgent
├── bridges/
│   └── gemini_cli.py           # Gemini API bridge
├── graph/
│   ├── graph_service.py        # KnowledgeGraphService
│   ├── schema.py               # SQLAlchemy models (Node, Edge)
│   └── ner_extractor.py        # Named Entity Recognition
├── services/
│   ├── llm_service.py          # LLM abstraction layer
│   ├── manager_service.py      # Manager agent service
│   ├── session_service.py      # Chat session persistence
│   ├── consolidator_service.py # "The Liver" - digests sessions
│   ├── notebooklm_service.py   # NotebookLM MCP client
│   └── story_bible_service.py  # Story Bible parsing & validation
├── workflows/
│   ├── base.py                 # Workflow, WorkflowStep, WorkflowResult
│   └── smart_scaffold.py       # AI Scaffolding Agent workflow
└── external/
    └── notebooklm-mcp/         # Node.js MCP server for NotebookLM
```

---

## Core Services

### 1. The Foreman (Intelligent Creative Partner)

**File:** `backend/agents/foreman.py`

The Foreman is an Ollama-powered intelligent agent that serves as a creative writing partner throughout the novel-writing process. Unlike a simple chatbot wizard, the Foreman understands narrative craft and actively challenges weak structural choices.

> **Design Philosophy:** See [specs/STORY_BIBLE_ARCHITECT.md](specs/STORY_BIBLE_ARCHITECT.md) for the complete specification.

#### Three Modes Across Project Lifecycle

| Mode | Stage | Purpose |
|------|-------|---------|
| `ARCHITECT` | Conception | Build Story Bible, query NotebookLM, challenge structure |
| `DIRECTOR` | Execution | Draft scenes, inject context, maintain beat awareness |
| `EDITOR` | Polish | Check voice consistency, pacing, continuity |

#### Key Classes

##### `ForemanMode`
```python
class ForemanMode(Enum):
    ARCHITECT = "architect"  # Stage 1: Story Bible creation
    DIRECTOR = "director"    # Stage 2: Scene drafting
    EDITOR = "editor"        # Stage 3: Revision and polish
```

##### `TemplateRequirement`
```python
@dataclass
class TemplateRequirement:
    name: str                  # "Protagonist", "Beat Sheet", etc.
    file_path: str             # Path pattern (supports {name} placeholder)
    status: str = "not_started"  # not_started, in_progress, complete
    required_fields: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    last_updated: Optional[datetime] = None
```

##### `WorkOrder`
Tracks what needs to be completed and current progress.

```python
@dataclass
class WorkOrder:
    project_title: str
    protagonist_name: str
    mode: ForemanMode = ForemanMode.ARCHITECT
    templates: List[TemplateRequirement] = field(default_factory=list)
    notebooks: Dict[str, str] = field(default_factory=dict)  # role -> notebook_id
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def completion_percentage(self) -> float:
        """Calculate overall completion (0-100%)."""

    @property
    def is_complete(self) -> bool:
        """All templates marked as complete."""

    def get_status_summary(self) -> str:
        """Generate a status summary for the Foreman's context."""
```

##### `Foreman`
The main agent class.

```python
class Foreman:
    def __init__(
        self,
        model: str = "llama3.2:3b",
        ollama_url: str = "http://localhost:11434",
        notebooklm_client = None,
        story_bible_service = None,
        content_path: Path = None,
    ):
        # Stores conversation history, work order, KB entries

    # Project Management
    def start_project(self, project_title: str, protagonist_name: str) -> WorkOrder
    def register_notebook(self, notebook_id: str, role: str)  # role: world, voice, craft
    def reset(self)

    # Conversation
    async def chat(self, user_message: str) -> Dict:
        """
        Send a message and get a response.

        Returns:
            {
                "response": str,      # Foreman's response text
                "actions": List,      # Actions taken (notebook queries, KB writes)
                "work_order": Dict,   # Current work order status
                "kb_entries_pending": int
            }
        """

    # Knowledge Base
    def get_kb_entries(self) -> List[Dict]
    def flush_kb_entries(self) -> List[Dict]  # Return and clear pending entries
```

#### Action System

The Foreman can emit structured JSON actions that the system executes:

```python
# Query a NotebookLM notebook
{
    "action": "query_notebook",
    "notebook_role": "world",  # or "voice", "craft"
    "query": "What is the social structure of the Gatekeepers?"
}

# Save a decision to the Knowledge Base
{
    "action": "save_decision",
    "category": "character",  # or "world", "constraint", "structure"
    "key": "mickey_fatal_flaw",
    "value": "Intellectual arrogance - dismisses emotional intelligence",
    "source": "Writer brainstorm + Future 2034 notebook"
}

# Update a template field
{
    "action": "update_template",
    "template": "Protagonist",
    "field": "fatal_flaw",
    "value": "Intellectual arrogance - believes pure logic solves everything"
}
```

#### System Prompt (Embedded Craft Knowledge)

The Foreman has ~2000 tokens of craft knowledge in its system prompt:

- **Fatal Flaw vs Circumstance**: Challenges "external problem" flaws
- **The Lie**: Ensures protagonist has mistaken belief driving behavior
- **15-Beat Structure**: Knows Save the Cat! percentages and purposes
- **Midpoint Types**: False Victory vs False Defeat understanding
- **Character Arc**: Setup → Midpoint shift → Resolution

#### Context Window Management

```
┌─────────────────────────────────────────────────────────────┐
│ FOREMAN CONTEXT WINDOW (~7000 tokens total)                 │
├─────────────────────────────────────────────────────────────┤
│ [SYSTEM PROMPT] ~2000 tokens                                │
│   Craft knowledge, action instructions, mode-specific skills│
│                                                             │
│ [WORK ORDER] ~200 tokens                                    │
│   Current templates and completion status                   │
│                                                             │
│ [KB RETRIEVAL] ~1000 tokens                                 │
│   Relevant decisions, constraints, facts                    │
│                                                             │
│ [CONVERSATION] ~4000 tokens                                 │
│   Recent exchanges with the writer                          │
└─────────────────────────────────────────────────────────────┘
```

#### Factory Function

```python
def create_foreman(
    notebooklm_client=None,
    story_bible_service=None,
    content_path: Path = None,
    model: str = "llama3.2:3b",
) -> Foreman:
    """
    Factory function to create a configured Foreman instance.

    Usage:
        foreman = create_foreman(
            notebooklm_client=get_notebooklm_client(),
            story_bible_service=StoryBibleService(content_path),
            content_path=Path("content"),
        )
    """
```

---

### 2. StoryBibleService

**File:** `backend/services/story_bible_service.py`

The central service for Phase 2: Story Bible System. Manages scaffolding, parsing, and validation of Story Bible artifacts.

#### Key Classes

##### `ProtagonistData`
```python
@dataclass
class ProtagonistData:
    name: str = ""
    true_character: str = ""      # Core traits under pressure
    characterization: str = ""     # Observable qualities
    fatal_flaw: str = ""           # Internal weakness
    the_lie: str = ""              # Mistaken belief
    arc_start: str = ""
    arc_midpoint: str = ""
    arc_resolution: str = ""
    relationships: list[dict] = field(default_factory=list)
    contradiction_score: float = 0.0  # 0.0-1.0 complexity metric

    @property
    def is_valid(self) -> bool:
        """Requires name, fatal_flaw, and the_lie."""
```

##### `BeatData`
```python
@dataclass
class BeatData:
    number: int          # 1-15
    name: str            # "Opening Image", "Catalyst", etc.
    percentage: str      # "1%", "10%", "50%", etc.
    description: str = ""
    scene_link: str = ""  # e.g., "1.5.2"

    @property
    def is_complete(self) -> bool:
        """Has both name and description."""
```

##### `BeatSheetData`
```python
@dataclass
class BeatSheetData:
    title: str = ""
    beats: list[BeatData] = field(default_factory=list)
    current_beat: int = 1
    midpoint_type: str = ""  # "false_victory" or "false_defeat"
    theme_stated: str = ""   # From Beat 2

    @property
    def is_valid(self) -> bool:
        """All 15 beats defined and complete."""

    @property
    def completion_percentage(self) -> float:
        """How complete is the beat sheet (0-100%)."""
```

##### `StoryBibleStatus`
```python
@dataclass
class StoryBibleStatus:
    protagonist_exists: bool = False
    protagonist_has_flaw: bool = False
    protagonist_has_lie: bool = False
    beat_sheet_exists: bool = False
    beat_sheet_complete: bool = False
    scene_strategy_exists: bool = False
    theme_defined: bool = False
    world_rules_exist: bool = False

    @property
    def phase2_complete(self) -> bool:
        """Can we proceed to Phase 3 (Execution)?"""
        return (protagonist_exists and protagonist_has_flaw
                and protagonist_has_lie and beat_sheet_complete)

    @property
    def completion_score(self) -> float:
        """Overall completion percentage (0-100%)."""
```

#### Parsers

##### `ProtagonistParser`
Extracts structured data from `Protagonist.md` files.

```python
class ProtagonistParser:
    def parse(self, content: str, filename: str = "") -> ProtagonistData:
        """
        Parse protagonist file content into structured data.

        Handles:
        - Template format (## Fatal Flaw, ## The Lie, etc.)
        - Freeform documents (searches for key markers)
        - Mickey Bardot Enhanced Identity format
        """

    def _extract_section(self, content: str, headers: list[str]) -> str:
        """Extract content under any of the given headers."""

    def _calculate_contradiction_score(self, data: ProtagonistData) -> float:
        """
        Score 0.0-1.0 measuring character complexity:
        - +0.3 if True Character differs from Characterization
        - +0.3 if Fatal Flaw defined
        - +0.2 if The Lie defined
        - +0.2 if Arc shows change
        """
```

##### `BeatSheetParser`
Enforces Save the Cat! 15-beat structure.

```python
class BeatSheetParser:
    BEAT_NAMES = [
        "Opening Image", "Theme Stated", "Setup", "Catalyst", "Debate",
        "Break into Two", "B Story", "Fun & Games", "Midpoint",
        "Bad Guys Close In", "All Is Lost", "Dark Night of the Soul",
        "Break into Three", "Finale", "Final Image"
    ]

    BEAT_PERCENTAGES = [
        "1%", "5%", "1-10%", "10%", "10-20%", "20%", "22%", "20-50%",
        "50%", "50-75%", "75%", "75-80%", "80%", "80-99%", "99-100%"
    ]

    def parse(self, content: str) -> BeatSheetData:
        """Parse beat sheet, extracting all 15 beats and midpoint type."""
```

#### Main Service Methods

```python
class StoryBibleService:
    def __init__(self, content_path: Path):
        self.content_path = content_path
        self.story_bible_path = content_path / "Story Bible"

    # Directory Structure
    def ensure_directory_structure(self) -> dict:
        """Create Characters/, Story Bible/Structure/, etc."""

    # Template Generation
    def generate_protagonist_template(self, name: str, pre_filled: dict = None) -> str
    def generate_beat_sheet_template(self, title: str, pre_filled: dict = None) -> str
    def generate_scene_strategy_template(self, ...) -> str
    def generate_theme_template(self, title: str) -> str
    def generate_world_rules_template(self, title: str) -> str

    # Scaffold Creation
    def scaffold_story_bible(
        self,
        project_title: str,
        protagonist_name: str,
        pre_filled: dict = None
    ) -> dict:
        """Create all Story Bible files with optional pre-filled data."""

    # Parsing
    def parse_protagonist(self, file_path: Path = None) -> ProtagonistData
    def parse_beat_sheet(self, file_path: Path = None) -> BeatSheetData

    # Validation (Level 2 Health Checks)
    def validate_story_bible(self) -> StoryBibleStatus
    def get_validation_report(self) -> dict
```

---

### 2. NotebookLMMCPClient

**File:** `backend/services/notebooklm_service.py`

MCP client for Google NotebookLM integration via Puppeteer-based Node.js server.

#### Architecture

```
Python API ─── MCP Protocol ─── Node.js Server ─── Puppeteer ─── NotebookLM Web
```

#### Configuration

```python
AUTH_TIMEOUT_SECONDS = 120  # For first-time Google Login
QUERY_TIMEOUT_SECONDS = 45  # Standard queries
```

#### Key Methods

```python
class NotebookLMMCPClient:
    # Singleton pattern
    _instance: Optional["NotebookLMMCPClient"] = None

    async def ensure_started(self):
        """Launch Node.js MCP server if not running."""

    async def setup_auth(self) -> Dict:
        """Trigger authentication flow (opens browser for Google login)."""

    async def list_notebooks(self) -> List[NotebookInfo]:
        """Fetch available notebooks."""

    async def query_notebook(self, notebook_id: str, query: str) -> NotebookResponse:
        """
        Query a notebook with a question.

        Returns:
            NotebookResponse with answer, sources, notebook_id, query
        """

    async def extract_character_profile(self, notebook_id: str, character_name: str) -> Dict
    async def extract_world_building(self, notebook_id: str, aspect: str) -> Dict
    async def query_for_context(self, notebook_id: str, entity_name: str, entity_type: str) -> str
```

#### Response Models

```python
class NotebookInfo(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    source_count: int = 0
    created_at: str = ""
    updated_at: str = ""

class NotebookResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]
    notebook_id: str
    query: str
```

---

### 3. SessionService

**File:** `backend/services/session_service.py`

Persistent chat session management for "The Workbench".

#### Purpose
- Create and track chat sessions
- Log all messages (user, assistant, system)
- Provide audit trail for Consolidator
- Track uncommitted events for graph ingestion

#### Key Methods
```python
class SessionService:
    def create_session(self, scene_id: str = None) -> str
    def log_event(self, session_id: str, role: str, content: str, ...) -> SessionEvent
    def get_session_history(self, session_id: str, limit: int = 50) -> List[SessionEvent]
    def get_session_stats(self, session_id: str) -> dict
    def get_active_sessions(self, limit: int = 20) -> List[dict]
    def get_uncommitted_events(self, session_id: str = None) -> List[SessionEvent]
    def mark_as_committed(self, event_ids: List[int]) -> int
```

---

### 4. ConsolidatorService

**File:** `backend/services/consolidator_service.py`

"The Liver" - digests chat sessions into the knowledge graph.

#### Purpose
- Extract entities from chat conversations
- Merge new information into knowledge graph
- Detect and flag conflicts
- Use local Llama 3.2 for extraction (zero cost)

#### Key Methods
```python
class ConsolidatorService:
    async def digest_session(self, session_id: str, dry_run: bool = False) -> dict
    async def digest_all_uncommitted(self, dry_run: bool = False) -> dict
```

---

### 5. KnowledgeGraphService

**File:** `backend/graph/graph_service.py`

SQLite-backed knowledge graph for story entities.

#### Schema (from `graph/schema.py`)
```python
class Node(Base):
    id: int
    name: str
    node_type: str  # character, location, event, theme, etc.
    properties: JSON
    created_at: datetime
    updated_at: datetime

class Edge(Base):
    id: int
    source_id: int  # FK to Node
    target_id: int  # FK to Node
    relation: str   # KNOWS, DEPENDS_ON, CONTRADICTS, etc.
    properties: JSON
```

#### Key Methods
```python
class KnowledgeGraphService:
    def add_node(self, node: Node) -> Node
    def get_node(self, node_id: int) -> Optional[Node]
    def find_node_by_name(self, name: str) -> Optional[Node]
    def add_edge(self, edge: Edge) -> Edge
    def get_neighbors(self, node_id: int) -> List[Node]
```

---

### 6. GraphIngestor

**File:** `backend/ingestor.py`

Ingests markdown files from `content/` into the knowledge graph.

#### Features
- Uses **local Llama 3.2 via Ollama** (zero cost)
- Extracts entities and relationships
- Stores to `backend/knowledge_graph.json`

#### Usage
```python
ingestor = GraphIngestor(max_files=10)  # Limit for testing
result = await ingestor.run_ingestion()
```

---

## Directory Structure

### Content Folder Layout

```
content/
├── Characters/
│   ├── Mickey_Bardot.md           # Protagonist
│   └── Noni.md                    # Supporting character
├── Story Bible/
│   ├── Structure/
│   │   ├── Beat_Sheet.md          # 15-beat structure
│   │   └── Scene_Strategy.md      # Scene-level plans
│   ├── Themes_and_Philosophy/
│   │   └── 04_Theme.md            # Theme document
│   └── Research/
│       └── NotebookLM_Export.md   # Synthesized research
├── World Bible/
│   └── Rules.md                   # World rules
└── Scenes/
    └── Chapter_1.md               # Written scenes
```

---

## Templates

### Story Bible Templates

All templates are defined in `story_bible_service.py`:

| Template | Purpose | Required Fields |
|----------|---------|-----------------|
| `PROTAGONIST_TEMPLATE` | Character profile | name, fatal_flaw, the_lie |
| `BEAT_SHEET_TEMPLATE` | 15-beat structure | All 15 beats |
| `SCENE_STRATEGY_TEMPLATE` | Scene planning | goal, conflict, outcome |
| `THEME_TEMPLATE` | Theme document | central_theme, thesis |
| `WORLD_RULES_TEMPLATE` | World rules | fundamental_rules |

---

## Data Flow

### Story Bible Creation Flow

```
1. User uploads research to NotebookLM
                ↓
2. POST /story-bible/smart-scaffold
                ↓
3. SmartScaffoldWorkflow:
   ├── Query NotebookLM for protagonist
   ├── Query NotebookLM for beat sheet
   ├── Query NotebookLM for themes
   ├── Query NotebookLM for world rules
   ├── Synthesize into templates
   └── Validate completeness
                ↓
4. Story Bible files created in content/
                ↓
5. GET /story-bible/status → Level 2 Health Checks
                ↓
6. When phase2_complete=true → Ready for Phase 3
```

### Session → Graph Flow

```
1. User chats in Workbench
                ↓
2. POST /session/{id}/message (logged)
                ↓
3. POST /graph/consolidate/{session_id}
                ↓
4. ConsolidatorService:
   ├── Get uncommitted events
   ├── Extract entities (Llama 3.2)
   ├── Merge into knowledge_graph.json
   └── Mark events as committed
                ↓
5. GET /health/status shows updated graph
```

---

## Configuration Files

### `agents.yaml`
Configures AI agents for tournaments and evaluations.

```yaml
agents:
  - id: drafter-narrative
    type: drafter
    enabled: true
    model: gpt-4
    use_cases: [tournament]

  - id: critic-structure
    type: critic
    enabled: true
    model: gpt-4
    use_cases: [evaluation]
```

### `backend/notebooklm_config.json`
Stores configured notebook IDs.

```json
{
  "notebooks": [
    {"id": "abc123", "title": "Big Brain Research"}
  ]
}
```

---

*Generated for Writers Factory v0.1*
