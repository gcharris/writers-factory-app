# Component Audit - Writers Factory Frontend

> Audit of all 91 Svelte components to identify integration status and wiring gaps.

**Audit Date**: November 30, 2025
**Last Updated**: November 30, 2025
**Total Components**: 90 (after cleanup)
**Integrated**: 46 (51%) - up from 42
**Orphaned**: 44 (49%) - down from 49

---

## Session Progress (eloquent-raman branch)

### Completed This Session
- [x] Created Component Audit document
- [x] Deleted `FileTree 2.svelte` (duplicate)
- [x] Wired 4 orphaned components to StudioToolsPanel:
  - VoiceTournamentLauncher → voice-tournament tab
  - ScaffoldGenerator → scaffold-generator tab
  - HealthDashboard → health-dashboard tab
  - SceneVariantGrid → scene-multiplier tab
- [x] Created Track A components (ScoreDisplay, ModeIndicator, ForemanAction)
- [x] Fixed FileTree file loading bug (encodeURIComponent issue)

### Pending Testing (IDE Agent)
- [ ] Test StudioToolsPanel tabs render correctly
- [ ] Test folder expansion in FileTree
- [ ] Verify onboarding persistence in Tauri WebView
- [ ] Run `npm run check` for TypeScript errors

### Remaining Work (Track B Revised)
- [ ] Wire GraphModal to graph exploration components
- [ ] Add "Force Advance Phase" debug tool
- [ ] Fix any bugs found during testing
- [ ] Wire remaining useful orphaned components

---

## Integration Status Summary

| Status | Count | Description |
|--------|-------|-------------|
| **Integrated** | 42 | Imported and used in the app flow |
| **Orphaned** | 49 | Exist but never imported/rendered |
| **Duplicate** | 1 | `FileTree 2.svelte` - should be deleted |

---

## Integrated Components (42)

These components are actively used in the application:

### Core Layout (from +page.svelte)
| Component | Location | Purpose |
|-----------|----------|---------|
| MainLayout.svelte | components/ | 3-panel IDE layout with toolbar/statusbar |
| FileTree.svelte | components/ | Binder panel file browser |
| TreeNode.svelte | components/ | File tree node (used by FileTree) |
| Editor.svelte | components/ | Monaco editor for manuscript |
| ForemanPanel.svelte | components/ | Chat interface panel |
| Modal.svelte | components/ | Reusable modal wrapper |

### Modals (from +page.svelte)
| Component | Location | Purpose |
|-----------|----------|---------|
| SettingsPanel.svelte | components/ | Settings tabbed modal |
| StudioToolsPanel.svelte | components/ | Studio tools tabbed modal |
| GraphModal.svelte | components/ | Knowledge graph viewer |
| NotebookLMPanel.svelte | components/ | NotebookLM research interface |
| SessionManagerModal.svelte | components/ | Chat session history |
| OnboardingWizard.svelte | Onboarding/ | First-time setup wizard |

### From MainLayout.svelte
| Component | Location | Purpose |
|-----------|----------|---------|
| StatusBar.svelte | components/ | Bottom status bar |
| Toast.svelte | components/ | Toast notifications |
| StoryBibleWizard.svelte | components/ | Story Bible creation flow |
| NotebookRegistration.svelte | components/ | NotebookLM notebook registration |

### From StatusBar.svelte
| Component | Location | Purpose |
|-----------|----------|---------|
| ModeIndicator.svelte | StatusBar/ | Foreman mode indicator (NEW) |

### From ForemanPanel.svelte (Chat Components)
| Component | Location | Purpose |
|-----------|----------|---------|
| AgentDropdown.svelte | chat/ | Agent/model selector |
| StageDropdown.svelte | chat/ | Writing stage selector |
| MentionPicker.svelte | chat/ | @mention autocomplete |
| AttachButton.svelte | chat/ | File attachment button |
| ContextBadge.svelte | chat/ | Context item badges |
| VoiceInput.svelte | chat/ | Voice dictation button |
| StatusBar.svelte | chat/ | Chat-specific status bar |
| WorkOrderHistory.svelte | chat/ | Work order history panel |
| ForemanAction.svelte | chat/ | Foreman action renderer (NEW) |

### From SettingsPanel.svelte
| Component | Location | Purpose |
|-----------|----------|---------|
| SettingsAgents.svelte | Settings/ | API keys configuration |
| SettingsOrchestrator.svelte | Settings/ | AI model/quality tier |
| SettingsVoice.svelte | Settings/ | Voice calibration settings |
| SettingsAdvanced.svelte | Settings/ | Advanced options |
| SettingsAssistant.svelte | Settings/ | Assistant personalization |
| SquadWizard.svelte | Squads/ | Squad configuration wizard |

