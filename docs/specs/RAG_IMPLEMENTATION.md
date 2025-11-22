# RAG-Lite Implementation Specification

**Version**: 1.0
**Status**: Draft
**Related**: ARCHITECTURE.md, Knowledge Router

---

## Problem Statement

Writers need context-aware AI assistance. The system must:

1. Retrieve relevant information from the Knowledge Graph and Story Bible
2. Fit context within model token limits (varies by provider)
3. Preserve narrative coherence (not just keyword matching)
4. Route queries to the right knowledge source automatically

This is "RAG-Lite" - simpler than enterprise RAG systems, optimized for narrative workflows.

---

## Architecture

### Knowledge Router Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE ROUTER                           │
│                                                                  │
│  User Query: "How should Mickey react to this betrayal?"        │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  QUERY CLASSIFIER                          │ │
│  │                                                            │ │
│  │  Classify: CHARACTER_QUERY + EMOTIONAL_STATE               │ │
│  │  Entities: [Mickey]                                        │ │
│  │  Context: betrayal, reaction, psychology                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│         ┌────────────────────┴────────────────────┐             │
│         ▼                                         ▼             │
│  ┌────────────────┐                    ┌────────────────────┐  │
│  │ Knowledge Graph│                    │   NotebookLM       │  │
│  │                │                    │                    │  │
│  │ • Mickey node  │                    │ • Psychology refs  │  │
│  │ • Relationships│                    │ • Character theory │  │
│  │ • Arc progress │                    │ • Similar scenes   │  │
│  └────────────────┘                    └────────────────────┘  │
│         │                                         │             │
│         └────────────────────┬────────────────────┘             │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  CONTEXT ASSEMBLER                         │ │
│  │                                                            │ │
│  │  Budget: 8000 tokens                                       │ │
│  │  Priority: Character > Plot > World > Technique            │ │
│  │  Output: Assembled context block                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Query Classification

### Query Types

| Type | Examples | Primary Source | Secondary |
|------|----------|----------------|-----------|
| `CHARACTER_LOOKUP` | "Who is Mickey?" | Knowledge Graph | Story Bible |
| `CHARACTER_DEEP` | "What's Mickey's Fatal Flaw?" | Story Bible | Knowledge Graph |
| `PLOT_STATUS` | "Where are we in the Beat Sheet?" | Beat_Sheet.md | Knowledge Graph |
| `RELATIONSHIP` | "How does Mickey feel about Noni?" | Knowledge Graph edges | - |
| `WORLD_RULES` | "How does quantum cognition work?" | World/Rules.md | NotebookLM |
| `WRITING_TECHNIQUE` | "How do I write compressed prose?" | NotebookLM | - |
| `SCENE_CONTEXT` | "What happened in previous scene?" | Manuscript files | Knowledge Graph |
| `HYBRID` | "How should Mickey react here?" | Both sources | Merged |

### Classification Implementation

