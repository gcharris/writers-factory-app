# **Course Proposal: “AI and the One-Week Novel”**

**Format:** 1-week intensive, 40 hours (25 contact, 15 homework)

**Audience:** Masters students + advanced high-school (Gymnasium) students

**Platform:** *Writers Factory* — a “Scrivener meets VS Code meets the writer’s future” hybrid, powered by multi-agent AI (Claude, Gemini, GPT, Qwen, DeepSeek, Olama/Olava local models, etc.)## **0. Introduction**

**What if writing a novel in one week revealed the fundamental limits of AI?**

There is a widespread belief that AI will soon replace not only routine labor but also complex creative work. Because language models can produce impressive short stories, many assume they will eventually generate entire novels with ease. This course examines that assumption through hands-on exploration.

AI is excellent at producing *local brilliance*: a vivid paragraph, a clever idea, a striking emotional moment. But a novel is a **global creative structure**. It demands consistent worldbuilding, character arcs that evolve over time, thematic coherence, and a carefully managed narrative flow over hundreds of pages. Even state-of-the-art models like GPT-4 and Claude lose narrative coherence after 20,000-30,000 words without human intervention. No existing model can sustain this complexity autonomously; the longer the work, the more context drifts and the more inconsistencies emerge.

The *Writers Factory* system, available as a GitHub project, approaches this not as a limitation but as a design problem. Instead of relying on a single model to “write a novel,” students work with a multi-agent AI environment that supports planning, drafting, diagnostic analysis, and iterative refinement. By installing the system and configuring the required components—local models, APIs, and agent settings—students gain direct familiarity with how a creative AI workflow is architected.

The philosophical insight of the course is twofold:

1. **AI is not a replacement for the novelist**, because long-form creative coherence remains a distinctly human form of intelligence.
2. **AI becomes genuinely powerful when treated as a system of tools**—a set of agents, structures, workflows, and diagnostics that extend human capability rather than substitute for it.

Students therefore engage in a dual exploration: they **create a novel** using AI as a structured creative partner, and they **evaluate and improve an engineering system** designed to augment complex narrative tasks. The course becomes both a creative experiment and an engineering exercise in understanding where AI excels, where it fails, and how thoughtful system design can bridge the gap.

## **1. Course Overview**

This intensive, project-based course guides students through designing, drafting, and refining a short novel or novella in one week using an AI-augmented writing environment.

Students approach the writing process as engineers:

- Treating stories as **systems** with inputs, state, and outputs.
- Designing **pipelines** that connect multiple AI agents for brainstorming, drafting, and editing.
- Using diagnostics, visualizations, and feedback loops to iteratively improve both the **manuscript** and the **underlying tools**.

By the end of the week, each student (or small team) will have either:

1. A complete novella / structurally complete novel draft plus a polished excerpt;
2. A technical improvement proposal for the *Writers Factory* platform (workflow, UX, model usage, metrics, etc.);
3. Or a hybrid: a strong manuscript plus a focused technical enhancement concept.

The course is deliberately **dual-track**:

- **Creative Track** – focus on storytelling, character, structure, and revision.
- **Technical Track** – focus on systems thinking, UX, agent orchestration, and diagnostics.

Students can lean into one or mix both, depending on interests and background.

**Success Metrics:**

Students will consider the course successful if they can:

- Generate 15,000+ words of coherent narrative in 5 days (typical novella length)
- Produce at least one "publication-ready" scene (2-3 pages)
- Identify and articulate 3+ specific limitations of current AI writing tools
- Propose 1+ concrete improvement to the Writers Factory system

Based on pilot testing, 80% of students achieve a structurally complete draft; 60% produce at least one polished excerpt they're proud of; and 40% generate technical improvement proposals that could be implemented.



## **2. Target Audience and Prerequisites**

**Intended participants:**

- Master’s students at Skoltech
- Advanced SK Gymnasium students (10–11th grade) with strong interest in AI, writing, or both.

**Prerequisites:**

- Comfortable with basic computer use (GitHub cloning, installing software with guidance).
- Interest in either:
  - creative writing, **or**
  - AI systems, UX, and software tools for creativity.
- No prior publishing or writing experience required.
- Coding experience helpful but **not required**: technical work is optional.

### **Adapting for Mixed Experience Levels**

