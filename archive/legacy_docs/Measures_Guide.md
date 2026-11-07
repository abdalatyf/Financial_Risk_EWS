# Financial Risk Measures & Metrics Guide

**Project:** Financial Risk Early Warning System (DEPI Round 5 — Capstone)  
**Workspace:** `power_bi/` & `src/analytics/`  
**Lead Financial Modeler:** Hazem Taha Hosny  
**Lead Data Architect:** Abdalatyf Ahmed Ibrahim  

---

## 1. Overview & Architecture

The Early Warning System (EWS) evaluates **Dual-Sided Concentration Risk** across 20 U.S. commercial banks over a 15-year quarterly panel (2008–2023, 60 quarters, 1,190 bank-quarters). 

The metrics catalog is divided into **7 foundational risk pillars** plus a **Composite EWS Engine**. Calculations originate from two complementary layers:
1. **Python / MySQL Layer:** Vectorized pre-calculations saved in `fact_quarterly_risk_wide.csv` and exposed via SQL views (e.g. `vw_powerbi_executive_summary`, `vw_powerbi_bank_risk_wide`).
2. **Power BI DAX Layer:** Dynamic slice-and-dice measures defined centrally inside the `_Measures` table (`power_bi/power bi project.SemanticModel/definition/tables/_Measures.tmdl`).

> [!IMPORTANT]
> ### 📐 The Golden Rule of DAX Ratio Modeling
> Never write `AVERAGE(Ratio)` across banks or quarters. All aggregated ratios must strictly follow:
> $$\text{Ratio} = \frac{\sum(\text{Numerator})}{\sum(\text{Denominator})}$$

---

## 2. Complete Metrics Catalog by Risk Pillar

### Pillar 1: Capital Adequacy & Duration Shock Scenarios

| Code | Metric Name | Mathematical Formula | Risk Direction | Regulatory Benchmark |
| :--- | :--- | :--- | :---: | :--- |
| **C1** | **CET1 Ratio** | $\frac{\text{Common Equity Tier 1}}{\text{Risk-Weighted Assets (RWA)}}$ | Lower $\rightarrow$ Risk | Basel III Well-Capitalized: $\ge 6.5\%$ |
| **C2** | **Tier 1 Capital Ratio** | $\frac{\text{Tier 1 Capital}}{\text{RWA}}$ | Lower $\rightarrow$ Risk | Regulatory Well-Capitalized: $\ge 8.0\%$ |
| **C3** | **Equity to Assets** | $\frac{\text{Total Consolidated Equity}}{\text{Total Assets}}$ | Lower $\rightarrow$ Risk | Leverage Cushion: $\ge 7.0\%$ |
| **C4** | **HTM Loss to Equity** | $\frac{\max(0, \text{HTM Amortized Cost} - \text{HTM Fair Value})}{\text{Total Consolidated Equity}}$ | Higher $\rightarrow$ Risk | Safe: $< 25\%$ \| Critical: $\ge 50\%$ |
| **C5** | **Total Sec. Loss to Equity** | $\frac{\text{HTM Unrealized Loss} + \text{AFS Unrealized Loss}}{\text{Total Consolidated Equity}}$ | Higher $\rightarrow$ Risk | Capital Wipeout: $\ge 80\%$ |
| **C6** | **Tier 1 Ratio after HTM Loss** *(Capital Illusion Gap)* | $\frac{\text{Tier 1 Capital} - \text{HTM Unrealized Loss}}{\text{RWA}}$ | Lower $\rightarrow$ Risk | Unadjusted vs Adjusted Divergence (SVB dropped from $15.3\%$ to $1.65\%$) |
| **C7** | **Securities Loss to RWA** | $\frac{\text{Total Securities Paper Losses}}{\text{RWA}}$ | Higher $\rightarrow$ Risk | Stress Buffer Depletion |

---

### Pillar 2: Liquidity & Deposit Flight Vulnerability

