---
layout: default
title: Student Projects
---

# 🏆 Student Projects Showcase

> **"The best way to predict the future is to invent it."**

Here we celebrate the output of the Writers Factory. From completed novellas to critical system architecture upgrades, this is what our students have built in just one week.

<div style="text-align: center; margin: 30px 0;">
    <a href="{{ '/submission_guide' | relative_url }}" style="background: #2ea44f; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">📤 Submit Your Project</a>
</div>

---

<!-- Community Showcase Section -->
<style>
    .showcase-section {
        max-width: 1000px;
        margin: 40px auto;
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
    
    @media (max-width: 768px) {
        .showcase-grid {
            grid-template-columns: 1fr;
        }
    }
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
