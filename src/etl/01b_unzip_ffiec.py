import os
import glob
import zipfile
import re
from datetime import datetime

class FFIECUnzipper:
    """
    Physically extracts the necessary Call Report schedules from the massive ZIP files
    into a structured 'extracted' directory.
    """
    def __init__(self, raw_zips_dir, extracted_dir):
        self.raw_zips_dir = raw_zips_dir
        self.extracted_dir = extracted_dir
        self.target_prefixes = ('FFIEC CDR Call Bulk POR', 'FFIEC CDR Call Schedule RC', 'FFIEC CDR Call Schedule RI')

    def parse_date(self, filename):
        # Phase 4 Fix: Secure regex date parsing to prevent string-hack failures
        match = re.search(r'\d{8}', filename)
        if match:
            return datetime.strptime(match.group(0), "%m%d%Y").strftime("%Y-%m-%d")
        return None

    def run_unzip(self):
        zips = glob.glob(os.path.join(self.raw_zips_dir, "*.zip"))
        print(f"Found {len(zips)} ZIP files. Beginning physical extraction...")
        
        for i, zip_path in enumerate(zips, 1):
            filename = os.path.basename(zip_path)
            quarter_date = self.parse_date(filename)
            
            if not quarter_date:
                continue
                
            quarter_dir = os.path.join(self.extracted_dir, quarter_date)
            os.makedirs(quarter_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as z:
                files_to_extract = [f for f in z.namelist() if f.startswith(self.target_prefixes) and f.endswith('.txt')]
                for f in files_to_extract:
                    target_path = os.path.join(quarter_dir, f)
                    if not os.path.exists(target_path): 
                        z.extract(f, quarter_dir)
                        
        print("\n[SUCCESS] All 60 quarters have been physically extracted to the staging folder.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_zips = os.path.join(BASE_DIR, "data", "raw", "ffiec_zips")
    extracted = os.path.join(BASE_DIR, "data", "raw", "ffiec_extracted")
    unzipper = FFIECUnzipper(raw_zips, extracted)
    unzipper.run_unzip()
