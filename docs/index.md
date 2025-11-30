---
layout: default
title: Welcome
---

<div style="text-align: center; padding-top: 50px;">

# AI and the One-Week Novel
### Skoltech ISP 2026

<br>

> **"We are not just writing a novel; we are engineering a synthetic cognitive system."**

<br>

This is an experimental intensive course exploring the intersection of **Large Language Models**, **System Architecture**, and **Creative Narratology**.

---

### For University Administration
This course is designed to bridge the gap between engineering systems and creative arts.
*   **Duration:** 1 Week (Intensive)
*   **Format:** Dual Track (Creative & Technical)
*   **Objective:** To test the limits of Long-Context AI in complex narrative generation.

---

### For Students
Access to the **Writers Factory** software, API keys, and daily schedule is restricted to enrolled students.

<div id="login-form" style="margin-top: 30px; padding: 20px; background: #f6f8fa; border-radius: 6px; display: inline-block;">
    <p><strong>Enter Access Code:</strong></p>
    <input type="password" id="password-input" placeholder="Enter code..." onkeydown="checkEnter(event)" style="padding: 8px; border-radius: 4px; border: 1px solid #ccc;">
    <button onclick="checkPassword()" style="padding: 8px 16px; background: #2ea44f; color: white; border: none; border-radius: 4px; cursor: pointer;">Enter Class</button>
    <p id="error-msg" style="color: red; display: none; margin-top: 10px;">Incorrect Code</p>
</div>

</div>

<script>
function checkPassword() {
    var password = document.getElementById("password-input").value;
    // Simple client-side check. 
    // The real security is the Private Repo for the binary downloads.
    if (password === "skoltech2026" || password === "admin") {
        sessionStorage.setItem('authenticated', 'true');
        window.location.href = "{{ '/student_portal' | relative_url }}";
    } else {
        document.getElementById("error-msg").style.display = "block";
    }
}

function checkEnter(event) {
    if (event.key === "Enter") {
        checkPassword();
    }
}
</script>
