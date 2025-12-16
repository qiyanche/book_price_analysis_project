from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from utils.io_helpers import project_path

"""
Visualization Script
--------------------
Creates several plots using Matplotlib:

1. Histogram of book prices
2. Boxplot of price distribution
3. Bar chart of top 10 most expensive books

All plots are saved in the results/ folder.
"""

IN_CSV = project_path("data", "processed", "prices.csv")
OUT_DIR = project_path("results")


def plot_histogram(df):
    plt.figure(figsize=(8, 5))
    plt.hist(df["price"], bins=20)
    plt.title("Distribution of Book Prices")
    plt.xlabel("Price (GBP)")
    plt.ylabel("Frequency")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "hist_price.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out


def plot_boxplot(df):
    plt.figure(figsize=(6, 5))
    plt.boxplot(df["price"], vert=True, showmeans=True)
    plt.title("Boxplot of Book Prices")
    plt.ylabel("Price (GBP)")

    out = OUT_DIR / "boxplot_price.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out


def plot_top10(df):
    # Find max price per product
    top10 = (
        df.groupby(["product_id", "name"])["price"]
        .max()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    plt.figure(figsize=(10, 6))
    plt.barh(top10["name"], top10["price"])
    plt.title("Top 10 Most Expensive Books")
    plt.xlabel("Price (GBP)")
    plt.ylabel("Book Title")
    plt.tight_layout()

    out = OUT_DIR / "top10_books.png"
    plt.savefig(out, dpi=150)
    plt.close()
    return out


def main():
    df = pd.read_csv(IN_CSV)

    if df.empty:
        print("[WARN] prices.csv is empty. Run clean_data.py first.")
        return

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])

    p1 = plot_histogram(df)
    print(f"[OK] Saved {p1}")

    p2 = plot_boxplot(df)
    print(f"[OK] Saved {p2}")

    p3 = plot_top10(df)
    print(f"[OK] Saved {p3}")


if __name__ == "__main__":
    main()
