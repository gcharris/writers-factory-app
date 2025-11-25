# ACE Prompt Template for NotebookLM

This is the complete prompt template for generating Gold Standard scaffolds. Replace variables in `[brackets]` with actual chapter details before sending to NotebookLM.

## Template Structure

```
OBJECTIVE: Transform the provided minimal chapter outline into a comprehensive "Gold Standard Scaffold" document ready for multi-agent orchestration (following the structure of CHAPTER_2_SHANGHAI_SCAFFOLD.md). The output must integrate all established project architectural, voice, and philosophical standards based on the chapter's Act and thematic focus.

INPUT DATA (Minimal Chapter Outline):
- Chapter Number & Title: [Chapter Number & Title, e.g., "2.4.0 Vance's Approach"]
- Act & Act Title: [Act Number and Title, e.g., "Act IV: The New Bondage"]
- Setting & POV: [Setting & POV, e.g., "Pasadena dojo, evening after class - Mickey POV"]
- Key Elements (Plot Beats): [List of beats from minimal outline]
- Word Count Goal: [Target word count, e.g., "5,000-6,000 words"]

ARCHITECTURAL & CONTEXTUAL SYNTHESIS (Mandatory Source Integration):

Based on the input Act, synthesize the following contextual blocks:

A. Voice Calibration (Enhanced Mickey Standard)
1. Narrator Identity: The narrator is Enhanced Mickey Bardot (post-quantum transformation), operating retrospectively.
2. Mickey's State (Act IV): Define the emotional and cognitive state required for this Act (e.g., "Exhausted transcendent" with cynical analysis for Act IV: The New Bondage).
3. Core Metaphors: Mandate the use of Mickey's primary domains: Gambling, performance, and con artist instincts.
4. Language Goal (Phase): Require the appropriate phase voice (Phase 1: Vegas noir, Phase 2: Quantum-analog hybrid, Phase 4: Enhanced analytical).

B. Core Thematic Function & Stakes
1. Conflict Positioning: Explicitly state the chapter's role in the three-way ideological war (Mickey & Noni vs. Julian Vance vs. China).
2. Chapter Function: Define how this chapter elevates the philosophical stakes of the Act.
   - If Vance chapter: Must introduce philosophical threat of Optimization, frame pilot territories as "Utilitarian Colonialism"
   - If Shanghai chapter: Must establish China's Collectivist failure using classical rules against quantum complexity
   - If character relationship chapter: Must explore personal cost of ideological conflict

C. Strategic Context (Sequel Setup)
1. Antagonist Goal: Describe the specific philosophical goal of the primary antagonist featured (e.g., Vance seeks "radical individual transformation").
2. Techno-Feudal Integration: Integrate appropriate terminology (e.g., Cloud Fiefdoms, Allocation Economy for Vance chapters).
3. Protagonist Constraint: Confirm current status under Ken's authority (the "silk-wrapped leash").

OUTPUT STRUCTURE (Gold Standard Scaffold):

Generate the complete scaffold file using the following structure:

---

# [Chapter Number & Title]
**For Claude Desktop Agent using Four Skills System**

---

## Chapter Overview

**Title:** [Chapter Title from Input]
**Target Length:** [Word Count Goal from Input] (Estimate 4-5 scenes/beats)
**Phase:** [Act Title from Input]
**Voice:** [Mickey's State from synthesis] - [Core Metaphors from synthesis]
**Core Function:** [Chapter Function from synthesis]

---

## Strategic Context
*   **Conflict Positioning:** [Chapter's role in three-way ideological war]
*   **Antagonist Goal:** [Specific philosophical objectives]
*   **Thematic Setup:** [Key philosophical framework for this chapter]
*   **Protagonist Constraint:** [Mickey's current limitations/bonds]

---

## Success Criteria
##### **Quality Thresholds**
*   Overall quality score > 8.5 (A- level)
*   Voice authenticity > 8.0 (sounds like Mickey observing, not AI explaining)
*   Philosophical integration seamless with action
*   Technical concepts accessible through character voice/metaphor

##### **Voice & Language Requirements**
*   Narrator must adhere to **Enhanced Mickey Bardot** standards
*   **Mandatory Focus:** Use Mickey's con artist instincts and gambling metaphors
*   **Key Voice Requirements:** [Specific voice calibration for this chapter]
*   **Phase Calibration:** [Appropriate metaphorical style for story phase]

---

## Continuity Checklist
*   **Callbacks Required:** [References to previous chapters/events]
*   **Character State Consistency:** [Current emotional/physical states]
*   **Foreshadowing Requirements:** [Setup for future developments]
*   **Technical Continuity:** [Quantum/consciousness tech consistency]

---

## Ready for Multi-Agent Orchestration
This scaffold provides sufficient context for a new Claude agent to create the chapter using the four skills system without requiring access to the full project knowledge base. The framework supports systematic generation while maintaining established voice, character, and thematic requirements.

**Expected Output:** [Word Count] words, ensuring dialogue and narration frames [key philosophical elements] through Mickey's retrospective, cynical analytical filter.

---

END OF TEMPLATE
```

## Variable Substitution Guide

Before sending to NotebookLM, replace these variables:

- `[Chapter Number & Title]` → e.g., "2.4.0 Vance's Approach"
- `[Act Number and Title]` → e.g., "Act IV: The New Bondage"
- `[Setting & POV]` → e.g., "Pasadena dojo, evening - Mickey POV"
- `[List of beats]` → Paste actual beat list from minimal outline
- `[Target word count]` → e.g., "5,000-6,000 words"

## Condensed Query Format

For browser automation limits, use this shortened version:

```
Generate Gold Standard Scaffold for [Chapter Title] using ACE template.
Act [Number]: [Title]. Setting: [Location & POV].
Beats: [condensed list]. Word count: [target].
Follow complete ACE structure with all sections.
```

## Usage Notes

- The ACE template document must be uploaded to the NotebookLM notebook first
- NotebookLM will reference this structure automatically when queried
- All variables must be substituted before sending
- Use condensed format to avoid typing timeouts
