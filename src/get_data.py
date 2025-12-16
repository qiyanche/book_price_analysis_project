from __future__ import annotations

import json
import random
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from utils.io_helpers import project_path, write_json

"""
Data Source:
-----------
Books to Scrape (http://books.toscrape.com/) is a purposely designed
static e-commerce website for practicing web scraping.

Because it serves static HTML (no JavaScript rendering), it is ideal
for DSCI 510 course projects that require using requests + BeautifulSoup.
"""

BASE_URL = "http://books.toscrape.com/catalogue/"
START_PAGE = 1
MAX_PAGES = 50  # maximum number of pages to attempt


# Request headers used to mimic a real browser
HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


# Random delay to avoid sending requests too quickly
REQUEST_DELAY_SEC = (1.0, 2.0)


def fetch(url: str) -> Optional[str]:
    """
    Send an HTTP GET request and return HTML text if successful.
    Returns None if the request fails or server responds with an error code.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.text
        print(f"[WARN] {url} -> HTTP {resp.status_code}")
        return None
    except requests.RequestException as e:
        print(f"[ERROR] {url} -> {e}")
        return None


def parse_book_list(html: str, page_url: str) -> List[Dict[str, Any]]:
    """
    Parse a single book listing page.

    The HTML structure of each book item is roughly:

        <article class="product_pod">
            <h3>
                <a title="Book Title" href="a-light-in-the-attic_1000/index.html"></a>
            </h3>
            <p class="price_color">£51.77</p>
            <p class="instock availability">In stock (19 available)</p>
        </article>

    Returns a list of dictionaries containing book metadata.
    """
    soup = BeautifulSoup(html, "lxml")
    items: List[Dict[str, Any]] = []

    products = soup.select("article.product_pod")
    if not products:
        print(f"[INFO] No product pods found on {page_url}")
        return items

    for art in products:
        # Extract name and product page URL
        a_tag = art.find("h3").find("a")
        name = a_tag.get("title") or a_tag.get_text(strip=True)
        href = a_tag.get("href")

        # Convert relative URL to absolute
        if href.startswith("http"):
            url = href
        else:
            url = BASE_URL + href.lstrip("./")

        # Extract price text “£51.77”
        price_text = ""
        price_tag = art.find("p", class_="price_color")
        if price_tag:
            price_text = price_tag.get_text(strip=True)

        price = None
        if price_text:
            m = re.search(r"(\d+[\.,]?\d*)", price_text)
            if m:
                price = float(m.group(1).replace(",", ""))

        # Extract availability information
        availability = ""
        avail_tag = art.find("p", class_="instock")
        if avail_tag:
            availability = avail_tag.get_text(strip=True)

        items.append(
            {
                "site": "books",
                "name": name,
                "url": url,
                "price": price,
                "orig_price": None,        # This website does not show original prices
                "currency": "GBP",
                "availability": availability,
                "category": None,          # Category is not available on this listing page
                "source_url": page_url,
            }
        )

    print(f"[INFO] Parsed {len(items)} books from {page_url}")
    return items


def scrape() -> Dict[str, Any]:
    """
    Loop through listing pages until:
    - no HTML is returned, or
    - no products are found on the page.

    Returns a snapshot dictionary that includes:
    - snapshot_time (UTC)
    - items (all scraped books)
    """
    snapshot_time = datetime.now(timezone.utc).isoformat()
    out: Dict[str, Any] = {"snapshot_time": snapshot_time, "items": []}

    for page in range(START_PAGE, MAX_PAGES + 1):

        # Construct the URL for each page
        if page == 1:
            url = BASE_URL + "page-1.html"
        else:
            url = BASE_URL + f"page-{page}.html"

        print(f"[INFO] Fetching page {page}: {url}")
        html = fetch(url)
        time.sleep(random.uniform(*REQUEST_DELAY_SEC))

        if not html:
            print(f"[INFO] Stopping at page {page}: no HTML content.")
            break

        items = parse_book_list(html, url)
        if not items:
            print(f"[INFO] Stopping at page {page}: no products found.")
            break

        out["items"].extend(items)

    return out


def main() -> None:
    """Main entry point for scraping and saving raw JSON output."""
    data = scrape()
    date_tag = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    raw_path = project_path("data", "raw", f"snapshot_books_{date_tag}.json")
    write_json(raw_path, data)
    print(f"[OK] Wrote {len(data.get('items', []))} items -> {raw_path}")


if __name__ == "__main__":
    main()
