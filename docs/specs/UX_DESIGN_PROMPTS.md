# Writers Factory - Comprehensive UI Design Prompts

**Generated for**: Figma AI / Gemini 3.0
**Context**: Desktop Application (Tauri + Svelte)
**Date**: November 25, 2025
**Version**: 2.0 - Aligned with UI_COMPONENT_INVENTORY.md

---

## Design System Foundation

### Visual Identity: "Cyber-Noir"
- **Primary Background**: `#0f1419` (Deep charcoal)
- **Secondary Background**: `#1a2027` (Panel backgrounds)
- **Tertiary Background**: `#242d38` (Cards, elevated surfaces)
- **Border Color**: `#2d3a47` (Subtle panel dividers)
- **Primary Text**: `#e6edf3` (High contrast white)
- **Secondary Text**: `#8b949e` (Muted descriptions)
- **Accent Gold**: `#d4a574` (Director Mode highlights, active states)
- **Accent Cyan**: `#58a6ff` (Links, interactive elements)
- **Success Green**: `#3fb950`
- **Warning Yellow**: `#d29922`
- **Error Red**: `#f85149`
- **Typography**:
  - UI: Inter or SF Pro (sans-serif)
  - Editor: IBM Plex Mono or JetBrains Mono (monospace)
  - Manuscript preview: Merriweather (serif, for reading comfort)

---

## Phase 1: Application Shell & 4-Panel Layout

### Prompt 1.0 – Global Style Guide & Design Tokens

**Role**: You are a Senior Design Systems Architect creating a comprehensive design system.

**Task**: Create a complete design token library and style guide for "Writers Factory," a professional desktop IDE for novelists.

**Deliverables**:

1. **Color Palette** (as specified above in Visual Identity)

2. **Typography Scale**:
   - `heading-xl`: 24px, 700 weight (Modal titles)
   - `heading-lg`: 18px, 600 weight (Panel headers)
   - `heading-md`: 14px, 600 weight (Card titles)
   - `body`: 14px, 400 weight (Default text)
   - `body-sm`: 12px, 400 weight (Metadata, timestamps)
   - `mono`: 13px, 400 weight (Code, file paths)

3. **Spacing Scale**: 4px base unit
   - `space-1`: 4px, `space-2`: 8px, `space-3`: 12px, `space-4`: 16px
   - `space-5`: 20px, `space-6`: 24px, `space-8`: 32px, `space-10`: 40px

4. **Border Radius**:
   - `radius-sm`: 4px (Buttons, inputs)
   - `radius-md`: 6px (Cards)
   - `radius-lg`: 8px (Modals)
   - `radius-full`: 9999px (Pills, badges)

5. **Elevation/Shadows**:
   - `shadow-sm`: Subtle card elevation
   - `shadow-md`: Dropdowns, popovers
   - `shadow-lg`: Modals, overlays

6. **Component States**:
   - Default, Hover (+5% brightness), Active (accent border), Disabled (50% opacity)
   - Focus: 2px accent ring with 2px offset

**Visual Tone**: Professional, dense but organized. Think VS Code meets Bloomberg Terminal with a literary soul.

---

### Prompt 1.1 – Main Application Shell (4-Panel IDE)

**Role**: You are a Lead Product Designer for professional creative software.

**Task**: Design the main application shell for "Writers Factory" showing the complete 4-panel IDE layout.

**Context**: This is a desktop application (1920×1080 minimum) for professional novelists. It must feel like a powerful IDE (VS Code, JetBrains) but optimized for prose writing and AI-assisted creation.

**CRITICAL**: The layout has **FOUR panels**, not three.

**Layout Specifications**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ MENU BAR                                                                │
│ File  Edit  Selection  View  AI  Go  Run  Terminal  Window  Help        │
├────────────┬─────────────────────────┬──────────────────┬───────────────┤
│            │                         │                  │               │
│  PANEL 1   │       PANEL 2           │     PANEL 3      │   PANEL 4     │
│  BINDER    │       CANVAS            │     FOREMAN      │   STUDIO      │
│            │                         │   ┌──────────┐   │               │
│  File      │   Monaco Editor         │   │  CHAT    │   │  Tool Cards   │
│  Tree      │   + Breadcrumbs         │   │  (top)   │   │  Grid         │
│            │                         │   ├──────────┤   │               │
│  240px     │   Flexible (min 500px)  │   │  GRAPH   │   │  280px        │
│  width     │                         │   │  (bottom)│   │  width        │
│            │                         │   └──────────┘   │               │
│            │                         │   320px width    │               │
├────────────┴─────────────────────────┴──────────────────┴───────────────┤
│ STATUS BAR                                                              │
│ Graph: 1,240 nodes │ Uncommitted: 3 │ Claude 3.5 │ DIRECTOR │ Ln 142    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Panel 1 - BINDER** (240px fixed width):
- Header: "BINDER" with collapse button (chevron)
- File tree showing:
  ```
  ▼ My Novel Project
    ▼ Story Bible
      ├─ Protagonist.md ✓
      ├─ BeatSheet.md ◐
      ├─ Theme.md □
      └─ WorldRules.md □
    ▼ Manuscript
      ▼ Act 1
        ├─ Chapter 1
        │  ├─ Scene 1.1.md
        │  └─ Scene 1.2.md
        └─ Chapter 2
    ▶ Characters
    ▶ Locations
  ```
- Status badges next to Story Bible files: ✓ (complete/green), ◐ (in-progress/yellow), □ (not started/gray)
- Right-click context menu items: "New File", "New Folder", "Rename", "Delete", "Ingest to Graph"

**Panel 2 - CANVAS** (flexible, minimum 500px):
- Breadcrumb navigation: `My Novel > Act 1 > Chapter 1 > Scene 1.1.md`
- Monaco editor area with:
  - Line numbers in gutter (muted color)
  - Sample dramatic prose visible
  - Serif font for manuscript text (Merriweather)
- Bottom bar: Word count "1,247 words" | "Last saved: 2 min ago"

**Panel 3 - FOREMAN** (320px fixed width, vertically split):
- **Top Section (60% height) - Chat**:
  - Header: "FOREMAN" + Mode badge showing "DIRECTOR" in gold
  - Work Order card:
    ```
    ┌────────────────────────────┐
    │ Current Task               │
    │ Draft Scene 2.1            │
    │ ████████░░ 75%            │
    │ 3 of 4 templates complete  │
    └────────────────────────────┘
    ```
  - Chat messages (alternating user/AI bubbles)
  - Input field with send button at bottom
- **Bottom Section (40% height) - Mini Graph**:
  - Header: "KNOWLEDGE GRAPH" + expand button
  - Force-directed graph preview (small nodes, simplified)
  - "3 conflicts" warning badge (red) if applicable

**Panel 4 - STUDIO** (280px fixed width):
- Header: "STUDIO" with collapse button
- 2-column card grid (2×4 layout):
  ```
  ┌─────────────┬─────────────┐
  │ Story Bible │ Voice       │
  │ ◐ 2/4      │ Tournament  │
  ├─────────────┼─────────────┤
  │ Scaffold    │ Scene       │
  │ Generator   │ Writer      │
  ├─────────────┼─────────────┤
  │ Enhancement │ Health      │
  │ Pipeline    │ ⚠ 2 issues │
  ├─────────────┼─────────────┤
  │ Metabolism  │ Settings    │
  │ 3 pending   │ ⚙          │
  └─────────────┴─────────────┘
  ```
- Each card: Icon, title, status indicator, hover state

**Menu Bar**:
- Standard menu items: File, Edit, Selection, View, AI, Go, Run, Terminal, Window, Help
- "AI" menu should show: "Model Orchestrator ▸" with checkmark next to "Balanced Tier"

**Status Bar** (32px height):
- Left: "Graph: 1,240 nodes • 3,891 edges"
- Center: "Uncommitted: 3" (yellow if >0)
- Right: "Claude 3.5 Sonnet" | "DIRECTOR" (gold badge) | "Ln 142, Col 8"

**Visual Tone**: Dark mode, professional, dense but organized. Cyber-noir aesthetic with slate grays and gold accents.

---

## Phase 2: Individual Panel Details

### Prompt 2.1 – Panel 1: BINDER (File Navigation)

**Role**: You are a UI Designer specializing in file management interfaces.

**Task**: Design the complete BINDER panel for file navigation.

**Context**: Writers navigate their novel's file structure here. The panel must show Story Bible templates with completion status.

**Component Specifications**:

1. **Panel Header** (40px):
   - "BINDER" label (heading-md, uppercase, letter-spacing: 0.5px)
   - Collapse chevron button (right side)
   - Subtle bottom border

2. **File Tree Container**:
   - Scrollable area with 8px padding
   - Tree indentation: 16px per level

