# book_price_analysis_project
An end-to-end data pipeline that scrapes, cleans, analyzes, and visualizes book prices from a public website using Python.
1. Project Overview

This project collects, cleans, analyzes, and visualizes book price data from an online bookstore.
All data were obtained via Python web scraping (no pre-downloaded datasets), fulfilling the course requirement for automated data collection.

The project demonstrates a complete data pipeline:

Data Collection — Web scraping using requests + BeautifulSoup

Data Cleaning — Removing HTML artifacts, handling missing values, ensuring type consistency

Data Analysis — Descriptive statistics using NumPy and Pandas

Data Visualization — Plotting distributions and comparisons using Matplotlib

This repository contains all scripts necessary to reproduce the workflow.

2. Data Source

The data were collected from:

 http://books.toscrape.com/

A publicly available demo bookstore website designed for web scraping practice.

Data fields extracted include:

Product ID
Book title
Product page URL
Price
Rating
Category
Snapshot timestamp
Raw HTML pages are parsed and saved as JSON snapshots.

3. Project Structure
│
├── data/
│   ├── raw/                
│   └── processed/          
│
├── results/
│   ├── hist_price.png
│   ├── boxplot_price.png
│   ├── top10_books.png
│   ├── summary_stats.json
│   └── metrics_by_product.csv
│
├── src/
│   ├── get_data.py         ← Web scraping script
│   ├── clean_data.py       ← Data cleaning & structuring
│   ├── run_analysis.py     ← Descriptive statistics
│   └── visualize_results.py← Matplotlib plots
│
├── utils/
│   └── io_helpers.py       ← Path + JSON helper utilities
│
├── README.md
└── requirements.txt


4.Step 1: Create & Activate Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

Step 2: Install Dependencies
pip install -r requirements.txt

Step 3: Run the Web Scraper
python src/get_data.py


This script will:

Fetch multiple book listing pages

Extract titles, prices, ratings, categories

Save raw JSON snapshots into data/raw/

Step 4: Clean the Data
python src/clean_data.py


This will:

Parse raw HTML into structured records

Remove duplicates and missing values

Convert price to numeric

Save:

data/processed/books_clean.json

data/processed/prices.csv

Step 5: Run Statistical Analysis
python src/run_analysis.py


Outputs:

summary_stats.json — mean, median, std, percentiles

metrics_by_product.csv — grouped stats (per book)

Step 6: Generate Plots
python src/visualize_results.py


Creates:

hist_price.png — price distribution

boxplot_price.png — variation & outliers

top10_books.png — most expensive books

5. Results Summary
Global Price Statistics Example:
{
  "count": 2000,
  "mean": 35.07,
  "median": 33.0,
  "std": 14.43,
  "min": 10.0,
  "max": 99.0,
  "p25": 22.16,
  "p75": 47.45
}

Visualizations Produced:

✔ Histogram (price distribution)

✔ Boxplot (spread & outliers)

✔ Top 10 most expensive books

All located in results/.

6. Technologies Used:

Python 3.10+
requests,BeautifulSoup4,pandas,numpy,matplotlib,json,pathlib



