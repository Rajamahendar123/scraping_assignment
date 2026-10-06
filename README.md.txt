# Multi-Source Web Scraping & Data Consolidation Pipeline

## 1. Project Overview
A production-ready ETL pipeline written in Python that extracts, cleans, standardizes, validates, and consolidates data from two public websites:
1. Books to Scrape (https://books.toscrape.com/): ~1,000 book records spanning 50 pages.
2. Quotes to Scrape (https://quotes.toscrape.com/): 100 quote records spanning 10 pages.

The pipeline combines these disparate sources into a unified tabular schema, cleans formatting quirks, validates records against business constraints, eliminates duplicate entries, and writes the output to output/final_dataset.csv along with an execution metric summary in output/summary_report.json.

## 2. Environment & Prerequisites
- Python Version: 3.10 to 3.14 compatible.
- Required Libraries: requests, beautifulsoup4, pytest.

### Installation & Virtual Environment Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

## 3. How to Run
Run the main script from the project root:
python main.py

### CLI Options (Bonus Feature)
- Limit pages per source: python main.py --max-pages 2
- Scrape a single source: python main.py --source quotes
- Adjust rate-limit delay: python main.py --delay 1.0

### Run Unit Tests
pytest

## 4. Website Observations & HTML Structure
- Books to Scrape (https://books.toscrape.com/):
  - Container element: article.product_pod
  - Title: Extracted from h3 > a['title'] attribute.
  - Price: Extracted from p.price_color.
  - Rating: Encoded as class names on p.star-rating.
  - Pagination: Navigated using li.next > a.
- Quotes to Scrape (https://quotes.toscrape.com/):
  - Container element: div.quote
  - Quote text: Stored in span.text.
  - Author: Located in small.author.
  - Tags: Extracted from a.tag links.
  - Pagination: Navigated using li.next > a.

## 5. Unified Data Model
- source: Origin website identifier
- source_url: Absolute HTTP/HTTPS URL
- name_or_title: Book title or cleaned quote text
- category: None for books, 'Quotes' for quotes
- price: Numeric float (currency symbol removed)
- rating: Integer 1 to 5
- author: Author name string (quotes only)
- tags: Semicolon-delimited, sorted, unique tags
- description: Reserved schema column
- scraped_at: Standardized ISO-8601 UTC timestamp

## 6. Pipeline Design & Strategies
- Dynamic Pagination: Resolves relative URLs using urllib.parse.urljoin until li.next > a is no longer present.
- Data Cleaning: Strips non-breaking spaces (\xa0), removes smart quotation marks, casts prices to floats, and maps rating word strings to numbers.
- Validation: Checks source recognition, presence of titles, valid URL structure, non-negative prices, and ratings within [1, 5].
- Deduplication Strategy: Computes SHA-256 hashes of lowercased, punctuation-free title/quote keys to filter duplicates.
- Error Handling & Reliability: Utilizes requests.Session with retries and exponential backoff on HTTP 429 and 500-level codes, with rate limiting.

## 7. Assumptions & Known Limitations
- Listing pages for Books to Scrape omit descriptions and categories; these remain None to avoid 1,000 extra HTTP requests.
- Both practice websites serve static unique content; deduplication logic is verified using offline mock fixtures in tests/test_deduplication.py.