3. **FileTreeNode** (each row 28px height):
   - Expand/collapse chevron (▶/▼) for folders
   - File type icon (16×16):
    - 📁 Folder (closed)
    - 📂 Folder (open)
    - 📄 Generic file
    - 📖 Story Bible template
    - 📝 Scene file
   - File/folder name (body text, truncate with ellipsis)
   - **Story Bible badges** (right-aligned):
    - ✓ Green circle: Complete
    - ◐ Yellow half-circle: In Progress
    - □ Gray square: Not Started
    - ❌ Red X: Invalid/Error
   - Hover: Background highlight (#242d38)
   - Selected: Accent left border (3px gold) + background

4. **FileContextMenu** (right-click popup):
   - Width: 200px
   - Items (each 32px height):
    - "New File" + icon
    - "New Folder" + icon
    - Separator line
    - "Rename" + keyboard hint (F2)
    - "Delete" + keyboard hint (⌫)
    - Separator line
    - "Ingest to Graph"
    - "Open in External Editor"
   - Hover state: Background highlight
   - Shadow: shadow-md

5. **Drag-Drop Indicators**:
   - Drag handle appears on hover (⠿ icon, left of item)
   - Drop target: Dashed border (2px accent color)
   - Invalid drop: Red dashed border

**Sample Content to Show**:
```
▼ Crimson Protocol (Project)
  ▼ Story Bible
    ├─ 📖 Protagonist.md ✓
    ├─ 📖 BeatSheet.md ◐
    ├─ 📖 Theme.md □
    └─ 📖 WorldRules.md □
  ▼ Manuscript
    ▼ Act 1 - Setup
      ▼ Chapter 1 - The Heist
        ├─ 📝 Scene 1.1 - Bank Vault.md
        └─ 📝 Scene 1.2 - Escape.md
      ▶ Chapter 2 - Aftermath
    ▶ Act 2 - Confrontation
    ▶ Act 3 - Resolution
  ▶ Characters
  ▶ Locations
  ▶ Research
```

---

### Prompt 2.2 – Panel 2: CANVAS (Editor)

**Role**: You are a UI Designer for text editors and writing tools.

**Task**: Design the complete CANVAS panel containing the manuscript editor.

**Context**: This is where writers spend most of their time. It must be clean, distraction-free, and support long writing sessions.

**Component Specifications**:

1. **BreadcrumbNav** (36px height):
   - Container with subtle bottom border
   - Path segments as clickable links:
     `Crimson Protocol` › `Act 1` › `Chapter 1` › `Scene 1.1 - Bank Vault.md`
   - Each segment: body-sm text, cyan on hover
   - Current segment: bold, non-clickable
   - Overflow: Show first + last segments with "..." in middle

2. **MonacoWrapper** (main editor area):
   - **Gutter** (48px width):
    - Line numbers (right-aligned, muted text color)
    - Folding indicators for markdown headers
    - Git diff indicators (green/red bars for changes)
   - **Editor Content**:
    - Font: Merriweather (serif) for prose, 16px, 1.7 line-height
    - Background: Slightly lighter than panel (#1a2027)
    - Selection: Accent color at 30% opacity
    - Current line: Subtle highlight
    - Cursor: Thin vertical bar (accent color)
   - **Minimap** (right edge, optional):
    - 80px width, shows document structure
    - Highlights current viewport

3. **Editor Footer** (28px height):
   - Left: Word count "1,247 words" | Character count "6,891 chars"
   - Center: "Modified" indicator (yellow dot if unsaved)
   - Right: "Saved 2 min ago" | "Markdown" language indicator

4. **Inline Actions** (floating toolbar on text selection):
   - Appears above selected text
   - Buttons: "Ask Foreman" | "Enhance" | "Define Character" | "Add to Graph"
   - Arrow pointing to selection
   - Dismisses on click outside

**Sample Prose to Display**:
```
# Scene 1.1 - The Bank Vault

The vault door groaned open, revealing three decades of
accumulated secrets. Mickey Bardot stepped inside, his
breath forming small clouds in the refrigerated air.

"Thirty seconds," Sarah's voice crackled through the earpiece.

He moved with practiced efficiency, fingers dancing across
safe deposit boxes until he found number 1247. The one
that had haunted his dreams for fifteen years.

Inside, a single photograph. A woman he'd tried to forget.
```

---

### Prompt 2.3 – Panel 3: FOREMAN (Chat + Knowledge Graph)

**Role**: You are a UI Designer specializing in AI chat interfaces and data visualization.

**Task**: Design the complete FOREMAN panel with its split-view layout (chat above, graph below).

**Context**: The Foreman is the AI assistant that guides writers through the creative process. The panel shows both the conversation and a live knowledge graph.

**Component Specifications**:

1. **Panel Header** (40px):
   - "FOREMAN" label
   - Mode indicator badge:
    - ARCHITECT (blue)
    - VOICE_CALIBRATION (purple)
    - DIRECTOR (gold)
    - EDITOR (green)
   - Settings gear icon (right)

2. **WorkOrderTracker** (100px, collapsible card):
   ```
   ┌────────────────────────────────────┐
   │ 📋 Current Work Order              │
   ├────────────────────────────────────┤
   │ Draft Scene 2.1 - The Confrontation│
   │                                    │
   │ ████████████░░░░ 75%               │
   │                                    │
   │ Templates: ✓✓✓◐ (3/4 complete)     │
   │ Missing: Theme.md                  │
   └────────────────────────────────────┘
   ```
   - Click to expand → shows template checklist

3. **ForemanChat** (expandable area):
   - **Message List** (scrollable):
    - User messages: Right-aligned, accent background bubble
    - Foreman messages: Left-aligned, secondary background bubble
    - Each message shows:
      - Avatar (user photo or Foreman icon)
      - Message text (markdown rendered)
      - Timestamp (body-sm, muted)
      - Copy button (appears on hover)
   - **Streaming indicator**: Three animated dots when Foreman is responding

4. **ForemanInput** (56px, bottom of chat):
   - Text input: "Ask the Foreman..." placeholder
   - Send button (arrow icon, accent color)
   - Attachment button (paperclip icon) for file context

5. **Draggable Split Handle**:
   - Horizontal bar between chat and graph
   - Cursor changes to resize cursor
   - Min heights: Chat 200px, Graph 150px

6. **LiveGraph** (bottom section):
   - **Header** (32px): "KNOWLEDGE GRAPH" + expand button + "3 conflicts" warning badge
   - **Graph Canvas**:
    - Force-directed layout with physics simulation
    - Node types with colors:
      - CHARACTER: Cyan circles
      - LOCATION: Magenta circles
      - THEME: Gold circles
      - PLOT_ITEM: Green circles
    - Node labels (truncated to 12 chars)
    - Edges as curved lines (gray, 1px)
    - Selected node: Enlarged, glowing border
   - **Mini Controls** (overlay, bottom-right):
    - Zoom in/out buttons
    - Fit to view button
    - Filter button → opens filter popover

7. **GraphConflictIndicator** (badge on graph header):
   - Red badge: "3 conflicts"
   - Click → opens GraphConflictResolver modal

**Sample Chat to Display**:
```
[Foreman]: I see you're working on Scene 2.1. Based on your
Beat Sheet, this scene should introduce the "Debate" beat
where Mickey questions whether to pursue the truth.

[User]: How should I show his internal conflict?

[Foreman]: Consider using his physical environment as a
mirror. The bank vault's cold, sterile interior could
reflect his emotional state. I notice from your Theme.md
that "truth vs. comfort" is central—perhaps he literally
chooses between two safe deposit boxes?

[User]: That's perfect. Can you draft an opening paragraph?

[Foreman]: ▪▪▪ (typing...)
```

---

### Prompt 2.4 – Panel 4: STUDIO (Tool Cards)

**Role**: You are a UI Designer for dashboard and card-based interfaces.

**Task**: Design the complete STUDIO panel showing the tool launcher cards.

**Context**: The Studio provides quick access to all major features. Each card launches a specific workflow modal.

**Component Specifications**:

1. **Panel Header** (40px):
   - "STUDIO" label
   - Collapse chevron (right)

2. **Card Grid Container**:
   - 2-column grid layout
   - Gap: 12px between cards
   - Padding: 12px
   - Scrollable if content exceeds panel height

3. **StudioCard** (each card ~100px height):
   - **Structure**:
     ```
     ┌──────────────────────┐
     │ 📖  Story Bible      │
     │                      │
     │ ◐ 2 of 4 templates   │
     │ complete             │
     │                      │
     │ [Continue →]         │
     └──────────────────────┘
     ```
   - Icon (24×24, top-left)
   - Title (heading-md)
   - Status line (body-sm, muted)
   - Action button or indicator (bottom)
   - **States**:
    - Default: Secondary background
    - Hover: Elevated (shadow-sm), slight brightness increase
    - Active: Accent border (left, 3px)
    - Disabled: 50% opacity, no hover effect
    - Warning: Yellow left border
    - Error: Red left border

4. **Card Inventory** (8 cards total):

   **Row 1**:
   - **StoryBibleCard**:
    - Icon: 📖
    - Title: "Story Bible"
    - Status: "◐ 2/4 templates" (shows completion)
    - Badge: Progress indicator

   - **VoiceTournamentCard**:
    - Icon: 🎭
    - Title: "Voice Tournament"
    - Status: "Ready to calibrate" or "Voice set: Noir-Lyrical"
    - Badge: None or checkmark if complete

   **Row 2**:
   - **ScaffoldCard**:
    - Icon: 🏗️
    - Title: "Scaffold Generator"
    - Status: "Create scene structure"
    - Badge: None

   - **SceneWriterCard**:
    - Icon: ✍️
    - Title: "Scene Writer"
    - Status: "Generate variants"
    - Badge: None

   **Row 3**:
   - **EnhancementCard**:
    - Icon: ✨
    - Title: "Enhancement"
    - Status: "Current: 78/100" (scene score)
    - Badge: Score color (green >85, yellow 70-85, red <70)

   - **HealthCheckCard**:
    - Icon: 🏥
    - Title: "Health Check"
    - Status: "Last: 2 hours ago"
    - Badge: "⚠ 2" (warning count, yellow) or "✓" (green if clean)

   **Row 4**:
   - **MetabolismCard**:
    - Icon: 🧠
    - Title: "Metabolism"
    - Status: "3 uncommitted events"
    - Badge: Yellow dot if pending

   - **SettingsCard**:
    - Icon: ⚙️
    - Title: "Settings"
    - Status: "Configure AI & scoring"
    - Badge: None

5. **Mode-Dependent Visibility**:
   - ARCHITECT mode: Story Bible card highlighted, others dimmed
   - VOICE_CALIBRATION: Voice Tournament highlighted
   - DIRECTOR: Scaffold, Scene Writer, Enhancement highlighted
   - EDITOR: All cards available equally

---

## Phase 3: Critical Modals

### Prompt 3.1 – Settings Modal (Complete)

**Role**: You are a UX Designer for complex configuration systems.

**Task**: Design the complete Settings modal with all 11 configuration categories.

**Context**: Power users need granular control over AI behavior, scoring weights, and API integrations. This is a **CRITICAL BLOCKER** - without API key configuration, no cloud features work.

**Modal Specifications**:
- Size: 900px × 650px (centered)
- Background overlay: Black at 60% opacity
- Border radius: radius-lg (8px)
- Shadow: shadow-lg

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️ Settings                                              [✕]   │
├─────────────────┬───────────────────────────────────────────────┤
│                 │                                               │
│  SIDEBAR        │           CONTENT AREA                        │
│  (200px)        │           (700px)                             │
│                 │                                               │
│  ▸ Agents ●     │   [Content for selected category]            │
│    Scoring      │                                               │
│    Voice        │                                               │
│    Metaphor     │                                               │
│    Anti-Patterns│                                               │
│    Enhancement  │                                               │
│    Foreman      │                                               │
│    Orchestrator │                                               │
│    Tournament   │                                               │
│    Health       │                                               │
│    Advanced     │                                               │
│                 │                                               │
├─────────────────┴───────────────────────────────────────────────┤
│                          [Reset to Defaults]  [Apply & Close]   │
└─────────────────────────────────────────────────────────────────┘
```

**Sidebar Navigation**:
- Each category as a row (36px height)
- Selected: Accent left border, bold text
- Hover: Background highlight
- Indicator dot (●) if category has validation errors

**Category 1: AGENTS (SettingsAgents.svelte)** - P0 CRITICAL:
```
┌─────────────────────────────────────────────────────────────────┐
│ API Keys & Agent Configuration                                  │
│                                                                 │
│ Configure your AI provider API keys. At least one key is       │
│ required for cloud features.                                    │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ OpenAI                                    [Test] ✓ Valid   │  │
│ │ [••••••••••••••••••sk-abc123]            [Show]           │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ Anthropic                                 [Test] ✓ Valid   │  │
│ │ [••••••••••••••••••sk-ant-xyz]           [Show]           │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ Google (Gemini)                          [Test] ⚠ Missing │  │
│ │ [Enter API key...]                       [Show]           │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ DeepSeek                                 [Test] ⚠ Missing │  │
│ │ [Enter API key...]                       [Show]           │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ + Show more providers (Mistral, XAI, Qwen, Kimi, Zhipu...)     │
│                                                                 │
│ ─────────────────────────────────────────────────────────────  │
│                                                                 │
│ Foreman Model                                                   │
│ [Claude 3.5 Sonnet                                    ▼]       │
│ The model used for the Foreman AI assistant                    │
│                                                                 │
│ Tournament Agents                                               │
│ Select which agents participate in variant tournaments:        │
│ [✓] Claude 3.5 Sonnet    [✓] GPT-4o                           │
│ [✓] DeepSeek R1          [ ] Gemini 2.0                       │
│ [ ] Mistral Large        [ ] Qwen                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Category 2: SCORING (SettingsScoring.svelte)**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Scoring Rubric Configuration                                    │
│                                                                 │
│ Preset: [Literary Fiction               ▼]                     │
│         (Thriller, Romance, Balanced, Custom)                  │
│                                                                 │
│ Rubric Weights (must sum to 100%)                              │
│                                                                 │
│ Voice Authenticity           ████████████░░░░░░ 30%  [slider]  │
│ How closely prose matches your calibrated voice                │
│                                                                 │
│ Character Consistency        ████████░░░░░░░░░░ 20%  [slider]  │
│ Adherence to defined character attributes                      │
│                                                                 │
│ Metaphor Discipline          ████████░░░░░░░░░░ 20%  [slider]  │
│ Domain variety and saturation limits                           │
│                                                                 │
│ Anti-Pattern Avoidance       ██████░░░░░░░░░░░░ 15%  [slider]  │
│ Avoiding purple prose, clichés, filter words                   │
│                                                                 │
│ Phase Appropriateness        ██████░░░░░░░░░░░░ 15%  [slider]  │
│ Style adaptation across story phases                           │
│                                                                 │
│ ─────────────────────────────────────────────────────────────  │
│                                           Total: 100% ✓        │
└─────────────────────────────────────────────────────────────────┘
```

**Category 3: VOICE (SettingsVoice.svelte)**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Voice Strictness Settings                                       │
│                                                                 │
│ Authenticity Level                                             │
│ [Medium                                            ▼]          │
│ Low: Allows more deviation from voice bundle                   │
│ Medium: Balanced flexibility                                   │
│ High: Strict adherence to calibrated voice                     │
│                                                                 │
│ Purpose Adherence                                              │
│ [Medium                                            ▼]          │
│ How strictly beats must serve narrative purpose                │
│                                                                 │
│ Fusion Tolerance                                               │
│ [Low                                               ▼]          │
│ Mixing of voice characteristics across scenes                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Category 4: METAPHOR (SettingsMetaphor.svelte)**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Metaphor Discipline Settings                                    │
│                                                                 │
│ Domain Saturation Limit                                        │
│ [══════════●═══════════] 35%                                   │
│ Maximum percentage of metaphors from a single domain           │
│                                                                 │
│ Primary Domain Allowance                                       │
│ [═══════●═════════════] 40%                                    │
│ How much the dominant domain can exceed others                 │
│                                                                 │
│ Simile Tolerance (per 1000 words)                             │
│ [═══●═════════════════] 3                                      │
│ Maximum similes allowed per thousand words                     │
│                                                                 │
│ Minimum Domain Diversity                                       │
│ [═══════●═════════════] 4                                      │
│ Minimum number of metaphor domains required                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Category 5: ANTI-PATTERNS (SettingsAntiPatterns.svelte)**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Anti-Pattern Management                                         │
│                                                                 │
│ System Patterns                                      [Edit]    │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ Pattern               │ Severity │ Enabled │              │  │
│ ├───────────────────────┼──────────┼─────────┤              │  │
│ │ Purple prose          │ Warning  │ [✓]     │              │  │
│ │ Filter words          │ Warning  │ [✓]     │              │  │
│ │ Said-bookisms         │ Error    │ [✓]     │              │  │
│ │ Passive voice (excess)│ Warning  │ [✓]     │              │  │
│ │ Adverb overuse        │ Warning  │ [ ]     │              │  │
│ │ Cliché detection      │ Warning  │ [✓]     │              │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ Custom Patterns                               [+ Add Pattern]  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ "suddenly"            │ Warning  │ [✓]     │ [Delete]     │  │
│ │ "very" adjective      │ Info     │ [✓]     │ [Delete]     │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Category 6: ENHANCEMENT (SettingsEnhancement.svelte)**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Enhancement Pipeline Settings                                   │
│                                                                 │
│ Auto-Enhancement Threshold                                     │
│ [═════════════════●════] 90                                    │
│ Scenes scoring above this skip enhancement                     │
│                                                                 │
│ Action Prompt Threshold                                        │
│ [═════════════●════════] 85                                    │
│ Scores 85-90 get targeted fix suggestions                      │
│                                                                 │
│ Six-Pass Enhancement Threshold                                 │
│ [═════════●════════════] 70                                    │
│ Scores 70-85 get full 6-pass enhancement                       │
│                                                                 │
│ Rewrite Threshold                                              │
│ [═════════●════════════] 70                                    │
│ Scores below this recommend full rewrite                       │
│                                                                 │
│ ─────────────────────────────────────────────────────────────  │
│                                                                 │
│ Enhancement Aggressiveness                                     │
│ [Balanced                                          ▼]          │
│ Conservative: Minimal changes, preserve author voice           │
│ Balanced: Moderate improvements                                │
│ Aggressive: Maximum enhancement, may alter style               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Category 7: FOREMAN (SettingsForeman.svelte)**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Foreman Behavior Settings                                       │
│                                                                 │
│ Proactiveness                                                  │
│ [Medium                                            ▼]          │
│ How often Foreman offers unsolicited suggestions               │
│                                                                 │
│ Challenge Intensity                                            │
│ [Medium                                            ▼]          │
│ How strongly Foreman pushes back on weak ideas                 │
│                                                                 │
│ Explanation Verbosity                                          │
│ [Detailed                                          ▼]          │
│ Length and depth of Foreman explanations                       │
│                                                                 │
│ Auto KB-Writes                                                 │
│ [✓] Automatically write to Knowledge Base                      │
│ When enabled, Foreman adds to KB without confirmation          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Category 8: ORCHESTRATOR (SettingsOrchestrator.svelte)**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Model Orchestrator                                              │
│                                                                 │
│ [✓] Enable Smart Model Selection                               │
│ Automatically chooses the best model for each task             │
│                                                                 │
│ Quality Tier                                                   │
│ ┌─────────────────┬─────────────────┬─────────────────┐        │
│ │    BUDGET       │    BALANCED     │    PREMIUM      │        │
│ │                 │   ◉ Selected    │                 │        │
│ │   ~$0.50/day    │   ~$2.00/day    │   ~$5.00/day    │        │
│ │                 │                 │                 │        │
│ │  DeepSeek R1    │  Claude Sonnet  │  Claude Opus    │        │
│ │  Gemini Flash   │  GPT-4o         │  GPT-4 Turbo    │        │
│ │                 │  DeepSeek R1    │  Gemini Ultra   │        │
│ │                 │                 │                 │        │
│ │  Good for       │  Best balance   │  Maximum        │        │
│ │  exploration    │  of cost &      │  quality for    │        │
│ │  & drafts       │  quality        │  final output   │        │
│ └─────────────────┴─────────────────┴─────────────────┘        │
│                                                                 │
│ Monthly Budget                                                  │
│ [$] [50.00                                         ]           │
│                                                                 │
│ Current Spend                                                   │
│ ████████░░░░░░░░░░░░ $18.47 / $50.00 (37%)                     │
│ ⚠️ Projected: $42.00 by month end                               │
│                                                                 │
│ [✓] Prefer Local Models When Available                         │
│ Use Ollama models for non-critical tasks                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Category 9: TOURNAMENT (SettingsTournament.svelte)** - Phase 4:
```
┌─────────────────────────────────────────────────────────────────┐
│ Multi-Model Tournament (Phase 4)                                │
│                                                                 │
│ [ ] Enable Multi-Model Tournaments                             │
│ Run multiple models in parallel for critical decisions         │
│                                                                 │
│ Tournament Tasks                                               │
│ Select which tasks trigger multi-model tournaments:            │
│ [ ] Scene Generation (most expensive)                          │
│ [ ] Voice Calibration                                          │
│ [ ] Enhancement Suggestions                                    │
│ [✓] Critical Plot Decisions                                    │
│                                                                 │
│ Models Per Tournament                                          │
│ [═════●═══════════════] 3                                      │
│ How many models compete (2-5)                                  │
│                                                                 │
│ Daily Tournament Limit                                         │
│ [═════════●═══════════] 5                                      │
│ Maximum tournaments per day to control costs                   │
│                                                                 │
│ ⚠️ Cost Warning                                                 │
│ With current settings, tournaments may add ~$3/day to costs    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Category 10: HEALTH (SettingsHealth.svelte)**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Health Check Settings                                           │
│                                                                 │
│ Health Check Model                                             │
│ [Claude 3.5 Sonnet                                    ▼]       │
│                                                                 │
│ ── Pacing Analysis ─────────────────────────────────────────   │
│                                                                 │
│ Plateau Detection Window (scenes)                              │
│ [═════════●═══════════] 5                                      │
│                                                                 │
│ Tension Variance Tolerance                                     │
│ [═══════●═════════════] 0.15                                   │
│                                                                 │
│ ── Structure Analysis ──────────────────────────────────────   │
│                                                                 │
│ Beat Deviation Tolerance                                       │
│ [═════════●═══════════] 10%                                    │
│ How far scenes can deviate from ideal beat positions           │
│                                                                 │
│ ── Character Analysis ──────────────────────────────────────   │
│                                                                 │
│ Minimum Flaw Mentions (per act)                                │
│ [═══════●═════════════] 3                                      │
│                                                                 │
│ Cast Appearance Threshold                                      │
│ [═════●═══════════════] 20%                                    │
│ Main characters must appear in at least this % of scenes       │
│                                                                 │
│ ── Theme Analysis ──────────────────────────────────────────   │
│                                                                 │
│ Symbol Recurrence Minimum                                      │
│ [═════●═══════════════] 5                                      │
│ Symbols should appear at least this many times                 │
│                                                                 │
│ Theme Resonance Score Threshold                                │
│ [═══════════●═════════] 7.0                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Category 11: ADVANCED (SettingsAdvanced.svelte)**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Advanced Settings                                               │
│                                                                 │
│ ⚠️ These settings are for advanced users. Incorrect values     │
│ may degrade performance.                                        │
│                                                                 │
│ Max Conversation History                                       │
│ [═════════════●═══════] 50 messages                            │
│ Messages retained in Foreman context window                    │
│                                                                 │
│ KB Context Limit                                               │
│ [═════════●═══════════] 8000 tokens                            │
│ Maximum Knowledge Base context per request                     │
│                                                                 │
│ Voice Bundle Injection                                         │
│ [Always                                            ▼]          │
│ When to include voice bundle in prompts                        │
│ (Always / Scene Generation Only / On Request)                  │
│                                                                 │
│ RAG Strategy                                                   │
│ [Hybrid                                            ▼]          │
│ How Knowledge Base retrieval works                             │
│ (Vector / Keyword / Hybrid)                                    │
│                                                                 │
│ File Watcher Mode                                              │
│ [Immediate                                         ▼]          │
│ How quickly file changes trigger graph updates                 │
│ (Immediate / 5s Polling / Manual Only)                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Shared Components** (used across all categories):

1. **SettingSlider**: Label, value display, range slider, tooltip icon
2. **SettingDropdown**: Label, select dropdown, help text
3. **SettingToggle**: Label, toggle switch, description
4. **SettingSecret**: Masked input, show/hide button, test button, status indicator

---

### Prompt 3.2 – Story Bible Wizard (ARCHITECT Mode)

**Role**: You are a UX Designer for wizard-style onboarding flows.

**Task**: Design the complete Story Bible Wizard modal for ARCHITECT mode.

**Context**: Writers create their foundational story documents here. The wizard guides them through 4 templates: Protagonist, Beat Sheet, Theme, and World Rules. The Foreman AI assists in real-time.

**Modal Specifications**:
- Size: 1000px × 700px (centered)
- Full-screen option available

**Layout**:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ 📖 Story Bible Architect                              [⛶ Expand] [✕]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Progress: ████████░░░░░░░░ 2 of 4 Complete                            │
│                                                                         │
│  ┌──────────┬──────────┬──────────┬──────────┐                         │
│  │ ✓        │ ◉        │ ○        │ ○        │                         │
│  │Protagonist│Beat Sheet│  Theme   │World Rules│                        │
│  │ Complete │ Active   │ Pending  │ Pending  │                         │
│  └──────────┴──────────┴──────────┴──────────┘                         │
│                                                                         │
├────────────────────────────────┬────────────────────────────────────────┤
│                                │                                        │
│    ARCHITECT ASSISTANT         │         LIVE DOCUMENT PREVIEW          │
│         (450px)                │              (550px)                   │
│                                │                                        │
│  ┌──────────────────────────┐  │  ┌──────────────────────────────────┐ │
│  │ 🤖 Architect Mode        │  │  │ # Beat Sheet                     │ │
│  │                          │  │  │                                  │ │
│  │ Let's define your story's│  │  │ ## The 15-Beat Structure         │ │
│  │ beat sheet using the     │  │  │                                  │ │
│  │ Save the Cat! structure. │  │  │ 1. **Opening Image** (1%)        │ │
│  │                          │  │  │    _A glimpse of Mickey's        │ │
│  │ I see from your          │  │  │    mundane life before the       │ │
│  │ Protagonist.md that      │  │  │    heist changes everything._    │ │
│  │ Mickey's flaw is         │  │  │                                  │ │
│  │ "obsessive loyalty."     │  │  │ 2. **Theme Stated** (5%)         │ │
│  │                          │  │  │    _"Some secrets are better     │ │
│  │ What event forces him    │  │  │    left buried."_                │ │
│  │ to confront this flaw?   │  │  │                                  │ │
│  │ This will be your        │  │  │ 3. **Setup** (1-10%)             │ │
│  │ "All Is Lost" moment.    │  │  │    [To be defined...]            │ │
│  │                          │  │  │                                  │ │
│  └──────────────────────────┘  │  │ 4. **Catalyst** (12%)            │ │
│                                │  │    [To be defined...]            │ │
│  ┌──────────────────────────┐  │  │                                  │ │
│  │ [Your response here...]  │  │  │ ...                              │ │
│  │                     [→]  │  │  │                                  │ │
│  └──────────────────────────┘  │  └──────────────────────────────────┘ │
│                                │                                        │
│  ┌──────────────────────────┐  │  [Edit Directly] [Save Progress]      │
│  │ 📚 Reference: World NB   │  │                                        │
│  │ "Psychology of loyalty   │  │                                        │
│  │ in high-stakes..."       │  │                                        │
│  └──────────────────────────┘  │                                        │
│                                │                                        │
├────────────────────────────────┴────────────────────────────────────────┤
│                                                                         │
│  NotebookLM Sources: [World ✓] [Voice ✓] [Craft ○]    [Configure →]   │
│                                                                         │
│  [← Previous Template]                    [Skip to Next] [Complete →]  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Component Specifications**:

1. **Progress Tracker** (top):
   - 4 step indicators (circle + label)
   - States: ✓ Complete (green), ◉ Active (gold), ○ Pending (gray)
   - Progress bar spanning all steps

2. **Template Steps**:
   - **Protagonist.md**: Name, Fatal Flaw, The Lie They Believe, Arc Summary
   - **BeatSheet.md**: 15 beats with percentages and descriptions
   - **Theme.md**: Central Theme, Theme Statement, Symbol Seeds
   - **WorldRules.md**: Genre conventions, physics, magic systems

3. **Left Panel - Architect Assistant**:
   - Mode badge: "🤖 Architect Mode"
   - Chat-style interface (scrollable)
   - Foreman asks guiding questions
   - References pulled from NotebookLM (collapsible drawer)
   - Input field at bottom

4. **Right Panel - Live Document**:
   - Real-time markdown preview
   - Updates as user provides answers
   - Syntax highlighting for headings
   - "Edit Directly" button → switches to edit mode
   - "Save Progress" button

5. **NotebookLM Integration** (bottom bar):
   - Connected notebooks: World, Voice, Craft
   - Status indicators (✓ connected, ○ not configured)
   - "Configure" link → opens NotebookLM settings

6. **Navigation Buttons**:
   - "Previous Template" / "Next Template"
   - "Skip" (with confirmation)
   - "Complete" (only when all fields filled)

**Visual Tone**: Warmer than main IDE. Sepia/parchment hints for "planning/foundation" feel. Still professional but more inviting.

---

### Prompt 3.3 – Voice Calibration Tournament (25-Variant Grid)

**Role**: You are a UI Designer specializing in comparison and selection interfaces.

**Task**: Design the Voice Calibration Tournament showing a 5×5 grid of 25 variants.

**Context**: The system generates 25 text variants (5 AI agents × 5 writing strategies) of the same sample passage. The writer compares them to select their novel's voice.

**CRITICAL**: This is a **25-variant grid** (5×5), NOT a 5-variant display.

**Modal Specifications**:
- Size: Full screen (or 1400px × 900px minimum)
- Scrollable grid area

**Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🎭 Voice Calibration Tournament                          [Compare] [✕]     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Round 1 of 3: Initial Selection    ████████░░░░░░░░ 25 variants           │
│                                                                             │
│  Filter: [All Agents ▼] [All Strategies ▼]  Sort: [Score ▼]  [Grid │ List] │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│           │ Action    │ Atmospheric │ Minimalist │ Dialogue  │ Literary   │
│           │ Focus     │             │            │ Heavy     │            │
│  ─────────┼───────────┼─────────────┼────────────┼───────────┼────────────│
│           │           │             │            │           │            │
│  Claude   │ [Card 1]  │  [Card 2]   │  [Card 3]  │ [Card 4]  │  [Card 5]  │
│  3.5      │   87/100  │    82/100   │   79/100   │   84/100  │   91/100 ★ │
│           │           │             │            │           │            │
│  ─────────┼───────────┼─────────────┼────────────┼───────────┼────────────│
│           │           │             │            │           │            │
│  GPT-4o   │ [Card 6]  │  [Card 7]   │  [Card 8]  │ [Card 9]  │  [Card 10] │
│           │   85/100  │    88/100 ★ │   76/100   │   81/100  │   83/100   │
│           │           │             │            │           │            │
│  ─────────┼───────────┼─────────────┼────────────┼───────────┼────────────│
│           │           │             │            │           │            │
│  DeepSeek │ [Card 11] │  [Card 12]  │  [Card 13] │ [Card 14] │  [Card 15] │
│  R1       │   78/100  │    80/100   │   85/100 ★ │   77/100  │   79/100   │
│           │           │             │            │           │            │
│  ─────────┼───────────┼─────────────┼────────────┼───────────┼────────────│
│           │           │             │            │           │            │
│  Gemini   │ [Card 16] │  [Card 17]  │  [Card 18] │ [Card 19] │  [Card 20] │
│  2.0      │   82/100  │    79/100   │   74/100   │   86/100 ★│   81/100   │
│           │           │             │            │           │            │
│  ─────────┼───────────┼─────────────┼────────────┼───────────┼────────────│
│           │           │             │            │           │            │
│  Mistral  │ [Card 21] │  [Card 22]  │  [Card 23] │ [Card 24] │  [Card 25] │
│  Large    │   80/100  │    77/100   │   82/100   │   79/100  │   84/100   │
│           │           │             │            │           │            │
│  ─────────┴───────────┴─────────────┴────────────┴───────────┴────────────│
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Selected: Claude 3.5 + Literary (91/100)                                   │
│                                                                             │
│  [Add to Comparison (3 max)]  [View Full Text]  [Select as Winner →]       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**VoiceVariantCard** (each cell in grid):
```
┌─────────────────────────────┐
│ Claude + Literary    91 ★   │
├─────────────────────────────┤
│                             │
│ "The vault door groaned     │
│ open, its ancient hinges    │
│ protesting the intrusion    │
│ like a grandmother          │
│ disturbed from sleep..."    │
│                             │
│ [Preview: 150 words]        │
│                             │
├─────────────────────────────┤
│ [◉ Select] [Compare] [Full] │
└─────────────────────────────┘
```

**Card Specifications**:
- Size: ~220px × 180px
- Header: Agent name + Strategy badge
- Score: Color-coded (green >85, yellow 70-85, red <70)
- Star (★) indicates top score in row/column
- Preview: First 150 words, truncated with ellipsis
- Hover: Elevation increase, border highlight
- Selected: Gold border (3px), checkmark overlay

**Comparison Mode** (side-by-side):
```
┌──────────────────────────────────────────────────────────────────────────┐
│ Comparing 3 Variants                                           [✕ Close]│
├──────────────────────┬──────────────────────┬────────────────────────────┤
│                      │                      │                            │
│ Claude + Literary    │ GPT-4o + Atmospheric │ DeepSeek + Minimalist      │
│ 91/100 ★             │ 88/100               │ 85/100                     │
│                      │                      │                            │
│ "The vault door      │ "Cold air spilled    │ "The vault opened.         │
│ groaned open, its    │ from the vault like  │ Mickey stepped inside.     │
│ ancient hinges       │ the breath of        │ Thirty seconds."           │
│ protesting the       │ something long       │                            │
│ intrusion like a     │ forgotten, carrying  │ [Full text ~800 words...]  │
│ grandmother          │ with it the weight   │                            │
│ disturbed from       │ of secrets           │                            │
│ sleep. Mickey        │ accumulated over     │                            │
│ stepped across the   │ decades..."          │                            │
│ threshold..."        │                      │                            │
│                      │                      │                            │
│ [Full text...]       │ [Full text...]       │                            │
│                      │                      │                            │
├──────────────────────┴──────────────────────┴────────────────────────────┤
│                                                                          │
│ Voice: ███░░ 85   Voice: ████░ 90   Voice: ██░░░ 70                      │
│ Char:  ████░ 92   Char:  ███░░ 82   Char:  ████░ 95                      │
│ Meta:  ████░ 88   Meta:  ████░ 88   Meta:  █████ 100                     │
│                                                                          │
│            [Select This Winner]  [Select This]  [Select This]            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Winner Selection Modal**:
```
┌────────────────────────────────────────────────────────────┐
│ 🏆 Confirm Voice Selection                                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ You've selected:                                           │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Claude 3.5 Sonnet + Literary Strategy                  │ │
│ │ Score: 91/100                                          │ │
│ │                                                        │ │
│ │ "The vault door groaned open..."                       │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ Additional References (optional):                          │
│ [ ] Include GPT-4o + Atmospheric as anti-pattern          │
│ [ ] Include DeepSeek + Minimalist as alternate voice      │
│                                                            │
│ This will generate your Voice Reference Bundle with:       │
│ • Gold Standard example                                    │
│ • Style characteristics                                    │
│ • Anti-patterns to avoid                                   │
│ • Phase evolution guidance                                 │
│                                                            │
│         [Cancel]           [Generate Voice Bundle →]       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

### Prompt 3.4 – Director Mode: Scaffold Generator

**Role**: You are a UX Designer for multi-step creative workflows.

**Task**: Design the 2-stage Scaffold Generator for Director Mode.

**Context**: Before writing a scene, writers create a "scaffold" - a detailed outline. Stage 1 provides a draft summary with enrichment suggestions. Stage 2 shows the full scaffold after optional enrichment from NotebookLM.

**Modal Specifications**:
- Size: 900px × 700px

**Stage 1 Layout**:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🏗️ Scaffold Generator - Stage 1: Draft Summary                   [✕]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Creating scaffold for: Scene 2.1 - The Confrontation                   │
│  Beat: "Debate" (15-25% of story)                                       │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DRAFT SUMMARY                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  Mickey confronts Sarah about her involvement with The State.           │
│  Their confrontation takes place in the abandoned warehouse where       │
│  they used to meet as children. The scene should establish:             │
│                                                                         │
│  • Mickey's internal conflict (loyalty vs. truth)                       │
│  • Sarah's hidden motivations                                           │
│  • The photograph as a symbolic bridge between past and present         │
│                                                                         │
│  Suggested word count: 2,500-3,000 words                                │
│  Tone: Tense, nostalgic undertones                                      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ENRICHMENT SUGGESTIONS                                                 │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  The AI suggests querying your notebooks for additional context:        │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ 📚 World Notebook                                    [Query →]    │ │
│  │ "What are the visual details of abandoned warehouses in 1990s     │ │
│  │ Detroit? Focus on sensory details: sounds, smells, lighting."     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ 📚 Psychology Notebook                               [Query →]    │ │
│  │ "How do siblings with trauma histories communicate during         │ │
│  │ high-stakes confrontations? Non-verbal cues and deflection."     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ 📚 Voice Notebook                                    [Query →]    │ │
│  │ "Examples of literary confrontation scenes with nostalgic         │ │
│  │ undertones. Reference: Donna Tartt, Dennis Lehane."              │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  [Skip Enrichment →]                                                    │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Enrichment Progress: 0 of 3 queries completed                          │
│                                                                         │
│  [Cancel]                               [Generate Full Scaffold →]      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Enrichment Query Modal** (popup when clicking Query):
```
┌────────────────────────────────────────────────────────────┐
│ Query World Notebook                                  [✕]  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ What are the visual details of abandoned warehouses    │ │
│ │ in 1990s Detroit? Focus on sensory details...          │ │
│ │                                              [Edit]    │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ [Send Query]                                               │
│                                                            │
│ ─────────────────────────────────────────────────────────  │
│                                                            │
│ Response:                                                  │
│                                                            │
│ "Abandoned warehouses in 1990s Detroit featured exposed   │
│ brick walls with peeling paint in industrial greens and   │
│ browns. Broken skylights allowed shafts of dusty light    │
│ to cut through the darkness. The smell of rust, old       │
│ machinery oil, and something organic—mold or rot—would    │
│ permeate everything. Sound would echo dramatically:       │
│ footsteps on concrete, dripping water, distant traffic    │
│ filtered through broken windows..."                        │
│                                                            │
│                   [Add to Scaffold]  [Discard]             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Stage 2 Layout** (after enrichment):
```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🏗️ Scaffold Generator - Stage 2: Full Scaffold                   [✕]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Scene 2.1 - The Confrontation                                          │
│  ████████████████ Scaffold Complete                                     │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  # Scene 2.1: The Confrontation                                         │
│                                                                         │
│  ## Setup                                                               │
│  Mickey arrives at the abandoned Packard plant warehouse at dusk.       │
│  The space is cavernous—exposed brick, broken skylights casting         │
│  orange light, the smell of rust and old machinery oil.                 │
│                                                                         │
│  ## Opening Hook                                                        │
│  He finds Sarah already there, standing where they used to play         │
│  as children. She's holding the same photograph he discovered           │
│  in the safe deposit box.                                               │
│                                                                         │
│  ## Rising Action                                                       │
│  - Mickey demands to know how she got the photo                         │
│  - Sarah deflects with childhood memories (sibling trauma pattern)      │
│  - Physical staging: they circle each other, maintaining distance       │
│  - Mickey's internal conflict surfaces (Voice Bundle: show don't tell)  │
│                                                                         │
│  ## Climax Beat                                                         │
│  Sarah reveals she's been working with The State to protect him.        │
│  "Some secrets are better left buried"—Theme Statement echo.            │
│                                                                         │
│  ## Resolution Hook                                                     │
│  Mickey must choose: accept her protection or pursue the truth.         │
│  He walks away without answering—setting up the Midpoint.              │
│                                                                         │
│  ## Technical Notes                                                     │
│  - Word target: 2,500-3,000                                             │
│  - POV: Mickey (close third)                                            │
│  - Tone: Tense, nostalgic undertones                                    │
│  - Sensory anchors: rust smell, orange light, echo of voices            │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STRUCTURE OPTIONS                                                      │
│  Select how the scene should open:                                      │
│                                                                         │
│  ○ Action Opening - Mickey is already mid-argument when scene starts   │
│  ◉ Atmospheric Opening - Establish warehouse mood before dialogue       │
│  ○ Dialogue Hook - Open with Sarah's provocative line                   │
│  ○ Internal Opening - Begin in Mickey's head as he approaches           │
│  ○ Flashback Frame - Start with childhood memory, transition to now     │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [← Back to Enrichment]  [Edit Scaffold]  [Generate Scene Variants →]  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Prompt 3.5 – Director Mode: Scene Variant Tournament

**Role**: You are a UI Designer for creative selection and comparison tools.

**Task**: Design the Scene Variant Tournament showing 15 generated scene variants.

**Context**: After the scaffold is created, the system generates 15 full scene drafts (3 models × 5 strategies). Writers compare, score, and select the best—or create a hybrid.

**Modal Specifications**:
- Size: Full screen recommended

**Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✍️ Scene Variant Tournament                                          [✕]  │
│                                                                             │
│ Scene 2.1: The Confrontation    15 variants generated                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Filter: [All Models ▼] [All Strategies ▼]   Sort: [Score ▼]   View: [Grid] │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 🥇 TOP VARIANT: Claude + Literary                          92/100   │   │
│  │                                                                     │   │
│  │ "The Packard plant warehouse held its breath as Mickey stepped      │   │
│  │ across the threshold. Three decades of Detroit's decline had        │   │
│  │ transformed the space into something holy—a cathedral of rust       │   │
│  │ and broken promises where he and Sarah had once played..."          │   │
│  │                                                                     │   │
│  │ [Read Full Scene (2,847 words)]  [Score Breakdown]  [Select →]     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┬──────────┐  │
│  │ Claude       │ Claude       │ Claude       │ Claude       │ Claude   │  │
│  │ Action  87   │ Atmos   85   │ Minimal 81   │ Dialog  84   │ Liter 92★│  │
│  │              │              │              │              │          │  │
│  │ "Mickey's    │ "Rust and    │ "She was     │ "'You came.' │ [TOP]    │  │
│  │ fist         │ silence.     │ there.       │ Sarah's      │          │  │
│  │ connected    │ The old      │ Waiting.     │ voice        │          │  │
│  │ with the     │ plant..."    │ Like she     │ echoed..."   │          │  │
│  │ wall..."     │              │ knew."       │              │          │  │
│  │              │              │              │              │          │  │
│  │ [Select]     │ [Select]     │ [Select]     │ [Select]     │ [Select] │  │
│  ├──────────────┼──────────────┼──────────────┼──────────────┼──────────┤  │
│  │ GPT-4o       │ GPT-4o       │ GPT-4o       │ GPT-4o       │ GPT-4o   │  │
│  │ Action  84   │ Atmos   88 ★ │ Minimal 79   │ Dialog  86   │ Liter 83 │  │
│  │              │              │              │              │          │  │
│  │ "The door    │ "Evening     │ "Warehouse.  │ "'Fifteen    │ "Memory  │  │
│  │ screamed     │ light        │ Sarah.       │ years,'      │ is a     │  │
│  │ as he        │ filtered     │ Silence."    │ she said..." │ ghost..."│  │
│  │ kicked..."   │ through..."  │              │              │          │  │
│  │              │              │              │              │          │  │
│  │ [Select]     │ [Select]     │ [Select]     │ [Select]     │ [Select] │  │
│  ├──────────────┼──────────────┼──────────────┼──────────────┼──────────┤  │
│  │ DeepSeek     │ DeepSeek     │ DeepSeek     │ DeepSeek     │ DeepSeek │  │
│  │ Action  80   │ Atmos   82   │ Minimal 85 ★ │ Dialog  78   │ Liter 81 │  │
│  │              │              │              │              │          │  │
│  │ [Preview...] │ [Preview...] │ [Preview...] │ [Preview...] │ [Prev...]│  │
│  │              │              │              │              │          │  │
│  │ [Select]     │ [Select]     │ [Select]     │ [Select]     │ [Select] │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┴──────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Selected for Comparison: Claude + Literary (92), GPT-4o + Atmos (88)       │
│                                                                             │
│  [Compare Selected (2)]  [Create Hybrid from Selected]  [Select Winner →]   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Score Breakdown Modal**:
```
┌────────────────────────────────────────────────────────────────────────┐
│ Score Breakdown: Claude + Literary                              [✕]   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                        OVERALL: 92/100 (A)                             │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  Voice Authenticity        ████████████████████░░░░  85%  (30)  │ │
│  │  Matches calibrated voice well. Minor drift in middle section.  │ │
│  │                                                                  │ │
│  │  Character Consistency     █████████████████████████  98%  (20) │ │
│  │  Mickey's flaw visible throughout. Sarah authentic.             │ │
│  │                                                                  │ │
│  │  Metaphor Discipline       ████████████████████░░░░  88%  (20)  │ │
│  │  4 domains used. Industrial primary (32%). No saturation.       │ │
│  │                                                                  │ │
│  │  Anti-Pattern Avoidance    █████████████████████████  95%  (15) │ │
│  │  1 filter word detected. No purple prose.                       │ │
│  │                                                                  │ │
│  │  Phase Appropriateness     █████████████████████████  96%  (15) │ │
│  │  Debate beat well-executed. Tension appropriate.                │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  Detected Issues:                                                      │
│  • Line 47: "He felt that he was nervous" → filter word              │
│  • Line 112: Industrial metaphor count: 8 (approaching limit)         │
│                                                                        │
│               [View Full Analysis]  [View in Context]                  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

**Hybrid Creator**:
```
┌────────────────────────────────────────────────────────────────────────┐
│ 🔀 Create Hybrid Scene                                           [✕]  │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ Combine the best elements from multiple variants:                      │
│                                                                        │
│ Selected Variants:                                                     │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ [1] Claude + Literary (92)                              [Remove]  ││
│ │ [2] GPT-4o + Atmospheric (88)                           [Remove]  ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ Merge Instructions:                                                    │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ Use the opening atmosphere from Variant 2 (GPT-4o).               ││
│ │ Take the dialogue exchanges from Variant 1 (Claude).              ││
│ │ Use Claude's ending but add more sensory detail from GPT-4o.      ││
│ │                                                                    ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ ⚠️ Hybrid generation will create a new variant combining these        │
│ elements. The AI will smooth transitions and maintain consistency.    │
│                                                                        │
│                    [Cancel]           [Generate Hybrid →]              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Prompt 3.6 – Director Mode: Enhancement Pipeline

**Role**: You are a UX Designer for editorial revision tools.

**Task**: Design the Enhancement Pipeline interface showing the 3 enhancement modes.

**Context**: Based on the scene score, the system recommends one of three enhancement approaches:
- **85-89**: Action Prompt (targeted fixes)
- **70-84**: Six-Pass Enhancement (systematic rewrite)
- **<70**: Full Rewrite recommended

**Modal Specifications**:
- Size: 1100px × 750px (split view)

**Layout (Action Prompt Mode - Score 85-89)**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✨ Enhancement Pipeline - Action Prompt Mode                          [✕]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Scene: 2.1 - The Confrontation     Score: 87/100 (A-)                       │
│ Mode: Action Prompt (targeted fixes for scores 85-89)                       │
│                                                                             │
├────────────────────────────────────────┬────────────────────────────────────┤
│                                        │                                    │
│      ORIGINAL TEXT                     │       SUGGESTED FIXES              │
│                                        │                                    │
│ The Packard plant warehouse held its   │ ┌────────────────────────────────┐│
│ breath as Mickey stepped across the    │ │ Fix 1 of 4                     ││
│ threshold. Three decades of Detroit's  │ │                                ││
│ decline had transformed the space      │ │ Line 47: Filter Word           ││
│ into something holy.                   │ │                                ││
│                                        │ │ OLD:                           ││
│ He [felt that he was nervous]          │ │ "He felt that he was nervous"  ││
│    ^^^^^^^^^^^^^^^^^^^^^^^^            │ │                                ││
│    ⚠️ Filter word detected             │ │ NEW:                           ││
│                                        │ │ "His hands trembled against    ││
│ Sarah stood in the center, exactly     │ │ his thighs"                    ││
│ where they used to play as children.   │ │                                ││
│ The photograph dangled from her        │ │ [Accept] [Reject] [Edit]       ││
│ fingers like an accusation.            │ └────────────────────────────────┘│
│                                        │                                    │
│ [More industrial metaphors than        │ ┌────────────────────────────────┐│
│ recommended in this paragraph...]      │ │ Fix 2 of 4                     ││
│    ^^^^^^^^^^^^^^^^^^^^^^^^^^          │ │                                ││
│    ⚠️ Metaphor saturation warning     │ │ Line 112: Metaphor Saturation  ││
│                                        │ │                                ││
│ "Fifteen years," she said. The words   │ │ OLD:                           ││
│ [echoed like machinery grinding to     │ │ "rust-eaten beams groaned      ││
│ a halt in the rust-eaten space].       │ │ like dying engines"            ││
│                                        │ │                                ││
│                                        │ │ NEW:                           ││
│                                        │ │ "the beams creaked overhead,   ││
│                                        │ │ shedding decades of dust"      ││
│                                        │ │                                ││
│                                        │ │ [Accept] [Reject] [Edit]       ││
│                                        │ └────────────────────────────────┘│
│                                        │                                    │
│                                        │ Progress: 1 of 4 fixes reviewed   │
│                                        │ Projected new score: 91/100       │
│                                        │                                    │
├────────────────────────────────────────┴────────────────────────────────────┤
│                                                                             │
│ [Accept All]  [Reject All]  [Show Diff]            [Apply Changes →]        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout (Six-Pass Mode - Score 70-84)**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✨ Enhancement Pipeline - Six-Pass Mode                               [✕]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Scene: 2.3 - The Chase     Score: 76/100 (C+)                               │
│ Mode: Six-Pass Enhancement (systematic improvement for scores 70-84)        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Enhancement Progress                                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Pass 1: Sensory Anchoring            ████████████████████ Complete │   │
│  │  Added 12 sensory details. +4 points.                               │   │
│  │                                                                     │   │
│  │  Pass 2: Dialogue Naturalization      ████████████████████ Complete │   │
│  │  Revised 8 dialogue tags. +3 points.                                │   │
│  │                                                                     │   │
│  │  Pass 3: Metaphor Balancing           ████████████░░░░░░░░ 60%      │   │
│  │  Redistributing domain usage...                                     │   │
│  │                                                                     │   │
│  │  Pass 4: Rhythm & Pacing              ░░░░░░░░░░░░░░░░░░░░ Pending  │   │
│  │  Sentence length variation                                          │   │
│  │                                                                     │   │
│  │  Pass 5: Voice Alignment              ░░░░░░░░░░░░░░░░░░░░ Pending  │   │
│  │  Calibrate to Voice Bundle                                          │   │
│  │                                                                     │   │
│  │  Pass 6: Anti-Pattern Sweep           ░░░░░░░░░░░░░░░░░░░░ Pending  │   │
│  │  Final cleanup pass                                                 │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Original Score: 76/100                                                     │
│  Current Score:  83/100 (+7)                                                │
│  Projected Final: 89/100                                                    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Pause]  [View Changes So Far]  [Skip to Pass 6]       [Continue →]        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout (Rewrite Warning - Score <70)**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚠️ Enhancement Pipeline - Rewrite Recommended                         [✕]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Scene: 2.5 - The Betrayal     Score: 58/100 (F)                             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │                    ⚠️ Score Below Enhancement Threshold             │   │
│  │                                                                     │   │
│  │  This scene scores 58/100, which is below the 70-point threshold   │   │
│  │  for effective enhancement. The Six-Pass process typically cannot  │   │
│  │  improve scenes by more than 15-20 points.                          │   │
│  │                                                                     │   │
│  │  Major Issues Detected:                                             │   │
│  │  • Voice: 45/100 - Significant drift from calibrated voice         │   │
│  │  • Character: 52/100 - Mickey's flaw not visible                   │   │
│  │  • Structure: Scene doesn't serve the "Midpoint" beat              │   │
│  │                                                                     │   │
│  │  Recommendations:                                                   │   │
│  │  1. Return to Scaffold Generator and revise the scene plan         │   │
│  │  2. Generate new variants with updated scaffold                     │   │
│  │  3. Consider if this scene is necessary (could it be cut?)         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [Back to Scaffold]  [Generate New Variants]  [Force Enhancement Anyway]    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Prompt 3.7 – Health Report Viewer