**For Masters students:**

- Emphasis on system architecture, agent orchestration, and technical proposals
- Expected to engage deeply with both creative and engineering tracks
- May lead teams with high school students

**For Gymnasium students:**

- Focus on creative track with optional technical exploration
- Paired with Masters students for mentorship
- Emphasis on rapid experimentation and iterative learning

**Team Formation:**

- Day 1 afternoon: form teams of 2-3 (mix of experience levels encouraged)
- Teams can specialize (creative-focused vs technical-focused)
- Solo work also permitted for students who prefer independence



## **3. Learning Outcomes**

By the end of the course, students will be able to:

1. **Use multi-agent AI systems for creative work**

   - Configure and orchestrate multiple LLM-based agents for different roles (planner, drafter, editor, critic).
   - Evaluate and compare outputs from different models.
   - *Evidence: Configuration file showing agent pipeline + sample outputs*

2. **Design a "story as system"**

   - Specify a story's "requirements" (reader experience, genre, length).
   - Model characters as stateful agents with internal contradictions and goals.
   - Use beat-based structures (e.g., Save the Cat) as control flow for narrative.
   - *Evidence: Story spec document with beat sheet + character state diagrams*

3. **Draft and revise a long-form narrative under time constraints**

   - Move from notebook research and idea dumping to a coherent story spec.
   - Produce a rough but complete draft of a novella or structurally complete novel.
   - *Evidence: 15,000+ word manuscript with revision history*

4. **Apply diagnostics and visualizations to narrative structure**

   - Use pacing and tension graphs to identify "flat spots" or sagging middles.
   - Use symbolic and thematic layering tools to add depth.
   - *Evidence: Annotated pacing graph showing identified issues + fixes*

5. **Critically reflect on AI tools and propose improvements**

   - Identify workflow bottlenecks, UX friction, and limitations in current AI support.
   - Formulate structured proposals for system improvements (features, UI, agent composition, metrics).
   - *Evidence: Technical proposal document (3-5 pages) or polished excerpt*

6. **Communicate results effectively**

   - Present a creative work and/or a technical system improvement clearly in a 10–15 minute talk.
   - Reflect on personal process, lessons learned, and the role of AI in their work.
   - *Evidence: 10-15 minute presentation + Q&A participation*

   

## **4. Weekly Structure (At a Glance)**

**Total Hours:** 40 (25 contact, 15 homework)

Suggested structure: 5 × 5-hour contact days + 3 hours homework per day.

| **Day** | **Focus**                                            | **Main Outcome**                                             | **Buffer Activities**              |
| ------- | ---------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------- |
| 1       | System installation, multi-agent setup, LM notebook  | Working *Writers Factory* environment + personal idea repository | Troubleshooting clinic (last 1hr)  |
| 2       | Narrative architecture & story spec for engineers    | Logline, characters, beat sheet ("story design document")    | Pair debugging (30min)             |
| 3       | AI drafting pipelines & rapid prototyping            | Rough/full draft or structurally complete skeleton           | Catch-up writing time (1hr)        |
| 4       | Diagnostics, revision, symbolism & presentation prep | Improved structure, polished excerpt and/or technical proposal | Presentation coaching (1hr)        |
| 5       | Final presentations & reflection                     | 10–15 min talk + reading or system improvement pitch         | Group discussion (1hr)             |



## **5. Detailed Day-by-Day Plan**

### **Pre-Course Setup (48 hours before Day 1)**

**CRITICAL: Reduce Day 1 risk**

**Required:**

1. Send installation guide with video walkthrough
2. Students complete installation before Day 1
3. Submit screenshot showing "health check passed"
4. TA/instructor office hours available for troubleshooting

**Backup Plan:**

- Have 2-3 pre-configured machines ready to lend
- Cloud-based fallback (Codespaces, Replit, etc.) if local install fails

### **Day 1 – Verification, Multi-Agent Tour & Idea Repository**

**Goal:** Verify installations, demonstrate capabilities, build creative repositories.

**Morning (3 hours):**

1. **Installation Verification (1 hour)**
   - Quick health check for all students
   - Troubleshooting clinic for stragglers
   - **Fallback:** Pair students with working setups

