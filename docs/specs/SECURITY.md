# Security & Credentials Specification

**Version**: 1.0
**Status**: Draft
**Related**: ARCHITECTURE.md, Agent Pool

---

## Problem Statement

Writers Factory integrates with multiple AI providers (Anthropic, OpenAI, Google, xAI, DeepSeek). Each requires API keys that must be:

1. Stored securely (never in plaintext config files)
2. Accessible to the backend at runtime
3. Manageable by users without editing JSON files
4. Protected if the machine is compromised

---

## Architecture

### Credential Storage Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY ARCHITECTURE                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    USER INTERFACE                          │ │
│  │  Settings Panel → Add/Edit/Delete API Keys                │ │
│  │  Status indicators: ✓ Valid | ⚠ Invalid | ○ Not Set       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  CREDENTIAL MANAGER                        │ │
│  │                                                            │ │
│  │  • Validates API keys before storing                      │ │
│  │  • Encrypts/decrypts on read/write                        │ │
│  │  • Routes to appropriate storage backend                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌────────────┐      ┌────────────┐      ┌────────────────┐   │
│  │  macOS     │      │  Windows   │      │  Linux         │   │
│  │  Keychain  │      │  Credential│      │  Secret Service│   │
│  │            │      │  Manager   │      │  / libsecret   │   │
│  └────────────┘      └────────────┘      └────────────────┘   │
│                                                                  │
│  FALLBACK (if keyring unavailable):                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Encrypted JSON file with machine-derived key             │ │
│  │  ~/.writers-factory/credentials.enc                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### 1. Python Keyring Integration

```python
# backend/services/credential_service.py
import keyring
import json
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import platform

SERVICE_NAME = "writers-factory"

class CredentialService:
    """
    Secure credential storage using OS-native keychain when available.
    Falls back to encrypted file storage.
    """

    PROVIDERS = {
        'anthropic': {'key_name': 'ANTHROPIC_API_KEY', 'test_url': 'https://api.anthropic.com/v1/messages'},
        'openai': {'key_name': 'OPENAI_API_KEY', 'test_url': 'https://api.openai.com/v1/models'},
        'google': {'key_name': 'GOOGLE_API_KEY', 'test_url': 'https://generativelanguage.googleapis.com/v1/models'},
        'xai': {'key_name': 'XAI_API_KEY', 'test_url': 'https://api.x.ai/v1/models'},
        'deepseek': {'key_name': 'DEEPSEEK_API_KEY', 'test_url': 'https://api.deepseek.com/v1/models'},
    }

    def __init__(self):
        self.keyring_available = self._check_keyring()
        self.fallback_path = Path.home() / ".writers-factory" / "credentials.enc"

    def _check_keyring(self) -> bool:
        """Check if OS keyring is available and functional."""
        try:
            # Try to access keyring - will fail if no backend available
            keyring.get_keyring()
            return True
        except Exception:
            return False

    def store_credential(self, provider: str, api_key: str) -> dict:
        """
        Store an API key securely.

        Returns validation result and storage status.
        """
        if provider not in self.PROVIDERS:
            return {'success': False, 'error': f'Unknown provider: {provider}'}

        # Validate the key first
        validation = self._validate_key(provider, api_key)
        if not validation['valid']:
            return {'success': False, 'error': validation['error']}

        # Store securely
        try:
            if self.keyring_available:
                keyring.set_password(SERVICE_NAME, provider, api_key)
            else:
                self._store_fallback(provider, api_key)

            return {
                'success': True,
                'storage': 'keychain' if self.keyring_available else 'encrypted_file',
                'provider': provider
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_credential(self, provider: str) -> str | None:
        """Retrieve an API key."""
        if self.keyring_available:
            return keyring.get_password(SERVICE_NAME, provider)
        else:
            return self._get_fallback(provider)

    def delete_credential(self, provider: str) -> bool:
        """Remove an API key."""
        try:
            if self.keyring_available:
                keyring.delete_password(SERVICE_NAME, provider)
            else:
                self._delete_fallback(provider)
            return True
        except Exception:
            return False

    def list_configured_providers(self) -> list[dict]:
        """List all providers and their configuration status."""
        result = []
        for provider in self.PROVIDERS:
            key = self.get_credential(provider)
            result.append({
                'provider': provider,
                'configured': key is not None,
                'key_preview': f"{key[:8]}...{key[-4:]}" if key else None
            })
        return result

    def _validate_key(self, provider: str, api_key: str) -> dict:
        """Validate an API key by making a lightweight API call."""
        import httpx

        config = self.PROVIDERS[provider]
        headers = self._get_auth_headers(provider, api_key)

        try:
            # Use a lightweight endpoint (list models, not generate)
            response = httpx.get(
                config['test_url'],
                headers=headers,
                timeout=10.0
            )

            if response.status_code in (200, 201):
                return {'valid': True}
            elif response.status_code == 401:
                return {'valid': False, 'error': 'Invalid API key'}
            elif response.status_code == 403:
                return {'valid': False, 'error': 'API key lacks required permissions'}
            else:
                return {'valid': False, 'error': f'Unexpected response: {response.status_code}'}

        except httpx.TimeoutException:
            # Timeout might mean key is valid but slow - accept it
            return {'valid': True, 'warning': 'Could not fully validate (timeout)'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def _get_auth_headers(self, provider: str, api_key: str) -> dict:
        """Get provider-specific auth headers."""
        if provider == 'anthropic':
            return {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01'
            }
        elif provider in ('openai', 'deepseek', 'xai'):
            return {'Authorization': f'Bearer {api_key}'}
        elif provider == 'google':
            return {'x-goog-api-key': api_key}
        return {}

    # --- Fallback Encrypted Storage ---

    def _get_machine_key(self) -> bytes:
        """Derive encryption key from machine-specific data."""
        # Use a combination of machine identifiers
        machine_id = f"{platform.node()}-{os.getlogin()}-writers-factory"

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"writers-factory-salt",  # Fixed salt is OK here
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))

    def _store_fallback(self, provider: str, api_key: str):
        """Store in encrypted JSON file."""
        self.fallback_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing or create new
        data = self._load_fallback_data()
        data[provider] = api_key

        # Encrypt and save
        fernet = Fernet(self._get_machine_key())
        encrypted = fernet.encrypt(json.dumps(data).encode())
        self.fallback_path.write_bytes(encrypted)

    def _get_fallback(self, provider: str) -> str | None:
        """Get from encrypted JSON file."""
        data = self._load_fallback_data()
        return data.get(provider)

    def _delete_fallback(self, provider: str):
        """Delete from encrypted JSON file."""
        data = self._load_fallback_data()
        if provider in data:
            del data[provider]
            fernet = Fernet(self._get_machine_key())
            encrypted = fernet.encrypt(json.dumps(data).encode())
            self.fallback_path.write_bytes(encrypted)

    def _load_fallback_data(self) -> dict:
        """Load and decrypt fallback storage."""
        if not self.fallback_path.exists():
            return {}

        try:
            fernet = Fernet(self._get_machine_key())
            encrypted = self.fallback_path.read_bytes()
            decrypted = fernet.decrypt(encrypted)
            return json.loads(decrypted)
        except Exception:
            return {}
```

