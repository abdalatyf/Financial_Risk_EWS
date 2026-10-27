# DEPI Graduation Project — Milestone 2
## 4. System Analysis & Design

**Track:** Professional Data Analyst (DEPI Round 5)  
**Group ID:** BNS5_DAT3_S1  
**Project Name:** Financial Risk Early Warning System (EWS)  
**Team Leader:** Abdalatyf Ahmed Ibrahim  
**Submission Deadline:** November 06, 2026  

---

### 4.1 Problem Statement & Objectives

#### 1. Problem Statement & Project Goals
The collapse of Silicon Valley Bank (SVB), Signature Bank, and First Republic Bank in March 2023 demonstrated that standard regulatory capital metrics (e.g. CET1 and Tier 1 Capital) fail to provide timely warning of modern liquidity contagion and unhedged balance sheet duration mismatches.

The goal of the **Financial Risk Early Warning System (EWS)** is to design, implement, and validate an automated forensic data platform that mathematically proves the 2023 crisis was predictable. By unifying 15 years of quarterly regulatory Call Reports (FFIEC), daily macroeconomic Federal Reserve interest rates (FRED), and equity market dynamics across a panel of 20 U.S. commercial banks, the system detects **Dual-Sided Concentration Risk**:
* **Asset Side:** Severe unhedged duration and interest rate risk locked into fixed-income Held-to-Maturity (HTM) portfolios.
* **Liability Side:** Excessive reliance on uninsured, flight-prone deposits concentrated in a single sector.

#### 2. System Actors & Use Case Descriptions
* **Actor 1: Regulatory Supervisory Examiner (FDIC / Fed / OCC)**
  * *Use Case:* Evaluates systemic peer rankings, monitors early warning indicator surges, and inspects institutions entering the Amber/Red danger zones 2 to 4 quarters ahead of statutory failure.
* **Actor 2: Bank Chief Risk Officer (CRO) & ALCO Committee**
  * *Use Case:* Audits the institution's true economic capital after marking HTM and AFS portfolios to market, simulating deposit run depletion thresholds.
* **Actor 3: Data Engineer / Lead Architect (Abdalatyf Ahmed Ibrahim)**
  * *Use Case:* Executes automated ingestion of bulk regulatory archives, manages MySQL Star Schema staging, and monitors automated unit testing pipelines.
* **Actor 4: Academic Evaluation Panel (DEPI Instructors)**
  * *Use Case:* Reviews methodology reproducibility, database normalization standards, econometric validity, and business intelligence narrative.

#### 3. Use Case Diagram
```mermaid
flowchart LR
    subgraph Actors["System Actors"]
        A1["Bank Supervisory Examiner"]
        A2["Bank CRO / ALCO Director"]
        A3["Data Engineer / Architect"]
        A4["DEPI Evaluation Panel"]
    end

    subgraph System["Financial Risk EWS Platform"]
        UC1["UC-01: Ingest & Extract 15-Yr Call Reports"]
        UC2["UC-02: Normalize & Reconcile Financials"]
        UC3["UC-03: Compute 31 Specialized Risk Metrics"]
        UC4["UC-04: Calculate Capital Illusion Gap"]
        UC5["UC-05: Simulate Run-on-the-Bank Fragility"]
        UC6["UC-06: Query Executive 8-Page BI Dashboards"]
        UC7["UC-07: Execute Automated QA & Model Backtest"]
    end

    A3 --> UC1
    A3 --> UC2
    A3 --> UC7
    A2 --> UC3
    A2 --> UC4
    A2 --> UC5
    A1 --> UC5
    A1 --> UC6
    A4 --> UC6
    A4 --> UC7
```

#### 4. Summary of Functional & Non-Functional Constraints
* **Functional Capabilities:** Automated parsing of 60 FFIEC ZIP files, YTD-to-quarterly income transformation, Basel III capital ratio standardization, loan sector reconciliation (< 2% variance), and computation of 31 risk indicators.
* **Non-Functional Constraints:** Pipeline execution $< 180$ seconds, sub-500ms SQL query execution, zero hardcoded drive paths (`BASE_DIR`), parameterized security isolation (`.env`), and 16:9 executive visual layouts.

