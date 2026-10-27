# DEPI Graduation Project — Milestone 3
## 5. Implementation (Source Code & Execution)

**Track:** Professional Data Analyst (DEPI Round 5)  
**Group ID:** BNS5_DAT3_S1  
**Project Name:** Financial Risk Early Warning System (EWS)  
**Team Leader & Lead Architect:** Abdalatyf Ahmed Ibrahim  
**Submission Deadline:** November 30, 2026  

---

### 5.1 Source Code Architecture & Standards

The implementation layer is structured into modular Python data engineering and analytical components located in `src/etl/` and `src/analytics/`, adhering to enterprise software engineering standards:

```
src/
├── etl/
│   ├── 01_extract_market_api.py       # Market equities & FRED Fed rate fetcher
│   ├── 01b_unzip_call_reports.py      # Physical extraction of raw Call Report archives
│   ├── 02_extract_loans.py            # Schedule RC-C loan sector normalization & balancing
│   ├── 03_transform_market_fed.py     # Market OHLC enforcement & zombie bank trimming
│   ├── 04_extract_financials.py       # Financial statement extraction & capital recovery
│   └── 05_load_to_mysql.py            # Star Schema generator & bulk relational loader
└── analytics/
    └── 06_calculate_risk_metrics.py   # Multi-layer risk formulas & EWS composite engine
```

#### 1. Structured & Well-Commented Code
All codebase components follow strict modular paradigms with comprehensive docstrings explaining regulatory background, MDRM code mappings, and mathematical logic:
* **Physical Staging Cache (`01b_unzip_call_reports.py`):** Employs an "Extract Once, Read Many" strategy. Rather than repeatedly parsing 60 compressed ZIP files (~1.5 GB) in memory, targeted schedules (`RC`, `RI`, `RC-C`, `RC-R`, `RC-O`) are staged once into `data/raw/ffiec_extracted/`. This cut extraction runtime from 8 minutes to under 8 seconds.
* **Unified Extraction Helper (`get_val`):** Dynamically scans candidate MDRM series (`RCFD`, `RCON`, `RCOA`), strips non-numeric artifacts (such as `%` symbols injected by the FFIEC in 2015), and safely casts values to numeric types while preserving structural missing data as `NaN`.
* **FASB 160 Noncontrolling Interest Recovery (`RCFD3000`):** Extracts minority interest in consolidated subsidiaries, ensuring 100% adherence to the U.S. GAAP consolidated balance sheet identity ($\text{Assets} = \text{Liabilities} + \text{Bank Equity} + \text{Noncontrolling Interest}$) and eliminating all historical discrepancies ($221 \rightarrow 0$).

#### 2. Coding Standards & Naming Conventions
* **PEP 8 Compliance:** All Python code adheres to PEP 8 style standards, utilizing 4-space indentation, descriptive snake_case variable and function names, and uppercase constants.
* **SQL Conventions:** Relational database scripts adhere to ANSI SQL standards with capitalized keywords (`SELECT`, `INSERT`, `CREATE TABLE`) and lowercase, snake_case table and column identifiers.
* **Path Isolation:** All filesystem references are dynamically derived via `pathlib.Path(__file__).resolve().parents[2]` (`BASE_DIR`). No hardcoded drive letters (`D:\` or `C:\`) exist in the source code.

#### 3. Modular Code & Reusability
* **Bank Profile Consolidation:** The pipeline loads institution metadata dynamically from `config/banks.csv`, mapping Federal Reserve `IDRSSD` identifiers to permanent `FDIC_CERT` numbers and cohort risk tiers.
* **Vectorized Matrix Computations:** Mathematical risk indicators and accounting balance checks leverage optimized Pandas and NumPy vectorization rather than slow iterative loops.

#### 4. Security & Error Handling
* **Credential Isolation:** Database credentials (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_PORT`) are loaded strictly from an external `.env` file via `python-dotenv`.
* **SQL Injection Prevention:** Relational database inserts utilize parameterized query strings (`cursor.executemany(query, data_tuples)`) guaranteeing complete isolation from SQL injection vulnerabilities.
* **Graceful Degradation & Non-Destructive CLI:** Scripts detect missing archives, catch `EOFError` when running non-interactively in CI/CD pipelines, and support explicit `--rebuild` flags to prevent accidental database truncation.

