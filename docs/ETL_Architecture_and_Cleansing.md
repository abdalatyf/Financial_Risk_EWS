# ETL Architecture & Data Cleansing Methodology
**Project:** SVB Early Warning System (EWS)  
**Role:** Data Engineering & Database Administration  

## 1. Pipeline Architecture
The ETL (Extract, Transform, Load) pipeline was engineered using an **Object-Oriented Python** approach, adhering to the enterprise principle of "Extract Once, Read Many."

* **Data Volume:** 15 years of quarterly FFIEC Call Reports (60 ZIP files, ~1.5 GB) + 15 years of daily stock market data.
* **Extraction Strategy:** Rather than unzipping massive files in memory repeatedly, the pipeline physically stages the raw text files into a `data/raw/ffiec_extracted/` directory. This reduced processing time from several minutes to under 10 seconds.
* **Consolidation:** The pipeline dynamically maps evolving `IDRSSD` identifiers to permanent `FDIC_CERT` numbers using the FFIEC `POR` (Profile) files, ensuring continuity even if a bank undergoes mergers.

---

## 2. Data Cleansing & Remediation Operations

During the extraction phase, our automated quality assurance audits identified and programmatically resolved several critical data anomalies in the source data.

### A. FFIEC Format Evolution (The Percentage Bug)
**Issue:** In Q1 2015, the FFIEC overhauled Schedule RC-R (Regulatory Capital) and began appending `%` symbols to the end of their reporting strings (e.g., reporting `"13.0740%"` instead of `"13.0740"`).
**Resolution:** The `get_val()` extraction method was rewritten to dynamically strip non-numeric symbols (`%`) prior to executing strict `pandas.to_numeric` casting. This successfully recovered 639 missing capital ratio data points from 2015-2023.

### B. IDRSSD Merger Duplication
**Issue:** During bank acquisitions, multiple active `IDRSSD` codes can temporarily map to a single `FDIC_CERT` within the same quarter, resulting in duplicated rows and artificially inflated loan balances.
**Resolution:** Applied `.groupby(['Date', 'FDIC_CERT', 'Bank_Name'])` with `.sum()` and `.max()` aggregations prior to export. This cleanly consolidates subsidiary data into the parent holding company.

### C. Short-Term Borrowings Fragmentation
**Issue:** The FFIEC does not provide a single unified column for Short-Term Borrowings.
**Resolution:** The pipeline was engineered to mathematically reconstruct this metric by scanning multiple schedules and aggregating:
1. `B993` (Federal Funds Purchased)
2. `B995` (Securities sold under agreements to repurchase)
3. `3190` (Other borrowed money with remaining maturity < 1 year)

### D. Market Data OHLC Consistency
**Issue:** Raw data from Yahoo Finance occasionally contained floating-point precision errors where a stock's `High` price was mathematically recorded as lower than its `Open` price.
**Resolution:** Implemented programmatic OHLC (Open, High, Low, Close) math enforcement. The script forces `High = max(High, Open, Close)` and rounds all prices uniformly to 4 decimal places, preventing downstream SQL database constraint crashes.

### E. "Zombie Bank" Trimming (SBNY)
**Issue:** Signature Bank (SBNY) was seized on March 12, 2023. Post-seizure, the stock traded on OTC markets for fractions of a penny, creating anomalous zero-values.
**Resolution:** Implemented a strict cutoff filter for `SBNY` at `2023-03-12` to prevent OTC zombie-pricing from corrupting predictive machine learning models.

---

## 3. Final Star Schema Target
The output of the Python ETL pipeline results in 4 perfectly clean, fully normalized CSV files ready for MySQL loading:

1. `fact_financials.csv` (1,189 rows)
2. `fact_loan_sectors.csv` (1,189 rows)
3. `fact_daily_market.csv` (74,909 rows)
4. `dim_macro_fed_rates.csv` (5,844 rows)

*(See Data Dictionary for exact column specifications and SQL data types).*
