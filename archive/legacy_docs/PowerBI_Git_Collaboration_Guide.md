# Power BI Developer Mode (.pbip) — Team Git Collaboration Workflow

**Project:** Financial Risk Early Warning System (DEPI Round 5 - Capstone)  
**Workspace:** `power_bi/`  
**Team Leader & QA Lead:** Abdalatyf Ahmed Ibrahim  
**Repository:** [https://github.com/abdalatyf/Financial_Risk_EWS](https://github.com/abdalatyf/Financial_Risk_EWS)

---

## 1. Team Branch Matrix

Each team member works on their own personal branch. Task/page scope is assigned separately by the Team Leader.

| Team Member | Personal Branch |
| :--- | :--- |
| **Abdalatyf Ahmed Ibrahim** (Team Leader) | `main` |
| **Hazem Taha Hosny** | `feature/hazem` |
| **Mohamed Kamel Farouk** | `feature/mohamed-kamel` |
| **Omar Mohamed Abdulwahab** | `feature/omar-abdulwahab` |
| **Ibrahim Mosleh Ibrahim** | `feature/ibrahim-mosleh` |
| **Mohamed Lotfy Makram** | `feature/mohamed-lotfy` |

---

## 2. The 5 Golden Rules of Power BI Git Collaboration

> [!CAUTION]
> ### ⚠️ RULE 1: NEVER Run Git Commands with Power BI Desktop Open!
> Power BI Desktop locks underlying cache files (`cache.abf`) and overwrites local files upon closing.  
> **Always SAVE and CLOSE Power BI Desktop completely before running `git checkout`, `git pull`, `git merge`, or `git commit`.**

> [!IMPORTANT]
> ### 🛡️ RULE 2: Page-Level Isolation (Zero Merge Conflicts)
> In Power BI Developer Mode (`.pbip`), each report page has a dedicated folder under:  
> `power_bi/power bi project.Report/definition/pages/<page_id>/`  
> Two people must **never edit the same page at the same time**. Coordinate with the Team Leader before touching a page someone else is working on.

> [!TIP]
> ### 📐 RULE 3: Centralized DAX Measures Table
> All calculation measures must be placed inside the `_Measures` table (`power_bi/power bi project.SemanticModel/definition/tables/_Measures.tmdl`). Never create implicit measures inside visuals.

> [!NOTE]
> ### 🔄 RULE 4: Always Sync with `main` Before Opening Power BI
> Before starting your work session, ensure you pull the latest updates:  
> `git checkout main` $\rightarrow$ `git pull origin main` $\rightarrow$ `git checkout your-feature-branch` $\rightarrow$ `git merge main`

> [!WARNING]
> ### 🚫 RULE 5: Never Commit User Settings or Caches
> The `.gitignore` file automatically excludes `**/.pbi/`, `cache.abf`, and `localSettings.json`. If `git status` shows any file containing `.pbi/`, do NOT add it.

---

## 3. Step-by-Step Developer Workflow

### Step 1: Starting Your Work Session (Branch & Sync)
```bash
# 1. Ensure Power BI Desktop is CLOSED
# 2. Sync your local main branch
git checkout main
git pull origin main

# 3. Switch to your personal branch (or create tracking if first time)
git checkout feature/mohamed-kamel    # Example for Mohamed Kamel
# (For Hazem: git checkout feature/hazem)
# (For Omar: git checkout feature/omar-abdulwahab)
# (For Ibrahim: git checkout feature/ibrahim-mosleh)
# (For Lotfy: git checkout feature/mohamed-lotfy)

# 4. Bring any new measures or updates from main into your branch
git merge main
```

### Step 2: Working in Power BI Desktop
1. Open `power_bi/power bi project.pbip` in Power BI Desktop.
2. Build your assigned pages according to the UI/UX storyboard in `EWS_UI-UX.pptx`.
3. Save your changes (`Ctrl + S`).
4. **Close Power BI Desktop completely.**

### Step 3: Reviewing & Committing Changes
```bash
# 1. Inspect what changed
git status

# 2. Stage only your Power BI definition changes
git add "power_bi/power bi project.Report/"
git add "power_bi/power bi project.SemanticModel/"

# 3. Commit with a conventional semantic message
git commit -m "feat(pbi-page-2): implement Funding & Run Risk scatter map and KPI cards"

# 4. Push your branch to GitHub
git push origin feature/mohamed-kamel
```

### Step 4: Submitting for Review (Pull Request)
1. Go to GitHub: [Financial_Risk_EWS / Pull Requests](https://github.com/abdalatyf/Financial_Risk_EWS/pulls)
2. Click **New Pull Request**.
3. Set **Base:** `main` $\leftarrow$ **Compare:** `feature/your-branch`.
4. Add description of pages built, screenshots, and tag **@abdalatyf** for review.

---

## 4. Team Leader & QA Review Workflow (Abdalatyf)

When a developer submits a PR:
```bash
# 1. Fetch and checkout the developer's branch locally
git fetch origin
git checkout feature/mohamed-kamel

# 2. Open power_bi/power bi project.pbip in Power BI Desktop to visually verify:
#    - Slicers work cleanly
#    - Formatting matches EWS_UI-UX.pptx design
#    - Ratios match SUM()/SUM() standards

# 3. Close Power BI Desktop
# 4. If approved, merge into main via GitHub PR (or locally):
git checkout main
git pull origin main
git merge --no-ff feature/powerbi-core-pages
git push origin main
```

---

## 5. Quick Troubleshooting

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **Git error: `cannot lock ref` or `Permission denied`** | Power BI Desktop is still running in background. | Close Power BI Desktop. Check Task Manager for `PBIDesktop.exe` and end task if stuck. |
| **Merge conflict in `model.tmdl` or `_Measures.tmdl`** | Two developers added measures simultaneously. | Open TMDL in VS Code. Accept both incoming measure blocks (they are plain text). |
| **Power BI prompts to authenticate MySQL** | Local credentials not cached in user's Power BI. | Select `Database` tab, User: `root`, enter local MySQL password, Database: `Financial_Risk_EWS_db`. |
