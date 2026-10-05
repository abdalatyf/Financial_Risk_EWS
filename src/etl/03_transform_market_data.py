import pandas as pd
import numpy as np
import glob
import os

class MarketDataTransformer:
    def __init__(self, raw_market_dir, raw_fed_path, processed_dir, banks_csv_path):
        self.raw_market_dir = raw_market_dir
        self.raw_fed_path = raw_fed_path
        self.processed_dir = processed_dir
        
        self.banks_df = pd.read_csv(banks_csv_path)
        # Create lookups
        self.ticker_to_basis = dict(zip(self.banks_df['ticker'], self.banks_df['price_basis']))
        self.ticker_to_end_date = dict(zip(self.banks_df['ticker'], self.banks_df['last_trading_date']))
        
        self.master_df = pd.DataFrame()
        self.fed_df = pd.DataFrame()

    def clean_numeric(self, val):
        if pd.isna(val):
            return np.nan
        val = str(val).upper().strip()
        val = val.replace('$', '').replace(',', '')
        try:
            if 'M' in val: return float(val.replace('M', '')) * 1000000
            elif 'K' in val: return float(val.replace('K', '')) * 1000
            elif 'B' in val: return float(val.replace('B', '')) * 1000000000
            else: return float(val)
        except ValueError:
            return np.nan

    def process_fed_rate(self):
        print("Processing Federal Funds Rate (FRED)...")
        df = pd.read_csv(self.raw_fed_path)
        date_col = [c for c in df.columns if 'DATE' in c.upper()][0]
        rate_col = [c for c in df.columns if 'DFF' in c.upper()][0]
        
        df = df[[date_col, rate_col]].rename(columns={date_col: 'Date', rate_col: 'Fed_Rate'})
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Fed_Rate'] = pd.to_numeric(df['Fed_Rate'], errors='coerce')
        df['Fed_Rate'] = df['Fed_Rate'].ffill()
        self.fed_df = df.dropna(subset=['Date'])

    def process_bank_file(self, filepath):
        filename = os.path.basename(filepath)
        ticker = filename.replace('_daily.csv', '')
        
        # We only process if it's in our banks registry
        if ticker not in self.ticker_to_basis:
            return pd.DataFrame()
            
        df = pd.read_csv(filepath)
        cols = [c.upper().strip() for c in df.columns]
        df.columns = cols
        
        date_col = 'DATE' if 'DATE' in cols else cols[0]
        df['Date'] = pd.to_datetime(df[date_col], errors='coerce')
        
        if 'CLOSE/LAST' in cols: df['Close'] = df['CLOSE/LAST']
        elif 'PRICE' in cols: df['Close'] = df['PRICE']
        elif 'CLOSE' in cols: df['Close'] = df['CLOSE']
        else: df['Close'] = np.nan
            
        if 'VOLUME' in cols: df['Volume'] = df['VOLUME']
        elif 'VOL.' in cols: df['Volume'] = df['VOL.']
        else: df['Volume'] = np.nan

        df['Open'] = df['OPEN'] if 'OPEN' in cols else np.nan
        df['High'] = df['HIGH'] if 'HIGH' in cols else np.nan
        df['Low'] = df['LOW'] if 'LOW' in cols else np.nan
        
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = df[col].apply(self.clean_numeric)

        df['Ticker'] = ticker
        df['Price_Basis'] = self.ticker_to_basis.get(ticker, 'unknown')
        df = df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Price_Basis']]
        
        df['Low'] = df[['Low', 'Open', 'Close']].min(axis=1)
        df['High'] = df[['High', 'Open', 'Close']].max(axis=1)
        
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].round(4)
            
        df['Volume'] = df['Volume'].fillna(0)
        
        df = df[(df['Date'] >= '2008-01-01') & (df['Date'] <= '2023-12-31')]
        
        # Trim based on last trading date
        end_date = self.ticker_to_end_date.get(ticker)
        if pd.notna(end_date):
            df = df[df['Date'] <= pd.to_datetime(end_date)]
            
        return df.dropna(subset=['Date', 'Close'])

    def run_pipeline(self):
        self.process_fed_rate()
        market_files = glob.glob(os.path.join(self.raw_market_dir, "*.csv"))
        print(f"Found {len(market_files)} bank market files. Transforming schemas...")
        
        frames = []
        for file in market_files:
            df = self.process_bank_file(file)
            if not df.empty:
                frames.append(df)
            
        self.master_df = pd.concat(frames, ignore_index=True)
        # Format date as string to avoid timezone issues when saving
        self.master_df['Date'] = self.master_df['Date'].dt.strftime('%Y-%m-%d')
        self.master_df = self.master_df.sort_values(by=['Date', 'Ticker']).reset_index(drop=True)
        
        market_output = os.path.join(self.processed_dir, "fact_daily_market.csv")
        self.master_df.to_csv(market_output, index=False)
        
        self.fed_df['Date'] = self.fed_df['Date'].dt.strftime('%Y-%m-%d')
        self.fed_df = self.fed_df.sort_values(by=['Date']).reset_index(drop=True)
        fed_output = os.path.join(self.processed_dir, "dim_macro_fed_rates.csv")
        self.fed_df.to_csv(fed_output, index=False)
        
        print("\n[SUCCESS] Market & Macro Data ETL Complete!")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_market = os.path.join(BASE_DIR, "data", "raw", "market_daily")
    raw_fed = os.path.join(BASE_DIR, "data", "raw", "fed_rate.csv")
    processed = os.path.join(BASE_DIR, "data", "processed")
    banks_csv = os.path.join(BASE_DIR, "config", "banks.csv")
    transformer = MarketDataTransformer(raw_market, raw_fed, processed, banks_csv)
    transformer.run_pipeline()
