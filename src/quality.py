import pandas as pd

def split_valid_and_rejected(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Validate records and return (valid_rows, rejected_rows, quality_report).
    A rejected row includes a pipe-separated rejection_reason.
    """
    work = df.copy()
    original_count = len(work)
    reasons = pd.Series("", index=work.index, dtype="object")

    def mark(mask: pd.Series, message: str) -> None:
        nonlocal reasons
        mask = mask.fillna(True)
        reasons.loc[mask] = reasons.loc[mask].apply(
            lambda old: f"{old}|{message}" if old else message
        )

    # Convert fields before applying numeric/date validation.
    work["order_date"] = pd.to_datetime(work["order_date"], errors="coerce")
    for col in ["quantity", "unit_price", "discount"]:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    mark(work["order_id"].isna() | (work["order_id"].astype(str).str.strip() == ""), "missing_order_id")
    mark(work["order_date"].isna(), "invalid_order_date")
    mark(work["quantity"].isna() | (work["quantity"] <= 0), "invalid_quantity")
    mark(work["unit_price"].isna() | (work["unit_price"] < 0), "invalid_unit_price")
    mark(work["discount"].isna() | (work["discount"] < 0) | (work["discount"] > 1), "invalid_discount")

    # Only the first occurrence of an order ID is retained.
    duplicate_ids = work["order_id"].notna() & work["order_id"].astype(str).duplicated(keep="first")
    mark(duplicate_ids, "duplicate_order_id")

    rejected_mask = reasons.ne("")
    rejected = work.loc[rejected_mask].copy()
    rejected["rejection_reason"] = reasons.loc[rejected_mask]
    valid = work.loc[~rejected_mask].copy()

    report_rows = [
        {"metric": "input_rows", "value": int(original_count)},
        {"metric": "valid_rows", "value": int(len(valid))},
        {"metric": "rejected_rows", "value": int(len(rejected))},
        {"metric": "rejection_rate_pct", "value": round((len(rejected) / original_count * 100), 2) if original_count else 0.0},
        {"metric": "duplicate_order_ids", "value": int(duplicate_ids.sum())},
        {"metric": "missing_values_before_cleaning", "value": int(df.isna().sum().sum())},
    ]
    report = pd.DataFrame(report_rows)
    return valid, rejected, report
