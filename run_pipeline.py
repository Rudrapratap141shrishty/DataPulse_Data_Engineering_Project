import argparse
import logging
from pathlib import Path
import pandas as pd

from src.ingestion import load_orders
from src.quality import split_valid_and_rejected
from src.transform import transform_orders
from src.analytics import aggregate_daily_revenue, aggregate_by_category, aggregate_by_region

ROOT = Path(__file__).resolve().parent

def run_pipeline(input_path: str | Path = ROOT / "data/raw/orders.csv",
                 output_dir: str | Path = ROOT / "data/processed") -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / "reports").mkdir(exist_ok=True)

    logging.basicConfig(
        filename=ROOT / "reports/pipeline.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        force=True,
    )
    logging.info("Pipeline started. Input=%s", input_path)

    raw = load_orders(input_path)
    valid, rejected, quality_report = split_valid_and_rejected(raw)
    clean = transform_orders(valid)

    clean.to_csv(output_dir / "clean_orders.csv", index=False)
    rejected.to_csv(output_dir / "rejected_rows.csv", index=False)
    quality_report.to_csv(output_dir / "quality_report.csv", index=False)
    aggregate_daily_revenue(clean).to_csv(output_dir / "daily_revenue.csv", index=False)
    aggregate_by_category(clean).to_csv(output_dir / "category_summary.csv", index=False)
    aggregate_by_region(clean).to_csv(output_dir / "region_summary.csv", index=False)

    logging.info("Pipeline finished. input=%d valid=%d rejected=%d", len(raw), len(clean), len(rejected))
    return {
        "input_rows": len(raw),
        "valid_rows": len(clean),
        "rejected_rows": len(rejected),
        "output_dir": str(output_dir),
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the DataPulse ETL pipeline.")
    parser.add_argument("--input", default=str(ROOT / "data/raw/orders.csv"), help="Path to input CSV")
    parser.add_argument("--output", default=str(ROOT / "data/processed"), help="Output directory")
    args = parser.parse_args()
    result = run_pipeline(args.input, args.output)
    print("Pipeline completed:")
    for key, value in result.items():
        print(f"  {key}: {value}")