### From Settings Components (Shared)
| Component | Location | Purpose |
|-----------|----------|---------|
| SettingsSection.svelte | Settings/ | Reusable section wrapper |
| SettingsToggle.svelte | Settings/ | Toggle switch control |
| SettingsSlider.svelte | Settings/ | Slider control |
| SettingsRadioGroup.svelte | Settings/ | Radio button group |

### From Onboarding
| Component | Location | Purpose |
|-----------|----------|---------|
| Step1WorkspaceLocation.svelte | Onboarding/ | Workspace folder selection |
| Step2CloudModels.svelte | Onboarding/ | Cloud model API key setup |
| Step3NameAssistant.svelte | Onboarding/ | Assistant naming |

### Director Mode (NEW - from Track A)
| Component | Location | Purpose |
|-----------|----------|---------|
| ScoreDisplay.svelte | Director/ | 100-point scoring rubric display (NEW) |

---

## Orphaned Components (49)

These components exist but are **NOT imported anywhere**. They either:
1. Were planned but never wired up
2. Are duplicates of other implementations
3. Were deprecated but not deleted

### High-Priority Orphans (Should Be Wired Up)

These are **complete, useful components** that just need to be integrated:

| Component | Location | Backend Ready? | Integration Target |
|-----------|----------|----------------|-------------------|
| **HealthDashboard.svelte** | components/ | YES | StudioToolsPanel health tab |
| **GraphHealthDashboard.svelte** | components/ | YES | StudioToolsPanel or standalone |
| **LiveGraph.svelte** | components/ | YES | GraphModal or StudioToolsPanel |
| **GraphExplorer.svelte** | components/ | YES | GraphModal |
| **GraphCanvas.svelte** | components/ | YES | GraphModal/GraphExplorer |
| **GraphControls.svelte** | components/ | YES | GraphModal/GraphExplorer |
| **GraphNodeDetails.svelte** | components/ | YES | GraphExplorer |
| **ScaffoldGenerator.svelte** | components/ | YES | StudioToolsPanel scaffold tab |
| **VoiceTournamentLauncher.svelte** | components/ | YES | StudioToolsPanel voice tab |
| **VoiceVariantGrid.svelte** | components/ | YES | Voice tournament UI |
| **VoiceComparisonView.svelte** | components/ | YES | Voice tournament UI |
| **SceneVariantGrid.svelte** | components/ | YES | Director mode UI |
| **SceneComparison.svelte** | components/ | YES | Director mode UI |
| **SixPassEnhancement.svelte** | components/ | YES | Director mode UI |
| **ActionPromptView.svelte** | components/ | YES | Director mode UI |
| **EnhancementPanel.svelte** | components/ | YES | Director mode UI |
| **HardwareStatusPanel.svelte** | Squads/ | YES | SquadWizard or Settings |

### Medium-Priority Orphans (Need Review)

| Component | Location | Notes |
|-----------|----------|-------|
| ArchitectModeUI.svelte | components/ | Mode-specific UI - check if needed |
| StudioPanel.svelte | components/ | May be older version of StudioToolsPanel |
| ForemanChatPanel.svelte | components/ | Different chat implementation? |
| AgentPanel.svelte | components/ | Check if different from ForemanPanel |
| ChatSidebar.svelte | components/ | Check if deprecated |
| NotebookPanel.svelte | components/ | Duplicate of NotebookLMPanel? |
| TabbedPanel.svelte | components/ | Generic tabbed panel - may be useful |
| UsageIndicator.svelte | components/ | API usage tracking - wire to StatusBar? |
| WorkOrderTracker.svelte | components/ | Different from WorkOrderHistory? |

### Low-Priority Orphans (Settings Variants)

| Component | Location | Notes |
|-----------|----------|-------|
| SettingsForeman.svelte | Settings/ | May be duplicate |
| SettingsHealth.svelte | Settings/ | Check if needed |
| SettingsScoring.svelte | Settings/ | Scoring rubric settings |
| SettingsEnhancement.svelte | Settings/ | Enhancement settings |
| SettingsKeyProvisioning.svelte | Settings/ | May be part of SettingsAgents |
| SettingsSquad.svelte | Settings/ | May duplicate SquadWizard |
| SettingsForeman.svelte | components/ | Root-level duplicate |
| SettingsEnhancement.svelte | components/ | Root-level duplicate |
| SettingsScoring.svelte | components/ | Root-level duplicate |
| SettingsTournament.svelte | components/ | Tournament settings |
| SettingsAntiPatterns.svelte | components/ | Anti-pattern config |
| SettingsContext.svelte | components/ | Context settings |

### Visualization Components (Need D3/Force Graph)

