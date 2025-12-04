# Deployment & Security Strategy

## The Conflict
You have two opposing goals:
1.  **Secure the App:** Keep the Source Code (and API Keys) **Private**.
2.  **Share the Course:** Make the Website (and Student Projects) **Public**.

## Option A: The "GitHub Pro" Route (Current Path)
*   **Plan:** GitHub Pro ($4/month).
*   **Repo Visibility:** Private.
*   **Website Visibility:** **Private** (Only logged-in collaborators can see it).
*   **Student Access:** You must invite every student as a "Collaborator".
*   **Risk:** Collaborators can see the **Source Code** (and API Keys).
*   **Verdict:** ❌ **Not Recommended** if you want to hide API keys from students.

## Option B: The "Two-Repo" Split (Recommended)
*   **Plan:** GitHub Free (Free).
*   **Setup:**
    1.  **Repo 1 (Private):** `writers-factory-app` (The Source Code + Keys).
    2.  **Repo 2 (Public):** `writers-factory-course` (The Website + Student Projects).
*   **Website Visibility:** **Public** (Anyone can see the Splash Page).
*   **Student Access:** Students can "Fork & Pull Request" to Repo 2 without seeing Repo 1.
*   **Downloads:** Anyone can download the PDFs from Repo 2.
*   **Verdict:** ✅ **Best for Security & Sharing.**

---

## How to Upgrade to GitHub Pro (If you choose Option A)
1.  Go to **GitHub.com** and log in.
2.  Click your **Profile Picture** (top right) → **Settings**.
3.  Click **Billing and plans** (left sidebar).
4.  Click **Upgrade** next to "Free".
5.  Select **GitHub Pro** ($4/month).
6.  Enter payment info.

## How to execute Option B (The Split)
1.  Create a new Public Repository on GitHub (e.g., `writers-factory-course`).
2.  Move the `docs/` folder content to this new repo.
3.  Enable GitHub Pages on the new repo.
4.  Keep your current repo Private (for the app code).