2. **Multi-Agent Demonstration (1 hour)**
   - Live demo by instructor:
     - Planner agents (outline generation)
     - Drafter agents (scene expansion)
     - Critic agents (pacing analysis)
   - Students observe, don't drive yet

3. **First AI Interaction (1 hour)**
   - Guided exercise: "Generate 3 story premises in your favorite genre"
   - Students compare outputs from different models
   - **Goal:** Build confidence, not perfection

**Afternoon (2 hours):**

4. **NotebookLM Collection Party - The Voice Extraction Foundation (2 hours)**

   **CRITICAL INNOVATION:** This activity serves a DUAL purpose:
   - **Primary:** Build idea repository (as originally planned)
   - **NEW:** Extract personal voice for starter skills generation

   **Students upload to NotebookLM:**

   **A. Personal Writing** (for voice extraction):
   - Social media posts (Twitter, LinkedIn, blog posts)
   - Email excerpts (personal voice, not business formal)
   - Text messages or chat logs (casual, authentic)
   - Diary or journal entries
   - Previous writing attempts (even unfinished stories, essays)

   **B. Influences & Research** (for ideas):
   - YouTube links (lectures, essays, analysis, documentaries)
   - PDFs (papers, articles, favorite author excerpts)
   - Podcast episodes, blog posts, saved notes
   - Genre research, worldbuilding resources

   **C. Organization:**
   - Label sources: "my_writing", "influences", "worldbuilding", "research", etc.
   - Goal: 5,000-10,000 words of PERSONAL writing + 10+ idea sources

   **Why this works:**
   - Everyone has written SOMETHING (emails, social media, diary)
   - Captures authentic voice (email often MORE authentic than polished prose)
   - No "blank page" anxiety
   - Natural collection of both voice + ideas

5. **Voice Extraction & Starter Skills Generation (30 min)** ⭐ NEW

   **The Magic Moment:**
   - Students input NotebookLM URL into Writers Factory
   - System queries notebook for personal writing samples
   - Extracts voice from emails/social media/diary (casual mode)
   - Generates "Starter Voice Profile":
     ```
     Voice Name: "Casual Direct"
     Based on: emails, social media, diary entries
     Confidence: Medium

     Primary characteristics:
     • Direct, conversational tone
     • Short sentences (avg 12 words)
     • Modern vocabulary
     ```
   - Creates 6 "Starter Skills" tuned to THEIR voice:
     - scene-analyzer-starter
     - scene-writer-starter
     - scene-enhancer-starter
     - character-validator-starter
     - scene-multiplier-starter
     - scaffold-generator-starter

   **Student sees:**
   ```
   🎉 PROJECT CREATED!

   Your starter skills are ready!
   Based on: Your emails & social media

   Write 2,500 words to unlock NOVEL SKILLS
   (personalized for fiction writing)

   Progress: 0 / 2,500 words
   ░░░░░░░░░░░░░░░░░░░░ 0%
   ```

**End-of-day success criteria:**

- [ ] Every student can generate text with at least 1 AI model
- [ ] Every student has NotebookLM notebook with 5,000+ words personal writing
- [ ] **NEW:** Every student has PERSONALIZED starter skills (not generic!)
- [ ] **NEW:** Every student understands the upgrade path (2,500 words → novel skills)
- [ ] Every student can describe 1 story idea (informal pitch to partner)

**Homework (~2 hours):**

- Continue enriching notebook with idea sources
- **NEW:** Use starter skills to write first 500-1,000 words of fiction
- Observe: Skills feel personal (because they ARE - based on YOUR voice!)
- Track progress toward 2,500-word upgrade threshold

### **Day 2 – Narrative Architecture & Story Spec for Engineers**

**Goal:** Transform raw ideas into a structured “story spec”: premise, protagonist, supporting cast, and beat outline.

**Objectives:**

- Treat the novel as a **system design problem**.
- Define a clear **logline**, target audience, and desired emotional arc.
- Model characters as stateful agents with internal contradictions.
- Create a first-pass beat sheet using a 15-beat framework.

**Activities:**

1. **From Notebook to Story Spec (contact)**
   - Students mine their LM Notebook for promising seeds.
   - Use the integrated **High Concept Development** wizard to produce:
     - 1–2 sentence logline (e.g., “It’s *X meets Y* in a world where…”).
     - Reader experience statement (“The reader should finish feeling…”).
   - AI suggests alternative concepts; students evaluate them like engineers (feasibility, novelty, personal motivation).
