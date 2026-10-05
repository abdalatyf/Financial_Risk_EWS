# Financial Risk EWS 🏦📉

**DEPI Graduation Project - Professional Data Analyst Track (Round 5)**  
*A comprehensive forensic data analysis of 20 U.S. banks (2008–2023) to mathematically prove the predictability of the March 2023 banking crisis.*

---

## 🎯 Project Objective
This system detects and quantifies **Dual-Sided Concentration Risk**:
1. **Liability Side Risk:** Extreme depositor concentration (94% of SVB's deposits were uninsured tech/VC funds subject to immediate flight).
2. **Asset Side Risk:** Duration risk (40%+ of assets locked in long-duration Hold-to-Maturity (HTM) bonds that lost billions in fair value as the Fed raised rates).

By analyzing raw FFIEC Call Reports alongside macroeconomic Fed data, this pipeline establishes a mathematical early warning threshold (Liquidity Fragility Ratio) that proves SVB was effectively insolvent months before the bank run.

---

## 🏛️ The 20-Bank Comparative Cohort
To prove *why* SVB failed while others survived, our EWS contrasts Silicon Valley Bank against a structured cohort of 19 other institutions, categorized into 4 systemic tiers:

| Tier | Category | Banks Tracked |
| :--- | :--- | :--- |
| **1** | **Crisis Casualties** | Silicon Valley Bank, Signature Bank, First Republic, Silvergate |
| **2** | **High-Stress Survivors** | PacWest, Western Alliance, Zions, Comerica, NYCB |
| **3** | **Regional Peers** | KeyBank, Fifth Third, M&T, Huntington, Citizens |
| **4** | **Mega G-SIBs** | JPMorgan, Bank of America, Wells Fargo, PNC, U.S. Bank |

---

## 📂 Project Architecture

```text
EWS_SourceCode/
├── config/
│   └── banks.csv                 # Master registry (IDRSSD, Tickers, Tiers)
├── data/
│   ├── processed/                # Final clean CSVs & SQL Tables (Ignored by Git)
│   └── raw/
│       ├── ffiec_zips/           # 490MB of FFIEC Call Report ZIPs (2008-2023)
│       ├── market_daily/         # Historical stock OHLC & Volume
│       └── fed_rate.csv          # Macro Federal Funds Rate History
├── docs/                         # DEPI Documentation, Proposals, architecture
├── src/
│   ├── etl/                      # 100% automated Python Extraction Pipeline
│   └── sql/                      # Star Schema creation & analytical views
├── setup_and_run.bat             # 1-Click Environment Setup & ETL Runner
├── requirements.txt              # Python dependencies
└── .env.example                  # Template for local MySQL credentials
```

---

## 🚀 1-Click Setup & Execution
We have provided a fully automated script manager for seamless installation and deployment. 

**Prerequisites:** 
* Python 3.9+ 
* MySQL Server (Local or Remote)

### Step 1: Configure Database Credentials
1. In the root directory, locate the `.env.example` file.
2. Rename it to exactly: `.env`
3. Open it and type in your local MySQL `DB_PASSWORD`. (This file is strictly ignored by Git to protect your password).

### Step 2: Run the Pipeline
If you are on Windows, simply double click the script manager:
> **`setup_and_run.bat`**

**What this script automatically does:**
1. Creates an isolated Python virtual environment (`venv`).
2. Installs all required packages (`pandas`, `numpy`, `python-dotenv`).
3. Safely extracts the 490MB of `.zip` files into 2.7GB of staging `.txt` files.
4. Executes the **Extract, Transform, Load (ETL)** pipeline to detect target banks, resolve historic FDIC certificate mergers via `IDRSSD`, convert YTD incomes to Quarterly incomes, and generate clean Fact/Dimension tables.
5. Saves the final production-ready tables into the `data/processed/` folder.

---

## 📊 The Data Pipeline (ETL Scripts)
If you wish to run the scripts manually, they must be executed in this order:

1. `01b_unzip_ffiec.py`: Physically extracts the raw Call Report TXT files.
2. `02_extract_transform_ffiec.py`: Extracts and maps the 16 Loan Sectors.
3. `03_transform_market_data.py`: Normalizes stock prices, flags price basis, and prunes post-failure penny stock data.
4. `04_extract_financials.py`: Calculates Core Financials (Capital Ratios, HTM/AFS values, Net Income, Uninsured Deposits).
5. `05_load_to_mysql.py`: Connects to MySQL, generates the Snowflake Schema, and inserts all 80,000+ metrics.

---
*Created for the Digital Egypt Pioneers Initiative (DEPI).*
