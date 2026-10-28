import os
import sys
import numpy as np
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

class RiskMetricsCalculator:
    """
    Financial Risk EWS - Quantitative Analytics & Risk Engine.
    Implements Hazem's 32 Risk Measures, Composite EWS Scoring Engine, 
    and MySQL Relational Star Schema / Analytical Views.
    """

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.processed_dir = os.path.join(self.base_dir, "data", "processed")
        self.config_dir = os.path.join(self.base_dir, "config")
        
        load_dotenv(os.path.join(self.base_dir, ".env"))
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("MYSQL_DATABASE", "Financial_Risk_EWS_db")
        self.connection = None

        # Metadata catalog for all 33 metrics (32 measures + EWS Composite Score)
        self.metric_definitions = [
            # 1. Capital Adequacy
            ("C1", "CET1 Ratio", "Capital", True, "lower_is_risk", "Common Equity Tier 1 capital over risk-weighted assets"),
            ("C2", "Tier 1 Capital Ratio", "Capital", True, "lower_is_risk", "Regulatory Tier 1 capital over risk-weighted assets"),
            ("C3", "Equity to Assets", "Capital", False, "lower_is_risk", "Total consolidated equity capital over total assets"),
            ("C4", "HTM Loss to Equity", "Capital", True, "higher_is_risk", "Held-to-Maturity unrealized bond loss over total equity"),
            ("C5", "Total Securities Loss to Equity", "Capital", True, "higher_is_risk", "Combined HTM and AFS unrealized losses over total equity"),
            ("C6", "Tier 1 Ratio after HTM Loss", "Capital", True, "lower_is_risk", "Tier 1 capital minus HTM unrealized loss over RWA"),
            ("C7", "Securities Loss to RWA", "Capital", False, "higher_is_risk", "Combined bond portfolio paper losses over RWA"),

            # 2. Liquidity & Deposits
            ("L1", "Consolidated Uninsured Deposit Ratio", "Liquidity", True, "higher_is_risk", "Total uninsured domestic and foreign deposits over total deposits"),
            ("L1a", "Domestic Uninsured Deposit Ratio", "Liquidity", False, "higher_is_risk", "Uninsured domestic deposits over total domestic deposits"),
            ("L1b", "Foreign Deposit Share", "Liquidity", False, "higher_is_risk", "Foreign branch deposits over total consolidated deposits"),
            ("L2", "Liquid Assets to Assets", "Liquidity", False, "lower_is_risk", "Cash balances plus AFS market value securities over total assets"),
            ("L3", "Liquidity Fragility Ratio", "Liquidity", True, "higher_is_risk", "Total uninsured deposits over liquid assets (Cash + AFS)"),
            ("L4", "Deposit Growth YoY", "Liquidity", True, "two_sided", "Year-over-year growth rate in total deposits"),
            ("L5", "Noninterest-Bearing Deposit Share", "Liquidity", False, "two_sided", "Demand noninterest-bearing deposits over total deposits"),
            ("L6", "Loan to Deposit Ratio", "Liquidity", False, "higher_is_risk", "Total net loans over total deposits"),

            # 3. Wholesale Funding
            ("F1", "Borrowings to Assets", "Funding", True, "higher_is_risk", "Short-term borrowings plus FHLB advances over total assets"),
            ("F1a", "Short-Term Borrowings to Assets", "Funding", False, "higher_is_risk", "Short-term wholesale borrowings over total assets"),
            ("F1b", "FHLB Advances to Assets", "Funding", False, "higher_is_risk", "FHLB emergency liquidity advances over total assets"),

            # 4. Securities & Duration
            ("S1", "HTM Concentration Ratio", "Securities", True, "higher_is_risk", "Held-to-Maturity securities book carrying value over total assets"),
            ("S2", "HTM Loss to Assets", "Securities", False, "higher_is_risk", "Unrealized HTM paper loss over total assets"),
            ("S3", "HTM Fair-Value Decline Pct", "Securities", True, "higher_is_risk", "Percentage market price devaluation of HTM portfolio"),
            ("S4", "Total Securities Share", "Securities", False, "higher_is_risk", "Total securities holdings (HTM + AFS) over total assets"),
            ("S5", "AFS Unrealized Gain Loss", "Securities", False, "lower_is_risk", "AFS fair market value minus amortized cost"),

            # 5. Credit & Loan Diversity
            ("K2", "C&I Loan Share", "Credit", True, "higher_is_risk", "Commercial and industrial loans over total gross loans"),
            ("K3", "Commercial Real Estate Share", "Credit", True, "higher_is_risk", "Construction, multifamily, and nonfarm commercial RE over total gross loans"),
            ("K4", "Loan Portfolio HHI", "Credit", False, "higher_is_risk", "Herfindahl-Hirschman Index of loan diversification across 16 sectors"),

            # 6. Profitability
            ("P1", "Annualized Return on Assets (ROA)", "Profitability", True, "lower_is_risk", "Quarterly net income annualized (x4) over total assets"),
            ("P2", "Annualized Return on Equity (ROE)", "Profitability", False, "lower_is_risk", "Quarterly net income annualized (x4) over total equity"),
            ("P3", "Net Interest Income Growth YoY", "Profitability", False, "lower_is_risk", "Year-over-year percentage change in net interest income"),
            ("P4", "NII to Assets", "Profitability", False, "lower_is_risk", "Quarterly net interest income annualized (x4) over total assets"),

            # 7. Market & Macro Shock
            ("M1", "Stock Drawdown from 52-Week Peak", "Market", True, "lower_is_risk", "Equity price decline relative to preceding 252-day peak"),
            ("M2", "60-Day Stock Volatility", "Market", False, "higher_is_risk", "Annualized standard deviation of daily equity returns over past 60 days"),
            ("M3", "Fed Rate Change YoY", "Market", True, "higher_is_risk", "Year-over-year change in Federal Funds Effective Rate (percentage points)"),

            # 8. Composite Index
            ("EWS_SCORE", "Composite Early Warning Risk Score", "Composite", True, "higher_is_risk", "Weighted multi-pillar risk index (0 to 100)")
        ]

    def load_processed_data(self):
        """Loads and merges foundational datasets."""
        print("[INFO] Loading processed datasets from data/processed/...")
        fin_path = os.path.join(self.processed_dir, "fact_financials.csv")
        loans_path = os.path.join(self.processed_dir, "fact_loan_sectors.csv")
        mkt_path = os.path.join(self.processed_dir, "fact_daily_market.csv")
        fed_path = os.path.join(self.processed_dir, "dim_macro_fed_rates.csv")
        banks_path = os.path.join(self.config_dir, "banks.csv")

        df_fin = pd.read_csv(fin_path)
        df_loans = pd.read_csv(loans_path)
        df_mkt = pd.read_csv(mkt_path)
        df_fed = pd.read_csv(fed_path)
        df_banks = pd.read_csv(banks_path)

        # Merge financial and loan facts (1,190 bank-quarters)
        df = pd.merge(df_fin, df_loans.drop(columns=['Bank_Name']), on=['Date', 'Bank_ID', 'IDRSSD'])
        df['quarter_id'] = pd.to_datetime(df['Date']).dt.to_period('Q').dt.strftime('%Y-Q%q')
        df = df.sort_values(['IDRSSD', 'Date']).reset_index(drop=True)

        return df, df_mkt, df_fed, df_banks

    def calculate_metrics(self, df, df_mkt, df_fed, df_banks):
        """Calculates all 32 risk indicators and Composite EWS Score."""
        print("[INFO] Calculating Hazem's 32 Risk Measures and Composite EWS Engine...")

        # Helper constructs
        total_equity_cap = df['Total_Equity'] + df['Noncontrolling_Interest'].fillna(0.0)
        unrealized_htm_loss = df['HTM_Securities'] - df['HTM_Fair_Value']
        unrealized_afs_loss = df['AFS_Amortized_Cost'] - df['AFS_Securities']
        total_sec_loss = unrealized_htm_loss + unrealized_afs_loss
        total_uninsured_deposits = df['Uninsured_Deposits'] + df['Foreign_Deposits']
        liquid_assets = df['Cash_Balances'] + df['AFS_Securities']

        # -------------------------------------------------------------
        # Pillar 1: Capital Adequacy
        # -------------------------------------------------------------
        df['C1'] = df['CET1_Ratio_Pct']
        df['C2'] = df['Tier1_Ratio_Pct']
        df['C3'] = total_equity_cap / df['Total_Assets']
        df['C4'] = unrealized_htm_loss / total_equity_cap
        df['C5'] = total_sec_loss / total_equity_cap
        df['C6'] = (df['Tier1_Capital'] - unrealized_htm_loss) / df['Risk_Weighted_Assets']
        df['C7'] = total_sec_loss / df['Risk_Weighted_Assets']

        # -------------------------------------------------------------
        # Pillar 2: Liquidity & Deposits
        # -------------------------------------------------------------
        df['L1'] = total_uninsured_deposits / df['Total_Deposits']
        df['L1a'] = df['Uninsured_Deposits'] / df['Domestic_Deposits']
        df['L1b'] = df['Foreign_Deposits'] / df['Total_Deposits']
        df['L2'] = liquid_assets / df['Total_Assets']
        df['L3'] = total_uninsured_deposits / liquid_assets
        
        # L4: Deposit Growth YoY (grouped by bank)
        df['L4'] = df.groupby('IDRSSD')['Total_Deposits'].pct_change(4)
        df['L5'] = df['Noninterest_Bearing_Deposits'] / df['Total_Deposits']
        df['L6'] = df['Total_Loans'] / df['Total_Deposits']

        # -------------------------------------------------------------
        # Pillar 3: Wholesale Funding
        # -------------------------------------------------------------
        df['F1'] = (df['Short_Term_Borrowings'] + df['FHLB_Advances']) / df['Total_Assets']
        df['F1a'] = df['Short_Term_Borrowings'] / df['Total_Assets']
        df['F1b'] = df['FHLB_Advances'] / df['Total_Assets']

        # -------------------------------------------------------------
        # Pillar 4: Securities & Duration
        # -------------------------------------------------------------
        df['S1'] = df['HTM_Securities'] / df['Total_Assets']
        df['S2'] = unrealized_htm_loss / df['Total_Assets']
        # S3: Price decline % (clamp division by zero if HTM == 0)
        df['S3'] = np.where(df['HTM_Securities'] > 0, 1.0 - (df['HTM_Fair_Value'] / df['HTM_Securities']), 0.0)
        df['S4'] = (df['HTM_Securities'] + df['AFS_Securities']) / df['Total_Assets']
        df['S5'] = df['AFS_Securities'] - df['AFS_Amortized_Cost']

        # -------------------------------------------------------------
        # Pillar 5: Credit & Loan Diversity
        # -------------------------------------------------------------
        # We use Gross_Total_Loans for loan shares so all 16 sector slices sum exactly to 100%
        loan_base = df['Gross_Total_Loans'].replace(0, np.nan)
        df['K2'] = df['8_C_and_I'] / loan_base
        cre_volume = df['1_Construction'] + df['4_Multifamily'] + df['5_Commercial_RE']
        df['K3'] = cre_volume / loan_base

        # K4: Loan HHI across all 16 discrete sectors
        sector_cols = [c for c in df.columns if c[0].isdigit()]
        sector_shares_sq = np.zeros(len(df))
        for col in sector_cols:
            share = (df[col] / loan_base) * 100.0
            sector_shares_sq += np.nan_to_num(share ** 2, nan=0.0)
        df['K4'] = sector_shares_sq

        # -------------------------------------------------------------
        # Pillar 6: Profitability
        # -------------------------------------------------------------
        df['P1'] = (df['Net_Income'] * 4.0) / df['Total_Assets']
        df['P2'] = (df['Net_Income'] * 4.0) / df['Total_Equity']
        df['P3'] = df.groupby('IDRSSD')['Net_Interest_Income'].pct_change(4)
        df['P4'] = (df['Net_Interest_Income'] * 4.0) / df['Total_Assets']

        # -------------------------------------------------------------
        # Pillar 7: Market & Macro Shock (M1, M2, M3)
        # -------------------------------------------------------------
        # Precompute daily market metrics per ticker
        df_mkt['Date'] = pd.to_datetime(df_mkt['Date'])
        df_mkt = df_mkt.sort_values(['Ticker', 'Date']).reset_index(drop=True)
        df_mkt['Daily_Return'] = df_mkt.groupby('Ticker')['Close'].pct_change()
        df_mkt['Rolling_252_Max'] = df_mkt.groupby('Ticker')['Close'].transform(lambda x: x.rolling(252, min_periods=1).max())
        df_mkt['Drawdown'] = df_mkt['Close'] / df_mkt['Rolling_252_Max'] - 1.0
        # 60-day annualized volatility
        df_mkt['Rolling_60_Vol'] = df_mkt.groupby('Ticker')['Daily_Return'].transform(lambda x: x.rolling(60, min_periods=20).std() * np.sqrt(252))

        # Map IDRSSD to Ticker
        idrssd_to_ticker = dict(zip(df_banks['idrssd'].astype(int), df_banks['ticker']))
        df['Ticker'] = df['IDRSSD'].map(idrssd_to_ticker)

        # Precompute Fed Rate series per quarter
        df_fed['Date'] = pd.to_datetime(df_fed['Date'])
        df_fed = df_fed.sort_values('Date').reset_index(drop=True)
        unique_dates = sorted(df['Date'].unique())
        fed_q_map = {}
        for i, d_str in enumerate(unique_dates):
            d = pd.to_datetime(d_str)
            curr_matches = df_fed[df_fed['Date'] <= d]
            r_curr = curr_matches['Fed_Rate'].iloc[-1] if not curr_matches.empty else 0.0
            if i >= 4:
                d_prev = pd.to_datetime(unique_dates[i-4])
                prev_matches = df_fed[df_fed['Date'] <= d_prev]
                r_prev = prev_matches['Fed_Rate'].iloc[-1] if not prev_matches.empty else r_curr
                diff = r_curr - r_prev
            else:
                diff = np.nan
            fed_q_map[d_str] = diff

        df['M3'] = df['Date'].map(fed_q_map)

        # Compute M1 & M2 on quarter-end dates for each row
        m1_vals = []
        m2_vals = []
        df['Date_dt'] = pd.to_datetime(df['Date'])

        for _, row in df.iterrows():
            ticker = row['Ticker']
            q_date = row['Date_dt']
            mkt_bank = df_mkt[(df_mkt['Ticker'] == ticker) & (df_mkt['Date'] <= q_date)]
            if not mkt_bank.empty:
                last_row = mkt_bank.iloc[-1]
                # If last trading was within 120 days of quarter end, use it
                if (q_date - last_row['Date']).days <= 120:
                    m1_vals.append(last_row['Drawdown'])
                    m2_vals.append(last_row['Rolling_60_Vol'])
                else:
                    m1_vals.append(np.nan)
                    m2_vals.append(np.nan)
            else:
                m1_vals.append(np.nan)
                m2_vals.append(np.nan)

        df['M1'] = m1_vals
        df['M2'] = m2_vals
        df = df.drop(columns=['Date_dt', 'Ticker'])

        # -------------------------------------------------------------
        # Pillar 8: Composite EWS Score Engine (Hazem's 6 Core Drivers)
        # -------------------------------------------------------------
        # Piecewise linear scaling with clamping to [0, 100]
        # L3: Liquidity Fragility (25%) [0.50 -> 0, 1.00 -> 100]
        l3_score = np.clip((df['L3'].fillna(0.0) - 0.50) / (1.00 - 0.50) * 100.0, 0.0, 100.0)

        # C6: Adjusted Tier 1 Capital (20%) [10.0% -> 0, 4.0% -> 100]
        c6_val = df['C6'].fillna(0.12)
        c6_score = np.clip((0.10 - c6_val) / (0.10 - 0.04) * 100.0, 0.0, 100.0)

        # S1: HTM Concentration (20%) [15.0% -> 0, 35.0% -> 100]
        s1_score = np.clip((df['S1'].fillna(0.0) - 0.15) / (0.35 - 0.15) * 100.0, 0.0, 100.0)

        # L1: Consolidated Uninsured Deposits (15%) [50.0% -> 0, 80.0% -> 100]
        l1_score = np.clip((df['L1'].fillna(0.0) - 0.50) / (0.80 - 0.50) * 100.0, 0.0, 100.0)

        # F1: Borrowings to Assets (10%) [4.0% -> 0, 12.0% -> 100]
        f1_score = np.clip((df['F1'].fillna(0.0) - 0.04) / (0.12 - 0.04) * 100.0, 0.0, 100.0)

        # K3: CRE Exposure Share (10%) [20.0% -> 0, 40.0% -> 100]
        k3_score = np.clip((df['K3'].fillna(0.0) - 0.20) / (0.40 - 0.20) * 100.0, 0.0, 100.0)

        # Composite Weighted Index (0 - 100)
        df['EWS_SCORE'] = (
            0.25 * l3_score +
            0.20 * c6_score +
            0.20 * s1_score +
            0.15 * l1_score +
            0.10 * f1_score +
            0.10 * k3_score
        ).round(2)

        # Store individual component stress scores for explainability
        df['L3_Score'] = l3_score.round(1)
        df['C6_Score'] = c6_score.round(1)
        df['S1_Score'] = s1_score.round(1)
        df['L1_Score'] = l1_score.round(1)
        df['F1_Score'] = f1_score.round(1)
        df['K3_Score'] = k3_score.round(1)

        # Assign Supervisory Alert Level
        conditions = [
            (df['EWS_SCORE'] < 60.0),
            (df['EWS_SCORE'] >= 60.0) & (df['EWS_SCORE'] < 80.0),
            (df['EWS_SCORE'] >= 80.0)
        ]
        choices = ['GREEN', 'AMBER', 'RED']
        df['Alert_Level'] = np.select(conditions, choices, default='GREEN')

        # Re-sort consistently by Date and Bank_ID
        df = df.sort_values(['Date', 'Bank_ID']).reset_index(drop=True)
        return df

    def export_csvs(self, df):
        """Saves wide and long analytical datasets to data/processed/."""
        print("[INFO] Exporting analytical CSVs...")

        # 1. Wide Dataset
        wide_cols = [
            'Date', 'quarter_id', 'Bank_ID', 'IDRSSD',
            'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7',
            'L1', 'L1a', 'L1b', 'L2', 'L3', 'L4', 'L5', 'L6',
            'F1', 'F1a', 'F1b',
            'S1', 'S2', 'S3', 'S4', 'S5',
            'K2', 'K3', 'K4',
            'P1', 'P2', 'P3', 'P4',
            'M1', 'M2', 'M3',
            'EWS_SCORE', 'Alert_Level',
            'L3_Score', 'C6_Score', 'S1_Score', 'L1_Score', 'F1_Score', 'K3_Score'
        ]
        df_wide = df[wide_cols].copy()
        wide_path = os.path.join(self.processed_dir, "fact_quarterly_risk_wide.csv")
        df_wide.to_csv(wide_path, index=False)
        print(f"[SUCCESS] Saved Wide Analytical Dataset ({len(df_wide)} rows) to: {wide_path}")

        # 2. Long Dataset (Unpivoted for Star Schema)
        metric_codes = [m[0] for m in self.metric_definitions]
        df_long = df.melt(
            id_vars=['quarter_id', 'IDRSSD'],
            value_vars=metric_codes,
            var_name='metric_code',
            value_name='metric_value'
        )
        long_path = os.path.join(self.processed_dir, "fact_quarterly_risk_long.csv")
        df_long.to_csv(long_path, index=False)
        print(f"[SUCCESS] Saved Long Relational Dataset ({len(df_long)} rows) to: {long_path}")

        return df_wide, df_long

    def connect_db(self):
        """Connects to MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host, user=self.user, password=self.password, database=self.database
            )
            print(f"[SUCCESS] Connected to MySQL Database: {self.database}")
        except Exception as e:
            print(f"[ERROR] Could not connect to MySQL: {e}")
            self.connection = None

    def load_to_mysql(self, df_wide, df_long):
        """Creates dim_risk_metric, fact_risk_metrics, and analytical views in MySQL."""
        if not self.connection or not self.connection.is_connected():
            print("[WARN] MySQL not connected. Skipping database loading.")
            return

        cursor = self.connection.cursor()
        print("[INFO] Creating relational tables `dim_risk_metric` and `fact_risk_metrics`...")

        # 1. Create dim_risk_metric
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dim_risk_metric (
                metric_id INT AUTO_INCREMENT PRIMARY KEY,
                metric_code VARCHAR(10) UNIQUE NOT NULL,
                metric_name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                is_core BOOLEAN NOT NULL DEFAULT FALSE,
                risk_direction VARCHAR(20) NOT NULL,
                description TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Insert metadata definitions
        metric_id_map = {}
        for code, name, cat, is_core, direction, desc in self.metric_definitions:
            cursor.execute("""
                INSERT INTO dim_risk_metric (metric_code, metric_name, category, is_core, risk_direction, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    metric_name=VALUES(metric_name), category=VALUES(category), 
                    is_core=VALUES(is_core), risk_direction=VALUES(risk_direction), description=VALUES(description)
            """, (code, name, cat, is_core, direction, desc))
            
            cursor.execute("SELECT metric_id FROM dim_risk_metric WHERE metric_code=%s", (code,))
            metric_id_map[code] = cursor.fetchone()[0]

        # 2. Create fact_risk_metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fact_risk_metrics (
                quarter_id VARCHAR(10) NOT NULL,
                idrssd INT NOT NULL,
                metric_id INT NOT NULL,
                metric_value DECIMAL(18, 6) NULL,
                PRIMARY KEY (quarter_id, idrssd, metric_id),
                CONSTRAINT fk_frm_quarter FOREIGN KEY (quarter_id) REFERENCES dim_quarter (quarter_id),
                CONSTRAINT fk_frm_bank FOREIGN KEY (idrssd) REFERENCES dim_bank (idrssd),
                CONSTRAINT fk_frm_metric FOREIGN KEY (metric_id) REFERENCES dim_risk_metric (metric_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Clear previous rows if any and bulk insert
        cursor.execute("TRUNCATE TABLE fact_risk_metrics")
        df_long['metric_id'] = df_long['metric_code'].map(metric_id_map)

        insert_data = []
        for _, row in df_long.iterrows():
            val = None if pd.isna(row['metric_value']) else float(row['metric_value'])
            insert_data.append((
                row['quarter_id'],
                int(row['IDRSSD']),
                int(row['metric_id']),
                val
            ))

        cursor.executemany("""
            INSERT INTO fact_risk_metrics (quarter_id, idrssd, metric_id, metric_value)
            VALUES (%s, %s, %s, %s)
        """, insert_data)
        self.connection.commit()
        print(f"[SUCCESS] Loaded {len(insert_data)} records into `fact_risk_metrics`!")

        # 3. Create Power BI Analytical Views
        print("[INFO] Creating optimized SQL analytical views for Power BI Desktop...")

        # View 1: vw_powerbi_executive_summary
        cursor.execute("DROP VIEW IF EXISTS vw_powerbi_executive_summary")
        cursor.execute("""
            CREATE VIEW vw_powerbi_executive_summary AS
            SELECT 
                b.bank_id,
                b.bank_name,
                b.tier,
                b.tier_label,
                q.quarter_id,
                q.year,
                q.quarter_num,
                q.era,
                MAX(CASE WHEN m.metric_code = 'EWS_SCORE' THEN f.metric_value END) AS ews_score,
                CASE 
                    WHEN MAX(CASE WHEN m.metric_code = 'EWS_SCORE' THEN f.metric_value END) >= 80.0 THEN 'RED'
                    WHEN MAX(CASE WHEN m.metric_code = 'EWS_SCORE' THEN f.metric_value END) >= 60.0 THEN 'AMBER'
                    ELSE 'GREEN'
                END AS alert_level,
                MAX(CASE WHEN m.metric_code = 'L3' THEN f.metric_value END) AS liquidity_fragility_ratio,
                MAX(CASE WHEN m.metric_code = 'C6' THEN f.metric_value END) AS tier1_after_htm_loss,
                MAX(CASE WHEN m.metric_code = 'S1' THEN f.metric_value END) AS htm_concentration_ratio,
                MAX(CASE WHEN m.metric_code = 'L1' THEN f.metric_value END) AS uninsured_deposit_ratio,
                MAX(CASE WHEN m.metric_code = 'F1' THEN f.metric_value END) AS borrowings_to_assets,
                MAX(CASE WHEN m.metric_code = 'K3' THEN f.metric_value END) AS cre_share
            FROM fact_risk_metrics f
            JOIN dim_bank b ON f.idrssd = b.idrssd
            JOIN dim_quarter q ON f.quarter_id = q.quarter_id
            JOIN dim_risk_metric m ON f.metric_id = m.metric_id
            GROUP BY b.bank_id, b.bank_name, b.tier, b.tier_label, q.quarter_id, q.year, q.quarter_num, q.era;
        """)

        # View 2: vw_powerbi_loan_concentration
        cursor.execute("DROP VIEW IF EXISTS vw_powerbi_loan_concentration")
        cursor.execute("""
            CREATE VIEW vw_powerbi_loan_concentration AS
            SELECT 
                b.bank_id,
                b.bank_name,
                b.tier,
                b.tier_label,
                q.quarter_id,
                q.year,
                q.quarter_num,
                s.sector_name,
                l.loan_amount,
                k.loan_hhi,
                k.cre_share,
                k.ci_share
            FROM fact_loan_balances l
            JOIN dim_bank b ON l.idrssd = b.idrssd
            JOIN dim_quarter q ON l.quarter_id = q.quarter_id
            JOIN dim_loan_sector s ON l.sector_id = s.sector_id
            LEFT JOIN (
                SELECT 
                    r.quarter_id,
                    r.idrssd,
                    MAX(CASE WHEN m.metric_code = 'K4' THEN r.metric_value END) AS loan_hhi,
                    MAX(CASE WHEN m.metric_code = 'K3' THEN r.metric_value END) AS cre_share,
                    MAX(CASE WHEN m.metric_code = 'K2' THEN r.metric_value END) AS ci_share
                FROM fact_risk_metrics r
                JOIN dim_risk_metric m ON r.metric_id = m.metric_id
                WHERE m.metric_code IN ('K2', 'K3', 'K4')
                GROUP BY r.quarter_id, r.idrssd
            ) k ON l.quarter_id = k.quarter_id AND l.idrssd = k.idrssd;
        """)

        # View 3: vw_powerbi_bank_risk_wide
        cursor.execute("DROP VIEW IF EXISTS vw_powerbi_bank_risk_wide")
        cursor.execute("""
            CREATE VIEW vw_powerbi_bank_risk_wide AS
            SELECT 
                b.bank_id,
                b.bank_name,
                b.tier,
                b.tier_label,
                q.quarter_id,
                q.year,
                q.quarter_num,
                q.era,
                MAX(CASE WHEN m.metric_code = 'C1' THEN f.metric_value END) AS C1_CET1_Ratio,
                MAX(CASE WHEN m.metric_code = 'C2' THEN f.metric_value END) AS C2_Tier1_Ratio,
                MAX(CASE WHEN m.metric_code = 'C3' THEN f.metric_value END) AS C3_Equity_to_Assets,
                MAX(CASE WHEN m.metric_code = 'C4' THEN f.metric_value END) AS C4_HTM_Loss_to_Equity,
                MAX(CASE WHEN m.metric_code = 'C5' THEN f.metric_value END) AS C5_Total_Sec_Loss_to_Equity,
                MAX(CASE WHEN m.metric_code = 'C6' THEN f.metric_value END) AS C6_Tier1_after_HTM_Loss,
                MAX(CASE WHEN m.metric_code = 'C7' THEN f.metric_value END) AS C7_Sec_Loss_to_RWA,
                MAX(CASE WHEN m.metric_code = 'L1' THEN f.metric_value END) AS L1_Consolidated_Uninsured_Share,
                MAX(CASE WHEN m.metric_code = 'L1a' THEN f.metric_value END) AS L1a_Domestic_Uninsured_Share,
                MAX(CASE WHEN m.metric_code = 'L1b' THEN f.metric_value END) AS L1b_Foreign_Deposit_Share,
                MAX(CASE WHEN m.metric_code = 'L2' THEN f.metric_value END) AS L2_Liquid_Assets_to_Assets,
                MAX(CASE WHEN m.metric_code = 'L3' THEN f.metric_value END) AS L3_Liquidity_Fragility_Ratio,
                MAX(CASE WHEN m.metric_code = 'L4' THEN f.metric_value END) AS L4_Deposit_Growth_YoY,
                MAX(CASE WHEN m.metric_code = 'L5' THEN f.metric_value END) AS L5_Noninterest_Bearing_Share,
                MAX(CASE WHEN m.metric_code = 'L6' THEN f.metric_value END) AS L6_Loan_to_Deposit_Ratio,
                MAX(CASE WHEN m.metric_code = 'F1' THEN f.metric_value END) AS F1_Borrowings_to_Assets,
                MAX(CASE WHEN m.metric_code = 'F1a' THEN f.metric_value END) AS F1a_ST_Borrowings_to_Assets,
                MAX(CASE WHEN m.metric_code = 'F1b' THEN f.metric_value END) AS F1b_FHLB_Advances_to_Assets,
                MAX(CASE WHEN m.metric_code = 'S1' THEN f.metric_value END) AS S1_HTM_Concentration,
                MAX(CASE WHEN m.metric_code = 'S2' THEN f.metric_value END) AS S2_HTM_Loss_to_Assets,
                MAX(CASE WHEN m.metric_code = 'S3' THEN f.metric_value END) AS S3_HTM_Fair_Value_Decline,
                MAX(CASE WHEN m.metric_code = 'S4' THEN f.metric_value END) AS S4_Total_Securities_Share,
                MAX(CASE WHEN m.metric_code = 'S5' THEN f.metric_value END) AS S5_AFS_Unrealized_Gain_Loss,
                MAX(CASE WHEN m.metric_code = 'K2' THEN f.metric_value END) AS K2_CI_Share,
                MAX(CASE WHEN m.metric_code = 'K3' THEN f.metric_value END) AS K3_CRE_Share,
                MAX(CASE WHEN m.metric_code = 'K4' THEN f.metric_value END) AS K4_Loan_HHI,
                MAX(CASE WHEN m.metric_code = 'P1' THEN f.metric_value END) AS P1_ROA_Annualized,
                MAX(CASE WHEN m.metric_code = 'P2' THEN f.metric_value END) AS P2_ROE_Annualized,
                MAX(CASE WHEN m.metric_code = 'P3' THEN f.metric_value END) AS P3_NII_Growth_YoY,
                MAX(CASE WHEN m.metric_code = 'P4' THEN f.metric_value END) AS P4_NII_to_Assets,
                MAX(CASE WHEN m.metric_code = 'M1' THEN f.metric_value END) AS M1_Stock_Drawdown,
                MAX(CASE WHEN m.metric_code = 'M2' THEN f.metric_value END) AS M2_Stock_Volatility_60d,
                MAX(CASE WHEN m.metric_code = 'M3' THEN f.metric_value END) AS M3_Fed_Rate_Change_YoY,
                MAX(CASE WHEN m.metric_code = 'EWS_SCORE' THEN f.metric_value END) AS EWS_Composite_Score
            FROM fact_risk_metrics f
            JOIN dim_bank b ON f.idrssd = b.idrssd
            JOIN dim_quarter q ON f.quarter_id = q.quarter_id
            JOIN dim_risk_metric m ON f.metric_id = m.metric_id
            GROUP BY b.bank_id, b.bank_name, b.tier, b.tier_label, q.quarter_id, q.year, q.quarter_num, q.era;
        """)

        # View 4: vw_powerbi_market_daily
        cursor.execute("DROP VIEW IF EXISTS vw_powerbi_market_daily")
        cursor.execute("""
            CREATE VIEW vw_powerbi_market_daily AS
            SELECT 
                b.bank_id,
                b.bank_name,
                b.ticker,
                b.tier,
                b.tier_label,
                m.date,
                m.open_price,
                m.high_price,
                m.low_price,
                m.close_price,
                m.volume,
                r.fed_funds_rate
            FROM fact_daily_market m
            JOIN dim_bank b ON m.idrssd = b.idrssd
            LEFT JOIN dim_macro_fed_rates r ON m.date = r.date;
        """)

        self.connection.commit()
        print("[SUCCESS] All 4 Power BI Analytical SQL Views created successfully in MySQL!")

    def run(self):
        """Executes the full risk calculation and loading pipeline."""
        df_base, df_mkt, df_fed, df_banks = self.load_processed_data()
        df_calculated = self.calculate_metrics(df_base, df_mkt, df_fed, df_banks)
        df_wide, df_long = self.export_csvs(df_calculated)

        self.connect_db()
        if self.connection:
            try:
                self.load_to_mysql(df_wide, df_long)
            finally:
                if self.connection.is_connected():
                    self.connection.close()
                    print("[INFO] MySQL connection closed.")

        print("\n==============================================================")
        print("[SUCCESS] Quantitative Risk Analytics Engine execution complete!")
        print("==============================================================")

if __name__ == "__main__":
    calculator = RiskMetricsCalculator()
    calculator.run()
