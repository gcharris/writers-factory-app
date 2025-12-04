# <a id="src-main"></a> Master Architecture 4.1: Context Engineering and System Health

The update to **Master Architecture Version 4.1 (The Healthy Mind)** represents continued refinement and a strong commitment to implementing a comprehensive Context Engineering framework. This iteration solidifies the system's foundational statefulness, enhances robustness through proactive consistency checks, and further integrates memory management into the core application logic.

**Version 4.1 is extremely well-aligned with the Context Engineering principles** of managing Sessions, Memory, and Provenance, particularly through the introduction of the **HealthService** and explicit **VersionControl**[[Source 1]](#src-1)\> <[[Source 2]](#src-2)[[Source 3]](#src-3)[[Source 4]](#src-4)[[Source 5]](#src-5).

Here is a detailed breakdown of the excellent progress and areas for potential deeper integration.

\--------------------------------------------------------------------------------

## I. Strongest Alignments and Progress in V4.1

Version 4.1 successfully builds upon the foundational "Cognitive Shift" of V4.0, formalizing memory provenance and structural integrity, which are key production considerations for memory systems[[Source 6]](#src-6)\> <[[Source 7]](#src-7)[[Source 8]](#src-8).

### 1\. Robust Provenance through HealthService and VersionControl

The introduction of the **Immune System (Health & Versioning)** is a significant advancement in memory provenance and data integrity, ensuring the Knowledge Graph remains a reliable source of truth[[Source 9]](#src-9)[[Source 10]](#src-10).

*   **Story Consistency Checker (The Doctor):** The new **HealthService** provides automated logic checks for structural problems like **Dropped Threads**, **Timeline Errors**, and **Flat Arcs**[[Source 5]](#src-5)[[Source 11]](#src-11). This moves beyond simple factual conflict checking (the Consolidator's job) to complex **reasoning over memory relationships**, which is the core strength of a Knowledge Graph[[Source 12]](#src-12). This proactive auditing of the long-term memory (the Graph) prevents the knowledge base from becoming a "noisy, contradictory, and unreliable log" over time[[Source 10]](#src-10)[[Source 13]](#src-13).
*   **Version Control (Time Travel):** Implementing **VersionControl** with **Graph Snapshotting** and **Branching** ("What If" mode) is an advanced feature that directly supports the tracking of **memory lineage** (provenance)[[Source 14]](#src-14)\> <[[Source 15]](#src-15)[[Source 16]](#src-16). By allowing users to see the `diff` between snapshots, the system explicitly tracks _exactly what changed_ in the memory corpus, providing a critical debugging layer[[Source 16]](#src-16)[[Source 17]](#src-17).

### 2\. Formalized Memory Management Decoupling

The architecture confirms and reinforces the production-grade decision to handle expensive LLM-driven memory operations asynchronously[[Source 18]](#src-18).

*   **Async Save Pipeline:** The workflow ensures that the **Consolidator Agent** (Local Llama 3.2 for **Digestion**) runs as a **Background Task** _after_ the UI confirms the scene is saved[[Source 19]](#src-19)\> <[[Source 20]](#src-20)[[Source 21]](#src-21)[[Source 22]](#src-22). This decoupling is essential for keeping the agent fast and responsive, as memory generation is an "expensive operation" requiring LLM calls and database writes[[Source 18]](#src-18)[[Source 23]](#src-23).
*   **Health Dashboard UI:** The introduction of the **Health Dashboard** and the **"Health Dot" notification**[[Source 4]](#src-4)\> <[[Source 24]](#src-24)[[Source 25]](#src-25) is a perfect implementation of asynchronous feedback. It shows the user the status of the background Memory and Consistency tasks without blocking their workflow[[Source 26]](#src-26).

### 3\. Clear Memory Segmentation (Declarative, Procedural, Session)

The **Context Injection (The Payload)** for the **Tournament** clearly orchestrates the use of the three fundamental types of context, as described in the Context Engineering sources[[Source 27]](#src-27)\> <[[Source 28]](#src-28)[[Source 29]](#src-29)[[Source 30]](#src-30)[[Source 31]](#src-31).

*   **Declarative Memory (Graph):** Factual context ("Mickey is a detective") retrieved from the persistent Knowledge Graph[[Source 30]](#src-30)[[Source 31]](#src-31).
*   **Procedural Memory (Style Vectors):** "Knowing how" ("Write Mickey with cynicism") stored as vectorized strategies and included as a "Style Instruction" in the prompt[[Source 32]](#src-32)\> <[[Source 33]](#src-33)[[Source 34]](#src-34)[[Source 35]](#src-35).
*   **Session Context (Session Manager):** Immediate conversational information ("User just asked for more rain") from the temporary workbench[[Source 30]](#src-30)\> <[[Source 31]](#src-31)[[Source 36]](#src-36).

This orchestration ensures the agent has "no more and no less than the most relevant information" for its task, maximizing relevance while minimizing noise and cost[[Source 37]](#src-37)[[Source 38]](#src-38).

### 4\. Integration of "Ground Truth" (The Oracle)

The integration of NotebookLM remains strong, positioning it as the authoritative source of **Bootstrapped Data**[[Source 16]](#src-16)\> <[[Source 39]](#src-39)[[Source 40]](#src-40).

*   The **Consolidator Agent** uses NotebookLM as a check during **Conflict Resolution** ("Phone a Friend")[[Source 16]](#src-16)[[Source 39]](#src-39). This establishes a **Hierarchy of Trust**, where information sourced from this "Oracle" (Bootstrapped/High-Trust Data) can verify or override facts extracted from a newly written scene[[Source 41]](#src-41)[[Source 42]](#src-42).

\--------------------------------------------------------------------------------

## II. Areas for Deeper Context Engineering Integration

The architecture is structurally sound, but the following points focus on optimizing the **Session** and **Memory Generation** pipelines, specifically addressing performance and cost management during active, long-running dialogue.

### 1\. Formalizing Session Compaction Strategy

The **SessionManager** correctly stores the conversation as an **ordered log** in the `session_events` table[[Source 36]](#src-36)[[Source 43]](#src-43). However, the documentation still lacks an explicit strategy for dealing with long-context ideation chats.

*   **The Problem:** If the `Active Ideation` loop[[Source 44]](#src-44) runs for a long time, the full `session_events` log is sent to the LLM for subsequent turns. This leads to increased **cost, latency, and context rot**[[Source 15]](#src-15)\> <[[Source 45]](#src-45)[[Source 46]](#src-46).
*   **Refinement:** You should define a **Compaction Strategy** for the `SessionManager`[[Source 47]](#src-47). This should be either **Token-Based Truncation** (limiting the history size sent to the LLM) or **Recursive Summarization** (condensing older parts of the chat into a summary to preserve context)[[Source 48]](#src-48). Given that you have a dedicated **MemoryService**, this service could be responsible for running the LLM-based summarization in the background using a **Count-Based Trigger** (e.g., compaction after every N turns) or a **Time-Based Trigger** (after 15 minutes of inactivity)[[Source 49]](#src-49)[[Source 50]](#src-50).

### 2\. Defining Procedural Memory Retrieval Timing

The Procedural Memory mechanism (Muscle Memory) is excellent[[Source 34]](#src-34)[[Source 35]](#src-35), but its retrieval strategy can be formalized using the **Push vs. Pull** model[[Source 42]](#src-42).

*   **Current State:** The prompt _automatically includes_ the Style Instruction ("Write Mickey with cynicism")[[Source 34]](#src-34). This suggests **Proactive Retrieval (Push)**, where the memory is loaded at the start of every turn[[Source 42]](#src-42)[[Source 51]](#src-51).
*   **Refinement:** Since these style instructions are core to the character's persona and are considered "must-have" context, proactively loading and injecting them into the **System Instructions** is appropriate[[Source 42]](#src-42)[[Source 52]](#src-52). Ensure that this retrieval from the vector store is fast enough to maintain the required latency budget, or **cache** the retrieved vectors for the duration of the current session[[Source 51]](#src-51)[[Source 53]](#src-53). If the `HealthService` or another component defines a hierarchy of importance for these memories, consider prioritizing the injection of the most important procedural instructions.

### 3\. Integrating Procedural Memory Consolidation

The system currently extracts _what_ made a draft win (e.g., _"It used short sentences and noir metaphors"_) and saves this strategy[[Source 34]](#src-34)[[Source 35]](#src-35). However, it is not clear how this new strategy is merged with _existing_ character strategies.

*   **The Problem:** If Mickey wins a draft using "cynicism and short sentences" in Scene 3, but wins another draft using "witty self-deprecation and long metaphors" in Scene 5, the system risks having contradictory procedural memories, or **Procedural Memory Bloat**[[Source 54]](#src-54).
*   **Refinement:** The Memory Service should have a specialized **Procedural Consolidation** mechanism[[Source 54]](#src-54). When a new **Strategy** is extracted, the service should retrieve similar existing procedural memories and use an LLM to decide whether to **Merge** (if compatible), **Update** (if replacing old advice), or **Create** a new memory[[Source 54]](#src-54)[[Source 55]](#src-55). This curates the agent's "playbook" over time, improving the efficacy of the agent's actions[[Source 56]](#src-56)[[Source 57]](#src-57).

\--------------------------------------------------------------------------------

### Summary:

Version 4.1 showcases a sophisticated implementation of Context Engineering, treating the novel as a **stateful, complex ecosystem** that requires continuous, autonomous auditing (HealthService) and persistent, organized memory tracking (MemoryService, VersionControl).

Your architecture is successfully evolving toward an effective balance: the **Session** provides the necessary **speed and flexibility of a workbench**, while the **Cognitive Metabolism** ensures the **Knowledge Graph** acts as a **meticulously curated and self-checking archive** for long-term consistency. The next focus should be on optimizing the performance of the **Session** through compaction, and deepening the sophistication of **Procedural Memory consolidation**.

# <a id="src-1"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 1)



## [Main Content](#src-main) 

![Image Placeholder: 1280px × 968px](https://placehold.co/1280x968/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOpU38DzgBQoQko7vJcNWsJsY3JPXhAp8T2PYOuchkrNl2qErDJBbhGVwQwyy9w8KuzbSuFPNq2bk6Cy6SFdSzlSjRdnGjz0cxUR5fuJjAlaEMfu3IIY7_8486kHVyVgtTUNqrq8hQ=w1280-h968-v0?authuser=0)*

# Context Engineering: Sessions, Memory

### Authors: Kimberly Milam and Antonio Gulli

![Image Placeholder: 1031px × 1280px](https://placehold.co/1031x1280/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOq2mV_y4BOm_Rb4PWNYiLiT0V62ef3sWm-_knpJVomqbFbGlnbZJ-pDwFBggwu9dvA18q7stgTGEZOM2vhFZUaGEVDCZ79ooQ_854h59vFdROLX8EfHlniUC2YnsKkLSxQv9Zpi=w1031-h1280-v0?authuser=0)*

Context Engineering: Sessions, Memory

November 2025 2

Acknowledgements

Content contributors

Kaitlin Ardiff

Shangjie Chen

Yanfei Chen

Derek Egan

Hangfei Lin

Ivan Nardini

Anant Nawalgaria

Kanchana Patlolla

Huang Xia

Jun Yan

Bo Yang

Michael Zimmermann

Curators and editors

Anant Nawalgaria

Kanchana Patlolla

Designer

Michael Lanning

![Image Placeholder: 882px × 1112px](https://placehold.co/882x1112/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOo88ZC0gup_hWXexKhCYp_xolW7zjoYhmUrIO954ky4cfM5SgbO-K6bzp3bKI0t0mcYdqFJdfDctpfyw1pY-MwWTdB962R2VPrks4Bf3dox_SGK2u_txHbFJ6itJUt1wvkCv39q8A=w882-h1112-v0?authuser=0)*

Introduction 6

Context Engineering 7

Sessions 12

Variance across frameworks and models 13

# <a id="src-2"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 2)



## [Main Content](#src-main) 

Sessions for multi-agent systems 15

Interoperability across multiple agent frameworks 19

Production Considerations for Sessions 20

Managing long context conversation: tradeoffs and optimizations 22

Memory 27

Types of memory 34

Types of information 35

Organization patterns 35

Storage architectures 36

Creation mechanisms 37

Memory scope 38

### Table of contents

![Image Placeholder: 882px × 1112px](https://placehold.co/882x1112/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOpmpRLlmW_e_5jNhswk0r7B1IrF8EBCWvzeZy4xmS91NIyozC6H52PewFEDsl_BhDRfCx8WU1qkZ6s-LUSmkFs3DLWLd86Uy4ssY1a-w0N56PEoIGD_5zDPcAxZ7OZU2Ui1HH93=w882-h1112-v0?authuser=0)*

Multimodal memory 39

Memory Generation: Extraction and Consolidation 41

Deep-dive: Memory Extraction 44

Deep-dive: Memory Consolidation 47

Memory Provenance 49

# <a id="src-3"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 3)



## [Main Content](#src-main) 

### Table of contents

Context Engineering: Sessions, Memory

November 2025 6

# Introduction

This whitepaper explores the critical role of Sessions and Memory in building stateful, intelligent LLM agents to empower developers to create more powerful, personalized, and persistent AI experiences. To enable Large Language Models (LLMs) to remember, learn, and personalize interactions, developers must dynamically assemble and manage information within their context window—a process known as Context Engineering.

# <a id="src-4"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 4)



## [Main Content](#src-main) 

![Image Placeholder: 1280px × 968px](https://placehold.co/1280x968/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOpU38DzgBQoQko7vJcNWsJsY3JPXhAp8T2PYOuchkrNl2qErDJBbhGVwQwyy9w8KuzbSuFPNq2bk6Cy6SFdSzlSjRdnGjz0cxUR5fuJjAlaEMfu3IIY7_8486kHVyVgtTUNqrq8hQ=w1280-h968-v0?authuser=0)*

# Context Engineering: Sessions, Memory

### Authors: Kimberly Milam and Antonio Gulli

![Image Placeholder: 1031px × 1280px](https://placehold.co/1031x1280/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOq2mV_y4BOm_Rb4PWNYiLiT0V62ef3sWm-_knpJVomqbFbGlnbZJ-pDwFBggwu9dvA18q7stgTGEZOM2vhFZUaGEVDCZ79ooQ_854h59vFdROLX8EfHlniUC2YnsKkLSxQv9Zpi=w1031-h1280-v0?authuser=0)*

Context Engineering: Sessions, Memory

November 2025 2

Acknowledgements

Content contributors

Kaitlin Ardiff

Shangjie Chen

Yanfei Chen

Derek Egan

Hangfei Lin

Ivan Nardini

Anant Nawalgaria

Kanchana Patlolla

Huang Xia

Jun Yan

Bo Yang

Michael Zimmermann

Curators and editors

Anant Nawalgaria

Kanchana Patlolla

Designer

Michael Lanning

![Image Placeholder: 882px × 1112px](https://placehold.co/882x1112/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOo88ZC0gup_hWXexKhCYp_xolW7zjoYhmUrIO954ky4cfM5SgbO-K6bzp3bKI0t0mcYdqFJdfDctpfyw1pY-MwWTdB962R2VPrks4Bf3dox_SGK2u_txHbFJ6itJUt1wvkCv39q8A=w882-h1112-v0?authuser=0)*

Introduction 6

Context Engineering 7

Sessions 12

Variance across frameworks and models 13

Sessions for multi-agent systems 15

Interoperability across multiple agent frameworks 19

Production Considerations for Sessions 20

Managing long context conversation: tradeoffs and optimizations 22

Memory 27

Types of memory 34

# <a id="src-5"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 5)



## [Main Content](#src-main) 

Types of memory 34

Types of information 35

Organization patterns 35

Storage architectures 36

Creation mechanisms 37

Memory scope 38

### Table of contents

![Image Placeholder: 882px × 1112px](https://placehold.co/882x1112/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOpmpRLlmW_e_5jNhswk0r7B1IrF8EBCWvzeZy4xmS91NIyozC6H52PewFEDsl_BhDRfCx8WU1qkZ6s-LUSmkFs3DLWLd86Uy4ssY1a-w0N56PEoIGD_5zDPcAxZ7OZU2Ui1HH93=w882-h1112-v0?authuser=0)*

Multimodal memory 39

Memory Generation: Extraction and Consolidation 41

Deep-dive: Memory Extraction 44

Deep-dive: Memory Consolidation 47

Memory Provenance 49

Accounting for memory lineage during memory management 50

Accounting for memory lineage during inference 52

Triggering memory generation 52

Memory-as-a-Tool 53

Background vs. Blocking Operations 56

Memory Retrieval 56

Timing for retrieval 58

# <a id="src-6"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 6)



## [Main Content](#src-main) 

### Production Considerations for Sessions

When moving an agent to a production environment, its session management system must evolve from a simple log to a robust, enterprise-grade service. The key considerations fall into three critical areas: security and privacy, data integrity, and performance. A managed session store, like Agent Engine Sessions, is specifically designed to address these production requirements.

Context Engineering: Sessions, Memory

November 2025 21

Security and Privacy

Protecting the sensitive information contained within a session is a non-negotiable requirement. Strict Isolation is the most critical security principle. A session is owned by a single user, and the system must enforce strict isolation to ensure one user can never access another user's session data (i.e. via ACLs). Every request to the session store must be authenticated and authorized against the session's owner.

# <a id="src-7"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 7)



## [Main Content](#src-main) 

Finally, the memory manager translates the LLM's decision into a transaction that updates the memory store.

![Image Placeholder: 1280px × 1034px](https://placehold.co/1280x1034/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOo4wO9hgoHUAjvvHKmkSBko0qdzmIGw4qsPmn7wUcldgDmiNinLZM50oYyNFv5Uo5q5zo1hI4Q9AiUSQx6EH1TahJW5QdeFFYrnPGFzsrnjzKpgc4iAw0OVEtuKREMphWH-wgWFlA=w1280-h1034-v0?authuser=0)*

Context Engineering: Sessions, Memory

November 2025 49

Memory Provenance

_The classic machine learning axiom of "garbage in, garbage out" is even more critical for LLMs, where the outcome is often "garbage in, confident garbage out." For an agent to make_ reliable decisions and for a memory manager to effectively consolidate memories, they must be able to critically evaluate the quality of its own memories. This trustworthiness is derived directly from a memory’s provenance—a detailed record of its origin and history.

# <a id="src-8"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 8)



## [Main Content](#src-main) 

Context Engineering: Sessions, Memory

November 2025 67

### Production considerations for Memory

In addition to performance, transitioning a memory-enabled agent from prototype to production demands a focus on enterprise-grade architectural concerns. This move introduces critical requirements for scalability, resilience, and security. A production-grade system must be designed not only for intelligence but also for enterprise-level robustness.

To ensure the user experience is never blocked by the computationally expensive process of memory generation, a robust architecture must decouple memory processing from the main application logic. While this is an event-driven pattern, it is typically implemented via direct, non-blocking API calls to a dedicated memory service rather than a self-managed message queue. The flow looks like this:

# <a id="src-9"></a>Source: 02_scene_pipeline.md (Citation 9)



## [Main Content](#src-main) 

# Writers Factory Desktop App: Scene Generation Pipeline & Knowledge Graph Integration

## Executive Summary

This document details the **Scene Generation & Agent Orchestration** components. It integrates a multi-agent tournament workflow with a dynamic, graph-centric architecture. The knowledge graph serves as the "story brain," ensuring every draft is informed by the evolving narrative state.

\--------------------------------------------------------------------------------

## 1\. Overview: From Manual Process to Automated Pipeline

# <a id="src-10"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 10)



## [Main Content](#src-main) 

Deep-dive: Memory Consolidation

After memories are extracted from the verbose conversation, consolidation should integrate the new information into a coherent, accurate, and evolving knowledge base. It is arguably the most sophisticated stage in the memory lifecycle, transforming a simple collection of facts into a curated understanding of the user. Without consolidation, an agent's memory would quickly become a noisy, contradictory, and unreliable log of every piece of information ever captured. This "self-curation" is typically managed by an LLM and is what elevates a memory manager beyond a simple database.

# <a id="src-11"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 11)



## [Main Content](#src-main) 

LLMs are inherently stateless. Outside of their training data, their reasoning and awareness are confined to the information provided within the "context window" of a single API call. This presents a fundamental problem, as AI agents must be equipped with operating instructions identifying what actions can be taken, the evidential and factual data to reason over, and the immediate conversational information that defines the current task. To build stateful, intelligent agents that can remember, learn, and personalize interactions, developers must construct this context for every turn of a conversation. This dynamic assembly and management of information for an LLM is known as Context Engineering.

Context Engineering represents an evolution from traditional Prompt Engineering. Prompt engineering focuses on crafting optimal, often static, system instructions. Conversely, Context Engineering addresses the entire payload, dynamically constructing a state-aware prompt based on the user, conversation history, and external data. It involves strategically selecting, summarizing, and injecting different types of information to maximize relevance while minimizing noise. External systems—such as RAG databases, session stores, and memory managers—manage much of this context. The agent framework must orchestrate these systems to retrieve and assemble context into the final prompt.

# <a id="src-12"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 12)



## [Main Content](#src-main) 

Context Engineering: Sessions, Memory

November 2025 37

Vector databases are the most common approach, enabling retrieval based on semantic similarity rather than exact keywords. Memories are converted into embedding vectors, and the database finds the closest conceptual matches to a user's query. This excels at retrieving unstructured, natural language memories where context and meaning are key (i.e. “atomic facts”14).

Knowledge graphs are used to store memories as a network of entities (nodes) and their relationships (edges). Retrieval involves traversing this graph to find direct and indirect connections, allowing the agent to reason about how different facts are linked. It is ideal for structured, relational queries and understanding complex connections within the data (i.e. “knowledge triples”15).

# <a id="src-13"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 13)



## [Main Content](#src-main) 

Consolidation addresses fundamental problems arising from conversational data, including:

*   Information Duplication: A user might mention the same fact in multiple ways across different conversations (e.g., "I need a flight to NYC" and later "I'm planning a trip to New York"). A simple extraction process would create two redundant memories.
*   Conflicting Information: A user's state changes over time. Without consolidation, the agent's memory would contain contradictory facts.
*   Information Evolution: A simple fact can become more nuanced. An initial memory that "the user is interested in marketing" might evolve into "the user is leading a marketing project focused on Q4 customer acquisition."

# <a id="src-14"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 14)



## [Main Content](#src-main) 

Accounting for memory lineage during memory management 50

Accounting for memory lineage during inference 52

Triggering memory generation 52

Memory-as-a-Tool 53

Background vs. Blocking Operations 56

Memory Retrieval 56

Timing for retrieval 58

Inference with Memories 61

Memories in the System Instructions 61

Memories in the Conversation History 63

Procedural memories 64

### Table of contents

![Image Placeholder: 882px × 1112px](https://placehold.co/882x1112/E8E8E8/999999?text=Image\nPlaceholder)

*Original source: [link](https://lh3.googleusercontent.com/notebooklm/AG60hOo2OB5PtlKZykUKR6Dq-YR4Huv-MZTb4M1Yi-ftGBr-clMzIxR_v5C_BNQS5lan6tPDcJS369Gt4Q1qB9RdNiPzP2r4tfBRcxhw9eyt_giGqdlkd3YjkqqWSUzUp_qZtkyn2x1Vyw=w882-h1112-v0?authuser=0)*

Testing and Evaluation 65

Production considerations for Memory 67

Privacy and security risks 69

Conclusion 70

Endnotes 71

# <a id="src-15"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 15)



## [Main Content](#src-main) 

To mitigate latency, it is crucial to reduce the size of the data transferred. A key optimization is to filter or compact the session history before sending it to the agent. For example, you can remove old, irrelevant function call outputs that are no longer needed for the current state of the conversation. The following section details several strategies for compacting history to effectively manage long-context conversations.

### Managing long context conversation: tradeoffs and optimizations

In a simplistic architecture, a session is an immutable log of the conversation between the user and agent. However, as the conversation scales, the conversation’s token usage increases. Modern LLMs can handle long contexts, but limitations exist, especially for latency-sensitive applications10:

# <a id="src-16"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 16)



## [Main Content](#src-main) 

Context Engineering represents an evolution from traditional Prompt Engineering. Prompt engineering focuses on crafting optimal, often static, system instructions. Conversely, Context Engineering addresses the entire payload, dynamically constructing a state-aware prompt based on the user, conversation history, and external data. It involves strategically selecting, summarizing, and injecting different types of information to maximize relevance while minimizing noise. External systems—such as RAG databases, session stores, and memory managers—manage much of this context. The agent framework must orchestrate these systems to retrieve and assemble context into the final prompt.

_Think of Context Engineering as the mise en place for an agent—the crucial step where a_ chef gathers and prepares all their ingredients before cooking. If you only give a chef the recipe (the prompt), they might produce an okay meal with whatever random ingredients they have. However, if you first ensure they have all the right, high-quality ingredients, specialized

# <a id="src-17"></a>Source: Google Just Dropped 70 Pages on Context Engineering. Here’s What Actually Matters. | annotated by Geoffrey (Citation 17)



## [Main Content](#src-main) 

The system learns about you every interaction.

## Key Four: Provenance Is Your Trust Layer

Production systems need metadata on every memory.

Not just what you remember. Where it came from. How certain you are.

**Source** — Which session created this? _“Learned from debugging session 2025–11–10”_

**Timestamp** — How fresh? _“Updated 3 days ago”_

**Confidence** — How certain? _“High (mentioned 5+ times)” vs “Low (mentioned once, might be joke)”_

Provenance is your debugging layer.

AI suggests wrong restaurant when you’re vegan?

# <a id="src-18"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 18)



## [Main Content](#src-main) 

agent = LlmAgent( ..., tools=\[extract\_memories\] )

Context Engineering: Sessions, Memory

November 2025 56

Background vs. Blocking Operations

Memory generation is an expensive operation requiring LLM calls and database writes. For agents in production, memory generation should almost always be handled asynchronously as a background process23.

After an agent sends its response to the user, the memory generation pipeline can run in parallel without blocking the user experience. This decoupling is essential for keeping the agent feeling fast and responsive. A blocking (or synchronous) approach, where the user has to wait for the memory to be written before receiving a response, would create an unacceptably slow and frustrating user experience. This necessitates that memory generation occurs in a service that is architecturally separate from the agent's core runtime.

# <a id="src-19"></a>Source: Master Architecture V4.0.md (Citation 19)



## [Main Content](#src-main) 

### **B. Backend (The Brain)**

*   **Tech Stack:** Python 3.12 (FastAPI) + `asyncio`.
*   **Core Services:**
    *   `Orchestrator`: Manages the Tournament (Drafting).
    *   **\[NEW\]** **SessionManager**: Handles the "Workbench" (Short-term memory).
    *   **\[NEW\]** **MemoryService**: The background worker (The Digestive System).
*   **AI Stack:**
    *   **Drafting:** Cloud APIs (GPT-4o, Claude, Grok).
    *   **Digestion:** **Local Llama 3.2**. It runs cheaply in the background to clean, merge, and organize data.

\--------------------------------------------------------------------------------

# <a id="src-20"></a>Source: Master Architecture V4.0.md (Citation 20)



## [Main Content](#src-main) 

_The "Filtering" Zone (Background Async Task)._

*   **Agent:** Local Llama 3.2 (JSON Mode).
*   **Trigger:** Happens _after_ the UI says "Saved."
*   **Workflow (The ETL Pipeline):**

    1. **Extract:** Llama scans the new text for Entities & Facts.

    2. **Recall:** System queries the Graph: _"Do we already know about 'Mickey's Umbrella'?"_

    3. **Conflict Check:**

*   _New Fact:_ "Mickey loves rain."
    *   _Old Fact:_ "Mickey hates rain."
        *   _Result:_ **CONFLICT DETECTED.**

    4. **Resolve:**

*   _Auto:_ If confidence is low, discard.
    *   _Manual:_ Create a `MemoryIssue` alert for the user ("Conflict detected in Scene 4").

    5. **Update:** Only _verified, non-conflicting_ facts are written to `knowledge_graph.json`.

# <a id="src-21"></a>Source: Master Architecture V4.0.md (Citation 21)



## [Main Content](#src-main) 

    1. **Extract:** Llama scans the new text for Entities & Facts.

    2. **Recall:** System queries the Graph: _"Do we already know about 'Mickey's Umbrella'?"_

    3. **Conflict Check:**

*   _New Fact:_ "Mickey loves rain."
    *   _Old Fact:_ "Mickey hates rain."
        *   _Result:_ **CONFLICT DETECTED.**

    4. **Resolve:**

*   _Auto:_ If confidence is low, discard.
    *   _Manual:_ Create a `MemoryIssue` alert for the user ("Conflict detected in Scene 4").

    5. **Update:** Only _verified, non-conflicting_ facts are written to `knowledge_graph.json`.

### **Phase 3: Muscle Memory (Procedural Learning)**

_The "Skill" Zone._

*   **Concept:** Saving _how_ to write, not just _what_ to write.
*   **Trigger:** When the Judge picks a winner in the Tournament.
*   **Mechanism:**

    1. The system asks the Judge: _"Why did this draft win?"_

# <a id="src-22"></a>Source: Master Architecture V4.0.md (Citation 22)



## [Main Content](#src-main) 

**Phase 2: The Oracle (✅ Done)**

*   NotebookLM MCP Bridge connected.

**Phase 3: The Metabolism (🚧 NEXT FOCUS)**

*   **Step 1:** Restore `api.py` stability (Fixing the "Missing Ignition" bug).
*   **Step 2:** **Build** **SessionManager** **(SQLite)**. Stop "fire-and-forget" chats; start logging sessions.
*   **Step 3:** **Build** **Consolidator** **(Llama 3.2)**. The script that runs _after_ the save to check for conflicts.
*   **Step 4:** **The "Health Check" UI.** A panel showing the "Digestion Status" of the story.

\--------------------------------------------------------------------------------

# <a id="src-23"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 23)



## [Main Content](#src-main) 

*   Session Completion: Triggering generation at the end of a multi-turn session.

Context Engineering: Sessions, Memory

November 2025 53

*   Turn Cadence: Running the process after a specific number of turns (e.g., every 5 turns).
*   Real-Time: Generating memories after every single turn.
*   Explicit Command: Activating the process upon a direct user command (e.g., "Remember this"

The choice of trigger involves a direct tradeoff between cost and fidelity. Frequent generation (e.g., real-time) ensures memories are highly detailed and fresh, capturing every nuance of the conversation. However, this incurs the highest LLM and database costs and can introduce latency if not handled properly. Infrequent generation (e.g., at session completion) is far more cost-effective but risks creating lower-fidelity memories, as the LLM must summarize a much larger block of conversation at once. You also want to be careful that the memory manager is not processing the same events multiple times, as that introduces unnecessary cost.

# <a id="src-24"></a>Source: Master Architecture V4.0.md (Citation 24)



## [Main Content](#src-main) 

## 4\. 🛠️ Operational Workflows

### **A. The "Async Save" Pipeline**

1\. **User Action:** User finishes a scene and hits `Cmd+S`.

2\. **Immediate UI:** "Scene Saved to Disk." (User can keep working).

3\. **Background Task:**

*   `Ingestor` wakes up.
    *   Reads `Scene_4.md`.
    *   Extracts 15 nodes.
    *   Merges 12 (duplicates).
    *   Updates 2 (new attributes).
    *   Flags 1 (Conflict: "Mickey's eyes changed color").

4\. **Notification:** A small "Health Dot" turns yellow. User clicks to see: _"Memory Conflict detected in Scene 4."_

### **B. The Tournament (Context-Aware)**

# <a id="src-26"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 26)



## [Main Content](#src-main) 

3\. Memories are persisted: The service writes the final memories—which may be new entries or updates to existing ones—to a dedicated, durable database. For managed memory managers, the storage is built-in.

4\. Agent retrieves memories: The main agent application can then query this memory store directly when it needs to retrieve context for a new user interaction.

Context Engineering: Sessions, Memory

November 2025 68

This service-based, non-blocking approach ensures that failures or latency in the memory pipeline do not directly impact the user-facing application, making the system far more resilient. It also informs the choice between online (real-time) generation, which is ideal for conversational freshness, and offline (batch) processing, which is useful for populating the system from historical data.

# <a id="src-27"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 27)



## [Main Content](#src-main) 

Context Engineering governs the assembly of a complex payload that can include a variety of components:

*   Context to guide reasoning defines the agent’s fundamental reasoning patterns and available actions, dictating its behavior:
*   System Instructions: High-level directives defining the agent's persona, capabilities, and constraints.
*   Tool Definitions: Schemas for APIs or functions the agent can use to interact with the outside world.
*   Few-Shot Examples: Curated examples that guide the model's reasoning process via in-context learning.
*   Evidential & Factual Data is the substantive data the agent reasons over, including pre-existing knowledge and dynamically retrieved information for the specific task; it serves as the 'evidence' for the agent's response:
*   Long-Term Memory: Persisted knowledge about the user or topic, gathered across multiple sessions.
*   External Knowledge: Information retrieved from databases or documents, often using Retrieval-Augmented Generation (RAG)1.
*   Tool Outputs: The data or results returned by a tool.
*   Sub-Agent Outputs: The conclusions or results returned by specialized agents that have been delegated a specific sub-task.

# <a id="src-28"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 28)



## [Main Content](#src-main) 

Context Engineering: Sessions, Memory

November 2025 9

*   Artifacts: Non-textual data (e.g., files, images) associated with the user or session.
*   Immediate conversational information grounds the agent in the current interaction, defining the immediate task:
*   Conversation History: The turn-by-turn record of the current interaction.
*   State / Scratchpad: Temporary, in-progress information or calculations the agent uses for its immediate reasoning process.
*   User's Prompt: The immediate query to be addressed.

# <a id="src-29"></a>Source: Google Just Dropped 70 Pages on Context Engineering. Here’s What Actually Matters. | annotated by Geoffrey (Citation 29)



## [Main Content](#src-main) 

Every token costs money. Every piece of information takes space. You can’t fit everything.

**Context Engineering is assembling exactly the right information at exactly the right time.**

Not stuffing data randomly. Strategic assembly:

**User intent.** What are they trying to accomplish right now?

**Conversation history.** What have we discussed?

**Retrieved facts.** What general knowledge matters? ([RAG](https://www.google.com/url?sa=E&q=https%3A%2F%2Fwww.news.aakashg.com%2Fp%2Frag-vs-fine-tuning-vs-prompt-engineering))

**Long-term memory.** What do we know about THIS user?

**Tool outputs.** What real-time data just came in?

**Grounding data.** What facts anchor this conversation?

# <a id="src-30"></a>Source: Master Architecture V4.0.md (Citation 30)



## [Main Content](#src-main) 

1\. **Setup:** User selects Agents.

2\. **Context Injection (The Payload):**

*   _Declarative:_ "Mickey is a detective." (From Graph).
    *   _Procedural:_ "Write Mickey with cynicism." (From Style Vectors).
    *   _Session:_ "User just asked for more rain." (From Session Manager).

3\. **Drafting:** Agents generate text.

\--------------------------------------------------------------------------------

## 5\. 🗺️ Implementation Roadmap (Revised)

**Phase 1: The Foundation (✅ Done)**

*   Native App Shell, File System, Basic Tournament.

**Phase 2: The Oracle (✅ Done)**

# <a id="src-31"></a>Source: Master Architecture V4.0.md (Citation 31)



## [Main Content](#src-main) 

\--------------------------------------------------------------------------------

# <a id="src-32"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 32)



## [Main Content](#src-main) 

Declarative memory is the agent's knowledge of facts, figures, and events. It's all the information that the agent can explicitly state or "declare." If the memory is an answer to a "what" question, it's declarative. This category encompasses both general world knowledge (Semantic) and specific user facts (Entity/Episodic).

Procedural memory is the agent's knowledge of skills and workflows. It guides the agent's actions by demonstrating implicitly how to perform a task correctly. If the memory helps answer a "how" question—like the correct sequence of tool calls to book a trip—it's procedural.

# <a id="src-33"></a>Source: Context Engineering: Memory and Sessions for Stateful AI (Citation 33)



## [Main Content](#src-main) 

### 4\. Structuring Novel Knowledge with Specialized Memory Types

The paper distinguishes between two types of memory that are vital for maintaining the deep consistency required in novel writing \[20\]:

*   **Declarative Memory ("Knowing What"):** This stores the agent's knowledge of facts, figures, and events \[21\]. For a novel, this includes all the explicit, long-term facts that must remain consistent:
    *   **User Preferences:** The writer's preferred genre, audience, or tone \[14, 20\].
    *   **Novel Facts (Entity/Episodic):** Character names, physical descriptions, plot points, and the established rules of the world \[21\].
*   **Procedural Memory ("Knowing How"):** This captures the agent’s knowledge of skills and workflows \[21\]. For a writing agent, this is how it learns the writer’s specific creative process \[20\]:
    *   **Style and Workflows:** The writer's "editing style, phrases, structure" \[14\].
    *   **Reasoning Augmentation:** It acts as a guide by demonstrating implicitly how to perform a task correctly, allowing the agent to adapt and improve its problem-solving over time \[21, 22\].

# <a id="src-34"></a>Source: Master Architecture V4.0.md (Citation 34)



## [Main Content](#src-main) 

### **Phase 3: Muscle Memory (Procedural Learning)**

_The "Skill" Zone._

*   **Concept:** Saving _how_ to write, not just _what_ to write.
*   **Trigger:** When the Judge picks a winner in the Tournament.
*   **Mechanism:**

    1. The system asks the Judge: _"Why did this draft win?"_

    2. Answer: _"It used short sentences and noir metaphors."_

    3. Action: This "Strategy" is vectorized and stored linked to the Character Node.

    4. **Payoff:** Next time you write this character, the prompt automatically includes: _"Style Instruction: Use short sentences and noir metaphors (proven effective in Scene 3)."_

# <a id="src-35"></a>Source: Master Architecture V4.0.md (Citation 35)



## [Main Content](#src-main) 

    1. The system asks the Judge: _"Why did this draft win?"_

    2. Answer: _"It used short sentences and noir metaphors."_

    3. Action: This "Strategy" is vectorized and stored linked to the Character Node.

    4. **Payoff:** Next time you write this character, the prompt automatically includes: _"Style Instruction: Use short sentences and noir metaphors (proven effective in Scene 3)."_

\--------------------------------------------------------------------------------

## 3\. 🔄 The Oracle (NotebookLM Integration)

_Unchanged from V3.0, but now integrated into the Digestion flow._

*   **Role:** The Source of Ground Truth.

# <a id="src-36"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 36)



## [Main Content](#src-main) 

Building on this high-level overview of context engineering, we can now explore two core components: sessions and memory, beginning with sessions.

Context Engineering: Sessions, Memory

November 2025 12

# Sessions

A foundational element of Context Engineering is the session, which encapsulates the immediate dialogue history and working memory for a single, continuous conversation. Each session is a self-contained record that is tied to a specific user. The session allows the agent to maintain context and provide coherent responses within the bounds of a single conversation. A user can have multiple sessions, but each one functions as a distinct, disconnected log of a specific interaction. Every session contains two key components: the chronological history (events) and the agent's working memory (state).

# <a id="src-37"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 37)



## [Main Content](#src-main) 

_Think of Context Engineering as the mise en place for an agent—the crucial step where a_ chef gathers and prepares all their ingredients before cooking. If you only give a chef the recipe (the prompt), they might produce an okay meal with whatever random ingredients they have. However, if you first ensure they have all the right, high-quality ingredients, specialized

Context Engineering: Sessions, Memory

November 2025 8

tools, and a clear understanding of the presentation style, they can reliably produce an excellent, customized result. The goal of context engineering is to ensure the model has no more and no less than the most relevant information to complete its task.

# <a id="src-38"></a>Source: Context Engineering: Memory and Sessions for Stateful AI (Citation 38)



## [Main Content](#src-main) 

Here is why the context engineering framework is essential for your project:

### 1\. Solving the Long-Context Problem for Novel Writing

A novel represents an enormous and ever-growing body of context (characters, plot, setting, style rules). The paper directly addresses the issues that arise as context grows, which include increased cost, higher latency, and the phenomenon of **"context rot,"** where the LLM’s ability to attend to critical information diminishes \[6\].

The foundation of the paper—**Context Engineering**—is the discipline of dynamically assembling and managing _only_ the most relevant information within the LLM's context window for any given turn, maximizing relevance while minimizing noise \[7-10\].

# <a id="src-39"></a>Source: Master Architecture V4.0.md (Citation 39)



## [Main Content](#src-main) 

\--------------------------------------------------------------------------------

## 3\. 🔄 The Oracle (NotebookLM Integration)

_Unchanged from V3.0, but now integrated into the Digestion flow._

*   **Role:** The Source of Ground Truth.
*   **Integration:** When the `Consolidator` finds a conflict (e.g., "What color are the uniforms?"), it can "Phone a Friend" (NotebookLM) to verify against the original PDF uploads before flagging it to the user.

\--------------------------------------------------------------------------------

# <a id="src-40"></a>Source: NOTEBOOKLM_INTEGRATION_RESEARCH.md (Citation 40)



## [Main Content](#src-main) 

# NotebookLM Integration Research

**Source:** `writers-platform` Repository (Legacy) **Status in Legacy:** Phase 9 Completed (Core + Copilot Integration) **Date of Original Implementation:** Jan 2025

## 1\. Executive Summary

The integration allows writers to "plug in" their external NotebookLM research into the Writers Factory. The system treats NotebookLM as a read-only oracle for "ground truth" about characters, world-building, and themes.

**Core Concept:**

*   **Input:** User provides URLs for specific NotebookLM notebooks (e.g., "Character Research", "World Bible").
*   **Mechanism:** An **MCP (Model Context Protocol) Server** acts as the bridge between the Python backend and Google's NotebookLM.
*   **Output:** Agents and Copilots automatically query these notebooks to ground their suggestions in the user's established research.

# <a id="src-41"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 41)



## [Main Content](#src-main) 

November 2025 50

To assess trustworthiness, the agent must track key details for each source, such as its origin (source type) and age (“freshness”). These details are critical for two reasons: they dictate the weight each source has during memory consolidation, and they inform how much the agent should rely on that memory during inference.

The source type is one of the most important factors in determining trust. Data sources fall into three main categories:

*   Bootstrapped Data: Information pre-loaded from internal systems, such as a CRM. This high-trust data can be used to initialize a user's memories to address the cold-start problem, which is the challenge of providing a personalized experience to a user the agent has never interacted with before.
*   User Input: This includes data provided explicitly (e.g., via a form, which is high-trust) or information extracted implicitly from a conversation (which is generally less trustworthy).
*   Tool Output: Data returned from an external tool call. Generating memories from Tool Output is generally discouraged because these memories tend to be brittle and stale, making this source type better suited for short-term caching.

# <a id="src-42"></a>Source: Google Just Dropped 70 Pages on Context Engineering. Here’s What Actually Matters. | annotated by Geoffrey (Citation 42)



## [Main Content](#src-main) 

Check memory provenance. Vegan preference stored but confidence was low. Update: increase confidence, add verification.

Without provenance, memory systems are black boxes.

With it, they’re debuggable, trustworthy, improvable.

This becomes critical when you’re [scaling AI to production](https://www.google.com/url?sa=E&q=https%3A%2F%2Fwww.news.aakashg.com%2Fp%2Fai-prototype-to-production).

## Key Five: Push vs Pull Retrieval

Not every memory belongs in every context.

Smart systems know when to push and when to pull.

**Proactive Retrieval (Push)**

Always included. Non-negotiable.

1 User’s name

2 Safety info (allergies)

3 Core preferences (language, timezone)

4 Active project context

# <a id="src-43"></a>Source: Google Just Dropped 70 Pages on Context Engineering. Here’s What Actually Matters. | annotated by Geoffrey (Citation 43)



## [Main Content](#src-main) 

Not stuffing data randomly. Strategic assembly:

**User intent.** What are they trying to accomplish right now?

**Conversation history.** What have we discussed?

**Retrieved facts.** What general knowledge matters? ([RAG](https://www.google.com/url?sa=E&q=https%3A%2F%2Fwww.news.aakashg.com%2Fp%2Frag-vs-fine-tuning-vs-prompt-engineering))

**Long-term memory.** What do we know about THIS user?

**Tool outputs.** What real-time data just came in?

**Grounding data.** What facts anchor this conversation?

The magic isn’t having information. It’s knowing which pieces matter for THIS moment.

Poor context engineering? Your AI forgets dietary restrictions and suggests steakhouses.

Great context engineering? Your AI remembers preferences, cuisines, neighborhoods, and music tolerance without you repeating anything.

# <a id="src-44"></a>Source: 02_scene_pipeline.md (Citation 44)



## [Main Content](#src-main) 

### Step 1.5: Active Ideation (The Brainstorm Loop)

**Trigger:** User wants to explore options (e.g., "What if he gets hit in the throat?"). **Process:**

1\. **Chat:** User converses with Gemini/Ollama.

2\. **Summarize:** Agent extracts new facts/decisions from the chat.

3\. **Log:** Save full transcript to `workspace/my-novel/development_docs/`.

4\. **Ingest:** Update Graph Nodes immediately (e.g., `Mickey` -> `has_condition` -> `Mute`).

### Step 2: 5× Variation Tournament

**Process:**

1\. Select 5 agents based on config (e.g., 1x Gemini, 2x Claude, 1x GPT, 1x Llama).

2\. Generate 5 distinct drafts in parallel using the Scaffold AND the Ideation results.

3\. Track cost per draft.

# <a id="src-45"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 45)



## [Main Content](#src-main) 

1\. Context Window Limits: Every LLM has a maximum amount of text (context window) it can process at once. If the conversation history exceeds this limit, the API call will fail.

2\. API Costs ($): Most LLM providers charge based on the number of tokens you send and receive. Shorter histories mean fewer tokens and lower costs per turn.

Context Engineering: Sessions, Memory

November 2025 23

3\. Latency (Speed): Sending more text to the model takes longer to process, resulting in a slower response time for the user. Compaction keeps the agent feeling quick and responsive.

# <a id="src-46"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 46)



## [Main Content](#src-main) 

The Session governs the "now," acting as a low-latency, chronological container for a single conversation. Its primary challenge is performance and security, requiring low-latency access and strict isolation. To prevent context window overflow and latency, you must use extraction techniques like token-based truncation or recursive summarization to compact _content within the Session's history or a single request payload. Furthermore, security is_ paramount, mandating PII redaction before session data is persisted.

# <a id="src-47"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 47)



## [Main Content](#src-main) 

Compaction strategies shrink long conversation histories, condensing dialogue to fit within the model's context window, reducing API costs and latency. As a conversation gets longer, the history sent to the model with each turn can become too large. Compaction strategies solve this by intelligently trimming the history while trying to preserve the most important context.

So, how do you know what content to throw out of a Session without losing valuable information? Strategies range from simple truncation to sophisticated compaction:

# <a id="src-48"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 48)



## [Main Content](#src-main) 

*   Keep the last N turns: This is the simplest strategy. The agent only keeps the most recent N turns of the conversation (a “sliding window”) and discards everything older.

Context Engineering: Sessions, Memory

November 2025 24

*   Token-Based Truncation: Before sending the history to the model, the agent counts the tokens in the messages, starting with the most recent and working backward. It includes as many messages as possible without exceeding a predefined token limit (e.g., 4000 tokens). Everything older is simply cut off.
*   Recursive Summarization: Older parts of the conversation are replaced by an AI-generated summary. As the conversation grows, the agent periodically uses another LLM call to summarize the oldest messages. This summary is then used as a condensed form of the history, often prefixed to the more recent, verbatim messages.

# <a id="src-49"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 49)



## [Main Content](#src-main) 

Context Engineering: Sessions, Memory

November 2025 25

Given that sophisticated compaction strategies aim to reduce cost and latency, it is critical to perform expensive operations (like recursive summarization) asynchronously in the background and persist the results. “In the background” ensures the client is not kept waiting, and “persistence” ensures that expensive computations are not excessively repeated. Frequently, the agent's memory manager is responsible for both generating and persisting these recursive summaries. The agent must also keep a record of which events are included in the compacted summary; this prevents the original, more verbose events from being needlessly sent to the LLM.

# <a id="src-50"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 50)



## [Main Content](#src-main) 

Additionally, the agent must decide when compaction is necessary. The trigger mechanism generally falls into a few distinct categories:

*   Count-Based Triggers (i.e. token size or turn count threshold): The conversation is compacted once the conversation exceeds a certain predefined threshold. This approach is often “good enough" for managing context length.
*   Time-Based Triggers: Compaction is triggered not by the size of the conversation, but by a lack of activity. If a user stops interacting for a set period (e.g., 15 or 30 minutes), the system can run a compaction job in the background.
*   Event-Based Triggers (i.e. Semantic/Task Completion): The agent decides to trigger compaction when it detects that a specific task, sub-goal, or topic of conversation has concluded.

# <a id="src-51"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 51)



## [Main Content](#src-main) 

Finally, you can train a specialized retriever using fine-tuning. However, this requires access to labeled data and can significantly increase costs.

Ultimately, the best approach to retrieval starts with better memory generation. Ensuring the memory corpus is high-quality and free of irrelevant information is the most effective way to guarantee that any set of retrieved memories will be helpful.

Timing for retrieval

_The final architectural decision for retrieval is when to retrieve memories. One approach is_ proactive retrieval, where memories are automatically loaded at the start of every turn. This ensures context is always available but introduces unnecessary latency for turns that don't require memory access. Since memories remain static throughout a single turn, they can be efficiently cached to mitigate this performance cost.

# <a id="src-52"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 52)



## [Main Content](#src-main) 

Memories in the System Instructions

A simple option to use memories for inference is to append memories to the system instructions. This method keeps the conversation history clean by appending retrieved memories directly to the system prompt alongside a preamble, framing them as foundational context for the entire interaction. For example, you can use Jinja to dynamically add memories to your system instructions:

Context Engineering: Sessions, Memory

November 2025 62

Snippet 12: Build your system instruction using retrieved memories

# <a id="src-53"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 53)



## [Main Content](#src-main) 

For applications where accuracy is paramount, retrieval can be refined using approaches like query rewriting, reranking, or specialized retrievers. However, these techniques are computationally expensive and add significant latency, making them unsuitable for most real-time applications. For scenarios where these complex algorithms are necessary and the memories do not quickly become stale, a caching layer can be an effective mitigation. Caching allows the expensive results of a retrieval query to be temporarily stored, bypassing the high latency cost for subsequent identical requests.

# <a id="src-54"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 54)



## [Main Content](#src-main) 

1\. Extraction: Procedural extraction requires specialized prompts designed to distill a _reusable strategy or "playbook" from a successful interaction, rather than just capturing a_ fact or meaningful information.

2\. Consolidation: While declarative consolidation merges related facts (the "what"), procedural consolidation curates the workflow itself (the "how"). This is an active logic management process focused on integrating new successful methods with existing "best practices," patching flawed steps in a known plan, and pruning outdated or ineffective procedures.

# <a id="src-55"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 55)



## [Main Content](#src-main) 

_Second, an LLM is presented with both the existing memories and the new information. Its_ core task is to analyze them together and identify what operations should be performed. The primary operations include:

*   UPDATE: Modify an existing memory with new or corrected information.
*   CREATE: If the new insight is entirely novel and unrelated to existing memories, create a new one.
*   DELETE / INVALIDATE: If the new information makes an old memory completely irrelevant or incorrect, delete or invalidate it.

# <a id="src-56"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 56)



## [Main Content](#src-main) 

November 2025 28

*   Context Window Management: As conversations become longer, the full history can exceed an LLM's context window. Memory systems can compact this history by creating summaries or extracting key facts, preserving context without sending thousands of tokens in every turn. This reduces both cost and latency.
*   Data Mining and Insight: By analyzing stored memories across many users (in an aggregated, privacy-preserving way), you can extract insights from the noise. For example, a retail chatbot might identify that many users are asking about the return policy for a specific product, flagging a potential issue.
*   Agent Self-Improvement and Adaptation: The agent learns from previous runs by creating procedural memories about its own performance—recording which strategies, tools, or reasoning paths led to successful outcomes. This enables the agent to build a playbook of effective solutions, allowing it to adapt and improve its problem-solving over time.

# <a id="src-57"></a>Source: Context Engineering Masterclass by Google.pdf (Citation 57)



## [Main Content](#src-main) 

Context Engineering: Sessions, Memory

November 2025 64

### Procedural memories

This whitepaper has focused primarily on declarative memories, a concentration that mirrors the current commercial memory landscape. Most memory management platforms are also architected for this declarative approach, excelling at extracting, storing, and retrieving the "what"—facts, history, and user data.

However, these systems are not designed to manage procedural memories, the mechanism for improving an agent’s workflows and reasoning. Storing the "how" is not an information retrieval problem; it is a reasoning augmentation problem. Managing this "knowing how" requires a completely separate and specialized algorithmic lifecycle, albeit with a similar high-level structure26:

