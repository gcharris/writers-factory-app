"""
The Foreman - Intelligent Creative Writing Partner

An Ollama-powered agent that guides writers through the novel creation process.
Operates in three modes across the project lifecycle:
- Architect (Stage 1): Story Bible creation
- Director (Stage 2): Scene drafting
- Editor (Stage 3): Revision and polish

The Foreman maintains persistent memory through the Knowledge Base and
adapts to the writer's pace while keeping the work order in mind.
"""

import asyncio
import json
import logging
import httpx
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from backend.services.foreman_kb_service import get_foreman_kb_service, ForemanKBService

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Data Classes
# =============================================================================

class ForemanMode(Enum):
    """The four operational modes of the Foreman."""
    ARCHITECT = "architect"           # Stage 1: Story Bible creation
    VOICE_CALIBRATION = "voice_calibration"  # Stage 1.5: Voice tournament
    DIRECTOR = "director"             # Stage 2: Scene drafting
    EDITOR = "editor"                 # Stage 3: Revision and polish


class TemplateStatus(Enum):
    """Status of a Story Bible template."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DRAFT_READY = "draft_ready"
    COMPLETE = "complete"


@dataclass
class TemplateRequirement:
    """A required template in the work order."""
    name: str
    file_path: str
    status: TemplateStatus = TemplateStatus.NOT_STARTED
    required_fields: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'file_path': self.file_path,
            'status': self.status.value,
            'required_fields': self.required_fields,
            'missing_fields': self.missing_fields,
            'last_updated': self.last_updated,
        }


@dataclass
class WorkOrder:
    """
    The Foreman's work order - tracks what needs to be done.

    The Foreman always knows:
    - What's done
    - What's incomplete
    - What's blocked
    """
    project_title: str
    protagonist_name: str
    mode: ForemanMode = ForemanMode.ARCHITECT
    templates: List[TemplateRequirement] = field(default_factory=list)
    notebooks: Dict[str, str] = field(default_factory=dict)  # notebook_id -> role
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        if not self.templates:
            self._init_architect_templates()

    def _init_architect_templates(self):
        """Initialize templates for Architect mode."""
        self.templates = [
            TemplateRequirement(
                name="Protagonist",
                file_path="Characters/{name}.md",
                required_fields=["fatal_flaw", "the_lie", "arc_start", "arc_resolution"],
            ),
            TemplateRequirement(
                name="Beat Sheet",
                file_path="Story Bible/Structure/Beat_Sheet.md",
                required_fields=[f"beat_{i}" for i in range(1, 16)] + ["midpoint_type"],
            ),
            TemplateRequirement(
                name="Theme",
                file_path="Story Bible/Themes_and_Philosophy/Theme.md",
                required_fields=["central_theme", "theme_statement"],
            ),
            TemplateRequirement(
                name="World Rules",
                file_path="World Bible/Rules.md",
                required_fields=["fundamental_rules"],
            ),
        ]

    @property
    def completion_percentage(self) -> float:
        """Overall work order completion."""
        if not self.templates:
            return 0.0
        complete = sum(1 for t in self.templates if t.status == TemplateStatus.COMPLETE)
        return (complete / len(self.templates)) * 100

    @property
    def is_complete(self) -> bool:
        """Can we proceed to the next stage?"""
        return all(t.status == TemplateStatus.COMPLETE for t in self.templates)

    def get_status_summary(self) -> str:
        """Generate a status summary for the Foreman's context."""
        lines = [f"WORK ORDER: {self.project_title}"]
        lines.append(f"Mode: {self.mode.value.upper()}")
        lines.append(f"Completion: {self.completion_percentage:.0f}%")
        lines.append("")
        lines.append("Templates:")
        for t in self.templates:
            status_icon = {
                TemplateStatus.NOT_STARTED: "□",
                TemplateStatus.IN_PROGRESS: "◐",
                TemplateStatus.DRAFT_READY: "◑",
                TemplateStatus.COMPLETE: "✓",
            }[t.status]
            missing = f" (missing: {', '.join(t.missing_fields)})" if t.missing_fields else ""
            lines.append(f"  {status_icon} {t.name}{missing}")

        if self.notebooks:
            lines.append("")
            lines.append("Notebooks:")
            for nb_id, role in self.notebooks.items():
                lines.append(f"  • {role}: {nb_id[:8]}...")

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        return {
            'project_title': self.project_title,
            'protagonist_name': self.protagonist_name,
            'mode': self.mode.value,
            'templates': [t.to_dict() for t in self.templates],
            'notebooks': self.notebooks,
            'completion_percentage': self.completion_percentage,
            'is_complete': self.is_complete,
            'created_at': self.created_at,
        }


@dataclass
class ConversationMessage:
    """A single message in the conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KBEntry:
    """An entry to be written to the Knowledge Base."""
    entry_type: str  # "decision", "constraint", "character", "world", "notebook"
    key: str
    value: Any
    source: str = ""  # Where this came from (notebook, brainstorm, etc.)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# System Prompts
# =============================================================================

ARCHITECT_SYSTEM_PROMPT = """# THE FOREMAN - ARCHITECT MODE

You are the Foreman, an expert creative writing partner specializing in narrative structure and the Narrative Protocol methodology. You guide writers from unstructured research to a complete, validated Story Bible.

## YOUR ROLE

You are NOT a chatbot wizard collecting form inputs. You are a thinking, craft-aware collaborator who:

1. ASSESSES available resources (NotebookLM notebooks, existing files)
2. IDENTIFIES gaps against Story Bible requirements
3. PROPOSES paths to fill gaps (query notebooks, brainstorm, create new sources)
4. CHALLENGES weak structural choices with craft expertise
5. CONNECTS elements across multiple sources
6. SYNTHESIZES into properly structured templates

## NARRATIVE PROTOCOL REQUIREMENTS

### PROTAGONIST (Required)
- **Fatal Flaw**: Internal weakness that blocks success
  - MUST be internal/psychological, NOT external circumstance
  - "Being poor" is circumstance; "inability to trust" is a flaw
- **The Lie**: Mistaken belief driving the Fatal Flaw
  - What they wrongly believe about themselves or the world
- **Arc**: Transformation from start to end

### BEAT SHEET (Required - 15 beats)
1. Opening Image (1%) - "Before" snapshot
2. Theme Stated (5%) - Theme hinted
3. Setup (1-10%) - Ordinary world
4. Catalyst (10%) - Inciting incident
5. Debate (10-20%) - Protagonist hesitates
6. Break into Two (20%) - Commits
7. B Story (22%) - Subplot with theme
8. Fun & Games (20-50%) - Promise of premise
9. Midpoint (50%) - FALSE VICTORY or FALSE DEFEAT
10. Bad Guys Close In (50-75%) - Opposition tightens
11. All Is Lost (75%) - Lowest point
12. Dark Night of the Soul (75-80%) - Despair
13. Break into Three (80%) - Solution found
14. Finale (80-99%) - Final confrontation
15. Final Image (99-100%) - Mirror of opening

### THEME (Required)
- Central Theme: Core idea explored
- Theme Statement: One-sentence encapsulation

### WORLD RULES (Required)
- Fundamental Rules: Non-negotiable laws of this story world

## YOUR BEHAVIORAL FRAMEWORK

### When Assessing Notebooks
- Inventory what's available
- Categorize by potential: World-building, Character Voice, Craft Reference
- Be explicit about what you see and what's missing