```python
# backend/services/query_classifier.py
from enum import Enum
from dataclasses import dataclass
import re

class QueryType(Enum):
    CHARACTER_LOOKUP = "character_lookup"
    CHARACTER_DEEP = "character_deep"
    PLOT_STATUS = "plot_status"
    RELATIONSHIP = "relationship"
    WORLD_RULES = "world_rules"
    WRITING_TECHNIQUE = "writing_technique"
    SCENE_CONTEXT = "scene_context"
    HYBRID = "hybrid"

@dataclass
class ClassifiedQuery:
    query_type: QueryType
    entities: list[str]
    keywords: list[str]
    sources: list[str]  # ['graph', 'story_bible', 'notebooklm', 'manuscript']

class QueryClassifier:
    """
    Classifies user queries to determine routing strategy.

    Uses pattern matching + entity detection.
    Future: Could use LLM for ambiguous queries.
    """

    # Entity patterns (loaded from Knowledge Graph)
    def __init__(self, known_entities: set[str]):
        self.known_entities = known_entities
        self.character_patterns = [
            r"who is (\w+)",
            r"tell me about (\w+)",
            r"(\w+)'s (flaw|lie|arc|relationship)",
            r"how does (\w+) feel",
        ]
        self.technique_patterns = [
            r"how (do|should) I write",
            r"what is (compressed prose|voice|metaphor)",
            r"technique for",
            r"writing advice",
        ]
        self.plot_patterns = [
            r"what beat",
            r"where (are we|is the story)",
            r"beat sheet",
            r"plot progress",
        ]

    def classify(self, query: str) -> ClassifiedQuery:
        """Classify a query and determine routing."""
        query_lower = query.lower()

        # Extract mentioned entities
        entities = self._extract_entities(query)

        # Check patterns
        if self._matches_patterns(query_lower, self.technique_patterns):
            return ClassifiedQuery(
                query_type=QueryType.WRITING_TECHNIQUE,
                entities=entities,
                keywords=self._extract_keywords(query),
                sources=['notebooklm']
            )

        if self._matches_patterns(query_lower, self.plot_patterns):
            return ClassifiedQuery(
                query_type=QueryType.PLOT_STATUS,
                entities=entities,
                keywords=self._extract_keywords(query),
                sources=['story_bible']
            )

        # Character queries
        if entities:
            # Deep character query (Fatal Flaw, The Lie, etc.)
            if any(term in query_lower for term in ['flaw', 'lie', 'arc', 'true character']):
                return ClassifiedQuery(
                    query_type=QueryType.CHARACTER_DEEP,
                    entities=entities,
                    keywords=self._extract_keywords(query),
                    sources=['story_bible', 'graph']
                )

            # Relationship query
            if len(entities) > 1 or 'relationship' in query_lower:
                return ClassifiedQuery(
                    query_type=QueryType.RELATIONSHIP,
                    entities=entities,
                    keywords=self._extract_keywords(query),
                    sources=['graph']
                )

            # Simple character lookup
            return ClassifiedQuery(
                query_type=QueryType.CHARACTER_LOOKUP,
                entities=entities,
                keywords=self._extract_keywords(query),
                sources=['graph', 'story_bible']
            )

        # Hybrid/ambiguous - use both sources
        return ClassifiedQuery(
            query_type=QueryType.HYBRID,
            entities=entities,
            keywords=self._extract_keywords(query),
            sources=['graph', 'story_bible', 'notebooklm']
        )

    def _extract_entities(self, query: str) -> list[str]:
        """Find known entities mentioned in query."""
        found = []
        for entity in self.known_entities:
            if entity.lower() in query.lower():
                found.append(entity)
        return found

    def _extract_keywords(self, query: str) -> list[str]:
        """Extract meaningful keywords for search."""
        # Remove stopwords, keep nouns/verbs
        stopwords = {'is', 'the', 'a', 'an', 'how', 'what', 'who', 'where', 'when', 'do', 'does'}
        words = re.findall(r'\w+', query.lower())
        return [w for w in words if w not in stopwords and len(w) > 2]

    def _matches_patterns(self, text: str, patterns: list[str]) -> bool:
        """Check if text matches any pattern."""
        return any(re.search(p, text) for p in patterns)
```

---

## Context Assembly

### Token Budgets by Provider

```python
# backend/config/context_budgets.py

CONTEXT_BUDGETS = {
    'claude-sonnet-4-5': {
        'max_input': 200000,
        'recommended_context': 16000,  # Leave room for response
        'max_context': 32000,
    },
    'gpt-4o': {
        'max_input': 128000,
        'recommended_context': 12000,
        'max_context': 24000,
    },
    'gemini-pro': {
        'max_input': 1000000,
        'recommended_context': 16000,  # Don't need to use all of it
        'max_context': 32000,
    },
    'grok-2': {
        'max_input': 131072,
        'recommended_context': 12000,
        'max_context': 24000,
    },
    'deepseek-chat': {
        'max_input': 64000,
        'recommended_context': 8000,
        'max_context': 16000,
    }
}

# Priority order for context allocation
CONTEXT_PRIORITY = [
    'character_core',      # Fatal Flaw, The Lie, Arc (highest priority)
    'scene_strategy',      # Current scene's Goal/Conflict/Outcome
    'relevant_characters', # Other characters in scene
    'beat_context',        # Where we are in Beat Sheet
    'world_rules',         # Relevant world-building
    'recent_scenes',       # What just happened
    'technique_guidance',  # Writing advice (lowest priority)
]
```