#### 5. High-Level Software Architecture
The platform follows a four-layer **Push-Down Analytical Architecture**, separating heavy computational processing from interactive presentation:

```mermaid
flowchart TD
    subgraph Layer1["1. Raw Ingestion Layer (Bronze)"]
        A1["FFIEC Bulk ZIPs (60 Quarters)"]
        A2["Yahoo / Market Daily (20 Banks)"]
        A3["FRED Fed Funds Rate (Daily)"]
    end

    subgraph Layer2["2. Processing & Normalization Layer (Silver)"]
        B1["FFIEC Unzipper & Stager (01b)"]
        B2["Loan Sector Normalizer (02)"]
        B3["Market & Macro Transformer (03)"]
        B4["Financials & Capital Recovery (04)"]
        B5["Python Risk Calculation Engine (06)"]
    end

    subgraph Layer3["3. Enterprise Warehouse Layer (Gold - MySQL)"]
        C1["Relational Star Schema Database"]
        C2["6 Dimension Tables"]
        C3["3 Normalized Fact Tables"]
        C4["Denormalized Analytical Views"]
    end

    subgraph Layer4["4. Business Intelligence & Executive UI (Presentation)"]
        D1["Figma Design System & Prototypes"]
        D2["8-Page Power BI Interactive Report"]
        D3["Executive EWS Heatmap & Single-Bank Drilldown"]
    end

    A1 --> B1
    B1 --> B2
    B1 --> B4
    A2 --> B3
    A3 --> B3
    B2 --> B5
    B4 --> B5
    B2 --> C1
    B3 --> C1
    B4 --> C1
    B5 --> C1
    C1 --> C4
    D1 -.-> D2
    C4 --> D2
    D2 --> D3
```

---

### 4.2 Database Design & Data Modeling

#### 1. Entity-Relationship Diagram (ERD)
The database utilizes a high-performance **Star Schema** optimized for analytical queries across 20 institutions over 60 quarters:

```mermaid
erDiagram
    dim_bank ||--o{ fact_financials : "reports"
    dim_quarter ||--o{ fact_financials : "per quarter"
    dim_financial_metric ||--o{ fact_financials : "measured by"

    dim_bank ||--o{ fact_loan_balances : "holds"
    dim_quarter ||--o{ fact_loan_balances : "per quarter"
    dim_loan_sector ||--o{ fact_loan_balances : "allocated across"

    dim_bank ||--o{ fact_daily_market : "trades"
    dim_date ||--o{ fact_daily_market : "on date"

    dim_quarter ||--o{ dim_date : "contains"
    dim_date ||--o{ dim_macro_fed_rates : "rates observed on"

    dim_bank {
        int idrssd PK
        string ticker
        string bank_id
        string bank_name
        int tier
        string tier_label
    }

    dim_quarter {
        string quarter_id PK
        int year
        int quarter_num
        date quarter_end_date
        string era
    }

    dim_date {
        date date PK
        string quarter_id FK
        string day_of_week
    }

    dim_financial_metric {
        int metric_id PK
        string metric_name UK
        string statement_type
    }

    dim_loan_sector {
        int sector_id PK
        string sector_name UK
    }

    dim_macro_fed_rates {
        date date PK, FK
        decimal fed_funds_rate
    }

    fact_financials {
        string quarter_id PK, FK
        int idrssd PK, FK
        int metric_id PK, FK
        decimal metric_value
    }

    fact_loan_balances {
        string quarter_id PK, FK
        int idrssd PK, FK
        int sector_id PK, FK
        decimal loan_amount
    }

    fact_daily_market {
        date date PK, FK
        int idrssd PK, FK
        decimal open_price
        decimal high_price
        decimal low_price
        decimal close_price
        bigint volume
    }
```

