"""
Context Assembler Service for GraphRAG.

Assembles context from multiple sources within model-specific token budgets.
Uses priority-based allocation: most important context first, truncates or
omits lower-priority content if over budget.

Part of GraphRAG Phase 1 - Foundation.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from .query_classifier import ClassifiedQuery

logger = logging.getLogger(__name__)

# Import tiktoken with fallback
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not installed - token counting will use estimation")


@dataclass
class ContextBudget:
    """Token budget configuration for a model."""
    max_input: int           # Model's maximum input tokens
    recommended_context: int  # Recommended context size for best results
    max_context: int          # Maximum context before truncation becomes aggressive


# Token budgets by model - these are conservative estimates leaving room for response
CONTEXT_BUDGETS: Dict[str, ContextBudget] = {
    # Anthropic
    'claude-sonnet-4-5': ContextBudget(200000, 16000, 32000),
    'claude-opus-4': ContextBudget(200000, 16000, 32000),
    'claude-3-5-sonnet': ContextBudget(200000, 16000, 32000),
    'claude-3-opus': ContextBudget(200000, 16000, 32000),
    # OpenAI
    'gpt-4o': ContextBudget(128000, 12000, 24000),
    'gpt-4o-mini': ContextBudget(128000, 12000, 24000),
    'gpt-4-turbo': ContextBudget(128000, 12000, 24000),
    # Google
    'gemini-2.0-flash': ContextBudget(1000000, 16000, 32000),
    'gemini-pro': ContextBudget(1000000, 16000, 32000),
    # xAI
    'grok-2': ContextBudget(131072, 12000, 24000),
    # DeepSeek
    'deepseek-chat': ContextBudget(64000, 8000, 16000),
    'deepseek-coder': ContextBudget(64000, 8000, 16000),
    # Alibaba
    'qwen-plus': ContextBudget(131072, 12000, 24000),
    'qwen-turbo': ContextBudget(131072, 12000, 24000),
    # Mistral
    'mistral-large': ContextBudget(128000, 12000, 24000),
    'mistral-medium': ContextBudget(32000, 6000, 12000),
    # Local Ollama models
    'llama3.2:3b': ContextBudget(8192, 2000, 4000),
    'mistral:7b': ContextBudget(32768, 6000, 12000),
    # Default for unknown models
    'default': ContextBudget(8192, 4000, 6000),
}

# Priority order for context sections (highest to lowest)
CONTEXT_PRIORITY = [
    'character_core',        # Fatal Flaw, The Lie, Arc (NEVER truncate)
    'active_scaffold',       # Current scene's scaffold
    'scene_strategy',        # Goal/Conflict/Outcome
    'relevant_relationships', # Key character relationships
    'beat_context',          # Beat Sheet position
    'world_rules',           # Relevant world constraints
    'recent_decisions',      # From Foreman KB
    'technique_guidance',    # NotebookLM results (lowest priority)
]


class ContextAssembler:
    """
    Assembles context from multiple sources within token budget.

    Uses priority-based allocation: most important context first,
    truncates or omits lower-priority content if over budget.
    """

    def __init__(self, model: str = 'claude-sonnet-4-5'):
        """
        Initialize the assembler for a specific model.

        Args:
            model: Model identifier for token budget lookup
        """
        self.model = model
        self.budget = CONTEXT_BUDGETS.get(model, CONTEXT_BUDGETS['default'])

        # Initialize tokenizer
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoder = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                logger.warning(f"Failed to load tiktoken encoder: {e}")
                self.encoder = None
        else:
            self.encoder = None

        logger.info(f"ContextAssembler initialized for {model} (budget: {self.budget.recommended_context} tokens)")

    def assemble(
        self,
        classified_query: 'ClassifiedQuery',
        graph_context: Dict,
        story_bible_context: Dict,
        kb_context: List[Dict],
        notebooklm_results: Optional[str] = None,
        active_scaffold: Optional[Dict] = None,
    ) -> str:
        """
        Assemble context block from multiple sources.

        Args:
            classified_query: The classified query with entities and keywords
            graph_context: Data from knowledge graph {'characters': {}, 'edges': []}
            story_bible_context: Parsed Story Bible data
            kb_context: List of Foreman KB entries
            notebooklm_results: Optional NotebookLM query results
            active_scaffold: Optional current scene scaffold

        Returns:
            Formatted context string within token budget
        """
        budget = self.budget.recommended_context
        blocks = []
        used_tokens = 0
        included_sections = []

        # 1. Character Core (highest priority) - NEVER truncate
        for entity in classified_query.entities:
            if entity in graph_context.get('characters', {}):
                char_block = self._format_character_core(
                    entity,
                    graph_context['characters'][entity],
                    story_bible_context.get('characters', {}).get(entity)
                )
                tokens = self._count_tokens(char_block)
                blocks.append(char_block)
                used_tokens += tokens
                included_sections.append(f"character_core:{entity}")

        # 2. Active Scaffold (if writing a scene)
        if active_scaffold:
            scaffold_block = self._format_scaffold(active_scaffold)
            tokens = self._count_tokens(scaffold_block)
            if used_tokens + tokens <= budget:
                blocks.append(scaffold_block)
                used_tokens += tokens
                included_sections.append("active_scaffold")

        # 3. Relevant Relationships
        if classified_query.entities and 'edges' in graph_context:
            rel_block = self._format_relationships(
                classified_query.entities,
                graph_context['edges']
            )
            if rel_block:
                tokens = self._count_tokens(rel_block)
                if used_tokens + tokens <= budget:
                    blocks.append(rel_block)
                    used_tokens += tokens
                    included_sections.append("relationships")

        # 4. Beat Context
        if 'beat_sheet' in story_bible_context:
            beat_block = self._format_beat_context(story_bible_context['beat_sheet'])
            tokens = self._count_tokens(beat_block)
            if used_tokens + tokens <= budget:
                blocks.append(beat_block)
                used_tokens += tokens
                included_sections.append("beat_context")

        # 5. World Rules (filtered by relevance)
        if 'world_rules' in story_bible_context:
            world_block = self._format_world_rules(
                story_bible_context['world_rules'],
                classified_query.keywords
            )
            if world_block:
                tokens = self._count_tokens(world_block)
                if used_tokens + tokens <= budget:
                    blocks.append(world_block)
                    used_tokens += tokens
                    included_sections.append("world_rules")

        # 6. Recent KB Decisions
        if kb_context:
            remaining = budget - used_tokens
            if remaining > 100:  # Only include if meaningful space
                kb_block = self._format_kb_context(kb_context, remaining)
                blocks.append(kb_block)
                used_tokens += self._count_tokens(kb_block)
                included_sections.append("kb_context")

        # 7. NotebookLM Results (lowest priority, fill remaining space)
        if notebooklm_results:
            remaining = budget - used_tokens
            if remaining > 200:  # Only include if meaningful space left
                nlm_block = self._truncate_to_tokens(
                    f"## Writing Guidance\n\n{notebooklm_results}",
                    remaining
                )
                blocks.append(nlm_block)
                used_tokens += self._count_tokens(nlm_block)
                included_sections.append("notebooklm")

        # Assemble final context with metadata
        context = "\n\n---\n\n".join(blocks)
        metadata = f"<!-- Context: {', '.join(included_sections)} | {used_tokens} tokens -->\n\n"

        logger.debug(f"Assembled context: {len(included_sections)} sections, {used_tokens} tokens")
        return metadata + context

    def _format_character_core(
        self,
        name: str,
        graph_data: Dict,
        story_bible_data: Optional[Dict]
    ) -> str:
        """Format essential character information."""
        parts = [f"## Character: {name.title()}"]

        if graph_data.get('description'):
            parts.append(f"**Summary**: {graph_data['description']}")

        if story_bible_data:
            if story_bible_data.get('fatal_flaw'):
                parts.append(f"**Fatal Flaw**: {story_bible_data['fatal_flaw']}")
            if story_bible_data.get('the_lie'):
                parts.append(f"**The Lie**: {story_bible_data['the_lie']}")
            if story_bible_data.get('arc'):
                parts.append(f"**Arc**: {story_bible_data['arc']}")
            if story_bible_data.get('true_character'):
                parts.append(f"**True Character**: {story_bible_data['true_character']}")

        return "\n".join(parts)

    def _format_scaffold(self, scaffold: Dict) -> str:
        """Format active scene scaffold."""
        callbacks = scaffold.get('callbacks', [])
        foreshadowing = scaffold.get('foreshadowing', [])

        return f"""## Active Scene Scaffold