**Role**: You are a UX Designer for diagnostic and reporting interfaces.

**Task**: Design the Health Report Viewer showing manuscript-wide analysis.

**Context**: The health system analyzes the entire manuscript for structural issues: pacing problems, beat alignment, character consistency, theme resonance, and symbolic layering.

**Modal Specifications**:
- Size: 1000px × 750px

**Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🏥 Manuscript Health Report                                           [✕]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Generated: November 25, 2025, 2:34 PM    Scope: Full Manuscript             │
│                                                                             │
│ Overall Health: ████████████████░░░░ 82/100 (Good)                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐    │
│ │ Pacing  │  Beats  │Character│  Theme  │ Symbols │  Arc    │Conflicts│    │
│ │   85    │   78    │   91    │   80    │   75    │   88    │  ⚠️ 3   │    │
│ │    ✓    │   ⚠️    │    ✓    │    ✓    │   ⚠️    │    ✓    │         │    │
│ └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ▼ PACING ANALYSIS (85/100)                                          [Hide] │
│   ─────────────────────────────────────────────────────────────────────    │
│                                                                             │
│   Tension Curve:                                                            │
│   Act 1: ▁▂▃▄▅▆▇█▇▆  (Appropriate rising action)                           │
│   Act 2: █▇▆▅▅▅▅▆▇█  ⚠️ Plateau detected (Chapters 8-11)                   │
│   Act 3: ▆▇████████  (Strong climax)                                       │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ ⚠️ Warning: Tension Plateau                                         │  │
│   │                                                                     │  │
│   │ Chapters 8-11 show minimal tension variation (0.12 variance).      │  │
│   │ This 4-chapter stretch may feel slow to readers.                   │  │
│   │                                                                     │  │
│   │ Affected scenes: 8.1, 8.2, 9.1, 9.2, 10.1, 11.1                    │  │
│   │                                                                     │  │
│   │ LLM Assessment: "Plateau appears UNINTENTIONAL. The scenes         │  │
│   │ repeat similar emotional beats without escalation."                │  │
│   │                                                                     │  │
│   │ Recommendation: Introduce a complication in Chapter 9, or          │  │
│   │ compress Chapters 8-10 into two chapters.                          │  │
│   │                                                                     │  │
│   │ [View Affected Scenes]  [Mark as Intentional]                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│ ▶ BEAT PROGRESS (78/100)                                           [Show]  │
│   ─────────────────────────────────────────────────────────────────────    │
│   2 beats misaligned from ideal positions. Click to expand.                │
│                                                                             │
│ ▶ CHARACTER CONSISTENCY (91/100)                                   [Show]  │
│   ─────────────────────────────────────────────────────────────────────    │
│   All main characters consistent. 1 minor character age discrepancy.       │
│                                                                             │
│ ▶ THEME RESONANCE (80/100)                                         [Show]  │
│   ─────────────────────────────────────────────────────────────────────    │
│   Theme statement appears in 12 scenes. Recommended: 15+.                  │
│                                                                             │
│ ▼ SYMBOLIC LAYERING (75/100)                                        [Hide] │
│   ─────────────────────────────────────────────────────────────────────    │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ Symbol: "The Photograph"                                            │  │
│   │ Occurrences: 8 │ Meaning Evolution: ✓ (progresses across acts)     │  │
│   │                                                                     │  │
│   │ Act 1: Memory/nostalgia                                             │  │
│   │ Act 2: Evidence/accusation                                          │  │
│   │ Act 3: Reconciliation/acceptance                                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ ⚠️ Warning: Underdeveloped Symbol                                   │  │
│   │                                                                     │  │
│   │ Symbol: "The Warehouse"                                             │  │
│   │ Occurrences: 3 (minimum recommended: 5)                            │  │
│   │                                                                     │  │
│   │ This symbol appears in Act 1 and Act 2 but is absent from Act 3.  │  │
│   │ Consider reintroducing it in the climax for resonance.             │  │
│   │                                                                     │  │
│   │ [View Occurrences]  [Dismiss]                                       │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ [Export as Markdown]  [Export as JSON]  [Schedule Auto-Check]  [Close]      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 4: Supporting Components

