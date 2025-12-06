---
layout: default
title: Download
---

<div id="login-section" class="login-form">
    <h2>Student Access</h2>
    <p class="text-muted">Enter your course access code to download Writers Factory.</p>
    <input type="password" id="password-input" placeholder="Access Code..." onkeydown="if(event.key==='Enter')checkPassword()">
    <button onclick="checkPassword()" class="btn-primary" style="width: 100%;">Get Access</button>
    <p id="error-msg" style="color: var(--error); display: none; margin-top: 12px;">Incorrect Code</p>
    <p class="text-muted" style="margin-top: 24px; font-size: 0.9rem;">
        Not enrolled yet? <a href="/about">Learn about the course</a>
    </p>
</div>

<div id="portal-content" markdown="1">

# Download Writers Factory

You're in! Here's everything you need to get started.

---

## Choose Your Track

<div class="track-grid">
    <div class="card writer" style="border-top: 4px solid var(--accent-gold);">
        <h3>Writer Track</h3>
        <p><strong>Goal:</strong> Write a 15k+ word novella</p>
        <p><strong>Setup:</strong> Download & Run (No coding)</p>
        <p class="text-muted">The app includes pre-paid API keys (~$500 value). Do not share.</p>
        <a href="https://github.com/gcharris/writers-factory-desktop/releases/latest" class="btn-primary" style="margin-top: 16px; display: inline-block;">Download App</a>
    </div>
    <div class="card architect" style="border-top: 4px solid var(--accent-blue);">
        <h3>Architect Track</h3>
        <p><strong>Goal:</strong> Optimize the Context Engine</p>
        <p><strong>Setup:</strong> Clone repo & modify code</p>
        <p class="text-muted">Full source access. Submit PRs for extra credit.</p>
        <a href="https://github.com/gcharris/writers-factory-desktop" class="btn-secondary" style="margin-top: 16px; display: inline-block;">View Source</a>
    </div>
</div>

---

## Quick Start

1. **Download** the app for your platform (Mac/Windows)
2. **Launch** it - you should see "Welcome to Writers Factory"
3. **Read** the [Pre-Flight Checklist](/learn/preflight) before Day 1
4. **Prepare** your NotebookLM with 5,000+ words of your writing

---

## Important: Confidentiality

> **The Writer Track app includes pre-paid API keys worth ~$500/student.**
> - Do NOT share the app binary with anyone outside the course
> - Do NOT upload to public file servers
> - Access is tracked - leaked keys will be revoked

---

## Resources

| Resource | Link |
|----------|------|
| Pre-Flight Checklist | [/learn/preflight](/learn/preflight) |
| 5 Core Notebooks | [/learn/notebooks](/learn/notebooks) |
| Full Schedule | [/schedule](/schedule) |
| Writer's Journey | [/journey](/journey) |
| Submit Your Work | [/portal/submit](/portal/submit) |

---

## Need Help?

- [Troubleshooting Guide](https://github.com/gcharris/writers-factory-desktop/wiki/Troubleshooting)
- [Discussion Board](https://github.com/gcharris/writers-factory-desktop/discussions)
- [Report a Bug](https://github.com/gcharris/writers-factory-desktop/issues)

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