### 2. Tauri Integration (Desktop App)

For the Tauri desktop app, we can use the native OS keychain directly via Rust:

```rust
// src-tauri/src/credentials.rs
use tauri::command;
use keyring::Entry;

const SERVICE_NAME: &str = "writers-factory";

#[command]
pub fn store_api_key(provider: String, api_key: String) -> Result<(), String> {
    let entry = Entry::new(SERVICE_NAME, &provider)
        .map_err(|e| e.to_string())?;

    entry.set_password(&api_key)
        .map_err(|e| e.to_string())?;

    Ok(())
}

#[command]
pub fn get_api_key(provider: String) -> Result<Option<String>, String> {
    let entry = Entry::new(SERVICE_NAME, &provider)
        .map_err(|e| e.to_string())?;

    match entry.get_password() {
        Ok(password) => Ok(Some(password)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(e) => Err(e.to_string()),
    }
}

#[command]
pub fn delete_api_key(provider: String) -> Result<(), String> {
    let entry = Entry::new(SERVICE_NAME, &provider)
        .map_err(|e| e.to_string())?;

    entry.delete_password()
        .map_err(|e| e.to_string())?;

    Ok(())
}
```

---

## API Endpoints

```python
# In api.py

@app.get("/credentials/status")
async def credentials_status():
    """Get configuration status for all providers."""
    cred_service = CredentialService()
    return {
        "providers": cred_service.list_configured_providers(),
        "storage_backend": "keychain" if cred_service.keyring_available else "encrypted_file"
    }

@app.post("/credentials/{provider}")
async def store_credential(provider: str, request: CredentialRequest):
    """Store an API key securely."""
    cred_service = CredentialService()
    result = cred_service.store_credential(provider, request.api_key)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@app.delete("/credentials/{provider}")
async def delete_credential(provider: str):
    """Remove an API key."""
    cred_service = CredentialService()
    success = cred_service.delete_credential(provider)
    return {"success": success}

@app.post("/credentials/{provider}/validate")
async def validate_credential(provider: str, request: CredentialRequest):
    """Validate an API key without storing it."""
    cred_service = CredentialService()
    return cred_service._validate_key(provider, request.api_key)
```