### Prompt 4.1 – Menu Bar

**Role**: You are a UI Designer for desktop application chrome.

**Task**: Design the application menu bar for Writers Factory.

**Specifications**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📝 Writers Factory    File  Edit  Selection  View  AI  Go  Run  Help       │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Menu Contents**:

**File**: New, Open, Save, Save As, Export, Close, Exit
**Edit**: Undo, Redo, Cut, Copy, Paste, Find, Replace
**Selection**: Select All, Expand Selection, Shrink Selection
**View**: Toggle Binder, Toggle Studio, Toggle Foreman, Zoom In/Out, Full Screen
**AI**:
  - Foreman Mode ▸ (Architect, Voice Cal, Director, Editor)
  - Model Orchestrator ▸ (Budget, Balanced ✓, Premium)
  - Run Health Check
  - Trigger Metabolism
**Go**: Go to Scene, Go to Chapter, Go to Beat, Go to Conflict
**Run**: Run Tournament, Generate Variants, Enhance Scene
**Help**: Documentation, Keyboard Shortcuts, About

---

### Prompt 4.2 – Status Bar

**Role**: You are a UI Designer for information-dense status displays.

**Task**: Design the application status bar.

**Specifications**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Graph: 1,240 nodes • 3,891 edges │ ⚠️ Uncommitted: 3 │ Claude 3.5 │ DIRECTOR │ Ln 142, Col 8 │ 1,247 words │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Sections** (left to right):
1. **Graph Stats**: Node/edge count
2. **Metabolism Status**: Uncommitted event count (yellow if >0, click to digest)
3. **Active Model**: Current AI model
4. **Foreman Mode**: Color-coded badge (click to change)
5. **Cursor Position**: Line and column
6. **Word Count**: Current file word count

