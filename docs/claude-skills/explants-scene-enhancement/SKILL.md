---
name: explants-scene-enhancement
description: Complete narrative editing framework for The Explants novel using Enhanced Mickey voice system. Applies surgical fixes, voice authentication, and technical craft while preserving original compressed phrasing and character-specific voice.
---

# Scene Enhancement for The Explants

## Input Mode Detection

**This skill supports TWO input modes:**

### MODE A: Action Prompt (Surgical Fix Application)
**Input:** Action prompt file or text containing `## ENHANCEMENT ACTION PROMPT` header
**Process:** Apply specified fixes only, preserve all other content
**Output:** `[scene-name] [enhanced].md` in original directory
**References:** NOT required (fixes pre-specified, context included in prompt)

**Detection:**
- File path contains `-action-prompt.md`, OR
- Text contains header: `## ENHANCEMENT ACTION PROMPT` or `# ENHANCEMENT ACTION PROMPT`

**Workflow:**
1. Parse action prompt for target scene path
2. Load target scene file
3. Apply fixes sequentially using string matching
4. Verify preservation instructions followed
5. Output enhanced version with `[enhanced]` suffix

### MODE B: Full Scene Enhancement (Traditional Workflow)
**Input:** Raw scene file or scene text
**Process:** Full diagnostic + enhancement using 6-pass ritual
**Output:** `[scene-name] [enhanced].md` in original directory
**References:** REQUIRED (Gold Standard, Anti-Pattern Sheet, Scene-Polishing-Ritual)

**Detection:**
- File path ends in `.md` and does NOT contain `-action-prompt`, OR
- Text does NOT contain action prompt header

**Workflow:**
1. Load reference files (Gold Standard, Anti-Pattern Sheet, Scene-Polishing-Ritual)
2. Apply 6-Pass Enhancement Ritual (diagnostic integrated in passes)
3. Output enhanced version with `[enhanced]` suffix

---

**AUTO-DETECTION:** Skill automatically determines mode based on input. No user selection needed.

---

## Quick Setup

**FIRST: Detect Input Mode**

Check if input is:
- ✅ **Action Prompt:** Contains `## ENHANCEMENT ACTION PROMPT` header or filename ends in `-action-prompt.md`
  → **Skip to:** Action Prompt Application Mode
  → **References:** Not required (fixes pre-specified)

- ✅ **Raw Scene:** Regular `.md` file or scene text without action prompt header
  → **Continue below:** Load references and proceed with full enhancement

**MANDATORY PRE-ENHANCEMENT (Raw Scene Mode Only):**
Load from references folder:
1. **`references/Mickey-Bardot-Enhanced-Trilogy-Voice-Gold-Standard.md`** (primary voice authority)
2. **`references/Mickey Voice Anti-Pattern Sheet.md`** (failure patterns)
3. **`references/metaphor-domains.md`** (rotation strategy)

**Note:** These files contain essential voice rules and must be consulted before enhancement.

---

## Action Prompt Application Mode

**Use when:** Input detected as action prompt (contains header or filename pattern)

### STEP 1: Parse Action Prompt
Locate the following sections in the action prompt:
- `## TARGET SCENE` → Extract exact file path
- `## FIXES TO APPLY` → Extract each FIX block with OLD/NEW strings
- `## CRITICAL: DO NOT MODIFY` → Extract preservation instructions
- `## VERIFICATION CHECKLIST` → Extract success criteria

### STEP 2: Archive Original FIRST (CRITICAL - Data Loss Prevention)

**BEFORE MAKING ANY MODIFICATIONS:**

1. **Extract scene directory and filename** from TARGET SCENE path
2. **Create Archive subdirectory** if it doesn't exist: `[PART-directory]/Archive/`
3. **Copy original to Archive** BEFORE any edits:
   ```
   cp "[scene-name].md" → "Archive/[scene-name] [original].md"
   ```
4. **Verify archive copy exists** and is readable

**WHY THIS ORDER IS CRITICAL:**
- ✅ Preserves true original before any modifications
- ✅ No dependency on git for recovery
- ✅ Safe rollback if enhancement fails
- ✅ Truly non-destructive workflow

**NEVER:**
- ❌ Apply fixes before archiving original
- ❌ Rely on git to recover original
- ❌ Modify file before preserving it

**If archive fails:** Report error and HALT - do not proceed with modifications.

---

### STEP 3: Load Target Scene
Read the scene file specified in TARGET SCENE section.
**Verify:** File exists and is readable. If not found, report error and halt.

### STEP 4: Apply Fixes Using String Matching
For each FIX in order:

