import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

class RiskMetricsCalculator:
    def __init__(self):
        # Dynamically find project root and load .env
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        load_dotenv(os.path.join(BASE_DIR, ".env"))
        
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("MYSQL_DATABASE", "Financial_Risk_EWS_db")
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host, user=self.user, password=self.password, database=self.database
        )
        print(f"[SUCCESS] Connected to {self.database}")

    def fetch_base_data(self):
        """Pulls the fact table and pivots it so Python can do math easily."""
        print("[INFO] Fetching base financial data from MySQL...")
        query = """
            SELECT f.quarter_id, f.idrssd, m.metric_name, f.metric_value
            FROM fact_financials f
            JOIN dim_financial_metric m ON f.metric_id = m.metric_id
        """
        df = pd.read_sql(query, self.connection)
        
        # Pivot from LONG to WIDE format
        # This turns metric names into columns so we can do easy math: df['Metric_A'] / df['Metric_B']
        df_wide = df.pivot(index=['quarter_id', 'idrssd'], columns='metric_name', values='metric_value').reset_index()
        return df_wide

    def calculate_custom_metrics(self, df):
        """
        FINANCE TEAM: Add your complex formulas here!
        """
        print("[INFO] Calculating complex risk metrics in Python...")
        
        # 1. Uninsured Deposit Ratio (Liability Flight Risk)
        df['Uninsured_Deposit_Ratio'] = df['Uninsured_Deposits'] / df['Total_Deposits']
        
        # 2. HTM Concentration Risk (Asset Duration Risk)
        df['HTM_Concentration_Ratio'] = df['HTM_Securities'] / df['Total_Assets']
        
        # 3. Unrealized HTM Losses (The Silent Killer)
        df['Unrealized_HTM_Losses'] = df['HTM_Securities'] - df['HTM_Fair_Value']
        
        # 4. Liquidity Fragility Ratio (Can they survive a run?)
        # Formula: Uninsured Deposits / Highly Liquid Assets (Cash + AFS)
        liquid_assets = df['Cash_Balances'] + df['AFS_Amortized_Cost']
        df['Liquidity_Fragility_Ratio'] = df['Uninsured_Deposits'] / liquid_assets
        
        # 5. Adjusted Tier 1 Capital (True Solvency)
        df['Adjusted_Tier1_Capital'] = df['Tier1_Capital'] - df['Unrealized_HTM_Losses']

        # Isolate ONLY the new calculated columns to push back to the DB
        new_metrics = [
            'Uninsured_Deposit_Ratio', 'HTM_Concentration_Ratio', 
            'Unrealized_HTM_Losses', 'Liquidity_Fragility_Ratio', 'Adjusted_Tier1_Capital'
        ]
        
        # Melt back to LONG format
        df_new_long = df.melt(
            id_vars=['quarter_id', 'idrssd'], 
            value_vars=new_metrics, 
            var_name='metric_name', 
            value_name='metric_value'
        )
        
        # Drop any nulls (e.g., division by zero)
        df_new_long = df_new_long.dropna(subset=['metric_value'])
        return df_new_long

    def push_to_database(self, df_long):
        print("[INFO] Registering new metrics and pushing to MySQL...")
        cursor = self.connection.cursor()
        
        # 1. Register new metrics in dim_financial_metric and get their IDs
        unique_metrics = df_long['metric_name'].unique()
        metric_id_map = {}
        
        for metric in unique_metrics:
            # Insert if it doesn't exist
            cursor.execute("INSERT IGNORE INTO dim_financial_metric (metric_name, statement_type) VALUES (%s, %s)", 
                           (metric, 'Calculated Risk Metric'))
            # Fetch the ID
            cursor.execute("SELECT metric_id FROM dim_financial_metric WHERE metric_name=%s", (metric,))
            metric_id_map[metric] = cursor.fetchone()[0]

        # 2. Map the ID back to the dataframe
        df_long['metric_id'] = df_long['metric_name'].map(metric_id_map)

        # 3. Insert into fact_financials
        insert_data = []
        for _, row in df_long.iterrows():
            insert_data.append((
                row['quarter_id'], 
                int(row['idrssd']), 
                int(row['metric_id']), 
                float(row['metric_value'])
            ))
            
        cursor.executemany("""
            INSERT IGNORE INTO fact_financials (quarter_id, idrssd, metric_id, metric_value) 
            VALUES (%s, %s, %s, %s)
        """, insert_data)
        
        self.connection.commit()
        print(f"[SUCCESS] {len(insert_data)} complex calculated metrics inserted into fact_financials!")

    def run(self):
        try:
            self.connect()
            df_wide = self.fetch_base_data()
            df_new_metrics = self.calculate_custom_metrics(df_wide)
            self.push_to_database(df_new_metrics)
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()

if __name__ == "__main__":
    calculator = RiskMetricsCalculator()
    calculator.run()