---

### Prompt 4.3 – Toast Notifications

**Role**: You are a UI Designer for notification systems.

**Task**: Design the toast notification system.

**Specifications**:
- Position: Bottom-right corner, stacked
- Width: 350px
- Auto-dismiss: 5 seconds (errors persist)
- Types: Success (green), Error (red), Warning (yellow), Info (blue)

**Examples**:
```
┌───────────────────────────────────────┐
│ ✓ Scene saved successfully            │
│   Scene 2.1 saved to manuscript       │
│                               [Undo]  │
└───────────────────────────────────────┘

┌───────────────────────────────────────┐
│ ⚠️ API rate limit approaching         │
│   80% of daily quota used             │
│                      [View Settings]  │
└───────────────────────────────────────┘

┌───────────────────────────────────────┐
│ ❌ Enhancement failed                  │
│   Claude API returned error 429       │
│                              [Retry]  │
└───────────────────────────────────────┘
```

---

### Prompt 4.4 – Loading States

**Role**: You are a UI Designer for progress and loading states.

**Task**: Design loading indicators for various operations.

**Types**:

1. **Full Screen Overlay** (long operations):
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                     ◌ Generating 15 variants...                 │
│                                                                 │
│                     ████████░░░░░░░░ 53%                        │
│                                                                 │
│                     Claude: 5/5 ✓                               │
│                     GPT-4o: 3/5 ◌                               │
│                     DeepSeek: 0/5 ○                             │
│                                                                 │
│                     [Cancel]                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

