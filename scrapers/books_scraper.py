import logging
import time
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from scrapers.base_scraper import create_session

logger = logging.getLogger(__name__)

class BooksScraper:
    SOURCE_NAME = "Books to Scrape"
    START_URL = "https://books.toscrape.com/catalogue/page-1.html"

    def __init__(self, session: requests.Session | None = None, request_delay: float = 0.5):
        self.session = session or create_session()
        self.request_delay = request_delay

    def _parse_article(self, article, page_url: str) -> dict:
        link_elem = article.select_one("h3 > a")
        price_elem = article.select_one("p.price_color")
        rating_elem = article.select_one("p.star-rating")

        title = link_elem.get("title") if link_elem and link_elem.get("title") else None
        href = link_elem.get("href") if link_elem else None
        abs_url = urljoin(page_url, href) if href else page_url
        price_raw = price_elem.get_text() if price_elem else None
        rating_raw = " ".join(rating_elem.get("class", [])) if rating_elem else None

        return {
            "source": self.SOURCE_NAME,
            "source_url": abs_url,
            "name_or_title": title,
            "category": None,
            "price": price_raw,
            "rating": rating_raw,
            "author": None,
            "tags": None,
            "description": None,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    def scrape(self, max_pages: int | None = None) -> list[dict]:
        url = self.START_URL
        page_num = 1
        raw_records = []

        logger.info("Starting scrape for source: %s", self.SOURCE_NAME)
        while url:
            if max_pages and page_num > max_pages:
                logger.info("[%s] Reached maximum allowed pages (%d). Stopping.", self.SOURCE_NAME, max_pages)
                break

            logger.info("[%s] Fetching page %d: %s", self.SOURCE_NAME, page_num, url)
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                response.encoding = "utf-8"
            except requests.RequestException as exc:
                logger.error("[%s] Network error on page %d (%s): %s", self.SOURCE_NAME, page_num, url, exc)
                break

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.select("article.product_pod")

            for article in articles:
                try:
                    record = self._parse_article(article, url)
                    raw_records.append(record)
                except Exception as parse_err:
                    logger.warning("[%s] Error parsing book element on page %d: %s", self.SOURCE_NAME, page_num, parse_err)

            next_elem = soup.select_one("li.next > a")
            url = urljoin(url, next_elem["href"]) if next_elem and next_elem.get("href") else None
            page_num += 1
            time.sleep(self.request_delay)

        logger.info("[%s] Crawl complete. Total records collected: %d", self.SOURCE_NAME, len(raw_records))
        return raw_records
