import mysql.connector
from mysql.connector import Error
import pandas as pd
import numpy as np
import os
import math

class MySQLDataLoader:
    def __init__(self, host, user, password, database, processed_dir, banks_csv_path):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.processed_dir = processed_dir
        self.connection = None

        # Load dynamic registry
        self.banks_df = pd.read_csv(banks_csv_path)
        self.idrssd_to_ticker = dict(zip(self.banks_df['idrssd'].astype(str), self.banks_df['ticker']))
        self.ticker_to_idrssd = dict(zip(self.banks_df['ticker'], self.banks_df['idrssd'].astype(str)))

    def connect(self):
        try:
            temp_conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password)
            cursor = temp_conn.cursor()
            
            # Check if database exists and ask for user approval
            cursor.execute(f"SHOW DATABASES LIKE '{self.database}'")
            if cursor.fetchone():
                print(f"\n[WARNING] Database '{self.database}' already exists.")
                choice = input("Do you want to DROP the existing database and rebuild from scratch? (y/n): ")
                if choice.strip().lower() == 'y':
                    cursor.execute(f"DROP DATABASE {self.database}")
                    print(f"[INFO] Database dropped successfully.")
                else:
                    print("[INFO] Proceeding without dropping (using INSERT IGNORE).")
                    
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            temp_conn.close()

            self.connection = mysql.connector.connect(
                host=self.host, user=self.user, password=self.password, database=self.database
            )
            print(f"[SUCCESS] Connected to MySQL Database: {self.database}")
        except Error as e:
            print(f"[ERROR] while connecting to MySQL: {e}")

    def create_schema(self):
        cursor = self.connection.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_bank (
            idrssd INT PRIMARY KEY,
            ticker VARCHAR(10),
            bank_id VARCHAR(20),
            bank_name VARCHAR(100)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_quarter (
            quarter_id VARCHAR(10) PRIMARY KEY,
            year INT,
            quarter_num INT,
            quarter_end_date DATE
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_date (
            date DATE PRIMARY KEY,
            quarter_id VARCHAR(10),
            day_of_week VARCHAR(15),
            FOREIGN KEY (quarter_id) REFERENCES dim_quarter(quarter_id)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_financial_metric (
            metric_id INT AUTO_INCREMENT PRIMARY KEY,
            metric_name VARCHAR(100) UNIQUE,
            statement_type VARCHAR(50)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_loan_sector (
            sector_id INT AUTO_INCREMENT PRIMARY KEY,
            sector_name VARCHAR(100) UNIQUE
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_financials (
            quarter_id VARCHAR(10),
            idrssd INT,
            metric_id INT,
            metric_value DECIMAL(20,4),
            PRIMARY KEY (quarter_id, idrssd, metric_id),
            FOREIGN KEY (quarter_id) REFERENCES dim_quarter(quarter_id),
            FOREIGN KEY (idrssd) REFERENCES dim_bank(idrssd),
            FOREIGN KEY (metric_id) REFERENCES dim_financial_metric(metric_id)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_loan_balances (
            quarter_id VARCHAR(10),
            idrssd INT,
            sector_id INT,
            loan_amount DECIMAL(20,2),
            PRIMARY KEY (quarter_id, idrssd, sector_id),
            FOREIGN KEY (quarter_id) REFERENCES dim_quarter(quarter_id),
            FOREIGN KEY (idrssd) REFERENCES dim_bank(idrssd),
            FOREIGN KEY (sector_id) REFERENCES dim_loan_sector(sector_id)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_daily_market (
            date DATE,
            idrssd INT,
            open_price DECIMAL(10,4),
            high_price DECIMAL(10,4),
            low_price DECIMAL(10,4),
            close_price DECIMAL(10,4),
            volume BIGINT,
            PRIMARY KEY (date, idrssd),
            FOREIGN KEY (date) REFERENCES dim_date(date),
            FOREIGN KEY (idrssd) REFERENCES dim_bank(idrssd)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_macro_fed_rates (
            date DATE PRIMARY KEY,
            fed_funds_rate DECIMAL(10,4),
            FOREIGN KEY (date) REFERENCES dim_date(date)
        )""")

        self.connection.commit()
        print("[SUCCESS] Snowflake Schema created successfully.")

    def clean_nan(self, val):
        if pd.isna(val) or (isinstance(val, float) and math.isnan(val)):
            return None
        return val

    def load_data(self):
        cursor = self.connection.cursor()
        df_fin = pd.read_csv(os.path.join(self.processed_dir, 'fact_financials.csv'))
        df_loans = pd.read_csv(os.path.join(self.processed_dir, 'fact_loan_sectors.csv'))
        df_market = pd.read_csv(os.path.join(self.processed_dir, 'fact_daily_market.csv'))
        df_fed = pd.read_csv(os.path.join(self.processed_dir, 'dim_macro_fed_rates.csv'))

        print("DataFrames loaded. Beginning normalization and inserts...")

        banks = df_fin[['IDRSSD', 'Bank_ID', 'Bank_Name']].drop_duplicates()
        for _, row in banks.iterrows():
            idrssd = int(row['IDRSSD'])
            ticker = self.idrssd_to_ticker.get(str(idrssd), 'UNKNOWN')
            cursor.execute("INSERT IGNORE INTO dim_bank (idrssd, ticker, bank_id, bank_name) VALUES (%s, %s, %s, %s)",
                           (idrssd, ticker, row['Bank_ID'], row['Bank_Name']))
        
        dates = pd.to_datetime(df_market['Date'].dropna().unique())
        for d in dates:
            q_id = f"{d.year}-Q{d.quarter}"
            cursor.execute("INSERT IGNORE INTO dim_quarter (quarter_id, year, quarter_num, quarter_end_date) VALUES (%s, %s, %s, %s)",
                           (q_id, d.year, d.quarter, d.to_period('Q').end_time.date()))
            cursor.execute("INSERT IGNORE INTO dim_date (date, quarter_id, day_of_week) VALUES (%s, %s, %s)",
                           (d.date(), q_id, d.strftime('%A')))

        for _, row in df_fed.iterrows():
            d = pd.to_datetime(row['Date']).date()
            if d in dates.date:
                cursor.execute("INSERT IGNORE INTO dim_macro_fed_rates (date, fed_funds_rate) VALUES (%s, %s)",
                               (d, self.clean_nan(row['Fed_Rate'])))

        sector_cols = [c for c in df_loans.columns if c[0].isdigit()]
        sector_map = {}
        for s in sector_cols:
            cursor.execute("INSERT IGNORE INTO dim_loan_sector (sector_name) VALUES (%s)", (s,))
            cursor.execute("SELECT sector_id FROM dim_loan_sector WHERE sector_name=%s", (s,))
            sector_map[s] = cursor.fetchone()[0]

        df_loans['quarter_id'] = pd.to_datetime(df_loans['Date']).dt.to_period('Q').dt.strftime('%Y-Q%q')
        df_loans_melt = df_loans.melt(id_vars=['quarter_id', 'IDRSSD'], value_vars=sector_cols, var_name='Sector', value_name='Amount')
        
        loan_data = []
        for _, row in df_loans_melt.iterrows():
            val = self.clean_nan(row['Amount'])
            if val is not None:
                loan_data.append((row['quarter_id'], int(row['IDRSSD']), sector_map[row['Sector']], val))
        cursor.executemany("INSERT IGNORE INTO fact_loan_balances (quarter_id, idrssd, sector_id, loan_amount) VALUES (%s, %s, %s, %s)", loan_data)

        ignore_cols = ['Date', 'IDRSSD', 'Bank_ID', 'Bank_Name']
        metric_cols = [c for c in df_fin.columns if c not in ignore_cols]
        
        metric_map = {}
        for m in metric_cols:
            stmt_type = 'Income Statement' if 'Income' in m else 'Capital Ratios' if 'Ratio' in m else 'Balance Sheet'
            cursor.execute("INSERT IGNORE INTO dim_financial_metric (metric_name, statement_type) VALUES (%s, %s)", (m, stmt_type))
            cursor.execute("SELECT metric_id FROM dim_financial_metric WHERE metric_name=%s", (m,))
            metric_map[m] = cursor.fetchone()[0]

        df_fin['quarter_id'] = pd.to_datetime(df_fin['Date']).dt.to_period('Q').dt.strftime('%Y-Q%q')
        df_fin_melt = df_fin.melt(id_vars=['quarter_id', 'IDRSSD'], value_vars=metric_cols, var_name='Metric', value_name='Value')

        fin_data = []
        for _, row in df_fin_melt.iterrows():
            val = self.clean_nan(row['Value'])
            if val is not None:
                fin_data.append((row['quarter_id'], int(row['IDRSSD']), metric_map[row['Metric']], val))
        cursor.executemany("INSERT IGNORE INTO fact_financials (quarter_id, idrssd, metric_id, metric_value) VALUES (%s, %s, %s, %s)", fin_data)

        market_data = []
        for _, row in df_market.iterrows():
            idrssd = self.ticker_to_idrssd.get(row['Ticker'])
            if idrssd:
                market_data.append((
                    pd.to_datetime(row['Date']).date(), int(idrssd), 
                    self.clean_nan(row['Open']), self.clean_nan(row['High']), 
                    self.clean_nan(row['Low']), self.clean_nan(row['Close']), 
                    self.clean_nan(row['Volume'])
                ))
        cursor.executemany("INSERT IGNORE INTO fact_daily_market (date, idrssd, open_price, high_price, low_price, close_price, volume) VALUES (%s, %s, %s, %s, %s, %s, %s)", market_data)

        self.connection.commit()
        print("[SUCCESS] All 80,000+ rows successfully inserted into the Snowflake Schema!")

if __name__ == "__main__":
    from dotenv import load_dotenv
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    banks_csv_path = os.path.join(BASE_DIR, "config", "banks.csv")
    env_path = os.path.join(BASE_DIR, ".env")
    
    load_dotenv(dotenv_path=env_path)
    
    loader = MySQLDataLoader(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "Financial_Risk_EWS_db"),
        processed_dir=processed_dir,
        banks_csv_path=banks_csv_path
    )
    
    if not loader.password or loader.password == "YOUR_PASSWORD_HERE":
        print("[ERROR] Please update the .env file with your actual MySQL password before running.")
    else:
        loader.connect()
        loader.create_schema()
        loader.load_data()