### When Identifying Gaps
- Compare available resources to requirements
- Be specific: "I have situation but not interior"
- Always offer multiple paths forward

### When Challenging Weak Choices
- Push back firmly but constructively
- Explain WHY something doesn't work
- Offer alternatives grounded in the writer's material

### When Synthesizing Across Sources
- Make connections explicit
- Show your reasoning
- Check resonance before proceeding

## CONVERSATION STYLE

- Be direct and substantive, not chatty
- Show your thinking ("GAP DETECTED:", "SYNTHESIS:", "OPTIONS:")
- Challenge respectfully but firmly
- Always propose next step

## AVAILABLE ACTIONS

When you need to take an action, respond with a JSON block:

```json
{"action": "query_notebook", "notebook_id": "...", "query": "..."}
{"action": "write_template", "template": "protagonist", "content": {...}}
{"action": "update_status", "template": "protagonist", "status": "in_progress", "missing": [...]}
{"action": "save_decision", "category": "character|world|structure|constraint|preference", "key": "...", "value": "...", "source": "..."}
```

Always explain what you're doing and why before taking an action.
"""


VOICE_CALIBRATION_SYSTEM_PROMPT = """# THE FOREMAN - VOICE CALIBRATION MODE

You are the Foreman, transitioning from Story Bible completion to Voice Calibration. Your job is to guide the writer through discovering the narrative voice for their story.

## YOUR ROLE

Voice is everything in fiction. Before we write scenes, we must FIND the voice. You will:

1. EXPLAIN the voice calibration process
2. HELP the writer craft a test passage prompt
3. GUIDE selection of AI agents for the tournament
4. INTERPRET tournament results
5. REFINE voice calibration based on writer feedback
6. CONFIRM voice is locked before proceeding to Director mode

## VOICE CALIBRATION PROCESS

### Phase 1: Test Passage Design
- Help writer identify a KEY SCENE that will reveal voice
- Should include: dialogue, action, interiority, world details
- ~500 words of prose that exercises all voice muscles

