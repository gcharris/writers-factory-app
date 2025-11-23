# Troubleshooting Guide

Common issues and solutions for the Smart Scaffold Generator.

## NotebookLM Connection Issues

### Authentication Failures
**Symptoms:**
- "Authentication failed" errors
- Can't access notebook list
- Permission denied messages

**Solutions:**
```bash
# Re-authenticate
cd ~/.claude/skills/notebooklm && python scripts/run.py auth_manager.py login

# Check current status
cd ~/.claude/skills/notebooklm && python scripts/run.py auth_manager.py status

# Clear auth cache if needed
cd ~/.claude/skills/notebooklm && python scripts/run.py auth_manager.py logout
cd ~/.claude/skills/notebooklm && python scripts/run.py auth_manager.py login
```

### Wrong Notebook Active
**Symptoms:**
- Scaffold generation returns irrelevant content
- Missing Explants-specific terminology
- No architectural context

**Solutions:**
```bash
# List all notebooks
cd ~/.claude/skills/notebooklm && python scripts/run.py notebook_manager.py list

# Switch to correct notebook
cd ~/.claude/skills/notebooklm && python scripts/run.py notebook_manager.py switch [NOTEBOOK_ID]

# Verify correct notebook is active
cd ~/.claude/skills/notebooklm && python scripts/run.py notebook_manager.py current
```

## Query and Response Issues

### Typing Timeout Errors
**Symptoms:**
- "Timeout 30000ms exceeded" during query
- Browser automation fails during typing
- Query cuts off mid-send

**Solutions:**
- **Use condensed query format** (< 500 characters)
- **Reference ACE template in notebook** instead of including full prompt
- **Break into multiple shorter queries** if needed
- **Verify browser window is active** during automation

**Example Fix:**
```
# Instead of full ACE prompt (2000+ chars)
Generate Gold Standard Scaffold for Chapter 4: Vance's Approach using ACE template.
Act IV: The New Bondage. Setting: Pasadena dojo, Mickey POV.
Beats: Vance arrives, acknowledges pioneers, pilot territories, precision management.
5,000-6,000 words.
```

### Incomplete Scaffold Output
**Symptoms:**
- Missing required sections (Strategic Context, Continuity)
- Generated scaffold ends abruptly
- No multi-agent readiness statement

**Solutions:**
1. **Verify ACE template** is uploaded to notebook
2. **Request completion** with follow-up query:
   ```
   Complete the scaffold with Strategic Context and Continuity Checklist sections.
   ```
3. **Ask for missing sections explicitly:**
   ```
   Add the missing Success Criteria and Multi-Agent Orchestration sections.
   ```
4. **Use completion prompt:**
   ```
   Is that ALL you need for a complete Gold Standard scaffold?
   ```

## Quality Issues

### Generic/Shallow Output
**Symptoms:**
- No specific philosophical terminology
- Generic character descriptions
- Missing Explants-specific context
- Sounds like generic story outline

**Root Causes & Solutions:**

**Missing Architectural Documents:**
- **Check:** Notebook contains master planning documents
- **Fix:** Upload architectural blueprints, nine-act structure
- **Test:** Query should reference specific Act functions

**No Character Profiles:**
- **Check:** Character state documents in notebook
- **Fix:** Add detailed profiles with current Act states
- **Update:** Reflect latest character development

**Missing Voice Guidelines:**
- **Check:** Enhanced Mickey voice standards uploaded
- **Fix:** Add complete voice documentation
- **Include:** Anti-patterns, metaphor domains, phase requirements

### Wrong Philosophical Terminology
**Symptoms:**
- Generic terms instead of "Utilitarian Colonialism"
- Missing "Vector Beta/Gamma" references
- No consciousness war concepts
- Generic good vs. evil framing

**Solutions:**
1. **Upload philosophical framework documents**
2. **Add consciousness war ideology documents**
3. **Include three-vector system documentation**
4. **Verify terminology consistency** across uploaded docs
5. **Add glossary document** defining key terms

### No Continuity Callbacks
**Symptoms:**
- No references to Volume 1 events
- Missing previous chapter connections
- Character states don't reflect story progression
- Disconnected from trilogy arc

**Solutions:**
1. **Upload Volume 1 complete manuscript**
2. **Add completed Volume 2 chapters** (replace scaffolds with final prose)
3. **Include character relationship history**
4. **Explicitly request continuity** in query:
   ```
   Include callbacks to Volume 1 events and Chapter 2 Shanghai chaos.
   ```

## Input Quality Issues

