# DEPI Graduation Project — Milestone 4
## 6. Testing & Quality Assurance Report

**Track:** Professional Data Analyst (DEPI Round 5)  
**Group ID:** BNS5_DAT3_S1  
**Project Name:** Financial Risk Early Warning System (EWS)  
**QA & Testing Lead:** Omar Mohamed Abdulwahab Mohamed (Student ID: 21172370) (Under direction of Abdalatyf Ahmed Ibrahim, Team Leader)  
**Execution Date:** October 27, 2026  
**Test Suite Status:** 🟢 **21 / 21 Tests Passed (100% Pass Rate in 0.485s)**  

---

### 6.1 Test Plan & QA Methodology

The Quality Assurance strategy for the Financial Risk EWS applies a multi-tier verification methodology ensuring that data extraction, transformation, and relational modeling meet enterprise and academic standards:

```
ETL & Database QA Architecture:
├── 1. Code Portability & Environment Security (Tests 01-02, 19-20)
│   ├── No hardcoded filesystem drive paths (dynamic BASE_DIR)
│   ├── Entity coverage (20 unique banks, 4 risk tiers)
│   └── Secret isolation (.env ignored, .env.example sanitized)
├── 2. Structural & Mathematical Integrity (Tests 03-09, 18, 21)
│   ├── Exact bank-quarter alignment (1,190 active rows across facts)
│   ├── Structural NULL handling (Basel III CET1 pre-2015, SI/WAL uninsured)
│   ├── Balance sheet identity (Assets = Liabilities + Equity + NCI)
│   ├── Deposit decomposition (Total = Domestic + Foreign)
│   └── Loan sector gross/net reconciliation (< 2% unearned variance)
├── 3. Market & Macro Data Quality (Tests 10-12)
│   ├── Physical OHLC bounding (Low <= Open/Close <= High)
│   ├── Delisted zombie trading truncation at official resolution dates
│   └── Continuous Federal Funds Rate coverage without gaps
└── 4. Relational Database & Forensic Validation (Tests 13-17)
    ├── MySQL Star Schema existence (all 9 tables)
    ├── Foreign key referential integrity (zero orphan records)
    ├── Dimensional enrichment (tier, tier_label, era)
    └── Forensic benchmark verification against SVB Q4-2022 Call Report
```

---

### 6.2 Automated Test Execution Results (`tests/test_etl_qa.py`)

All tests are implemented in Python's standard `unittest` framework and run non-destructively against the local repository and database:

