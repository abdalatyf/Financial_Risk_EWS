# DEPI Graduation Project — Milestone 2
## 4. System Analysis & Design

**Track:** Professional Data Analyst (DEPI Round 5)  
**Group ID:** BNS5_DAT3_S1  
**Project Name:** Financial Risk Early Warning System (EWS)  
**Team Leader:** Abdalatyf Ahmed Ibrahim  
**Submission Deadline:** November 06, 2026  

---

### 4.1 Software Architecture

The Financial Risk EWS follows a decoupled, three-tier **Push-Down Analytical Architecture**:

```mermaid
flowchart TD
    subgraph Layer1["1. Raw Data Ingestion (Bronze Layer)"]
        A1["FFIEC Bulk ZIPs (60 Quarters)"]
        A2["Yahoo / Market Daily (20 Banks)"]
        A3["FRED Fed Funds Rate (Daily)"]
    end

    subgraph Layer2["2. Processing & Normalization (Silver Layer)"]
        B1["FFIEC Unzipper & Stager (01b)"]
        B2["Loan Sector Normalizer (02)"]
        B3["Market Transformer (03)"]
        B4["Financials & Capital Recovery (04)"]
        B5["Python Risk Engine (06)"]
    end

    subgraph Layer3["3. Enterprise Warehouse (Gold Layer - MySQL)"]
        C1["Relational Star Schema Database"]
        C2["6 Dimension Tables"]
        C3["3 Normalized Fact Tables"]
        C4["Analytical SQL Views"]
    end

    subgraph Layer4["4. Business Intelligence & Executive UI (Presentation Layer)"]
        D1["Figma Design System & Mockups"]
        D2["8-Page Power BI Interactive Report"]
        D3["Executive EWS Heatmap & Drill-Downs"]
    end

    A1 --> B1
    B1 --> B2
    B1 --> B4
    A2 --> B3
    A3 --> B3
    B2 --> B5
    B4 --> B5
    B2 --> C1
    B3 --> C1
    B4 --> C1
    B5 --> C1
    C1 --> C4
    D1 -.-> D2
    C4 --> D2
    D2 --> D3
```

---

### 4.2 Database Design & Data Modeling (ERD)

The data warehouse is modeled as a normalized **Star / Snowflake Schema** centered around financial performance, credit distribution, and daily market valuation:

```mermaid
erDiagram
    dim_bank ||--o{ fact_financials : "reports"
    dim_quarter ||--o{ fact_financials : "per quarter"
    dim_financial_metric ||--o{ fact_financials : "measured by"

    dim_bank ||--o{ fact_loan_balances : "holds"
    dim_quarter ||--o{ fact_loan_balances : "per quarter"
    dim_loan_sector ||--o{ fact_loan_balances : "allocated across"

    dim_bank ||--o{ fact_daily_market : "trades"
    dim_date ||--o{ fact_daily_market : "on date"

    dim_quarter ||--o{ dim_date : "contains"
    dim_date ||--o{ dim_macro_fed_rates : "rates observed on"

    dim_bank {
        int idrssd PK
        string ticker
        string bank_id
        string bank_name
        int tier
        string tier_label
    }

    dim_quarter {
        string quarter_id PK
        int year
        int quarter_num
        date quarter_end_date
        string era
    }

    dim_date {
        date date PK
        string quarter_id FK
        string day_of_week
    }

    dim_financial_metric {
        int metric_id PK
        string metric_name UK
        string statement_type
    }

    dim_loan_sector {
        int sector_id PK
        string sector_name UK
    }

    dim_macro_fed_rates {
        date date PK, FK
        decimal fed_funds_rate
    }

    fact_financials {
        string quarter_id PK, FK
        int idrssd PK, FK
        int metric_id PK, FK
        decimal metric_value
    }

    fact_loan_balances {
        string quarter_id PK, FK
        int idrssd PK, FK
        int sector_id PK, FK
        decimal loan_amount
    }

    fact_daily_market {
        date date PK, FK
        int idrssd PK, FK
        decimal open_price
        decimal high_price
        decimal low_price
        decimal close_price
        bigint volume
    }
```

