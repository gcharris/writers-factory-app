# Workflows Documentation

> Technical documentation for the workflow infrastructure in Writers Factory.

---

## Overview

Workflows are composable, multi-step async processes that:
- Execute steps in sequence
- Pass context between steps
- Track progress and timing
- Handle errors gracefully
- Return detailed execution results

---

## Architecture

```
backend/workflows/
├── __init__.py         # Module exports
├── base.py             # Workflow, WorkflowStep, WorkflowResult
└── smart_scaffold.py   # SmartScaffoldWorkflow implementation
```

---

## Base Classes

### WorkflowStep

A single step in a workflow execution.

**File:** `backend/workflows/base.py`

```python
@dataclass
class WorkflowStep:
    name: str                           # Human-readable step name
    func: Callable                      # Async function to execute
    kwargs: Dict[str, Any]              # Arguments for the function
    result: Optional[Any] = None        # Execution result
    error: Optional[Exception] = None   # Error if failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def duration_ms(self) -> Optional[float]:
        """Duration in milliseconds if completed."""

    @property
    def status(self) -> str:
        """Returns: 'pending', 'running', 'completed', or 'failed'"""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """Execute this step with the given context."""
```

### WorkflowResult

Container for workflow execution results.

```python
@dataclass
class WorkflowResult:
    workflow_name: str                  # Class name of the workflow
    success: bool                       # True if all steps completed
    steps: List[WorkflowStep]           # All steps with their results
    final_result: Any = None            # Result from last successful step
    context: Dict[str, Any]             # Final context with all step results
    total_duration_ms: float = 0.0      # Total execution time
    error: Optional[str] = None         # Error message if failed

    def get_step_result(self, step_name: str) -> Optional[Any]:
        """Get result from a specific step by name."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
```

**Example `to_dict()` output:**
```json
{
  "workflow": "SmartScaffoldWorkflow",
  "success": true,
  "duration_ms": 45230.5,
  "error": null,
  "steps": [
    {"name": "Query Protagonist Data", "status": "completed", "duration_ms": 8200.3, "error": null},
    {"name": "Query Beat Sheet", "status": "completed", "duration_ms": 9500.1, "error": null},
    {"name": "Synthesize Story Bible", "status": "completed", "duration_ms": 5100.7, "error": null}
  ],
  "final_result": {"created_files": [...], "validation": {...}}
}
```

### Workflow (Abstract Base Class)

Base class for all workflow implementations.

```python
class Workflow(ABC):
    def __init__(self):
        self.steps: List[WorkflowStep] = []
        self.context: Dict[str, Any] = {}
        self._progress_callback: Optional[Callable] = None

    def add_step(
        self,
        name: str,
        func: Callable,
        **kwargs
    ) -> "Workflow":
        """
        Add a step to the workflow.
        Returns self for method chaining.

        The function must be async and accept (context, **kwargs).
        """

    def on_progress(self, callback: Callable[[int, int, str], None]) -> "Workflow":
        """
        Set progress callback.
        Callback signature: (current_step, total_steps, step_name)
        """

    async def execute(
        self,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Execute all steps in sequence.

        - Updates context after each step
        - Stops on first error
        - Tracks timing for each step
        """

    @abstractmethod
    async def run(self, **kwargs) -> WorkflowResult:
        """
        Main entry point for the workflow.
        Subclasses must implement this.
        """

    def reset(self) -> "Workflow":
        """Reset workflow for re-execution."""
```

---

## Creating a Workflow

### Step 1: Define the Workflow Class

```python
from backend.workflows.base import Workflow, WorkflowResult

class MyCustomWorkflow(Workflow):
    def __init__(self, some_service):
        super().__init__()
        self.service = some_service

    async def run(self, input_param: str) -> WorkflowResult:
        self.reset()  # Clear previous runs

        # Add steps
        self.add_step("Step 1", self._step_one, param=input_param)
        self.add_step("Step 2", self._step_two)
        self.add_step("Step 3", self._step_three)

        # Execute with initial context
        return await self.execute({'input': input_param})
```

### Step 2: Implement Step Functions

Each step function must:
- Be `async`
- Accept `context: Dict[str, Any]` as first argument
- Accept any additional kwargs passed via `add_step`
- Return a value (stored in `context` for next steps)

```python
async def _step_one(self, context: Dict[str, Any], param: str) -> Dict:
    """First step - fetches data."""
    result = await self.service.fetch_data(param)
    return {'data': result, 'count': len(result)}

async def _step_two(self, context: Dict[str, Any]) -> Dict:
    """Second step - processes data from step one."""
    # Access previous step's result from context
    data = context.get('step_1', {}).get('data', [])
    processed = [transform(item) for item in data]
    return {'processed': processed}

async def _step_three(self, context: Dict[str, Any]) -> Dict:
    """Third step - validates results."""
    processed = context.get('step_2', {}).get('processed', [])
    is_valid = all(validate(item) for item in processed)
    return {'valid': is_valid, 'item_count': len(processed)}
```

### Step 3: Use the Workflow

```python
# Create workflow instance
workflow = MyCustomWorkflow(some_service)

# Optional: add progress callback
workflow.on_progress(lambda curr, total, name: print(f"Step {curr}/{total}: {name}"))

# Run workflow
result = await workflow.run(input_param="example")

# Check results
if result.success:
    print(f"Completed in {result.total_duration_ms}ms")
    print(f"Final result: {result.final_result}")
else:
    print(f"Failed: {result.error}")
```

---

## SmartScaffoldWorkflow

