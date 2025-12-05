# Task: SettingsAdvanced Panel Enhancement

**Priority:** Low (Final Polish)
**Estimated Effort:** 2-3 hours
**Dependencies:** None (UI refinement only)

---

## Current State

`SettingsAdvanced.svelte` (917 lines) already implements:

### Implemented Features
- **Expert Mode Toggle**: Enables/disables advanced features
- **Context Window Settings**:
  - Conversation history limit (slider: 5-50)
  - Knowledge Base context limit (slider: 100-5000 chars)
  - Continuity context depth (slider: 1-10 scenes)
- **Voice Bundle Injection**: Full/Summary/Minimal modes
- **Debug Tools**: Force mode change buttons (requires Expert Mode)

### Missing Features
1. **Ollama Configuration**
   - Custom Ollama server URL (currently hardcoded to `localhost:11434`)
   - Connection test button

2. **LLM Default Parameters**
   - Temperature slider (0.0-1.0)
   - Top-P slider (0.0-1.0)
   - Max tokens default

3. **Data Management**
   - Clear conversation cache
   - Export settings to JSON
   - Import settings from JSON
   - Reset all settings to defaults

---

## Implementation

### 1. Add Ollama Configuration Section

```svelte
<!-- After Expert Mode section -->
<div class="section">
  <h3>Local AI Configuration</h3>

  <div class="setting-item">
    <div class="setting-header">
      <label for="ollama-url">Ollama Server URL</label>
    </div>
    <div class="url-input-group">
      <input
        type="text"
        id="ollama-url"
        bind:value={advanced.ollama_url}
        placeholder="http://localhost:11434"
      />
      <button class="btn-test" on:click={testOllamaConnection}>
        Test Connection
      </button>
    </div>
    {#if ollamaStatus}
      <p class="status {ollamaStatus.ok ? 'success' : 'error'}">
        {ollamaStatus.message}
      </p>
    {/if}
    <p class="setting-desc">URL for local Ollama server</p>
  </div>
</div>
```

### 2. Add LLM Default Parameters Section

```svelte
<div class="section">
  <h3>LLM Defaults</h3>
  <p class="section-desc">Default parameters for AI generation (can be overridden per-request)</p>

  <div class="setting-item">
    <div class="setting-header">
      <label for="temperature">Temperature</label>
      <span class="setting-value">{advanced.default_temperature.toFixed(2)}</span>
    </div>
    <input
      type="range"
      id="temperature"
      min="0"
      max="1"
      step="0.05"
      bind:value={advanced.default_temperature}
      class="slider"
    />
    <p class="setting-desc">
      Lower = more focused/deterministic, Higher = more creative/random
    </p>
  </div>

  <div class="setting-item">
    <div class="setting-header">
      <label for="top-p">Top-P (Nucleus Sampling)</label>
      <span class="setting-value">{advanced.default_top_p.toFixed(2)}</span>
    </div>
    <input
      type="range"
      id="top-p"
      min="0.1"
      max="1"
      step="0.05"
      bind:value={advanced.default_top_p}
      class="slider"
    />
    <p class="setting-desc">
      Controls diversity by limiting to top probability mass
    </p>
  </div>
</div>
```

### 3. Add Data Management Section

```svelte
<div class="section danger-zone">
  <h3>Data Management</h3>

  <div class="data-actions">
    <div class="action-item">
      <div class="action-info">
        <strong>Export Settings</strong>
        <p>Download all settings as JSON file</p>
      </div>
      <button class="btn-secondary" on:click={exportSettings}>
        Export
      </button>
    </div>

    <div class="action-item">
      <div class="action-info">
        <strong>Import Settings</strong>
        <p>Load settings from JSON file</p>
      </div>
      <button class="btn-secondary" on:click={importSettings}>
        Import
      </button>
      <input
        type="file"
        accept=".json"
        bind:this={fileInput}
        on:change={handleFileImport}
        style="display: none"
      />
    </div>

    <div class="action-item">
      <div class="action-info">
        <strong>Clear Conversation Cache</strong>
        <p>Remove all cached conversations (does not affect saved sessions)</p>
      </div>
      <button class="btn-warning" on:click={clearCache}>
        Clear Cache
      </button>
    </div>

    <div class="action-item">
      <div class="action-info">
        <strong>Reset All Settings</strong>
        <p>Restore all settings to factory defaults</p>
      </div>
      <button class="btn-danger" on:click={confirmReset}>
        Reset All
      </button>
    </div>
  </div>
</div>
```

### 4. Script Additions

