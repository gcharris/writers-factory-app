# Task: Chat Input Model/Agent Dropdown

## Overview
Add a dropdown menu to the chat input area that allows users to select which AI model to use for the current message, similar to Cursor AI's model selector.

## Current State
- Chat input is in `frontend/src/lib/components/chat/ChatInput.svelte`
- The "Muse" dropdown currently exists but only shows the assistant name
- `defaultChatModel` store exists in `stores.js` (set during onboarding)
- Backend has `/api-keys/status` endpoint that returns available providers

## Requirements

### 1. Model Dropdown UI
- Replace or enhance the current "Muse" dropdown with a model selector
- Show all available models based on API key status
- Display model name and provider (e.g., "DeepSeek V3", "Claude 3.5 Sonnet")
- Visual indicator for currently selected model
- Keyboard navigation support (arrow keys, enter to select)

### 2. Available Models
Fetch from `/api-keys/status` and map to display names:

**Embedded (Free) Tier:**
- `deepseek` → "DeepSeek V3"
- `qwen` → "Qwen"
- `mistral` → "Mistral Large"
- `moonshot` → "Moonshot Kimi"
- `zhipu` → "ChatGLM"

**Premium (User Keys) Tier:**
- `openai` → "GPT-4o"
- `anthropic` → "Claude 3.5 Sonnet"
- `xai` → "Grok 2"
- `gemini` → "Gemini 2.0 Flash"

**Local:**
- `ollama` → Show installed Ollama models (fetch from `/ollama/models`)

### 3. Model Selection Behavior
- Selected model should be used for the next message only (per-message selection)
- Default to `defaultChatModel` store value when conversation starts
- Persist last-used model in session (not localStorage)
- Show model badge on sent messages to indicate which model was used

### 4. Visual Design
- Match existing UI style (dark theme, cyan accent)
- Compact dropdown that doesn't obstruct chat input
- Group models by tier (Free / Premium / Local)
- Show checkmark or highlight on selected model
- Optional: Show model capabilities/context window as tooltip

### 5. Integration Points

**Stores to use:**
- `defaultChatModel` - Initial default from onboarding
- Create new `selectedChatModel` writable for current selection

**API Endpoints:**
- `GET /api-keys/status` - Get available providers
- `GET /ollama/models` - Get local Ollama models
- Chat endpoint already accepts `model` parameter

**Files to modify:**
- `frontend/src/lib/components/chat/ChatInput.svelte` - Main implementation
- `frontend/src/lib/stores.js` - Add `selectedChatModel` store
- `frontend/src/lib/api_client.ts` - May need model mapping helpers

## Technical Notes

### Model ID Mapping
```typescript
const MODEL_IDS: Record<string, string> = {
  deepseek: 'deepseek-chat',
  qwen: 'qwen-turbo',
  mistral: 'mistral-large-latest',
  moonshot: 'moonshot-v1-8k',
  zhipu: 'glm-4',
  openai: 'gpt-4o',
  anthropic: 'claude-3-5-sonnet-20241022',
  xai: 'grok-2-latest',
  gemini: 'gemini-2.0-flash'
};
```

### Dropdown Component Structure
```svelte
<div class="model-selector">
  <button class="model-trigger" on:click={toggleDropdown}>
    <span class="model-icon">🤖</span>
    <span class="model-name">{selectedModelName}</span>
    <span class="chevron">▼</span>
  </button>

  {#if isOpen}
    <div class="model-dropdown">
      <div class="model-group">
        <div class="group-label">Free Models</div>
        {#each freeModels as model}
          <button class="model-option" on:click={() => selectModel(model)}>
            {model.name}
          </button>
        {/each}
      </div>
      <!-- Premium and Local groups -->
    </div>
  {/if}
</div>
```

## Acceptance Criteria
- [ ] Dropdown shows all available models based on API key status
- [ ] Models are grouped by tier (Free/Premium/Local)
- [ ] Selected model is visually indicated
- [ ] Model selection persists for subsequent messages in session
- [ ] Sent messages show which model was used
- [ ] Keyboard navigation works (Escape to close, arrows to navigate)
- [ ] Dropdown closes when clicking outside
- [ ] Default model comes from onboarding selection

## Reference
- Cursor AI model selector for UX inspiration
- Existing `AgentDropdown.svelte` component may have reusable patterns

## Priority
High - This is a core UX feature for model selection
