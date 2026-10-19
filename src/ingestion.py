from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = [
    "order_id", "order_date", "customer_id", "region", "product",
    "category", "quantity", "unit_price", "discount"
]

def load_orders(path: str | Path) -> pd.DataFrame:
    """Read an orders CSV and verify that the expected schema is present."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input CSV was not found: {path}")
    df = pd.read_csv(path)
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
    return df
