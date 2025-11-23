# Director Mode API Reference

**Version**: 1.0
**Date**: November 23, 2025
**Base URL**: `http://localhost:8000`

---

## Overview

Director Mode provides 16 API endpoints organized into four categories:

| Category | Endpoints | Purpose |
|----------|-----------|---------|
| Scaffold Generation | 3 | Two-stage context assembly |
| Scene Writing | 4 | Multi-model variant generation |
| Scene Analysis | 4 | 5-category scoring framework |
| Scene Enhancement | 4 | Two-mode polish pipeline |

---

## Scaffold Generation

### POST /director/scaffold/draft-summary

**Stage 1**: Generate a draft summary with enrichment suggestions.

This is the checkpoint where the writer decides whether to add NotebookLM enrichment before generating the full scaffold.

**Request Body:**
```json
{
  "project_id": "string",
  "chapter_number": 1,
  "scene_number": 1,
  "beat_info": {
    "beat_number": 7,
    "beat_name": "Midpoint",
    "beat_percentage": "50%",
    "description": "Character commits to goal",
    "beat_type": "mirror_moment"
  },
  "characters": [
    {
      "name": "John Smith",
      "role": "protagonist",
      "fatal_flaw": "Pride",
      "the_lie": "I don't need anyone",
      "arc_state": "Still believing The Lie"
    }
  ],
  "scene_description": "John confronts his past at the old house",
  "available_notebooks": [
    {"id": "abc123", "role": "world"},
    {"id": "def456", "role": "voice"}
  ]
}
```

**Response:**
```json
{
  "project_id": "string",
  "chapter_number": 1,
  "scene_number": 1,
  "narrative_summary": "In this pivotal scene...",
  "available_context": {
    "from_story_bible": ["protagonist flaw", "theme"],
    "from_kb": ["previous scene events"]
  },
  "enrichment_suggestions": [
    {
      "notebook_id": "abc123",
      "suggested_query": "What are the details of the old family house?",
      "reason": "Setting authenticity"
    }
  ]
}
```

---

### POST /director/scaffold/enrich

Fetch enrichment data from a NotebookLM notebook.

**Request Body:**
```json
{
  "notebook_id": "abc123",
  "query": "What are the details of the old family house?"
}
```

**Response:**
```json
{
  "notebook_id": "abc123",
  "query": "What are the details of the old family house?",
  "answer": "The family house was a Victorian...",
  "retrieved_at": "2025-11-23T22:30:00Z"
}
```

---

### POST /director/scaffold/generate

**Stage 2**: Generate the full scaffold document with optional enrichment.

**Request Body:**
```json
{
  "project_id": "string",
  "chapter_number": 1,
  "scene_number": 1,
  "title": "The Return Home",
  "beat_info": { ... },
  "characters": [ ... ],
  "scene_description": "string",
  "voice_state": "confident but vulnerable",
  "phase": "act2_midpoint",
  "target_word_count": "1500-2000",
  "theme": "Pride prevents connection",
  "enrichment_data": [
    {
      "notebook_id": "abc123",
      "query": "What are the details...",
      "answer": "The family house was..."
    }
  ]
}
```

**Response:**
```json
{
  "scaffold": {
    "chapter_number": 1,
    "scene_number": 1,
    "title": "The Return Home",
    "beat_info": { ... },
    "characters": [ ... ],
    "voice_state": "confident but vulnerable",
    "phase": "act2_midpoint",
    "strategic_context": "...",
    "continuity_notes": "...",
    "success_criteria": [ ... ],
    "enrichment_applied": [ ... ]
  },
  "markdown": "# Scene 1.1: The Return Home\n\n..."
}
```

---

## Scene Writing

### POST /director/scene/structure-variants

Generate 5 different structural approaches to a scene before writing prose.

**Request Body:**
```json
{
  "scene_id": "ch1_s1",
  "beat_description": "Protagonist confronts past",
  "scaffold": { ... },
  "pov_character": "John",
  "target_word_count": "1500-2000"
}
```

**Response:**
```json
{
  "scene_id": "ch1_s1",
  "variants": [
    {
      "id": "A",
      "approach": "Action-heavy",
      "description": "Fast pacing, physical movement",
      "sections": [
        {"name": "Opening", "word_count": 300, "focus": "Physical arrival"},
        {"name": "Discovery", "word_count": 500, "focus": "Finding artifact"},
        ...
      ],
      "strengths": ["Momentum", "Tension"],
      "weaknesses": ["Less introspection"]
    },
    {
      "id": "B",
      "approach": "Character-focused",
      ...
    },
    ...
  ],
  "recommendation": "A",
  "recommendation_reason": "Beat function favors external action"
}
```

