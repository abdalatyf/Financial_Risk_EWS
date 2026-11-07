# Setup Guide — From Zero to Power BI

**Project:** Financial Risk EWS (DEPI Round 5 — BNS5_DAT3_S1)  
**Platform:** Windows 10/11 (64-bit)  
**Time needed:** ~30–45 minutes (most of it is installs and the first pipeline run)  
**Disk space:** ~5 GB free (the FFIEC ZIPs expand to ~2.7 GB)

When you finish this guide, you will have the full database on your laptop and Power BI Desktop opening the project with live data.

---

## Step 1 — Install the Required Software

Install these **in order**. Keep the default options unless noted.

| # | Software | Version | Download | Important Notes |
| :-: | :--- | :--- | :--- | :--- |
| 1 | **Git** | Latest | https://git-scm.com/download/win | Defaults are fine. |
| 2 | **Python** | 3.12 | https://www.python.org/downloads/ | ⚠️ On the first installer screen, tick **"Add python.exe to PATH"**. |
| 3 | **MySQL Server** | 8.0 Community | https://dev.mysql.com/downloads/installer/ | Choose **Server only** (or Developer Default). Keep port **3306**. **Write down the `root` password you set.** |
| 4 | **MySQL Connector/NET** | **8.0.32** | https://downloads.mysql.com/archives/c-net/ | ⚠️ Use **8.0.32** exactly, **Complete** setup. Newer/preview versions (e.g. 9.x / 26.x) are rejected by Power BI. |
| 5 | **Power BI Desktop** | Latest | Microsoft Store or https://powerbi.microsoft.com/desktop | Install **after** Connector/NET, or restart Power BI after installing it. |

**Check the installs** — open a new PowerShell window and run:
```powershell
git --version
python --version
```
Both should print a version. If `python` is not found, reinstall Python with "Add to PATH" ticked.

---

## Step 2 — Get the Code

```powershell
cd D:\
git clone https://github.com/abdalatyf/Financial_Risk_EWS.git
cd Financial_Risk_EWS
```

The repository already contains all raw data (FFIEC Call Report ZIPs, market prices, Fed rates) — **no extra downloads needed**.

---

## Step 3 — Configure Your Database Password

1. In the project folder, copy the template:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` in Notepad and replace `YOUR_PASSWORD_HERE` with **your** MySQL `root` password:
   ```ini
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_real_password
   MYSQL_DATABASE=Financial_Risk_EWS_db
   ```
3. Save and close.

> `.env` is ignored by Git — your password is never uploaded to GitHub.

---

## Step 4 — Run the Full Pipeline (1 Click)

Make sure **MySQL Server is running** (it starts automatically with Windows after install).

Double-click **`setup_and_run.bat`** in the project folder (or run it from PowerShell). It will:

| Step | What happens |
| :-: | :--- |
| — | Creates a Python virtual environment (`venv`) and installs `requirements.txt` |
| 1/7 | Unzips the 60 FFIEC Call Report archives (**slowest step — a few minutes**) |
| 2/7 | Extracts the 16 loan sectors |
| 3/7 | Cleans daily market prices |
| 4/7 | Extracts quarterly financial statements |
| 5/7 | **Creates `Financial_Risk_EWS_db` in MySQL** and loads the Star Schema |
| 6/7 | Calculates the risk metrics, EWS score, and Power BI views |
| 7/7 | Runs the automated QA test suites |

✅ **Success looks like:**
```
[SUCCESS] Entire ETL & Analytics Pipeline finished successfully!
```

> Step 5 **drops and rebuilds** the database every time. That is safe — everything is regenerated from the files in the repo.

---

## Step 5 — Open the Project in Power BI

1. Open the file: `power_bi\power bi project.pbip`
2. If Power BI asks for **MySQL credentials**:
   - Select the **Database** tab (**not** Windows)
   - User name: `root`
   - Password: your MySQL password
   - Click **Connect**
3. Click **Home → Refresh**. The visuals should fill with data.

The connection uses two parameters — `pServer = localhost` and `pDatabase = Financial_Risk_EWS_db` — so it works on every laptop without editing anything.

---

## Step 6 — Switch to Your Personal Branch

Close Power BI first, then follow the **Git Collaboration Guide** (`PowerBI_Git_Collaboration_Guide.md`) to check out your branch:

```powershell
git checkout feature/<your-name>
```

---

## Troubleshooting

| Problem | Cause | Fix |
| :--- | :--- | :--- |
| `'python' is not recognized` | Python not on PATH | Reinstall Python and tick **"Add python.exe to PATH"**. Open a **new** terminal. |
| `[5/7] MySQL load failed` / `Can't connect to MySQL server on 'localhost:3306'` | MySQL not running, or wrong password | Start the **MySQL80** service (Win+R → `services.msc`). Check the password in `.env`. |
| `Access denied for user 'root'@'localhost'` | Wrong password in `.env` | Fix `MYSQL_PASSWORD` in `.env` and re-run the `.bat`. |
| Power BI: *"This connector requires one or more additional components: MySQL Connector/NET"* | Connector missing, wrong version, or Power BI not restarted | Uninstall other Connector/NET versions, install **8.0.32 (Complete)**, then **fully close and reopen** Power BI (check Task Manager for `PBIDesktop.exe`). |
| Power BI: *"We couldn't authenticate with the credentials provided"* | Used the SQL Server connector, or the Windows tab | Use the **MySQL database** connector and the **Database** tab with `root`. |
| Power BI won't open the `.pbip` file | Old Power BI version | Update Power BI Desktop. On older versions enable *File → Options → Preview features → Power BI Project (.pbip) save option*. |
| Tests fail at step 7/7 | Data or code mismatch | Run `git pull` to get the latest code, then re-run `setup_and_run.bat`. If it still fails, send the error to the Team Leader. |
