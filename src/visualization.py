import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid")

def revenue_trend_chart(daily: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 4))
    if not daily.empty:
        ax.plot(pd.to_datetime(daily["order_day"]), daily["net_revenue"], marker="o")
    ax.set_title("Daily Net Revenue")
    ax.set_xlabel("Order date")
    ax.set_ylabel("Net revenue")
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig

def category_chart(category_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 4))
    if not category_df.empty:
        sns.barplot(data=category_df, x="category", y="net_revenue", ax=ax)
        ax.tick_params(axis="x", rotation=25)
    ax.set_title("Net Revenue by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Net revenue")
    fig.tight_layout()
    return fig

def region_heatmap(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5))
    if not df.empty:
        pivot = df.pivot_table(index="region", columns="category", values="net_revenue", aggfunc="sum", fill_value=0)
        sns.heatmap(pivot, annot=True, fmt=".0f", cmap="Blues", ax=ax)
    ax.set_title("Revenue: Region × Category")
    fig.tight_layout()
    return fig