---

### POST /director/scene/generate-variants

Generate scene variants using multiple models and strategies.

**Request Body:**
```json
{
  "scene_id": "ch1_s1",
  "scaffold": { ... },
  "structure_variant": { ... },
  "voice_bundle_path": "projects/my_project/voice_references",
  "story_bible": {
    "protagonist_name": "John",
    "fatal_flaw": "Pride",
    "the_lie": "I don't need anyone",
    "theme": "Connection requires vulnerability",
    "phase": "act2"
  },
  "models": [
    {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "name": "Claude"},
    {"provider": "openai", "model": "gpt-4o", "name": "GPT-4o"},
    {"provider": "deepseek", "model": "deepseek-chat", "name": "DeepSeek"}
  ],
  "strategies": ["action", "character", "dialogue", "atmospheric", "balanced"],
  "target_word_count": 1500
}
```

**Response:**
```json
{
  "scene_id": "ch1_s1",
  "variants": [
    {
      "variant_id": "Claude_action_1",
      "model_name": "Claude",
      "strategy": "action",
      "content": "The front door...",
      "word_count": 1523,
      "score": 87,
      "grade": "A-",
      "analysis": { ... }
    },
    ...
  ],
  "rankings": [
    {"variant_id": "Claude_character_2", "score": 92, "grade": "A"},
    {"variant_id": "GPT-4o_balanced_5", "score": 89, "grade": "A-"},
    ...
  ],
  "winner": {
    "variant_id": "Claude_character_2",
    "score": 92,
    "grade": "A"
  },
  "total_variants": 15,
  "generation_time_ms": 45000
}
```

---

### POST /director/scene/create-hybrid

Create a hybrid scene by combining elements from multiple variants.

**Request Body:**
```json
{
  "scene_id": "ch1_s1",
  "variant_ids": ["Claude_character_2", "GPT-4o_balanced_5"],
  "sources": [
    {"variant_id": "Claude_character_2", "section": "opening"},
    {"variant_id": "GPT-4o_balanced_5", "section": "dialogue"},
    {"variant_id": "Claude_character_2", "section": "closing"}
  ],
  "instructions": "Use Claude's introspective opening, GPT's dialogue pacing, Claude's emotional resolution"
}
```

**Response:**
```json
{
  "scene_id": "ch1_s1",
  "hybrid_content": "...",
  "sources_used": [ ... ],
  "word_count": 1487,
  "score": 91,
  "grade": "A"
}
```

---

### POST /director/scene/quick-generate

Fast single-model generation without tournament.

**Request Body:**
```json
{
  "scene_id": "ch1_s1",
  "scaffold": { ... },
  "voice_bundle_path": "projects/my_project/voice_references",
  "strategy": "balanced",
  "target_word_count": 1500
}
```

**Response:**
```json
{
  "variant_id": "quick_ch1_s1",
  "content": "...",
  "word_count": 1489,
  "score": 84,
  "grade": "A-",
  "model": "claude-sonnet-4-20250514",
  "strategy": "balanced"
}
```

---

## Scene Analysis

### POST /director/scene/analyze

Full 5-category analysis of a scene draft.

**Request Body:**
```json
{
  "scene_id": "ch1_s1",
  "scene_content": "The front door groaned...",
  "pov_character": "John",
  "phase": "act2",
  "voice_bundle_path": "projects/my_project/voice_references",
  "story_bible": {
    "protagonist_name": "John",
    "fatal_flaw": "Pride",
    "the_lie": "I don't need anyone",
    "theme": "Connection requires vulnerability",
    "capabilities": ["driving", "negotiation"],
    "relationships": {"Mary": "estranged sister"}
  }
}
```