#### 2. Logical & Physical Schema Details
* **Dimension Tables (6):**
  * `dim_bank`: Stores static institution descriptors, ticker symbols, FDIC Certificate, Federal Reserve IDRSSD, and vulnerability classification (`tier` 1 to 4, `tier_label`).
  * `dim_quarter`: Stores quarterly calendar attributes and macroeconomic regimes (`era`: GFC, ZIRP, Normalization, COVID Surge, Rate Shock).
  * `dim_date`: Comprehensive daily calendar linking daily market observations to quarterly financial cycles.
  * `dim_financial_metric`: Metadata catalog defining the 22 core Call Report line items across Balance Sheet (`RC`), Income Statement (`RI`), Regulatory Capital (`RC-R`), and Uninsured & Foreign Deposits (`RC-O`, `RC-E`).
  * `dim_loan_sector`: 16 discrete lending categories extracted from Schedule RC-C (e.g. Commercial Real Estate, 1-4 Family Residential, Construction, C&I).
  * `dim_macro_fed_rates`: Daily Federal Funds Effective Rate time series sourced from FRED.
* **Fact Tables (3):**
  * `fact_financials`: 25,598 normalized rows (1,190 bank-quarters × 22 metrics, accounting for structural nulls) stored in third normal form (3NF).
  * `fact_loan_balances`: 19,040 normalized rows (1,190 bank-quarters × 16 loan sectors).
  * `fact_daily_market`: 74,525 daily market observations with OHLC prices and trade volumes.

#### 3. Normalization Considerations & Optimization
* **Storage Efficiency:** Transitioning from "Wide" CSV tables (19-35 columns) to a normalized "Narrow/Long" Star Schema reduced sparse null storage by 64%.
* **Composite Primary Keys:** Composite PKs `(quarter_id, idrssd, metric_id)` guarantee idempotent loading and zero duplicate entries.
* **Indexing Strategy:** B-tree indexes are applied on foreign key joins `(idrssd, quarter_id)` and calendar dates, enabling analytical SQL view filtering in $< 50$ ms.

---

### 4.3 Data Flow & System Behavior

#### 1. Level 0 DFD: Context-Level Diagram
```mermaid
flowchart LR
    S1["FFIEC CDR Public Repository"] -->|"Bulk Call Report Archives"| EWS(("Financial Risk EWS Platform"))
    S2["FRED (St. Louis Fed)"] -->|"Effective Fed Funds Rate"| EWS
    S3["Yahoo Finance & Market Data"] -->|"Daily OHLCV Equities"| EWS

    EWS -->|"8-Page Power BI Executive Dashboard"| U1["Bank Supervisors & Examiners"]
    EWS -->|"EWS Heatmap & Risk Metrics"| U2["Bank Chief Risk Officers"]
    EWS -->|"Figma Mockups & Academic Backtest"| U3["DEPI Evaluation Panel"]
```

#### 2. Level 1 DFD: Detailed Process Flow
```mermaid
flowchart TD
    P1["1.0 Physical Extraction & Staging"] --> P2["2.0 Schema Cleaning & Financial Recovery"]
    P2 --> P3["3.0 Risk Metric & Velocity Engine"]
    P3 --> P4["4.0 Relational Loader (MySQL)"]
    P4 --> P5["5.0 Analytical View Generation"]
    P5 --> P6["6.0 Power BI Dashboard Rendering"]

    D1[("Raw File Storage")] <--> P1
    D2[("Processed CSV Warehouse")] <--> P2
    D2 <--> P3
    D3[("MySQL Star Schema")] <--> P4
    D3 <--> P5
    P6 --> D4["Executive User Interface"]
```

#### 3. Sequence Diagram: Pipeline Execution Flow
```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / User
    participant Bat as setup_and_run.bat
    participant Py as Python ETL Pipeline (01b-05)
    participant DB as MySQL Database
    participant BI as Power BI Desktop

    Dev->>Bat: Execute 1-Click Setup
    Bat->>Bat: Initialize venv & install requirements.txt
    Bat->>Py: Run 01b (Unzip Call Reports)
    Bat->>Py: Run 02 & 04 (Extract Loans & Financials)
    Bat->>Py: Run 03 (Transform Market & Fed Data)
    Dev->>Py: Execute 05_load_to_mysql.py --rebuild
    Py->>DB: Verify / Create Star Schema (9 Tables)
    Py->>DB: Bulk Insert ~119,163 Normalized Rows
    DB-->>Py: Transaction Commit Confirmed
    Dev->>BI: Connect to MySQL Database
    BI->>DB: Query Optimized Analytical Views
    DB-->>BI: Return Pre-Aggregated Risk Metrics
    BI->>Dev: Render 8-Page Interactive Dashboard
```

