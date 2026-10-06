import logging
import time
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from scrapers.base_scraper import create_session

logger = logging.getLogger(__name__)

class QuotesScraper:
    SOURCE_NAME = "Quotes to Scrape"
    START_URL = "https://quotes.toscrape.com/"

    def __init__(self, session: requests.Session | None = None, request_delay: float = 0.5):
        self.session = session or create_session()
        self.request_delay = request_delay

    def _parse_quote(self, quote_div, page_url: str) -> dict:
        text_elem = quote_div.select_one("span.text")
        author_elem = quote_div.select_one("small.author")
        tags_elems = quote_div.select("a.tag")
        author_link = quote_div.select_one("a[href^='/author/']")

        quote_text = text_elem.get_text() if text_elem else None
        author_text = author_elem.get_text() if author_elem else None
        tag_list = [tag.get_text().strip() for tag in tags_elems if tag.get_text()]
        source_url = urljoin(page_url, author_link["href"]) if author_link and author_link.get("href") else page_url

        return {
            "source": self.SOURCE_NAME,
            "source_url": source_url,
            "name_or_title": quote_text,
            "category": "Quotes",
            "price": None,
            "rating": None,
            "author": author_text,
            "tags": ";".join(tag_list) if tag_list else None,
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
            quote_divs = soup.select("div.quote")

            for qdiv in quote_divs:
                try:
                    record = self._parse_quote(qdiv, url)
                    raw_records.append(record)
                except Exception as parse_err:
                    logger.warning("[%s] Error parsing quote element on page %d: %s", self.SOURCE_NAME, page_num, parse_err)

            next_elem = soup.select_one("li.next > a")
            url = urljoin(url, next_elem["href"]) if next_elem and next_elem.get("href") else None
            page_num += 1
            time.sleep(self.request_delay)

        logger.info("[%s] Crawl complete. Total records collected: %d", self.SOURCE_NAME, len(raw_records))
        return raw_records
