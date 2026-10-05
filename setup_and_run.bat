@echo off
setlocal enabledelayedexpansion

echo ==============================================================
echo Financial Risk EWS - Professional ETL Script Manager
echo ==============================================================

:: Check if virtual environment exists, if not create it
if not exist "venv\Scripts\activate" (
    echo [INFO] Creating Python Virtual Environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
)

:: Activate the virtual environment
echo [INFO] Activating Virtual Environment...
call venv\Scripts\activate

:: Install requirements
echo [INFO] Installing required dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    exit /b 1
)

echo.
echo ==============================================================
echo Running the ETL Pipeline...
echo ==============================================================

:: Step 1: Unzip FFIEC Data
echo [1/5] Unzipping FFIEC Data (May take a few minutes)...
python src\etl\01b_unzip_ffiec.py
if errorlevel 1 (
    echo [ERROR] Extraction failed.
    exit /b 1
)

:: Step 2: Extract FFIEC Loan Sectors
echo [2/5] Extracting Loan Sectors...
python src\etl\02_extract_transform_ffiec.py
if errorlevel 1 (
    echo [ERROR] Loan extraction failed.
    exit /b 1
)

:: Step 3: Transform Market Data
echo [3/5] Transforming Market Data...
python src\etl\03_transform_market_data.py
if errorlevel 1 (
    echo [ERROR] Market data transformation failed.
    exit /b 1
)

:: Step 4: Extract Financials
echo [4/5] Extracting Financials...
python src\etl\04_extract_financials.py
if errorlevel 1 (
    echo [ERROR] Financials extraction failed.
    exit /b 1
)

:: Optional Step 5: MySQL Loader
:: We skip it by default unless explicitly asked or run independently, but let's just note it
echo [5/5] Skipping MySQL load step. To load to DB, run: python src\etl\05_load_to_mysql.py

echo.
echo ==============================================================
echo [SUCCESS] Entire ETL Pipeline finished successfully!
echo Processed outputs are located in: data\processed\
echo ==============================================================
pause