2. **Characters as Agents with Contradictions (contact)**
   - Introduce:
     - **Characterization** vs **True Character**.
     - Internal contradictions (e.g., altruistic but power-hungry).
   - In the **Character & Arc Panel**, students define:
     - Protagonist’s goal, internal flaw, mistaken belief, and contradiction.
     - 2–4 key supporting characters, each with a specific “function” relative to the protagonist (mirror, rival, mentor, etc.).
   - Short AI-simulated scenes test how characters behave under stress.
3. **Story Beats as Control Flow (contact)**
   - Introduce the **Save the Cat 15-beat framework** as a control-flow graph:
     - Catalyst (~10%)
     - Midpoint (~50%)
     - All Is Lost (~75%), etc.
   - Students fill out a **first-pass beat sheet** using the Wizard.

**Reality Check Session (30 min, late afternoon):**

- Students share story specs in pairs
- Partner provides "feasibility feedback":
  - Is this achievable in 3 days?
  - Is the scope too broad? Too narrow?
  - Which 2-3 scenes are most critical to draft first?
- Revise scope if needed (better to succeed with smaller scope than fail with larger)

**End-of-day deliverables:**

- One-page **Story Spec** (logline, audience, tone, genre).
- Character sheets for protagonist and key supporting cast.
- Rough 15-beat outline.

**Homework (~2 hours):**

- Refine beat sheet and expand a few beats into more detailed scene notes.
- Optional: free-write in character voice (journaling) to deepen internal contradictions.



### **Day 3 – Drafting with Multi-Agent Pipelines**

**Goal:** Move from design to execution: configure AI drafting pipelines and create a rough draft or structurally complete story.

**Objectives:**

- Think of drafting as a **pipeline** of specialized agents.
- Use Tournament / Ensemble modes to compare and hybridize AI outputs.
- Produce a complete rough narrative: novella or full-arc skeleton.

**Activities:**

1. **Designing the Drafting Pipeline (contact)**

   - Present typical pipeline pattern:
     - Beat → scene stub → expanded scene → style/voice pass → light edit.
   - Students configure, within *Writers Factory*:
     - Prompts for planner, drafter, stylist, and editor agents.
     - Choice of underlying models (e.g., premium cloud vs local Ollama).
   - Test run on 1–2 beats.

   

2. **Tournament & Ensemble Drafting (contact)**

   - For a key scene (e.g. Catalyst or Midpoint):

     - Generate multiple variations (different agents/prompts).
     - Use **Tournament Compare View** to evaluate: clarity, emotional impact, coherence with spec.
     - Manually hybridize a “winner” version.

     

3. **Scaling to the Full Draft (contact + homework)**

   - Turn the beat sheet into a **task list**.
   - Students aim for:
     - A full novella draft **or**
     - Complete drafts of all key beats + shorter bridging scenes.
   - Emphasis on "good enough to revise" rather than perfection.

**Progress Tracking & Triage (contact, 30 min @ 3pm)**

**Checkpoint:**

- Quick stand-up: "What percentage of your draft is complete?"
- Triage into 3 groups:
  - **On track** (50%+ complete): Continue drafting
  - **Behind** (20-50% complete): Prioritize key scenes only
  - **Struggling** (< 20%): Switch to technical track or reduce scope

**Instructor/TA provides:**

- Encouragement for "on track" students
- Strategic advice for "behind" students (which scenes to cut)
- Alternative path for "struggling" students (technical proposal instead)

**🎉 THE UPGRADE MOMENT (Late Day 3 or Early Day 4):**

**When a student hits 2,500 words**, Writers Factory automatically prompts:

```
┌──────────────────────────────────────────┐
│  🎉 CONGRATULATIONS!                     │
│                                          │
│  You've written 2,500 words of fiction! │
│                                          │
│  READY TO UNLOCK NOVEL SKILLS?           │
│                                          │
│  Your Starter Skills were based on      │
│  emails and social media (casual voice).│
│                                          │
│  Now let's analyze your FICTION voice   │
│  and generate TRUE custom skills!        │
│                                          │
│  This upgrade will:                      │
│  ✓ Analyze your 2,500 words of fiction │
│  ✓ Extract your novel-specific voice   │
│  ✓ Generate 6 novel-tuned skills        │
│  ✓ Show you how your voice evolved      │
│                                          │
│  Time: ~5 minutes                        │
│                                          │
│  [Upgrade to Novel Skills Now!]          │
└──────────────────────────────────────────┘
```

