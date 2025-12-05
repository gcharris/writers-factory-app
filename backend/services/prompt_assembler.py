"""
PromptAssembler Service - Agent Instruction System Phase 2

Assembles the Context Sandwich for agent prompts:
1. Identity (agent persona)
2. Process Map (workflow overview)
3. Mode Rules (current mode instructions)
4. Session State (dynamic XML)
5. Protocols (output format)
6. Conversation History
7. User Message

Supports:
- Multiple agents (Foreman, Character Coach, Plot Doctor, etc.)
- Mode-aware assembly (for Foreman)
- Tier-based prompt sizing (full/medium/minimal)
- Model-specific adaptations
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import yaml

logger = logging.getLogger(__name__)

# Prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class PromptTier(Enum):
    """Prompt assembly tiers based on model capabilities."""
    FULL = "full"        # 128K+ context, high XML reliability
    MEDIUM = "medium"    # 32K-128K context, medium reliability
    MINIMAL = "minimal"  # <32K context, low reliability


@dataclass
class AssemblyConfig:
    """Configuration for prompt assembly."""
    agent_id: str = "foreman"
    model_id: str = "mistral:7b"
    mode: Optional[str] = None  # For mode-aware agents like Foreman
    max_kb_entries: int = 10
    max_conversation_turns: int = 10
    include_voice_bundle: bool = True
    include_guardrails: bool = True


@dataclass
class AssembledPrompt:
    """Result of prompt assembly."""
    system_prompt: str
    tier: PromptTier
    token_estimate: int
    included_sections: List[str] = field(default_factory=list)
    agent_id: str = "foreman"
    mode: Optional[str] = None


@dataclass
class AgentConfig:
    """Agent configuration loaded from agents.yaml."""
    agent_id: str
    name: str
    description: str
    icon: str
    has_modes: bool
    modes: List[str] = field(default_factory=list)
    default_mode: Optional[str] = None
    identity_file: str = ""
    process_map_file: Optional[str] = None
    mode_files: Dict[str, str] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    focus_areas: List[str] = field(default_factory=list)


# Model tier mapping
MODEL_TIERS: Dict[str, PromptTier] = {
    # Full tier - large context, high reliability
    "claude-sonnet-4-5": PromptTier.FULL,
    "claude-opus-4-5": PromptTier.FULL,
    "claude-3-5-sonnet-20241022": PromptTier.FULL,
    "claude-3-7-sonnet-20250219": PromptTier.FULL,
    "claude-3-opus-20240229": PromptTier.FULL,
    "gpt-4o": PromptTier.FULL,
    "gpt-4o-mini": PromptTier.FULL,
    "gemini-2.0-flash": PromptTier.FULL,
    "gemini-2.0-flash-exp": PromptTier.FULL,
    "grok-2": PromptTier.FULL,
    "grok-2-latest": PromptTier.FULL,
    "mistral-large": PromptTier.FULL,
    "mistral-large-latest": PromptTier.FULL,

    # Medium tier - decent context, medium reliability
    "deepseek-chat": PromptTier.MEDIUM,
    "qwen-plus": PromptTier.MEDIUM,
    "qwen-max": PromptTier.MEDIUM,
    "qwen-turbo": PromptTier.MEDIUM,
    "qwen-turbo-latest": PromptTier.MEDIUM,
    "mistral:7b": PromptTier.MEDIUM,
    "mistral": PromptTier.MEDIUM,
    "moonshot-v1-128k": PromptTier.MEDIUM,
    "glm-4": PromptTier.MEDIUM,
    "yandexgpt-5.1-pro": PromptTier.MEDIUM,

    # Minimal tier - limited context, low reliability
    "llama3.2:3b": PromptTier.MINIMAL,
    "llama3.2": PromptTier.MINIMAL,
    "yandexgpt-5-lite": PromptTier.MINIMAL,
    "hunyuan-lite": PromptTier.MINIMAL,
    "gpt-3.5-turbo": PromptTier.MINIMAL,
}

# Models that need XML format reinforcement
XML_REINFORCEMENT_MODELS = {
    "gemini-2.0-flash", "gemini-2.0-flash-exp",  # Prefers JSON
    "llama3.2:3b", "llama3.2",  # Low instruction following
    "deepseek-chat",  # Medium reliability
    "qwen-plus", "qwen-turbo",  # Medium reliability
}


class PromptAssembler:
    """
    Assembles the Context Sandwich for agent prompts.

    Responsibilities:
    - Load modular prompt files
    - Generate session state XML
    - Apply model-specific adaptations
    - Manage context window budget
    """

    def __init__(self):
        self._prompt_cache: Dict[str, str] = {}
        self._agent_configs: Dict[str, AgentConfig] = {}
        self._agents_yaml_loaded = False

    def _ensure_agents_loaded(self):
        """Load agents.yaml if not already loaded."""
        if self._agents_yaml_loaded:
            return

        agents_file = PROMPTS_DIR / "agents.yaml"
        if not agents_file.exists():
            logger.warning(f"agents.yaml not found at {agents_file}")
            self._agents_yaml_loaded = True
            return

        try:
            with open(agents_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            for agent_id, agent_data in data.get('agents', {}).items():
                self._agent_configs[agent_id] = AgentConfig(
                    agent_id=agent_id,
                    name=agent_data.get('name', agent_id),
                    description=agent_data.get('description', ''),
                    icon=agent_data.get('icon', '🤖'),
                    has_modes=agent_data.get('has_modes', False),
                    modes=agent_data.get('modes', []),
                    default_mode=agent_data.get('default_mode'),
                    identity_file=agent_data.get('identity_file', ''),
                    process_map_file=agent_data.get('process_map_file'),
                    mode_files=agent_data.get('mode_files', {}),
                    capabilities=agent_data.get('capabilities', []),
                    focus_areas=agent_data.get('focus_areas', []),
                )

            self._agents_yaml_loaded = True
            logger.info(f"Loaded {len(self._agent_configs)} agent configurations")

        except Exception as e:
            logger.error(f"Failed to load agents.yaml: {e}")
            self._agents_yaml_loaded = True

    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent."""
        self._ensure_agents_loaded()
        return self._agent_configs.get(agent_id)

    def get_available_agents(self) -> List[AgentConfig]:
        """Get all available agent configurations."""
        self._ensure_agents_loaded()
        return list(self._agent_configs.values())

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt file with caching."""
        if filename in self._prompt_cache:
            return self._prompt_cache[filename]

        path = PROMPTS_DIR / filename
        if not path.exists():
            logger.warning(f"Prompt file not found: {path}")
            return ""

        try:
            content = path.read_text(encoding='utf-8')
            self._prompt_cache[filename] = content
            return content
        except Exception as e:
            logger.error(f"Failed to load prompt file {path}: {e}")
            return ""

    def _get_tier(self, model_id: str) -> PromptTier:
        """Determine prompt tier for a model."""
        # Check exact match first
        if model_id in MODEL_TIERS:
            return MODEL_TIERS[model_id]

        # Check partial matches (e.g., "mistral:7b" matches "mistral")
        model_lower = model_id.lower()
        for known_model, tier in MODEL_TIERS.items():
            if known_model in model_lower or model_lower in known_model:
                return tier

        # Default to medium
        return PromptTier.MEDIUM

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (~4 chars per token)."""
        return len(text) // 4

    def assemble(
        self,
        config: AssemblyConfig,
        work_order: Optional[Any] = None,
        conversation_history: Optional[List[Dict]] = None,
        user_message: str = "",
        active_context: Optional[Dict] = None,
        kb_entries: Optional[List[Dict]] = None,
        voice_bundle_summary: Optional[str] = None,
        active_scaffold: Optional[Dict] = None,
    ) -> AssembledPrompt:
        """
        Assemble complete prompt for the agent.

        Args:
            config: Assembly configuration
            work_order: Current work order state (for Foreman)
            conversation_history: Recent conversation turns
            user_message: Current user input
            active_context: Optional context (file, beat, scene)
            kb_entries: Knowledge Base entries to include
            voice_bundle_summary: Voice bundle summary (for DIRECTOR/EDITOR)
            active_scaffold: Current scene scaffold (for DIRECTOR)

        Returns:
            AssembledPrompt with complete system prompt
        """
        self._ensure_agents_loaded()

        tier = self._get_tier(config.model_id)
        included_sections = []
        parts = []

        # Get agent config
        agent_config = self._agent_configs.get(config.agent_id)
        if not agent_config:
            logger.warning(f"Unknown agent: {config.agent_id}, using foreman")
            agent_config = self._agent_configs.get('foreman')

        # Determine effective mode
        mode = config.mode
        if agent_config and agent_config.has_modes and not mode:
            mode = agent_config.default_mode or 'architect'

        # === LAYER 1: SHARED PROJECT CONTEXT ===
        if tier != PromptTier.MINIMAL:
            project_context = self._load_prompt("shared/project_context.md")
            if project_context:
                parts.append(project_context)
                included_sections.append("project_context")

        # === LAYER 2: AGENT IDENTITY ===
        if agent_config and agent_config.identity_file:
            identity = self._load_prompt(agent_config.identity_file)
            if identity:
                if tier == PromptTier.MINIMAL:
                    # Compress identity for minimal tier
                    identity = self._compress_identity(identity)
                parts.append(identity)
                included_sections.append("identity")

        # === LAYER 3: PROCESS MAP (Foreman only, skip for minimal) ===
        if agent_config and agent_config.process_map_file and tier != PromptTier.MINIMAL:
            process_map = self._load_prompt(agent_config.process_map_file)
            if process_map:
                if tier == PromptTier.MEDIUM:
                    # Summarize for medium tier
                    process_map = self._summarize_process_map(process_map)
                parts.append(process_map)
                included_sections.append("process_map")

        # === LAYER 4: MODE RULES (for mode-aware agents) ===
        if agent_config and agent_config.has_modes and mode:
            mode_file = agent_config.mode_files.get(mode)
            if mode_file:
                mode_rules = self._load_prompt(mode_file)
                if mode_rules:
                    if tier == PromptTier.MINIMAL:
                        mode_rules = self._get_mode_essentials(mode_rules)
                    parts.append(mode_rules)
                    included_sections.append(f"mode:{mode}")

        # === LAYER 5: SESSION STATE (Dynamic XML) ===
        session_state = self._generate_session_state(
            agent_id=config.agent_id,
            mode=mode,
            work_order=work_order,
            active_context=active_context,
            kb_entries=kb_entries,
            voice_bundle_summary=voice_bundle_summary,
            active_scaffold=active_scaffold,
            tier=tier,
            max_kb_entries=config.max_kb_entries,
        )
        if session_state:
            parts.append(session_state)
            included_sections.append("session_state")

        # === LAYER 6: GUARDRAILS (if enabled and relevant) ===
        if config.include_guardrails and tier != PromptTier.MINIMAL:
            # Voice anti-patterns for DIRECTOR/EDITOR modes
            if mode in ('director', 'editor'):
                antipatterns = self._load_prompt("shared/guardrails/voice_antipatterns.md")
                if antipatterns:
                    parts.append(antipatterns)
                    included_sections.append("voice_antipatterns")

            # Continuity rules for DIRECTOR/EDITOR modes
            if mode in ('director', 'editor'):
                continuity = self._load_prompt("shared/guardrails/continuity_rules.md")
                if continuity:
                    parts.append(continuity)
                    included_sections.append("continuity_rules")

        # === LAYER 7: PROTOCOLS ===
        protocols = self._load_prompt("shared/protocols.md")
        if protocols:
            if tier == PromptTier.MINIMAL:
                protocols = self._get_core_protocols(protocols)
            parts.append(protocols)
            included_sections.append("protocols")

        # === MODEL-SPECIFIC ADAPTATIONS ===
        # Add XML reinforcement for unreliable models
        if config.model_id in XML_REINFORCEMENT_MODELS:
            parts.append(self._get_xml_reinforcement())
            included_sections.append("xml_reinforcement")

        # Gemini-specific adaptation
        if 'gemini' in config.model_id.lower():
            parts.append(self._get_gemini_adaptation())
            included_sections.append("gemini_adaptation")

        # Assemble system prompt
        system_prompt = "\n\n---\n\n".join(parts)

        # Add conversation history if provided
        if conversation_history:
            history_str = self._format_conversation(
                conversation_history,
                max_turns=config.max_conversation_turns
            )
            if history_str:
                system_prompt += f"\n\n---\n\n## CONVERSATION HISTORY\n\n{history_str}"
                included_sections.append("conversation_history")

        # Token estimate
        token_estimate = self._estimate_tokens(system_prompt)

        return AssembledPrompt(
            system_prompt=system_prompt,
            tier=tier,
            token_estimate=token_estimate,
            included_sections=included_sections,
            agent_id=config.agent_id,
            mode=mode,
        )

    def _generate_session_state(
        self,
        agent_id: str,
        mode: Optional[str],
        work_order: Optional[Any],
        active_context: Optional[Dict],
        kb_entries: Optional[List[Dict]],
        voice_bundle_summary: Optional[str],
        active_scaffold: Optional[Dict],
        tier: PromptTier,
        max_kb_entries: int,
    ) -> str:
        """Generate session state XML."""
        lines = ['<session_state>']

        # Core positioning
        lines.append(f'  <current_agent>{agent_id}</current_agent>')
        if mode:
            lines.append(f'  <current_mode>{mode.upper()}</current_mode>')

        # Work order info (if available)
        if work_order:
            completion = getattr(work_order, 'completion_percentage', 0)
            lines.append(f'  <completion_pct>{completion:.0f}</completion_pct>')

            # Project info
            project_title = getattr(work_order, 'project_title', 'Untitled')
            protagonist = getattr(work_order, 'protagonist_name', 'Unknown')
            lines.append('  <project>')
            lines.append(f'    <title>{self._escape_xml(project_title)}</title>')
            lines.append(f'    <protagonist>{self._escape_xml(protagonist)}</protagonist>')
            lines.append('  </project>')

            # Template status (for ARCHITECT mode)
            if mode in ('architect', 'voice_calibration') and tier != PromptTier.MINIMAL:
                templates = getattr(work_order, 'templates', [])
                if templates:
                    lines.append('  <work_order>')
                    for template in templates:
                        name = getattr(template, 'name', 'Unknown')
                        status = getattr(template, 'status', 'unknown')
                        if hasattr(status, 'value'):
                            status = status.value
                        missing = getattr(template, 'missing_fields', [])
                        if missing:
                            missing_str = ', '.join(missing)
                            lines.append(f'    <template name="{name}" status="{status}" missing="{missing_str}"/>')
                        else:
                            lines.append(f'    <template name="{name}" status="{status}"/>')
                    lines.append('  </work_order>')

        # Active context
        if active_context:
            lines.append('  <active_context>')
            for key, value in active_context.items():
                lines.append(f'    <{key}>{self._escape_xml(str(value))}</{key}>')
            lines.append('  </active_context>')

        # Voice bundle (for DIRECTOR/EDITOR)
        if voice_bundle_summary and mode in ('director', 'editor'):
            lines.append('  <voice_bundle loaded="true">')
            lines.append(f'    <voice_summary>{self._escape_xml(voice_bundle_summary)}</voice_summary>')
            lines.append('  </voice_bundle>')

        # Active scaffold (for DIRECTOR)
        if active_scaffold and mode == 'director':
            lines.append('  <active_scaffold>')
            for key, value in active_scaffold.items():
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                lines.append(f'    <{key}>{self._escape_xml(str(value))}</{key}>')
            lines.append('  </active_scaffold>')

        # Knowledge context (limited by tier)
        if kb_entries:
            # Limit entries based on tier
            tier_limits = {
                PromptTier.FULL: max_kb_entries,
                PromptTier.MEDIUM: min(max_kb_entries, 5),
                PromptTier.MINIMAL: min(max_kb_entries, 2),
            }
            limit = tier_limits.get(tier, 5)
            limited_entries = kb_entries[:limit]

            if limited_entries:
                lines.append('  <knowledge_context>')
                for entry in limited_entries:
                    category = entry.get('category', 'general')
                    key = entry.get('key', '')
                    value = entry.get('value', '')
                    lines.append(f'    <entry category="{category}" key="{self._escape_xml(key)}">')
                    lines.append(f'      {self._escape_xml(value)}')
                    lines.append('    </entry>')
                lines.append('  </knowledge_context>')

        lines.append('</session_state>')

        return '\n'.join(lines)

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters."""
        if not text:
            return ""
        return (
            text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;')
        )

    def _compress_identity(self, identity: str) -> str:
        """Compress identity for minimal tier."""
        # Extract first section (core identity)
        lines = identity.split('\n')
        compressed = []
        in_core = False

        for line in lines[:50]:  # First 50 lines max
            if '## Core Identity' in line or '# THE ' in line:
                in_core = True
            if in_core:
                compressed.append(line)
            if in_core and line.startswith('## ') and 'Core Identity' not in line:
                break

        if compressed:
            return '\n'.join(compressed)

        # Fallback: first 500 characters
        return identity[:500] + "\n\n[Identity compressed for context limits]"

    def _summarize_process_map(self, process_map: str) -> str:
        """Summarize process map for medium tier."""
        return """# WRITING PROCESS (Summary)

