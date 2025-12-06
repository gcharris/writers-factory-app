---
layout: default
title: LLM Models
protected: true
---

<script>
if (!sessionStorage.getItem('authenticated')) {
    window.location.href = "/portal/";
}
</script>

# Models Overview: Writing Agents and Their Foundations

This document provides an overview of the large language models used inside the **Writers Factory**. Each agent in the system is powered by a different model, which means they think, write, and respond differently. Understanding these differences will help you choose the right agent for the right task.

The purpose of the course is not to produce a perfect novel but to explore **context engineering**—learning how instructions, constraints, and narrative context shape what an AI can do. You can complete all exercises with any model, but exploring multiple models will deepen your understanding of how they vary.

---

## Why Multiple Models?

Different language models have different strengths:

*   **Some excel at narrative writing** (tone, style, pacing).
*   **Some are strong researchers**, pulling together information and structure.
*   **Some are more literal or analytical**, making them good for outlining or checking coherence.
*   **Some specialize by language**, such as Russian-language support.

Because the Writers Factory is agent-based, each agent behaves differently depending on the model behind it. This variety is intentional.

---

## Two "Tournaments": Choosing Your Voices

As part of the course, you will run two small "tournaments" among your agents:

### 1. Narration & Voice Tournament
Early in the process, you will send identical prompts to several agents to compare how each one handles narration, tone, and stylistic choices. This helps you discover which model best matches the voice you want for your novel.

### 2. Scene-Writing Tournament
Later, during scene creation, you can give the same scene prompt to multiple agents. By comparing their interpretations—structure, detail, pacing—you get a clear sense of which agents perform best for specific types of scenes.

These tournaments are not about competition but **exploration**. They give you a practical feel for model differences and help you choose which agents should carry the main narrative load.

---

## Model Access During the MVP Trial

During the MVP period of the Writers Factory:

*   **Bring Your Own Key**: Required for the first-tier American models (OpenAI, Anthropic, XAI/Grok, Google Gemini).
*   **Keys Included (MVP Trial)**: All other models are provided during the MVP period.
*   **Shared Yandex Key (Russian Writing)**: A shared Yandex key is included for now. High usage may require students to switch to personal keys.

---

## Full Model Index (by Region)

### — US —
*   **OpenAI** (GPT-4o, o1-preview)
*   **Anthropic** (Claude 3.5 Sonnet, Opus)
*   **XAI** (Grok Beta)
*   **Google** (Gemini 1.5 Pro)

### — China / Asia —
*   **DeepSeek** (DeepSeek V3)
*   **Alibaba** (Qwen / DashScope)
*   **Moonshot** (Kimi)
*   **Zhipu AI** (ChatGLM)
*   **Tencent** (Hunyuan)

### — Europe —
*   **Mistral AI** (Mistral Large, Pixtral)

### — Russia —
*   **Yandex AI** (YandexGPT 4)

### — Local —
*   **Ollama** (Llama 3, Mistral, Gemma - running on your machine)

---

## Using Models for Writing, Research, and More

As you work through the course, you may find that:

*   **Claude-based agents** are strong narrative stylists.
*   **Gemini-based agents** often excel at research-heavy tasks.
*   **OpenAI-based agents** provide strong reasoning and structured output.
*   **Asian models** can offer surprisingly competitive capabilities depending on the prompt.
*   **Yandex** is often the best option for Russian-language writing.

Exploring these differences is part of the learning process.

---

## Why This Matters for the One-Week Novel

The course uses these models to demonstrate how much of writing is actually **structural thinking and context design**.

The novel you create is secondary—the real objective is mastering **context engineering** through deliberate experiments with multiple agents.
