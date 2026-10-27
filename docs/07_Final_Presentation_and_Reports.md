# DEPI Graduation Project — Milestone 4
## 7. Final Presentation & Reports

**Track:** Professional Data Analyst (DEPI Round 5)  
**Group ID:** BNS5_DAT3_S1  
**Project Name:** Financial Risk Early Warning System (EWS)  
**Team Leader:** Abdalatyf Ahmed Ibrahim  
**Submission Deadline:** December 04, 2026  

---

### 7.1 User Manual (Operational Guide)

The **Financial Risk Early Warning System (EWS)** executive interface is delivered through Microsoft Power BI Desktop, connected natively to the local MySQL relational data warehouse (`Financial_Risk_EWS_db`).

#### 1. System Navigation & Global Controls
Every dashboard canvas contains standardized global filters along the top header:
* **Cohort Tier Slicer:** Filter the view by risk group:
  * *Tier 1:* Crisis Casualties (SVB, SBNY, FRC, SI)
  * *Tier 2:* High-Stress Regional Survivors (PACW, WAL, CMA, ZION, NYCB)
  * *Tier 3:* Diversified Regional Peers (KEY, FITB, MTB, HBAN, CFG, RF)
  * *Tier 4:* Mega G-SIBs (JPM, BAC, WFC, PNC, USB)
* **Macroeconomic Era Slicer:** Slice the 15-year timeline by historical monetary regimes:
  * *Great Financial Crisis (GFC):* 2008 – 2009
  * *Zero Interest Rate Policy (ZIRP):* 2010 – 2015
  * *Policy Normalization:* 2016 – 2019
  * *COVID-19 Inflow Surge:* 2020 – 2021
  * *Fed Rate Shock:* 2022 – 2023
* **Quarterly Timeline Slider:** Select any individual quarter or temporal range between Q1 2008 and Q4 2022.

#### 2. Interpreting Early Warning Indicators
Bank examiners and risk analysts should interpret key metrics according to the following regulatory benchmarks:

| Metric Name | Calculation Formula | Safe Zone (🟢) | Elevated Warning (🟡) | Critical Danger (🔴) |
| :--- | :--- | :---: | :---: | :---: |
| **Liquidity Fragility Ratio** | $\frac{\text{Uninsured Deposits}}{\text{Cash} + \text{AFS Securities (Market Value)}}$ | $< 0.60$ | $0.60 - 1.00$ | $> 1.00$ *(Mathematical Insolvency under Run)* |
| **Capital Illusion Gap** | $\text{Reported Tier 1} - \text{Full Adjusted Tier 1}$ | $< 2.0\%$ | $2.0\% - 5.0\%$ | $> 5.0\%$ *(Significant Unrealized Losses Masked)* |
| **HTM Concentration Share** | $\frac{\text{Held-to-Maturity Securities}}{\text{Total Assets}}$ | $< 15\%$ | $15\% - 30\%$ | $> 30\%$ *(High Duration Lock-in)* |
| **Uninsured Deposit Share** | $\frac{\text{Uninsured Deposits}}{\text{Total Deposits}}$ | $< 50\%$ | $50\% - 70\%$ | $> 70\%$ *(Extreme Flight Sensitivity)* |
| **Wholesale Reliance Ratio** | $\frac{\text{Short-Term Borrowings} + \text{FHLB Advances}}{\text{Total Liabilities}}$ | $< 5\%$ | $5\% - 12\%$ | $> 12\%$ *(Emergency Funding Dependence)* |
| **Composite EWS Score** | Weighted Multi-Pillar Index (0 to 100) | $< 60$ | $60 - 80$ | $\ge 80$ *(Imminent Supervisory Action Required)* |

#### 3. Drill-Through Protocol (Page 9: Single-Bank Deep-Dive)
* **How to Drill:** Right-click on any bank data point in the Page 1 Heatmap or Page 2 Scatter Plot, select **Drill-Through**, and click **Single-Bank Deep-Dive**.
* **Detailed Tabs:** The deep-dive screen exposes 4 diagnostic tabs:
  1. *Balance Sheet Composition:* Historical asset and liability trends.
  2. *Interest Rate Sensitivity:* Duration shock simulation on HTM bond valuation.
  3. *Deposit Flight Simulation:* Step-wise liquidity depletion curves under 10% to 50% deposit withdrawal runs.
  4. *Peer Quartile Ranking:* Bank percentile rank benchmarked against Tier 2 and Tier 3 peers.

