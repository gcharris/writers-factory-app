# Contributing to Writers Factory

Thank you for your interest in contributing to Writers Factory! This guide will help you get started with development, understand our code structure, and make meaningful contributions.

---

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Areas Needing Help](#areas-needing-help)

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Rust** (for Tauri) - [Install rustup](https://rustup.rs/)
- **Ollama** (for local AI) - [Install Ollama](https://ollama.ai/)
- **Git** for version control

### Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/writers-factory-app.git
cd writers-factory-app

# Add upstream remote
git remote add upstream https://github.com/gcharris/writers-factory-app.git
```

---

## 💻 Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Ollama model
ollama pull llama3.2

# Optional: Set up API keys for cloud features
cp .env.example .env
# Edit .env with your API keys
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Install Tauri CLI (if not already installed)
cargo install tauri-cli
```

### Running Development Servers

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run tauri dev  # Desktop app
# OR
npm run dev        # Browser (http://localhost:1420)
```

---

## 📁 Project Structure

```
writers-factory-app/
├── backend/                  # Python FastAPI backend
│   ├── agents/              # AI agent implementations
│   │   └── foreman.py       # The Foreman (Ollama-powered partner)
│   ├── services/            # Business logic services
│   │   ├── scene_analyzer_service.py     # 5-category scoring
│   │   ├── scaffold_generator_service.py  # 2-stage scaffolds
│   │   ├── scene_enhancement_service.py   # Enhancement pipeline
│   │   ├── voice_calibration_service.py   # Voice tournaments
│   │   ├── graph_health_service.py        # Structural validation
│   │   └── [13 more services...]
│   ├── models/              # Database models (SQLAlchemy)
│   ├── tests/               # pytest test suites
│   ├── api.py               # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   └── agents.yaml          # Agent configuration
├── frontend/                # SvelteKit + Tauri frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/  # Svelte components
│   │   │   │   ├── MainLayout.svelte      # 4-panel IDE layout
│   │   │   │   ├── ForemanChatPanel.svelte # Chat interface
│   │   │   │   ├── StudioPanel.svelte      # Mode-aware actions
│   │   │   │   ├── SettingsPanel.svelte    # Settings UI
│   │   │   │   └── [15+ more components]
│   │   │   ├── api_client.ts  # Backend API client
│   │   │   └── stores.js      # Svelte stores (state management)
│   │   ├── routes/          # SvelteKit routes
│   │   └── app.css          # Cyber-noir design system
│   ├── src-tauri/           # Tauri configuration
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
├── docs/                    # Documentation (58+ files)
│   ├── specs/               # Technical specifications
│   ├── dev_logs/            # Implementation logs
│   ├── claude-skills/       # Reference skills from Explants
│   ├── ARCHITECTURE.md      # System architecture
│   ├── guides/TESTING.md    # Testing guide
│   └── [50+ more docs]
└── README.md                # Project overview
```

---

## 🔄 Development Workflow

### 1. Create a Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# OR
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

**Backend Changes**:
- Add/modify services in `backend/services/`
- Add corresponding tests in `backend/tests/`
- Update API endpoints in `backend/api.py` if needed
- Run tests: `pytest tests/ -v`

**Frontend Changes**:
- Add/modify components in `frontend/src/lib/components/`
- Update stores in `frontend/src/lib/stores.js` if needed
- Follow Cyber-noir design system (see `frontend/src/app.css`)
- Test manually in browser/desktop app

### 3. Write Tests

**All new backend code must have tests**:
```bash
cd backend
pytest tests/test_your_new_service.py -v
```

See [TESTING.md](../guides/TESTING.md) for detailed testing guidelines.

### 4. Run Quality Checks

```bash
# Backend
cd backend
pytest tests/ -v                    # Run tests
python -m py_compile api.py         # Check syntax

# Frontend
cd frontend
npm run check                       # Type check
npm run build                       # Build check
```

### 5. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add scene analyzer anti-pattern detection

- Implement zero-tolerance pattern detection
- Add metaphor domain saturation analysis
- Add 15+ test cases for edge scenarios
- Update API_REFERENCE.md with new endpoints"
```

**Commit Message Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Fill out the PR template with:
# - Description of changes
# - Testing performed
# - Related issues
```

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# All backend tests
cd backend
pytest tests/ -v

# Specific test file
pytest tests/test_scene_analyzer_service.py -v

# With coverage
pytest tests/ --cov=backend/services --cov-report=html
```

### Writing Tests

**Structure**:
```python
"""Tests for ServiceName - Brief description"""

import pytest
from unittest.mock import AsyncMock, patch

# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def service_instance():
    """Create service instance for testing."""
    return ServiceName(project_id="test")

@pytest.fixture
def mock_data():
    """Create mock data."""
    return {...}

# =============================================================================
# Test Classes
# =============================================================================

class TestFeature:
    """Tests for specific feature."""

    @pytest.mark.asyncio
    async def test_scenario(self, service_instance, mock_data):
        """Test that scenario works correctly."""
        # Arrange
        # Act
        result = await service_instance.method(mock_data)
        # Assert
        assert result is not None
```

**See [TESTING.md](../guides/TESTING.md) for comprehensive testing documentation.**

---

## 📝 Code Style

### Python (Backend)

**Follow PEP 8**:
- 4-space indentation
- Max line length: 100 characters
- Use type hints where possible
- Docstrings for all public methods

**Example**:
```python
async def generate_scaffold(
    self,
    beat_info: BeatInfo,
    character_context: str,
    project_id: str,
) -> ScaffoldResult:
    """
    Generate scene scaffold from beat information.

    Args:
        beat_info: Beat information from Story Bible
        character_context: Character context string
        project_id: Project identifier

    Returns:
        ScaffoldResult with scaffold content and metadata

    Raises:
        ValueError: If beat_info is invalid
    """
    # Implementation
```

### TypeScript/JavaScript (Frontend)

**Style**:
- 2-space indentation
- Use TypeScript types
- Descriptive variable names
- Async/await for promises

**Example**:
```typescript
async function analyzeScene(
  sceneContent: string,
  voiceBundle: VoiceBundle
): Promise<SceneAnalysis> {
  const response = await fetch('/api/director/scene/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scene_content: sceneContent, voice_bundle: voiceBundle }),
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  return await response.json();
}
```

### Svelte Components

**Structure**:
```svelte
<script lang="ts">
  // Imports
  import { onMount } from 'svelte';

  // Props
  export let title: string;
  export let data: any[];

  // State
  let loading = false;

  // Functions
  async function loadData() {
    loading = true;
    // Load data
    loading = false;
  }

  // Lifecycle
  onMount(() => {
    loadData();
  });
</script>

<div class="container">
  <h2>{title}</h2>
  {#if loading}
    <p>Loading...</p>
  {:else}
    <!-- Content -->
  {/if}
</div>

<style>
  .container {
    /* Styles */
  }
</style>
```

---

## 🔍 Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated if needed
- [ ] Commit messages are descriptive
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- How was this tested?
- What tests were added?

## Related Issues
Fixes #123

## Screenshots (if applicable)
```

### Review Process

1. **Automated Checks**: Tests must pass
2. **Code Review**: At least one approval required
3. **Documentation Review**: Docs must be updated
4. **Merge**: Squash and merge to main

---

## 🎯 Areas Needing Help

### High Priority

**Backend Testing (Critical)**:
- 13 services still need tests (only 4 of 19 tested)
- Priority: SceneWriterService, StructureVariantService, SettingsService
- See [TESTING.md](../guides/TESTING.md) for test patterns

**Frontend UI Components (Phase 5)**:
- Track 3: ARCHITECT Mode UI (7 components)
- Track 3: VOICE_CALIBRATION Mode UI (6 components)
- Track 3: DIRECTOR Mode UI (16 components)
- See [UI_IMPLEMENTATION_PLAN_V2.md](../specs/UI_IMPLEMENTATION_PLAN_V2.md)

### Medium Priority

**Documentation**:
- User guides for completed features
- API endpoint examples
- Troubleshooting guides
- Video tutorials

**Bug Fixes**:
- Check [GitHub Issues](https://github.com/gcharris/writers-factory-app/issues)
- Look for "good first issue" label

### Low Priority

**Code Quality**:
- Refactoring for better maintainability
- Performance optimizations
- Security improvements

---

## 📚 Resources

### Documentation
- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture
- [TESTING.md](../guides/TESTING.md) - Testing guide
- [API_REFERENCE.md](../API_REFERENCE.md) - API endpoints
- [BACKEND_SERVICES.md](../BACKEND_SERVICES.md) - Service documentation
- [DOCS_INDEX.md](../DOCS_INDEX.md) - Complete documentation index

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SvelteKit Documentation](https://kit.svelte.dev/)
- [Tauri Documentation](https://tauri.app/)
- [pytest Documentation](https://docs.pytest.org/)

---

## 💬 Communication

- **Questions**: [GitHub Discussions](https://github.com/gcharris/writers-factory-app/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/gcharris/writers-factory-app/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/gcharris/writers-factory-app/issues)

---

## 📜 License

By contributing to Writers Factory, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Writers Factory! Every contribution, no matter how small, helps make this tool better for novelists everywhere.**
