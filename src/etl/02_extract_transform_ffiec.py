import pandas as pd
import glob
import os

class FFIECLoansExtractor:
    def __init__(self, raw_dir, processed_dir, banks_csv_path):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        
        # Load banks registry
        self.banks_df = pd.read_csv(banks_csv_path)
        self.banks_df['idrssd'] = self.banks_df['idrssd'].astype(str)
        self.target_idrssds = set(self.banks_df['idrssd'])
        self.idrssd_to_meta = dict(zip(
            self.banks_df['idrssd'], 
            zip(self.banks_df['bank_id'], self.banks_df['bank_name'])
        ))
        self.master_loan_data = []

    def get_val(self, row, *cols):
        for col in cols:
            if col in row and pd.notna(row[col]):
                val = pd.to_numeric(row[col], errors='coerce')
                if pd.notna(val):
                    return val
        return 0.0

    def process_quarter(self, quarter_dir):
        quarter_date = os.path.basename(quarter_dir)
        
        try:
            rcci_files = glob.glob(os.path.join(quarter_dir, "*RCCI*.txt"))
            if not rcci_files: return
            
            df_rcci = pd.read_csv(rcci_files[0], sep='\t', dtype=str, low_memory=False)
            if 'IDRSSD' not in df_rcci.columns: return
            
            df_loans = df_rcci[df_rcci['IDRSSD'].astype(str).isin(self.target_idrssds)].copy()
            
            for index, row in df_loans.iterrows():
                idrssd = str(row['IDRSSD'])
                bank_id, bank_name = self.idrssd_to_meta[idrssd]
                
                total_loans = self.get_val(row, 'RCFD2122', 'RCON2122')
                unearned = self.get_val(row, 'RCFD2123', 'RCON2123')
                
                sec_1_const = self.get_val(row, 'RCFDF158', 'RCONF158') + self.get_val(row, 'RCFDF159', 'RCONF159')
                sec_2_farm = self.get_val(row, 'RCFD1420', 'RCON1420')
                sec_3_resi = self.get_val(row, 'RCFD5367', 'RCON5367') + self.get_val(row, 'RCFD5368', 'RCON5368')
                sec_4_multi = self.get_val(row, 'RCFD1460', 'RCON1460')
                sec_5_cre = self.get_val(row, 'RCFDF160', 'RCONF160') + self.get_val(row, 'RCFDF161', 'RCONF161')
                sec_6_dep_inst = self.get_val(row, 'RCFDB531', 'RCONB531') + self.get_val(row, 'RCFDB534', 'RCONB534') + self.get_val(row, 'RCFDB535', 'RCONB535')
                sec_7_nondep_inst = self.get_val(row, 'RCFDJ454', 'RCONJ454')
                sec_8_ci = self.get_val(row, 'RCFD1763', 'RCON1766') + self.get_val(row, 'RCFD1764')
                sec_9_agri = self.get_val(row, 'RCFD1590', 'RCON1590')
                sec_10_cards = self.get_val(row, 'RCFDB538', 'RCONB538')
                sec_11_auto = self.get_val(row, 'RCFDK137', 'RCONK137')
                sec_12_other_con = self.get_val(row, 'RCFDK207', 'RCONK207') + self.get_val(row, 'RCFDB539', 'RCONB539')
                sec_13_foreign = self.get_val(row, 'RCFD2081', 'RCON2081')
                sec_14_muni = self.get_val(row, 'RCFD2107', 'RCON2107')
                sec_15_leases = self.get_val(row, 'RCFD2165', 'RCON2165')
                sec_16_other = self.get_val(row, 'RCFDJ451', 'RCONJ451') + self.get_val(row, 'RCFD1563', 'RCON1563')
                
                gross_mapped = (sec_1_const + sec_2_farm + sec_3_resi + sec_4_multi + sec_5_cre +
                                sec_6_dep_inst + sec_7_nondep_inst + sec_8_ci + sec_9_agri +
                                sec_10_cards + sec_11_auto + sec_12_other_con +
                                sec_13_foreign + sec_14_muni + sec_15_leases + sec_16_other)
                
                net_mapped = gross_mapped - unearned
                variance = total_loans - net_mapped
                if variance != 0: sec_16_other += variance
                
                self.master_loan_data.append({
                    "Date": quarter_date, "Bank_ID": bank_id, "Bank_Name": bank_name, "IDRSSD": idrssd,
                    "Total_Loans": total_loans, "1_Construction": sec_1_const,
                    "2_Farmland": sec_2_farm, "3_Residential_1_4": sec_3_resi,
                    "4_Multifamily": sec_4_multi, "5_Commercial_RE": sec_5_cre,
                    "6_Depository_Inst": sec_6_dep_inst, "7_Nondepository_Inst": sec_7_nondep_inst,
                    "8_C_and_I": sec_8_ci, "9_Agriculture": sec_9_agri,
                    "10_Credit_Cards": sec_10_cards, "11_Auto": sec_11_auto,
                    "12_Other_Consumer": sec_12_other_con, "13_Foreign_Gov": sec_13_foreign,
                    "14_Municipal": sec_14_muni, "15_Leases": sec_15_leases, "16_All_Other": sec_16_other
                })
                
        except Exception as e:
            print(f"[ERROR] {quarter_dir}: {e}")

    def run_pipeline(self):
        quarter_dirs = sorted([d for d in glob.glob(os.path.join(self.raw_dir, "*")) if os.path.isdir(d)])
        print(f"Found {len(quarter_dirs)} extracted quarters. Beginning Loan Extraction...")
        
        for i, q_dir in enumerate(quarter_dirs, 1):
            self.process_quarter(q_dir)
            
        print("Transforming to Pandas DataFrame...")
        df_final = pd.DataFrame(self.master_loan_data)
        
        # Aggregate at IDRSSD level (actually sum is fine here for loans, or max. Let's use sum for multiple loan branches if any)
        df_final = df_final.groupby(['Date', 'Bank_ID', 'Bank_Name', 'IDRSSD'], as_index=False).sum()
        df_final = df_final.sort_values(by=["Date", "Bank_Name"]).reset_index(drop=True)
        
        output_path = os.path.join(self.processed_dir, "fact_loan_sectors.csv")
        df_final.to_csv(output_path, index=False)
        print(f"\n[SUCCESS] Saved perfectly clean Star Schema fact table to: {output_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    extracted = os.path.join(BASE_DIR, "data", "raw", "ffiec_extracted")
    processed = os.path.join(BASE_DIR, "data", "processed")
    banks_csv = os.path.join(BASE_DIR, "config", "banks.csv")
    extractor = FFIECLoansExtractor(extracted, processed, banks_csv)
    extractor.run_pipeline()
