---
layout: default
title: How to Submit
protected: true
---

<script>
if (!sessionStorage.getItem('authenticated')) {
    window.location.href = "/portal/";
}
</script>

# How to Submit Your Work

> **"Shipping is a feature."**

Because this course is hosted on GitHub, we don't use a "file upload" form. We use **Pull Requests**. This ensures your work is permanently archived in the repository's history.

---

## Option A: The "Architect" Way (Recommended)
*Best for: Engineers and those who want the "Contributor" badge.*

1.  **Fork the Repository:** Click the `Fork` button at the top right of the GitHub page.
2.  **Add Your File:**
    *   Upload your PDF/EPUB to `docs/assets/student_projects/`.
    *   Name it clearly: `Title_YourName.pdf`.
3.  **Update the Showcase:**
    *   Edit `docs/showcase.md`.
    *   Add a new "Book Card" entry for your project (copy an existing one).
    *   Link it to your file: `{{ '/assets/student_projects/Title_YourName.pdf' | relative_url }}`.
4.  **Open a Pull Request:**
    *   Commit your changes.
    *   Open a PR against the `main` branch.
    *   **Title:** "Submission: [Book Title] by [Your Name]".

---

## Option B: The "Writer" Way (Easy)
*Best for: Pure creative track students.*

1.  **Go to the [Discussions Tab](https://github.com/gcharris/writers-factory-desktop/discussions).**
2.  **Create a New Discussion** in the "Showcase" category.
3.  **Title:** "Submission: [Book Title]".
4.  **Body:**
    *   Attach your PDF/EPUB (drag and drop).
    *   Write a short blurb (Genre, Word Count).
5.  **The Admin** will manually add it to the website for you.

---

## What to Submit
*   **The Novel:** PDF or EPUB format.
*   **The Cover:** Optional PNG/JPG (we will resize it).
*   **The Metadata:** Title, Author Name (or Pseudonym), Genre, Word Count.

---

## 🎨 Creating Your Cover (The "Muse" Phase)

Since we are "Engineering the Muse," we encourage you to use AI tools to generate your cover art.

**Recommended Tools:**
*   **Midjourney** (Best for artistic style)
*   **DALL-E 3** (Best for following instructions)
*   **Stable Diffusion** (Best for local control)

**Prompting Strategy:**
> "A book cover for a [GENRE] novel titled '[TITLE]'. The central image is [KEY SYMBOL]. The style is [ART STYLE: e.g., Noir, Cyberpunk, Oil Painting]. Cinematic lighting, high resolution, typography."

**Note:** If you can't add text to the image, just submit the artwork. We can add the title for you.

---

## 📄 Final Formatting Checklist

Before you export, ensure your manuscript looks professional:

1.  **Title Page:**
    *   Title (Centered, Large)
    *   Author Name
    *   "Skoltech ISP 2026"
    *   Word Count
2.  **Layout:**
    *   Font: Times New Roman or Garamond, 12pt.
    *   Spacing: 1.5 or Double spaced.
    *   Margins: 1 inch (2.54 cm).
3.  **File Name:** `Title_AuthorName.pdf` (e.g., `The_Silicon_Dream_TeamAlpha.pdf`).

