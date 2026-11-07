# UI/UX Design & Dashboard Storyboard Guide

**Project:** Financial Risk Early Warning System (DEPI Round 5 — Capstone)  
**Lead UI/UX Designer:** Mohamed Lotfy Makram  
**Target Platform:** Microsoft Power BI Desktop (`1920 × 1080 px`, 16:9 Widescreen)  
**Design File:** [📂 `design/EWS_UI-UX.pptx`](../../design/EWS_UI-UX.pptx)  

---

## 1. Design System & Global Standards

### Canvas & Theme Specifications
* **Aspect Ratio:** 16:9 Widescreen (`1920 × 1080 px` in Power BI / `13.33" × 7.5"` in PowerPoint).
* **Color Palette:**
  * **Background Theme:** Financial Intelligence Dark Navy (`#0A192F` / `#0D1B2A`).
  * **Card Containers:** Deep Slate with subtle stroke (`#1B2A4A` / border `#2A3E66`).
  * **Text Typography:** Segoe UI / Calibri:
    * Page Titles: 20pt Bold (`#FFFFFF`)
    * KPI Callout Values: 28pt Bold (`#FFFFFF`)
    * Subtitles & Labels: 10–11pt Regular (`#9FB6CC`)
    * Executive Takeaway Message: 11pt Medium (`#E2E8F0`)
* **Official 4-Tier Supervisory Alert Palette:**
  * 🟢 **Sound / Low Risk:** `#2E7D32` (Score $< 45.0$)
  * 🟡 **Watchlist / Moderate Risk:** `#FBC02D` (Score $45.0\text{--}59.9$)
  * 🟠 **Elevated Concern:** `#ED6C02` (Score $60.0\text{--}79.9$)
  * 🔴 **Critical Danger:** `#D32F2F` (Score $\ge 80.0$)

### Persistent Navigation & Layout Architecture
Every screen maintains an identical 3-zone structure:
1. **Top Header Strip:**
   * Left: Project Brand (`EWS`), DEPI Capstone Badge, Screen Counter (`SCREEN 0X / 09 · Q4 2022`).
   * Center/Right: Screen Title, Subtitle, and the bold **Executive Takeaway Message** (`Message: ...`).
2. **Left-Hand Global Slicer Bar:**
   * **BANK GROUPS:** Casualties (Tier 1), High-stress (Tier 2), Regional (Tier 3), G-SIBs (Tier 4).
   * **RISK LEVELS:** Sound ($<45$), Watchlist ($45\text{--}59$), Elevated ($60\text{--}79$), Critical ($\ge 80$).
3. **Main Content Canvas:**
   * Upper Row: 3 to 5 Primary KPI Cards.
   * Lower Area: Coordinated analytical visuals (Matrices, Scatters, Dual-Axis, and Dumbbell charts).

---

## 2. Screen-by-Screen Blueprint (Screens 01 to 09)

### Screen 01: Executive Command Center & Systemic Risk Overview
* **Narrative Takeaway:** *"Message: Red grows in the crisis banks years before 2023."*
* **Top KPI Strip:**
  1. `COMPOSITE EWS SCORE`
  2. `BANKS AT CRITICAL LEVEL`
  3. `TOTAL UNINSURED EXPOSURE`
  4. `AGGREGATE HTM LOSSES`
* **Main Visual:** **Historical Threat Matrix**
  * Rows: 20 commercial banks (grouped by peer tier).
  * Columns: 60 historical quarters (2008-Q1 to 2022-Q4).
  * Cell Formatting: Compact square tiles colored by the 4 alert tiers with font color matching background color to eliminate text clutter.
  * Hover Tooltip: Displays Bank Name, Quarter, EWS Score, Alert Level, and Top Risk Driver.

### Screen 02: Funding & Run Risk
* **Narrative Takeaway:** *"Message: SVB and its peers sit in the high-risk corner: high uninsured share and high fragility."*
* **Top KPI Strip:** $L1$ Uninsured Ratio, $L1b$ Domestic Uninsured Ratio, $L3$ Liquidity Fragility Ratio, $L2$ Liquid Assets to Assets, $F1$ Borrowings to Assets.
* **Visuals:**
  * **Funding Vulnerability Map:** Scatter chart ($X = L1 \text{ Uninsured Share}$, $Y = L3 \text{ Fragility Ratio}$, Size = Total Assets). Danger Zone: Upper-right quadrant ($L1 > 70\%, L3 > 1.0\times$).
  * **Funding Sources:** Stacked column chart ($F1a \text{ Short-Term Borrowings} + F1b \text{ FHLB Advances}$).
  * **Deposit Dynamics:** Dual line chart ($L4 \text{ Deposit Growth YoY}$ vs $L5 \text{ Noninterest-Bearing Share}$).

### Screen 03: Securities & Rate Shock
* **Narrative Takeaway:** *"Message: Rising rates cut bond values; the paper losses grew to nearly all of equity."*
* **Top KPI Strip:** $S1$ HTM Concentration, $S2$ HTM Loss to Assets, $S3$ HTM FV Decline Pct, $S4$ Total Securities Share.
* **Visuals:**
  * **HTM vs Fed Rate Hikes:** Dual-axis chart ($S1 + S3 \text{ lines}$ vs $M3 \text{ Fed Rate Change columns}$).
  * **Securities Loss to Equity:** Line chart ($C4 \text{ HTM Loss} + C5 \text{ Total Securities Loss}$).
  * **AFS Unrealized Gain/Loss:** Column chart ($S5$ marked-to-market).

