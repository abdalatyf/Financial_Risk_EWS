# DEPI Graduation Project — Milestone 1
## 2. Literature Review & Theoretical Framework

**Track:** Professional Data Analyst (DEPI Round 5)  
**Group ID:** BNS5_DAT3_S1  
**Project Name:** Financial Risk Early Warning System (EWS)  
**Team Leader:** Abdalatyf Ahmed Ibrahim  
**Submission Date:** October 16, 2026  

---

### 2.1 Theoretical Background & Prior Work

The 2023 banking crisis represents a watershed moment in financial economics, demonstrating that traditional regulatory oversight models failed to account for the speed of modern digital liquidity contagion and duration mismatches.

#### 1. The Classic Foundation: Diamond-Dybvig (1983) & Bank Runs
The foundational framework for liquidity risk is the **Diamond-Dybvig Model (1983)**, which formalizes how commercial banks perform maturity transformation by funding long-term, illiquid assets with short-term, liquid liabilities (demand deposits). Diamond and Dybvig proved that this structure creates multiple equilibria:
* **The Normal Equilibrium:** Depositors withdraw funds only according to idiosyncratic consumption needs, allowing banks to maintain solvency.
* **The Run Equilibrium:** When depositors believe other depositors will withdraw, it becomes individually rational to withdraw immediately, triggering a self-fulfilling panic that forces the fire-sale of illiquid assets.

#### 2. The 2023 Federal Reserve Post-Mortem (The Barr Report, April 2023)
In the official Federal Reserve evaluation, *Review of the Supervision and Regulation of Silicon Valley Bank*, Vice Chair for Supervision Michael S. Barr highlighted four foundational supervisory failures:
* **SVB Senior Leadership Failure:** SVB failed to manage basic interest rate and liquidity risk, failing to recognize that rapid deposit inflows from 2020–2021 were hot money driven by zero-interest rate monetary stimulus.
* **The AOCI Exemption Loophole:** Under the 2018 Economic Growth, Regulatory Relief, and Consumer Protection Act (EGRRCPA), Category IV banks (\$100B–\$250B in assets) were granted an exemption allowing them to opt out of reflecting Accumulated Other Comprehensive Income (AOCI) unrealized losses in regulatory capital.
* **Regulatory Lag:** Supervisory teams identified foundational risks (issuing Matters Requiring Attention - MRAs), but failed to escalate enforcement before the run materialized.

#### 3. Modern Bank Run Velocity & Social Media Contagion
Recent empirical research (Cookson, Fox, Gil-Bazo, Mathews, & Schiller, 2023) documented that the SVB collapse was the **fastest bank run in global financial history**:
* Over **\$42 billion in deposits were withdrawn in under 10 hours** on March 9, 2023, followed by queued requests for an additional \$100 billion on March 10.
* Digital banking channels, mobile apps, and venture capitalist communication networks (Slack, WhatsApp, X/Twitter) acted as instant coordination mechanisms, rendering traditional multi-day regulatory liquidity monitoring obsolete.

#### 4. Dual-Sided Balance Sheet Fragility
Traditional Early Warning Systems often focus solely on the **Asset Side** (Credit Risk: Non-Performing Loans) or solely on the **Liability Side** (Deposit outflows). The academic literature of the 2023 crisis shows that catastrophe occurred due to the **simultaneous collision of both sides**:
* **Asset Side:** Unhedged duration risk with 40%+ of balance sheets locked into fixed-rate Held-to-Maturity (HTM) bonds that lost 15–20% of their fair value when the Federal Reserve raised benchmark interest rates by 425 basis points in 2022.
* **Liability Side:** Severe depositor concentration, where over 90% of deposits exceeded the \$250,000 FDIC insurance limit and belonged to a single interconnected industry (tech startups and VC funds).

---

### 2.2 Academic & Industry Benchmarking