### Context Assembler

```python
# backend/services/context_assembler.py
import tiktoken
from pathlib import Path

class ContextAssembler:
    """
    Assembles context from multiple sources within token budget.

    Uses priority-based allocation: most important context first,
    truncate or omit lower-priority content if over budget.
    """

    def __init__(self, model: str = 'claude-sonnet-4-5'):
        self.model = model
        self.budget = CONTEXT_BUDGETS.get(model, CONTEXT_BUDGETS['claude-sonnet-4-5'])
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def assemble(
        self,
        classified_query: ClassifiedQuery,
        graph_results: dict,
        story_bible_content: dict,
        notebooklm_results: str | None = None,
        scene_content: str | None = None
    ) -> str:
        """
        Assemble context block from multiple sources.

        Returns formatted context string within token budget.
        """
        budget = self.budget['recommended_context']
        blocks = []
        used_tokens = 0

        # 1. Character Core (highest priority)
        if classified_query.entities:
            for entity in classified_query.entities:
                char_block = self._format_character_context(
                    entity, graph_results, story_bible_content
                )
                tokens = self._count_tokens(char_block)
                if used_tokens + tokens <= budget:
                    blocks.append(char_block)
                    used_tokens += tokens

        # 2. Scene Strategy (if writing/analyzing a scene)
        if scene_content and 'scene_strategy' in story_bible_content:
            strategy_block = self._format_scene_strategy(
                story_bible_content['scene_strategy']
            )
            tokens = self._count_tokens(strategy_block)
            if used_tokens + tokens <= budget:
                blocks.append(strategy_block)
                used_tokens += tokens

        # 3. Beat Sheet Context
        if 'beat_sheet' in story_bible_content:
            beat_block = self._format_beat_context(
                story_bible_content['beat_sheet']
            )
            tokens = self._count_tokens(beat_block)
            if used_tokens + tokens <= budget:
                blocks.append(beat_block)
                used_tokens += tokens

        # 4. World Rules (if relevant)
        if classified_query.query_type in (QueryType.WORLD_RULES, QueryType.HYBRID):
            if 'world_rules' in story_bible_content:
                world_block = self._format_world_rules(
                    story_bible_content['world_rules'],
                    classified_query.keywords
                )
                tokens = self._count_tokens(world_block)
                if used_tokens + tokens <= budget:
                    blocks.append(world_block)
                    used_tokens += tokens

        # 5. NotebookLM Results (technique guidance)
        if notebooklm_results:
            remaining = budget - used_tokens
            nlm_block = self._truncate_to_tokens(
                f"## Writing Guidance (from NotebookLM)\n\n{notebooklm_results}",
                remaining
            )
            blocks.append(nlm_block)

        return "\n\n---\n\n".join(blocks)

    def _format_character_context(
        self,
        entity: str,
        graph_results: dict,
        story_bible: dict
    ) -> str:
        """Format character information from graph + Story Bible."""
        parts = [f"## Character: {entity}"]

        # From Knowledge Graph
        if entity in graph_results.get('nodes', {}):
            node = graph_results['nodes'][entity]
            parts.append(f"**Summary**: {node.get('desc', 'No description')}")

            # Relationships
            edges = [e for e in graph_results.get('edges', [])
                     if e['source'] == entity or e['target'] == entity]
            if edges:
                parts.append("**Relationships**:")
                for edge in edges[:5]:  # Limit relationships
                    other = edge['target'] if edge['source'] == entity else edge['source']
                    parts.append(f"  - {edge['relation']} → {other}")

        # From Story Bible (deeper info)
        if entity in story_bible.get('characters', {}):
            char_data = story_bible['characters'][entity]
            if 'fatal_flaw' in char_data:
                parts.append(f"**Fatal Flaw**: {char_data['fatal_flaw']}")
            if 'the_lie' in char_data:
                parts.append(f"**The Lie**: {char_data['the_lie']}")
            if 'arc' in char_data:
                parts.append(f"**Arc**: {char_data['arc']}")

        return "\n".join(parts)

    def _format_scene_strategy(self, strategy: dict) -> str:
        """Format current scene's strategy."""
        return f"""## Current Scene Strategy

**Goal**: {strategy.get('goal', 'Not defined')}
**Conflict**: {strategy.get('conflict', 'Not defined')}
**Outcome**: {strategy.get('outcome', 'Not defined')}
**Beat Connection**: {strategy.get('beat', 'Not specified')}
**Flaw Challenge**: {strategy.get('flaw_challenge', 'Not specified')}"""

    def _format_beat_context(self, beat_sheet: dict) -> str:
        """Format current beat sheet status."""
        current = beat_sheet.get('current_beat', 'Unknown')
        current_desc = beat_sheet.get('beats', {}).get(str(current), {})

        return f"""## Beat Sheet Status

**Current Beat**: {current} - {current_desc.get('name', '')}
**Description**: {current_desc.get('description', '')}
**Progress**: {beat_sheet.get('progress', 'Unknown')}"""

    def _format_world_rules(self, rules: dict, keywords: list[str]) -> str:
        """Format world rules, prioritizing keyword-relevant ones."""
        parts = ["## World Rules"]

        # Filter rules by keyword relevance
        for rule_name, rule_content in rules.items():
            if any(kw in rule_name.lower() or kw in str(rule_content).lower()
                   for kw in keywords):
                parts.append(f"**{rule_name}**: {rule_content}")

        return "\n".join(parts) if len(parts) > 1 else ""

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        tokens = self.encoder.encode(text)
        if len(tokens) <= max_tokens:
            return text
        truncated = self.encoder.decode(tokens[:max_tokens])
        return truncated + "\n\n[... truncated for length]"
```

