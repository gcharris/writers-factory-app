# 🔒 Admin Checklist: Securing the Course

Since the app contains embedded API keys ($$$), security is the priority.

## 1. GitHub Setup (The $4/mo Solution)
- [ ] **Upgrade to GitHub Pro** (Settings -> Billing).
- [ ] **Make Repo Private** (Settings -> General -> Danger Zone).
- [ ] **Enable Private Pages** (Settings -> Pages -> Visibility -> Private).
    - *Result:* Only users with access to the repo can see the website.

## 2. Student Onboarding
- [ ] **Collect GitHub Usernames** from all students.
- [ ] **Invite Students** (Settings -> Collaborators -> Add people).
    - *Role:* `Read` (if they are Writers) or `Write` (if they are Architects).
    - *Note:* Even "Read" access allows them to see the website and download the Releases.

## 3. Branch Protection (Critical)
Prevent students from accidentally breaking the code.
- [ ] Go to **Settings -> Branches**.
- [ ] Add rule for `main`.
- [ ] Check **"Require a pull request before merging"**.
- [ ] Check **"Require approval from code owners"** (That's you).

## 4. The "Kill Switch"
If a key leaks:
- [ ] Have the **OpenAI/Anthropic Dashboards** bookmarked.
- [ ] Know exactly which key is embedded in the build.
- [ ] Be ready to **Rotate (Revoke)** that key instantly if usage spikes.