---

### 5.2 Version Control & Collaboration

The project development lifecycle is managed via Git and hosted publicly on GitHub:

* **Official Repository Link:** [https://github.com/abdalatyf/Financial_Risk_EWS](https://github.com/abdalatyf/Financial_Risk_EWS)
* **Default Branch:** `main` (Production-ready, certified code).

#### 1. Branching Strategy
The team employs a modified **GitFlow** and **Feature Branching** workflow:
* `main`: Protected production branch; only tested, certified code signed off by the Team Leader and QA Lead is merged here.
* `develop`: Integration branch where data pipeline, risk calculation, and Power BI assets are staged.
* `feature/*`: Dedicated task branches for individual team members:
  * `feature/financial-measures` (Hazem Taha Hosny)
  * `feature/figma-storyboard` (Mohamed Lotfy)
  * `feature/powerbi-core-pages` (Mohamed Kamel)
  * `feature/qa-unit-tests` (Omar Mohamed Abdulwahab)
  * `feature/powerbi-drilldown` (Ibrahim Mosleh)

#### 2. Commit History & Documentation
Every commit adheres to Conventional Commits standards:
* `feat:` Introduction of new pipeline scripts or risk calculations.
* `fix:` Algorithmic bug fixes (e.g. `%` stripping, IDRSSD deduplication, OHLC price bounds).
* `docs:` Updates to official DEPI milestone documentation and architecture diagrams.
* `test:` Addition and expansion of automated unit tests in `tests/test_etl_qa.py`.
* `refactor:` Code improvements that do not alter output logic.

#### 3. Continuous Integration & Quality Gate
Before merging code into `main`, the test suite `python -m unittest tests/test_etl_qa.py` must execute with a 100% pass rate across all 20 test cases.

---

### 5.3 Deployment & Execution Guide

#### 1. System Requirements
* **Operating System:** Windows 10/11 (64-bit), macOS 12+, or Ubuntu Linux 22.04 LTS.
* **Hardware:** Minimum 8 GB RAM (16 GB recommended), 4 CPU cores, 5 GB free disk space.
* **Software Dependencies:**
  * Python 3.11+ or 3.12 (with `pip` and `venv`)
  * MySQL Server 8.0+ or 9.0 Community Edition
  * Microsoft Power BI Desktop (for dashboard visualization)
  * Git 2.30+

#### 2. Configuration Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/abdalatyf/Financial_Risk_EWS.git
   cd Financial_Risk_EWS
   ```
2. Copy the template environment file:
   ```bash
   copy .env.example .env
   ```
3. Edit `.env` to configure your local MySQL credentials:
   ```ini
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_actual_password
   MYSQL_DATABASE=Financial_Risk_EWS_db
   ```

#### 3. Execution Guide (1-Click Automated Setup)
To execute the entire pipeline end-to-end on Windows, run the provided automated batch script:
```cmd
setup_and_run.bat
```
The script performs the following actions automatically:
1. Verifies Python installation and creates an isolated virtual environment (`.venv`).
2. Installs required packages from `requirements.txt`.
3. Executes Call Report physical extraction (`01b_unzip_call_reports.py`).
4. Extracts and reconciles loan sectors (`02_extract_loans.py`).
5. Enforces OHLC bounds and processes market/Fed data (`03_transform_market_fed.py`).
6. Extracts quarterly balance sheets and recovers capital ratios (`04_extract_financials.py`).
7. Executes the automated 20-test QA suite (`tests/test_etl_qa.py`).
8. Initializes the MySQL Star Schema and loads 116,783 rows (`05_load_to_mysql.py --rebuild`).

#### 4. Executable Files & Deployment Artifacts
* **`setup_and_run.bat`:** Windows automated bootstrap runner.
* **`src/etl/05_load_to_mysql.py --rebuild`:** Relational database schema generation and loader.
* **`tests/test_etl_qa.py`:** Automated QA verification suite.
* **MySQL Schema:** 9 normalized tables hosting 15 years of forensic data ready for direct Power BI connection.
