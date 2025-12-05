---
layout: default
title: Context Engineering
---

# Context Engineering: The New Prompt Engineering

> **"The AI revolution isn’t about bigger models. It’s about context."**

For the last two years, the industry has been obsessed with **Prompt Engineering**—the art of whispering the right magic words to get a good result.

But for a novelist building a 100,000-word manuscript, "magic words" aren't enough. You need **state**. You need **memory**. You need **consistency**.

This course introduces the next evolution of AI interaction: **Context Engineering**.

---

## The Core Shift

**Prompt Engineering** is static. It asks: *"How do I phrase this question?"*

**Context Engineering** is dynamic. It asks: *"What information does the model need right now to answer this question correctly?"*

An LLM (Large Language Model) is inherently **stateless**. It has amnesia. Every time you talk to it, it's meeting you for the first time. To write a novel, we have to cure that amnesia. We do this by dynamically assembling a "Payload" of context for every single interaction.

---

## The Architecture of a Muse

In the **Writers Factory**, we implement Google's "Context Engineering" framework to turn a stateless chatbot into a stateful creative partner.

### 1. Sessions (The Workbench)
Think of a **Session** as your messy desk while you're working. It holds the immediate conversation, the current scene draft, and your temporary notes. It is fast, chaotic, and temporary.

*   **In the App:** This is your "Ideation Chat" or the current "Drafting Tournament."

### 2. Memory (The Filing Cabinet)
**Memory** is where we store the "Truth" of the story. It is organized, searchable, and persistent. When you finish a session, the important facts are extracted and filed away here.

*   **In the App:** This is the **Knowledge Graph**. We don't just save text files; we save relationships. *Mickey KNOWS Alice. Alice IS_IN The Casino.*

---

## Types of Context

To engineer a muse, we must manage two distinct types of memory:

### Declarative Memory ("Knowing What")
These are the hard facts of your world.
*   *Character names, eye colors, backstories.*
*   *The rules of your magic system.*
*   *The plot points of Chapter 3.*

**How we engineer it:** We use **RAG (Retrieval-Augmented Generation)** to pull specific facts from your **NotebookLM** research and inject them into the prompt.

### Procedural Memory ("Knowing How")
This is the "muscle memory" of your writing style.
*   *Your sentence rhythm.*
*   *Your preference for "show, don't tell."*
*   *Your specific tone (e.g., "Noir Cynicism").*

**How we engineer it:** We run **Voice Tournaments**. When you pick a winning draft, we extract the *mathematical patterns* of that text and save them as a "Style Vector." Future prompts are instructed to match that vector.

---

## The Writers Factory Approach

We are not just writing prompts. We are building a **Context Engine**.

1.  **The Input:** You ask for a scene.
2.  **The Assembly:** The system pauses. It queries the **Knowledge Graph**:
    *   *Who is in this scene?* (Retrieves Character Nodes)
    *   *What just happened?* (Retrieves Previous Scene Summary)
    *   *What is the tone?* (Retrieves Style Vector)
3.  **The Payload:** It packages all this into a massive, invisible context window.
4.  **The Generation:** Only *then* does it ask the AI to write.

**The result?** The AI doesn't hallucinate. It doesn't forget your main character's name. It writes like *you*, because we engineered the context to make it impossible for it to be anyone else.

> **"You are Tony Stark. The Context Engine is the suit."**

---

## Deep Dive: The Systems Behind the Magic

Want to understand the specific systems that power the Context Engine?

| System | What It Does | Learn More |
|--------|--------------|------------|
| **GraphRAG** | Turns your story into a computable graph of relationships. Calculates tension, tracks setups and payoffs, detects contradictions. | [GraphRAG: The Living Brain](graphrag) |
| **Voice Calibration** | Runs a tournament where AI models compete to match your voice. The winner becomes your permanent style reference. | [Voice Calibration System](voice_calibration) |
| **Narrative Dashboard** | Real-time visualization of tension levels and pacing. Tells you when your story needs more conflict or resolution. | *Coming in Director Mode* |

These three systems work together during every scene generation, ensuring consistency across all dimensions: facts (Graph), voice (Calibration), and structure (Dashboard).
