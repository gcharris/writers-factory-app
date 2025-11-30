# <a id="src-main"></a> Software 3.0: Coding Workflow Applied to Narrative Design

The workflow implemented in the Writers Factory is highly analogous to the AI-assisted development workflow you previously summarized, but it is specialized and architected specifically for **creative narrative production**[[Source 1]](#src-1). Both systems operate as **partial autonomy apps**[[Source 2]](#src-2)[[Source 3]](#src-3), utilizing external context management systems to overcome the inherent "anterograde amnesia" of Large Language Models (LLMs)[[Source 4]](#src-4)[[Source 5]](#src-5).

Here is a comparison of the key phases and mechanisms:

### 1\. Core Goal and Architectural Philosophy

<table><thead><tr><th><span _ngcontent-ng-c2328698254="" data-start-index="488" class="ng-star-inserted">Feature</span></th><th><span _ngcontent-ng-c2328698254="" data-start-index="495" class="ng-star-inserted">Development Workflow (Coding)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="6: AI Workflow: Task Decomposition and Context Agents">6</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="7: The Agentic Development Pipeline: LLM Context Mastery">7</span></button></span></th><th><span _ngcontent-ng-c2328698254="" data-start-index="524" class="ng-star-inserted">Writers Factory Workflow (Narrative)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="3: The Writers Factory: Structuring AI for Novelists">3</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="8: ARCHITECTURE.md">8</span></button></span></th></tr></thead><tbody><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="560" class="ng-star-inserted">Domain</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="566" class="ng-star-inserted">Software development, code implementation, and debugging for systems (e.g., Pipecat, Vappy)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="7: The Agentic Development Pipeline: LLM Context Mastery">7</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="9: The Agentic Development Pipeline: LLM Context Mastery">9</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="657" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="658" class="ng-star-inserted">Professional novel-writing IDE that manages the entire lifecycle of a book, from concept to market</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="8: ARCHITECTURE.md">8</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="10: Author’s Writing Dashboard (Book Writing Tracker) | annotated by Geoffrey">10</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="756" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="757" class="ng-star-inserted">Core AI Deficit Addressed</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="782" class="ng-star-inserted">LLM unreliability out of the box; teaching specific development processes</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="6: AI Workflow: Task Decomposition and Context Agents">6</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="7: The Agentic Development Pipeline: LLM Context Mastery">7</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="855" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="856" class="ng-star-inserted">LLM </span><b _ngcontent-ng-c2328698254="" data-start-index="860" class="ng-star-inserted">anterograde amnesia</b><span _ngcontent-ng-c2328698254="" data-start-index="879" class="ng-star-inserted"> (inability to consolidate knowledge over time) against the complexity of novel-length narrative</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="4: The Writers Factory: Structuring AI for Novelists">4</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="5: Writers Factory: Augmenting Narrative with Context Engineering">5</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="975" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="976" class="ng-star-inserted">Governing Philosophy</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="996" class="ng-star-inserted">Centered on </span><b _ngcontent-ng-c2328698254="" data-start-index="1008" class="ng-star-inserted">context management system</b><span _ngcontent-ng-c2328698254="" data-start-index="1033" class="ng-star-inserted"> and </span><b _ngcontent-ng-c2328698254="" data-start-index="1038" class="ng-star-inserted">task decomposition</b><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="6: AI Workflow: Task Decomposition and Context Agents">6</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="7: The Agentic Development Pipeline: LLM Context Mastery">7</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="1056" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="1057" class="ng-star-inserted">Enforces </span><b _ngcontent-ng-c2328698254="" data-start-index="1066" class="ng-star-inserted">Structure Before Freedom</b><span _ngcontent-ng-c2328698254="" data-start-index="1090" class="ng-star-inserted">, mandating the completion of the Preparation Phase (Story Bible) before accessing the Execution Phase (drafting)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="3: The Writers Factory: Structuring AI for Novelists">3</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" class="citation-marker" jslog="219344;track:generic_click,impression,hover"><span _ngcontent-ng-c2328698254="" aria-label="Hide additional citations" class="ng-star-inserted" style="">&gt; &lt;</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted" style=""><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="11: ARCHITECTURE.md">11</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="12: Writers Factory: Augmenting Narrative with Context Engineering">12</span></button></span></span><span _ngcontent-ng-c2328698254="" data-start-index="1203" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="1204" class="ng-star-inserted">Context Management</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="1222" class="ng-star-inserted">Project memory captured in a root documentation folder optimized for retrieval by expert sub-agents</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="13: The Agentic Development Pipeline: LLM Context Mastery">13</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="1321" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="1322" class="ng-star-inserted">Uses </span><b _ngcontent-ng-c2328698254="" data-start-index="1327" class="ng-star-inserted">Context Engineering</b><span _ngcontent-ng-c2328698254="" data-start-index="1346" class="ng-star-inserted"> where the story state is externalized and managed in a </span><b _ngcontent-ng-c2328698254="" data-start-index="1402" class="ng-star-inserted">Knowledge Graph</b><span _ngcontent-ng-c2328698254="" data-start-index="1417" class="ng-star-inserted"> (The Living Brain)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="3: The Writers Factory: Structuring AI for Novelists">3</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" class="citation-marker" jslog="219344;track:generic_click,impression,hover"><span _ngcontent-ng-c2328698254="" aria-label="Hide additional citations" class="ng-star-inserted" style="">&gt; &lt;</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted" style=""><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="12: Writers Factory: Augmenting Narrative with Context Engineering">12</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="14: ARCHITECTURE.md">14</span></button></span></span><span _ngcontent-ng-c2328698254="" data-start-index="1436" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="1437" class="ng-star-inserted">UI Analogy</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="1447" class="ng-star-inserted">Functions like a </span><b _ngcontent-ng-c2328698254="" data-start-index="1464" class="ng-star-inserted">highly specialized research team and editor</b><span _ngcontent-ng-c2328698254="" data-start-index="1507" class="ng-star-inserted"> for code</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="15: The Agentic Development Pipeline: LLM Context Mastery">15</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="1516" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="1517" class="ng-star-inserted">Designed as </span><b _ngcontent-ng-c2328698254="" data-start-index="1529" class="ng-star-inserted">"Scrivener meets VS Code meets the writer’s future"</b><span _ngcontent-ng-c2328698254="" data-start-index="1580" class="ng-star-inserted">—a specialized IDE built for speed, organization, and AI augmentation</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="3: The Writers Factory: Structuring AI for Novelists">3</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="16: Scrivener meets VS Code meets the writer’s future.md">16</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="1649" class="ng-star-inserted">.</span></td></tr></tbody></table>

Feature

Development Workflow (Coding)[[Source 6]](#src-6)[[Source 7]](#src-7)

Writers Factory Workflow (Narrative)[[Source 3]](#src-3)[[Source 8]](#src-8)

**Domain**

Software development, code implementation, and debugging for systems (e.g., Pipecat, Vappy)[[Source 7]](#src-7)[[Source 9]](#src-9).

Professional novel-writing IDE that manages the entire lifecycle of a book, from concept to market[[Source 8]](#src-8)[[Source 10]](#src-10).

**Core AI Deficit Addressed**

LLM unreliability out of the box; teaching specific development processes[[Source 6]](#src-6)[[Source 7]](#src-7).

LLM **anterograde amnesia** (inability to consolidate knowledge over time) against the complexity of novel-length narrative[[Source 4]](#src-4)[[Source 5]](#src-5).

**Governing Philosophy**

Centered on **context management system** and **task decomposition**[[Source 6]](#src-6)[[Source 7]](#src-7).

Enforces **Structure Before Freedom**, mandating the completion of the Preparation Phase (Story Bible) before accessing the Execution Phase (drafting)[[Source 3]](#src-3)\> <[[Source 11]](#src-11)[[Source 12]](#src-12).

**Context Management**

Project memory captured in a root documentation folder optimized for retrieval by expert sub-agents[[Source 13]](#src-13).

Uses **Context Engineering** where the story state is externalized and managed in a **Knowledge Graph** (The Living Brain)[[Source 3]](#src-3)\> <[[Source 12]](#src-12)[[Source 14]](#src-14).

**UI Analogy**

Functions like a **highly specialized research team and editor** for code[[Source 15]](#src-15).

Designed as **"Scrivener meets VS Code meets the writer’s future"**—a specialized IDE built for speed, organization, and AI augmentation[[Source 3]](#src-3)[[Source 16]](#src-16).

\--------------------------------------------------------------------------------

### 2\. Planning, Research, and Decomposition Phase

In both workflows, complex tasks are broken down and context is gathered by specialized entities, but the output shifts from technical documentation to structured narrative artifacts.

<table><thead><tr><th><span _ngcontent-ng-c2328698254="" data-start-index="1961" class="ng-star-inserted">Feature</span></th><th><span _ngcontent-ng-c2328698254="" data-start-index="1968" class="ng-star-inserted">Development Workflow (Coding)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="9: The Agentic Development Pipeline: LLM Context Mastery">9</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="17: The Agentic Development Pipeline: LLM Context Mastery">17</span></button></span></th><th><span _ngcontent-ng-c2328698254="" data-start-index="1997" class="ng-star-inserted">Writers Factory Workflow (Narrative)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="18: TASK_Creation_Wizard.md">18</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="19: WORKFLOWS.md">19</span></button></span></th></tr></thead><tbody><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="2033" class="ng-star-inserted">Initiation</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2043" class="ng-star-inserted">The user uses the </span><b _ngcontent-ng-c2328698254="" class="code ng-star-inserted" data-start-index="2061">plan task</b><span _ngcontent-ng-c2328698254="" data-start-index="2070" class="ng-star-inserted"> custom command</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="9: The Agentic Development Pipeline: LLM Context Mastery">9</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="2085" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2086" class="ng-star-inserted">The user initiates the optional </span><b _ngcontent-ng-c2328698254="" data-start-index="2118" class="ng-star-inserted">Creation Wizard Pipeline</b><span _ngcontent-ng-c2328698254="" data-start-index="2142" class="ng-star-inserted"> to build a story bible</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="18: TASK_Creation_Wizard.md">18</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="2165" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="2166" class="ng-star-inserted">Task Decomposition</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2184" class="ng-star-inserted">Complex research is delegated to specialized </span><b _ngcontent-ng-c2328698254="" data-start-index="2229" class="ng-star-inserted">research sub-agents</b><span _ngcontent-ng-c2328698254="" data-start-index="2248" class="ng-star-inserted"> (e.g., Vappy Expert sub-agent, Pipecat expert sub-agent)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="9: The Agentic Development Pipeline: LLM Context Mastery">9</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="2305" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2306" class="ng-star-inserted">The workflow uses a </span><b _ngcontent-ng-c2328698254="" data-start-index="2326" class="ng-star-inserted">SmartScaffoldWorkflow</b><span _ngcontent-ng-c2328698254="" data-start-index="2347" class="ng-star-inserted"> (AI Scaffolding Agent) to query external resources and structure the story</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="19: WORKFLOWS.md">19</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="20: DOCS_INDEX.md">20</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="2422" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="2423" class="ng-star-inserted">Context/Research Sources</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2447" class="ng-star-inserted">Local clones of repos, online documentation, and open API (Swagger) documentation</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="9: The Agentic Development Pipeline: LLM Context Mastery">9</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="2528" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2529" class="ng-star-inserted">Queries </span><b _ngcontent-ng-c2328698254="" data-start-index="2537" class="ng-star-inserted">Google NotebookLM</b><span _ngcontent-ng-c2328698254="" data-start-index="2554" class="ng-star-inserted"> for research materials (protagonist data, 15-beat structure, themes, world rules)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="19: WORKFLOWS.md">19</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="21: API_REFERENCE.md">21</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="2636" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="2637" class="ng-star-inserted">Output/Artifacts</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2653" class="ng-star-inserted">Planning documents generated by the orchestrating agent: </span><b _ngcontent-ng-c2328698254="" data-start-index="2710" class="ng-star-inserted">Implementation Notes</b><span _ngcontent-ng-c2328698254="" data-start-index="2730" class="ng-star-inserted">, </span><b _ngcontent-ng-c2328698254="" data-start-index="2732" class="ng-star-inserted">The Plan</b><span _ngcontent-ng-c2328698254="" data-start-index="2740" class="ng-star-inserted">, </span><b _ngcontent-ng-c2328698254="" data-start-index="2742" class="ng-star-inserted">Decisions File</b><span _ngcontent-ng-c2328698254="" data-start-index="2756" class="ng-star-inserted">, and </span><b _ngcontent-ng-c2328698254="" data-start-index="2762" class="ng-star-inserted">Status File</b><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="17: The Agentic Development Pipeline: LLM Context Mastery">17</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="22: The Agentic Development Pipeline: LLM Context Mastery">22</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="2773" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2774" class="ng-star-inserted">Structured narrative documents generated in Phase 2 (</span><b _ngcontent-ng-c2328698254="" data-start-index="2827" class="ng-star-inserted">Story Bible System</b><span _ngcontent-ng-c2328698254="" data-start-index="2845" class="ng-star-inserted">): </span><b _ngcontent-ng-c2328698254="" data-start-index="2848" class="ng-star-inserted">Protagonist.md</b><span _ngcontent-ng-c2328698254="" data-start-index="2862" class="ng-star-inserted"> (Fatal Flaw, The Lie), </span><b _ngcontent-ng-c2328698254="" data-start-index="2886" class="ng-star-inserted">Beat_Sheet.md</b><span _ngcontent-ng-c2328698254="" data-start-index="2899" class="ng-star-inserted"> (15 beats), </span><b _ngcontent-ng-c2328698254="" data-start-index="2912" class="ng-star-inserted">Theme.md</b><span _ngcontent-ng-c2328698254="" data-start-index="2920" class="ng-star-inserted">, and </span><b _ngcontent-ng-c2328698254="" data-start-index="2926" class="ng-star-inserted">World Rules.md</b><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="23: DIRECTOR_MODE_SPECIFICATION.md">23</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" class="citation-marker" jslog="219344;track:generic_click,impression,hover"><span _ngcontent-ng-c2328698254="" aria-label="Hide additional citations" class="ng-star-inserted" style="">&gt; &lt;</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted" style=""><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="24: DOCS_INDEX.md">24</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="25: TASK_Creation_Wizard.md">25</span></button></span></span><span _ngcontent-ng-c2328698254="" data-start-index="2940" class="ng-star-inserted">.</span></td></tr></tbody></table>

Feature

Development Workflow (Coding)[[Source 9]](#src-9)[[Source 17]](#src-17)

Writers Factory Workflow (Narrative)[[Source 18]](#src-18)[[Source 19]](#src-19)

**Initiation**

The user uses the **plan task** custom command[[Source 9]](#src-9).

The user initiates the optional **Creation Wizard Pipeline** to build a story bible[[Source 18]](#src-18).

**Task Decomposition**

Complex research is delegated to specialized **research sub-agents** (e.g., Vappy Expert sub-agent, Pipecat expert sub-agent)[[Source 9]](#src-9).

The workflow uses a **SmartScaffoldWorkflow** (AI Scaffolding Agent) to query external resources and structure the story[[Source 19]](#src-19)[[Source 20]](#src-20).

**Context/Research Sources**

Local clones of repos, online documentation, and open API (Swagger) documentation[[Source 9]](#src-9).

Queries **Google NotebookLM** for research materials (protagonist data, 15-beat structure, themes, world rules)[[Source 19]](#src-19)[[Source 21]](#src-21).

**Output/Artifacts**

Planning documents generated by the orchestrating agent: **Implementation Notes**, **The Plan**, **Decisions File**, and **Status File**[[Source 17]](#src-17)[[Source 22]](#src-22).

Structured narrative documents generated in Phase 2 (**Story Bible System**): **Protagonist.md** (Fatal Flaw, The Lie), **Beat\_Sheet.md** (15 beats), **Theme.md**, and **World Rules.md**[[Source 23]](#src-23)\> <[[Source 24]](#src-24)[[Source 25]](#src-25).

\--------------------------------------------------------------------------------

### 3\. Execution, Iteration, and Review Phase

The execution phase in the Writers Factory replaces coding with **Tournament Mode** drafting, and the review shifts from technical corrections to **narrative diagnostics**[[Source 26]](#src-26)\> <[[Source 27]](#src-27)[[Source 28]](#src-28).

<table><thead><tr><th><span _ngcontent-ng-c2328698254="" data-start-index="3228" class="ng-star-inserted">Feature</span></th><th><span _ngcontent-ng-c2328698254="" data-start-index="3235" class="ng-star-inserted">Development Workflow (Coding)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="15: The Agentic Development Pipeline: LLM Context Mastery">15</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="22: The Agentic Development Pipeline: LLM Context Mastery">22</span></button></span></th><th><span _ngcontent-ng-c2328698254="" data-start-index="3264" class="ng-star-inserted">Writers Factory Workflow (Narrative)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="26: DIRECTOR_MODE_SPECIFICATION.md">26</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" class="citation-marker" jslog="219344;track:generic_click,impression,hover"><span _ngcontent-ng-c2328698254="" aria-label="Hide additional citations" class="ng-star-inserted" style="">&gt; &lt;</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted" style=""><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="27: The Writers Factory: Structuring AI for Novelists">27</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="28: Writers Factory: Augmenting Narrative with Context Engineering">28</span></button></span></span></th></tr></thead><tbody><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="3300" class="ng-star-inserted">Execution Trigger</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="3317" class="ng-star-inserted">User reviews planning documents for corrections (e.g., strict schema, JSON config) and then commands the agent to complete the implementation</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="22: The Agentic Development Pipeline: LLM Context Mastery">22</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="3458" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="3459" class="ng-star-inserted">The system performs </span><b _ngcontent-ng-c2328698254="" data-start-index="3479" class="ng-star-inserted">Level 2 Health Checks</b><span _ngcontent-ng-c2328698254="" data-start-index="3500" class="ng-star-inserted"> to validate the Story Bible completion (e.g., checking if all 15 beats are defined) before allowing the user to enter </span><b _ngcontent-ng-c2328698254="" data-start-index="3619" class="ng-star-inserted">Director Mode</b><span _ngcontent-ng-c2328698254="" data-start-index="3632" class="ng-star-inserted"> (drafting)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="3: The Writers Factory: Structuring AI for Novelists">3</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" class="citation-marker" jslog="219344;track:generic_click,impression,hover"><span _ngcontent-ng-c2328698254="" aria-label="Hide additional citations" class="ng-star-inserted" style="">&gt; &lt;</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted" style=""><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="27: The Writers Factory: Structuring AI for Novelists">27</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="29: DOCS_INDEX.md">29</span></button></span></span><span _ngcontent-ng-c2328698254="" data-start-index="3643" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="3644" class="ng-star-inserted">Generation Strategy</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="3663" class="ng-star-inserted">Agent completes the implementation based on the finalized plan</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="22: The Agentic Development Pipeline: LLM Context Mastery">22</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="3725" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="3726" class="ng-star-inserted">Runs a </span><b _ngcontent-ng-c2328698254="" data-start-index="3733" class="ng-star-inserted">Tournament + Multiplier</b><span _ngcontent-ng-c2328698254="" data-start-index="3756" class="ng-star-inserted"> pipeline where a </span><b _ngcontent-ng-c2328698254="" data-start-index="3774" class="ng-star-inserted">Squad</b><span _ngcontent-ng-c2328698254="" data-start-index="3779" class="ng-star-inserted"> of agents (e.g., Claude Sonnet, GPT-4o, Grok) compete to generate up to </span><b _ngcontent-ng-c2328698254="" data-start-index="3852" class="ng-star-inserted">25 unique scene variants</b><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="27: The Writers Factory: Structuring AI for Novelists">27</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" class="citation-marker" jslog="219344;track:generic_click,impression,hover"><span _ngcontent-ng-c2328698254="" aria-label="Hide additional citations" class="ng-star-inserted" style="">&gt; &lt;</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted" style=""><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="28: Writers Factory: Augmenting Narrative with Context Engineering">28</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="30: DIRECTOR_MODE_SPECIFICATION.md">30</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="31: DIRECTOR_MODE_SPECIFICATION.md">31</span></button></span></span><span _ngcontent-ng-c2328698254="" data-start-index="3876" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="3877" class="ng-star-inserted">Autonomy Control</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="3893" class="ng-star-inserted">User maintains control by setting goals and correcting idiomatic usage before committing code</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="15: The Agentic Development Pipeline: LLM Context Mastery">15</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="3986" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="3987" class="ng-star-inserted">The </span><b _ngcontent-ng-c2328698254="" data-start-index="3991" class="ng-star-inserted">Autonomy Slider</b><span _ngcontent-ng-c2328698254="" data-start-index="4006" class="ng-star-inserted"> is managed via </span><b _ngcontent-ng-c2328698254="" data-start-index="4022" class="ng-star-inserted">Director Mode</b><span _ngcontent-ng-c2328698254="" data-start-index="4035" class="ng-star-inserted"> and </span><b _ngcontent-ng-c2328698254="" data-start-index="4040" class="ng-star-inserted">Tournament Mode</b><span _ngcontent-ng-c2328698254="" data-start-index="4055" class="ng-star-inserted">, avoiding massive, unmanageable outputs and ensuring the AI remains "on the leash"</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="27: The Writers Factory: Structuring AI for Novelists">27</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" class="citation-marker" jslog="219344;track:generic_click,impression,hover"><span _ngcontent-ng-c2328698254="" aria-label="Hide additional citations" class="ng-star-inserted" style="">&gt; &lt;</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted" style=""><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="28: Writers Factory: Augmenting Narrative with Context Engineering">28</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="30: DIRECTOR_MODE_SPECIFICATION.md">30</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="32: Cursor: The Iron Man Suit of Software 3.0 Development">32</span></button></span></span><span _ngcontent-ng-c2328698254="" data-start-index="4138" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="4139" class="ng-star-inserted">Verification / Auditing</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="4162" class="ng-star-inserted">The user reviews the plan and generated output</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="22: The Agentic Development Pipeline: LLM Context Mastery">22</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="4208" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="4209" class="ng-star-inserted">The human writer acts as the </span><b _ngcontent-ng-c2328698254="" data-start-index="4238" class="ng-star-inserted">auditor</b><span _ngcontent-ng-c2328698254="" data-start-index="4245" class="ng-star-inserted"> using a specialized GUI to quickly verify output</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="27: The Writers Factory: Structuring AI for Novelists">27</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="28: Writers Factory: Augmenting Narrative with Context Engineering">28</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="4294" class="ng-star-inserted">. This includes reviewing results scored against a </span><b _ngcontent-ng-c2328698254="" data-start-index="4345" class="ng-star-inserted">100-Point Scoring Rubric</b><span _ngcontent-ng-c2328698254="" data-start-index="4369" class="ng-star-inserted"> (e.g., Voice Authenticity, Character Consistency)</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="28: Writers Factory: Augmenting Narrative with Context Engineering">28</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="33: DIRECTOR_MODE_SPECIFICATION.md">33</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="4419" class="ng-star-inserted">.</span></td></tr><tr><td><b _ngcontent-ng-c2328698254="" data-start-index="4420" class="ng-star-inserted">Maintenance/Post-Task</b></td><td><span _ngcontent-ng-c2328698254="" data-start-index="4441" class="ng-star-inserted">Commands like </span><b _ngcontent-ng-c2328698254="" class="code ng-star-inserted" data-start-index="4455">root cause analysis</b><span _ngcontent-ng-c2328698254="" data-start-index="4474" class="ng-star-inserted"> (collaborative debugging via logging and Git reset) and </span><b _ngcontent-ng-c2328698254="" class="code ng-star-inserted" data-start-index="4531">create pull request</b><span _ngcontent-ng-c2328698254="" data-start-index="4550" class="ng-star-inserted"> for maintenance</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="34: The Agentic Development Pipeline: LLM Context Mastery">34</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="4566" class="ng-star-inserted">.</span></td><td><span _ngcontent-ng-c2328698254="" data-start-index="4567" class="ng-star-inserted">The </span><b _ngcontent-ng-c2328698254="" data-start-index="4571" class="ng-star-inserted">Consolidator Agent</b><span _ngcontent-ng-c2328698254="" data-start-index="4589" class="ng-star-inserted"> runs in the background (Metabolism Phase) to ingest new chat/scene decisions into the graph, ensuring the story memory is current</span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="3: The Writers Factory: Structuring AI for Novelists">3</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" class="citation-marker" jslog="219344;track:generic_click,impression,hover"><span _ngcontent-ng-c2328698254="" aria-label="Hide additional citations" class="ng-star-inserted" style="">&gt; &lt;</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted" style=""><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="12: Writers Factory: Augmenting Narrative with Context Engineering">12</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="35: API_REFERENCE.md">35</span></button></span></span><span _ngcontent-ng-c2328698254="" data-start-index="4719" class="ng-star-inserted">. Diagnostics include </span><b _ngcontent-ng-c2328698254="" data-start-index="4741" class="ng-star-inserted">Narrative Health Checks</b><span _ngcontent-ng-c2328698254="" data-start-index="4764" class="ng-star-inserted"> (Phase 3D) that flag issues like </span><b _ngcontent-ng-c2328698254="" data-start-index="4798" class="ng-star-inserted">Pacing Plateaus</b><span _ngcontent-ng-c2328698254="" data-start-index="4813" class="ng-star-inserted"> (flat tension over multiple chapters) and failure to test the </span><b _ngcontent-ng-c2328698254="" data-start-index="4876" class="ng-star-inserted">Fatal Flaw</b><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false"><span _ngcontent-ng-c2328698254="" aria-label="27: The Writers Factory: Structuring AI for Novelists">27</span></button></span><span _ngcontent-ng-c2328698254="" class="ng-star-inserted"><button _ngcontent-ng-c2328698254="" dialoglabel="Citation Details" triggerdescription="Click to open citation details" class="xap-inline-dialog citation-marker ng-star-inserted" jslog="219344;track:generic_click,impression,hover" aria-haspopup="dialog" aria-describedby="cdk-describedby-message-ng-1-100" cdk-describedby-host="ng-1" data-disabled="false" style="opacity: 0.6;"><span _ngcontent-ng-c2328698254="" aria-label="36: Phase 3D Graph Health Service - Complete Implementation Plan.md">36</span></button></span><span _ngcontent-ng-c2328698254="" data-start-index="4886" class="ng-star-inserted">.</span></td></tr></tbody></table>

Feature

Development Workflow (Coding)[[Source 15]](#src-15)[[Source 22]](#src-22)

Writers Factory Workflow (Narrative)[[Source 26]](#src-26)\> <[[Source 27]](#src-27)[[Source 28]](#src-28)

**Execution Trigger**

User reviews planning documents for corrections (e.g., strict schema, JSON config) and then commands the agent to complete the implementation[[Source 22]](#src-22).

The system performs **Level 2 Health Checks** to validate the Story Bible completion (e.g., checking if all 15 beats are defined) before allowing the user to enter **Director Mode** (drafting)[[Source 3]](#src-3)\> <[[Source 27]](#src-27)[[Source 29]](#src-29).

**Generation Strategy**

Agent completes the implementation based on the finalized plan[[Source 22]](#src-22).

Runs a **Tournament + Multiplier** pipeline where a **Squad** of agents (e.g., Claude Sonnet, GPT-4o, Grok) compete to generate up to **25 unique scene variants**[[Source 27]](#src-27)\> <[[Source 28]](#src-28)[[Source 30]](#src-30)[[Source 31]](#src-31).

**Autonomy Control**

User maintains control by setting goals and correcting idiomatic usage before committing code[[Source 15]](#src-15).

The **Autonomy Slider** is managed via **Director Mode** and **Tournament Mode**, avoiding massive, unmanageable outputs and ensuring the AI remains "on the leash"[[Source 27]](#src-27)\> <[[Source 28]](#src-28)[[Source 30]](#src-30)[[Source 32]](#src-32).

**Verification / Auditing**

The user reviews the plan and generated output[[Source 22]](#src-22).

The human writer acts as the **auditor** using a specialized GUI to quickly verify output[[Source 27]](#src-27)[[Source 28]](#src-28). This includes reviewing results scored against a **100-Point Scoring Rubric** (e.g., Voice Authenticity, Character Consistency)[[Source 28]](#src-28)[[Source 33]](#src-33).

**Maintenance/Post-Task**

Commands like **root cause analysis** (collaborative debugging via logging and Git reset) and **create pull request** for maintenance[[Source 34]](#src-34).

The **Consolidator Agent** runs in the background (Metabolism Phase) to ingest new chat/scene decisions into the graph, ensuring the story memory is current[[Source 3]](#src-3)\> <[[Source 12]](#src-12)[[Source 35]](#src-35). Diagnostics include **Narrative Health Checks** (Phase 3D) that flag issues like **Pacing Plateaus** (flat tension over multiple chapters) and failure to test the **Fatal Flaw**[[Source 27]](#src-27)[[Source 36]](#src-36).

In summary, both workflows are highly evolved examples of **Software 3.0** applications[[Source 1]](#src-1)[[Source 37]](#src-37), designed to manage the "fallible systems" of LLMs[[Source 2]](#src-2)[[Source 27]](#src-27). The development workflow focuses on context management for specialized technical requirements, while the Writers Factory applies the same advanced architectural pattern (Context Graph, Specialized Agents, Auditable Output) to enforce **professional creative methodology** (character depth, structural pacing, and authentic voice)[[Source 3]](#src-3)[[Source 28]](#src-28).

# <a id="src-1"></a>Source: The Writers Factory: Structuring AI for Novelists (Citation 1)



## [Main Content](#src-main) 

*   **Opening:** We are entering a fundamental shift in software development: **Software 3.0** \[1\]. The Large Language Model (LLM) is our new computer, and our prompts are now programs \[1\].
*   **The Writers Factory:** The Factory is built entirely for this new era. It is a **professional novel-writing IDE** (Integrated Development Environment) \[2, 3\].
*   **Purpose:** Our goal is not just generation, but **collaboration** \[3\]—using AI agents to ensure consistency with a predefined methodology \[2\].
*   **Under the Hood:** Students will be using a **local-first desktop application** built using **Tauri + Svelte** with a **Python Backend** \[4, 5\]. The core app provides a visible **Editor, Graph Panel, and Agent Panel** \[4\].

# <a id="src-2"></a>Source: Cursor: The Iron Man Suit of Software 3.0 Development (Citation 2)



## [Main Content](#src-main) 

\---

\## 1. Theoretical Function of Cursor (The "Partial Autonomy App")

Theoretically, Cursor is classified as a \*\*partial autonomy app\*\*. It acts as a necessary intermediary layer, augmenting the human developer's capabilities without completely removing them from the loop.

The lecturer emphasizes that highly capable LLMs are still \*\*fallible systems\*\* possessing "cognitive deficits" like hallucination and jagged intelligence. Cursor is built to manage this uncertainty by optimizing the \*\*generation-verification loop\*\*, where the AI performs the generation and the human performs the verification.

# <a id="src-3"></a>Source: The Writers Factory: Structuring AI for Novelists (Citation 3)



## [Main Content](#src-main) 

### III. The Solution: Context Engineering the Living Brain (3:30 – 6:30)

**(Goal: Introduce the Knowledge Graph and the "Structure Before Freedom" philosophy.)**

*   **Necessity of the Application:** To use the LLM's power effectively, we must use a specialized application—a **partial autonomy app**—designed to manage the intelligence layer \[7, 8\].
*   **Context Engineering:** The Factory’s solution is **Context Engineering**. The true state of your story is externalized and managed in the **Knowledge Graph**, which we call **The Living Brain** \[7, 9\].
*   **The Structure is Sacred:** The system enforces the core philosophy of **Structure Before Freedom** \[10\]. Writers must complete the **Preparation Phase** (Story Bible artifacts) before they can access the Execution Phase (drafting) \[10\].
    *   **Required Artifacts:** This involves creating structured files like **Protagonist.md** (defining Fatal Flaw and The Lie) and **Beat\_Sheet.md** (using the **Save the Cat! 15-Beat Structure**) \[11-13\].
*   **Metabolism and Memory:** This Graph is not static; it **evolves** \[9\]. The system implements a **Metabolism** phase \[9, 14\] where the **Consolidator Agent** runs in the background to parse chat history and saved text into updated graph nodes, ensuring the AI never "forgets" the established lore \[7, 9, 14\].

# <a id="src-4"></a>Source: The Writers Factory: Structuring AI for Novelists (Citation 4)



## [Main Content](#src-main) 

### II. The Problem: LLM Amnesia vs. Story Complexity (1:30 – 3:30)

**(Goal: Explain the LLM’s inherent defects and why simple prompting fails the novelist.)**

*   **LLMs are Fallible:** These "people spirits" possess **jagged intelligence** and "cognitive deficits" \[6\].
*   **The Crucial Deficit: Anterograde Amnesia:** LLMs do not natively consolidate knowledge over time \[6\]. Their working memory, the **context window**, gets wiped \[6\].
*   **The Writing Challenge:** Writing a novel requires maintaining thousands of facts, character arcs, and world rules over hundreds of pages. **Trying to manage this complexity by manually writing text prompts over and over is doomed to fail** because you are constantly asking the computer to remember things it is biologically structured to forget \[6\].

# <a id="src-5"></a>Source: Writers Factory: Augmenting Narrative with Context Engineering (Citation 5)



## [Main Content](#src-main) 

### II. The Problem: LLM Amnesia vs. Story Complexity (1:30 – 3:30)

**(Goal: Explain the LLM’s inherent defects and why simple prompting fails the novelist.)**

*   **LLMs are Fallible:** These "people spirits" possess **jagged intelligence** and "cognitive deficits" \[6\].
*   **The Crucial Deficit: Anterograde Amnesia:** LLMs do not natively consolidate knowledge over time \[6\]. Their working memory, the **context window**, gets wiped \[6\].
*   **The Writing Challenge:** Writing a novel requires maintaining thousands of facts, character arcs, and world rules over hundreds of pages. **Trying to manage this complexity by manually writing text prompts over and over is doomed to fail** because you are constantly asking the computer to remember things it is biologically structured to forget \[6\].

# <a id="src-6"></a>Source: AI Workflow: Task Decomposition and Context Agents (Citation 6)



## [Main Content](#src-main) 

The demonstrated AI-assisted development workflow is centered on implementing a \*\*context management system\*\* around large language models (LLMs), such as Claude Code, combined with \*\*task decomposition\*\* to achieve greater productivity and reliability than using these tools out of the box.

This workflow was developed to teach the AI the specific development processes for a project, and it was eventually adopted by an engineering team at a $4 billion unicorn.

The workflow proceeds through defined phases using custom commands and specialized agents:

# <a id="src-7"></a>Source: The Agentic Development Pipeline: LLM Context Mastery (Citation 7)



## [Main Content](#src-main) 

The demonstrated AI-assisted development workflow is centered on implementing a \*\*context management system\*\* around large language models (LLMs), such as Claude Code, combined with \*\*task decomposition\*\* to achieve greater productivity and reliability than using these tools out of the box.

This workflow was developed to teach the AI the specific development processes for a project, and it was eventually adopted by an engineering team at a $4 billion unicorn.

The workflow proceeds through defined phases using custom commands and specialized agents:

# <a id="src-8"></a>Source: ARCHITECTURE.md (Citation 8)



## [Main Content](#src-main) 

# Writers Factory - Desktop App Architecture

**Version**: 2.0 (Consolidated) **Date**: November 22, 2025 **Status**: Foundation Complete, Writers Group Ready

\--------------------------------------------------------------------------------

## Executive Summary

Writers Factory is a **professional novel-writing IDE** that enforces a structured creative methodology while providing AI-powered assistance. It is designed for a **group of writers** who follow the **Narrative Protocol** methodology.

This document supersedes the Gemini architect's incremental approach and defines the complete system architecture based on:

# <a id="src-9"></a>Source: The Agentic Development Pipeline: LLM Context Mastery (Citation 9)



## [Main Content](#src-main) 

\* \*\*Initiation:\*\* The task begins using the \*\*\`plan task\` custom command\*\*.

\* \*\*Context Provisioning:\*\* The user provides vague guidance on \*how\* to implement the feature but is specific about the \*\*context required by each expert\*\*.

\* \*\*Task Decomposition:\*\* Complex research tasks are delegated to specialized \*\*research sub-agents\*\* (e.g., Vappy Expert sub-agent, Pipecat expert sub-agent). These sub-agents are responsible for research, not implementation.

\* \*\*Research Access:\*\* The research sub-agents are provided access to documentation, including local clones of repos, online documentation, and open API (Swagger) documentation for relevant systems (e.g., Pipecat, Vappy).

# <a id="src-10"></a>Source: Author’s Writing Dashboard (Book Writing Tracker) | annotated by Geoffrey (Citation 10)



## [Main Content](#src-main) 

fifth-lamb-825.notion.site Open original article

# Author’s Writing Dashboard (Book Writing Tracker)

Author: fifth-lamb-825 on Notion

Length: • 2 mins

Annotated by Geoffrey CarrHarris

Welcome! Firstly we want to thank you for purchasing our template, it really helps us and motivates us to make even more! Secondly, welcome to your all-in-one dashboard for writing you new book! Here you can do everything: plan, write, edit, publish, market and keep track of sales! Navigate through all the pages easily and keep track of your writing by adding each writing session via the button to see your progress on the chart! Good luck and Happy Writing!

# <a id="src-11"></a>Source: ARCHITECTURE.md (Citation 11)



## [Main Content](#src-main) 

*   `NARRATIVE PROTOCOL.md` - The creative methodology
*   `VISION_AND_ROADMAP.md` - The hierarchical structure vision
*   `writers-factory-core` - The existing tooling and workflows
*   Current `writers-factory-app` implementation

\--------------------------------------------------------------------------------

## Core Philosophy

### 1\. Structure Before Freedom

Writers must complete the **Preparation Phase** (Story Bible artifacts) before accessing the **Execution Phase** (drafting). The system enforces this.

### 2\. Hierarchy is Sacred

# <a id="src-12"></a>Source: Writers Factory: Augmenting Narrative with Context Engineering (Citation 12)



## [Main Content](#src-main) 

### III. The Solution: Context Engineering the Living Brain (3:30 – 6:30)

**(Goal: Introduce the Knowledge Graph and the "Structure Before Freedom" philosophy.)**

*   **Necessity of the Application:** To use the LLM's power effectively, we must use a specialized application—a **partial autonomy app**—designed to manage the intelligence layer \[7, 8\].
*   **Context Engineering:** The Factory’s solution is **Context Engineering**. The true state of your story is externalized and managed in the **Knowledge Graph**, which we call **The Living Brain** \[7, 9\].
*   **The Structure is Sacred:** The system enforces the core philosophy of **Structure Before Freedom** \[10\]. Writers must complete the **Preparation Phase** (Story Bible artifacts) before they can access the Execution Phase (drafting) \[10\].
    *   **Required Artifacts:** This involves creating structured files like **Protagonist.md** (defining Fatal Flaw and The Lie) and **Beat\_Sheet.md** (using the **Save the Cat! 15-Beat Structure**) \[11-13\].
*   **Metabolism and Memory:** This Graph is not static; it **evolves** \[9\]. The system implements a **Metabolism** phase \[9, 14\] where the **Consolidator Agent** runs in the background to parse chat history and saved text into updated graph nodes, ensuring the AI never "forgets" the established lore \[7, 9, 14\].

# <a id="src-13"></a>Source: The Agentic Development Pipeline: LLM Context Mastery (Citation 13)



## [Main Content](#src-main) 

\* \*\*Project Memory:\*\* Specific learnings and lessons are captured in a root documentation folder, structured with subfolders for different frameworks (e.g., \`pipecat\`). This project-specific memory acts as an advanced context management system, optimizing retrieval for future tasks. Expert sub-agents are prompted to check these learning folders.

\### 2. Planning and Research Phase

The process for implementing a new feature begins with a planning command that uses research agents to gather necessary context:

# <a id="src-15"></a>Source: The Agentic Development Pipeline: LLM Context Mastery (Citation 15)



## [Main Content](#src-main) 

The entire workflow functions like a highly specialized research team and editor, where the AI handles the bulk of research, drafting, and iterative execution, but the user maintains control by setting goals, correcting idiomatic framework usage, and signing off on the plan and decisions before committing code.

# <a id="src-16"></a>Source: Scrivener meets VS Code meets the writer’s future.md (Citation 16)



## [Main Content](#src-main) 

# **Scrivener meets VS Code meets the writer’s future**

This idea captures the strengths of:

*   **Scrivener:** Renowned for structuring, organizing, story planning, and easy navigation through large, multi-part manuscripts—ideal for creative writers and novelists.
*   **VS Code:** Modular, extensible, file-centric, developer-focused workspace—fast navigation, sidebars, plugin ecosystem, and split editing for technical and power users.
*   **Writer’s Future (your vision):** Seamless integration of AI agents, local and API-driven creativity, live analysis, context-aware drafting, stylometry, voice-guided editing, and knowledge base connectivity.

# <a id="src-17"></a>Source: The Agentic Development Pipeline: LLM Context Mastery (Citation 17)



## [Main Content](#src-main) 

\* \*\*Summary Generation:\*\* Sub-agents provide detailed summaries back to the main orchestrating agent. This approach ensures the orchestrating agent receives rich context without consuming excess tokens, as only the summary is returned.

\### 3. Review, Direction, and Iteration Phase

The orchestrating agent produces a series of documents based on the research, which the user must review before implementation.

The key documents generated are:

1\. \*\*Implementation Notes:\*\* Contains the full analysis provided by the sub-agents for review. The Pipecat sub-agent is specifically instructed to identify the \*\*idiomatic way\*\* of solving problems within that framework.

# <a id="src-18"></a>Source: TASK_Creation_Wizard.md (Citation 18)



## [Main Content](#src-main) 

# Task: Design Creation Wizard Pipeline for Writers Factory

**Priority**: High **Assigned To**: Cloud Agent **Estimated Time**: 6-8 hours **Dependencies**: UX Design task (can work in parallel)

\--------------------------------------------------------------------------------

## Context

You are designing a guided wizard to take a writer from "blank canvas" to "ready to write" - essentially building a complete story bible through an intelligent, conversational AI process.

This wizard is **optional** but highly valuable for writers starting fresh. It should embody best practices from successful novelists and editors, making expert writing knowledge accessible to beginners.

# <a id="src-19"></a>Source: WORKFLOWS.md (Citation 19)



## [Main Content](#src-main) 

### WorkflowResult

Container for workflow execution results.

# <a id="src-20"></a>Source: DOCS_INDEX.md (Citation 20)



## [Main Content](#src-main) 

<table><thead><tr><th><span _ngcontent-ng-c2328698254="" data-start-index="2395" class="ng-star-inserted">Group</span></th><th><span _ngcontent-ng-c2328698254="" data-start-index="2400" class="ng-star-inserted">Base Path</span></th><th><span _ngcontent-ng-c2328698254="" data-start-index="2409" class="ng-star-inserted">Description</span></th></tr></thead><tbody><tr><td><span _ngcontent-ng-c2328698254="" data-start-index="2420" class="ng-star-inserted">System</span></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted" data-start-index="2426">/agents</code><span _ngcontent-ng-c2328698254="" data-start-index="2433" class="ng-star-inserted">, </span><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted" data-start-index="2435">/manager</code></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2443" class="ng-star-inserted">Agent listing, health checks</span></td></tr><tr><td><span _ngcontent-ng-c2328698254="" data-start-index="2471" class="ng-star-inserted">Files</span></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted" data-start-index="2476">/files/{path}</code></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2489" class="ng-star-inserted">Read/write files</span></td></tr><tr><td><span _ngcontent-ng-c2328698254="" data-start-index="2505" class="ng-star-inserted">Graph</span></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted" data-start-index="2510">/graph/*</code></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2518" class="ng-star-inserted">Knowledge graph operations</span></td></tr><tr><td><span _ngcontent-ng-c2328698254="" data-start-index="2544" class="ng-star-inserted">Sessions</span></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted" data-start-index="2552">/session/*</code></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2562" class="ng-star-inserted">Chat session management</span></td></tr><tr><td><span _ngcontent-ng-c2328698254="" data-start-index="2585" class="ng-star-inserted">Consolidator</span></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted" data-start-index="2597">/graph/consolidate</code></td><td><span _ngcontent-ng-c2328698254="" data-start-index="2615" class="ng-star-inserted">"The Liver" - session digestion</span></td></tr><tr><td><span _ngcontent-ng-c2328698254="" data-start-index="2646" class="ng-star-inserted">Health</span></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="2652">/health/status</code></td><td>Combined dashboard data</td></tr><tr><td>NotebookLM</td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="2699">/notebooklm/*</code></td><td>External research queries</td></tr><tr><td>Story Bible</td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="2748">/story-bible/*</code></td><td>Phase 2 system</td></tr></tbody></table>

### Key Endpoints

# <a id="src-21"></a>Source: API_REFERENCE.md (Citation 21)



## [Main Content](#src-main) 

\--------------------------------------------------------------------------------

## Health Dashboard

### `GET /health/status`

Combined health endpoint for the dashboard.

Returns graph stats, conflicts, and uncommitted events in one call.

**Response:**

\--------------------------------------------------------------------------------

## NotebookLM Integration

# <a id="src-22"></a>Source: The Agentic Development Pipeline: LLM Context Mastery (Citation 22)



## [Main Content](#src-main) 

2\. \*\*The Plan:\*\* Outlines the overall approach to solving the problem, which the user reviews for modifications.

3\. \*\*Decisions File:\*\* Lists decisions the assistant has made autonomously and any \*\*pending decisions\*\* requiring user input.

4\. \*\*Status File:\*\* Communicates the current progress of the task implementation.

The user reviews these documents, providing necessary corrections, such as enforcing specific configurations (e.g., JSON only configuration, strict schema, error message handling). Once the planning documents are satisfactory, the user commands the agent to complete the implementation. A \*\*Task Context Tracker Assistant\*\* automatically keeps these documents updated during subsequent implementation cycles and iterations.

# <a id="src-23"></a>Source: DIRECTOR_MODE_SPECIFICATION.md (Citation 23)



## [Main Content](#src-main) 

This document specifies the complete workflow from Story Bible completion through final scene delivery.

\--------------------------------------------------------------------------------

## Prerequisites

Before Director Mode activates, the following must be complete:

### From Architect Mode (Phase 2A)

*   \[ \] Protagonist template (Fatal Flaw, The Lie, Arc)
*   \[ \] Beat Sheet (15 beats with percentages)
*   \[ \] Theme (central theme, theme statement)
*   \[ \] World Rules (fundamental constraints)
*   \[ \] Cast (supporting characters by function)

# <a id="src-24"></a>Source: DOCS_INDEX.md (Citation 24)



## [Main Content](#src-main) 

\--------------------------------------------------------------------------------

## Core Concepts

### The Narrative Protocol

Writers Factory implements the **Narrative Protocol** - a structured approach to novel writing:

# <a id="src-25"></a>Source: TASK_Creation_Wizard.md (Citation 25)



## [Main Content](#src-main) 

**Beat 1: Opening Image (0-1%)**

**Beat 2: Theme Stated (5%)**

**Beat 3: Setup (1-10%)**

# <a id="src-26"></a>Source: DIRECTOR_MODE_SPECIFICATION.md (Citation 26)



## [Main Content](#src-main) 

# Director Mode Specification

**Version**: 2.0 **Date**: November 23, 2025 **Status**: Backend Implementation Complete ✅

\--------------------------------------------------------------------------------

## Executive Summary

Director Mode is the second operational mode of the Foreman agent, activated after the Story Bible is complete. It orchestrates the **scene creation pipeline** - a multi-stage process that generates, scores, and enhances scenes using a combination of:

*   **Tournament**: Multiple AI agents compete on the same task
*   **Multiplier**: Each agent generates 5 creative variants
*   **Scoring**: 100-point rubric evaluates all variants
*   **Enhancement**: Surgical fixes polish the selected scene

# <a id="src-27"></a>Source: The Writers Factory: Structuring AI for Novelists (Citation 27)



## [Main Content](#src-main) 

### IV. Factory Architecture: Auditing the Generation-Verification Loop (6:30 – 8:30)

**(Goal: Show the students how they will interact with the multi-agent system and its checks.)**

*   **The Core Loop:** Since the LLM is fallible, the human must remain the **auditor** \[15, 16\]. The Factory is engineered to make this **verification phase as fast as possible** \[15\].
*   **Managing Generation (The Autonomy Slider in Practice):** We control agency through **Director Mode** \[17\].
    *   **Agent Pool:** Students will choose from a **Squad** of agents—including **Claude Sonnet 4.5** (best for voice and nuance), **GPT-4o** (best for polish and structure), and **Grok** (best for unconventional takes) \[18, 19\].
    *   **Tournament Mode:** When writing a scene, the system runs a **Tournament + Multiplier** pipeline \[20, 21\]. This means multiple agents generate up to 5 variants each, creating up to **25 unique approaches** to a single scene, maximizing the creative exploration space \[19, 20\].
*   **Managing Verification (The Auditor’s Tools):** You, the writer, audit the output using sophisticated diagnostics:
    *   **The 100-Point Scoring Rubric:** Every generated scene is scored based on explicit criteria, including **Voice Authenticity** (30% weight by default), **Character Consistency** (20%), and **Metaphor Discipline** (20%) \[22, 23\]. You can even customize these weights \[23, 24\].
    *   **Health Checks:** The system runs **narrative-aware** checks, moving beyond simple graph errors \[25-27\]. It flags issues like **Dropped Threads**, checks if the **Fatal Flaw has been tested recently**, and monitors **Beat Progress** against the 15-Beat Structure \[25, 26\].
    *   **AI Anti-Patterns:** Critically, the **Scene Analyzer** runs a pass for **Universal AI Anti-Patterns** \[28\], flagging generic phrases like _"plays a vital/significant/crucial/pivotal role"_ or excessive use of words like **"tapestry"** \[29, 30\]. This helps you remove the "stylistic fingerprint" of the AI \[31\].
*   **The Workflow:** This entire generation and verification process happens within the application, utilizing visual efficiency \[32\]. For quick action, you can use shortcuts like `Cmd+Shift+A` to ask an agent about a text selection or `Cmd+Shift+G` to look up context in the Knowledge Graph \[33\].

# <a id="src-28"></a>Source: Writers Factory: Augmenting Narrative with Context Engineering (Citation 28)



## [Main Content](#src-main) 

### IV. Factory Architecture: Auditing the Generation-Verification Loop (6:30 – 8:30)

**(Goal: Show the students how they will interact with the multi-agent system and its checks.)**

*   **The Core Loop:** Since the LLM is fallible, the human must remain the **auditor** \[15, 16\]. The Factory is engineered to make this **verification phase as fast as possible** \[15\].
*   **Managing Generation (The Autonomy Slider in Practice):** We control agency through **Director Mode** \[17\].
    *   **Agent Pool:** Students will choose from a **Squad** of agents—including **Claude Sonnet 4.5** (best for voice and nuance), **GPT-4o** (best for polish and structure), and **Grok** (best for unconventional takes) \[18, 19\].
    *   **Tournament Mode:** When writing a scene, the system runs a **Tournament + Multiplier** pipeline \[20, 21\]. This means multiple agents generate up to 5 variants each, creating up to **25 unique approaches** to a single scene, maximizing the creative exploration space \[19, 20\].
*   **Managing Verification (The Auditor’s Tools):** You, the writer, audit the output using sophisticated diagnostics:
    *   **The 100-Point Scoring Rubric:** Every generated scene is scored based on explicit criteria, including **Voice Authenticity** (30% weight by default), **Character Consistency** (20%), and **Metaphor Discipline** (20%) \[22, 23\]. You can even customize these weights \[23, 24\].
    *   **Health Checks:** The system runs **narrative-aware** checks, moving beyond simple graph errors \[25-27\]. It flags issues like **Dropped Threads**, checks if the **Fatal Flaw has been tested recently**, and monitors **Beat Progress** against the 15-Beat Structure \[25, 26\].
    *   **AI Anti-Patterns:** Critically, the **Scene Analyzer** runs a pass for **Universal AI Anti-Patterns** \[28\], flagging generic phrases like _"plays a vital/significant/crucial/pivotal role"_ or excessive use of words like **"tapestry"** \[29, 30\]. This helps you remove the "stylistic fingerprint" of the AI \[31\].
*   **The Workflow:** This entire generation and verification process happens within the application, utilizing visual efficiency \[32\]. For quick action, you can use shortcuts like `Cmd+Shift+A` to ask an agent about a text selection or `Cmd+Shift+G` to look up context in the Knowledge Graph \[33\].

# <a id="src-29"></a>Source: DOCS_INDEX.md (Citation 29)



## [Main Content](#src-main) 

Writers Factory implements the **Narrative Protocol** - a structured approach to novel writing:

1\. **Phase 1: NotebookLM Preparation** - Upload research to Google NotebookLM

2\. **Phase 2: Story Bible System** - Generate structured artifacts (enforced before drafting)

3\. **Phase 3: Execution** - Draft scenes with AI assistance

4\. **Phase 4: Archive** - Finalize and store completed scenes

### Key Artifacts

<table><thead><tr><th>Artifact</th><th>Location</th><th>Purpose</th></tr></thead><tbody><tr><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1660">Protagonist.md</code></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1674">content/Characters/</code></td><td>Character with Fatal Flaw &amp; The Lie</td></tr><tr><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1728">Beat_Sheet.md</code></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1741">content/Story Bible/Structure/</code></td><td>15-beat Save the Cat! structure</td></tr><tr><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1802">Scene_Strategy.md</code></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1819">content/Story Bible/Structure/</code></td><td>Scene-level planning</td></tr><tr><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1869">04_Theme.md</code></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1880">content/Story Bible/Themes_and_Philosophy/</code></td><td>Theme documentation</td></tr><tr><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1941">Rules.md</code></td><td><code _ngcontent-ng-c2328698254="" class="code ng-star-inserted highlighted" data-start-index="1949">content/World Bible/</code></td><td>World-building rules</td></tr></tbody></table>

### Level 2 Health Checks

Before proceeding to Phase 3 (Execution), the system validates:

*   \[ \] Protagonist file exists
*   \[ \] Protagonist has Fatal Flaw defined

# <a id="src-31"></a>Source: DIRECTOR_MODE_SPECIFICATION.md (Citation 31)



## [Main Content](#src-main) 

### Step 1: Scaffold Generation

For each chapter, the Foreman generates a **Gold Standard Scaffold** by reading from the Knowledge Graph.

# <a id="src-32"></a>Source: Cursor: The Iron Man Suit of Software 3.0 Development (Citation 32)



## [Main Content](#src-main) 

\### C. The Autonomy Slider

The "autonomy slider" is a core concept that defines Cursor's theoretical role as a partial autonomy product. It gives the user control over how much agency the AI is given for a specific task based on its complexity. The goal is to keep the AI "on the leash" to prevent it from becoming "overreactive" and generating overly large outputs (like 10,000-line diffs) that would bottleneck human verification.

Cursor offers several levels on this slider:

1\. \*\*Tap completion:\*\* The user is "mostly in charge" (lowest autonomy).

# <a id="src-34"></a>Source: The Agentic Development Pipeline: LLM Context Mastery (Citation 34)



## [Main Content](#src-main) 

\### 4. Supporting Commands

The workflow includes specialized commands for debugging and maintenance:

\* \*\*\`root cause analysis\`:\*\* This is a collaborative debugging procedure. The assistant investigates an issue, forms a hypothesis, adds debug logging, starts the server, waits for the user to reproduce the issue, checks the logs, and if the hypothesis is correct, it resets the codebase (using Git), applies the fix, and hands it back to the user for testing.

\* \*\*\`create pull request\`:\*\* This command generates a document in the docs folder containing all the necessary information for the user to create a pull request, including branch differences and suggested GitHub CLI commands.

# <a id="src-35"></a>Source: API_REFERENCE.md (Citation 35)



## [Main Content](#src-main) 

**Response:**

### `GET /session/{session_id}/history`

Retrieve chat history for a session.

**Parameters:**

*   `session_id` (path): Session UUID
*   `limit` (query): Max events to return (default: 50)

**Response:**

### `GET /session/{session_id}/stats`

Get session statistics for compaction decisions.

**Response:**

# <a id="src-36"></a>Source: Phase 3D Graph Health Service - Complete Implementation Plan.md (Citation 36)



## [Main Content](#src-main) 

## Problem Statement

Scene Analyzer (Phase 3B) validates individual scenes but **cannot detect**:

*   **Pacing Plateaus** → 3 consecutive chapters with flat tension
*   **Dropped Threads** → Setup introduced but never resolved
*   **Character Absences** → Supporting character vanishes for 10+ chapters
*   **Beat Deviation** → Act 2 finishes at wrong percentage of manuscript
*   **Flaw Challenge Gaps** → Protagonist's Fatal Flaw untested for too long
*   **Timeline Conflicts** → Character in two places simultaneously

\--------------------------------------------------------------------------------

# <a id="src-37"></a>Source: Context Engineering: Architecting Narrative in Software 3.0 (Citation 37)



## [Main Content](#src-main) 

*   **Opening:** We are entering the industry at an "extremely unique and very interesting time" because **software is changing fundamentally** \[1\]. For 70 years, we primarily used **Software 1.0** (code written by humans) \[1, 2\]. Then came **Software 2.0** (neural networks trained on data) \[2\].
*   **The Paradigm Shift:** Today, we are firmly in **Software 3.0**, where the Large Language Model (LLM) itself is a new kind of computer \[3\]. Your **prompts are now programs** written in natural language (English) \[3, 4\].
*   **Introducing the Factory:** The Writers Factory is built entirely within this **Software 3.0** paradigm. It is our response to the question: How do we rewrite the process of narrative creation now that we can program computers in English?

