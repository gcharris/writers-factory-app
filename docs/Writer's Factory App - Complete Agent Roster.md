## Writer's Factory App - Complete Agent Roster

### Primary AI Agent

**The Foreman**

- **Role**: Ollama-powered intelligent creative writing partner
- **Epithet**: *"Intelligent Creative Writing Partner"*
- **Default Model**: Ollama Llama 3.2:3b (local, zero-cost)
- **Modes**:
  - ARCHITECT (Story Bible creation)
  - VOICE_CALIBRATION (Voice tournament)
  - DIRECTOR (Scene drafting)
  - EDITOR (Revision and polish)
- **Location**: [backend/agents/foreman.py](vscode-webview://1m4t72u4cc7qj43ikuohjj69gqd3ru8csrs2q27qnrrsfqoemhrv/backend/agents/foreman.py)

------

### Tournament Agents (Scene Generation & Voice Calibration)

Configured in [agents.yaml](vscode-webview://1m4t72u4cc7qj43ikuohjj69gqd3ru8csrs2q27qnrrsfqoemhrv/agents.yaml):

#### 1. **GPT-4o** (OpenAI)

- **Epithet**: *"The Logic Master"*
- **Role**: "You prioritize structure, reasoning, and clarity."
- **Model**: `gpt-4o`
- **Use Cases**: tournament, judging
- **Status**: ✅ Enabled

#### 2. **Claude 3.7 Sonnet** (Anthropic)

- **Epithet**: *"The Nuanced Writer"*
- **Role**: "You prioritize tone, empathy, and creative flair."
- **Model**: `claude-3-7-sonnet-20250219`
- **Use Cases**: tournament, enhancement, critique
- **Status**: ✅ Enabled

#### 3. **Grok 2** (xAI)

- **Epithet**: *"The Witty Rebel"*
- **Role**: "You prioritize humor, directness, and unconventional thinking."
- **Model**: `grok-2`
- **Use Cases**: tournament, brainstorming
- **Status**: ✅ Enabled

#### 4. **DeepSeek V3** (DeepSeek)

- **Epithet**: *"The Systems Architect"*
- **Role**: "You focus on science, logic, and tactical plotting."
- **Model**: `deepseek-chat`
- **Use Cases**: tournament, analysis
- **Status**: ✅ Enabled

#### 5. **Qwen Plus** (Qwen)

- **Epithet**: *"The Polyglot Researcher"*
- **Role**: "You weave world-building details and cultural nuance."
- **Model**: `qwen-plus`
- **Use Cases**: tournament, context_injection
- **Status**: ✅ Enabled

#### 6. **Mistral Large** (Mistral)

- **Epithet**: *"The Stylist"*
- **Role**: "You tighten prose, pacing, and descriptive texture."
- **Model**: `mistral-large-latest`
- **Use Cases**: tournament, polish
- **Status**: ✅ Enabled

#### 7. **Zhipu GLM-4** (Zhipu)

- **Epithet**: *"The Strategist"*
- **Role**: "You surface plot twists, stakes, and long-arc consistency."
- **Model**: `glm-4`
- **Use Cases**: tournament, plotting
- **Status**: ✅ Enabled

#### 8. **Ollama Mistral 7B** (Ollama - Local)

- **Epithet**: *"The Local Workhorse"*
- **Role**: "You provide quality reasoning and prose at zero cost."
- **Model**: `mistral:7b`
- **Parameters**: 7.3 billion
- **Size**: 4.4 GB
- **Context**: 33k tokens
- **Use Cases**: tournament, coordination, quick_drafts, polish, enhancement
- **Status**: ✅ Enabled (now The Foreman's default model)
- **Endpoint**: [http://localhost:11434](http://localhost:11434/)
- **Capabilities**:
  - Excellent reasoning and code quality
  - Fast inference on local hardware
  - Significantly more capable than Llama 3.2 3B
  - Good for quality local work without API costs
  - Can serve as fallback for coordination tasks

#### 9. **Ollama Llama 3.2** (Ollama - Local)

- **Epithet**: *"The Local Scout"*
- **Role**: "You prototype ideas instantly with zero token cost."
- **Model**: `llama3.2:3b`
- **Parameters**: 3 billion
- **Size**: 2.0 GB
- **Context**: 128k tokens
- **Use Cases**: brainstorming, quick_drafts, character_checks
- **Status**: ✅ Enabled
- **Endpoint**: [http://localhost:11434](http://localhost:11434/)
- **Note**: Ultra-lightweight for rapid prototyping; use Mistral 7B when quality matters

------

### Local Model Comparison

| Model | Parameters | Size | Context | Speed | Reasoning | Best For |
|-------|------------|------|---------|-------|-----------|----------|
| **Mistral 7B** | 7.3B | 4.4 GB | 33k | Fast | Excellent | Quality local work |
| **Llama 3.2** | 3B | 2.0 GB | 128k | Very Fast | Basic | Quick prototypes |

**Recommendation**: Mistral 7B is now The Foreman's default model for better quality at zero cost. Llama 3.2 remains available for ultra-fast brainstorming where quality is less critical.

------

### Mistral Clarification

There are **two different Mistral models** in this system:

1. **Mistral Large (API-based)** - 123B parameters, premium model for tournament polish work
2. **Mistral 7B (Local Ollama)** - 7.3B parameters, installed locally but not yet configured

The local Mistral 7B has been added to `agents.yaml` and is now The Foreman's default model. Mistral Large remains available for high-quality tournament work.

------

### Default Tournament Configuration

From [scene_writer_service.py:53-57](vscode-webview://1m4t72u4cc7qj43ikuohjj69gqd3ru8csrs2q27qnrrsfqoemhrv/backend/services/scene_writer_service.py#L53-L57):



```python
DEFAULT_TOURNAMENT_MODELS = [
    {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "name": "Claude Sonnet"},
    {"provider": "openai", "model": "gpt-4o", "name": "GPT-4o"},
    {"provider": "deepseek", "model": "deepseek-chat", "name": "DeepSeek"},
]
```

------

### Summary

**Total Agents**: 10 (1 primary + 9 tournament agents)

**Tournament-Ready Agents**: 7 external APIs + 2 local (both configured)

- **External APIs**: GPT-4o, Claude 3.7, Grok 2, DeepSeek V3, Qwen Plus, Mistral Large, Zhipu GLM-4
- **Local (Ollama)**:
  - ✅ Mistral 7B (configured, now The Foreman's default)
  - ✅ Llama 3.2 3B (configured)

**By Specialty**:

- **Structure & Logic**: GPT-4o (Logic Master), DeepSeek V3 (Systems Architect)
- **Prose & Style**: Claude 3.7 (Nuanced Writer), Mistral Large (Stylist)
- **Creativity & Voice**: Grok 2 (Witty Rebel), Qwen Plus (Polyglot Researcher)
- **Strategy & Plot**: Zhipu GLM-4 (Strategist)
- **Quality Local Work**: Mistral 7B (Local Workhorse) - now default for The Foreman
- **Fast Prototyping**: Llama 3.2 (Local Scout)
- **Project Management**: The Foreman (Mistral 7B-powered, coordinates all others)

**Note**: The epithets in `agents.yaml` are personality descriptors that shape each agent's creative approach in tournaments. They're not just marketing - they're actually injected into the agent's system prompt during scene generation to enforce distinct creative styles.