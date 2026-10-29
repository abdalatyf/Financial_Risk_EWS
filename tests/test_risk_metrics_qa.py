"""
Financial Risk EWS - Automated QA Test Suite for Analytics & Risk Metrics
Uses standard library `unittest`.

Tests:
  TC-AN-01: Dimension Completeness (`dim_risk_metric` contains 34 official metrics)
  TC-AN-02: Fact Table Cardinality (40,460 records across 1,190 bank-quarters x 34 metrics)
  TC-AN-03: Analytical Wide CSV Cardinality & Schema (1,190 rows x 45 columns)
  TC-AN-04: MySQL Analytical Views Row Count Integrity:
            - `vw_powerbi_executive_summary`: 1,190
            - `vw_powerbi_bank_risk_wide`: 1,190
            - `vw_powerbi_loan_concentration`: 19,040 (strictly 1:1 with fact_loan_balances)
            - `vw_powerbi_market_daily`: 74,525
  TC-AN-05: SVB Q4-2022 Ground Truth Forensic Benchmarks (LFR, C6, S1, L1, Alert RED)
  TC-AN-06: Composite EWS Score Bounds & Alert Categorization ([0, 100] scale)
  TC-AN-07: Loan Concentration View Integrity (Zero Cartesian Inflation)
  TC-AN-08: Historical Early Warning Lead Time (SVB flagged RED well before collapse)
"""

import os
import unittest
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
load_dotenv(os.path.join(BASE_DIR, ".env"))

class TestRiskMetricsAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wide_path = os.path.join(PROCESSED_DIR, "fact_quarterly_risk_wide.csv")
        cls.long_path = os.path.join(PROCESSED_DIR, "fact_quarterly_risk_long.csv")
        cls.df_wide = pd.read_csv(cls.wide_path)
        cls.df_long = pd.read_csv(cls.long_path)

        cls.conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "Financial_Risk_EWS_db")
        )

    @classmethod
    def tearDownClass(cls):
        if cls.conn and cls.conn.is_connected():
            cls.conn.close()

    def test_01_dim_risk_metric_completeness(self):
        """TC-AN-01: Verify dim_risk_metric contains all 34 Hazem blueprint metrics."""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT metric_code, metric_name, category, is_core, risk_direction FROM dim_risk_metric")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 34, f"Expected 34 metrics in dim_risk_metric, found {len(rows)}")
        
        codes = {r["metric_code"] for r in rows}
        expected_sample = {"C1", "C6", "L1", "L3", "S1", "F1", "K3", "K4", "P1", "M1", "EWS_SCORE"}
        self.assertTrue(expected_sample.issubset(codes), f"Missing core metric codes: {expected_sample - codes}")

    def test_02_fact_risk_metrics_cardinality(self):
        """TC-AN-02: Verify 40,460 rows in fact_quarterly_risk_long.csv and MySQL fact_risk_metrics."""
        self.assertEqual(len(self.df_long), 40460, f"Expected 40,460 rows in long CSV, got {len(self.df_long)}")
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fact_risk_metrics")
        db_cnt = cursor.fetchone()[0]
        self.assertEqual(db_cnt, 40460, f"Expected 40,460 rows in MySQL fact_risk_metrics, got {db_cnt}")

    def test_03_wide_dataset_cardinality_and_columns(self):
        """TC-AN-03: Verify wide CSV has 1,190 bank-quarters, 45 columns, and required identifiers."""
        self.assertEqual(len(self.df_wide), 1190, f"Expected 1,190 bank-quarters, got {len(self.df_wide)}")
        self.assertEqual(len(self.df_wide.columns), 45, f"Expected 45 columns, got {len(self.df_wide.columns)}")
        required_cols = [
            "Date", "quarter_id", "Bank_ID", "IDRSSD",
            "C1", "C6", "L1", "L3", "S1", "F1", "K3", "K4", "P1", "M1",
            "EWS_SCORE", "Alert_Level", "L3_Score", "C6_Score", "S1_Score"
        ]
        for col in required_cols:
            self.assertIn(col, self.df_wide.columns, f"Missing required column in wide dataset: {col}")

    def test_04_analytical_views_row_counts(self):
        """TC-AN-04: Verify all 4 Power BI analytical views have expected row counts."""
        cursor = self.conn.cursor()
        expected_counts = {
            "vw_powerbi_executive_summary": 1190,
            "vw_powerbi_bank_risk_wide": 1190,
            "vw_powerbi_loan_concentration": 19040,
            "vw_powerbi_market_daily": 74525
        }
        for view, expected in expected_counts.items():
            cursor.execute(f"SELECT COUNT(*) FROM {view}")
            actual = cursor.fetchone()[0]
            self.assertEqual(actual, expected, f"View {view} row count mismatch: expected {expected}, got {actual}")

    def test_05_svb_q4_2022_metrics_benchmarks(self):
        """TC-AN-05: Verify SVB Q4-2022 forensic metrics match empirical crisis benchmarks."""
        svb_q4 = self.df_wide[(self.df_wide["Bank_ID"] == "SVB") & (self.df_wide["quarter_id"] == "2022-Q4")]
        self.assertEqual(len(svb_q4), 1, "SVB Q4-2022 record not found")
        row = svb_q4.iloc[0]

        # Liquidity Fragility Ratio ~ 4.30
        self.assertTrue(4.0 <= row["L3"] <= 4.6, f"SVB LFR out of expected range: {row['L3']}")
        # Adjusted Tier 1 Capital after HTM Loss ~ 1.65%
        self.assertTrue(0.01 <= row["C6"] <= 0.025, f"SVB C6 out of expected range: {row['C6']}")
        # HTM Concentration ~ 43.69%
        self.assertTrue(0.42 <= row["S1"] <= 0.45, f"SVB S1 out of expected range: {row['S1']}")
        # Consolidated Uninsured Ratio ~ 94.36%
        self.assertTrue(0.93 <= row["L1"] <= 0.96, f"SVB L1 out of expected range: {row['L1']}")
        # EWS Composite Score >= 80.0 & Alert RED
        self.assertGreaterEqual(row["EWS_SCORE"], 80.0, f"SVB EWS score should be critical: {row['EWS_SCORE']}")
        self.assertEqual(row["Alert_Level"], "RED", f"SVB alert should be RED: {row['Alert_Level']}")

    def test_06_composite_score_bounds(self):
        """TC-AN-06: Verify all EWS scores are bounded within [0, 100] and alert labels are valid."""
        valid_scores = self.df_wide["EWS_SCORE"].dropna()
        self.assertTrue((valid_scores >= 0.0).all(), "Found negative EWS scores")
        self.assertTrue((valid_scores <= 100.0).all(), "Found EWS scores exceeding 100.0")
        
        valid_alerts = set(self.df_wide["Alert_Level"].unique())
        self.assertTrue(valid_alerts.issubset({"GREEN", "YELLOW", "AMBER", "RED"}), f"Invalid alert levels: {valid_alerts}")

    def test_07_loan_concentration_view_integrity(self):
        """TC-AN-07: Verify loan sum in view matches fact table exactly (no cartesian duplication)."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(loan_amount) FROM fact_loan_balances")
        fact_sum = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(loan_amount) FROM vw_powerbi_loan_concentration")
        view_sum = cursor.fetchone()[0]

        self.assertAlmostEqual(float(fact_sum), float(view_sum), places=2,
            msg=f"Loan sum discrepancy in view! fact_sum={fact_sum}, view_sum={view_sum}")

    def test_08_historical_early_warning_lead_time(self):
        """TC-AN-08: Verify model flags SVB as RED by Q3 2022 (2 quarters ahead of collapse)."""
        svb_q3_2022 = self.df_wide[(self.df_wide["Bank_ID"] == "SVB") & (self.df_wide["quarter_id"] == "2022-Q3")].iloc[0]
        self.assertEqual(svb_q3_2022["Alert_Level"], "RED",
            f"EWS failed early warning criterion: SVB in 2022-Q3 was {svb_q3_2022['Alert_Level']}")

    def test_09_general_systemic_crisis_tier_separation(self):
        """TC-AN-09: Verify Q4-2022 tier separation: 4 Casualties RED, 5 Survivors AMBER, Mega G-SIBs Safe/Watchlist (<60)."""
        q4 = self.df_wide[self.df_wide["quarter_id"] == "2022-Q4"].set_index("Bank_ID")
        
        # 1. All 4 Crisis Casualties (Tier 1) MUST be RED (Score >= 80)
        casualties = ["SVB", "SBNY", "FRC", "SI"]
        for b in casualties:
            score = q4.loc[b, "EWS_SCORE"]
            alert = q4.loc[b, "Alert_Level"]
            self.assertEqual(alert, "RED", f"Casualty {b} must be RED in Q4-2022 (got {alert}, score={score})")
            self.assertGreaterEqual(score, 80.0, f"Casualty {b} score must be >= 80.0 (got {score})")

        # 2. All 5 High-Stress Survivors (Tier 2) MUST be AMBER (60 <= Score < 80)
        survivors = ["WAL", "PACW", "CMA", "ZION", "NYCB"]
        for b in survivors:
            score = q4.loc[b, "EWS_SCORE"]
            alert = q4.loc[b, "Alert_Level"]
            self.assertEqual(alert, "AMBER", f"Survivor {b} must be AMBER in Q4-2022 (got {alert}, score={score})")
            self.assertTrue(60.0 <= score < 80.0, f"Survivor {b} score must be in [60, 80) (got {score})")

        # 3. All 5 Mega G-SIBs (Tier 4) MUST be Safe/Watchlist GREEN or YELLOW (Score < 60)
        gsibs = ["JPM", "BAC", "WFC", "PNC", "USB"]
        for b in gsibs:
            score = q4.loc[b, "EWS_SCORE"]
            alert = q4.loc[b, "Alert_Level"]
            self.assertIn(alert, ["GREEN", "YELLOW"], f"G-SIB {b} must be GREEN or YELLOW in Q4-2022 (got {alert}, score={score})")
            self.assertLess(score, 60.0, f"G-SIB {b} score must be < 60.0 (got {score})")

if __name__ == "__main__":
    unittest.main()