| Code | Metric Name | Mathematical Formula | Risk Direction | Forensic Meaning |
| :--- | :--- | :--- | :---: | :--- |
| **L1** | **Consolidated Uninsured Deposit Share** | $\frac{\text{Uninsured Domestic Deposits} + \text{Foreign Deposits}}{\text{Total Deposits}}$ | Higher $\rightarrow$ Risk | Peer Avg: $\approx 45\%$ \| SVB: $94.4\%$ |
| **L1a** | **Domestic Uninsured Deposit Share** | $\frac{\text{Uninsured Domestic Deposits}}{\text{Domestic Deposits}}$ | Higher $\rightarrow$ Risk | FFIEC Schedule RC-O Memo line 1 |
| **L1b** | **Foreign Deposit Share** | $\frac{\text{Foreign Branch Deposits}}{\text{Total Consolidated Deposits}}$ | Higher $\rightarrow$ Risk | Offshore flight risk (Cayman branch) |
| **L2** | **Liquid Assets to Assets** | $\frac{\text{Cash Balances} + \text{AFS Fair Value}}{\text{Total Assets}}$ | Lower $\rightarrow$ Risk | First-line liquidity firebreak |
| **L3** | **Liquidity Fragility Ratio (LFR)** | $\frac{\text{Total Uninsured Deposits}}{\text{Cash Balances} + \text{AFS Fair Value}}$ | Higher $\rightarrow$ Risk | **Ratio $> 1.0$ = Mathematical Insolvency under total bank run** (SVB was $4.30\times$) |
| **L4** | **Deposit Growth YoY** | $\frac{\text{Deposits}_t - \text{Deposits}_{t-4}}{\text{Deposits}_{t-4}}$ | Two-sided | Rapid surge ($>30\%$) signals hot venture money; sharp runoff ($<-10\%$) signals bank run |
| **L5** | **Noninterest-Bearing Deposit Share** | $\frac{\text{Noninterest-Bearing Deposits}}{\text{Total Deposits}}$ | Two-sided | Zero-cost deposits that vanish when short-term interest rates spike |
| **L6** | **Loan to Deposit Ratio** | $\frac{\text{Gross Total Loans}}{\text{Total Deposits}}$ | Higher $\rightarrow$ Risk | Core liquidity utilization |

---

### Pillar 3: Wholesale Funding & Borrowing Velocity

| Code | Metric Name | Mathematical Formula | Risk Direction | Forensic Meaning |
| :--- | :--- | :--- | :---: | :--- |
| **F1** | **Borrowings to Assets** | $\frac{\text{Short-Term Borrowings} + \text{FHLB Advances}}{\text{Total Assets}}$ | Higher $\rightarrow$ Risk | High reliance indicates loss of stable core deposit funding |
| **F1a** | **Short-Term Borrowings to Assets** | $\frac{\text{Fed Funds Purchased} + \text{Repos} + \text{Other } <1\text{yr Borrowings}}{\text{Total Assets}}$ | Higher $\rightarrow$ Risk | Volatile repo/interbank dependency |
| **F1b** | **FHLB Advances to Assets** | $\frac{\text{Federal Home Loan Bank Advances}}{\text{Total Assets}}$ | Higher $\rightarrow$ Risk | Emergency liquidity lifeline masking deposit runoff |

---

### Pillar 4: Securities Portfolio & Duration Risk

