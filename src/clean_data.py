from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
from bs4 import BeautifulSoup

from utils.io_helpers import project_path, read_json, write_json

"""
Data Cleaning Script
--------------------
This script performs the following data-cleaning steps:

1. Read raw snapshot JSON files produced by `get_data.py`.
2. Normalize each raw record into a flat tabular schema.
3. Handle missing values (e.g., drop records missing critical fields,
   fill non-critical fields with defaults).
4. Strip any remaining HTML tags from text fields.
5. Remove duplicate records.
6. Convert the cleaned data into a structured JSON file and a CSV file.

If the source website contained non-English text, this is also the place
where translation to English would be performed. For Books to Scrape,
all content is already in English, so translation is not applied.
"""

# Output locations
PROCESSED_DIR = project_path("data", "processed")
OUT_JSON = PROCESSED_DIR / "books_clean.json"
OUT_CSV = PROCESSED_DIR / "prices.csv"


def strip_html(text: str | None) -> str | None:
    """
    Remove any HTML tags from a text string.

    For this dataset, most fields are already plain text, but this
    function demonstrates how HTML tags would be cleaned if present.
    """
    if text is None or pd.isna(text):
        return None
    # Use BeautifulSoup to robustly remove HTML tags
    return BeautifulSoup(str(text), "lxml").get_text(strip=True)


def maybe_translate_to_english(text: str | None) -> str | None:
    """
    Placeholder for language normalization.

    If the source data contained non-English text, this function would
    call a translation API or model to translate it into English.
    Because Books to Scrape is already in English, we simply return
    the original text.
    """
    return text


def normalize_record(raw: dict, snapshot_time: str) -> dict:
    """
    Normalize a single raw product record into a flat schema.

    We also derive a simple product_id from the URL (slug before '/index.html'),
    which allows us to track the same product across multiple snapshots.
    """
    url = raw.get("url") or ""
    # Example URL:
    # http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
    m = re.search(r"/catalogue/([^/]+)/index\.html", url)
    product_id = m.group(1) if m else None

    name = raw.get("name")
    availability = raw.get("availability")
    currency = raw.get("currency") or "GBP"

    # Strip HTML and (if needed) translate to English
    name = maybe_translate_to_english(strip_html(name))
    availability = maybe_translate_to_english(strip_html(availability))

    return {
        "snapshot_time": snapshot_time,
        "site": raw.get("site") or "books",
        "product_id": product_id,
        "name": name,
        "category": raw.get("category"),        # remains None for this dataset
        "price": raw.get("price"),
        "orig_price": raw.get("orig_price"),
        "currency": currency,
        "availability": availability,
        "url": url,
        "source_url": raw.get("source_url"),
    }


def main() -> None:
    raw_dir = project_path("data", "raw")
    snapshots = sorted(raw_dir.glob("snapshot_books_*.json"))

    if not snapshots:
        print("[WARN] No snapshot_books_*.json found in data/raw. Run get_data.py first.")
        return

    rows: list[dict] = []

    # ------------------------------------------------------------
    # 1. Load all raw snapshots and normalize records
    # ------------------------------------------------------------
    for path in snapshots:
        data = read_json(path)
        snapshot_time = data.get("snapshot_time")
        for item in data.get("items", []):
            rows.append(normalize_record(item, snapshot_time))

    if not rows:
        print("[WARN] No items found in raw snapshots. Nothing to clean.")
        return

    df = pd.DataFrame(rows)

    # ------------------------------------------------------------
    # 2. Handle missing values
    #    - Drop rows without a product name or price (critical fields)
    #    - Fill missing currency with a default value
    #    - Fill missing availability with a label
    # ------------------------------------------------------------
    before_rows = len(df)
    df = df.dropna(subset=["name", "price"]).copy()
    after_rows = len(df)
    print(f"[INFO] Dropped {before_rows - after_rows} rows with missing name or price.")

    df["currency"] = df["currency"].fillna("GBP")
    df["availability"] = df["availability"].fillna("Unknown")

    # ------------------------------------------------------------
    # 3. Remove duplicate records
    #    We treat (site, url) as a unique product snapshot.
    # ------------------------------------------------------------
    before_dups = len(df)
    df = df.drop_duplicates(subset=["site", "url", "snapshot_time"]).reset_index(drop=True)
    after_dups = len(df)
    print(f"[INFO] Removed {before_dups - after_dups} duplicate rows.")

    # ------------------------------------------------------------
    # 4. Ensure types are consistent
    # ------------------------------------------------------------
    df["snapshot_time"] = pd.to_datetime(df["snapshot_time"], utc=True, errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["orig_price"] = pd.to_numeric(df["orig_price"], errors="coerce")

    # Sort for reproducibility
    df = df.sort_values(["site", "product_id", "snapshot_time"]).reset_index(drop=True)

    # ------------------------------------------------------------
    # 5. Save cleaned, structured data as JSON and CSV
    # ------------------------------------------------------------
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Convert Timestamp to ISO string so that json can serialize it
    if pd.api.types.is_datetime64_any_dtype(df["snapshot_time"]):
        df["snapshot_time"] = df["snapshot_time"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # JSON: list of plain Python dicts (structured format)
    records = df.to_dict(orient="records")
    write_json(OUT_JSON, records)
    print(f"[OK] Wrote structured JSON -> {OUT_JSON} with {len(records)} records.")

    # CSV: convenient for later analysis in pandas
    df.to_csv(OUT_CSV, index=False)
    print(f"[OK] Wrote cleaned CSV -> {OUT_CSV} with {len(df)} rows.")


if __name__ == "__main__":
    main()