| Component | Location | Notes |
|-----------|----------|-------|
| GraphRelationshipEditor.svelte | components/ | Graph editing UI |
| HealthReportDetail.svelte | components/ | Detailed health reports |
| HealthTrends.svelte | components/ | Health over time charts |
| VoiceEvolutionChart.svelte | components/ | Voice calibration charts |
| VoiceBundleGenerator.svelte | components/ | Voice bundle creation |
| VoiceVariantSelector.svelte | components/ | Voice selection UI |
| StructureVariantSelector.svelte | components/ | Structure selection |
| SceneScoreBreakdown.svelte | components/ | Detailed score breakdown |
| ThemeOverridePanel.svelte | components/ | Theme customization |

### Definitely Delete

| Component | Location | Reason |
|-----------|----------|--------|
| FileTree 2.svelte | components/ | Duplicate with space in name |

**Note**: `Step1LocalAI.svelte` is NOT a duplicate - it's Step 2 (Ollama check), while `Step1WorkspaceLocation.svelte` is Step 1 (workspace folder). Both are needed.

### Editors (Alternative Implementations)

| Component | Location | Notes |
|-----------|----------|-------|
| CodeMirrorEditor.svelte | components/ | Alternative to Monaco |
| EditorHelp.svelte | components/ | Editor help panel |
| ModelSelector.svelte | chat/ | May duplicate AgentDropdown |

---

## Real Blockers for Testing

Based on IDE agent feedback, these are the actual blockers:

### 1. Folder Expansion Bug
**Location**: `FileTree.svelte` / `TreeNode.svelte`
**Issue**: Clicking folders to expand doesn't work properly
**Impact**: Can't navigate project files
**Priority**: HIGH

### 2. Temp Debug Code Resetting Onboarding
**Location**: `+page.svelte` (check onMount)
**Issue**: Debug code may reset `hasCompletedOnboarding`
**Impact**: Onboarding shows every time
**Priority**: HIGH

### 3. TypeScript Errors (~1028)
**Command**: `npm run check`
**Impact**: Type safety, potential runtime bugs
**Priority**: MEDIUM (doesn't block runtime)

### 4. StudioToolsPanel Shows Placeholders
**Location**: `StudioToolsPanel.svelte`
**Issue**: All tabs show "coming soon" placeholders
**Impact**: None of the studio tools work
**Priority**: HIGH - just needs wiring to existing components

---

## Recommended Wiring Tasks

### Priority 1: Wire Existing Components to StudioToolsPanel

The `StudioToolsPanel.svelte` currently shows placeholders for each tab. Wire up:

```
voice-tournament tab → VoiceTournamentLauncher.svelte + VoiceVariantGrid.svelte
scaffold-generator tab → ScaffoldGenerator.svelte
health-dashboard tab → HealthDashboard.svelte OR GraphHealthDashboard.svelte
scene-multiplier tab → SceneVariantGrid.svelte + SceneComparison.svelte
```

### Priority 2: Wire Graph Components to GraphModal

The `GraphModal.svelte` exists but likely shows nothing. Wire up:
```
GraphModal → GraphExplorer.svelte → GraphCanvas.svelte + GraphControls.svelte + GraphNodeDetails.svelte
```

### Priority 3: Add Debug Tools

Add a "Force Advance Phase" button for testing gated progression:
```
Location: StatusBar or Settings Advanced tab
Action: Call /foreman/advance-mode endpoint
```

### Priority 4: Clean Up Duplicates

1. Delete `FileTree 2.svelte`
2. Consolidate Settings duplicates
3. Decide between NotebookPanel vs NotebookLMPanel

---

## Integration Checklist for Track B

Instead of building new components, Track B should focus on **wiring up existing orphaned components**:

- [ ] Wire HealthDashboard to StudioToolsPanel health tab
- [ ] Wire ScaffoldGenerator to StudioToolsPanel scaffold tab
- [ ] Wire VoiceTournamentLauncher to StudioToolsPanel voice tab
- [ ] Wire SceneVariantGrid to StudioToolsPanel scene tab
- [ ] Wire GraphExplorer/GraphCanvas to GraphModal
- [ ] Wire LiveGraph to GraphModal or StatusBar
- [ ] Add UsageIndicator to StatusBar
- [ ] Wire HardwareStatusPanel to SquadWizard
- [ ] Add debug "Force Advance Phase" tool
- [ ] Delete FileTree 2.svelte
- [ ] Fix folder expansion bug
- [ ] Remove onboarding reset debug code

---

## Audit Methodology

1. Glob pattern to find all components: `frontend/src/lib/components/**/*.svelte`
2. Grep for imports: `import.*from.*components`
3. Read entry points: `+page.svelte`, `+layout.svelte`
4. Trace import chains from entry points
5. Mark any component not in import chain as "orphaned"

---

*Generated by Component Audit task - November 2025*