---

## Story Bible Parsing

### Structured Extraction

```python
# backend/services/story_bible_parser.py
import re
from pathlib import Path
import frontmatter

class StoryBibleParser:
    """
    Parses Story Bible markdown files into structured data.

    Extracts:
    - Protagonist: Fatal Flaw, The Lie, Arc
    - Beat Sheet: All 15 beats with current progress
    - Scene Strategy: Goal/Conflict/Outcome per scene
    - World Rules: Named rules with descriptions
    """

    def __init__(self, content_path: Path):
        self.content_path = content_path
        self.story_bible_path = content_path / "Story Bible"

    def parse_all(self) -> dict:
        """Parse entire Story Bible into structured dict."""
        return {
            'characters': self._parse_characters(),
            'beat_sheet': self._parse_beat_sheet(),
            'scene_strategies': self._parse_scene_strategies(),
            'world_rules': self._parse_world_rules(),
            'foundations': self._parse_foundations(),
        }

    def _parse_characters(self) -> dict:
        """Parse character files from Characters/ directory."""
        characters = {}
        char_dir = self.story_bible_path / "Characters"

        if not char_dir.exists():
            return characters

        for char_file in char_dir.glob("*.md"):
            name = char_file.stem
            content = char_file.read_text(encoding='utf-8')

            characters[name] = {
                'fatal_flaw': self._extract_section(content, 'Fatal Flaw'),
                'the_lie': self._extract_section(content, 'The Lie'),
                'true_character': self._extract_section(content, 'True Character'),
                'characterization': self._extract_section(content, 'Characterization'),
                'arc': self._extract_section(content, 'Arc'),
                'relationships': self._extract_list_section(content, 'Relationships'),
            }

        return characters

    def _parse_beat_sheet(self) -> dict:
        """Parse Beat_Sheet.md into structured beats."""
        beat_file = self.story_bible_path / "Structure" / "Beat_Sheet.md"

        if not beat_file.exists():
            return {}

        content = beat_file.read_text(encoding='utf-8')

        beats = {}
        # Pattern: **Beat Name** (percentage): Description
        beat_pattern = r'\d+\.\s+\*\*([^*]+)\*\*\s*\(([^)]+)\):\s*(.+?)(?=\n\d+\.|\n##|$)'

        for match in re.finditer(beat_pattern, content, re.DOTALL):
            beat_name = match.group(1).strip()
            percentage = match.group(2).strip()
            description = match.group(3).strip()

            beat_num = len(beats) + 1
            beats[str(beat_num)] = {
                'name': beat_name,
                'percentage': percentage,
                'description': description,
            }

        # Extract current progress
        progress_match = re.search(r'\*\*Active Beat\*\*:\s*(\d+)', content)
        current_beat = int(progress_match.group(1)) if progress_match else 1

        return {
            'beats': beats,
            'current_beat': current_beat,
            'progress': f"Beat {current_beat} of 15",
        }

    def _parse_scene_strategies(self) -> dict:
        """Parse Scene_Strategy.md into per-scene strategies."""
        strategy_file = self.story_bible_path / "Structure" / "Scene_Strategy.md"

        if not strategy_file.exists():
            return {}

        content = strategy_file.read_text(encoding='utf-8')
        strategies = {}

        # Pattern: ## Scene [Act].[Chapter].[Scene]: [Title]
        scene_pattern = r'##\s+Scene\s+([\d.]+):\s*([^\n]+)(.*?)(?=##\s+Scene|$)'

        for match in re.finditer(scene_pattern, content, re.DOTALL):
            scene_id = match.group(1).strip()
            title = match.group(2).strip()
            body = match.group(3)

            strategies[scene_id] = {
                'title': title,
                'goal': self._extract_section(body, 'Goal'),
                'conflict': self._extract_section(body, 'Conflict'),
                'outcome': self._extract_outcome(body),
                'beat': self._extract_section(body, 'Beat Connection'),
                'flaw_challenge': self._extract_section(body, 'Character Arc Progress'),
            }

        return strategies

    def _parse_world_rules(self) -> dict:
        """Parse World/Rules.md into named rules."""
        rules_file = self.story_bible_path / "World" / "Rules.md"

        if not rules_file.exists():
            return {}

        content = rules_file.read_text(encoding='utf-8')
        rules = {}

        # Pattern: ## Rule Name followed by content
        rule_pattern = r'##\s+([^\n]+)\n(.*?)(?=##|$)'

        for match in re.finditer(rule_pattern, content, re.DOTALL):
            rule_name = match.group(1).strip()
            rule_content = match.group(2).strip()
            rules[rule_name] = rule_content

        return rules

    def _parse_foundations(self) -> dict:
        """Parse foundational docs (Mindset, Audience, etc.)."""
        foundations = {}

        for doc_num, doc_name in [
            ('01', 'Mindset'),
            ('02', 'Audience'),
            ('03', 'Premise'),
            ('04', 'Theme'),
            ('05', 'Voice'),
        ]:
            doc_file = self.story_bible_path / f"{doc_num}_{doc_name}.md"
            if doc_file.exists():
                foundations[doc_name.lower()] = doc_file.read_text(encoding='utf-8')

        return foundations

    def _extract_section(self, content: str, heading: str) -> str:
        """Extract content under a markdown heading."""
        pattern = rf'##?\s*{re.escape(heading)}[^\n]*\n(.*?)(?=##|$)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_list_section(self, content: str, heading: str) -> list[str]:
        """Extract a list section."""
        text = self._extract_section(content, heading)
        return [line.strip('- ').strip() for line in text.split('\n') if line.strip().startswith('-')]

    def _extract_outcome(self, content: str) -> str:
        """Extract outcome from checkbox format."""
        outcome_pattern = r'\[x\]\s*(.+)'
        match = re.search(outcome_pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else ""
```

