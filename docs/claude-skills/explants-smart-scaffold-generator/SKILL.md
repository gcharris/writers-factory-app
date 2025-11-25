---
name: explants-smart-scaffold-generator
description: Transform minimal chapter/scene outlines into comprehensive "Gold Standard" scaffolds ready for multi-agent orchestration. Uses NotebookLM knowledge base to generate detailed context including character states, voice requirements, philosophical framework, and success criteria. Trigger when user provides minimal outline or requests scaffold generation for specific chapters/scenes.
---

# Explants Smart Scaffold Generator

Transform minimal chapter/scene outlines into comprehensive "Gold Standard" scaffolds by querying the NotebookLM knowledge base containing all project architectural documents.

## Core Workflow

### Step 1: Extract Input Requirements

From minimal outline or user request, identify:
- **Chapter/Scene Number & Title** (e.g., "Chapter 4: Vance's Approach")
- **Act & Setting** (e.g., "Act IV: The New Bondage - Pasadena dojo")
- **POV Character** (typically Mickey Bardot)
- **Key Plot Beats** (4-6 main story points)
- **Word Count Goal** (typically 5,000-6,000 words)

### Step 2: Verify NotebookLM Setup

Run authentication and notebook checks:
```bash
cd ~/.claude/skills/notebooklm && python scripts/run.py auth_manager.py status
cd ~/.claude/skills/notebooklm && python scripts/run.py notebook_manager.py list
```

**Critical:** Ensure active notebook contains the ACE prompt template document.

### Step 3: Generate Scaffold Query

Use the condensed query format from `references/ace-template.md`, substituting variables:
```
Generate Gold Standard Scaffold for [Chapter Title] using ACE template.
Act [Number]: [Title]. Setting: [Location & POV]. 
Beats: [condensed beat list]. Word count: [target].
```

### Step 4: Query NotebookLM

```bash
cd ~/.claude/skills/notebooklm && python scripts/run.py ask_question.py --question "[QUERY]"
```

### Step 5: Validate & Save

Check output against quality indicators in `references/quality-checklist.md`:
- ✅ Chapter Overview with voice state and core function
- ✅ Strategic Context with conflict positioning
- ✅ Success Criteria with quality thresholds
- ✅ Continuity Checklist with callbacks
- ✅ Precise philosophical terminology

Save as: `CHAPTER_[X]_[TITLE]_SCAFFOLD.md`

### Step 6: Report Results

Confirm scaffold quality and readiness for handoff to `explants-mickey-scene-writer` skill.

## Integration with Scene Pipeline

**Complete Workflow:**
```
Minimal Outline → Smart Scaffold Generator → Scene Writer → Enhancement → Analyzer → Final Scene
```

**Handoff to Scene Writer:**
```
Use [SCAFFOLD_FILENAME] to generate the full chapter.
```

## Advanced Usage

- **Batch Processing:** Process multiple outlines in sequence
- **Quality Validation:** Compare against reference example
- **Notebook Maintenance:** See `references/notebook-setup.md` for requirements

## References

- `references/ace-template.md` - Complete ACE prompt with variable substitution
- `references/quality-checklist.md` - Validation criteria and quality indicators  
- `references/notebook-setup.md` - Required documents and maintenance workflow
- `references/troubleshooting.md` - Common issues and solutions
- `assets/reference-scaffold.md` - Gold standard example for comparison

## Output Quality Standards

Generated scaffolds must match the structure and detail of the reference example, providing complete context for multi-agent scene generation without requiring additional knowledge base access.
