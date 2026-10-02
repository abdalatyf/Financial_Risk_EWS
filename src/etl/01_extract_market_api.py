import yfinance as yf
import pandas as pd
import os
import time

# Target Directory
target_dir = r"D:\Projects\EWS\EWS_SourceCode\data\raw\market_daily"
os.makedirs(target_dir, exist_ok=True)

# The 18 Banks to pull (SIVB and CMA are already done via CSV)
# Note: For NYCB, the ticker changed to FLG. For PacWest, it's BANC. 
# We'll use the active tickers that contain their historical data on Yahoo.
tickers = {
    "JPM": "JPMorgan",
    "BAC": "Bank of America",
    "WFC": "Wells Fargo",
    "PNC": "PNC Bank",
    "USB": "U.S. Bank",
    "FITB": "Fifth Third",
    "KEY": "KeyCorp",
    "RF": "Regions",
    "MTB": "M&T Bank",
    "HBAN": "Huntington",
    "CFG": "Citizens",
    "WAL": "Western Alliance",
    "BANC": "PacWest (now BANC)",
    "ZION": "Zions",
    "FLG": "New York Community (now FLG)",
    # Delisted / OTC tickers
    "FRCB": "First Republic",
    "SI": "Silvergate",
    "SBNY": "Signature"
}

start_date = "2008-01-01"
end_date = "2023-12-31"

print("="*60)
print("STARTING BRONZE LAYER API EXTRACTION (YFINANCE)")
print("="*60)

for ticker, name in tickers.items():
    csv_path = os.path.join(target_dir, f"{ticker}_daily.csv")
    
    # Skip if already downloaded (Idempotent!)
    if os.path.exists(csv_path):
        print(f"[SKIP] {ticker} ({name}) already exists.")
        continue
        
    print(f"Downloading {ticker} ({name})... ", end="")
    try:
        # Download data
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if df.empty:
            print(f"FAILED (No data returned from Yahoo)")
        else:
            # Flatten multi-index columns if they exist (yfinance sometimes returns multi-index)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # Save to CSV
            df.to_csv(csv_path)
            print(f"SUCCESS ({len(df):,} rows)")
            
    except Exception as e:
        print(f"FAILED ({e})")
        
    # Respect API rate limits
    time.sleep(1)

print("\n" + "="*60)
print("EXTRACTION COMPLETE.")
print(f"Check the folder: {target_dir}")
print("="*60)
