---
layout: default
title: Student Portal
protected: true
---

<div id="login-section" class="login-form">
    <h2>Student Access</h2>
    <p class="text-muted">Enter your course access code to continue.</p>
    <input type="password" id="password-input" placeholder="Access Code..." onkeydown="if(event.key==='Enter')checkPassword()">
    <button onclick="checkPassword()" class="btn-primary" style="width: 100%;">Enter Portal</button>
    <p id="error-msg" style="color: var(--error); display: none; margin-top: 12px;">Incorrect Code</p>
</div>

<div id="portal-content" style="display: none;" markdown="1">

# Student Portal: AI and the One-Week Novel

**Course Code:** ISP-2026 | **Format:** 1-week intensive | **Platform:** Writers Factory Desktop

---

## READ THIS FIRST: Confidentiality

> **IMPORTANT:** The "Writer Track" version of this software includes **pre-paid API keys** (worth ~$500/student).
> - **DO NOT share this binary** with anyone outside the course.
> - **DO NOT upload it** to public file servers.
> - Access is tracked. Leaked keys will result in immediate revocation.

---

## Choose Your Track

| The Writer Track | The Architect Track |
|------------------|---------------------|
| **Goal:** Write a novella (15k+ words) | **Goal:** Optimize the Context Engine |
| **Activity:** Creative Writing & Analysis | **Activity:** Prompt Engineering, Graph Logic |
| **Setup:** Download & Run (No coding) | **Setup:** Clone Repo & Modify Code |
| [Download Mac/Windows App](https://github.com/gcharris/writers-factory-desktop/releases/latest) | [View Source Code](https://github.com/gcharris/writers-factory-desktop) |

---

## Quick Navigation

<div class="track-grid">
    <div class="card" style="border-top: 4px solid var(--accent-gold);">
        <h4><a href="/portal/schedule">Weekly Schedule</a></h4>
        <p class="text-muted">Day-by-day breakdown of the intensive</p>
    </div>
    <div class="card" style="border-top: 4px solid var(--accent-cyan);">
        <h4><a href="/portal/tools/preflight">Pre-Flight Checklist</a></h4>
        <p class="text-muted">Everything you need before Day 1</p>
    </div>
</div>

---

## Pre-Course Setup

**Deadline:** 48 hours before Day 1

1. **Read the Philosophy:** [About Writers Factory](/about)
2. **Install the Software:** Use the link above for your track
3. **Health Check:** Open the app. If you see "Welcome to Writers Factory", you're ready.
4. **NotebookLM Preparation:** Create a NotebookLM account and upload 5,000 words of *personal writing* to train your Voice Avatar.

---

## Weekly Schedule Overview

| Day | Focus | Goal |
|-----|-------|------|
| **Day 1** | The Machine & The Voice | Set up, extract voice profile |
| **Day 2** | Narrative Architecture | Complete 15-beat outline |
| **Day 3** | The Drafting Pipeline | 50% of draft complete |
| **Day 4** | Diagnostics & Polish | Debug narrative, polish excerpt |
| **Day 5** | Showcase | Final assembly, presentations |

<p><a href="/portal/schedule" class="btn-secondary">View Full Schedule</a></p>

---

## Reference Documentation

<div class="track-grid">
    <div class="card">
        <h4>Getting Started</h4>
        <ul>
            <li><a href="/portal/tools/preflight"><strong>Pre-Flight Checklist</strong></a></li>
            <li><a href="/portal/tools/notebooks">5 Core Notebooks</a></li>
            <li><a href="/portal/tools/distillation">Distillation Prompts</a></li>
            <li><a href="/portal/tools/journey">Writer's Journey</a></li>
        </ul>
    </div>
    <div class="card">
        <h4>Core Concepts</h4>
        <ul>
            <li><a href="/portal/tools/context">Context Engineering</a></li>
            <li><a href="/portal/tools/models">LLM Models</a></li>
            <li><a href="/portal/tools/anti-patterns">Anti-Patterns</a></li>
        </ul>
    </div>
    <div class="card">
        <h4>System Deep Dives</h4>
        <ul>
            <li><a href="/portal/tools/graphrag">GraphRAG Conceptual</a></li>
            <li><a href="/portal/tools/graphrag-technical">GraphRAG Technical</a></li>
            <li><a href="/portal/tools/integration">Systems Integration</a></li>
        </ul>
    </div>
    <div class="card">
        <h4>Writing Modes</h4>
        <ul>
            <li><a href="/portal/tools/voice">Voice Calibration</a></li>
            <li><a href="/portal/tools/director">Director Mode</a></li>
            <li><a href="/portal/tools/agents">Agent Instructions</a></li>
        </ul>
    </div>
</div>

---

## Resources & Help

- [Troubleshooting Guide](https://github.com/gcharris/writers-factory-desktop/wiki/Troubleshooting)
- [Discussion Board](https://github.com/gcharris/writers-factory-desktop/discussions)
- [Report a Bug](https://github.com/gcharris/writers-factory-desktop/issues)

---

## Ownership

- **Your Writing:** All creative work belongs to you. Full ownership and control.
- **The Software:** Writers Factory remains property of Geoffrey Carr-Harris.
- **Engineer Contributions:** Technical contributions may be incorporated into future versions with acknowledgment.

---

*Writers Factory is an open-source AI writing environment built for Skoltech ISP 2026.*

</div>

<script>
// Check if already authenticated
if (sessionStorage.getItem('authenticated')) {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('portal-content').classList.add('authenticated');
}

function checkPassword() {
    var password = document.getElementById("password-input").value;
    if (password === "skoltech2026" || password === "admin") {
        sessionStorage.setItem('authenticated', 'true');
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('portal-content').classList.add('authenticated');
    } else {
        document.getElementById("error-msg").style.display = "block";
        var input = document.getElementById("password-input");
        input.style.borderColor = 'var(--error)';
        setTimeout(() => { input.style.borderColor = ''; }, 1000);
    }
}
</script>