**Scene**: {scaffold.get('title', 'Untitled')}
**Beat Alignment**: {scaffold.get('beat_alignment', 'Not specified')}
**POV**: {scaffold.get('pov_character', 'Not specified')}
**Goal**: {scaffold.get('scene_goal', 'Not specified')}
**Constraint**: {scaffold.get('protagonist_constraint', 'None')}
**Callbacks**: {', '.join(callbacks) if callbacks else 'None'}
**Foreshadowing**: {', '.join(foreshadowing) if foreshadowing else 'None'}"""

    def _format_relationships(self, entities: List[str], edges: List[Dict]) -> str:
        """Format relevant relationships between entities."""
        parts = ["## Relationships"]
        entity_set = {e.lower() for e in entities}
        relevant_edges = []

        for edge in edges:
            source = edge.get('source', '').lower()
            target = edge.get('target', '').lower()
            if source in entity_set or target in entity_set:
                relevant_edges.append(edge)

        if not relevant_edges:
            return ""

        for edge in relevant_edges[:10]:  # Limit to 10 most relevant
            parts.append(f"- {edge.get('source', '?')} --[{edge.get('relation', '?')}]--> {edge.get('target', '?')}")

        return "\n".join(parts) if len(parts) > 1 else ""

    def _format_beat_context(self, beat_sheet: Dict) -> str:
        """Format beat sheet status."""
        current = beat_sheet.get('current_beat', 1)
        beats = beat_sheet.get('beats', {})
        current_beat = beats.get(str(current), {})

        return f"""## Beat Sheet Status

