# Desktop App Bundling Strategy

> How to bundle Writers Factory as a standalone desktop application.

## Architecture Overview

```
Writers Factory Desktop App
├── Tauri Shell (Rust)
│   ├── Frontend (SvelteKit) - bundled automatically
│   └── Sidecar: Python Backend - needs PyInstaller
└── External Dependency: Ollama (user-installed)
```

## Phase 1: PyInstaller Backend Bundle

### 1.1 Create PyInstaller Spec

Create `backend/writers-factory.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all prompt files
prompt_files = [
    ('prompts', 'prompts'),  # Include entire prompts directory
]

# Collect data files from dependencies
datas = prompt_files + [
    ('templates', 'templates'),  # Story structure templates
]

a = Analysis(
    ['api.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ] + collect_submodules('sqlalchemy'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='writers-factory-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### 1.2 Build Commands

```bash
# macOS (Universal Binary)
cd backend
pyinstaller --clean writers-factory.spec
# Output: dist/writers-factory-backend

# For Apple Silicon + Intel universal binary:
pyinstaller --target-arch universal2 writers-factory.spec
```

## Phase 2: Tauri Sidecar Configuration

### 2.1 Update tauri.conf.json

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "Writers Factory",
  "version": "0.1.0",
  "identifier": "com.writersfactory.app",
  "build": {
    "beforeDevCommand": "npm run dev",
    "devUrl": "http://localhost:1420",
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../build"
  },
  "app": {
    "windows": [
      {
        "title": "Writers Factory",
        "width": 1400,
        "height": 900,
        "minWidth": 1024,
        "minHeight": 700,
        "center": true,
        "resizable": true
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "externalBin": [
      "binaries/writers-factory-backend"
    ],
    "resources": [
      "resources/*"
    ],
    "macOS": {
      "entitlements": "Entitlements.plist",
      "infoPlist": "Info.plist",
      "minimumSystemVersion": "10.15"
    }
  },
  "plugins": {
    "shell": {
      "sidecar": true,
      "scope": [
        {
          "name": "binaries/writers-factory-backend",
          "sidecar": true,
          "args": true
        }
      ]
    }
  }
}
```

### 2.2 Directory Structure for Binaries

```
frontend/src-tauri/
├── binaries/
│   ├── writers-factory-backend-aarch64-apple-darwin    # Apple Silicon
│   ├── writers-factory-backend-x86_64-apple-darwin     # Intel Mac
│   ├── writers-factory-backend-x86_64-pc-windows-msvc.exe
│   └── writers-factory-backend-x86_64-unknown-linux-gnu
├── resources/
│   └── (any additional resources)
└── tauri.conf.json
```

### 2.3 Rust Code to Launch Sidecar

In `src-tauri/src/main.rs`:

```rust
use tauri::Manager;
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn start_backend(app: tauri::AppHandle) -> Result<(), String> {
    let sidecar = app
        .shell()
        .sidecar("writers-factory-backend")
        .map_err(|e| e.to_string())?
        .args(["--port", "8000"])
        .spawn()
        .map_err(|e| e.to_string())?;

    // Store the child process handle for cleanup
    app.manage(sidecar);

    Ok(())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Auto-start backend on app launch
            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                if let Err(e) = start_backend(handle).await {
                    eprintln!("Failed to start backend: {}", e);
                }
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![start_backend])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## Phase 3: First-Run Setup Flow

### 3.1 Ollama Detection

The app should check for Ollama on startup:

```typescript
// frontend/src/lib/startup.ts
export async function checkOllama(): Promise<{installed: boolean, running: boolean}> {
  try {
    const response = await fetch('http://localhost:11434/api/tags');
    return { installed: true, running: response.ok };
  } catch {
    // Check if ollama binary exists
    const { Command } = await import('@tauri-apps/plugin-shell');
    try {
      await new Command('ollama', ['--version']).execute();
      return { installed: true, running: false };
    } catch {
      return { installed: false, running: false };
    }
  }
}