**Response:**
```json
{
  "scene_id": "ch1_s1",
  "total_score": 87,
  "grade": "A-",
  "categories": {
    "voice_authenticity": {
      "score": 26,
      "max": 30,
      "subcategories": {
        "authenticity_test": 9,
        "purpose_test": 9,
        "fusion_test": 8
      }
    },
    "character_consistency": {
      "score": 18,
      "max": 20,
      "notes": "One minor capability stretch"
    },
    "metaphor_discipline": {
      "score": 17,
      "max": 20,
      "domain_distribution": {"gambling": 3, "architecture": 2, "nature": 1}
    },
    "anti_pattern_compliance": {
      "score": 13,
      "max": 15,
      "violations_found": 2
    },
    "phase_appropriateness": {
      "score": 13,
      "max": 15
    }
  },
  "violations": [
    {
      "pattern_type": "formulaic",
      "matched_text": "walked carefully",
      "line_number": 23,
      "description": "Adverb-heavy movement",
      "penalty": 1
    }
  ],
  "metaphor_analysis": {
    "total_metaphors": 6,
    "domain_counts": {"gambling": 3, "architecture": 2, "nature": 1},
    "saturated_domains": [],
    "rotation_score": 18
  },
  "enhancement_needed": true,
  "recommended_mode": "action_prompt"
}
```

---

### POST /director/scene/compare

Analyze and rank multiple scene variants.

**Request Body:**
```json
{
  "variants": {
    "Claude": "The front door groaned...",
    "GPT-4o": "John hesitated at the threshold...",
    "DeepSeek": "Coming home meant facing..."
  },
  "pov_character": "John",
  "phase": "act2",
  "voice_bundle_path": "projects/my_project/voice_references"
}
```

**Response:**
```json
{
  "winner": "Claude",
  "rankings": [
    {"rank": 1, "model": "Claude", "score": 89, "grade": "A-", "enhancement_needed": true, "recommended_mode": "action_prompt"},
    {"rank": 2, "model": "GPT-4o", "score": 85, "grade": "A-", "enhancement_needed": true, "recommended_mode": "action_prompt"},
    {"rank": 3, "model": "DeepSeek", "score": 78, "grade": "B+", "enhancement_needed": true, "recommended_mode": "six_pass"}
  ],
  "details": {
    "Claude": { ... full analysis ... },
    "GPT-4o": { ... },
    "DeepSeek": { ... }
  }
}
```

---

### POST /director/scene/detect-patterns

Quick anti-pattern detection for real-time feedback.

**Request Body:** `scene_content` (string)

**Response:**
```json
{
  "violation_count": 3,
  "zero_tolerance_count": 0,
  "formulaic_count": 3,
  "violations": [
    {
      "pattern_type": "formulaic",
      "matched_text": "walked carefully",
      "line_number": 23,
      "description": "Adverb-heavy movement",
      "penalty": 0.5
    },
    ...
  ]
}
```

---

### POST /director/scene/analyze-metaphors

Quick metaphor domain analysis.

**Request Body:** `scene_content`, `voice_bundle_path?`

**Response:**
```json
{
  "total_metaphors": 8,
  "domain_counts": {
    "gambling": 4,
    "architecture": 2,
    "nature": 2
  },
  "saturated_domains": ["gambling"],
  "rotation_score": 15,
  "recommendations": ["Reduce gambling metaphors", "Add more variety"]
}
```

---

## Scene Enhancement

### POST /director/scene/enhance

Auto-select enhancement mode based on score and apply.

**Request Body:**
```json
{
  "scene_id": "ch1_s1",
  "scene_content": "The front door groaned...",
  "pov_character": "John",
  "phase": "act2",
  "voice_bundle_path": "projects/my_project/voice_references",
  "story_bible": { ... },
  "force_mode": null
}
```

**Response:**
```json
{
  "status": "enhanced",
  "result": {
    "scene_id": "ch1_s1",
    "mode": "action_prompt",
    "original_content": "...",
    "enhanced_content": "...",
    "original_score": 87,
    "final_score": 93,
    "action_prompt": { ... },
    "fixes_applied": [
      {"fix_number": 1, "description": "...", "status": "applied"},
      ...
    ],
    "enhanced_at": "2025-11-23T22:45:00Z"
  },
  "analysis_before": { ... }
}
```

**Mode Selection:**
- Score 85+: `action_prompt` (surgical fixes)
- Score 70-84: `six_pass` (full enhancement ritual)
- Score <70: `rewrite` (returns status "rewrite_needed")

---

### POST /director/scene/action-prompt

Generate surgical fixes without applying them.

**Request Body:**
```json
{
  "scene_id": "ch1_s1",
  "scene_content": "The front door groaned...",
  "pov_character": "John",
  "phase": "act2",
  "voice_bundle_path": "projects/my_project/voice_references"
}
```

