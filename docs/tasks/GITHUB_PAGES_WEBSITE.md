# GitHub Pages Website Setup

**Created**: 2025-12-06
**Status**: Ready for implementation
**Priority**: High
**Assigned To**: Claude Code IDE Agent

---

## Overview

Set up GitHub Pages for the Writers Factory course website. The site serves two audiences:

1. **Pre-Course (Public)**: Prospective students and university administrators
2. **During-Course (Protected)**: Enrolled students needing workflow guidance

---

## Design System: Cyber-Noir Theme

Port the app's design tokens from `frontend/src/app.css` to GitHub Pages.

### Color Palette

```css
/* Backgrounds */
--bg-primary: #0f1419;      /* Page background */
--bg-secondary: #1a2027;    /* Card backgrounds */
--bg-tertiary: #242d38;     /* Elevated surfaces */
--bg-elevated: #2d3640;     /* Hover states */

/* Text */
--text-primary: #e6edf3;    /* Headings, body */
--text-secondary: #8b949e;  /* Descriptions */
--text-muted: #6e7681;      /* Hints, timestamps */

/* Accents */
--accent-gold: #d4a574;     /* Primary CTA, Director Mode */
--accent-cyan: #58a6ff;     /* Links, interactive */
--accent-purple: #a371f7;   /* Voice Mode */
--accent-blue: #2f81f7;     /* Architect Mode */

/* Semantic */
--success: #3fb950;
--warning: #d29922;
--error: #f85149;

/* Borders */
--border: #2d3a47;
--border-subtle: #21262d;
```

### Typography

```css
--font-ui: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
--font-prose: 'Merriweather', Georgia, serif;
```

### Mode Colors (for badges/labels)

| Mode | Color | Hex |
|------|-------|-----|
| ARCHITECT | Blue | #2f81f7 |
| VOICE | Purple | #a371f7 |
| DIRECTOR | Gold | #d4a574 |
| EDITOR | Green | #3fb950 |

---

## Site Structure

### Proposed Organization

```
docs/
├── _config.yml                    # Jekyll configuration
├── assets/
│   └── css/
│       └── style.scss             # Custom Cyber-Noir theme
│
├── index.md                       # Public landing page
├── about.md                       # "Amnesiac Genius" story (from philosophy.md)
├── tracks.md                      # Writer vs Architect comparison (NEW)
├── showcase.md                    # Student gallery (keep public)
├── faq.md                         # Prerequisites, format (NEW)
│
└── portal/                        # PASSWORD PROTECTED SECTION
    ├── index.md                   # Course hub (from student_portal.md)
    ├── schedule.md                # Day-by-day breakdown (extract from portal)
    ├── submit.md                  # Submission guide
    └── tools/                     # Reference documentation
        ├── models.md              # LLM models overview (from team.md)
        ├── journey.md             # Full writer's journey
        ├── context.md             # Context engineering
        ├── graphrag.md            # GraphRAG conceptual
        ├── graphrag-technical.md  # GraphRAG implementation
        ├── voice.md               # Voice calibration
        ├── director.md            # Director mode
        ├── integration.md         # Systems integration
        ├── agents.md              # Agent instructions
        └── anti-patterns.md       # Common mistakes
```

### File Mapping (Current → New)

| Current File | New Location | Action |
|--------------|--------------|--------|
| `index.md` | `index.md` | Rewrite as pure landing (no password form) |
| `philosophy.md` | `about.md` | Rename, may condense later |
| `team.md` | `portal/tools/models.md` | Move to protected |
| `journey.md` | `portal/tools/journey.md` | Move to protected |
| `student_portal.md` | `portal/index.md` | Move, keep password check |
| `showcase.md` | `showcase.md` | Keep as-is (public) |
| `submission_guide.md` | `portal/submit.md` | Move to protected |
| `context_engineering.md` | `portal/tools/context.md` | Move to protected |
| `graphrag.md` | `portal/tools/graphrag.md` | Move to protected |
| `graphrag_implementation.md` | `portal/tools/graphrag-technical.md` | Move to protected |
| `voice_calibration.md` | `portal/tools/voice.md` | Move to protected |
| `director_mode.md` | `portal/tools/director.md` | Move to protected |
| `systems_integration.md` | `portal/tools/integration.md` | Move to protected |
| `agent_instructions.md` | `portal/tools/agents.md` | Move to protected |
| `anti_patterns.md` | `portal/tools/anti-patterns.md` | Move to protected |

---

## Implementation Tasks

### Phase 1: Foundation

#### 1.1 Create `_config.yml`

```yaml
title: Writers Factory
description: AI and the One-Week Novel - Skoltech ISP 2026
baseurl: ""  # or "/writers-factory-app" if not using custom domain
url: "https://gcharris.github.io"

# Build settings
markdown: kramdown
theme: minima  # Base theme to override

# Exclude from processing
exclude:
  - tasks/
  - ARCHITECTURE.md
  - API_REFERENCE.md
  - BACKEND_SERVICES.md
  - COMPONENT_AUDIT.md
  - DESKTOP_BUNDLING.md
  - DOCS_INDEX.md
  - DOCS_INVENTORY.md
  - DOCS_REORGANIZATION_PLAN.md
  - TESTING_CHECKLIST.md
  - UNIVERSAL_AGENT_INSTRUCTION_ARCHITECTURE.md
  - WORKFLOWS.md
  - WORKSPACE_SETUP_IMPLEMENTATION.md
  - WRITERS_JOURNEY.md
  - WRITERS_JOURNEY_IMPLEMENTATION_PLAN.md
  - "*.log"

# Navigation
nav:
  - title: About
    url: /about
  - title: Tracks
    url: /tracks
  - title: Showcase
    url: /showcase
  - title: FAQ
    url: /faq
  - title: Student Portal
    url: /portal/
```