- **ARCHITECT**: Build Story Bible (challenge structure, no prose)
- **VOICE_CALIBRATION**: Find narrative voice (run tournament, lock voice)
- **DIRECTOR**: Draft scenes (beat-aware, voice-consistent)
- **EDITOR**: Polish prose (ruthless revision)

Check `<current_mode>` in session state to determine active phase.
"""

    def _get_mode_essentials(self, mode_rules: str) -> str:
        """Extract essential mode rules for minimal tier."""
        # Get title and first major section
        lines = mode_rules.split('\n')
        essentials = []
        section_count = 0

        for line in lines:
            essentials.append(line)
            if line.startswith('## '):
                section_count += 1
                if section_count >= 2:  # Title + one section
                    break

        return '\n'.join(essentials)

    def _get_core_protocols(self, protocols: str) -> str:
        """Extract core protocols for minimal tier."""
        return """# OUTPUT PROTOCOLS (Essential)

Every response MUST use these XML tags:

**Message** (Required):
```xml
<message>Your response to the writer</message>
```

**Thinking** (Optional):
```xml
<thinking>Your internal reasoning</thinking>
```

**Actions** (When needed):
```xml
<action type="action_name">
  <param>value</param>
</action>
```

NEVER respond without `<message>` tags.
"""

    def _get_xml_reinforcement(self) -> str:
        """Get XML format reinforcement for unreliable models."""
        return """