| Test ID | Category | Test Scenario & Verification Objective | Expected Outcome | Actual Outcome | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | Portability | Scan `src/etl/*.py` for hardcoded drive letters (`D:\`, `C:\`). | Zero hardcoded paths | 0 hardcoded paths found | 🟢 **PASS** |
| **TC-02** | Configuration | Validate `config/banks.csv` integrity and tier coverage. | 20 banks, 4 unique tiers | 20 banks, 4 tiers (1 to 4) | 🟢 **PASS** |
| **TC-03** | CSV Alignment | Verify active row counts between financial and loan facts. | Exactly 1,190 rows each | 1,190 rows in both CSVs | 🟢 **PASS** |
| **TC-04** | Primary Key Join | Compare `(Date, IDRSSD)` primary key sets between fact tables. | 100% identical key sets | 100% match (1,190 keys) | 🟢 **PASS** |
| **TC-05** | Deduplication | Assert zero duplicate `(Date, IDRSSD)` keys in fact tables. | 0 duplicate keys | 0 duplicates found | 🟢 **PASS** |
| **TC-06** | Data Quality | Verify pre-Basel III `CET1_Ratio_Pct` is stored as `NaN` not `0.0`. | 0 zeros pre-2014 | 0 zeros (470 valid nulls) | 🟢 **PASS** |
| **TC-07** | Data Quality | Verify SI (2008–17) and WAL (2008–10) missing uninsured deposits are `NaN`. | 0 zeros where deposits exist | 0 zeros (40 SI, 12 WAL nulls)| 🟢 **PASS** |
| **TC-08** | Accounting | Validate Balance Sheet identity: $\text{Assets} = \text{Liab} + \text{Equity} + \text{NCI}$. | Discrepancy $< 0.1\%$ | Exactly 0 violations (100% balance) | 🟢 **PASS** |
| **TC-09** | Loan Balancing | Assert $\sum(\text{16 Sectors}) \ge \text{Total Loans}$ and unearned delta $< 2\%$. | Gross $\ge$ Net; delta $< 2\%$ | Max unearned delta $1.43\%$ | 🟢 **PASS** |
| **TC-10** | Market Bounds | Check physical OHLC ordering: $\text{Low} \le \text{Open/Close} \le \text{High}$. | 0 bound violations | 0 violations in 74,525 rows | 🟢 **PASS** |
| **TC-11** | Market Halts | Check delisted banks (`SIVB`, `SBNY`, `FRCB`, `PACW`) stop at cutoff. | Max trade date $\le$ cutoff | All 4 banks strictly cut off | 🟢 **PASS** |
| **TC-12** | Macro Rates | Validate Federal Reserve DFF series continuity. | $\ge 4,000$ rows, 0 nulls | 5,844 rows, 0 nulls | 🟢 **PASS** |
| **TC-13** | Database | Verify presence of all 9 Star Schema tables in MySQL. | 9 tables present | 9 tables verified present | 🟢 **PASS** |
| **TC-14** | Dimensionality | Verify `dim_bank` contains `tier` and `tier_label` for all 20 banks. | 20 rows, non-null tiers | 20 rows, all tiers populated | 🟢 **PASS** |
| **TC-15** | Dimensionality | Verify `dim_quarter` contains macro `era` classifications. | $\ge 4$ unique eras, 0 nulls | 5 unique eras, 0 nulls | 🟢 **PASS** |
| **TC-16** | Referential | Assert zero orphan foreign keys in fact tables. | 0 orphan records | 0 orphans in all 3 facts | 🟢 **PASS** |
| **TC-17** | Forensic | Verify SVB Q4-2022 matches official Call Report filings. | Assets \$209B, HTM \$91B, Uninsured \$151B, Foreign \$13.9B | Exact matches ($\Delta < 0.1\%$) | 🟢 **PASS** |
| **TC-18** | Accounting | Verify YTD-to-quarterly net income conversion is non-monotonic. | Q4 $\ne \sum(\text{Q1–Q4})$ | True quarterly verified | 🟢 **PASS** |
| **TC-19** | DevOps | Validate `setup_and_run.bat` portability. | Exists, 0 drive hardcodes | File present and portable | 🟢 **PASS** |
| **TC-20** | Security | Validate `.env` git exclusion and `.env.example` sanitization. | `.env` ignored, dummy pass | Password protected | 🟢 **PASS** |
| **TC-21** | Deposit Math | Verify deposit decomposition: $\text{Total} == \text{Domestic} + \text{Foreign}$. | 0 violations across 1,190 rows | 0 violations (max diff $0.0$) | 🟢 **PASS** |

---

### 6.3 Bug Reports & Remediations Log

During this Quality Assurance review cycle, 9 specific technical and data defects were identified, audited, and resolved:

#### Bug #1: Hardcoded File Path in `01_extract_market_api.py`
* **Severity:** High (DevOps / Portability)
* **Description:** Line 7 used `r"D:\Projects\EWS\EWS_SourceCode\..."`, which caused immediate runtime failure on team members' machines.
* **Resolution:** Replaced with dynamic relative resolution:  
  `BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`

#### Bug #2: Outdated PacWest Ticker Mapping in `01_extract_market_api.py`
* **Severity:** Medium (Market Data Integrity)
* **Description:** PacWest was mapped to `"BANC"`, pulling Banc of California post-merger price history rather than historical PacWest quotes.
* **Resolution:** Updated ticker entry to `"PACW"` aligned with the manual investing.com historical dataset.

#### Bug #3: Phantom Inactive Rows for First Republic Bank (`FRC`)
* **Severity:** High (Data Alignment)
* **Description:** FRC did not operate under an independent charter from 2008-Q1 to 2010-Q2. `04_extract_financials.py` generated 10 all-zero placeholder rows, causing row count mismatch (1,200 vs 1,190 in loans).
* **Resolution:** Added `if total_assets == 0.0: continue` check, dropping the 10 inactive quarters and perfectly synchronizing both fact tables to 1,190 active rows.

#### Bug #4: Structural Zero-Fill Poisoning on Pre-Basel III CET1
* **Severity:** High (Econometric Validity)
* **Description:** CET1 capital ratios did not exist before Basel III implementation (2014–2015). Call Reports filled empty fields with `0.0`, dragging down bank averages.
* **Resolution:** Replaced pre-2015 zeros with `np.nan` (`NULL` in MySQL), recovering 470 valid structural nulls.

#### Bug #5: Structural Zero-Fill on SI & WAL Uninsured Deposits
* **Severity:** High (Risk Metric Validity)
* **Description:** Silvergate (2008–2017) and Western Alliance (2008–2010) were exempt from filing Schedule RC-O memo 1. Zeros in uninsured deposits created false 0% fragility ratios.
* **Resolution:** Replaced missing uninsured deposits with `np.nan` for those specific exemption periods.

#### Bug #6: Missing Dimensional Attributes in MySQL Schema (`dim_bank`)
* **Severity:** Medium (Power BI Modeling)
* **Description:** `05_load_to_mysql.py` created `dim_bank` without `tier` and `tier_label`, preventing Power BI developers from slicing by bank vulnerability groups.
* **Resolution:** Added `tier INT` and `tier_label VARCHAR(50)` to `dim_bank` schema and populated directly from `config/banks.csv`.

#### Bug #7: Missing Macroeconomic Era in `dim_quarter`
* **Severity:** Low (Analytical Usability)
* **Description:** Quarters had no temporal grouping, requiring complex DAX grouping in Power BI.
* **Resolution:** Added `era VARCHAR(50)` attribute mapping each quarter to its macroeconomic regime (GFC, ZIRP, Normalization, COVID Surge, Rate Shock).

#### Bug #8: Cohort Table Inconsistency in `README.md`
* **Severity:** Low (Documentation)
* **Description:** The README cohort table omitted Regions Bank (RF) in Tier 3, reporting only 19 institutions.
* **Resolution:** Added Regions Bank to Tier 3, restoring the 20-bank cohort documentation.

#### Bug #9: Database Password Environment Variable Mismatch
* **Severity:** Medium (DevOps Onboarding)
* **Description:** README instructed teammates to define `DB_PASSWORD`, but scripts read `MYSQL_PASSWORD`.
* **Resolution:** Synchronized README instructions to `MYSQL_PASSWORD` matching `.env.example`.

---

### 6.4 Quality Certification & Readiness Sign-Off

The data extraction, cleaning, and relational modeling components have achieved **100% compliance** across all automated tests. The data warehouse is verified clean, normalized, and production-ready for the subsequent Analytical Calculation and Power BI Visualization phases.

* **Lead QA Auditor:** Omar Mohamed Abdulwahab Mohamed (Student ID: 21172370)  
* **Approved by:** Abdalatyf Ahmed Ibrahim (Team Leader & Lead Data Architect)
