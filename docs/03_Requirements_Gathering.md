# DEPI Graduation Project — Milestone 1
## 3. Requirements Gathering & Analysis

**Track:** Professional Data Analyst (DEPI Round 5)  
**Group ID:** BNS5_DAT3_S1  
**Project Name:** Financial Risk Early Warning System (EWS)  
**Team Leader:** Abdalatyf Ahmed Ibrahim  
**Submission Date:** October 16, 2026  

---

### 3.1 Stakeholder Analysis

A stakeholder analysis was conducted to identify the target audiences, their operational mandates, and their primary information requirements:

| Stakeholder Persona | Operational Mandate | Information Need & Value Proposition | Priority |
| :--- | :--- | :--- | :--- |
| **Federal Bank Supervisors (FDIC / Fed / OCC)** | Systemic stability oversight, early regulatory intervention, and deposit insurance fund protection. | Needs a reliable, multi-quarter early warning signal identifying banks transitioning into high run-vulnerability zones before insolvency occurs. | **High** |
| **Bank Chief Risk Officers (CROs) & ALCO Committees** | Asset-Liability Committee (ALCO) management, liquidity stress testing, and balance sheet duration hedging. | Requires peer-benchmarked ratios to detect if their institution's uninsured deposit share or HTM concentration deviates dangerously from peer quartiles. | **High** |
| **Institutional Depositors & Corporate Treasurers** | Capital preservation, cash management, and counterparty default risk management. | Demands transparent liquidity coverage metrics (Liquidity Fragility Ratio) to assess whether cash holdings are exposed to bail-in risks. | **Medium** |
| **DEPI Evaluation Panel & Academic Examiners** | Assessing data analysis competency, mathematical rigor, engineering reproducibility, and business storytelling. | Requires auditability: clean code, normalized relational databases, transparent econometric math, and high-impact visual delivery. | **High** |

---

### 3.2 User Stories & Use Cases

#### User Story 1: The Regulatory Supervisory Examiner
* **As a** Federal Bank Examiner,  
* **I want to** view a composite Early Warning Heatmap spanning 20 banks over the last 15 years,  
* **So that** I can immediately spot institutions whose composite risk scores enter the Amber/Red danger zone 2 to 4 quarters prior to liquidity failure.

#### User Story 2: The Bank Asset-Liability Committee (ALCO) Director
* **As an** ALCO Risk Manager,  
* **I want to** evaluate my bank’s Adjusted Tier 1 Capital after deducting unrealized HTM and AFS paper losses,  
* **So that** I can quantify our "Capital Illusion Gap" under simulated market rate hikes.

#### User Story 3: The Equity Analyst & Credit Auditor
* **As an** Equity Research Analyst,  
* **I want to** correlate bank stock price drawdowns and daily volatility against sudden quarterly spikes in Federal Home Loan Bank (FHLB) emergency advances,  
* **So that** I can identify the exact inflection point when wholesale emergency funding masks retail deposit flight.

#### User Story 4: The Data Quality Auditor
* **As a** Project Evaluator,  
* **I want to** execute a single automated batch script on a clean machine,  
* **So that** I can independently reproduce the entire ETL extraction, Star Schema database creation, and metric calculation from raw FFIEC files without manual intervention.

---

### 3.3 Functional Requirements (FR)

The system must satisfy the following functional specifications across the data pipeline:

* **FR1: Automated Ingestion & Extraction**
  * The system shall automatically parse and selectively extract target schedules (`RC`, `RI`, `RC-C`, `RC-E`, `RC-O`, `RC-R`, `RC-B`) from 60 bulk FFIEC ZIP files.
  * The system shall ingest daily market OHLCV price histories and Federal Reserve Effective Federal Funds Rate series.
* **FR2: Data Cleaning & Normalization**
  * The system shall convert cumulative Year-To-Date (YTD) income statement figures into true standalone quarterly figures.
  * The system shall standardize regulatory capital ratios across varying historical filing scales (decimal vs. percentage format).
  * The system shall programmatically reconcile unearned loan income to preserve the 16-sector loan balance sheet identity.
  * The system shall map all historical institutions to Federal Reserve `IDRSSD` identifiers to maintain continuity through bank mergers and acquisitions.
* **FR3: Multi-Layer Risk Metric Engine**
  * The system shall compute 31 risk indicators spanning the 7 analytical pillars (Capital, Liquidity, Funding, Securities, Loans, Profitability, Market).
  * The system shall compute dynamic time-series features (QoQ change, YoY change, rolling 4-quarter averages, and volatility).
  * The system shall compute peer-relative percentiles and z-scores benchmarked against the 20-bank cohort and the 4 tier groups.
* **FR4: Composite EWS Index & Backtest Engine**
  * The system shall calculate an overall 0–100 Early Warning Index based on pre-frozen indicator weights.
  * The system shall assign categorical alert states: 🟢 Green ($< 60$), 🟡 Amber ($60 - 80$), and 🔴 Red ($\ge 80$).
  * The system shall generate a backtest performance table detailing warning lead times and false-positive rates.
* **FR5: Executive Business Intelligence & Visualization**
  * The system shall provide an 8-page Power BI executive suite + 1 single-bank drill-down page.
  * The system shall provide standardized global slicers on every page (`Tier`, `Era`, `Bank`, `Quarter Range`).

---

### 3.4 Non-Functional Requirements (NFR)

* **NFR1: Performance & Latency**
  * The end-to-end Python ETL pipeline must process all 60 quarters (15 years of raw data) in under 3 minutes on standard personal computer hardware.
  * Analytical SQL view execution must complete in $< 500$ ms to maintain instantaneous user interaction in Power BI.
* **NFR2: Accuracy & Data Integrity**
  * Foreign key and primary key integrity must be strictly enforced in MySQL (no orphan fact records).
  * The balance sheet identity $\text{Assets} = \text{Liabilities} + \text{Equity}$ must hold across all normalized bank-quarters.
  * Missing historical items (e.g. Basel III CET1 prior to 2015) must be preserved as structural NULLs rather than misleading 0% figures.
* **NFR3: Security & Credential Protection**
  * Database credentials and host settings must never be hardcoded in scripts; they must be managed strictly via `.env` environment files.
  * `.env` files must be excluded from version control via `.gitignore`.
* **NFR4: Usability & UI/UX Standards**
  * Visual designs must follow an established Figma design system adhering to 16:9 aspect ratios (`1920 × 1080 px`).
  * Color schemes must be consistent across all pages, utilizing distinct color identifiers for each of the 4 bank tiers and standard traffic-light alert colors.
  * Every dashboard page must include an explicit academic data citation footer (*"Source: FFIEC Call Reports, Federal Reserve FRED, Yahoo Finance"*).
* **NFR5: Portability & Maintainability**
  * All file paths must be resolved dynamically relative to project roots (`BASE_DIR`), ensuring seamless execution on any developer machine without path editing.
  * The entire local environment must be deployable via a 1-click execution script (`setup_and_run.bat`).