### Insufficient Minimal Outline
**Symptoms:**
- Vague beat descriptions
- Missing critical context
- No clear character actions
- Generic plot points

**Solutions:**
- **Expand beat descriptions** with specific actions
- **Include character emotional states** in outline
- **Add technical/philosophical elements** relevant to chapter
- **Specify key relationships** and conflicts

**Example Improvement:**
```
# Weak outline
Beats: Vance arrives, talks to Mickey, makes offer

# Strong outline  
Beats: Vance arrives (radiating authority), acknowledges "pioneers," 
references "pilot territories," philosophy of precision management, 
invitation to see "functional transcendence"
```

### Wrong Variable Substitution
**Symptoms:**
- Template variables not replaced in query
- NotebookLM returns template instead of content
- Scaffold contains `[Chapter Title]` placeholders

**Solutions:**
- **Verify all variables substituted** before sending query
- **Double-check bracket replacements:** `[Chapter Number & Title]` → `2.4.0 Vance's Approach`
- **Use exact format** from ACE template
- **Test with known working example** first

## Integration Issues

### Scene Writer Can't Use Scaffold
**Symptoms:**
- Scene writer skill doesn't recognize scaffold
- Generated scenes ignore scaffold context
- Missing voice or character requirements

**Solutions:**
1. **Verify scaffold file naming:** `CHAPTER_[X]_[TITLE]_SCAFFOLD.md`
2. **Check file location** (same directory as minimal outline)
3. **Validate scaffold structure** against quality checklist
4. **Ensure multi-agent readiness statement** present
5. **Test handoff** with explicit file path

### Poor Scene Quality from Scaffold
**Symptoms:**
- Generated scenes don't match scaffold requirements
- Voice authenticity issues
- Missing philosophical integration

**Root Causes & Solutions:**

**Inadequate Voice Requirements:**
- **Check:** Voice section embedded in Success Criteria
- **Fix:** More specific voice calibration in scaffold
- **Include:** Phase-appropriate metaphor domains

**Missing Character Context:**
- **Check:** Detailed character emotional states
- **Fix:** More specific character context section
- **Include:** Current relationships and constraints

**Weak Philosophical Integration:**
- **Check:** Clear consciousness war positioning
- **Fix:** Stronger thematic setup and requirements
- **Include:** Specific terminology mandates

## Performance Issues

### Slow Query Response
**Symptoms:**
- NotebookLM takes >60 seconds to respond
- Browser appears to freeze during query
- Long processing times

**Solutions:**
- **Use shorter, condensed queries**
- **Ensure stable internet connection**
- **Close unnecessary browser tabs**
- **Try during off-peak hours**
- **Consider upgrading to NotebookLM paid tier**

### Rate Limiting
**Symptoms:**
- "Too many requests" errors
- Query rejection after multiple attempts
- Daily limit exceeded messages

**Solutions:**
- **Free tier limit:** 50 queries/day
- **Batch scaffold generation** to minimize queries
- **Plan query usage** for heavy generation sessions
- **Consider upgrading** to paid tier for higher limits
- **Space out queries** if near limit

## Error Recovery

### Complete Failure Recovery
If the skill completely fails:

1. **Start fresh:** Clear authentication and re-login
2. **Verify notebook:** Ensure correct notebook with all documents
3. **Test with known example:** Use Chapter 4: Vance's Approach
4. **Compare output:** Against reference scaffold quality
5. **Document the issue:** For future troubleshooting

### Partial Failure Recovery
If scaffold is generated but poor quality:

1. **Follow-up queries** to add missing sections
2. **Manual editing** to fix obvious issues
3. **Regenerate** with improved minimal outline
4. **Update notebook** with missing documents
5. **Validate against checklist** before use

## Prevention Best Practices

### Setup Prevention
- Always upload ACE template first
- Test with known working example
- Verify all architectural documents present
- Use descriptive file names in notebook
- Regular maintenance schedule

### Query Prevention
- Use condensed format to avoid timeouts
- Substitute all variables before sending
- Test query format with simple example
- Keep beat descriptions specific and actionable
- Include key philosophical elements in outline

### Quality Prevention
- Regular notebook audits
- Update character states as story progresses
- Replace scaffolds with final prose
- Maintain terminology consistency
- Test output against quality checklist

## Getting Help

### Escalation Path
1. **Check this troubleshooting guide**
2. **Review reference documentation**
3. **Compare against working examples**
4. **Test with minimal case**
5. **Document specific error patterns**

### Information to Gather
- Error messages (exact text)
- Query used (anonymized if needed)
- NotebookLM notebook status
- Expected vs. actual output
- Recent changes to notebook or setup