export async function checkRequiredModels(): Promise<string[]> {
  const required = ['llama3.2:3b', 'mistral:7b'];
  const missing: string[] = [];

  try {
    const response = await fetch('http://localhost:11434/api/tags');
    const data = await response.json();
    const installed = data.models.map((m: any) => m.name);

    for (const model of required) {
      if (!installed.includes(model)) {
        missing.push(model);
      }
    }
  } catch {
    return required; // All missing if can't connect
  }

  return missing;
}
```

### 3.2 Setup Wizard Component

```svelte
<!-- frontend/src/lib/components/SetupWizard.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { checkOllama, checkRequiredModels } from '$lib/startup';

  let step = 0;
  let ollamaStatus = { installed: false, running: false };
  let missingModels: string[] = [];
  let installing = false;

  onMount(async () => {
    ollamaStatus = await checkOllama();
    if (ollamaStatus.running) {
      missingModels = await checkRequiredModels();
    }

    // Skip wizard if everything is ready
    if (ollamaStatus.running && missingModels.length === 0) {
      step = -1; // Skip
    }
  });

  async function installModel(model: string) {
    installing = true;
    const { Command } = await import('@tauri-apps/plugin-shell');
    await new Command('ollama', ['pull', model]).execute();
    missingModels = missingModels.filter(m => m !== model);
    installing = false;
  }
</script>
```

## Phase 4: Data Locations

### 4.1 App Data Paths

```typescript
// frontend/src/lib/paths.ts
import { appDataDir, appConfigDir } from '@tauri-apps/api/path';

export async function getDataPaths() {
  return {
    // User data (projects, settings)
    data: await appDataDir(),     // ~/Library/Application Support/com.writersfactory.app/

    // Configuration
    config: await appConfigDir(), // ~/Library/Application Support/com.writersfactory.app/

    // Database location
    database: `${await appDataDir()}/writers_factory.db`,

    // Knowledge graph
    knowledgeGraph: `${await appDataDir()}/knowledge_graph.json`,
  };
}
```

### 4.2 Backend Must Support Configurable Paths

Update `backend/api.py` to accept data directory as argument:

```python
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=8000)
parser.add_argument('--data-dir', type=str, default=None)
args = parser.parse_args()

if args.data_dir:
    os.environ['WF_DATA_DIR'] = args.data_dir
```

## Build Pipeline

### Complete Build Script

```bash
#!/bin/bash
# scripts/build-desktop.sh

set -e

echo "=== Building Writers Factory Desktop ==="

# 1. Build Python backend
echo "Building Python backend..."
cd backend
pip install pyinstaller
pyinstaller --clean writers-factory.spec

# 2. Copy binaries to Tauri
echo "Copying binaries..."
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    TARGET="aarch64-apple-darwin"
elif [ "$ARCH" = "x86_64" ]; then
    TARGET="x86_64-apple-darwin"
fi

mkdir -p ../frontend/src-tauri/binaries
cp dist/writers-factory-backend "../frontend/src-tauri/binaries/writers-factory-backend-$TARGET"

# 3. Build Tauri app
echo "Building Tauri app..."
cd ../frontend
npm run tauri build

echo "=== Build Complete ==="
echo "Output: frontend/src-tauri/target/release/bundle/"
```

## Distribution Checklist

- [ ] PyInstaller backend builds for all targets (macOS ARM64, macOS x64, Windows, Linux)
- [ ] Tauri sidecar configuration tested
- [ ] First-run wizard handles Ollama detection
- [ ] Data paths configurable via CLI args
- [ ] Code signing configured (macOS notarization, Windows signing)
- [ ] Auto-update mechanism (Tauri updater plugin)
- [ ] Crash reporting integration

## Known Limitations

1. **Ollama Still External**: Users must install Ollama separately. Consider:
   - Bundling Ollama (large binary, licensing considerations)
   - Providing download link in setup wizard
   - Supporting alternative local LLM backends

2. **Binary Size**: PyInstaller bundle can be large (~100-200MB). Mitigations:
   - Use `--onefile` with UPX compression
   - Exclude unused dependencies
   - Consider `Nuitka` for smaller Python binaries

3. **Startup Time**: First launch may be slow due to:
   - Extracting PyInstaller bundle
   - Ollama model loading
   - Database initialization