**Response:**
```json
{
  "action_prompt": {
    "scene_id": "ch1_s1",
    "original_score": 87,
    "fixes": [
      {
        "fix_number": 1,
        "description": "Eliminate adverb-heavy movement",
        "old_text": "He walked carefully across the room",
        "new_text": "His steps measured the silence",
        "line_number": 23,
        "category": "formulaic"
      },
      ...
    ],
    "preservation_notes": [
      "Do not modify scene opening paragraph",
      "Preserve all dialogue attribution"
    ],
    "expected_score_improvement": 6
  },
  "markdown": "## ENHANCEMENT ACTION PROMPT\n\n...",
  "analysis": { ... }
}
```

---

### POST /director/scene/apply-fixes

Apply surgical fixes from an action prompt.

**Request Body:**
```json
{
  "scene_id": "ch1_s1",
  "scene_content": "The front door groaned...",
  "fixes": [
    {
      "fix_number": 1,
      "old_text": "He walked carefully across the room",
      "new_text": "His steps measured the silence",
      "description": "Eliminate adverb-heavy movement"
    },
    ...
  ]
}
```

**Response:**
```json
{
  "scene_id": "ch1_s1",
  "enhanced_content": "...",
  "fixes_applied": [
    {"fix_number": 1, "description": "...", "status": "applied"},
    {"fix_number": 2, "description": "...", "status": "not_found", "old_text_preview": "..."}
  ],
  "applied_count": 4,
  "total_fixes": 5
}
```

---

### POST /director/scene/six-pass

Force full 6-pass enhancement regardless of score.

**Request Body:**
```json
{
  "scene_id": "ch1_s1",
  "scene_content": "The front door groaned...",
  "pov_character": "John",
  "phase": "act2",
  "voice_bundle_path": "projects/my_project/voice_references",
  "story_bible": { ... }
}
```

**Response:**
```json
{
  "status": "enhanced",
  "result": {
    "scene_id": "ch1_s1",
    "mode": "six_pass",
    "original_content": "...",
    "enhanced_content": "...",
    "original_score": 78,
    "final_score": 91,
    "passes_completed": [
      {"pass_number": 1, "pass_name": "Sensory Anchoring", "changes_made": 12, "changes": ["Added concrete sensory details"]},
      {"pass_number": 2, "pass_name": "Verb Promotion + Simile Elimination", "changes_made": 8, "changes": ["Promoted verbs", "Eliminated similes"]},
      {"pass_number": 3, "pass_name": "Metaphor Rotation", "changes_made": 4, "changes": ["Rebalanced gambling"]},
      {"pass_number": 4, "pass_name": "Voice Embed (Not Hover)", "changes_made": 6, "changes": ["Embedded insights in action"]},
      {"pass_number": 5, "pass_name": "Italics Gate", "changes_made": 2, "changes": ["Reduced from 4 to 1 italics"]},
      {"pass_number": 6, "pass_name": "Voice Authentication", "changes_made": 3, "changes": ["Passed voice authentication tests"]}
    ],
    "enhanced_at": "2025-11-23T22:50:00Z"
  },
  "passes": [ ... ],
  "score_improvement": 13
}
```

**6-Pass Enhancement Ritual:**

| Pass | Name | Purpose |
|------|------|---------|
| 1 | Sensory Anchoring | Replace abstract moods with concrete sensory details |
| 2 | Verb Promotion | Make environment ACT; eliminate similes |
| 3 | Metaphor Rotation | Rebalance saturated domains |
| 4 | Voice Embed | Embed insights in action, not hovering commentary |
| 5 | Italics Gate | Limit to 0-1 italic passages per scene |
| 6 | Voice Authentication | Observer/Purpose/Fusion tests |

---

## Error Responses

All endpoints return standard HTTP error codes:

```json
{
  "detail": "Error message describing what went wrong"
}
```

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error - Processing failed |

---

## Backend Service Files

| Service | File | Purpose |
|---------|------|---------|
| Scene Analyzer | `backend/services/scene_analyzer_service.py` | 5-category scoring |
| Scaffold Generator | `backend/services/scaffold_generator_service.py` | Two-stage scaffolds |
| Scene Writer | `backend/services/scene_writer_service.py` | Multi-model variants |
| Scene Enhancement | `backend/services/scene_enhancement_service.py` | Two-mode polish |

---

*End of API Reference*