---

## Knowledge Router Service

```python
# backend/services/knowledge_router.py

class KnowledgeRouter:
    """
    Main router that orchestrates query classification,
    source retrieval, and context assembly.
    """

    def __init__(
        self,
        graph_path: Path,
        content_path: Path,
        notebooklm_client = None
    ):
        self.graph = self._load_graph(graph_path)
        self.story_bible = StoryBibleParser(content_path).parse_all()
        self.classifier = QueryClassifier(self._get_entities())
        self.assembler = ContextAssembler()
        self.notebooklm = notebooklm_client

    def query(self, user_query: str, model: str = 'claude-sonnet-4-5') -> dict:
        """
        Process a user query and return assembled context.

        Returns:
            {
                'context': str,  # Assembled context for LLM
                'sources': list, # Sources used
                'query_type': str,
                'entities': list,
            }
        """
        # 1. Classify query
        classified = self.classifier.classify(user_query)

        # 2. Gather from sources
        graph_results = {}
        notebooklm_results = None

        if 'graph' in classified.sources:
            graph_results = self._query_graph(classified)

        if 'notebooklm' in classified.sources and self.notebooklm:
            notebooklm_results = self.notebooklm.query(user_query)

        # 3. Assemble context
        self.assembler.model = model
        context = self.assembler.assemble(
            classified,
            graph_results,
            self.story_bible,
            notebooklm_results
        )

        return {
            'context': context,
            'sources': classified.sources,
            'query_type': classified.query_type.value,
            'entities': classified.entities,
        }

    def _query_graph(self, classified: ClassifiedQuery) -> dict:
        """Query knowledge graph for relevant nodes and edges."""
        results = {'nodes': {}, 'edges': []}

        for entity in classified.entities:
            # Find matching node
            for node in self.graph.get('nodes', []):
                if node['id'].lower() == entity.lower():
                    results['nodes'][entity] = node
                    break

            # Find edges involving entity
            for edge in self.graph.get('edges', []):
                if entity.lower() in (edge['source'].lower(), edge['target'].lower()):
                    results['edges'].append(edge)

        return results

    def _get_entities(self) -> set[str]:
        """Get all known entity names."""
        entities = set()
        for node in self.graph.get('nodes', []):
            entities.add(node['id'])
        return entities

    def _load_graph(self, graph_path: Path) -> dict:
        """Load knowledge graph from JSON."""
        if graph_path.exists():
            return json.loads(graph_path.read_text())
        return {'nodes': [], 'edges': []}
```

