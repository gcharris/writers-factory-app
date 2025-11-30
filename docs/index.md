---
layout: default
title: Welcome
---

<style>
    .hero-container {
        text-align: center;
        padding: 40px 20px;
        max-width: 800px;
        margin: 0 auto;
    }
    .hero-image {
        width: 100%;
        max-width: 800px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 30px;
    }
    .course-title {
        font-size: 2.5em;
        font-weight: 800;
        margin-bottom: 10px;
        background: -webkit-linear-gradient(45deg, #2c3e50, #3498db);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .course-subtitle {
        font-size: 1.2em;
        color: #666;
        margin-bottom: 40px;
        font-style: italic;
    }
    .login-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        display: inline-block;
        margin-top: 20px;
        max-width: 400px;
        width: 100%;
    }
    .login-input {
        width: 100%;
        padding: 12px;
        margin: 10px 0;
        border: 1px solid #ddd;
        border-radius: 8px;
        font-size: 16px;
        box-sizing: border-box;
    }
    .login-btn {
        width: 100%;
        padding: 12px;
        background: linear-gradient(45deg, #2ea44f, #218c3d);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: transform 0.1s;
    }
    .login-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(46, 164, 79, 0.3);
    }
    .admin-note {
        font-size: 0.9em;
        color: #888;
        margin-top: 30px;
        border-top: 1px solid #eee;
        padding-top: 20px;
    }
</style>

<div class="hero-container">
    
    <img src="{{ '/assets/images/writers_factory_hero.png' | relative_url }}" alt="The Cyborg Novelist" class="hero-image">

    <h1 class="course-title">AI and the One-Week Novel</h1>
    <div class="course-subtitle">Skoltech ISP 2026</div>

    <p style="font-size: 1.1em; line-height: 1.6; color: #444;">
        <strong>"We are not just writing a novel; we are engineering a synthetic cognitive system."</strong>
    </p>

    <div class="login-card">
        <h3>Student Access</h3>
        <p style="font-size: 0.9em; color: #666; margin-bottom: 20px;">Enter your course access code to view the schedule and download the software.</p>
        
        <input type="password" id="password-input" class="login-input" placeholder="Enter Access Code..." onkeydown="checkEnter(event)">
        <button onclick="checkPassword()" class="login-btn">Enter Class</button>
        <p id="error-msg" style="color: #d73a49; display: none; margin-top: 10px; font-size: 0.9em;">Incorrect Code</p>
    </div>

    <div class="admin-note">
        <p><strong>For University Administration:</strong> This is an experimental intensive course exploring the intersection of Large Language Models, System Architecture, and Creative Narratology.</p>
    </div>

</div>

<!-- Community Showcase Section -->
<style>
    .showcase-section {
        max-width: 1000px;
        margin: 60px auto;
        padding: 20px;
    }
    .showcase-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 40px;
    }
    .showcase-col h2 {
        font-size: 1.5em;
        margin-bottom: 20px;
        border-bottom: 2px solid #eee;
        padding-bottom: 10px;
        color: #2c3e50;
    }
    .book-card {
        background: white;
        border: 1px solid #eee;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        transition: transform 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .book-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .book-icon {
        font-size: 2em;
        margin-right: 15px;
    }
    .book-info h4 {
        margin: 0;
        color: #333;
    }
    .book-info p {
        margin: 5px 0 0;
        font-size: 0.85em;
        color: #666;
    }
    .tech-log {
        font-family: 'Courier New', monospace;
        background: #f6f8fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e1e4e8;
    }
    .log-entry {
        margin-bottom: 10px;
        font-size: 0.9em;
        color: #24292e;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
    .log-entry:last-child {
        border-bottom: none;
    }
    .badge {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.75em;
        font-weight: bold;
    }
    .badge-creative { background: #d4edda; color: #155724; }
    .badge-tech { background: #cce5ff; color: #004085; }
</style>

<div class="showcase-section">
    <div class="showcase-grid">
        <!-- Creative Track Output -->
        <div class="showcase-col">
            <h2>📚 Factory Output (Latest Novels)</h2>
            <div class="book-card">
                <div class="book-icon">📕</div>
                <div class="book-info">
                    <h4>The Silicon Dream</h4>
                    <p>by <em>Student Team Alpha</em> • Sci-Fi • 18k words</p>
                </div>
            </div>
            <div class="book-card">
                <div class="book-icon">📗</div>
                <div class="book-info">
                    <h4>Echoes of St. Petersburg</h4>
                    <p>by <em>Maria K.</em> • Historical Fiction • 22k words</p>
                </div>
            </div>
            <div class="book-card">
                <div class="book-icon">📘</div>
                <div class="book-info">
                    <h4>Protocol Zero</h4>
                    <p>by <em>Alexei V.</em> • Cyberpunk Thriller • 15k words</p>
                </div>
            </div>
        </div>

        <!-- Architect Track Output -->
        <div class="showcase-col">
            <h2>🛠️ System Upgrades (Commits)</h2>
            <div class="tech-log">
                <div class="log-entry">
                    <span class="badge badge-tech">PR #42</span>
                    <strong>Optimized Graph Retrieval</strong>
                    <br><span style="color:#586069">Merged by <em>dmitry_dev</em> 2 hours ago</span>
                </div>
                <div class="log-entry">
                    <span class="badge badge-tech">PR #41</span>
                    <strong>Added "Noir" Style Vector</strong>
                    <br><span style="color:#586069">Merged by <em>sarah_writer</em> 5 hours ago</span>
                </div>
                <div class="log-entry">
                    <span class="badge badge-tech">Fix</span>
                    <strong>Patched Memory Leak in Session Manager</strong>
                    <br><span style="color:#586069">Merged by <em>admin</em> yesterday</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function checkPassword() {
    var password = document.getElementById("password-input").value;
    if (password === "skoltech2026" || password === "admin") {
        sessionStorage.setItem('authenticated', 'true');
        window.location.href = "{{ '/student_portal' | relative_url }}";
    } else {
        document.getElementById("error-msg").style.display = "block";
        // Shake animation
        var card = document.querySelector('.login-card');
        card.style.transform = 'translateX(10px)';
        setTimeout(() => { card.style.transform = 'translateX(-10px)'; }, 100);
        setTimeout(() => { card.style.transform = 'translateX(0)'; }, 200);
    }
}

function checkEnter(event) {
    if (event.key === "Enter") {
        checkPassword();
    }
}
</script>
