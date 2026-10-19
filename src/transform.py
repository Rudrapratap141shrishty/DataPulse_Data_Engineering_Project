import numpy as np
import pandas as pd

TEXT_COLUMNS = ["customer_id", "region", "product", "category"]

def transform_orders(valid_df: pd.DataFrame) -> pd.DataFrame:
    """Clean text fields and create reusable revenue/time dimensions."""
    df = valid_df.copy()
    for col in TEXT_COLUMNS:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()
        df.loc[df[col].eq(""), col] = "Unknown"

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype("int64")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").astype(float)
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").astype(float)

    # NumPy vectorized calculations; avoid slow row-by-row loops.
    df["gross_revenue"] = np.multiply(df["quantity"].to_numpy(), df["unit_price"].to_numpy())
    df["discount_amount"] = df["gross_revenue"] * df["discount"]
    df["net_revenue"] = (df["gross_revenue"] - df["discount_amount"]).round(2)

    df["order_year"] = df["order_date"].dt.year.astype(int)
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["order_day"] = df["order_date"].dt.date.astype(str)
    df["weekday"] = df["order_date"].dt.day_name()
    df["is_weekend"] = df["order_date"].dt.dayofweek >= 5

    return df.sort_values("order_date").reset_index(drop=True)