| Prior Approach / System | Focus Area | Limitations Revealed in 2023 | Financial Risk EWS Innovation |
| :--- | :--- | :--- | :--- |
| **CAMELS Rating System** | Regulatory compliance & capital ratios | Static, non-public, slow quarterly lag; treats HTM paper losses as non-factors. | **Dynamic Market-to-Market Solvency:** Adjusts regulatory Tier 1 capital dynamically by subtracting both HTM and AFS unrealized paper losses. |
| **Basel III Liquidity Coverage Ratio (LCR)** | High-Quality Liquid Assets (HQLA) | Excluded Category IV regional banks under 2018 EGRRCPA rollbacks. | **Liquidity Fragility Ratio:** Measures uninsured flight risk against unencumbered cash and market-valued AFS securities. |
| **Z-Score / Credit Risk Models** | Default risk via credit defaults (Altman Z) | Focuses on corporate borrower insolvency, completely missing liquidity and duration runs. | **Dual-Sided Vulnerability Model:** Combines Asset Duration Risk (HTM decline) with Liability Run Risk (Uninsured deposit share). |
| **Traditional Econometric Studies** | Single-bank descriptive case studies | Descriptive post-mortem; suffers from small sample size and lack of peer context. | **20-Bank Panel over 60 Quarters:** Full econometric comparison across 4 risk tiers (Casualties, High-Stress Survivors, Regional, Mega Banks). |

---

### 2.3 Feedback, Evaluation & Suggested Improvements

#### DEPI Mentor / Academic Feedback
During initial technical review milestones, academic advisors and DEPI instructors recommended:
1. *Move away from simple manual spreadsheet analysis:* Manual Excel workbooks lack auditability, cannot scale to millions of data points, and are prone to human formula errors.
2. *Eliminate single-firm bias:* Do not analyze SVB in a vacuum; prove that healthy regional banks and mega-banks faced the same macro rate environment without failing.
3. *Prevent Hindsight Bias:* Ensure the analytical dataset strictly stops at Q4 2022 to demonstrate that the early warning alerts were firing prior to the actual March 2023 collapse.

#### Programmatic Improvements Implemented
* **Automated Data Pipeline:** Replaced manual downloads with a standardized, reproducible 5-stage ETL pipeline in Python (`01b` through `05`).
* **Normalized Star Schema:** Designed a 9-table relational database in MySQL ensuring data integrity, primary/foreign key relationships, and sub-second analytical querying.
* **Econometric Panel Expansion:** Scaled the investigation from 1 bank to 20 banks over 15 years (1,200 bank-quarters), incorporating 19 fundamental metrics, 16 loan sectors, and daily stock trading history.
* **Push-Down Analytics Architecture:** Pushed complex mathematical transformations down to Python and MySQL, ensuring that Power BI remains fast and responsive.

---

### 2.4 Final Grading Criteria Alignment

The project is structured to maximize scoring across the 4 core DEPI evaluation criteria:

```
Total Grade Breakdown (100%):
├── 1. Project Documentation & Research (25%)
│   ├── Planning, Literature Review, and Requirements Gathering
│   ├── System Analysis, ERD, and Data Flow Modeling
│   └── User Guides, Technical Architecture, and Source Citations
├── 2. Technical Implementation & Architecture (35%)
│   ├── Reproducible Python ETL Pipeline & DevOps Automation
│   ├── Normalized Relational Star Schema Database (MySQL)
│   └── Advanced Analytics, Risk Formulations, and Push-Down Views
├── 3. Data Visualization & UI/UX Design (25%)
│   ├── Professional Figma Wireframes and Design System
│   ├── 8-Page Interactive Power BI Executive Dashboard
│   └── Actionable Insights, Drill-Downs, and Conditional Alerting
└── 4. Final Defense & Presentation (15%)
    ├── 15-Minute Panel Presentation & Executive Storytelling
    ├── Rigorous EWS Model Backtest Proof & Q&A Defense
    └── Live Demonstration & Code Quality Verification
```