| Code | Metric Name | Mathematical Formula | Risk Direction | Forensic Meaning |
| :--- | :--- | :--- | :---: | :--- |
| **S1** | **HTM Concentration Ratio** | $\frac{\text{HTM Amortized Cost (Book Value)}}{\text{Total Assets}}$ | Higher $\rightarrow$ Risk | Peer Avg: $<15\%$ \| SVB: $43.7\%$ locked in fixed-rate bonds |
| **S2** | **HTM Loss to Assets** | $\frac{\max(0, \text{HTM Amortized Cost} - \text{HTM Fair Value})}{\text{Total Assets}}$ | Higher $\rightarrow$ Risk | Direct balance sheet asset impairment |
| **S3** | **HTM Fair Value Decline Pct** | $\frac{\text{HTM Amortized Cost} - \text{HTM Fair Value}}{\text{HTM Amortized Cost}}$ | Higher $\rightarrow$ Risk | Percentage paper price collapse due to Fed rate shock |
| **S4** | **Total Securities Share** | $\frac{\text{HTM Book Value} + \text{AFS Fair Value}}{\text{Total Assets}}$ | Higher $\rightarrow$ Risk | Securities-heavy vs loan-heavy bank business model |
| **S5** | **AFS Unrealized Gain / Loss** | $\text{AFS Fair Value} - \text{AFS Amortized Cost}$ | Lower $\rightarrow$ Risk | Marked-to-market securities paper gain/loss |

---

### Pillar 5: Loan Portfolio Diversity & Commercial Real Estate (CRE)

| Code | Metric Name | Mathematical Formula | Risk Direction | Supervisory Guideline |
| :--- | :--- | :--- | :---: | :--- |
| **K1** | **Loans to Assets** | $\frac{\text{Gross Total Loans}}{\text{Total Assets}}$ | Two-sided | Asset allocation to lending |
| **K2** | **C&I Loan Share** | $\frac{\text{Commercial \& Industrial Loans}}{\text{Gross Total Loans}}$ | Higher $\rightarrow$ Risk | Exposure to corporate and venture debt |
| **K3** | **Commercial Real Estate (CRE) Share** | $\frac{\text{Construction} + \text{Multifamily} + \text{Nonfarm Nonresidential}}{\text{Gross Total Loans}}$ | Higher $\rightarrow$ Risk | FDIC Guidance: flags banks exceeding $300\%$ of capital (e.g. NYCB) |
| **K4** | **Loan Portfolio HHI** | $\sum_{i=1}^{16} \left(\frac{\text{Loan Sector}_i}{\text{Gross Total Loans}} \times 100\right)^2$ | Higher $\rightarrow$ Risk | Herfindahl-Hirschman Index across all 16 Call Report Schedule RC-C loan categories |
| **K5** | **Residential Mortgage Share** | $\frac{1\text{–}4\text{ Family Residential Loans}}{\text{Gross Total Loans}}$ | Lower $\rightarrow$ Risk | Granular diversified collateral base |

---

### Pillar 6: Profitability & Earnings Quality

| Code | Metric Name | Mathematical Formula | Risk Direction | Forensic Meaning |
| :--- | :--- | :--- | :---: | :--- |
| **P1** | **Annualized Return on Assets (ROA)** | $\frac{\text{Quarterly Net Income} \times 4}{\text{Total Assets}}$ | Lower $\rightarrow$ Risk | Accounting earnings power (often masked balance sheet losses) |
| **P2** | **Annualized Return on Equity (ROE)** | $\frac{\text{Quarterly Net Income} \times 4}{\text{Total Consolidated Equity}}$ | Lower $\rightarrow$ Risk | Shareholder returns |
| **P3** | **NII Growth YoY** | $\frac{\text{Net Interest Income}_t - \text{Net Interest Income}_{t-4}}{\text{Net Interest Income}_{t-4}}$ | Lower $\rightarrow$ Risk | Net Interest Margin (NIM) compression indicator |
| **P4** | **NII to Assets** | $\frac{\text{Quarterly Net Interest Income} \times 4}{\text{Total Assets}}$ | Lower $\rightarrow$ Risk | Core intermediation margin yield |

---

### Pillar 7: High-Frequency Market & Macro Signals