2. **Inline Spinner** (quick operations):
```
[◌ Saving...] or [◌ Loading graph...]
```

3. **Skeleton States** (content loading):
```
┌─────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░ │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░ │
│ ▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────┘
```

---

### Prompt 4.5 – Command Palette

**Role**: You are a UI Interaction Designer.

**Task**: Design the Command Palette (Cmd+K) interaction.

**Specifications**:
- Size: 600px width, variable height
- Position: Centered, top third of screen
- Overlay: Blurred background

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔍 Type a command or search...                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Recent                                                          │
│ ├─ 📝 Scene 2.1 - The Confrontation              [↵ to open]   │
│ └─ ⚙️ Settings > Agents                          [↵ to open]   │
│                                                                 │
│ Actions                                                         │
│ ├─ 🏗️ Generate Scaffold                              ⌘⇧S       │
│ ├─ ✍️ Run Scene Tournament                           ⌘⇧T       │
│ ├─ ✨ Enhance Current Scene                          ⌘⇧E       │
│ ├─ 🧠 Trigger Metabolism                             ⌘⇧M       │
│ └─ 🏥 Run Health Check                               ⌘⇧H       │
│                                                                 │
│ Navigation                                                      │
│ ├─ → Go to Scene...                                  ⌘G        │
│ ├─ → Switch Foreman Mode...                          ⌘⇧F       │
│ └─ → Open Settings...                                ⌘,        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Checklist