---

### 4.3 Data Flow Diagrams (DFD)

#### Level 0: Context-Level DFD
```mermaid
flowchart LR
    S1["FFIEC CDR Public Repository"] -->|"Bulk Call Report Archives"| EWS(("Financial Risk EWS Platform"))
    S2["FRED (St. Louis Fed)"] -->|"Effective Fed Funds Rate"| EWS
    S3["Yahoo Finance & Market Data"] -->|"Daily OHLCV Equities"| EWS

    EWS -->|"8-Page Power BI Executive Dashboard"| U1["Bank Supervisors & Examiners"]
    EWS -->|"EWS Heatmap & Risk Metrics"| U2["Bank Chief Risk Officers"]
    EWS -->|"Figma Mockups & Academic Backtest"| U3["DEPI Evaluation Panel"]
```

#### Level 1: Detailed Process Flow
```mermaid
flowchart TD
    P1["1.0 Physical Extraction & Staging"] --> P2["2.0 Schema Cleaning & Financial Recovery"]
    P2 --> P3["3.0 Risk Metric & Velocity Engine"]
    P3 --> P4["4.0 Relational Loader (MySQL)"]
    P4 --> P5["5.0 Analytical View Generation"]
    P5 --> P6["6.0 Power BI Dashboard Rendering"]

    D1[("Raw File Storage")] <--> P1
    D2[("Processed CSV Warehouse")] <--> P2
    D2 <--> P3
    D3[("MySQL Star Schema")] <--> P4
    D3 <--> P5
    P6 --> D4["Executive User Interface"]
```

---

### 4.4 Data Flow & System Interactions (Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / User
    participant Bat as setup_and_run.bat
    participant Py as Python ETL Pipeline (01b-05)
    participant DB as MySQL Database
    participant BI as Power BI Desktop

    Dev->>Bat: Execute 1-Click Setup
    Bat->>Bat: Initialize venv & install requirements.txt
    Bat->>Py: Run 01b (Unzip Call Reports)
    Bat->>Py: Run 02 & 04 (Extract Loans & Financials)
    Bat->>Py: Run 03 (Transform Market & Fed Data)
    Dev->>Py: Execute 05_load_to_mysql.py
    Py->>DB: Verify / Create Star Schema (9 Tables)
    Py->>DB: Bulk Insert ~121,328 Normalized Rows
    DB-->>Py: Transaction Commit Confirmed
    Dev->>BI: Connect to MySQL Database
    BI->>DB: Query Optimized Analytical Views
    DB-->>BI: Return Pre-Aggregated Risk Metrics
    BI->>Dev: Render 8-Page Interactive Dashboard
```

---

### 4.5 System Deployment & Technology Stack

| Architecture Layer | Technology Selection | Version / Standard | Justification |
| :--- | :--- | :--- | :--- |
| **Language Runtime** | **Python** | 3.11+ / 3.12 | Industry standard for data engineering, vectorized math, and FFIEC parsing. |
| **Data Manipulation** | **Pandas & NumPy** | pandas 2.2.3, numpy 2.1.2 | High-performance matrix operations and time-series manipulation. |
| **Relational Database** | **MySQL Community Server** | 8.0+ / 9.0 | ACID compliant, high-speed relational Star Schema storage with foreign keys. |
| **Database Connector** | **mysql-connector-python** | 9.0.0 | Native transactional Python-MySQL pipeline communication. |
| **UI/UX Prototyping** | **Figma** | Cloud Standard | Official DEPI design deliverable; establishes layout guidelines and assets. |
| **Data Visualization** | **Microsoft Power BI** | Desktop (Latest) | Interactive multi-page executive dashboards, slicers, and drill-downs. |
| **DevOps & Automation** | **Windows Batch Scripting** | `setup_and_run.bat` | 1-click environment bootstrap, idempotency, and automated execution. |
| **Version Control** | **Git & GitHub** | GitHub Public Repo | Transparent collaboration, branch protection, and full commit lineage. |
