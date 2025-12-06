---
layout: default
title: GraphRAG Conceptual
protected: true
---

<script>
if (!sessionStorage.getItem('authenticated')) {
    window.location.href = "/portal/";
}
</script>

# GraphRAG: The Living Brain of Writers Factory

**From Context Flatness to Narrative Intelligence**

---

## The Problem We Solved

### Context Flatness in Traditional RAG

When we first built Writers Factory, we used standard Retrieval-Augmented Generation (RAG) - the industry standard approach where you embed text chunks and retrieve them by semantic similarity.

It worked. But it had a fundamental flaw.

When a writer asked "What happens next?", the system retrieved passages that were *lexically* similar to the query. It missed crucial *causal* links that are semantically distant but narratively connected:

- A gun mentioned in Act 1 that must fire in Act 3
- A character's fatal flaw that should affect their decision in Chapter 12
- A world rule established early that constrains possibilities later

The LLM would "hallucinate" continuity, reinventing facts or dropping subplots because it couldn't "see" the structural relationships between story elements.

### The Insight: Stories Have Physics

The breakthrough came from recognizing that novels aren't just collections of text - they have **narrative physics**:

- **Characters have goals** that motivate their actions
- **Obstacles hinder** those goals, creating conflict
- **Events cause** other events in chains
- **Earlier scenes foreshadow** later payoffs
- **Later scenes callback** to earlier setups

Standard RAG treats stories as bags of words. GraphRAG treats them as systems of relationships.

---

## From Chunks to Subgraphs

Instead of retrieving isolated text chunks, GraphRAG retrieves **connected subgraphs**.

When the Foreman queries the system, we traverse the graph to find not just the target node (e.g., "Character A") but its neighbors:

```
Character A → HAS_GOAL → Escape → BLOCKED_BY → Guard B
                ↓
            HAS_FLAW → Trust Issues → CHALLENGES → In Scene 7
```

The LLM receives a "pre-connected puzzle" ensuring every generated sentence honors the existing web of relationships.

---

## The Narrative Ontology

We defined 17 edge types that capture the mechanics of story:

| Category | Edge Types | What They Capture |
|----------|------------|-------------------|
| **Goal-Obstacle-Conflict** | MOTIVATES, HINDERS, CAUSES | The engine of plot |
| **Character Dynamics** | CHALLENGES, KNOWS, CONTRADICTS | Relationship tension |
| **Narrative Threading** | FORESHADOWS, CALLBACKS | Setup and payoff |
| **Basic Relationships** | LOCATED_IN, OWNS, LOVES, HATES | World structure |

This isn't just data storage - it's a **computable model of drama**.

---

## What GraphRAG Enables

### Active, Not Passive

Standard RAG is passive - it waits for queries and returns matches.

GraphRAG is active:
- It **infers** implied information (if Character A is in the Forest, and the Forest contains Wolves, danger exists)
- It **predicts** plot requirements (a gun in Act 1 must fire in Act 3)
- It **enforces** consistency (a dead character can't act in later scenes)

### Narrative Analysis

The graph can calculate metrics that matter to storytelling:

**Tension Score**: How many active HINDERS, unresolved FORESHADOWS, and CHALLENGES edges exist? High tension means conflict is escalating. Low tension means we need obstacles.

**Pacing Analysis**: What's the ratio of action edges to setup edges? Are we in a fast-paced sequence or building toward something?

**Community Detection**: Which characters cluster together? These clusters often represent subplots. Characters connecting clusters are your bridge characters - usually protagonists or catalysts.

### Tiered Verification

Not all consistency checks need the same depth:

| Tier | Speed | Example Checks |
|------|-------|----------------|
| **FAST** | <500ms | Is a dead character speaking? Missing callbacks? |
| **MEDIUM** | 2-5s | Has the protagonist's flaw been challenged recently? |
| **SLOW** | 5-30s | Full semantic analysis of timeline consistency |

Writers get immediate feedback on obvious issues without waiting for deep analysis.

---

## The Philosophy

### Structure Before Freedom

This aligns with Writers Factory's core philosophy. The graph enforces structural integrity so the creative LLM can focus on prose, voice, and artistry.

The writer provides vision. The graph provides memory. The LLM provides speed.

### Engineering Creativity

GraphRAG is infrastructure for creativity. It doesn't constrain the writer - it amplifies their vision by ensuring consistency at scale.

This is the core thesis of the course: **We are not just writing a novel; we are engineering a synthetic cognitive system.**

---

## For Students: Engineering Lessons

This implementation demonstrates several software engineering principles:

1. **Incremental Enhancement**: We built in phases, each adding capability without breaking existing function
2. **Graceful Degradation**: If embeddings aren't available, graph traversal still works
3. **Separation of Concerns**: Extraction, storage, retrieval, and analysis are independent services
4. **Configuration Over Code**: Edge types and verification levels are settings, not hardcoded

---

## Conclusion

GraphRAG transforms Writers Factory from a text completion tool into a **narrative operating system**.

The graph doesn't just remember your story - it understands its structure. It ensures that every scene honors the web of relationships you've built. It catches contradictions before they become plot holes. It calculates tension and suggests pacing adjustments.

This is what we mean by "engineering creativity" - using software architecture to amplify human vision, not replace it.

---

**For technical implementation details, see [GraphRAG Implementation (Technical)](graphrag_implementation.md)**

---

*Implementation: December 2025*
*Authors: Claude Code (Opus 4.5) + Human collaboration*
*Course: AI and the One-Week Novel - Skoltech ISP 2026*
