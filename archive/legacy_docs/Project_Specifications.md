# Project Specifications: Financial Risk EWS

## 1. Project Overview
**Name:** Financial Risk EWS  
**Objective:** To design and build an end-to-end data pipeline and analytical model that mathematically detects Dual-Sided Concentration Risk (Asset Duration Risk vs. Liability Flight Risk) across a cohort of 20 U.S. banks, proving the predictability of the March 2023 banking crisis.

## 2. Technical Stack & Architecture
The system follows a modern three-tier data architecture:

* **Data Engineering & Calculations (Python):** 
  * Python (Pandas, NumPy) is strictly used for all ETL processes, data normalization, and complex mathematical risk calculations.
* **Data Storage (MySQL):** 
  * A relational Snowflake/Star Schema hosted in MySQL to store the cleaned, calculated fact and dimension tables.
* **Data Visualization (Power BI):** 
  * Power BI connects directly to the MySQL database to render interactive dashboards and visual risk narratives.

## 3. Data Sources & Ingestion
* **FFIEC Call Reports:** 15 years (2008–2023) of raw zip files containing quarterly balance sheets and income statements.
* **FRED Macroeconomic Data:** Federal Funds Rate history to correlate asset devaluation with rate hikes.
* **Market Data:** Daily stock OHLC and volume data sourced from Yahoo Finance and Investing.com.

## 4. Core Python Calculations
Before data is visualized, Python will be used to compute the following critical risk metrics:
1. **Liquidity Fragility Ratio:** `(Total Uninsured Deposits) / (Highly Liquid Assets)`
   * *Specification:* A ratio > 1.0 indicates a mathematical guarantee of insolvency in the event of a total bank run.
2. **HTM Concentration Risk:** `(Hold-to-Maturity Securities) / (Total Assets)`
   * *Specification:* Tracks the percentage of assets locked in long-duration bonds sensitive to Fed rate hikes.
3. **Uninsured Deposit Ratio:** `(Uninsured Deposits) / (Total Deposits)`
   * *Specification:* Measures liability flight risk. (SVB exceeded 86%).

## 5. Power BI Dashboard Specifications
The final deliverables will include interactive Power BI dashboards with the following views:
* **The Crisis Heatmap:** A systemic view comparing the risk ratios of the 4 Crisis Casualties against the 16 surviving banks.
* **The Timeline Tracker:** A time-series chart showing the inverse correlation between rising Fed Interest Rates and the falling fair value of HTM bonds (2021–2023).
* **The Run-on-the-Bank Simulator:** A drill-down view showing how quickly a bank's liquid assets would be depleted based on varying percentages of deposit withdrawal.

## 6. Team Roles & Responsibilities
To execute these specifications, the team will divide responsibilities across the architecture:
* **Lead Data Engineer (Abdalatyf):** Manages the Python ETL architecture, data sourcing, and MySQL schema logic.
* **Python Calculation Analyst:** Writes the Python scripts to calculate the Liquidity Fragility and Concentration metrics.
* **Power BI Developer:** Ingests the MySQL data into Power BI, designs the UI/UX, and builds the visual DAX measures.
* **QA & Git Manager:** Tests the Python calculations for accuracy and manages the GitHub version control.
* **Business Analyst:** Owns the final narrative, researches the 2023 timeline, and structures the final 15-minute DEPI presentation.