#### 1.2 Create `assets/css/style.scss`

Create SCSS file that imports minima and overrides with Cyber-Noir tokens.

```scss
---
---

@import "minima";

:root {
  /* Port all CSS variables from app.css */
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-ui);
}

/* Cards */
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 24px;
}

/* Buttons */
.btn-primary {
  background: linear-gradient(135deg, var(--accent-gold), var(--accent-gold-hover));
  color: var(--bg-primary);
  border: none;
  border-radius: 6px;
  padding: 12px 24px;
  font-weight: 600;
}

.btn-secondary {
  background: transparent;
  color: var(--accent-cyan);
  border: 1px solid var(--accent-cyan);
  border-radius: 6px;
  padding: 12px 24px;
}

/* Mode badges */
.badge-architect { background: var(--accent-blue-muted); color: var(--accent-blue); }
.badge-voice { background: var(--accent-purple-muted); color: var(--accent-purple); }
.badge-director { background: var(--accent-gold-muted); color: var(--accent-gold); }
.badge-editor { background: var(--success-muted); color: var(--success); }

/* Links */
a {
  color: var(--accent-cyan);
  text-decoration: none;
}
a:hover {
  color: var(--accent-cyan-hover);
  text-decoration: underline;
}

/* Code blocks */
pre, code {
  background: var(--bg-input);
  font-family: var(--font-mono);
  border-radius: 4px;
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid var(--border);
  padding: 12px;
  text-align: left;
}
th {
  background: var(--bg-tertiary);
}
```

### Phase 2: Create Missing Pages

#### 2.1 Create `tracks.md` (NEW)

```markdown
---
layout: default
title: Choose Your Track
---

# Two Tracks, One Goal

## The Writer Track
For novelists who want to focus on the creative output.

- Goal: Complete a 15k+ word novella
- Tools: Use the app as-is
- Technical: None required

[Download the App →]

## The Architect Track
For engineers who want to understand and improve the system.

- Goal: Optimize the Context Engine
- Tools: Modify prompts, graph logic, configs
- Technical: Read the specs, submit PRs

[View Source Code →]
```

#### 2.2 Create `faq.md` (NEW)

```markdown
---
layout: default
title: FAQ
---

# Frequently Asked Questions

## Prerequisites
- What background do I need?
- Do I need to know how to code?

## Format
- How intensive is the week?
- What's the daily schedule?

## Outcomes
- What will I produce?
- How is work evaluated?
```

### Phase 3: Reorganize Existing Content

1. Move files according to mapping table above
2. Update all internal links
3. Add `layout: default` frontmatter to all pages
4. Add password check script to all `/portal/` pages

### Phase 4: Update Navigation

1. Create `_includes/nav.html` for consistent navigation
2. Add breadcrumbs for `/portal/tools/` pages
3. Create sidebar for tools section

---

## Password Protection Approach

Since GitHub Pages is static, we use client-side JavaScript:

### On Public Pages (index, about, tracks, showcase, faq)
- No password check
- Include link to `/portal/` which has the login

### On Portal Landing (`/portal/index.md`)
- Password form (as in current index.md)
- On success: set `sessionStorage.setItem('authenticated', 'true')`
- Redirect to portal content

### On All Portal Sub-pages
- Check `sessionStorage.getItem('authenticated')`
- If not authenticated, redirect to `/portal/`

```javascript
<script>
if (!sessionStorage.getItem('authenticated')) {
    window.location.href = "{{ '/portal/' | relative_url }}";
}
</script>
```

**Note**: This is security through obscurity. Determined users can bypass. The real protection is that the **repo is private** and the **app download link** is only visible to authenticated users.

---

## Images Required

The following images are referenced and should exist:

| Image | Location | Status |
|-------|----------|--------|
| `writers_factory_hero.png` | `assets/images/` | Exists |
| `6-phases-journey.png` | `assets/images/` | Check |
| `phase-0-research.png` | `assets/images/` | Check |
| `phase-1-setup.png` | `assets/images/` | Check |
| `phase-2-architect.png` | `assets/images/` | Check |
| `phase-3-voice.png` | `assets/images/` | Check |
| `phase-4-director.png` | `assets/images/` | Check |
| `engineering-the-muse.png` | `assets/images/` | Check |

---

## Link Fixes Needed

After reorganization, update these broken link patterns:

| Current Pattern | Should Be |
|-----------------|-----------|
| `(tasks/DIRECTOR_MODE_UI)` | `(tasks/DIRECTOR_MODE_UI.md)` or external link |
| `(graphrag)` | `(graphrag.md)` or `/portal/tools/graphrag` |
| `(voice_calibration)` | `/portal/tools/voice` |
| `(director_mode)` | `/portal/tools/director` |

---

## Testing Checklist

- [ ] `_config.yml` created and valid
- [ ] Styles render correctly (dark theme)
- [ ] All public pages accessible without auth
- [ ] Portal pages redirect to login if not authenticated
- [ ] Password "skoltech2026" grants access
- [ ] All internal links work
- [ ] Images display correctly
- [ ] Mobile responsive

---

## Notes

- **Course Name**: Use "Skoltech ISP 2026" consistently
- **Dates**: TBD - don't include specific dates yet
- **Content Condensing**: Defer to after reorganization is complete
- **Password Value**: `skoltech2026` (currently visible in source - acceptable for now)

---

## Related Documentation

- [App Design System](../../frontend/src/app.css) - Source of truth for colors
- [Philosophy Content](../philosophy.md) - Main course concept
- [Student Portal](../student_portal.md) - Current portal page

---

*Task created: December 6, 2025*
*Created by: Claude Desktop (Cloud Agent)*
