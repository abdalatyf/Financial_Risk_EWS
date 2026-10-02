# EWS Raw Data Dictionary & Source Tracking

This document catalogs the exact source, frequency, and contents of all raw datasets acquired for the SVB Early Warning System (EWS) project. It serves as the official Data Lineage documentation for the DEPI graduation panel.

## The 20-Bank Cohort
The project tracks 20 specific banking institutions (divided into four vulnerability tiers) to prove the mathematical effectiveness of the Early Warning System:

**Tier 1: The Crisis Casualties (Target Failures)**
* Silicon Valley Bank (CERT: 24735 | Ticker: SIVB)
* Signature Bank (CERT: 57053 | Ticker: SBNY)
* First Republic Bank (CERT: 59017 | Ticker: FRCB)
* Silvergate Bank (CERT: 27330 | Ticker: SI)

**Tier 2: High-Stress Survivors (Heavy Outflows)**
* Western Alliance Bank (CERT: 57512 | Ticker: WAL)
* PacWest (CERT: 34697 | Ticker: BANC)
* Comerica Bank (CERT: 983 | Ticker: CMA)
* Zions Bancorporation (CERT: 2270 | Ticker: ZION)
* New York Community Bank (CERT: 16022 | Ticker: FLG)

**Tier 3: Resilient Regional Peers (Control Group)**
* Fifth Third Bank (CERT: 6672 | Ticker: FITB)
* KeyBank (CERT: 17534 | Ticker: KEY)
* Regions Bank (CERT: 12368 | Ticker: RF)
* M&T Bank (CERT: 588 | Ticker: MTB)
* Huntington National Bank (CERT: 6560 | Ticker: HBAN)
* Citizens Bank (CERT: 57957 | Ticker: CFG)

**Tier 4: Mega G-SIBs (Systemically Important / Safe Havens)**
* JPMorgan Chase Bank (CERT: 628 | Ticker: JPM)
* Bank of America (CERT: 3510 | Ticker: BAC)
* Wells Fargo Bank (CERT: 3511 | Ticker: WFC)
* PNC Bank (CERT: 6384 | Ticker: PNC)
* U.S. Bank (CERT: 6548 | Ticker: USB)

---

## 1. FFIEC Call Reports (Quarterly Fundamentals)
**Location:** `D:\Projects\EWS\EWS_SourceCode\data\raw\ffiec_zips\`
**File Type:** 60 compressed `.zip` files containing Tab-Separated Values (`.txt`)
**Time Range:** Q1 2008 – Q4 2022 (60 Quarters)
**Data Source:** [FFIEC Central Data Repository (CDR) Public Data Distribution](https://cdr.ffiec.gov/public/pws/DownloadBulkData.aspx)
**Extraction Method:** Manual HTTPS download (bypassing Azure Geo-blocks)

### Schedule Mapping (Data Dictionary)
The ZIP files contain the official mandatory regulatory filings for all US commercial banks. Our ETL pipeline extracts the following specific schedules:
* **Schedule RC-C (RCCI.txt):** Loans and Lease Financing Receivables. *Used to extract the 16 highly granular loan sectors for the concentration risk Herfindahl-Hirschman Index (HHI).*
* **Schedule RC (RC.txt):** Consolidated Balance Sheet. *Used for Total Assets, Total Liabilities, and Cash/Balances.*
* **Schedule RC-E (RCE.txt):** Deposit Liabilities. *Used for Total Insured Deposits.*
* **Schedule RC-O (RCO.txt):** Other Data for Deposit Insurance. *Used to isolate Uninsured Deposits (critical for the Liquidity Fragility Metric).*
* **Schedule RC-R (RCR.txt):** Regulatory Capital. *Used to extract CET1 Capital Ratios.*
* **Schedule RC-B (RCB.txt):** Securities. *Used to track Held-to-Maturity (HTM) and Available-for-Sale (AFS) bond portfolios.*

---

## 2. Daily Market Data (Stock Equities)
**Location:** `D:\Projects\EWS\EWS_SourceCode\data\raw\market_daily\`
**File Type:** 20 Comma-Separated Values (`.csv`) files
**Time Range:** January 1, 2008 – December 31, 2023
**Frequency:** Daily (Trading Days Only; ~4,027 rows per active bank)
**Data Schema:** `Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume`

### Sourcing Breakdown
Because several banks collapsed and were delisted, a hybrid sourcing strategy was required:
* **Yahoo Finance API (yfinance):** 16 Active Banks (`JPM`, `BAC`, `WFC`, `PNC`, `USB`, `FITB`, `KEY`, `RF`, `MTB`, `HBAN`, `CFG`, `WAL`, `BANC`, `ZION`, `FLG`, `FRCB`). *Extracted via Python script (`01_extract_market_api.py`).*
* **Kaggle Database:** Silicon Valley Bank (`SIVB_daily.csv`). *Manual download from [Kaggle SVB Dataset](https://www.kaggle.com/datasets/zq1200/silicon-valley-bank-group-stock-price-history).*
* **Investing.com (CMA):** Comerica Bank (`CMA_daily.csv`). *Manual download from [Investing.com Comerica](https://www.investing.com/equities/comerica-inc-historical-data).*
* **Investing.com (SBNY):** Signature Bank (`SBNY_daily.csv`). *Manual download from [Investing.com Signature Bank](https://www.investing.com/equities/signature-bank-historical-data).*
* **Investing.com (SI):** Silvergate Capital (`SI_daily.csv`). *Manual download from [Investing.com Silvergate](https://www.investing.com/equities/silvergate-capital-corp-historical-data).*

---

## 3. Macroeconomic Catalysts (Interest Rates)
**Location:** `D:\Projects\EWS\EWS_SourceCode\data\raw\fed_rate.csv`
**File Type:** 1 Comma-Separated Values (`.csv`) file
**Time Range:** January 1, 2008 – December 31, 2023
**Frequency:** Daily (Calendar Days; 5,844 rows)
**Data Source:** [Federal Reserve Bank of St. Louis (FRED)](https://fred.stlouisfed.org/series/DFF)

### Metric Definition
* **Daily Effective Federal Funds Rate (DFF):** The interest rate depository institutions charge each other for overnight loans. This is the primary macroeconomic trigger for the 2023 banking crisis, as aggressive rate hikes depreciated the value of bank-held Treasury bonds.