**What happens:**
1. System analyzes their 2,500 words of actual fiction
2. Extracts "Novel Voice Profile" (different from email voice!)
3. Generates 6 novel-tuned skills
4. Shows comparison:
   - Starter voice: "Casual, short sentences"
   - Novel voice: "Literary, varied rhythm, richer metaphors"
5. Celebration with confetti 🎉

**Why this matters:**
- Students see tangible growth (email voice → fiction voice)
- Skills become MORE accurate for their actual writing
- Feels like leveling up (achievement unlocked!)
- From this point: same experience as experienced writers

**End-of-day deliverables:**

- Configured drafting pipeline in the system.
- A substantial portion of the story drafted; ideally a complete rough pass by the end of homework.

**Homework (~2 hours):**

- Continue drafting any missing scenes.
- Note friction points in the tool/workflow (for potential Day 5 technical proposals).



### **Day 4 – Diagnostics, Refinement & Presentation Prep**

**Goal:** Improve structure, pacing, and style; start preparing final presentations.

Objectives:**

- Use pacing and structural diagnostics to find weak spots.
- Polish at least one key excerpt to a “readable” level.
- Begin drafting a **presentation**: creative or technical.

**Activities:**

1. **Pacing & Structural Diagnostics (contact)**

   - Use the **Stylometry / Pacing Panel**:
     - Visualize tension vs chapter/beat.
     - Identify “flat spots” (e.g., several consecutive chapters with static tension).
   - AI suggests compression, added obstacles, or sharper turning points.
   - Students revise at least one problematic section.

2. **Voice & Style Refinement (contact)**

   - Discuss voice as signal; clichés and verbosity as noise.
   - Use **Voice Assessment** tools to:
     - Compare style to chosen examples without copying.
   - Perform line-edit passes on a few pages:
     - Reduce exposition dumps.
     - Strengthen dialogue and sensory detail.

3. **Symbolic & Thematic Layering (light, optional) (contact)**

   - Introduce simple symbolic techniques:
     - recurrence, evolution, juxtaposition.
   - In the **Symbolic Layering** / metadata panel:
     - Identify 1–2 motifs and plan their appearances.
   - Apply at least one symbolic adjustment to a key scene.

4. **Presentation Preparation (contact + homework)**

   - Students choose **one track** for Day 5:

   **Creative Track:**

   - Select a 2–3 page passage for reading.
   - Prepare a 10–15 min talk:
     - story premise,
     - creative process,
     - how they used AI,
     - what they learned.

   **Technical Track:**

   - Identify a pain point in the workflow.
   - Draft a short improvement proposal:
     - problem description,
     - proposed feature or change,
     - rough UX or architectural idea,
     - anticipated impact.

**Presentation Workshop (contact, 1 hour)**

**Goal:** Ensure every student has a clear, compelling talk.

**Activities:**

1. **Structure Template** (15 min):
   - Creative: Hook → Premise → Excerpt → Reflection
   - Technical: Problem → Solution → Demo/Mockup → Impact

2. **Lightning Practice** (30 min):
   - Students give 2-minute version of their talk to pairs
   - Partner provides feedback:
     - Was the hook engaging?
     - Was the main idea clear?
     - Did you speak too fast/slow?

3. **Slide/Visual Guidance** (15 min):
   - Show examples of good vs bad presentation visuals
   - Recommend: 5-8 slides MAX (or none for pure reading)

**End-of-day deliverables:**

- Improved structural outline or key sections.
- A polished excerpt and/or substantial technical proposal draft.
- Outline of a 10–15 minute presentation.

**Homework (~2 hours):**

- Final polish on excerpt or proposal.
- Rehearse talk (timing, clarity).

### Day 5 – Final Presentations & Reflection**

**Goal:** Share work, reflect on process, and capture insights for future improvements.

**Objectives:**

- Present creative or technical outcomes.
- Practice critical listening and constructive feedback.
- Reflect collectively on AI’s role in creative workflows.

**Activities:**

