# Claude Skills (Reference Materials)

**Status**: Reference Only - Not Active Code
**Purpose**: Original Claude skills that served as reference for implementing Writers Factory backend services

---

## Overview

This folder contains the original Claude skills (from Explants project) that were used as **reference implementation** when building the Writers Factory Director Mode backend services. These are **not active code** - they are documentation and reference materials showing how the vanilla Director Mode services were originally conceived.

## Contents

### Scene Writing Skills
1. **explants-mickey-scene-writer/** - Scene writing skill with Mickey Bardot voice
2. **explants-scene-analyzer-scorer/** - Scene analysis and scoring skill (5-category rubric)
3. **explants-scene-enhancement/** - Scene enhancement skill (Action Prompt, 6-Pass)
4. **explants-smart-scaffold-generator/** - Scaffold generation skill with NotebookLM integration
5. **explants-scene-multiplier/** - Scene multiplier skill (5 strategy variants)

### Character & Voice
6. **mickey-bardot-character-identity/** - Mickey Bardot character identity skill

### Reference Files
7. **Gemini Gem files/** - Gemini reference files for Mickey Bardot character
8. **SKILLS_AUDIT_SUMMARY.md** - Skills audit summary
9. **Sample Explants Chapter:scene generation.md** - Sample chapter generation session
10. **COMPLETE_CHAPTER_CREATION_PIPELINE.md** - Complete pipeline documentation
11. **Mickey Gemini Gem Instructions.md** - Gemini instructions for Mickey character

---

## How These Skills Inform Writers Factory

The Claude skills in this folder served as **proof of concept** for the Director Mode backend services:

| Claude Skill | Writers Factory Service | Status |
|--------------|-------------------------|--------|
| **explants-scene-analyzer-scorer** | `SceneAnalyzerService` | ✅ Implemented (Phase 3B) |
| **explants-smart-scaffold-generator** | `ScaffoldGeneratorService` | ✅ Implemented (Phase 3B) |
| **explants-mickey-scene-writer** | `SceneWriterService` | ✅ Implemented (Phase 3B) |
| **explants-scene-enhancement** | `SceneEnhancementService` | ✅ Implemented (Phase 3B) |
| **explants-scene-multiplier** | `SceneWriterService` (tournament) | ✅ Implemented (Phase 3B) |

---

## Key Differences: Skills vs. Services

### Claude Skills (This Folder)
- **Hard-coded for Mickey Bardot voice** (Explants project)
- **Claude-specific prompts and skill structure**
- **Single-project focus** (Mickey's Quantum Bio-Visibility trilogy)
- **Manual workflow** (copy-paste between skills)

### Writers Factory Services (Backend)
- **Universal framework** for any writer's voice (Phase 3C Settings-Driven)
- **Multi-model support** (Claude, GPT-4o, DeepSeek, Qwen)
- **Project-agnostic** (works with any novel project)
- **Automated workflow** (Foreman orchestration, API-driven)

---

## Why Retained?

These skills are retained in the repository because:
1. **Historical Record**: Show the original design thinking and implementation
2. **Reference Documentation**: Demonstrate how voice consistency, metaphor discipline, and anti-pattern detection were originally conceived
3. **Prompt Engineering**: Contain valuable system prompts and scoring rubrics that informed the Writers Factory backend
4. **Character Reference**: Mickey Bardot character files demonstrate the level of detail needed in Story Bible

---

## Important Notes

**DO NOT**:
- ❌ Use these skills directly in Writers Factory
- ❌ Attempt to import these as active code
- ❌ Confuse these with Writers Factory backend services

**DO**:
- ✅ Refer to these for understanding Director Mode design decisions
- ✅ Use as reference when adding new features to Director Mode
- ✅ Study the prompts and scoring rubrics for improvement ideas

---

**Status**: Reference materials only
**Active Code Location**: `/backend/services/` (SceneAnalyzerService, ScaffoldGeneratorService, SceneWriterService, SceneEnhancementService)
**Last Updated**: November 25, 2025