---

### 7.2 Technical Documentation & Data Dictionary

#### 1. System Architecture Summary
The system operates on a decoupled **Push-Down Analytical Architecture**:
* **ETL & Processing Layer:** Python 3.11 (`pandas`, `numpy`, `mysql-connector-python`) extracts raw FFIEC Call Report text archives, cleans anomalies (recovering 639 capital ratios and consolidating bank mergers), and computes 31 risk measures.
* **Storage Layer:** MySQL 8.0 relational Star Schema (`Financial_Risk_EWS_db`) consisting of 6 dimension tables and 3 fact tables storing 119,163 rows.
* **Presentation Layer:** Microsoft Power BI Desktop connected to relational tables and pre-aggregated analytical SQL views.

#### 2. Regulatory Data Dictionary (Core Fact Financials)
The warehouse tracks 22 fundamental financial metrics per bank-quarter extracted directly from official FFIEC MDRM series:

| Metric Column Name | FFIEC Schedule | Primary MDRM Code | Description & Accounting Treatment |
| :--- | :---: | :---: | :--- |
| `Total_Assets` | RC | `RCFD2170` | Total assets of the consolidated banking institution ($000s). |
| `Total_Liabilities` | RC | `RCFD2948` | Total liabilities ($000s). |
| `Total_Equity` | RC | `RCFD3210` | Total bank equity capital ($000s). |
| `Noncontrolling_Interest`| RC | `RCFD3000` | Noncontrolling / minority interests in consolidated subsidiaries ($000s). |
| `Cash_Balances` | RC-A | `RCFD0010` | Cash and balances due from depository institutions ($000s). |
| `Total_Securities` | RC | `RCFD1754` | Total held investment securities ($000s). |
| `HTM_Book_Value` | RC-B | `RCFD1754` | Held-to-Maturity amortized book cost ($000s). |
| `HTM_Fair_Value` | RC-B | `RCFD1771` | Held-to-Maturity market fair value ($000s). |
| `AFS_Fair_Value` | RC-B | `RCFD1773` | Available-for-Sale market fair value ($000s). |
| `Total_Loans_Net` | RC | `RCFD2122` | Net loans and leases held for investment ($000s). |
| `Domestic_Deposits` | RC | `RCON2200` | Total deposits in domestic U.S. offices ($000s). |
| `Foreign_Deposits` | RC | `RCFN2200` | Total deposits in foreign offices & offshore branches ($000s) (100% uninsured by law). |
| `Total_Deposits` | RC | `RCFD2200` / `RCON2200+RCFN2200` | Total consolidated domestic and foreign deposits ($000s). |
| `Uninsured_Deposits` | RC-O | `RCON5597` / `RCFD5597` | Estimated uninsured deposits in domestic offices exceeding $250K limit ($000s). |
| `Short_Term_Borrowings`| RC-M | `RCFDB993` + `B995` + `3190` | Federal funds purchased, repurchase agreements, and short-term debt. |
| `Tier1_Capital` | RC-R | `RCFD8274` | Tier 1 regulatory capital ($000s). |
| `CET1_Capital` | RC-R | `RCFDP841` | Common Equity Tier 1 capital ($000s) (active post-2014 under Basel III). |
| `Tier1_Ratio_Pct` | RC-R | `RCFD7206` | Reported Tier 1 risk-based capital ratio (standardized decimal). |
| `CET1_Ratio_Pct` | RC-R | `RCFDP872` | Reported Common Equity Tier 1 ratio (standardized decimal). |
| `Net_Income` | RI | `RIAD4340` | True quarterly net income (converted programmatically from YTD). |
| `Interest_Income` | RI | `RIAD4107` | Total interest income ($000s). |
| `Interest_Expense` | RI | `RIAD4073` | Total interest expense ($000s). |

