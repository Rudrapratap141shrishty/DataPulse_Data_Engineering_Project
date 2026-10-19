# DataPulse — End-to-End Data Engineering & Analytics Platform

DataPulse is an advanced, portfolio-ready data engineering and analytics project built with **Pandas, NumPy, Matplotlib, Seaborn, and Streamlit**. It demonstrates a practical ETL/ELT workflow: ingest raw data, validate it, clean and transform it, create analytical outputs, and explore results in an interactive dashboard.

## Features

- CSV ingestion with schema checks and useful error messages
- Data-quality checks: missing values, duplicate order IDs, invalid quantities/prices, and invalid dates
- Reproducible cleaning and transformation pipeline
- NumPy-based derived metrics and Pandas aggregations
- CSV outputs for cleaned data, rejected rows, quality report, and KPI summaries
- Interactive Streamlit dashboard with filters, KPIs, charts, and downloadable data
- Matplotlib and Seaborn visualizations
- Logging, configuration, sample dataset, and unit tests

## Architecture

```text
data/raw/orders.csv
       |
       v
src/ingestion.py  ---> raw DataFrame
       |
       v
src/quality.py    ---> quality report + rejected rows
       |
       v
src/transform.py  ---> cleaned / enriched DataFrame
       |
       +----> data/processed/clean_orders.csv
       +----> data/processed/rejected_rows.csv
       +----> data/processed/quality_report.csv
       +----> data/processed/daily_revenue.csv
       |
       v
Streamlit dashboard (app.py)
```

## 1. Requirements

- Python 3.10 or newer recommended
- pip
- VS Code or PyCharm

## 2. Create and activate a virtual environment

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run the commands in Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Run the ETL pipeline

From the project root:

```bash
python run_pipeline.py
```

The pipeline reads `data/raw/orders.csv` and writes output files into `data/processed/`.

To process another CSV:

```bash
python run_pipeline.py --input path/to/orders.csv
```

Expected columns:

`order_id, order_date, customer_id, region, product, category, quantity, unit_price, discount`

`discount` is a fraction from 0 to 1 (for example, `0.10` means 10%). The pipeline calculates `gross_revenue`, `discount_amount`, and `net_revenue`.

## 4. Run the dashboard

```bash
streamlit run app.py
```

Open the local URL shown in the terminal. Use the sidebar to filter date range, region, and category. The dashboard uses processed outputs if available; otherwise it runs the pipeline from the bundled sample data.

## 5. Run tests

```bash
python -m unittest discover -s tests -v
```

## 6. Data quality rules

- Required fields must exist.
- `order_id` must be present and unique.
- `order_date` must parse as a date.
- `quantity` must be greater than zero.
- `unit_price` must be non-negative.
- `discount` must be between 0 and 1.
- Rows failing core rules are sent to `rejected_rows.csv`.
- Missing region/product/category/customer fields are filled with `Unknown` where practical.
- Duplicate order IDs after the first valid occurrence are rejected.

## 7. Project structure

```text
datapulse_data_engineering_project/
├── app.py
├── run_pipeline.py
├── requirements.txt
├── README.md
├── .gitignore
├── config/
│   └── settings.json
├── data/
│   ├── raw/orders.csv
│   └── processed/.gitkeep
├── reports/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── ingestion.py
│   ├── quality.py
│   ├── transform.py
│   ├── analytics.py
│   └── visualization.py
└── tests/
    └── test_pipeline.py
```

## 8. Ideas to extend it

- Replace CSV ingestion with PostgreSQL, MySQL, or a REST API.
- Add a scheduled run using cron or Windows Task Scheduler.
- Store pipeline metadata in a database.
- Add Great Expectations or Pandera for richer data contracts.
- Add Docker and CI with GitHub Actions.
- Add incremental loads, partitioned Parquet files, and a warehouse layer.
- Add Kafka for streaming events.

## Troubleshooting

- **`ModuleNotFoundError`**: activate `.venv` and run `pip install -r requirements.txt`.
- **Dashboard has no data**: run `python run_pipeline.py`, then refresh Streamlit.
- **CSV schema error**: compare the CSV headers with the expected column list above.
- **Matplotlib backend warning**: this project uses `st.pyplot()` in Streamlit; no GUI window is required.