**Current Beat**: {current} - {current_beat.get('name', 'Unknown')}
**Description**: {current_beat.get('description', 'Not defined')}
**Progress**: Beat {current} of 15"""

    def _format_world_rules(self, rules: Dict, keywords: List[str]) -> str:
        """Format world rules, prioritizing keyword-relevant ones."""
        parts = ["## World Rules"]
        keyword_set = {k.lower() for k in keywords}

        # Filter rules by keyword relevance
        for rule_name, rule_content in rules.items():
            rule_text = f"{rule_name} {rule_content}".lower()
            if any(kw in rule_text for kw in keyword_set):
                content = rule_content[:500] if len(str(rule_content)) > 500 else rule_content
                parts.append(f"**{rule_name}**: {content}")

        return "\n".join(parts) if len(parts) > 1 else ""

    def _format_kb_context(self, entries: List[Dict], max_tokens: int) -> str:
        """Format KB entries within token limit."""
        parts = ["## Recent Decisions"]
        tokens_used = self._count_tokens(parts[0])

        for entry in entries:
            category = entry.get('category', 'general')
            key = entry.get('key', '')
            value = entry.get('value', '')
            line = f"- [{category}] {key}: {value}"
            line_tokens = self._count_tokens(line)

            if tokens_used + line_tokens > max_tokens:
                break

            parts.append(line)
            tokens_used += line_tokens

        return "\n".join(parts)

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Uses tiktoken if available, otherwise estimates at ~4 chars/token.
        """
        if not text:
            return 0

        if self.encoder:
            try:
                return len(self.encoder.encode(text))
            except Exception:
                pass

        # Fallback: estimate at ~4 characters per token
        return len(text) // 4

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token limit.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed

        Returns:
            Truncated text with ellipsis if needed
        """
        if not text:
            return ""

        if self.encoder:
            try:
                tokens = self.encoder.encode(text)
                if len(tokens) <= max_tokens:
                    return text
                # Leave room for truncation notice
                truncated = self.encoder.decode(tokens[:max_tokens - 20])
                return truncated + "\n\n[... truncated for length]"
            except Exception:
                pass

        # Fallback: estimate at ~4 characters per token
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars - 30] + "\n\n[... truncated for length]"

    def get_budget_info(self) -> Dict:
        """Get information about the current token budget."""
        return {
            'model': self.model,
            'max_input': self.budget.max_input,
            'recommended_context': self.budget.recommended_context,
            'max_context': self.budget.max_context,
            'tiktoken_available': self.encoder is not None,
        }


# Factory function
def get_context_assembler(model: str = 'claude-sonnet-4-5') -> ContextAssembler:
    """
    Get a ContextAssembler configured for a specific model.

    Args:
        model: Model identifier for token budget lookup

    Returns:
        Configured ContextAssembler instance
    """
    return ContextAssembler(model=model)