1. **Student Presentations (contact, 3 hours)**

   **Format:** 15 min per student (10 min present, 5 min feedback)

   **Feedback Protocol:**

   - **2 stars** (What worked well?)
   - **1 wish** (What could be even better?)
   - Delivered orally + written on index card

   **Order:**

   - Volunteers first (reward bravery)
   - Then semi-random (draw names)
   - Creative presentations first, then technical (natural progression)

   Each student (or team) presents for **10 minutes**:

   **Creative option:**

   - Brief overview of the story: premise, protagonist, major conflict.
   - Live reading of an excerpt they are proud of.
   - Short reflection on:
     - how AI helped or hindered,
     - what surprised them about their own process.

   **Technical option:**

   - Description of the problem in *Writers Factory* they chose to address.
   - Proposed solution: UX change, new feature, revised agent pipeline, better diagnostics, etc.
   - Discussion of feasibility, constraints, and potential next steps.

2. **Peer Feedback & Discussion (contact)**

   - Students provide short written or oral feedback.
   - Group reflection:
     - What worked well with AI assistance?
     - What felt frustrating or limiting?
     - How might these tools reshape research, experimentation, or other engineering tasks?

3. **Wrap-Up & Next Steps (contact)**

   - Suggestions for expanding the project post-course (continuing the novel, building an open-source tool, writing a paper on AI-assisted creativity).
   - Optional: collect improvement notes for future iterations of the course.

**End-of-course deliverables:**

- A completed or structurally complete novel/novella project **or**
- A structured technical improvement proposal for *Writers Factory* (possibly accompanied by code/UX mockups). 

## **6. Assessment and Grading**

**Model:** Pass/Fail

**Emphasis:** Effort, risk-taking, and completion, not perfection.

### **Pass/Fail Rubric**

**Pass requires 4/6 criteria:**

1. **Environment Setup** (Day 1)
   - [ ] Successfully ran AI generation on at least 1 model
   - [ ] Created NotebookLM notebook with 5+ sources

2. **Story Specification** (Day 2)
   - [ ] Submitted story spec (logline, character, beat sheet)
   - [ ] Received peer feedback and iterated

3. **Drafting Progress** (Day 3)
   - [ ] Generated at least 5,000 words of narrative
   - [ ] OR identified technical improvement area

4. **Revision & Analysis** (Day 4)
   - [ ] Used at least 1 diagnostic tool (pacing, character, etc.)
   - [ ] Produced polished excerpt (2-3 pages) OR technical proposal draft

5. **Final Deliverable** (Day 5)
   - [ ] Submitted complete manuscript (10,000+ words) OR technical proposal (3+ pages)
   - [ ] Meets minimum quality bar (coherent, spell-checked, formatted)

6. **Presentation** (Day 5)
   - [ ] Delivered 10-15 minute talk
   - [ ] Responded to at least 1 Q&A question
   - [ ] Participated in peer feedback

**Fail conditions:**

- Missing 3+ days without excuse
- No final deliverable submitted
- Presentation not delivered

**Optional recognition (non-graded):**

- "Most Innovative Story Concept"
- "Best Use of Multi-Agent Workflow"
- "Best Technical Improvement Proposal"
- "Clever System Hack / Experimental Use of the Platform"



## **7. Technical & Logistical Requirements**

### **Hardware Requirements (Per Student)**

**Minimum:**

- Laptop with 8GB RAM, 20GB free disk space
- Intel i5 / AMD Ryzen 5 or better (2018+)
- Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- Reliable internet (for API calls)

**Recommended:**

- 16GB RAM (for running local Ollama models smoothly)
- Dedicated GPU (optional, for faster local generation)

### **Software Prerequisites**

**Must install before Day 1:**

1. **Git** (for cloning repository)
2. **Python 3.10+** (for backend)
3. **Node.js 18+** (for frontend)
4. **VS Code or similar editor** (recommended)

**Provided by instructors:**

- Writers Factory GitHub repository (public link)
- Installation guide with screenshots/video
- Troubleshooting FAQ

### **AI Model Access**

**Option A: Cloud Models (Recommended for first-time users)**

- Instructor provides **shared API keys** with rate limits
- Cost: ~$5-10 per student for week (total: $150-300 for 30 students)
- Models: Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro

**Option B: Local Models (For advanced users or cost savings)**