---

## Frontend Settings Panel

```svelte
<!-- lib/components/SettingsPanel.svelte -->
<script>
    let providers = [];
    let selectedProvider = null;
    let apiKeyInput = '';
    let validating = false;
    let validationResult = null;

    async function loadProviders() {
        const res = await fetch('/api/credentials/status');
        const data = await res.json();
        providers = data.providers;
    }

    async function validateKey() {
        validating = true;
        const res = await fetch(`/api/credentials/${selectedProvider}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKeyInput })
        });
        validationResult = await res.json();
        validating = false;
    }

    async function saveKey() {
        const res = await fetch(`/api/credentials/${selectedProvider}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKeyInput })
        });

        if (res.ok) {
            apiKeyInput = '';
            validationResult = null;
            await loadProviders();
        }
    }
</script>

<div class="settings-panel">
    <h3>API Keys</h3>
    <p class="hint">Keys are stored securely in your system keychain</p>

    <div class="provider-list">
        {#each providers as provider}
            <div class="provider-row">
                <span class="provider-name">{provider.provider}</span>
                {#if provider.configured}
                    <span class="status configured">✓ {provider.key_preview}</span>
                    <button on:click={() => deleteKey(provider.provider)}>Remove</button>
                {:else}
                    <span class="status not-configured">Not configured</span>
                    <button on:click={() => selectedProvider = provider.provider}>Add</button>
                {/if}
            </div>
        {/each}
    </div>

    {#if selectedProvider}
        <div class="key-input">
            <h4>Configure {selectedProvider}</h4>
            <input
                type="password"
                bind:value={apiKeyInput}
                placeholder="Paste API key..."
            />
            <div class="actions">
                <button on:click={validateKey} disabled={validating}>
                    {validating ? 'Validating...' : 'Validate'}
                </button>
                <button on:click={saveKey} disabled={!validationResult?.valid}>
                    Save
                </button>
            </div>

            {#if validationResult}
                <div class="validation-result" class:valid={validationResult.valid}>
                    {validationResult.valid ? '✓ Valid key' : `✗ ${validationResult.error}`}
                </div>
            {/if}
        </div>
    {/if}
</div>
```

---

## Security Considerations

### What We Protect Against

| Threat | Mitigation |
|--------|------------|
| Plaintext key exposure | Keys in OS keychain or encrypted file |
| Config file in git | No plaintext config files; `.gitignore` enforced |
| Stolen encrypted file | Machine-derived key; useless on other machines |
| Invalid keys | Validation before storage prevents broken configs |
| Memory exposure | Keys not held in memory longer than needed |

### What We DON'T Protect Against

| Threat | Why |
|--------|-----|
| Root/admin access | OS keychain can be accessed by root |
| Memory forensics | Keys must exist in memory during API calls |
| Keylogger during input | Out of scope for app-level security |

---

## Migration from Existing credentials.json

For projects migrating from the old `credentials.json` approach:

```python
# backend/scripts/migrate_credentials.py

def migrate_from_json():
    """One-time migration from old credentials.json."""
    old_path = Path("backend/config/credentials.json")

    if not old_path.exists():
        print("No credentials.json found, skipping migration")
        return

    with open(old_path) as f:
        old_creds = json.load(f)

    cred_service = CredentialService()

    for provider, key in old_creds.items():
        if key:
            result = cred_service.store_credential(provider, key)
            if result['success']:
                print(f"✓ Migrated {provider}")
            else:
                print(f"✗ Failed {provider}: {result['error']}")

    # Backup and remove old file
    old_path.rename(old_path.with_suffix('.json.migrated'))
    print("\nOld credentials.json renamed to .migrated")
    print("Please verify keys work, then delete the .migrated file")
```

---

## Success Criteria

- [ ] API keys never stored in plaintext files
- [ ] OS keychain used when available (macOS Keychain, Windows Credential Manager)
- [ ] Graceful fallback to encrypted file when keychain unavailable
- [ ] Key validation before storage prevents broken configurations
- [ ] Settings UI allows add/edit/delete without touching files
- [ ] Migration path from old credentials.json
- [ ] Keys survive app updates (stored outside app directory)