### Phase 2: Agent Selection
- Present available agents (based on writer's API keys)
- Explain agent strengths/tendencies
- Recommend 3-5 agents for diverse perspectives

### Phase 3: Tournament
- Each agent generates 5 variants using different strategies:
  - ACTION_EMPHASIS: Fast pacing, physical detail, momentum
  - CHARACTER_DEPTH: Interior landscape, psychological truth
  - DIALOGUE_FOCUS: Voice through conversation
  - BRAINSTORMING: Idea exploration, multiple perspectives
  - BALANCED: Harmonious blend of all elements
- Total: 15-25 variants to review

### Phase 4: Selection & Refinement
- Guide writer through variant review
- Identify what WORKS and what DOESN'T
- Help articulate WHY certain passages resonate
- Document voice preferences for the Voice Bundle

### Phase 5: Voice Lock
- Confirm winning agent + strategy
- Generate Voice Reference Bundle
- These files travel with EVERY scene writing call

## VOICE BUNDLE CONTENTS

The bundle contains critical reference files:
- **Voice-Gold-Standard.md**: The winning passage + analysis
- **Voice-Anti-Pattern-Sheet.md**: What to AVOID
- **Phase-Evolution-Guide.md**: How voice adapts through story arcs

## CONVERSATION STYLE

- Be direct about the importance of this step
- Show enthusiasm for the craft of voice
- Challenge vague preferences ("I like it" → "What specifically?")
- Always connect voice choices to story requirements

## AVAILABLE ACTIONS

```json
{"action": "start_tournament", "test_prompt": "...", "agents": ["gpt-4o", "claude-sonnet"], "context": "..."}
{"action": "select_winner", "agent_id": "...", "variant_index": 0, "voice_notes": "..."}
{"action": "generate_bundle", "output_dir": "..."}
{"action": "advance_to_director", "confirm": true}
{"action": "save_decision", "category": "voice", "key": "...", "value": "...", "source": "calibration"}
```

## GUARD RAILS

You CANNOT advance to Director mode until:
- ✓ Tournament has been run
- ✓ Winner has been selected
- ✓ Voice Bundle has been generated
- ✓ Writer confirms voice lock

Always explain what you're doing and why before taking an action.
"""


DIRECTOR_SYSTEM_PROMPT = """# THE FOREMAN - DIRECTOR MODE

You are the Foreman in Director mode, guiding the writer through scene drafting.

## YOUR ROLE

With Story Bible complete and Voice calibrated, you now orchestrate scene creation:

1. MAINTAIN the beat sheet as your compass
2. ENSURE voice consistency using the Voice Bundle
3. GUIDE scene-by-scene progression
4. CHALLENGE scenes that drift from structure or voice
5. TRACK continuity across scenes
6. MONITOR manuscript health after completing chapters

## GRAPH HEALTH CHECKS (Phase 3D)

After completing a chapter, consider running a health check to catch structural issues early:

**When to run health checks:**
- After completing a chapter (recommended)
- After completing an act (milestone check)
- When the writer asks about pacing or structure
- Before major transitions (e.g., moving to Act 2 or 3)

**What health checks detect:**
- Pacing plateaus (flat tension across consecutive chapters)
- Beat structure deviations (15-beat alignment issues)
- Timeline consistency problems (character locations, world rules)
- Fatal Flaw challenge frequency (protagonist arc health)
- Supporting character underutilization
- Symbol and theme resonance at critical beats

**How to use:**
```json
{"action": "run_health_check", "scope": "chapter", "chapter_id": "chapter_4"}
```

If the health check reveals issues (score < 80), bring them to the writer's attention with specific recommendations from the report.

## SCAFFOLD GENERATION (Two-Stage Process)

Before writing any scene, generate a scaffold to ensure strategic alignment:

### Stage 1: Draft Summary
Present a quick preview to the writer:
- "Next up is Scene 4.1 - the Catalyst beat."
- Summarize what happens based on Beat Sheet
- List what context we already have
- Offer enrichment options: "Would you like to query your notebooks for more detail on [character voice / world building / craft reference]?"

### Stage 2: Full Scaffold (after writer confirms)
Generate the complete scaffold with:
- Chapter Overview (beat, voice state, core function)
- Strategic Context (conflict, goals, theme)
- Success Criteria (quality thresholds, voice requirements)
- Continuity Checklist (callbacks, foreshadowing)
- Any enrichment data from NotebookLM queries

## SCENE WRITING PROTOCOL

After scaffold is approved, every scene call includes:
- The scaffold document (strategic context)
- Voice Bundle files (mandatory)
- Relevant KB entries (character decisions, world rules)
- Continuity notes from previous scenes

## AVAILABLE ACTIONS

```json
{"action": "generate_draft_summary", "chapter": 4, "scene": 1, "beat": "catalyst", "description": "..."}
{"action": "enrich_scaffold", "notebook_id": "...", "query": "..."}
{"action": "generate_scaffold", "chapter": 4, "scene": 1, "title": "...", "enrichment": [...]}
{"action": "write_scene", "scaffold_id": "ch4-sc1", "context": {...}}
{"action": "query_notebook", "notebook_id": "...", "query": "..."}
{"action": "save_decision", "category": "continuity", "key": "...", "value": "...", "source": "scene"}
{"action": "run_health_check", "scope": "chapter", "chapter_id": "chapter_4"}
{"action": "advance_to_editor", "confirm": true}
```

## CONVERSATION STYLE

When presenting draft summaries, be conversational:
- "Alright, next up is Scene 4.1 - this is where the Catalyst hits..."
- "I have context on Jane's fatal flaw and her relationship with Joe."
- "Would you like me to ask your Character Voice notebook how Marcus typically speaks?"

Always explain what you're doing and why before taking an action.
"""


# =============================================================================
# The Foreman Agent
# =============================================================================

class Foreman:
    """
    The Foreman - Intelligent Creative Writing Partner.

    An Ollama-powered agent that guides writers through novel creation.
    """

    def __init__(
        self,
        model: str = "mistral:7b",
        ollama_url: str = "http://localhost:11434",
        notebooklm_client = None,
        story_bible_service = None,
        content_path: Path = None,
        kb_service: ForemanKBService = None,
    ):
        self.model = model
        self.ollama_url = ollama_url
        self.notebooklm_client = notebooklm_client
        self.story_bible_service = story_bible_service
        self.content_path = content_path or Path("content")

        # SQLite-backed Knowledge Base service
        self.kb_service = kb_service or get_foreman_kb_service()

        # State
        self.work_order: Optional[WorkOrder] = None
        self.conversation: List[ConversationMessage] = []
        self.kb_entries: List[KBEntry] = []  # In-memory cache (also persisted to SQLite)
        self.mode = ForemanMode.ARCHITECT

        # Voice calibration service (lazy loaded)
        self._voice_calibration_service = None

        # Director Mode services (lazy loaded)
        self._scaffold_service = None
        self._scene_writer_service = None
        self._scene_analyzer_service = None
        self._scene_enhancement_service = None

        # Action handlers
        self._action_handlers: Dict[str, Callable] = {
            "query_notebook": self._handle_query_notebook,
            "write_template": self._handle_write_template,
            "update_status": self._handle_update_status,
            "save_decision": self._handle_save_decision,
            # Voice calibration actions
            "start_tournament": self._handle_start_tournament,
            "select_winner": self._handle_select_winner,
            "generate_bundle": self._handle_generate_bundle,
            "advance_to_director": self._handle_advance_to_director,
            "advance_to_voice_calibration": self._handle_advance_to_voice_calibration,
            # Director Mode actions
            "generate_draft_summary": self._handle_generate_draft_summary,
            "enrich_scaffold": self._handle_enrich_scaffold,
            "generate_scaffold": self._handle_generate_scaffold,
            "write_scene": self._handle_write_scene,
            "analyze_scene": self._handle_analyze_scene,
            "enhance_scene": self._handle_enhance_scene,
            "advance_to_editor": self._handle_advance_to_editor,
            # Graph Health Check actions (Phase 3D)
            "run_health_check": self._handle_run_health_check,
        }

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def start_project(
        self,
        project_title: str,
        protagonist_name: str,
        notebooks: Dict[str, str] = None,
    ) -> Dict:
        """
        Start a new project with the Foreman.

        Args:
            project_title: Name of the novel project
            protagonist_name: Name of the protagonist
            notebooks: Dict mapping notebook_id to role (world, voice, craft)

        Returns:
            Initial work order and greeting
        """
        self.work_order = WorkOrder(
            project_title=project_title,
            protagonist_name=protagonist_name,
            notebooks=notebooks or {},
        )
        self.conversation = []
        self.kb_entries = []

        logger.info(f"Foreman starting project: {project_title}")

        return {
            "status": "started",
            "work_order": self.work_order.to_dict(),
            "message": f"Project '{project_title}' initialized. Ready to build Story Bible.",
        }

    def register_notebook(self, notebook_id: str, role: str) -> Dict:
        """Register a NotebookLM notebook with its role."""
        if not self.work_order:
            return {"error": "No active project. Call start_project first."}

        self.work_order.notebooks[notebook_id] = role

        # Save to KB
        self.kb_entries.append(KBEntry(
            entry_type="notebook",
            key=notebook_id,
            value=role,
            source="user_registration",
        ))

        return {
            "status": "registered",
            "notebook_id": notebook_id,
            "role": role,
        }

    # -------------------------------------------------------------------------
    # Conversation
    # -------------------------------------------------------------------------

    async def chat(self, user_message: str) -> Dict:
        """
        Send a message to the Foreman and get a response.

        The Foreman will:
        1. Consider the work order status
        2. Review relevant KB entries
        3. Respond with craft-aware guidance
        4. Optionally take actions (query, write, etc.)

        Phase 3E: Now uses intelligent model routing based on task complexity.

        Returns:
            Dict with response, any actions taken, and updated work order
        """
        if not self.work_order:
            return {"error": "No active project. Call start_project first."}

        # Add user message to conversation
        self.conversation.append(ConversationMessage(role="user", content=user_message))

        # Classify task complexity for model selection
        task_type = self._classify_task_complexity(user_message, self.get_context())

        # Get system prompt
        system_prompt = self._get_system_prompt()

        # Add work order status to system prompt
        work_order_status = self.work_order.get_status_summary()
        system_prompt += f"\n\n## CURRENT WORK ORDER\n\n```\n{work_order_status}\n```"

        # Add KB context
        kb_context = self._get_kb_context()
        if kb_context:
            system_prompt += f"\n\n## KNOWLEDGE BASE (Relevant Entries)\n\n{kb_context}"

        # Build conversation history for prompt (last N messages)
        conversation_history = "\n\n".join([
            f"{msg.role.upper()}: {msg.content}"
            for msg in self.conversation[-10:]  # Last 10 messages for context
        ])

        # Query with task-appropriate model (Phase 3E)
        response_text = await self._query_llm(
            prompt=conversation_history,
            system_prompt=system_prompt,
            task_type=task_type  # Triggers automatic model selection
        )

        # Add assistant response to conversation
        self.conversation.append(ConversationMessage(role="assistant", content=response_text))

        # Parse and execute any actions
        actions_taken = await self._parse_and_execute_actions(response_text)

        return {
            "response": response_text,
            "actions": actions_taken,
            "work_order": self.work_order.to_dict(),
            "kb_entries_pending": len(self.kb_entries),
            "model_routing": {
                "task_type": task_type,
                "is_advisor_task": task_type != "coordinator"
            }
        }

    def _build_context(self) -> List[Dict]:
        """Build the context window for Ollama."""
        messages = []

        # System prompt (mode-specific)
        system_prompt = self._get_system_prompt()

        # Add work order status to system prompt
        work_order_status = self.work_order.get_status_summary()
        system_prompt += f"\n\n## CURRENT WORK ORDER\n\n```\n{work_order_status}\n```"

        # Add any relevant KB context
        kb_context = self._get_kb_context()
        if kb_context:
            system_prompt += f"\n\n## KNOWLEDGE BASE (Relevant Entries)\n\n{kb_context}"

        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history (last N messages to fit context)
        max_messages = 20  # Adjust based on context window
        for msg in self.conversation[-max_messages:]:
            messages.append({"role": msg.role, "content": msg.content})

        return messages

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the current mode."""
        prompts = {
            ForemanMode.ARCHITECT: ARCHITECT_SYSTEM_PROMPT,
            ForemanMode.VOICE_CALIBRATION: VOICE_CALIBRATION_SYSTEM_PROMPT,
            ForemanMode.DIRECTOR: DIRECTOR_SYSTEM_PROMPT,
            ForemanMode.EDITOR: DIRECTOR_SYSTEM_PROMPT,  # TODO: Add EDITOR prompt
        }
        return prompts.get(self.mode, ARCHITECT_SYSTEM_PROMPT)

    def _get_kb_context(self) -> str:
        """
        Get relevant KB entries for context.

        Reads from SQLite for persisted decisions (survives restarts),
        falling back to in-memory cache if no project is active.
        """
        if not self.work_order:
            return ""

        # Get persisted context from SQLite
        context = self.kb_service.get_context_for_foreman(
            project_id=self.work_order.project_title,
            limit=20
        )

        if context:
            return context

        # Fallback to in-memory if SQLite is empty
        if not self.kb_entries:
            return ""

        lines = ["## Known Decisions & Facts"]
        for entry in self.kb_entries[-10:]:
            lines.append(f"- [{entry.entry_type}] {entry.key}: {entry.value}")
        return "\n".join(lines)

    def get_context(self) -> Dict:
        """Get current context for task classification."""
        return {
            "work_order": self.work_order.to_dict() if self.work_order else None,
            "mode": self.mode.value,
            "conversation_length": len(self.conversation),
        }

    # -------------------------------------------------------------------------
    # Ollama Integration
    # -------------------------------------------------------------------------

    async def _call_ollama(self, messages: List[Dict]) -> str:
        """Call Ollama API with the given messages."""
        url = f"{self.ollama_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        logger.info(f"Calling Ollama at {url} with model {self.model}")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)
                logger.info(f"Ollama response status: {response.status_code}")
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            return "I apologize, but I'm having trouble thinking right now. Please try again."
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"Error communicating with Ollama: {str(e)}"

    # -------------------------------------------------------------------------
    # Phase 3E: Multi-Model Cloud Integration
    # -------------------------------------------------------------------------

    def _detect_available_providers(self) -> Dict[str, bool]:
        """Detect which cloud providers have API keys configured."""
        return {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "deepseek": bool(os.getenv("DEEPSEEK_API_KEY")),
            "qwen": bool(os.getenv("QWEN_API_KEY")),
        }

    async def _query_openai(self, prompt: str, system_prompt: str, model: str) -> str:
        """Query OpenAI models (GPT-4o, etc.)."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found, falling back to Ollama")
            return await self._query_ollama(prompt, system_prompt, self.model)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                    }
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI query failed: {e}, falling back to Ollama")
            return await self._query_ollama(prompt, system_prompt, self.model)

    async def _query_anthropic(self, prompt: str, system_prompt: str, model: str) -> str:
        """Query Anthropic models (Claude Sonnet, etc.)."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not found, falling back to Ollama")
            return await self._query_ollama(prompt, system_prompt, self.model)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": model,
                        "max_tokens": 4096,
                        "system": system_prompt,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                response.raise_for_status()
                return response.json()["content"][0]["text"]
        except Exception as e:
            logger.error(f"Anthropic query failed: {e}, falling back to Ollama")
            return await self._query_ollama(prompt, system_prompt, self.model)

    async def _query_deepseek(self, prompt: str, system_prompt: str, model: str) -> str:
        """Query DeepSeek models."""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.warning("DEEPSEEK_API_KEY not found, falling back to Ollama")
            return await self._query_ollama(prompt, system_prompt, self.model)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ]
                    }
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek query failed: {e}, falling back to Ollama")
            return await self._query_ollama(prompt, system_prompt, self.model)

    async def _query_qwen(self, prompt: str, system_prompt: str, model: str) -> str:
        """Query Qwen (Alibaba) models."""
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            logger.warning("QWEN_API_KEY not found, falling back to Ollama")
            return await self._query_ollama(prompt, system_prompt, self.model)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "input": {
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ]
                        }
                    }
                )
                response.raise_for_status()
                return response.json()["output"]["text"]
        except Exception as e:
            logger.error(f"Qwen query failed: {e}, falling back to Ollama")
            return await self._query_ollama(prompt, system_prompt, self.model)

    async def _query_llm(
        self,
        prompt: str,
        system_prompt: str,
        model: str = None,
        task_type: str = "coordinator"
    ) -> str:
        """
        Query LLM with intelligent model selection.

        Phase 3E: Uses configurable task-specific models from settings.

        Args:
            prompt: User message
            system_prompt: System context
            model: Optional specific model (overrides automatic selection)
            task_type: Type of task for automatic routing

        Returns:
            LLM response text
        """
        # Load settings
        from backend.services.settings_service import settings_service
        from backend.services.model_orchestrator import orchestrator, SelectionCriteria

        foreman_settings = settings_service.get_category("foreman")
        orchestrator_settings = settings_service.get_category("orchestrator")

        # Determine which model to use
        if model is None:
            # Check if orchestrator is enabled (Phase 3E)
            if orchestrator_settings.get("enabled", False):
                # Use orchestrator for automatic model selection
                criteria = SelectionCriteria(
                    task_type=task_type,
                    quality_tier=orchestrator_settings.get("quality_tier", "balanced"),
                    monthly_budget=orchestrator_settings.get("monthly_budget"),
                    current_month_spend=orchestrator_settings.get("current_month_spend", 0.0),
                    prefer_local=orchestrator_settings.get("prefer_local", False)
                )
                model = orchestrator.select_model(criteria)
                logger.info(f"🎯 Orchestrator selected {model} for {task_type} ({criteria.quality_tier} tier)")
            else:
                # Use manual task_models configuration (existing behavior)
                task_models = foreman_settings.get("task_models", {})
                model = task_models.get(task_type, foreman_settings.get("coordinator_model", "mistral"))

                # Log model selection with visual indicators
                if task_type == "coordinator":
                    logger.debug(f"📋 Using {model} for {task_type}")
                else:
                    logger.info(f"🧠 Using {model} for {task_type}")

        # Route to appropriate provider based on model name
        if model.startswith("gpt-"):
            return await self._query_openai(prompt, system_prompt, model)
        elif model.startswith("claude-"):
            return await self._query_anthropic(prompt, system_prompt, model)
        elif model.startswith("deepseek-"):
            return await self._query_deepseek(prompt, system_prompt, model)
        elif model.startswith("qwen-"):
            return await self._query_qwen(prompt, system_prompt, model)
        else:
            # Default to Ollama for local models (mistral, llama, etc.)
            return await self._query_ollama(prompt, system_prompt, model)

    async def _query_ollama(self, prompt: str, system_prompt: str, model: str) -> str:
        """Query local Ollama models."""
        url = f"{self.ollama_url}/api/chat"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        logger.debug(f"Calling Ollama at {url} with model {model}")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"Error communicating with Ollama: {str(e)}"

    def _classify_task_complexity(self, message: str, context: Dict = None) -> str:
        """
        Classify task to determine if advisor model is needed.

        Returns: Task type string (e.g., "health_check_review", "coordinator")
        """
        message_lower = message.lower()

        # Health check interpretation
        if any(word in message_lower for word in ["health check", "score", "interpret", "what does this mean"]):
            return "health_check_review"

        # Voice calibration guidance
        if any(word in message_lower for word in ["voice", "tournament", "which variant", "calibration"]):
            return "voice_calibration_guidance"

        # Beat structure advice
        if any(word in message_lower for word in ["beat", "structure", "pacing", "act", "midpoint"]):
            return "beat_structure_advice"

        # Conflict resolution
        if any(word in message_lower for word in ["conflict", "contradiction", "timeline issue", "consistency"]):
            return "conflict_resolution"

        # Scaffold enrichment
        if any(word in message_lower for word in ["enrich", "scaffold", "notebook", "research"]):
            return "scaffold_enrichment_decisions"

        # Theme analysis
        if any(word in message_lower for word in ["theme", "symbolism", "meaning", "resonance"]):
            return "theme_analysis"

        # Structural planning
        if any(word in message_lower for word in ["plan", "outline", "strategy", "approach"]):
            return "structural_planning"

        # Default to simple coordination
        return "coordinator"

    # -------------------------------------------------------------------------
    # Action Handling
    # -------------------------------------------------------------------------

    async def _parse_and_execute_actions(self, response: str) -> List[Dict]:
        """Parse response for action blocks and execute them."""
        actions_taken = []

        # Look for JSON action blocks
        import re
        json_pattern = r'```json\s*(\{[^`]+\})\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)

        for match in matches:
            try:
                action_data = json.loads(match)
                action_type = action_data.get("action")

                if action_type in self._action_handlers:
                    result = await self._action_handlers[action_type](action_data)
                    actions_taken.append({
                        "action": action_type,
                        "data": action_data,
                        "result": result,
                    })
                else:
                    logger.warning(f"Unknown action type: {action_type}")

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse action JSON: {e}")

        return actions_taken

    async def _handle_query_notebook(self, action: Dict) -> Dict:
        """Handle a notebook query action."""
        if not self.notebooklm_client:
            return {"error": "NotebookLM client not configured"}

        notebook_id = action.get("notebook_id")
        query = action.get("query")

        if not notebook_id or not query:
            return {"error": "Missing notebook_id or query"}

        try:
            response = await self.notebooklm_client.query_notebook(notebook_id, query)
            return {
                "status": "success",
                "answer": response.answer,
                "sources": response.sources,
            }
        except Exception as e:
            logger.error(f"NotebookLM query failed: {e}")
            return {"error": str(e)}

    async def _handle_write_template(self, action: Dict) -> Dict:
        """Handle a template write action."""
        if not self.story_bible_service:
            return {"error": "Story Bible service not configured"}

        template = action.get("template")
        content = action.get("content", {})

        # Map template name to service method
        # For now, use the scaffold method with pre-filled data
        try:
            if template == "protagonist":
                result = self.story_bible_service.scaffold_story_bible(
                    project_title=self.work_order.project_title,
                    protagonist_name=self.work_order.protagonist_name,
                    pre_filled={"protagonist": content},
                )
                return {"status": "success", "files": result.get("created_files", [])}
            else:
                return {"error": f"Unknown template: {template}"}
        except Exception as e:
            logger.error(f"Template write failed: {e}")
            return {"error": str(e)}

    async def _handle_update_status(self, action: Dict) -> Dict:
        """Handle a status update action."""
        template_name = action.get("template")
        new_status = action.get("status")
        missing = action.get("missing", [])

        # Find the template
        for t in self.work_order.templates:
            if t.name.lower() == template_name.lower():
                t.status = TemplateStatus(new_status)
                t.missing_fields = missing
                t.last_updated = datetime.now(timezone.utc).isoformat()
                return {"status": "updated", "template": t.to_dict()}

        return {"error": f"Template not found: {template_name}"}

    async def _handle_save_decision(self, action: Dict) -> Dict:
        """
        Handle a decision save action - writes to SQLite immediately.

        Per Gemini Architect: SQLite for immediate writes (survives crashes),
        Consolidator later promotes "hard facts" to knowledge_graph.json.
        """
        key = action.get("key")
        value = action.get("value")
        source = action.get("source", "foreman")
        category = action.get("category", "decision")  # character, world, structure, constraint, preference

        if not self.work_order:
            return {"error": "No active project"}

        # Persist to SQLite immediately
        try:
            db_entry = self.kb_service.save_decision(
                project_id=self.work_order.project_title,  # Use project title as ID
                category=category,
                key=key,
                value=value,
                source=source,
            )
            logger.info(f"KB decision persisted: {key}")

            # Also keep in-memory cache for context
            entry = KBEntry(
                entry_type=category,
                key=key,
                value=value,
                source=source,
            )
            self.kb_entries.append(entry)

            return {"status": "saved", "entry": db_entry.to_dict()}
        except Exception as e:
            logger.error(f"Failed to persist KB decision: {e}")
            return {"error": str(e)}

    # -------------------------------------------------------------------------
    # Voice Calibration Actions
    # -------------------------------------------------------------------------

    def _get_voice_calibration_service(self):
        """Lazy-load the VoiceCalibrationService."""
        if self._voice_calibration_service is None:
            from backend.services.voice_calibration_service import VoiceCalibrationService
            self._voice_calibration_service = VoiceCalibrationService()
        return self._voice_calibration_service

    async def _handle_advance_to_voice_calibration(self, action: Dict) -> Dict:
        """
        Handle transition from ARCHITECT to VOICE_CALIBRATION mode.

        Requires Story Bible to be complete.
        """
        if not self.work_order:
            return {"error": "No active project"}

        # Check if Story Bible is complete
        if not self.work_order.is_complete:
            incomplete = [
                t.name for t in self.work_order.templates
                if t.status != TemplateStatus.COMPLETE
            ]
            return {
                "error": "Story Bible not complete",
                "incomplete_templates": incomplete,
                "message": f"Complete these templates first: {', '.join(incomplete)}"
            }

        # Transition to Voice Calibration
        self.mode = ForemanMode.VOICE_CALIBRATION
        self.work_order.mode = ForemanMode.VOICE_CALIBRATION

        # Save the transition decision
        await self._handle_save_decision({
            "category": "mode_transition",
            "key": "entered_voice_calibration",
            "value": datetime.now(timezone.utc).isoformat(),
            "source": "foreman"
        })

        logger.info(f"Transitioned to VOICE_CALIBRATION mode for {self.work_order.project_title}")

        return {
            "status": "transitioned",
            "new_mode": "voice_calibration",
            "message": "Story Bible complete! Now entering Voice Calibration mode."
        }

    async def _handle_start_tournament(self, action: Dict) -> Dict:
        """Handle starting a voice calibration tournament."""
        if self.mode != ForemanMode.VOICE_CALIBRATION:
            return {"error": "Must be in VOICE_CALIBRATION mode to start tournament"}

        test_prompt = action.get("test_prompt")
        agents = action.get("agents", [])
        context = action.get("context", "")

        if not test_prompt:
            return {"error": "Missing test_prompt for tournament"}

        vc_service = self._get_voice_calibration_service()

        # If no agents specified, get all ready agents
        if not agents:
            ready = vc_service.get_ready_agents("tournament")
            agents = [a.id for a in ready]

        if not agents:
            return {"error": "No agents available for tournament. Check API key configuration."}

        try:
            result = await vc_service.start_tournament(
                project_id=self.work_order.project_title,
                test_prompt=test_prompt,
                test_context=context,
                agent_ids=agents,
                variants_per_agent=5,
                voice_description=None
            )

            # Save tournament start to KB
            await self._handle_save_decision({
                "category": "voice",
                "key": "tournament_started",
                "value": {
                    "tournament_id": result.tournament_id,
                    "agents": agents,
                    "test_prompt": test_prompt[:200]  # Truncate for KB
                },
                "source": "voice_calibration"
            })

            return {
                "status": "tournament_started",
                "tournament_id": result.tournament_id,
                "agents_count": len(result.variants),
                "total_variants": sum(len(v) for v in result.variants.values()),
                "message": f"Tournament started with {len(agents)} agents. Review variants to select winner."
            }
        except Exception as e:
            logger.error(f"Tournament start failed: {e}")
            return {"error": str(e)}

    async def _handle_select_winner(self, action: Dict) -> Dict:
        """Handle selecting the winning voice from tournament."""
        if self.mode != ForemanMode.VOICE_CALIBRATION:
            return {"error": "Must be in VOICE_CALIBRATION mode to select winner"}

        agent_id = action.get("agent_id")
        variant_index = action.get("variant_index", 0)
        voice_notes = action.get("voice_notes", "")

        if not agent_id:
            return {"error": "Missing agent_id for winner selection"}

        vc_service = self._get_voice_calibration_service()

        try:
            # Get the latest tournament for this project
            tournaments = vc_service.tournaments.get(self.work_order.project_title, {})
            if not tournaments:
                return {"error": "No tournament found. Start a tournament first."}

            # Get most recent tournament
            tournament_id = list(tournaments.keys())[-1]

            result = await vc_service.select_winner(
                tournament_id=tournament_id,
                winner_agent_id=agent_id,
                winner_variant_index=variant_index,
                voice_config={
                    "voice_notes": voice_notes,
                    "selected_by": "writer",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

            # Save winner to KB
            await self._handle_save_decision({
                "category": "voice",
                "key": "winning_agent",
                "value": {
                    "agent_id": agent_id,
                    "variant_index": variant_index,
                    "voice_notes": voice_notes
                },
                "source": "voice_calibration"
            })

            return {
                "status": "winner_selected",
                "document": result.to_dict() if hasattr(result, 'to_dict') else str(result),
                "message": f"Voice winner selected: {agent_id}. Generate bundle to lock voice."
            }
        except Exception as e:
            logger.error(f"Winner selection failed: {e}")
            return {"error": str(e)}

    async def _handle_generate_bundle(self, action: Dict) -> Dict:
        """Handle generating the Voice Reference Bundle."""
        if self.mode != ForemanMode.VOICE_CALIBRATION:
            return {"error": "Must be in VOICE_CALIBRATION mode to generate bundle"}

        output_dir = action.get("output_dir")
        if not output_dir:
            output_dir = self.content_path / self.work_order.project_title / "Voice"

        vc_service = self._get_voice_calibration_service()

        try:
            bundle_paths = await vc_service.generate_voice_bundle(
                project_id=self.work_order.project_title,
                output_dir=Path(output_dir)
            )

            # Save bundle generation to KB
            await self._handle_save_decision({
                "category": "voice",
                "key": "voice_bundle_generated",
                "value": {
                    "files": [str(p) for p in bundle_paths.values()],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "source": "voice_calibration"
            })

            return {
                "status": "bundle_generated",
                "files": {k: str(v) for k, v in bundle_paths.items()},
                "message": "Voice Bundle generated. Ready to advance to Director mode."
            }
        except Exception as e:
            logger.error(f"Bundle generation failed: {e}")
            return {"error": str(e)}

    async def _handle_advance_to_director(self, action: Dict) -> Dict:
        """
        Handle transition from VOICE_CALIBRATION to DIRECTOR mode.

        Requires voice to be locked (bundle generated).
        """
        if not self.work_order:
            return {"error": "No active project"}

        if self.mode != ForemanMode.VOICE_CALIBRATION:
            return {"error": "Must be in VOICE_CALIBRATION mode first"}

        # Check if voice bundle exists
        vc_service = self._get_voice_calibration_service()
        calibration = vc_service.kb_storage.get(self.work_order.project_title)

        if not calibration or not calibration.get("voice_bundle_generated"):
            return {
                "error": "Voice not locked",
                "message": "Generate the Voice Bundle first before advancing to Director mode."
            }

        confirm = action.get("confirm", False)
        if not confirm:
            return {
                "status": "confirmation_required",
                "message": "Set confirm: true to advance to Director mode. This locks your voice choice."
            }

        # Transition to Director mode
        self.mode = ForemanMode.DIRECTOR
        self.work_order.mode = ForemanMode.DIRECTOR

        # Save the transition decision
        await self._handle_save_decision({
            "category": "mode_transition",
            "key": "entered_director",
            "value": datetime.now(timezone.utc).isoformat(),
            "source": "foreman"
        })

        logger.info(f"Transitioned to DIRECTOR mode for {self.work_order.project_title}")

        return {
            "status": "transitioned",
            "new_mode": "director",
            "message": "Voice locked! Now entering Director mode. Ready to write scenes."
        }

    def can_advance_to_voice_calibration(self) -> Dict:
        """Check if we can advance to Voice Calibration mode."""
        if not self.work_order:
            return {"can_advance": False, "reason": "No active project"}

        if self.mode != ForemanMode.ARCHITECT:
            return {"can_advance": False, "reason": f"Already in {self.mode.value} mode"}

        if not self.work_order.is_complete:
            incomplete = [
                t.name for t in self.work_order.templates
                if t.status != TemplateStatus.COMPLETE
            ]
            return {
                "can_advance": False,
                "reason": "Story Bible not complete",
                "incomplete_templates": incomplete
            }

        return {"can_advance": True, "reason": "Story Bible complete"}

    def can_advance_to_director(self) -> Dict:
        """Check if we can advance to Director mode."""
        if not self.work_order:
            return {"can_advance": False, "reason": "No active project"}

        if self.mode != ForemanMode.VOICE_CALIBRATION:
            return {"can_advance": False, "reason": f"Must be in voice_calibration mode, currently in {self.mode.value}"}

        vc_service = self._get_voice_calibration_service()
        calibration = vc_service.kb_storage.get(self.work_order.project_title)

        if not calibration or not calibration.get("voice_bundle_generated"):
            return {
                "can_advance": False,
                "reason": "Voice Bundle not generated",
                "steps_remaining": ["Select tournament winner", "Generate Voice Bundle"]
            }

        return {"can_advance": True, "reason": "Voice calibration complete"}

    # -------------------------------------------------------------------------
    # Director Mode Actions
    # -------------------------------------------------------------------------

    def _get_director_services(self):
        """Lazy-load all Director Mode services."""
        if self._scaffold_service is None:
            from backend.services.scaffold_generator_service import ScaffoldGeneratorService
            from backend.services.scene_writer_service import SceneWriterService
            from backend.services.scene_analyzer_service import SceneAnalyzerService
            from backend.services.scene_enhancement_service import SceneEnhancementService

            self._scaffold_service = ScaffoldGeneratorService()
            self._scene_writer_service = SceneWriterService()
            self._scene_analyzer_service = SceneAnalyzerService()
            self._scene_enhancement_service = SceneEnhancementService()

        return {
            "scaffold": self._scaffold_service,
            "writer": self._scene_writer_service,
            "analyzer": self._scene_analyzer_service,
            "enhancement": self._scene_enhancement_service,
        }

    async def _handle_generate_draft_summary(self, action: Dict) -> Dict:
        """
        Handle generating a draft scaffold summary.

        Action format:
        {"action": "generate_draft_summary", "chapter": 4, "scene": 1,
         "beat": "catalyst", "description": "..."}
        """
        if self.mode != ForemanMode.DIRECTOR:
            return {"error": "Must be in DIRECTOR mode to generate scaffolds"}

        if not self.work_order:
            return {"error": "No active project"}

        from backend.services.scaffold_generator_service import BeatInfo, CharacterContext

        services = self._get_director_services()
        scaffold_service = services["scaffold"]

        # Build BeatInfo from action
        beat_info = BeatInfo(
            beat_number=action.get("beat_number", 1),
            beat_name=action.get("beat", "Unknown Beat"),
            beat_percentage=action.get("beat_percentage", ""),
            description=action.get("description", ""),
            beat_type=action.get("beat_type", ""),
        )

        # Build character context from work order
        characters = [
            CharacterContext(
                name=self.work_order.protagonist_name,
                role="protagonist",
            )
        ]

        try:
            result = await scaffold_service.generate_draft_summary(
                project_id=self.work_order.project_title,
                chapter_number=action.get("chapter", 1),
                scene_number=action.get("scene", 1),
                beat_info=beat_info,
                characters=characters,
                scene_description=action.get("description", ""),
            )

            return {
                "status": "success",
                "scene_id": result.scene_id,
                "summary": result.narrative_summary,
                "ready_to_generate": result.ready_to_generate,
                "enrichment_suggestions": [s.to_dict() for s in result.enrichment_suggestions] if result.enrichment_suggestions else [],
            }
        except Exception as e:
            logger.error(f"Draft summary generation failed: {e}")
            return {"error": str(e)}

    async def _handle_enrich_scaffold(self, action: Dict) -> Dict:
        """
        Handle enriching scaffold with NotebookLM data.

        Action format:
        {"action": "enrich_scaffold", "notebook_id": "...", "query": "..."}
        """
        if self.mode != ForemanMode.DIRECTOR:
            return {"error": "Must be in DIRECTOR mode"}

        # Use existing notebook query handler
        return await self._handle_query_notebook(action)

    async def _handle_generate_scaffold(self, action: Dict) -> Dict:
        """
        Handle generating a full scaffold after enrichment.

        Action format:
        {"action": "generate_scaffold", "chapter": 4, "scene": 1,
         "title": "...", "enrichment": [...]}
        """
        if self.mode != ForemanMode.DIRECTOR:
            return {"error": "Must be in DIRECTOR mode"}

        if not self.work_order:
            return {"error": "No active project"}

        from backend.services.scaffold_generator_service import BeatInfo, CharacterContext

        services = self._get_director_services()
        scaffold_service = services["scaffold"]

        beat_info = BeatInfo(
            beat_number=action.get("beat_number", 1),
            beat_name=action.get("beat", "Unknown Beat"),
            beat_percentage=action.get("beat_percentage", ""),
            description=action.get("description", ""),
            beat_type=action.get("beat_type", ""),
        )

        characters = [
            CharacterContext(
                name=self.work_order.protagonist_name,
                role="protagonist",
            )
        ]

        try:
            result = await scaffold_service.generate_full_scaffold(
                project_id=self.work_order.project_title,
                chapter_number=action.get("chapter", 1),
                scene_number=action.get("scene", 1),
                title=action.get("title", f"Chapter {action.get('chapter', 1)}, Scene {action.get('scene', 1)}"),
                beat_info=beat_info,
                characters=characters,
                scene_description=action.get("description", ""),
                enrichment_data=action.get("enrichment", []),
            )

            return {
                "status": "success",
                "scaffold": result.to_dict(),
            }
        except Exception as e:
            logger.error(f"Scaffold generation failed: {e}")
            return {"error": str(e)}

    async def _handle_write_scene(self, action: Dict) -> Dict:
        """
        Handle writing a scene using the SceneWriterService.

        Action format:
        {"action": "write_scene", "scaffold_id": "ch4-sc1",
         "structure_variant": "A", "strategy": "BALANCED"}
        """
        if self.mode != ForemanMode.DIRECTOR:
            return {"error": "Must be in DIRECTOR mode"}

        services = self._get_director_services()
        writer_service = services["writer"]

        scene_id = action.get("scaffold_id", action.get("scene_id", "unknown"))
        strategy = action.get("strategy", "BALANCED")

        try:
            # Use quick_generate for single scene generation
            result = await writer_service.generate_single_scene(
                scene_id=scene_id,
                beat_description=action.get("beat_description", ""),
                voice_bundle=None,  # TODO: Load from voice bundle path
                strategy=strategy,
                target_word_count=action.get("target_word_count", "1500-2000"),
            )

            return {
                "status": "success",
                "scene_id": scene_id,
                "content": result.content if hasattr(result, 'content') else str(result),
                "word_count": result.word_count if hasattr(result, 'word_count') else None,
            }
        except Exception as e:
            logger.error(f"Scene writing failed: {e}")
            return {"error": str(e)}

    async def _handle_analyze_scene(self, action: Dict) -> Dict:
        """
        Handle analyzing a scene for quality scoring.

        Action format:
        {"action": "analyze_scene", "scene_id": "ch4-sc1", "content": "..."}
        """
        if self.mode != ForemanMode.DIRECTOR:
            return {"error": "Must be in DIRECTOR mode"}

        services = self._get_director_services()
        analyzer_service = services["analyzer"]

        scene_id = action.get("scene_id", "unknown")
        content = action.get("content", "")

        if not content:
            return {"error": "Missing scene content"}

        try:
            result = await analyzer_service.analyze_scene(
                scene_id=scene_id,
                scene_content=content,
                voice_bundle=None,
                story_bible=None,
                pov_character=action.get("pov_character", self.work_order.protagonist_name if self.work_order else "protagonist"),
                phase=action.get("phase", "act2"),
            )

            return {
                "status": "success",
                "scene_id": scene_id,
                "total_score": result.total_score,
                "grade": result.grade,
                "recommended_mode": result.recommended_mode,
                "categories": {k: v.to_dict() for k, v in result.categories.items()},
                "violations": len(result.violations),
                "enhancement_needed": result.enhancement_needed,
            }
        except Exception as e:
            logger.error(f"Scene analysis failed: {e}")
            return {"error": str(e)}

    async def _handle_enhance_scene(self, action: Dict) -> Dict:
        """
        Handle enhancing a scene based on its score.

        Action format:
        {"action": "enhance_scene", "scene_id": "ch4-sc1", "content": "...",
         "force_mode": "six_pass"}
        """
        if self.mode != ForemanMode.DIRECTOR:
            return {"error": "Must be in DIRECTOR mode"}

        services = self._get_director_services()
        analyzer_service = services["analyzer"]
        enhancement_service = services["enhancement"]

        scene_id = action.get("scene_id", "unknown")
        content = action.get("content", "")

        if not content:
            return {"error": "Missing scene content"}

        try:
            # First analyze
            analysis = await analyzer_service.analyze_scene(
                scene_id=scene_id,
                scene_content=content,
                voice_bundle=None,
                story_bible=None,
            )

            # Determine force mode
            force_mode = None
            if action.get("force_mode"):
                from backend.services.scene_enhancement_service import EnhancementMode
                force_mode = EnhancementMode(action["force_mode"])

            # Then enhance
            result = await enhancement_service.enhance_scene(
                scene_id=scene_id,
                scene_content=content,
                analysis=analysis,
                voice_bundle=None,
                story_bible=None,
                force_mode=force_mode,
            )

            return {
                "status": "enhanced" if result.mode.value != "rewrite" else "rewrite_needed",
                "scene_id": scene_id,
                "mode_used": result.mode.value,
                "original_score": result.original_score,
                "final_score": result.final_score,
                "enhanced_content": result.enhanced_content,
                "passes_completed": len(result.passes_completed) if result.passes_completed else 0,
            }
        except Exception as e:
            logger.error(f"Scene enhancement failed: {e}")
            return {"error": str(e)}

    async def _handle_run_health_check(self, action: Dict) -> Dict:
        """
        Handle running a health check on manuscript structure (Phase 3D).

        Action format:
        {"action": "run_health_check", "scope": "chapter", "chapter_id": "chapter_4.2"}
        {"action": "run_health_check", "scope": "act", "act_number": 2}
        {"action": "run_health_check", "scope": "manuscript"}

        Strategic Decision 3: Auto-trigger after chapter completion
        - Respects foreman proactiveness setting (high/medium/low)
        - High: Auto-run and notify on warnings
        - Medium: Auto-run but only notify on errors
        - Low: Manual trigger only
        """
        if self.mode not in [ForemanMode.DIRECTOR, ForemanMode.EDITOR]:
            return {"error": "Health checks only available in DIRECTOR or EDITOR mode"}

        if not self.work_order:
            return {"error": "No active project"}

        from backend.services.graph_health_service import get_graph_health_service

        scope = action.get("scope", "chapter")
        chapter_id = action.get("chapter_id")
        act_number = action.get("act_number")

        try:
            # Get health service for this project
            health_service = get_graph_health_service(self.work_order.project_title)

            # Run appropriate health check based on scope
            if scope == "chapter":
                if not chapter_id:
                    return {"error": "chapter_id required for chapter scope"}
                report = await health_service.run_chapter_health_check(chapter_id)

            elif scope == "act":
                if not act_number:
                    return {"error": "act_number required for act scope"}
                report = await health_service.run_act_health_check(act_number)

            elif scope == "manuscript":
                report = await health_service.run_full_manuscript_check()

            else:
                return {"error": f"Invalid scope: {scope}"}

            # Extract key metrics for Foreman's awareness
            warnings_by_severity = {
                "error": [w for w in report.warnings if w.severity == "error"],
                "warning": [w for w in report.warnings if w.severity == "warning"],
                "info": [w for w in report.warnings if w.severity == "info"],
            }

            # Save key findings to KB if significant
            if warnings_by_severity["error"]:
                await self._handle_save_decision({
                    "category": "health_check",
                    "key": f"health_issues_{scope}_{chapter_id or act_number or 'manuscript'}",
                    "value": {
                        "report_id": report.report_id,
                        "overall_score": report.overall_score,
                        "error_count": len(warnings_by_severity["error"]),
                        "warning_count": len(warnings_by_severity["warning"]),
                        "timestamp": report.timestamp,
                    },
                    "source": "graph_health_service"
                })

            return {
                "status": "complete",
                "report_id": report.report_id,
                "scope": scope,
                "overall_score": report.overall_score,
                "warnings": {
                    "error_count": len(warnings_by_severity["error"]),
                    "warning_count": len(warnings_by_severity["warning"]),
                    "info_count": len(warnings_by_severity["info"]),
                },
                "top_issues": [
                    {
                        "type": w.type,
                        "severity": w.severity,
                        "message": w.message,
                        "recommendation": w.recommendation,
                    }
                    for w in (warnings_by_severity["error"][:3] + warnings_by_severity["warning"][:3])
                ],
                "markdown_summary": report.to_markdown()[:500] + "..." if len(report.to_markdown()) > 500 else report.to_markdown(),
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"error": str(e)}

    async def _handle_advance_to_editor(self, action: Dict) -> Dict:
        """
        Handle transition from DIRECTOR to EDITOR mode.

        Action format:
        {"action": "advance_to_editor", "confirm": true}
        """
        if self.mode != ForemanMode.DIRECTOR:
            return {"error": "Must be in DIRECTOR mode to advance to EDITOR"}

        if not action.get("confirm"):
            return {"error": "Must confirm advancement with 'confirm': true"}

        # TODO: Check if all scenes are complete before advancing

        self.mode = ForemanMode.EDITOR
        if self.work_order:
            self.work_order.mode = ForemanMode.EDITOR

        await self._handle_save_decision({
            "category": "mode_transition",
            "key": "entered_editor",
            "value": datetime.now(timezone.utc).isoformat(),
            "source": "foreman"
        })

        logger.info(f"Transitioned to EDITOR mode for {self.work_order.project_title if self.work_order else 'unknown'}")

        return {
            "status": "transitioned",
            "new_mode": "editor",
            "message": "Director Mode complete! Now entering Editor mode for revision and polish."
        }

    # -------------------------------------------------------------------------
    # KB Operations
    # -------------------------------------------------------------------------

    def flush_kb_entries(self) -> Dict:
        """
        Get KB stats and clear in-memory cache.

        With SQLite persistence, entries are already saved immediately.
        This method now returns stats and clears the in-memory cache.
        """
        in_memory_count = len(self.kb_entries)
        self.kb_entries = []

        if self.work_order:
            stats = self.kb_service.get_stats(self.work_order.project_title)
            return {
                "flushed_from_memory": in_memory_count,
                "persisted_stats": stats,
            }
        return {"flushed_from_memory": in_memory_count}

    def clear_project_kb(self) -> int:
        """
        Clear all KB entries for the current project.

        Called when resetting the Foreman for a new project.
        """
        if not self.work_order:
            return 0

        deleted = self.kb_service.delete_project_kb(self.work_order.project_title)
        self.kb_entries = []
        return deleted

    def get_kb_stats(self) -> Dict:
        """Get KB statistics for the current project."""
        if not self.work_order:
            return {"error": "No active project"}

        return self.kb_service.get_stats(self.work_order.project_title)

    # -------------------------------------------------------------------------
    # State Management
    # -------------------------------------------------------------------------

    def get_state(self) -> Dict:
        """Get the current Foreman state for persistence."""
        return {
            "work_order": self.work_order.to_dict() if self.work_order else None,
            "conversation": [m.to_dict() for m in self.conversation],
            "kb_entries": [e.to_dict() for e in self.kb_entries],
            "mode": self.mode.value,
        }

    def load_state(self, state: Dict):
        """Load Foreman state from persistence."""
        if state.get("work_order"):
            wo = state["work_order"]
            self.work_order = WorkOrder(
                project_title=wo["project_title"],
                protagonist_name=wo["protagonist_name"],
                mode=ForemanMode(wo["mode"]),
                notebooks=wo.get("notebooks", {}),
            )
            # Restore template statuses
            for i, t_data in enumerate(wo.get("templates", [])):
                if i < len(self.work_order.templates):
                    self.work_order.templates[i].status = TemplateStatus(t_data["status"])
                    self.work_order.templates[i].missing_fields = t_data.get("missing_fields", [])

        self.conversation = [
            ConversationMessage(**m) for m in state.get("conversation", [])
        ]
        self.kb_entries = [
            KBEntry(**e) for e in state.get("kb_entries", [])
        ]
        self.mode = ForemanMode(state.get("mode", "architect"))


# =============================================================================
# Factory Function
# =============================================================================

def create_foreman(
    notebooklm_client=None,
    story_bible_service=None,
    content_path: Path = None,
    model: str = "mistral:7b",
) -> Foreman:
    """
    Factory function to create a configured Foreman instance.

    Usage:
        foreman = create_foreman(
            notebooklm_client=get_notebooklm_client(),
            story_bible_service=StoryBibleService(content_path),
        )
        foreman.start_project("Big Brain", "Mickey Bardot")
        response = await foreman.chat("Let's start with world-building")
    """
    return Foreman(
        model=model,
        notebooklm_client=notebooklm_client,
        story_bible_service=story_bible_service,
        content_path=content_path,
    )