| Code | Metric Name | Mathematical Formula | Risk Direction | Forensic Meaning |
| :--- | :--- | :--- | :---: | :--- |
| **M1** | **Stock Drawdown from 52-Week Peak** | $\frac{\text{Price}_t - \max_{252}(\text{Price})}{\max_{252}(\text{Price})}$ | Lower $\rightarrow$ Risk | Equity market capitalization collapse (leading indicator) |
| **M2** | **60-Day Stock Volatility** | $\text{StdDev}(\text{Daily Returns}_{t-60}) \times \sqrt{252}$ | Higher $\rightarrow$ Risk | Market anxiety & hedging pressure |
| **M3** | **Fed Rate Change YoY** | $\text{DFF}_t - \text{DFF}_{t-365}$ | Higher $\rightarrow$ Risk | Macro policy shock ($+425\text{ bps}$ in 2022) |

---

## 3. The Composite Early Warning Score (EWS_SCORE)

The Composite EWS Score ($0\text{ to }100$) integrates multi-pillar vulnerability with the **Single-Organ Failure Principle** (a bank can fail from acute liquidity exhaustion even if its 5-year average capital was acceptable):

```
Acute Stress Kicker = max(Score_L3, Score_L4, Score_F1, Score_CapDur, Score_M1)
Composite EWS Score = 0.50 * Multi_Pillar_Base + 0.50 * Acute_Stress_Kicker
```

### Official 4-Tier Supervisory Alert Scale

| Alert Tier | Hex Code | Composite Score | Supervisory Action / Interpretation |
| :--- | :---: | :---: | :--- |
| 🟢 **GREEN** | `#2E7D32` | $\text{Score} < 45.0$ | **Sound / Low Risk:** Balanced liquidity, low run risk, resilient capital buffers. |
| 🟡 **YELLOW** | `#FBC02D` | $45.0 \le \text{Score} < 60.0$ | **Supervisory Watchlist:** Emerging duration headwinds, elevated uninsured shares. |
| 🟠 **AMBER** | `#ED6C02` | $60.0 \le \text{Score} < 80.0$ | **Elevated Concern:** Severe multi-pillar vulnerability, liquidity stress, heightened scrutiny. |
| 🔴 **RED** | `#D32F2F` | $\text{Score} \ge 80.0$ | **Critical Danger / Insolvency:** Imminent run risk or severe single-organ terminal failure. |

---

## 4. Power BI DAX Measure Templates

All DAX measures should be added into the `_Measures` table (`power_bi/power bi project.SemanticModel/definition/tables/_Measures.tmdl`):

### 1. Liquidity Fragility Ratio (LFR)
```dax
LFR = 
VAR TotalUninsured = 
    CALCULATE(
        MAX('financial_risk_ews_db vw_powerbi_executive_summary'[uninsured_deposit_ratio])
    )
RETURN
    DIVIDE(
        SUM('financial_risk_ews_db fact_financials'[Uninsured_Deposits]) + SUM('financial_risk_ews_db fact_financials'[Foreign_Deposits]),
        SUM('financial_risk_ews_db fact_financials'[Cash_Balances]) + SUM('financial_risk_ews_db fact_financials'[AFS_Securities]),
        BLANK()
    )
```

### 2. Supervisory Alert Badge
```dax
Supervisory_Alert_Badge = 
VAR Score = SELECTEDVALUE('financial_risk_ews_db vw_powerbi_executive_summary'[ews_score])
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(Score), "NO DATA",
        Score >= 80,    "🔴 CRITICAL",
        Score >= 60,    "🟠 ELEVATED",
        Score >= 45,    "🟡 WATCHLIST",
        "🟢 SOUND"
    )
```

### 3. Dynamic Alert Color Hex (For Visual Conditional Formatting)
```dax
Alert_Color_Hex = 
VAR Score = SELECTEDVALUE('financial_risk_ews_db vw_powerbi_executive_summary'[ews_score])
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(Score), "#546E7A",
        Score >= 80,    "#D32F2F",
        Score >= 60,    "#ED6C02",
        Score >= 45,    "#FBC02D",
        "#2E7D32"
    )
```