### Infrastructure (P0) - 12 components
- [ ] MainLayout (4-panel shell)
- [ ] PanelBinder
- [ ] PanelCanvas
- [ ] PanelForeman
- [ ] PanelStudio
- [ ] MenuBar
- [ ] StatusBar
- [ ] StudioCard (reusable)
- [ ] SettingSlider
- [ ] SettingDropdown
- [ ] SettingToggle
- [ ] SettingSecret

### Core Features (P1) - 31 components
- [ ] ForemanChat + ForemanMessage
- [ ] WorkOrderTracker
- [ ] ForemanModeIndicator
- [ ] LiveGraph + GraphControls
- [ ] 8 Studio cards (StoryBible, Voice, Scaffold, Scene, Enhancement, Health, Metabolism, Settings)
- [ ] SettingsPanel + 4 critical sub-panels (Agents, Scoring, Orchestrator, Foreman)
- [ ] StoryBibleWizard + NotebookRegistration
- [ ] VoiceTournamentLauncher + VoiceVariantGrid + VoiceSelectionModal
- [ ] ScaffoldGenerator + EnrichmentSuggestions
- [ ] SceneVariantTournament + SceneScorecard
- [ ] EnhancementPipeline
- [ ] HealthReportViewer
- [ ] ToastNotifications
- [ ] CommandPalette

