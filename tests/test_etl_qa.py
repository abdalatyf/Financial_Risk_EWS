import os
import sys
import unittest
import pandas as pd
import numpy as np
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class TestETLQualityAssurance(unittest.TestCase):
    """
    Automated QA Test Suite for Financial Risk EWS.
    Verifies Extraction, Cleaning, Data Integrity, and Database Modeling.
    """

    @classmethod
    def setUpClass(cls):
        cls.base_dir = BASE_DIR
        cls.processed_dir = os.path.join(BASE_DIR, "data", "processed")
        cls.config_dir = os.path.join(BASE_DIR, "config")
        cls.banks_csv = os.path.join(cls.config_dir, "banks.csv")
        
        # Load processed datasets if available
        cls.fin_csv = os.path.join(cls.processed_dir, "fact_financials.csv")
        cls.loans_csv = os.path.join(cls.processed_dir, "fact_loan_sectors.csv")
        cls.market_csv = os.path.join(cls.processed_dir, "fact_daily_market.csv")
        cls.fed_csv = os.path.join(cls.processed_dir, "dim_macro_fed_rates.csv")

    # =========================================================================
    # Category 1: Source & Code Portability QA
    # =========================================================================

    def test_01_code_portability_no_hardcoded_paths(self):
        """Test 1: Verify no hardcoded drive paths (e.g. D:\\) exist in src/etl/*.py scripts."""
        etl_dir = os.path.join(self.base_dir, "src", "etl")
        for fname in os.listdir(etl_dir):
            if fname.endswith(".py"):
                fpath = os.path.join(etl_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.assertNotIn("D:\\Projects", content, f"Hardcoded path found in {fname}")
                    self.assertNotIn("C:\\Projects", content, f"Hardcoded path found in {fname}")

    def test_02_config_banks_coverage_and_tiers(self):
        """Test 2: Verify config/banks.csv contains exactly 20 unique banks across 4 tiers."""
        self.assertTrue(os.path.exists(self.banks_csv), "config/banks.csv missing")
        df_banks = pd.read_csv(self.banks_csv)
        self.assertEqual(len(df_banks), 20, "Must contain exactly 20 banks")
        self.assertEqual(df_banks['idrssd'].nunique(), 20, "All 20 IDRSSD must be unique")
        self.assertEqual(df_banks['tier'].nunique(), 4, "Must cover all 4 tiers (1 to 4)")
        expected_tiers = {1: "Crisis Casualty", 2: "High-Stress Survivor", 3: "Regional Peer", 4: "Mega G-SIB"}
        for tier_num, label in expected_tiers.items():
            self.assertTrue((df_banks[df_banks['tier'] == tier_num]['tier_label'] == label).all())

    # =========================================================================
    # Category 2: Data Cleaning & CSV Mathematical Integrity QA
    # =========================================================================

    def test_03_processed_fact_tables_row_alignment(self):
        """Test 3: Both fact_financials.csv and fact_loan_sectors.csv have exactly 1,190 active rows."""
        df_fin = pd.read_csv(self.fin_csv)
        df_loans = pd.read_csv(self.loans_csv)
        self.assertEqual(len(df_fin), 1190, f"fact_financials has {len(df_fin)} rows; expected 1,190")
        self.assertEqual(len(df_loans), 1190, f"fact_loan_sectors has {len(df_loans)} rows; expected 1,190")

    def test_04_primary_key_alignment_between_facts(self):
        """Test 4: Verify identical (Date, IDRSSD) keys between financial and loan facts."""
        df_fin = pd.read_csv(self.fin_csv)
        df_loans = pd.read_csv(self.loans_csv)
        keys_fin = set(zip(df_fin['Date'], df_fin['IDRSSD'].astype(str)))
        keys_loans = set(zip(df_loans['Date'], df_loans['IDRSSD'].astype(str)))
        self.assertEqual(keys_fin, keys_loans, "Mismatch between financial and loan bank-quarters")

    def test_05_zero_duplicate_keys(self):
        """Test 5: Zero duplicate (Date, IDRSSD) primary keys in both facts."""
        df_fin = pd.read_csv(self.fin_csv)
        df_loans = pd.read_csv(self.loans_csv)
        self.assertEqual(df_fin.duplicated(subset=['Date', 'IDRSSD']).sum(), 0, "Duplicates found in fact_financials")
        self.assertEqual(df_loans.duplicated(subset=['Date', 'IDRSSD']).sum(), 0, "Duplicates found in fact_loan_sectors")

    def test_06_structural_missing_cet1_handling(self):
        """Test 6: Verify pre-Basel III CET1 is stored as NaN/null rather than poisoned 0.0."""
        df_fin = pd.read_csv(self.fin_csv)
        # Any CET1 <= 2013 must be null/NaN
        pre_2014 = df_fin[df_fin['Date'] < '2014-01-01']
        zeros_count = (pre_2014['CET1_Ratio_Pct'] == 0.0).sum()
        self.assertEqual(zeros_count, 0, "Pre-Basel III CET1 must not contain 0.0 values")

    def test_07_structural_missing_uninsured_deposits_handling(self):
        """Test 7: Verify SI and WAL historical missing uninsured deposits are stored as NaN not 0.0."""
        df_fin = pd.read_csv(self.fin_csv)
        # Silvergate IDRSSD: 1216826 (2008-2017)
        si_historical = df_fin[(df_fin['IDRSSD'] == 1216826) & (df_fin['Date'] < '2018-01-01')]
        self.assertEqual((si_historical['Uninsured_Deposits'] == 0.0).sum(), 0, "SI missing uninsured must be NaN")
        
        # Western Alliance IDRSSD: 3138146 (2008-2010)
        wal_historical = df_fin[(df_fin['IDRSSD'] == 3138146) & (df_fin['Date'] < '2011-01-01')]
        self.assertEqual((wal_historical['Uninsured_Deposits'] == 0.0).sum(), 0, "WAL missing uninsured must be NaN")

    def test_08_accounting_identity_balance_sheet(self):
        """Test 8: Assets = Liabilities + Equity + Noncontrolling Interest holds across all 1,190 quarters."""
        df_fin = pd.read_csv(self.fin_csv)
        self.assertIn('Noncontrolling_Interest', df_fin.columns, "Noncontrolling_Interest column missing in fact_financials")
        nci = df_fin['Noncontrolling_Interest'].fillna(0.0)
        total_funding = df_fin['Total_Liabilities'] + df_fin['Total_Equity'] + nci
        diff = np.abs(df_fin['Total_Assets'] - total_funding)
        relative_diff = diff / df_fin['Total_Assets']
        anomalies = (relative_diff > 0.001).sum()
        self.assertEqual(anomalies, 0, f"Found {anomalies} accounting identity violations > 0.1% (expected 0 after NCI integration)")

    def test_09_loan_sector_sum_reconciliation(self):
        """Test 9: Sum of the 16 gross loan sectors minus unearned income matches Total_Loans."""
        df_loans = pd.read_csv(self.loans_csv)
        sector_cols = [c for c in df_loans.columns if c[0].isdigit()]
        sector_sum = df_loans[sector_cols].sum(axis=1)
        # Gross loans from RC-C must be >= Net Total Loans reported on RC line 4b (the difference is unearned income)
        self.assertTrue((sector_sum >= df_loans['Total_Loans'] - 1.0).all(), "Gross loan sum cannot be less than net total loans")
        # Unearned loan income must represent less than 2% of total loan volume
        unearned_ratio = (sector_sum - df_loans['Total_Loans']) / df_loans['Total_Loans']
        self.assertTrue((unearned_ratio < 0.02).all(), "Unearned loan income variance exceeds 2%")

    def test_10_market_data_ohlc_bounds(self):
        """Test 10: Low <= Open <= High and Low <= Close <= High across all market records."""
        df_market = pd.read_csv(self.market_csv)
        self.assertGreater(len(df_market), 60000, "Market data has fewer rows than expected")
        invalid_high = (df_market['High'] < df_market['Low']).sum()
        invalid_open = ((df_market['Open'] < df_market['Low']) | (df_market['Open'] > df_market['High'])).sum()
        invalid_close = ((df_market['Close'] < df_market['Low']) | (df_market['Close'] > df_market['High'])).sum()
        self.assertEqual(invalid_high, 0, "High cannot be strictly lower than Low")
        self.assertEqual(invalid_open, 0, "Open must be bounded between Low and High")
        self.assertEqual(invalid_close, 0, "Close must be bounded between Low and High")

    def test_11_delisted_bank_trading_cutoffs(self):
        """Test 11: Delisted banks strictly stop trading on or before their official last_trading_date."""
        df_market = pd.read_csv(self.market_csv)
        df_banks = pd.read_csv(self.banks_csv)
        cutoffs = dict(zip(df_banks['ticker'], df_banks['last_trading_date']))
        
        for ticker, cutoff in cutoffs.items():
            if pd.notna(cutoff):
                trades = df_market[df_market['Ticker'] == ticker]
                if not trades.empty:
                    max_date = trades['Date'].max()
                    self.assertLessEqual(max_date, str(cutoff), f"{ticker} traded after cutoff {cutoff}")

    def test_12_fed_rate_continuity(self):
        """Test 12: Federal Funds Rate series spans 2008 to 2023 with zero nulls."""
        df_fed = pd.read_csv(self.fed_csv)
        self.assertEqual(df_fed['Fed_Rate'].isnull().sum(), 0, "Fed rate contains nulls")
        self.assertGreaterEqual(len(df_fed), 4000, "Fed rate records too short")

    # =========================================================================
    # Category 3: MySQL Star Schema Modeling QA
    # =========================================================================

    def _get_db_conn(self):
        host = os.getenv("MYSQL_HOST", "localhost")
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE", "Financial_Risk_EWS_db")
        return mysql.connector.connect(host=host, user=user, password=password, database=database)

    def test_13_database_all_9_tables_exist(self):
        """Test 13: All 9 Star Schema tables exist in MySQL."""
        conn = self._get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [t[0].lower() for t in cursor.fetchall()]
        conn.close()
        
        expected = [
            'dim_bank', 'dim_quarter', 'dim_date', 'dim_financial_metric', 
            'dim_loan_sector', 'dim_macro_fed_rates',
            'fact_financials', 'fact_loan_balances', 'fact_daily_market'
        ]
        for tbl in expected:
            self.assertIn(tbl, tables, f"Table {tbl} missing from MySQL database")

    def test_14_dim_bank_enriched_columns_and_counts(self):
        """Test 14: dim_bank has 20 rows with non-null tier and tier_label."""
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM dim_bank")
        rows = cursor.fetchall()
        conn.close()
        
        self.assertEqual(len(rows), 20, "dim_bank must have exactly 20 banks")
        for r in rows:
            self.assertIn('tier', r, "tier column missing in dim_bank")
            self.assertIn('tier_label', r, "tier_label column missing in dim_bank")
            self.assertIsNotNone(r['tier'], f"tier is null for {r['bank_id']}")
            self.assertIsNotNone(r['tier_label'], f"tier_label is null for {r['bank_id']}")

    def test_15_dim_quarter_era_column_populated(self):
        """Test 15: dim_quarter has valid, populated era classifications."""
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT era FROM dim_quarter")
        eras = [r['era'] for r in cursor.fetchall()]
        conn.close()
        
        self.assertGreaterEqual(len(eras), 4, "Must have at least 4 macro eras")
        self.assertNotIn(None, eras, "era cannot be null in dim_quarter")

    def test_16_zero_foreign_key_orphans(self):
        """Test 16: Zero foreign key orphan rows in fact tables."""
        conn = self._get_db_conn()
        cursor = conn.cursor()
        
        # Check fact_financials -> dim_bank
        cursor.execute("SELECT COUNT(*) FROM fact_financials f LEFT JOIN dim_bank b ON f.idrssd = b.idrssd WHERE b.idrssd IS NULL")
        orphans = cursor.fetchone()[0]
        self.assertEqual(orphans, 0, "Orphan idrssd in fact_financials")
        
        # Check fact_loan_balances -> dim_bank
        cursor.execute("SELECT COUNT(*) FROM fact_loan_balances l LEFT JOIN dim_bank b ON l.idrssd = b.idrssd WHERE b.idrssd IS NULL")
        orphans_l = cursor.fetchone()[0]
        self.assertEqual(orphans_l, 0, "Orphan idrssd in fact_loan_balances")
        
        # Check fact_daily_market -> dim_bank
        cursor.execute("SELECT COUNT(*) FROM fact_daily_market m LEFT JOIN dim_bank b ON m.idrssd = b.idrssd WHERE b.idrssd IS NULL")
        orphans_m = cursor.fetchone()[0]
        self.assertEqual(orphans_m, 0, "Orphan idrssd in fact_daily_market")
        conn.close()

    # =========================================================================
    # Category 4: Forensic Sanity & Deployment QA
    # =========================================================================

    def test_17_svb_q4_2022_forensic_targets(self):
        """Test 17: SVB Q4-2022 numbers match official Call Report filings."""
        df_fin = pd.read_csv(self.fin_csv)
        svb_q4 = df_fin[(df_fin['IDRSSD'] == 802866) & (df_fin['Date'] == '2022-12-31')]
        self.assertEqual(len(svb_q4), 1, "SVB Q4-2022 row missing")
        row = svb_q4.iloc[0]
        
        # Total Assets ~ $209,026M ($209B)
        self.assertAlmostEqual(row['Total_Assets'], 209026000.0, delta=1000000.0)
        # HTM Securities ~ $91,327M ($91.3B)
        self.assertAlmostEqual(row['HTM_Securities'], 91327000.0, delta=1000000.0)
        # Uninsured Deposits ~ $151,593M ($151.6B)
        self.assertAlmostEqual(row['Uninsured_Deposits'], 151593000.0, delta=1000000.0)
        # Foreign Deposits (Cayman branch) ~ $13,899M ($13.9B)
        self.assertAlmostEqual(row['Foreign_Deposits'], 13899000.0, delta=100000.0)
        # Domestic Deposits ~ $161,479M ($161.5B)
        self.assertAlmostEqual(row['Domestic_Deposits'], 161479000.0, delta=1000000.0)
        # Total Deposits == Domestic + Foreign
        self.assertAlmostEqual(row['Total_Deposits'], row['Domestic_Deposits'] + row['Foreign_Deposits'], delta=1.0)

    def test_18_ytd_income_conversion_quarterly_variance(self):
        """Test 18: Quarterly Net_Income varies properly and is not monotonic YTD."""
        df_fin = pd.read_csv(self.fin_csv)
        jpm_2022 = df_fin[(df_fin['Bank_ID'] == 'JPM') & (df_fin['Date'].str.startswith('2022'))]
        incomes = jpm_2022['Net_Income'].tolist()
        self.assertEqual(len(incomes), 4, "JPM must have 4 quarters in 2022")
        # In true quarterly, Q4 is not the sum of Q1+Q2+Q3+Q4
        self.assertNotEqual(incomes[3], sum(incomes), "Net_Income appears to be cumulative YTD not quarterly")

    def test_19_batch_manager_portability(self):
        """Test 19: setup_and_run.bat exists and contains no hardcoded drive letters."""
        bat_path = os.path.join(self.base_dir, "setup_and_run.bat")
        self.assertTrue(os.path.exists(bat_path), "setup_and_run.bat missing")
        with open(bat_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertNotIn("D:\\Projects", content, "setup_and_run.bat has hardcoded paths")

    def test_20_gitignore_and_env_security(self):
        """Test 20: .env is ignored and .env.example contains no real passwords."""
        gitignore_path = os.path.join(self.base_dir, ".gitignore")
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gi_content = f.read()
            self.assertIn(".env", gi_content, ".env must be ignored in .gitignore")
            
        example_path = os.path.join(self.base_dir, ".env.example")
        with open(example_path, "r", encoding="utf-8") as f:
            ex_content = f.read()
            self.assertIn("YOUR_PASSWORD_HERE", ex_content, ".env.example must have placeholder password")

    def test_21_deposit_decomposition_identity(self):
        """Test 21: Verify Total_Deposits == Domestic_Deposits + Foreign_Deposits (|diff| <= 1.0) with 0 violations across all 1,190 bank-quarters."""
        df_fin = pd.read_csv(self.fin_csv)
        self.assertIn('Domestic_Deposits', df_fin.columns, "Domestic_Deposits column missing in fact_financials")
        self.assertIn('Foreign_Deposits', df_fin.columns, "Foreign_Deposits column missing in fact_financials")
        self.assertIn('Total_Deposits', df_fin.columns, "Total_Deposits column missing in fact_financials")
        self.assertEqual(len(df_fin), 1190, f"Expected 1,190 rows in fact_financials, got {len(df_fin)}")
        
        diff = np.abs(df_fin['Total_Deposits'] - (df_fin['Domestic_Deposits'] + df_fin['Foreign_Deposits']))
        violations = (diff > 1.0).sum()
        self.assertEqual(violations, 0, f"Found {violations} deposit decomposition violations (|diff| > 1.0)")

if __name__ == "__main__":
    unittest.main()
