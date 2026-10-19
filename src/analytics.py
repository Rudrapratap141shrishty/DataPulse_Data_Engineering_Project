import pandas as pd

def build_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"orders": 0, "revenue": 0.0, "customers": 0, "avg_order_value": 0.0, "units_sold": 0}
    return {
        "orders": int(df["order_id"].nunique()),
        "revenue": round(float(df["net_revenue"].sum()), 2),
        "customers": int(df["customer_id"].nunique()),
        "avg_order_value": round(float(df.groupby("order_id")["net_revenue"].sum().mean()), 2),
        "units_sold": int(df["quantity"].sum()),
    }

def aggregate_daily_revenue(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["order_day", "net_revenue", "orders"])
    return (df.groupby("order_day", as_index=False)
              .agg(net_revenue=("net_revenue", "sum"), orders=("order_id", "nunique"))
              .sort_values("order_day"))

def aggregate_by_category(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["category", "net_revenue", "units_sold", "orders"])
    return (df.groupby("category", as_index=False)
              .agg(net_revenue=("net_revenue", "sum"),
                   units_sold=("quantity", "sum"),
                   orders=("order_id", "nunique"))
              .sort_values("net_revenue", ascending=False))

def aggregate_by_region(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["region", "net_revenue", "orders"])
    return (df.groupby("region", as_index=False)
              .agg(net_revenue=("net_revenue", "sum"), orders=("order_id", "nunique"))
              .sort_values("net_revenue", ascending=False))