### Enhanced Features (P2) - 31 components
- [ ] FileContextMenu
- [ ] NodeDetailsPanel
- [ ] GraphConflictIndicator
- [ ] TemplateEditor
- [ ] VoiceBundlePreview
- [ ] SceneStructureSelector
- [ ] HybridSceneCreator
- [ ] ScoreComparison
- [ ] AntiPatternDetector
- [ ] MetaphorAnalyzer
- [ ] HealthTrendsChart
- [ ] HealthCheckTrigger
- [ ] GraphConflictResolver
- [ ] Settings sub-panels (Voice, Metaphor, AntiPatterns, Enhancement, Health, Advanced)
- [ ] SessionSwitcher
- [ ] UncommittedEventsIndicator
- [ ] ConsolidationProgress
- [ ] NotebookQueryModal
- [ ] LoadingOverlay

### Nice to Have (P3) - 13 components
- [ ] ThemeOverrideModal
- [ ] GraphIngestModal
- [ ] SessionHistoryBrowser
- [ ] SettingsTournament
- [ ] ModelRecommendationsPreview
- [ ] NotebookAuthFlow

---

*Generated: November 25, 2025*
*Aligned with: UI_COMPONENT_INVENTORY.md v2.0*
*Total Prompts: 18*
*Total Components Specified: 87*