---

## API Endpoints

```python
# In api.py

@app.post("/knowledge/query")
async def knowledge_query(request: QueryRequest):
    """
    Query the Knowledge Router.

    Automatically routes to appropriate sources and returns
    assembled context for LLM consumption.
    """
    router = get_knowledge_router()
    result = router.query(request.query, request.model)

    return {
        "context": result['context'],
        "metadata": {
            "query_type": result['query_type'],
            "sources": result['sources'],
            "entities": result['entities'],
        }
    }

@app.get("/knowledge/entities")
async def list_entities():
    """List all known entities in the Knowledge Graph."""
    router = get_knowledge_router()
    return {"entities": list(router._get_entities())}

@app.get("/knowledge/story-bible/status")
async def story_bible_status():
    """Get Story Bible parsing status and completeness."""
    router = get_knowledge_router()
    sb = router.story_bible

    return {
        "characters": len(sb.get('characters', {})),
        "beats_defined": len(sb.get('beat_sheet', {}).get('beats', {})),
        "current_beat": sb.get('beat_sheet', {}).get('current_beat'),
        "scene_strategies": len(sb.get('scene_strategies', {})),
        "world_rules": len(sb.get('world_rules', {})),
        "foundations": list(sb.get('foundations', {}).keys()),
    }
```

---

## Success Criteria

- [ ] Queries automatically route to best knowledge source
- [ ] Context assembled within model token budgets
- [ ] Character core info (Fatal Flaw, The Lie) always prioritized
- [ ] Story Bible parsing extracts all structured data
- [ ] Beat Sheet progress tracked and included in context
- [ ] Scene Strategy integrated when writing scenes
- [ ] NotebookLM results included when technique guidance needed
- [ ] Token counting accurate across providers
