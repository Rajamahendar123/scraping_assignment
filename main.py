import argparse
import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import time

from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from processing.cleaning import clean_record
from processing.validation import validate_record
from processing.deduplication import find_duplicates

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "scraper.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def parse_args():
    parser = argparse.ArgumentParser(description="Multi-Source Web Scraping ETL Pipeline")
    parser.add_argument("--source", choices=["all", "books", "quotes"], default="all",
                        help="Select sources to crawl (default: all)")
    parser.add_argument("--max-pages", type=int, default=None,
                        help="Limit number of pages scraped per source (useful for quick verification)")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Politeness delay in seconds between requests (default: 0.5)")
    return parser.parse_args()

def run_pipeline():
    args = parse_args()
    setup_logging()
    logger = logging.getLogger("main_pipeline")
    logger.info("=== Starting Multi-Source ETL Pipeline ===")

    start_time = time.time()
    raw_records = []
    collected_counts = {"Books to Scrape": 0, "Quotes to Scrape": 0}

    # 1. Scrape Stage
    if args.source in ("all", "books"):
        try:
            books_data = BooksScraper(request_delay=args.delay).scrape(max_pages=args.max_pages)
            raw_records.extend(books_data)
            collected_counts["Books to Scrape"] = len(books_data)
        except Exception as exc:
            logger.error("Error scraping Books to Scrape: %s", exc)

    if args.source in ("all", "quotes"):
        try:
            quotes_data = QuotesScraper(request_delay=args.delay).scrape(max_pages=args.max_pages)
            raw_records.extend(quotes_data)
            collected_counts["Quotes to Scrape"] = len(quotes_data)
        except Exception as exc:
            logger.error("Error scraping Quotes to Scrape: %s", exc)

    # 2. Cleaning Stage
    logger.info("Standardizing %d raw records...", len(raw_records))
    cleaned_records = [clean_record(r) for r in raw_records]
    cleaned_counts = {
        "Books to Scrape": sum(1 for r in cleaned_records if r.get("source") == "Books to Scrape"),
        "Quotes to Scrape": sum(1 for r in cleaned_records if r.get("source") == "Quotes to Scrape")
    }

    # 3. Validation Stage
    logger.info("Validating cleaned records...")
    valid_records = []
    rejected_records = []
    rejection_reasons = {}

    for rec in cleaned_records:
        problems = validate_record(rec)
        if problems:
            rejected_records.append(rec)
            for prob in problems:
                rejection_reasons[prob] = rejection_reasons.get(prob, 0) + 1
            logger.warning("Rejected record [%s]: %s | Issues: %s", rec.get("source"), rec.get("name_or_title"), problems)
        else:
            valid_records.append(rec)

    # 4. Deduplication Stage
    logger.info("Running deduplication on %d valid records...", len(valid_records))
    unique_records, duplicate_records = find_duplicates(valid_records)
    logger.info("Deduplication result: %d unique records, %d duplicate(s) filtered.",
                len(unique_records), len(duplicate_records))

    # 5. Output Stage
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / "final_dataset.csv"
    json_path = output_dir / "summary_report.json"

    fieldnames = [
        "source",
        "source_url",
        "name_or_title",
        "category",
        "price",
        "rating",
        "author",
        "tags",
        "description",
        "scraped_at"
    ]

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(unique_records)
    logger.info("Saved final consolidated dataset to %s", csv_path)

    duration = round(time.time() - start_time, 2)
    summary_stats = {
        "collected_per_source": collected_counts,
        "cleaned_per_source": cleaned_counts,
        "rejected_by_reason": rejection_reasons,
        "total_rejected": len(rejected_records),
        "duplicates_detected": len(duplicate_records),
        "final_record_count": len(unique_records),
        "execution_start_utc": datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat(),
        "execution_end_utc": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": duration
    }

    with open(json_path, mode="w", encoding="utf-8") as f:
        json.dump(summary_stats, f, indent=4)
    logger.info("Saved summary report to %s", json_path)
    logger.info("=== Pipeline Completed in %s seconds ===", duration)

if __name__ == "__main__":
    run_pipeline()