---

### 7.3 Project Presentation (PPT / Defense Structure)

The final 15-minute DEPI defense presentation is structured into 12 high-impact slides following executive storytelling methodology:

```
Defense Presentation Slide Deck (15 Minutes):
├── Slide 01: Title & Team Introduction (DEPI Round 5, Group BNS5_DAT3_S1)
├── Slide 02: Executive Problem Statement (Why Traditional Ratios Failed in March 2023)
├── Slide 03: The Diamond-Dybvig Theoretical Framework & 2023 Barr Report
├── Slide 04: Project Methodology & Reproducible 5-Stage Data Pipeline Architecture
├── Slide 05: Enterprise MySQL Star Schema & Dimensional Design
├── Slide 06: Forensic Breakthrough 1: The Liquidity Fragility Ratio (> 1.0 Insolvency)
├── Slide 07: Forensic Breakthrough 2: The Capital Illusion Gap (AOCI Opt-Out Deception)
├── Slide 08: 20-Bank Panel Comparative Heatmap (SVB vs. Survivors vs. Mega Banks)
├── Slide 09: Empirical Model Backtest Results (Lead Time & Confusion Matrix)
├── Slide 10: Live Power BI Dashboard Suite Demonstration (Pages 1–4, 9)
├── Slide 11: Regulatory Policy Recommendations (AOCI Elimination, Dynamic Stress Tests)
└── Slide 12: Conclusion, Technical Verification & Panel Q&A Defense
```

#### Anticipated Panel Questions & Prepared Defense Answers
* **Q1: Why did you stop the quarterly financial panel at Q4 2022 rather than March 2023?**
  * *Defense:* To mathematically prove **predictive early warning power** and completely eliminate **hindsight bias**. If our model signals SVB and Signature Bank as Critical/Red in Q2–Q4 2022 using only data available *prior* to the collapse, we prove the disaster was foreseeable months before the actual run.
* **Q2: Why not use a Machine Learning black-box model (e.g. Random Forest or XGBoost)?**
  * *Defense:* In regulatory bank supervision and financial litigation, models must be fully **explainable and audit-proof**. Regulators cannot issue formal cease-and-desist orders or enforce capital infusions based on uninterpretable neural network weights. Our econometric framework relies on mathematically transparent accounting identities that directly trace to audited Call Report filings.
* **Q3: How do you justify modifying regulatory Tier 1 capital when banks had an official AOCI opt-out?**
  * *Defense:* The regulatory opt-out was an accounting concession, not an economic reality. When depositors demand immediate liquidity, HTM bonds cannot be held to maturity—they must be liquidated at fair market value. Subtracting unrealized paper losses reveals true economic insolvency.

---

### 7.4 Video Demonstration Plan

The optional video submission is planned as a concise **5-minute technical demonstration** divided into four clear segments:

* **Segment 1: Code Portability & Setup Automation (0:00 - 1:15)**
  * *Screen Action:* Execute `setup_and_run.bat` in a clean terminal. Show virtual environment creation, pip package installation, automated ETL pipeline execution, and the 20-test QA suite passing in 0.5 seconds.
* **Segment 2: Database Schema & Relational Integrity (1:15 - 2:15)**
  * *Screen Action:* Open MySQL Workbench / CLI. Query `Financial_Risk_EWS_db`. Show the 9 Star Schema tables, demonstrate foreign key integrity, and execute an analytical SQL view showing SVB's deteriorating liquidity ratio.
* **Segment 3: Power BI Executive Dashboard Walkthrough (2:15 - 4:15)**
  * *Screen Action:* Navigate through Core Pages 1 to 4 in Power BI Desktop. Demonstrate slicer interactivity across the 4 bank tiers and 5 macroeconomic eras. Zoom into SVB and First Republic in the Run Risk Scatter plot. Right-click to trigger the single-bank drill-down.
* **Segment 4: Conclusion & Policy Summary (4:15 - 5:00)**
  * *Screen Action:* Display the final backtest confusion matrix table, summarizing that the EWS achieved a 2-quarter warning lead time on all 4 crisis casualties.