- Students install Ollama and download Llama 3 8B
- Free, but slower generation
- Requires 8GB+ RAM

**Option C: Hybrid (Recommended)**

- Use local for drafts (free, unlimited)
- Use cloud for final polish (better quality)
- Enable "Economy Mode" in Writers Factory

### **Facilities**

**Required:**

- **Computer lab** with 30-40 stations OR BYOD policy
- **Projector** + large screen for demonstrations
- **Whiteboards** (2+) for story diagrams and system sketches
- **Breakout space** for pair work and group discussions

**Nice to have:**

- **Document camera** for showing paper sketches/notes
- **Audio system** for playing AI-generated audio examples
- **Printing capability** for handouts and worksheets



## **8. Risk Mitigation Plan**

### **Risk 1: Installation Failures (HIGH probability)**

**Likelihood:** 30-40% of students will have installation issues

**Mitigation:**

- Pre-course installation with verification
- 3 backup machines pre-configured
- Cloud-based fallback (Codespaces)
- Pair programming (1 working machine = 2 students)

### **Risk 2: Students Get Stuck Creatively (MEDIUM probability)**

**Likelihood:** 20-30% will struggle with blank page

**Mitigation:**

- Day 2: Provide 10 "story starter" prompts (optional)
- Day 3: Allow students to switch to "remix existing story" mode
- Emphasis on "good enough" over perfection
- Technical track as alternative for those who pivot

### **Risk 3: AI Models Unavailable or Rate Limited (LOW but HIGH impact)**

**Likelihood:** 5-10%, but course-breaking if it happens

**Mitigation:**

- Ollama as offline fallback
- Multiple API keys with load balancing
- Instructor monitors usage daily
- Emergency cloud credits budget ($500)

### **Risk 4: Wide Skill Gap (MEDIUM probability)**

**Likelihood:** Masters students vastly outpace high schoolers

**Mitigation:**

- Mixed-experience teams (mentorship model)
- Differentiated expectations (rubric adjusts for experience)
- Optional "advanced challenges" for fast movers
- Celebrate different kinds of success (creative vs technical)

### **Risk 5: Students Produce Nothing (LOW probability)**

**Likelihood:** 5-10% "give up" midweek

**Mitigation:**

- Daily check-ins with progress tracking
- Day 3 triage (pivot to technical if needed)
- Pair accountability (teams check in on each other)
- Instructor 1-on-1 meetings for struggling students (Day 3-4)



## **9. Pre-Course Preparation Checklist**

### **2 Weeks Before:**

- [ ] Finalize enrollment (confirm 20-30 students)
- [ ] Send installation guide + video
- [ ] Schedule pre-course office hours (2-3 sessions)
- [ ] Procure API keys (or confirm institutional access)
- [ ] Test Writers Factory on 3 different OS types
- [ ] Prepare backup machines (3+)

### **1 Week Before:**

- [ ] Students submit installation health check
- [ ] Identify students needing extra help
- [ ] Prepare Day 1 slides and demos
- [ ] Create NotebookLM example notebook
- [ ] Print handouts (story spec templates, beat sheets)

### **2 Days Before:**

- [ ] Final check of computer lab setup
- [ ] Test projector and whiteboard availability
- [ ] Confirm all students have submitted health check
- [ ] Prepare "emergency kit" (USB drives with installers, backup API keys)

### **Day 0 (Optional):**

- [ ] Informal meet-and-greet session
- [ ] Installation troubleshooting clinic
- [ ] Show example projects from previous years (if available)



## **10. Post-Course Follow-Up**

### **Immediate (Day 5 evening):**

- Collect all manuscripts and proposals
- Send thank-you email with:
  - Links to submitted work
  - Survey for course feedback
  - Optional: invite to continue project

### **1 Week After:**

- Grade submissions (Pass/Fail)
- Send individual feedback (2-3 paragraphs per student) 
- Announce optional recognitions (best story, best proposal)

### **1 Month After:**

- Host optional "reunion session":
  - Students who continued their projects share progress
  - Discuss any implemented technical improvements
  - Plan potential publication anthology (if interest exists)

### **Long-term:**

- Consider creating a **Writers Factory Community**:
  - GitHub discussions for ongoing development
  - Showcase of best student works
  - Alumni mentorship for future cohorts