```typescript
// Add to state
let ollamaStatus: { ok: boolean; message: string } | null = null;
let fileInput: HTMLInputElement;

// Add to advanced object initialization
advanced = {
  ...existingFields,
  ollama_url: data.ollama_url ?? 'http://localhost:11434',
  default_temperature: data.default_temperature ?? 0.7,
  default_top_p: data.default_top_p ?? 0.9,
};

// New functions
async function testOllamaConnection() {
  ollamaStatus = null;
  try {
    const response = await fetch(`${advanced.ollama_url}/api/tags`);
    if (response.ok) {
      const data = await response.json();
      const modelCount = data.models?.length ?? 0;
      ollamaStatus = {
        ok: true,
        message: `Connected! ${modelCount} model(s) available`
      };
    } else {
      ollamaStatus = {
        ok: false,
        message: `Server responded with status ${response.status}`
      };
    }
  } catch (error) {
    ollamaStatus = {
      ok: false,
      message: 'Connection failed. Is Ollama running?'
    };
  }
}

async function exportSettings() {
  try {
    const response = await fetch(`${BASE_URL}/settings/export`);
    if (response.ok) {
      const settings = await response.json();
      const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `writers-factory-settings-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  } catch (error) {
    console.error('Export failed:', error);
    errorMessage = 'Failed to export settings';
  }
}

function importSettings() {
  fileInput.click();
}

async function handleFileImport(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;

  try {
    const text = await file.text();
    const settings = JSON.parse(text);

    const response = await fetch(`${BASE_URL}/settings/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    });

    if (response.ok) {
      saveMessage = 'Settings imported successfully';
      loadSettings(); // Reload to reflect changes
    } else {
      errorMessage = 'Failed to import settings';
    }
  } catch (error) {
    errorMessage = 'Invalid settings file';
  }
}

async function clearCache() {
  if (!confirm('Clear all conversation cache? This cannot be undone.')) return;

  try {
    const response = await fetch(`${BASE_URL}/cache/clear`, { method: 'POST' });
    if (response.ok) {
      saveMessage = 'Cache cleared successfully';
    }
  } catch (error) {
    errorMessage = 'Failed to clear cache';
  }
}

async function confirmReset() {
  if (!confirm('Reset ALL settings to defaults? This cannot be undone.')) return;
  if (!confirm('Are you sure? This will reset everything.')) return;

  try {
    const response = await fetch(`${BASE_URL}/settings/reset`, { method: 'POST' });
    if (response.ok) {
      saveMessage = 'Settings reset to defaults';
      loadSettings();
    }
  } catch (error) {
    errorMessage = 'Failed to reset settings';
  }
}
```

### 5. Style Additions

```css
.url-input-group {
  display: flex;
  gap: 0.5rem;
}

.url-input-group input {
  flex: 1;
}

.btn-test {
  padding: 0.5rem 1rem;
  background: #2d2d2d;
  border: 1px solid #404040;
  border-radius: 4px;
  color: #b0b0b0;
  cursor: pointer;
  white-space: nowrap;
}

.btn-test:hover {
  border-color: #00d9ff;
  color: #00d9ff;
}

.status {
  font-size: 0.75rem;
  margin-top: 0.5rem;
}

.status.success {
  color: #00ff88;
}

.status.error {
  color: #ff4444;
}

.danger-zone {
  border-color: #ff444440;
}

.danger-zone h3 {
  color: #ff6b6b;
}

.data-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #1a1a1a;
  border-radius: 6px;
}

.action-info {
  flex: 1;
}

.action-info strong {
  display: block;
  color: #ffffff;
  margin-bottom: 0.25rem;
}

.action-info p {
  font-size: 0.75rem;
  color: #888888;
  margin: 0;
}

.btn-warning {
  padding: 0.5rem 1rem;
  background: #ff990020;
  border: 1px solid #ff9900;
  border-radius: 4px;
  color: #ff9900;
  cursor: pointer;
}

.btn-warning:hover {
  background: #ff990040;
}

.btn-danger {
  padding: 0.5rem 1rem;
  background: #ff444420;
  border: 1px solid #ff4444;
  border-radius: 4px;
  color: #ff4444;
  cursor: pointer;
}

.btn-danger:hover {
  background: #ff444440;
}
```

---

## Backend Endpoints Needed

These endpoints may need to be added to `api.py`:

```python
@app.get("/settings/export")
async def export_all_settings():
    """Export all settings as JSON"""
    return settings_service.export_all()

@app.post("/settings/import")
async def import_settings(settings: dict):
    """Import settings from JSON"""
    return settings_service.import_all(settings)

@app.post("/settings/reset")
async def reset_all_settings():
    """Reset all settings to defaults"""
    return settings_service.reset_to_defaults()

@app.post("/cache/clear")
async def clear_cache():
    """Clear conversation cache"""
    # Implementation depends on caching strategy
    return {"status": "cleared"}
```

---

## Testing Checklist

- [ ] Ollama URL can be changed and persists
- [ ] Test Connection button works (success and failure states)
- [ ] Temperature slider saves correctly
- [ ] Top-P slider saves correctly
- [ ] Export creates valid JSON file
- [ ] Import restores settings correctly
- [ ] Clear Cache works without errors
- [ ] Reset All requires double confirmation
- [ ] Reset All actually resets everything

---

## Completion Criteria

1. All three new sections visible in SettingsAdvanced
2. Ollama connection test functional
3. LLM parameters persist and load correctly
4. Data management operations work end-to-end
5. No TypeScript errors (`npm run check` passes)

---

*This is polish work - the app is fully functional without these features.*