## CRITICAL FORMAT REMINDER

You MUST follow this format exactly:

1. Wrap ALL communication in `<message>...</message>` tags
2. Wrap reasoning in `<thinking>...</thinking>` tags
3. Wrap actions in `<action type="...">...</action>` tags
4. Do NOT use JSON for actions - use XML only
5. NEVER respond without message tags
"""

    def _get_gemini_adaptation(self) -> str:
        """Get Gemini-specific adaptation."""
        return """
## NOTE FOR GEMINI

Although you may prefer JSON, this application requires XML output.
Please use `<message>`, `<thinking>`, and `<action>` tags as specified.
"""

    def _format_conversation(self, history: List[Dict], max_turns: int) -> str:
        """Format conversation history."""
        if not history:
            return ""

        recent = history[-max_turns:] if len(history) > max_turns else history

        lines = []
        for turn in recent:
            role = turn.get('role', 'user').upper()
            content = turn.get('content', '')
            # Truncate very long messages
            if len(content) > 2000:
                content = content[:2000] + "\n\n[Message truncated]"
            lines.append(f"**{role}**: {content}")

        return "\n\n".join(lines)

    def clear_cache(self):
        """Clear prompt cache (for development/hot-reload)."""
        self._prompt_cache.clear()
        logger.info("Prompt cache cleared")


# Singleton instance
_assembler: Optional[PromptAssembler] = None


def get_prompt_assembler() -> PromptAssembler:
    """Get or create the PromptAssembler singleton."""
    global _assembler
    if _assembler is None:
        _assembler = PromptAssembler()
    return _assembler