### Screen 04: Capital Adequacy & Duration Scenarios
* **Narrative Takeaway:** *"Message: Reported capital looks compliant; under the HTM-loss scenario the cushion shrinks sharply."*
* **Top KPI Strip:** $C1$ CET1 Ratio, $C2$ Tier 1 Capital Ratio, $C3$ Equity to Assets, $C7$ Securities Loss to RWA.
* **Visuals:**
  * **Capital Illusion Gap (Dumbbell Chart):** $C2$ Reported Tier 1 vs $C6$ Tier 1 after HTM Loss per bank.
  * **CET1 vs PCA Reference:** Line chart of $C1$ over time with a constant reference line at $6.5\%$ (Well-Capitalized).
  * **Securities Loss to RWA:** Column chart of $C7$ over time.

### Screen 05: Multi-Measure Profitability
* **Narrative Takeaway:** *"Message: Profitability looked healthy while unrealized bond losses were growing."*
* **Top KPI Strip:** $P1$ Annualized ROA, $P2$ Annualized ROE, $P3$ NII Growth YoY, $P4$ NII to Assets.
* **Visuals:**
  * **ROA & ROE Trend:** Line charts of $P1$ and $P2$ over time.
  * **NII Growth Velocity:** Column chart of $P3$ with zero baseline.
  * **Core Margin Yield:** Line chart of $P4$ over time.

### Screen 06: CRE & Loan Portfolio Concentration
* **Narrative Takeaway:** *"Message: Resilient banks spread their loans; crisis banks concentrate in CRE or in one sector."*
* **Top KPI Strip:** $K2$ C&I Share, $K3$ CRE Share, $K4$ Loan HHI, $K1$ Loans to Assets, $K5$ Residential Share.
* **Visuals:**
  * **Loan Mix by Sector:** 100% stacked bar chart decomposing 16 sectors into 6 visual slices (C&I, Construction, Multifamily, Commercial RE, Residential, Other).
  * **CRE Concentration Ranking:** Horizontal bar chart of $K3$ CRE Share per bank against the FDIC $300\%$ guideline.

### Screen 07: Market Sentiment & Macro Signals
* **Narrative Takeaway:** *"Message: Markets and rates flagged stress before the filings did."*
* **Top KPI Strip:** $M1$ 52-Week Stock Drawdown, $M2$ 60-Day Volatility, $M3$ Fed Rate Change YoY.
* **Visuals:**
  * **Peak-to-Trough Drawdown:** Line chart tracking equity collapse ($M1$).
  * **Equity Market Volatility:** Line chart of 60-day annualized volatility ($M2$).
  * **Market vs Rates:** Dual-axis chart correlating stock drawdown ($M1$) with Fed rate hike speed ($M3$).

### Screen 08: Composite Model Backtest & Validation
* **Narrative Takeaway:** *"Message: The composite signal moves earlier than the traditional C1 + P1 baseline."*
* **Visuals:**
  * **Model Trajectory vs Baseline:** Line chart comparing Composite EWS Score ($0\text{--}100$) against the traditional CAMELS $C1+P1$ regulatory baseline.
  * **Empirical Backtest Table:** Matrix showing Failure Quarter, First Critical Signal Quarter, Lead Time (Quarters), and False Alarm Rates across the 20-bank panel.

### Screen 09: Single-Bank Supervisory Deep Dive
* **Narrative Takeaway:** Examiner diagnostic workstation for full forensic audit of any selected bank.
* **Visuals:**
  * **Bank Identification Card:** Legal Name, Ticker, FDIC Certificate, Peer Cohort, Latest Filing Date.
  * **Composite Risk Badge:** Large circular score badge with 4-tier alert badge.
  * **16-Sparkline Grid:** Structured into 4 thematic diagnostic rows:
    * *Row 1 (Capital):* $C1, C2, C4, C5, C6$
    * *Row 2 (Liquidity):* $L1, L3, L4, F1$
    * *Row 3 (Assets/Credit):* $S1, S3, K2, K3$
    * *Row 4 (Earnings/Market):* $P1, M1, M3$

---

## 3. How to Edit the Design Across Git

The UI/UX design is fully integrated into the Git workflow and can be edited in two ways:

### Method A: Direct Editing in Microsoft PowerPoint
1. Pull the latest code on your branch:
   ```bash
   git checkout feature/<your-name>
   git pull origin main
   ```
2. Open [`design/EWS_UI-UX.pptx`](../../design/EWS_UI-UX.pptx) in PowerPoint.
3. Edit slides, adjust layouts, modify cards, or update notes.
4. Save and close PowerPoint.
5. Commit and push:
   ```bash
   git add design/EWS_UI-UX.pptx
   git commit -m "feat(uiux): update Screen 04 layout and card styling"
   git push origin feature/<your-name>
   ```

### Method B: Programmatic Python Automation (`python-pptx`)
You can programmatically read, inspect, and update slide shapes, text, or notes via Python:
```python
from pptx import Presentation

prs = Presentation("design/EWS_UI-UX.pptx")
slide = prs.slides[0]  # Screen 01

# Inspect shapes
for shape in slide.shapes:
    if shape.has_text_frame:
        print(shape.name, ":", shape.text_frame.text)

# Save updates
prs.save("design/EWS_UI-UX.pptx")
```

### Method C: Markdown Text Specification
If you update visual specifications, thresholds, or layout rules, update this file (`UI_UX_Design_Guide.md`). GitHub will generate clean, line-by-line visual diffs for team pull requests.