#### 4. Activity Diagram: ETL & Risk Engine Workflow
```mermaid
flowchart TD
    Start([Start Pipeline]) --> Step1["Check for Existing Extracted Schedules"]
    Step1 --> Decision1{"Extracted Files Present?"}
    Decision1 -- No --> Step2["Extract Specific Schedules (RC, RI, RC-C, RC-R, RC-O)"]
    Decision1 -- Yes --> Step3["Read Staged Call Reports"]
    Step2 --> Step3
    Step3 --> Step4["Apply IDRSSD Mapping & Merger Deduplication"]
    Step4 --> Step5["Convert YTD Net Income to True Quarterly"]
    Step5 --> Step6["Strip '%' and Cast Capital Ratios (2015 Fix)"]
    Step6 --> Step7["Enforce Market OHLC Consistency (High >= Low)"]
    Step7 --> Step8["Compute 31 Risk Indicators & Composite EWS Score"]
    Step8 --> Step9["Execute Automated Unit Tests (tests/test_etl_qa.py)"]
    Step9 --> Decision2{"All 20 Tests Passed?"}
    Decision2 -- No --> Fail([Halt & Log Error])
    Decision2 -- Yes --> Step10["Bulk Load Star Schema to MySQL Database"]
    Step10 --> End([End Pipeline - Ready for Power BI])
```

#### 5. State Diagram: Institutional Risk State Lifecycle
```mermaid
stateDiagram-v2
    [*] --> Healthy: Liquidity Fragility < 0.60 & Capital Illusion Gap < 2.0%
    Healthy --> Vulnerable: Uninsured Deposits Surge (> 75%) OR HTM Share (> 25%)
    Vulnerable --> Critical: Fed Rate Hike Shock (> 400 bps) & Liquidity Fragility > 1.0
    Critical --> BankRun: Depositor Panic & Digital Run (> $40B Outflow)
    Critical --> RegulatoryIntervention: Emergency FHLB Funding / Capital Restructuring
    BankRun --> SeizedByFDIC: Cash Depletion & Negative Market-to-Market Tier 1
    RegulatoryIntervention --> Healthy: De-risked Balance Sheet & Injected Liquidity
    SeizedByFDIC --> [*]
```

#### 6. Class Diagram: Object-Oriented Pipeline Architecture
```mermaid
classDiagram
    class CallReportExtractor {
        +string base_dir
        +list target_schedules
        +unzip_bulk_archives()
        +get_val(schedule_df, mdrn_candidates)
    }

    class LoanSectorNormalizer {
        +dict sector_mapping
        +extract_loan_sectors()
        +reconcile_loan_totals()
    }

    class FinancialsExtractor {
        +dict balance_sheet_codes
        +dict income_statement_codes
        +convert_ytd_to_quarterly()
        +recover_capital_ratios()
    }

    class MarketTransformer {
        +string ticker_csv_dir
        +enforce_ohlc_consistency()
        +trim_delisted_banks()
        +merge_fed_funds_rate()
    }

    class MySQLLoader {
        +dict db_config
        +create_star_schema()
        +bulk_insert_facts()
        +create_analytical_views()
    }

    CallReportExtractor <|-- LoanSectorNormalizer
    CallReportExtractor <|-- FinancialsExtractor
    FinancialsExtractor --> MySQLLoader
    LoanSectorNormalizer --> MySQLLoader
    MarketTransformer --> MySQLLoader
```

---

### 4.4 UI/UX Design & Prototyping

#### 1. Figma Wireframes & Screen Architecture
The executive dashboard suite was designed in **Figma** adhering to executive corporate reporting standards. The suite comprises 8 core narrative pages and 1 detailed drill-down interface:

1. **Page 1: Systemic Early Warning Heatmap** — Executive bird's-eye view tracking all 20 banks across 60 quarters, color-coded by the 0–100 Composite EWS Score.
2. **Page 2: Bank Run Vulnerability Matrix** — Scatter plot cross-tabulating the **Liquidity Fragility Ratio** against the **Uninsured Deposit Share**, exposing the 4 casualties in the upper-right danger quadrant.
3. **Page 3: Rate Shock & Duration Impact** — Interactive dual-axis visual correlating Federal Reserve rate hikes against the devaluation of HTM bond portfolios.
4. **Page 4: Capital Illusion Gap (AOCI Opt-Out)** — Waterfall and variance charts illustrating the 13% divergence between reported regulatory Tier 1 capital and market-adjusted economic capital.
5. **Page 5: Loan Portfolio Concentration & CRE Exposure** — Decomposition of the 16 loan sectors with an interactive Herfindahl-Hirschman Index (HHI) gauge.
6. **Page 6: Wholesale Funding & Borrowing Velocity** — Line charts tracking emergency FHLB advance spikes that masked deposit runoff in late 2022.
7. **Page 7: Earnings Quality & NIM Compression** — Analysis of True Quarterly Net Income, Yield on Earning Assets, and Cost of Funds.
8. **Page 8: Market Sentiment & Delisting Contagion** — Correlation between daily stock drawdowns, market cap evaporation, and regulatory intervention dates.
9. **Page 9: Single-Bank Deep-Dive Drill-Down** — Comprehensive multi-tab profile enabling examiners to inspect any single bank across all 31 metrics with historical peer quartile bands.

#### 2. UI/UX Guidelines & Design System
* **Canvas Dimensions:** Standardized 16:9 widescreen format (`1920 × 1080 px`).
* **Color Palette:**
  * *Tier 1 (Crisis Casualties):* Crimson Red (`#D32F2F`)
  * *Tier 2 (High-Stress Survivors):* Deep Amber (`#ED6C02`)
  * *Tier 3 (Regional Peers):* Slate Navy (`#0288D1`)
  * *Tier 4 (Mega G-SIBs):* Forest Green (`#2E7D32`)
* **Alert States (Traffic Light System):**
  * 🟢 **Normal / Low Risk:** Composite Score $< 60$ (`#2E7D32`)
  * 🟡 **Elevated / Moderate Risk:** Composite Score $60 - 80$ (`#F57C00`)
  * 🔴 **Critical / High Warning:** Composite Score $\ge 80$ (`#D32F2F`)
* **Typography:** Segoe UI (Headers: 20pt Bold; KPI Callouts: 28pt Bold; Body: 11pt Regular).
* **Accessibility & Citations:** High-contrast text compliance (WCAG AA), tooltips providing metric definitions, and mandatory source attribution footers on all canvas pages.

---

### 4.5 System Deployment & Integration

#### 1. Technology Stack
| Architecture Layer | Technology Selection | Version | Rationale |
| :--- | :--- | :--- | :--- |
| **Language Runtime** | **Python** | 3.11+ / 3.12 | Industry standard for data engineering and vectorized calculations. |
| **Data Manipulation** | **Pandas & NumPy** | pandas 2.2.3, numpy 2.1.2 | High-performance matrix operations and time-series manipulation. |
| **Relational Database** | **MySQL Community Server** | 8.0+ / 9.0 | ACID compliant, high-speed relational Star Schema with foreign keys. |
| **Database Connector** | **mysql-connector-python** | 9.0.0 | Native transactional Python-MySQL pipeline communication. |
| **UI/UX Prototyping** | **Figma** | Cloud Standard | Official DEPI design deliverable; establishes layout guidelines and assets. |
| **Data Visualization** | **Microsoft Power BI** | Desktop (Latest) | Interactive multi-page executive dashboards, slicers, and drill-downs. |
| **DevOps & Automation** | **Windows Batch Scripting** | `setup_and_run.bat` | 1-click environment bootstrap, idempotency, and automated execution. |
| **Version Control** | **Git & GitHub** | GitHub Public Repo | Transparent collaboration, branch protection, and full commit lineage. |

