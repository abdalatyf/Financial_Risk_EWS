import pandas as pd
import glob
import os

class FFIECFinancialsExtractor:
    def __init__(self, extracted_dir, processed_dir, banks_csv_path):
        self.extracted_dir = extracted_dir
        self.processed_dir = processed_dir
        
        # Load banks registry
        self.banks_df = pd.read_csv(banks_csv_path)
        self.banks_df['idrssd'] = self.banks_df['idrssd'].astype(str)
        self.target_idrssds = set(self.banks_df['idrssd'])
        self.idrssd_to_meta = dict(zip(
            self.banks_df['idrssd'], 
            zip(self.banks_df['bank_id'], self.banks_df['bank_name'])
        ))
        
        self.metrics = {
            "Total_Assets": "2170", "Cash_Balances": "0010", "Total_Liabilities": "2948",
            "Total_Equity": "3210",
            "Tier1_Capital": "8274", "HTM_Securities": "1754", "AFS_Securities": "1773",
            "Risk_Weighted_Assets": "A223", "Tier1_Ratio_Pct": "7206",
            # --- HAZEM EXTENDED ANALYTICS METRICS ---
            "CET1_Ratio_Pct": "P793", "HTM_Fair_Value": "1771", 
            "AFS_Amortized_Cost": "1772", "Noninterest_Bearing_Deposits": "6631",
            "Net_Income": "4340", "Net_Interest_Income": "4074"
        }
        self.master_financials = []

    def get_val(self, row, mdrm_suffix, prefixes=None):
        if prefixes is None:
            prefixes = ['RCFD', 'RCON', 'RCOA', 'RCFN', 'RCFA', 'RIAD']
        for p in prefixes:
            col = p + mdrm_suffix
            if col in row and pd.notna(row[col]):
                val_str = str(row[col]).replace('%', '')
                val = pd.to_numeric(val_str, errors='coerce')
                if pd.notna(val):
                    return val
        return 0.0

    def process_quarter(self, quarter_dir):
        quarter_date = os.path.basename(quarter_dir)
        try:
            bank_data = {idrssd: {} for idrssd in self.target_idrssds}
            
            # Read RC (Balance Sheet) and RI (Income Statement) files
            call_files = glob.glob(os.path.join(quarter_dir, "FFIEC CDR Call Schedule RC*.txt")) + \
                         glob.glob(os.path.join(quarter_dir, "FFIEC CDR Call Schedule RI*.txt"))
            
            for call_file in call_files:
                if 'RCCI' in call_file: continue
                df_rc = pd.read_csv(call_file, sep='\t', dtype=str, low_memory=False)
                if 'IDRSSD' not in df_rc.columns: continue
                
                df_target = df_rc[df_rc['IDRSSD'].astype(str).isin(self.target_idrssds)]
                
                for _, row in df_target.iterrows():
                    idrssd = str(row['IDRSSD'])
                    
                    for metric_name, mdrm in self.metrics.items():
                        val = self.get_val(row, mdrm)
                        if val != 0 and (metric_name not in bank_data[idrssd] or bank_data[idrssd][metric_name] == 0):
                            bank_data[idrssd][metric_name] = val
                            
                    # Tier1_Ratio_Pct and CET1_Ratio_Pct standardizing
                    # Prior to 2015 some may be decimals. If > 1, divide by 100 to standardise to decimal.
                    for ratio_metric in ["Tier1_Ratio_Pct", "CET1_Ratio_Pct"]:
                        if ratio_metric in bank_data[idrssd]:
                            if bank_data[idrssd][ratio_metric] > 1.0:
                                bank_data[idrssd][ratio_metric] = bank_data[idrssd][ratio_metric] / 100.0

                    # Total Deposits: sum of RCON2200 (domestic) and RCFN2200 (foreign)
                    dom_dep = self.get_val(row, '2200', prefixes=['RCON'])
                    for_dep = self.get_val(row, '2200', prefixes=['RCFN'])
                    total_dep = dom_dep + for_dep
                    if total_dep != 0 and ("Total_Deposits" not in bank_data[idrssd] or bank_data[idrssd]["Total_Deposits"] == 0):
                        bank_data[idrssd]["Total_Deposits"] = total_dep
                        
                    # Uninsured Deposits: 5597
                    unins_dep = self.get_val(row, '5597')
                    if unins_dep != 0 and ("Uninsured_Deposits" not in bank_data[idrssd] or bank_data[idrssd]["Uninsured_Deposits"] == 0):
                        bank_data[idrssd]["Uninsured_Deposits"] = unins_dep

                    # Short Term Borrowings logic (B993 + B995 + 3190)
                    stb_val = self.get_val(row, 'B993') + self.get_val(row, 'B995') + self.get_val(row, '3190')
                    if stb_val != 0 and ("Short_Term_Borrowings" not in bank_data[idrssd] or bank_data[idrssd]["Short_Term_Borrowings"] == 0):
                        bank_data[idrssd]["Short_Term_Borrowings"] = stb_val
                        
                    # FHLB Advances logic: F055, F056, F057, F058, 2651
                    fhlb_val = (self.get_val(row, 'F055') + self.get_val(row, 'F056') + 
                                self.get_val(row, 'F057') + self.get_val(row, 'F058') + 
                                self.get_val(row, '2651'))
                    if fhlb_val != 0 and ("FHLB_Advances" not in bank_data[idrssd] or bank_data[idrssd]["FHLB_Advances"] == 0):
                        bank_data[idrssd]["FHLB_Advances"] = fhlb_val

            for idrssd, metrics in bank_data.items():
                bank_id, bank_name = self.idrssd_to_meta[idrssd]
                row_data = {"Date": quarter_date, "Bank_ID": bank_id, "Bank_Name": bank_name, "IDRSSD": idrssd}
                
                for metric_name in self.metrics.keys():
                    row_data[metric_name] = metrics.get(metric_name, 0.0)
                row_data["Total_Deposits"] = metrics.get("Total_Deposits", 0.0)
                row_data["Uninsured_Deposits"] = metrics.get("Uninsured_Deposits", 0.0)
                row_data["Short_Term_Borrowings"] = metrics.get("Short_Term_Borrowings", 0.0)
                row_data["FHLB_Advances"] = metrics.get("FHLB_Advances", 0.0)
                
                # Default empty/missing metrics to 0
                self.master_financials.append(row_data)

        except Exception as e:
            print(f"[ERROR] {quarter_dir}: {e}")

    def run_pipeline(self):
        quarter_dirs = sorted([d for d in glob.glob(os.path.join(self.extracted_dir, "*")) if os.path.isdir(d)])
        print(f"Found {len(quarter_dirs)} extracted quarters. Scanning massive core financial schedules...")
        
        for i, q_dir in enumerate(quarter_dirs, 1):
            self.process_quarter(q_dir)
            
        print("Consolidating Enterprise Financials...")
        df_final = pd.DataFrame(self.master_financials)
        
        # Deduplicate using IDRSSD
        df_final = df_final.groupby(['Date', 'Bank_ID', 'Bank_Name', 'IDRSSD'], as_index=False).max()
        df_final = df_final.sort_values(by=["Date", "Bank_Name"]).reset_index(drop=True)
        
        # Convert YTD Income to Quarterly Income
        # YTD income resets in Q1 (ends in 03-31). For Q2, Q3, Q4, we must subtract the previous quarter's value.
        df_final['Date'] = pd.to_datetime(df_final['Date'])
        df_final = df_final.sort_values(by=["IDRSSD", "Date"])
        
        # We need to subtract the previous row if they are in the same year.
        df_final['Year'] = df_final['Date'].dt.year
        df_final['Month'] = df_final['Date'].dt.month
        
        df_final['Prev_Net_Income'] = df_final.groupby(['IDRSSD', 'Year'])['Net_Income'].shift(1).fillna(0)
        df_final['Prev_Net_Interest_Income'] = df_final.groupby(['IDRSSD', 'Year'])['Net_Interest_Income'].shift(1).fillna(0)
        
        # Quarterly = YTD - Prev YTD
        df_final['Net_Income_Quarterly'] = df_final['Net_Income'] - df_final['Prev_Net_Income']
        df_final['Net_Interest_Income_Quarterly'] = df_final['Net_Interest_Income'] - df_final['Prev_Net_Interest_Income']
        
        # Replace original columns with the quarterly versions and clean up
        df_final['Net_Income'] = df_final['Net_Income_Quarterly']
        df_final['Net_Interest_Income'] = df_final['Net_Interest_Income_Quarterly']
        df_final = df_final.drop(columns=['Year', 'Month', 'Prev_Net_Income', 'Prev_Net_Interest_Income', 
                                          'Net_Income_Quarterly', 'Net_Interest_Income_Quarterly'])
                                          
        # Format Date back to string
        df_final['Date'] = df_final['Date'].dt.strftime('%Y-%m-%d')
        
        output_path = os.path.join(self.processed_dir, "fact_financials.csv")
        df_final.to_csv(output_path, index=False)
        print(f"\n[SUCCESS] Saved Core Financials to: {output_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    extracted = os.path.join(BASE_DIR, "data", "raw", "ffiec_extracted")
    processed = os.path.join(BASE_DIR, "data", "processed")
    banks_csv = os.path.join(BASE_DIR, "config", "banks.csv")
    extractor = FFIECFinancialsExtractor(extracted, processed, banks_csv)
    extractor.run_pipeline()
