"""
Financial Risk EWS - Analytics Verification Script
Tests and prints all database views, row counts, and SVB benchmark metrics.
"""
import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def main():
    print("=" * 70)
    print("FINANCIAL RISK EWS - ANALYTICS VERIFICATION")
    print("=" * 70)

    # 1. Check CSV files
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    wide_path = os.path.join(processed_dir, "fact_quarterly_risk_wide.csv")
    long_path = os.path.join(processed_dir, "fact_quarterly_risk_long.csv")

    df_wide = pd.read_csv(wide_path)
    df_long = pd.read_csv(long_path)
    print(f"[CSV CHECK] Wide Dataset: {len(df_wide)} rows, {len(df_wide.columns)} columns")
    print(f"[CSV CHECK] Long Dataset: {len(df_long)} rows, {len(df_long.columns)} columns")

    # 2. Check MySQL Database
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "Financial_Risk_EWS_db")
    )
    cursor = conn.cursor(dictionary=True)

    tables = ["dim_risk_metric", "fact_risk_metrics"]
    views = [
        "vw_powerbi_executive_summary",
        "vw_powerbi_bank_risk_wide",
        "vw_powerbi_loan_concentration",
        "vw_powerbi_market_daily"
    ]

    print("\n--- Relational Tables Row Counts ---")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM {t}")
        cnt = cursor.fetchone()["cnt"]
        print(f"  {t:<25}: {cnt:>8} rows")

    print("\n--- Analytical Views Row Counts ---")
    for v in views:
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM {v}")
        cnt = cursor.fetchone()["cnt"]
        print(f"  {v:<32}: {cnt:>8} rows")

    # 3. SVB Q4-2022 Ground Truth Benchmark Verification
    print("\n--- SVB (Silicon Valley Bank) 2022 Quarterly Timeline ---")
    cursor.execute("""
        SELECT 
            quarter_id,
            ews_score,
            alert_level,
            liquidity_fragility_ratio,
            tier1_after_htm_loss,
            htm_concentration_ratio,
            uninsured_deposit_ratio,
            borrowings_to_assets,
            cre_share
        FROM vw_powerbi_executive_summary
        WHERE bank_id = 'SVB' AND year = 2022
        ORDER BY quarter_id;
    """)
    svb_rows = cursor.fetchall()
    for r in svb_rows:
        print(f"  Quarter: {r['quarter_id']} | Score: {r['ews_score']:>5.1f} | Alert: {r['alert_level']:<5} | "
              f"LFR: {r['liquidity_fragility_ratio']:>4.2f} | C6: {r['tier1_after_htm_loss']*100:>5.2f}% | "
              f"S1: {r['htm_concentration_ratio']*100:>5.2f}% | L1: {r['uninsured_deposit_ratio']*100:>5.2f}% | "
              f"F1: {r['borrowings_to_assets']*100:>5.2f}%")

    # 4. Compare Casualties vs G-SIBs in Q4-2022
    print("\n--- Cross-Tier Benchmark in Q4-2022 (Crisis Casualties vs Mega G-SIBs) ---")
    cursor.execute("""
        SELECT 
            tier_label,
            bank_id,
            ews_score,
            alert_level,
            liquidity_fragility_ratio,
            tier1_after_htm_loss,
            htm_concentration_ratio,
            uninsured_deposit_ratio
        FROM vw_powerbi_executive_summary
        WHERE quarter_id = '2022-Q4' AND tier IN (1, 4)
        ORDER BY tier, ews_score DESC;
    """)
    tier_rows = cursor.fetchall()
    for r in tier_rows:
        print(f"  [{r['tier_label']:<16}] {r['bank_id']:<4} | Score: {r['ews_score']:>5.1f} | Alert: {r['alert_level']:<5} | "
              f"LFR: {r['liquidity_fragility_ratio']:>4.2f} | C6: {r['tier1_after_htm_loss']*100:>5.2f}% | "
              f"S1: {r['htm_concentration_ratio']*100:>5.2f}% | L1: {r['uninsured_deposit_ratio']*100:>5.2f}%")

    conn.close()
    print("\n" + "=" * 70)
    print("[SUCCESS] All checks completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