#### 2. Deployment Diagram
```mermaid
flowchart TD
    subgraph ClientHost["Local Developer Workstation (Windows 10/11 x64)"]
        subgraph AppRuntime["Python 3.11+ Isolated Environment (.venv)"]
            P1["ETL Scripts (01b-05)"]
            P2["QA Test Runner (tests/test_etl_qa.py)"]
        end

        subgraph DatabaseInstance["MySQL Server Community Edition (Port 3306)"]
            DB1[("Financial_Risk_EWS_db")]
            DB2["Star Schema (6 Dims, 3 Facts)"]
            DB3["Analytical SQL Views"]
            DB1 --- DB2
            DB2 --- DB3
        end

        subgraph ClientUI["Business Intelligence Client"]
            BI1["Power BI Desktop"]
            BI2["DirectQuery / Import Connector"]
            BI1 --- BI2
        end

        AppRuntime -->|"TCP/IP Connection (mysql-connector)"| DatabaseInstance
        ClientUI -->|"Native MySQL ODBC Connector"| DatabaseInstance
    end
```

#### 3. Component Diagram
```mermaid
flowchart TD
    subgraph IngestionComp["Ingestion Component"]
        C1["FFIEC Bulk Stager"]
        C2["Yahoo API Extractor"]
        C3["FRED Rate Fetcher"]
    end

    subgraph ProcessingComp["Processing & Normalization Component"]
        C4["Capital Ratio Recoverer"]
        C5["Loan Sector Balancer"]
        C6["True Quarterly Income Converter"]
        C7["Risk Metric Engine"]
    end

    subgraph StorageComp["Storage & Modeling Component"]
        C8["MySQL Schema Initializer"]
        C9["Star Schema Data Warehouse"]
        C10["Push-Down SQL Analytical Views"]
    end

    subgraph PresentationComp["Presentation Component"]
        C11["Power BI DAX Measure Layer"]
        C12["8-Page Dashboard Suite"]
        C13["Single-Bank Drill-Down"]
    end

    IngestionComp --> ProcessingComp
    ProcessingComp --> StorageComp
    StorageComp --> PresentationComp
```

---

### 4.6 Additional Deliverables

#### 1. API & External Data Ingestion Documentation
* **FFIEC CDR Public Repository:** Ingests quarterly bulk Call Report archives (`FFIEC CDR Call Bulk All Schedules MMDDYYYY.zip`). Extracted locally using regex MDRM scanners matching schedule files (`RC`, `RI`, `RC-C`, `RC-R`, `RC-O`).
* **Yahoo Finance API (`yfinance` / Market CSVs):** Ingests daily Open, High, Low, Close, and Volume for active tickers (`JPM`, `BAC`, `WFC`, `PNC`, `USB`, `FITB`, `KEY`, `MTB`, `HBAN`, `CFG`, `RF`, `WAL`, `CMA`, `ZION`, `NYCB`).
* **Delisted Bank Fallback CSVs:** Historical trade prices for seized/delisted institutions (`SIVB`, `SBNY`, `FRCB`, `PACW`) curated from Investing.com and OTC records, truncated strictly at FDIC receiver takeover dates.
* **FRED Macroeconomic Series:** Effective Federal Funds Rate (`DFF`), daily continuous observations.

#### 2. Testing & Validation Strategy
* **Automated Unit Testing:** 20 test cases implemented in `tests/test_etl_qa.py` verifying code portability, row alignment (1,190 bank-quarters), balance sheet accounting identity, loan sector balancing, OHLC bounding, and MySQL table schema presence.
* **Econometric Model Backtesting:** Empirical verification that the composite early warning index achieved $\ge 2$ quarters lead time on all Tier 1 failures with a false-positive rate $< 15\%$.

#### 3. Deployment Strategy
* **Automated Provisioning:** Standardized `setup_and_run.bat` creates a Python virtual environment (`.venv`), installs locked dependencies from `requirements.txt`, executes the 5-stage ETL pipeline, runs the 20-test QA suite, and loads the MySQL database in a single automated command.
* **Credential Isolation:** Database credentials are securely loaded from a local `.env` file excluded from version control.