**File:** `backend/workflows/smart_scaffold.py`

The "AI Scaffolding Agent" that converts NotebookLM research into Story Bible templates.

### Purpose

- Query NotebookLM for character, plot, theme, and world data
- Parse responses into structured template fields
- Create Story Bible files with synthesized content
- Validate completeness (Level 2 Health Checks)

### Steps

| # | Step Name | Description | Output |
|---|-----------|-------------|--------|
| 1 | Query Protagonist Data | Extract character profile from NotebookLM | `{raw_response, sources, protagonist_name}` |
| 2 | Query Beat Sheet | Extract 15-beat structure | `{raw_response, sources}` |
| 3 | Query Themes | Extract theme information | `{raw_response, sources}` |
| 4 | Query World Rules | Extract world-building rules | `{raw_response, sources}` |
| 5 | Synthesize Story Bible | Parse responses, create template files | `{created_files, protagonist_prefill, beat_sheet_prefill}` |
| 6 | Validate Completeness | Run Level 2 Health Checks | `{validation, phase2_complete, completion_score}` |

### Query Prompts

The workflow uses carefully crafted prompts to extract structured data:

**Protagonist Query:**
```
Based on all the sources in this notebook, provide a detailed character profile...
1. Name
2. True Character (core traits under pressure)
3. Characterization (observable qualities)
4. Fatal Flaw (internal weakness)
5. The Lie (mistaken belief)
6. Arc Starting State
7. Arc Midpoint
8. Arc Resolution
```

**Beat Sheet Query:**
```
Outline the 15-beat story structure (Save the Cat! format):
1. Opening Image (1%)
2. Theme Stated (5%)
...
15. Final Image (99-100%)
```

### Usage

**Via API:**
```http
POST /story-bible/smart-scaffold
Content-Type: application/json

{
  "notebook_id": "abc123",
  "project_title": "Big Brain",
  "protagonist_name": "Mickey Bardot"
}
```

**Programmatically:**
```python
from backend.workflows.smart_scaffold import SmartScaffoldWorkflow
from backend.services.notebooklm_service import get_notebooklm_client
from backend.services.story_bible_service import StoryBibleService
from pathlib import Path

# Initialize services
nlm_client = get_notebooklm_client()
story_bible_svc = StoryBibleService(Path("content"))

# Create and run workflow
workflow = SmartScaffoldWorkflow(nlm_client, story_bible_svc)
result = await workflow.run(
    notebook_id="abc123",
    project_title="Big Brain",
    protagonist_name="Mickey Bardot"
)

if result.success:
    validation = result.get_step_result("Validate Completeness")
    print(f"Phase 2 Complete: {validation['phase2_complete']}")
    print(f"Completion Score: {validation['completion_score']}%")
```

### Response Parsing

The workflow includes parsers that extract structured data from NotebookLM's natural language responses:

```python
def _parse_protagonist_response(self, response: str, protagonist_name: str) -> Dict[str, str]:
    """
    Extracts fields by looking for:
    - **Header**: Content patterns
    - ## Header sections
    - Numbered lists (1. Header: Content)
    """

def _parse_beat_sheet_response(self, response: str) -> Dict[str, str]:
    """
    Maps beat numbers (1-15) to template field names (beat_1, beat_2, etc.)
    Also detects midpoint_type (false_victory/false_defeat)
    """
```

---

## Context Flow

The workflow context accumulates results from each step:

```python
# After Step 1 (Query Protagonist Data)
context = {
    'notebook_id': 'abc123',
    'project_title': 'Big Brain',
    'protagonist_name': 'Mickey Bardot',
    'step_0_result': {...},
    'query_protagonist_data': {
        'raw_response': '...',
        'sources': [...],
        'protagonist_name': 'Mickey Bardot'
    }
}

# After Step 2 (Query Beat Sheet)
context['query_beat_sheet'] = {
    'raw_response': '...',
    'sources': [...]
}

# After Step 5 (Synthesize Story Bible)
context['synthesize_story_bible'] = {
    'created_files': [...],
    'protagonist_prefill': {...},
    'beat_sheet_prefill': {...}
}
```

---

## Error Handling

Workflows stop on first error and report which step failed:

```python
result = await workflow.run(...)

if not result.success:
    print(f"Error: {result.error}")
    # Example: "Step 'Query Protagonist Data' failed: NotebookLM timed out"

    # Check individual step status
    for step in result.steps:
        print(f"{step.name}: {step.status}")
        if step.error:
            print(f"  Error: {step.error}")
```

---

## Best Practices

### 1. Keep Steps Focused
Each step should do one thing well. This makes debugging easier.

### 2. Use Context for Data Flow
Don't store state in instance variables between steps. Use the context dict.

### 3. Return Structured Data
Always return dicts from steps so the data is accessible in context.

### 4. Handle External Service Failures
Wrap external calls (NotebookLM, LLMs) in try/except and provide meaningful error messages.

### 5. Reset Before Run
Always call `self.reset()` at the start of `run()` to clear previous execution state.

---

## Future Workflows

Planned workflows based on ARCHITECTURE.md roadmap:

| Workflow | Purpose | Phase |
|----------|---------|-------|
| `SceneGenerationWorkflow` | Draft scenes with tournament | Phase 3 |
| `ArchivistWorkflow` | Finalize and archive scenes | Phase 4 |
| `VoiceConsistencyWorkflow` | Check voice across chapters | Phase 5 |
| `NarrativeHealthWorkflow` | Run all health checks | Phase 3 |

---

*Generated for Writers Factory v0.1*