**CRITICAL:** Use OLD string for matching, NOT line numbers. Line numbers are reference only.

1. **Locate:** Search scene for exact OLD string
   - Use LOCATE section for context verification
   - If OLD string not found, report error and continue to next fix

2. **Replace:** Replace OLD with NEW using string matching
   - Preserve surrounding context exactly
   - One replacement per fix (don't replace all instances unless specified)

3. **Log:** Record fix application: `[✓] FIX N: [brief description]`

**Error Handling:** If OLD string not found, log `[✗] FIX N: OLD string not found - skipping` and continue.

### STEP 5: Verify Preservation
Check that elements listed in `## CRITICAL: DO NOT MODIFY` section remain unchanged:
- Search for each preserved element in enhanced scene
- Verify exact match to original
- Log: `[✓] Preserved: [element description]` or `[✗] Modified: [element description]`

### STEP 6: Run Verification Checklist
Execute each item in `## VERIFICATION CHECKLIST`:
- Pattern searches (e.g., regex for remaining violations)
- Count checks (e.g., all N fixes applied)
- Functional checks (e.g., scene still accomplishes purpose)
- Log results for each item

### STEP 7: Rename Enhanced File with Checkmark
After all fixes applied and verified:
1. **Rename enhanced file** to add checkmark indicator:
   ```
   mv "[scene-name].md" → "[scene-name] [✓].md"
   ```
2. **Verify final structure:**
   - Enhanced (canonical): `[PART-directory]/[scene-name] [✓].md`
   - Original (archived): `[PART-directory]/Archive/[scene-name] [original].md`
   - Action prompt: `[PART-directory]/Archive/[scene-number]-action-prompt.md`

### STEP 8: Report Results
Output in chat:

```markdown
# Enhancement Complete: [Scene Name]

## Applied Fixes: N/N successful
[✓] FIX 1: [description]
[✓] FIX 2: [description]
[✗] FIX 3: [description] - OLD string not found

## Preservation Check: N/N preserved
[✓] Lines XX-XX: [element description]
[✓] Line XX: [element description]

## Verification Results:
[✓] Pattern search: 0 violations detected
[✓] All fixes applied successfully
[✓] Scene function preserved

## Output:
**File created:** [path to enhanced file]
**Expected score improvement:** XX → XX (+N points)

## Notes:
[Any warnings, errors, or observations from the enhancement process]
```

---

## Core Workflow: Surgical Fix Method

**Use when:** Input is raw scene file (MODE B - Full Enhancement)

### PHASE 1: Diagnostic Only (Don't Change Anything)
Read scene completely. Mark ONLY genuinely broken elements:
- [ ] Weak similes ("like punctured tires")
- [ ] Formulaic patterns ("with [adjective] [noun]")
- [ ] Missing sensory details (abstract paragraphs)
- [ ] Academic voice drift (AI explaining Mickey vs Mickey thinking)

**Rule:** If you can't articulate WHY it's broken, don't touch it.

### PHASE 2: Preservation Check
For every marked phrase, ask:
- [ ] Is it compressed/punchy? → PRESERVE
- [ ] Is it character-specific voice? → PRESERVE  
- [ ] Is it quirky/memorable? → PRESERVE
- [ ] Does it serve story function? → PRESERVE

**Only proceed if:** "This is genuinely broken because..."

### PHASE 3: Surgical Fixes Only
Fix only what survived preservation check:
- Convert weak similes to direct metaphors
- Eliminate formulaic patterns
- Add sensory anchoring where missing
- Embed philosophy in concrete observation

### PHASE 4: Pattern Audit
Execute mandatory searches (see references/pattern-audit-procedures.md):
- "with precision" → Must be 0 instances
- "with [adjective] [noun]" → Embed in verbs
- Academic meta-commentary → Convert to embedded observation

---

## 6-Pass Enhancement Ritual

### Pass 1: Sensory Anchoring
Replace abstract moods with concrete details: air, light, texture, sound, smell.
**Target:** 3 sensory anchors per scene section.

### Pass 2: Verb Promotion + Simile Elimination  
Make environment act: "lobby air wheezed," "architecture confessed"
**Convert similes:** " like " → direct metaphors using literal-metaphorical reality.

### Pass 3: Metaphor Rotation
**Domain balance:** No domain >40% of total metaphors.
**Gambling limit:** Max 2-3 per scene.
**Force rotation:** performance, addiction, martial arts, surveillance, music.

### Pass 4: Voice Embed, Not Hover
Delete sentences that "explain" what previous sentence showed.
**Test:** Is insight embedded in action or floating above it?

### Pass 5: Italics Gate
**Goal:** 0-1 italics maximum per scene.
**Keep for:** QBVs, character arc moments, earned wisdom.
**Delete:** Repetitive explanations of what prose showed.

### Pass 6: Voice Authentication (CRITICAL)
**Three required tests:**
1. **Observer Test:** Mickey thinking vs AI explaining Mickey?
2. **Consciousness War Test:** Serves philosophical argument?
3. **Cognitive Fusion Test:** Analytical precision + cynical wisdom?

**See references/voice-authentication-tests.md for detailed criteria.**

---

### Pass 7: QBV Progression & Transformation Voice (IF APPLICABLE)

**Apply when:** Scene includes transformation or quantum capability emergence (Chapters 19-21)

**Check for:**
1. **QBV progression appropriate to phase:**
   - Pre-transformation (Ch 19-20): 2-3 instances showing quantum sensitivity emerging
   - Crisis (Interval): Identity recursion + system interface capability manifesting
   - Reconstruction: Harmonic reintegration + quantum clarity emerging

2. **Mickey's domains maintained throughout:**
   - Gambling/casino metaphors for enhanced pattern recognition
   - Performance/stage metaphors for identity layer navigation
   - Music/rhythm metaphors for consciousness self-organization
   - Recovery wisdom for surrender/transformation acceptance

3. **Capability emergence (not contamination):**
   - Technical language emerging from Mickey's expanding awareness
   - Consciousness architecture becoming visible through quantum capability
   - Integration feels earned through established QBV foundation
   - Process-over-noun philosophy emerging from direct perception

**Reference:** `references/qbv-progression-techniques.md`

---

### Pass 8: Italics Protocol Verification (ALL SCENES)

**Check for:**
1. **Pre-integration italics usage (Ch 1-20):**
   - QBVs in italics (edge bleeding, intensification phases)
   - Transformation interval: NO italics (lived reality, not vision)

2. **Post-integration italics violations (Ch 21+):**
   - ❌ Routine quantum awareness italicized
   - ❌ Bi-location operations italicized
   - ❌ Technical analysis italicized

3. **Post-integration italics reserved for:**
   - ✅ Transcendence beyond enhanced baseline
   - ✅ Major retrospective insights (trilogy-level)
   - ✅ Critical character/plot turning points

**Reference:** `references/italics-evolution-framework.md`

---

## Essential Anti-Patterns

**Voice Killers (Zero Tolerance):**
- ❌ Academic meta-commentary ("Enhanced perspective providing analysis")
- ❌ Philosophy floating above action (embed in concrete observation)
- ❌ "with [adjective] [noun]" patterns → embed in verbs
- ❌ Casino saturation (max 2-3 gambling metaphors)
- ❌ First-person italics (*We* → *Mickey*)

**Preservation Override Examples (NEVER change):**
- ✅ "Trevor was chill. House always gets its cut." (compressed voice)
- ✅ "precision of a man counting down minutes to his smoke break" (character insight)
- ✅ "Instant silhouette blur" (compressed action)

---

## Strategic "Enhanced" Usage

**PRESERVE "Enhanced" for:**
- Analytical authority: "Enhanced perspective recognized the pattern"
- POV distance: "Enhanced Mickey understood what analog Mickey couldn't"
- Technical analysis: "Enhanced awareness monitored operations"

**SUBSTITUTE with:**
- "Quantum consciousness" (ongoing action)
- "Mickey's awareness" (embedded voice)
- Direct observation (when voice should be natural)

**See references/enhanced-strategy-advanced.md for complete guide.**

---

## Output Format

### 1. Enhanced Scene (as markdown artifact)
- Clean prose only, ready to replace original
- Original filename maintained
- No diagnostic headers or analysis

### 2. Diagnostic Report (in chat)
- **Phase 1:** Problems identified
- **Phase 2:** What was preserved and why
- **Phase 3:** Changes made with examples
- **Phase 4:** Pattern audit results
- **Phase 6:** Voice authentication test results

---

## Reference Materials

**Detailed guides in references folder:**
- `Mickey-Bardot-Enhanced-Trilogy-Voice-Gold-Standard.md` - Primary benchmark (PRIMARY)
- `voice-authentication-tests.md` - Complete test criteria and examples
- `pattern-audit-procedures.md` - All mandatory searches with examples
- `enhanced-strategy-advanced.md` - Strategic "Enhanced" usage

**Quality benchmark:** Authentic Mickey voice serving consciousness war argument through concrete cynical observation.

**Success metric:** Scene passes voice authentication tests and sounds like Mickey thinking, not AI describing Mickey's thoughts.
