import re
from urllib.parse import urlsplit

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}

def clean_text(value: str | None) -> str | None:
    """Collapses whitespace, newlines, tabs, and non-breaking spaces (\xa0)."""
    if value is None:
        return None
    text = " ".join(value.replace("\xa0", " ").split())
    return text if text else None

def strip_quotes(value: str | None) -> str | None:
    """Removes surrounding curly/straight quotation marks and trailing whitespace."""
    if not value:
        return None
    cleaned = value.strip(" \t\n\r\xa0\"'“”‘’")
    return clean_text(cleaned)

def clean_price(raw: str | None) -> float | None:
    """Extracts numeric price from strings containing currency indicators."""
    if not raw:
        return None
    cleaned = str(raw).replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", cleaned)
    return float(match.group()) if match else None

def clean_rating(raw: str | None) -> int | None:
    """Maps words (e.g. 'Three') to integer values [1-5]."""
    if not raw:
        return None
    for token in str(raw).lower().split():
        if token in RATING_MAP:
            return RATING_MAP[token]
    return None

def clean_tags(raw_tags: str | None) -> str | None:
    """Lowercases, deduplicates, and sorts semicolon-separated tags."""
    if not raw_tags:
        return None
    tags = [t.strip().lower() for t in raw_tags.split(";") if t.strip()]
    if not tags:
        return None
    sorted_unique_tags = sorted(list(dict.fromkeys(tags)))
    return ";".join(sorted_unique_tags)

def normalize_url(url: str | None) -> str | None:
    """Verifies complete HTTP/HTTPS URL format."""
    if not url:
        return None
    url = url.strip()
    split = urlsplit(url)
    if split.scheme in ("http", "https") and split.netloc:
        return url
    return None

def clean_record(raw: dict) -> dict:
    """Standardizes and cleans all fields of a record."""
    cleaned = dict(raw)
    cleaned["source"] = clean_text(cleaned.get("source"))
    cleaned["source_url"] = normalize_url(cleaned.get("source_url"))

    if cleaned.get("source") == "Quotes to Scrape":
        cleaned["name_or_title"] = strip_quotes(cleaned.get("name_or_title"))
    else:
        cleaned["name_or_title"] = clean_text(cleaned.get("name_or_title"))

    cleaned["category"] = clean_text(cleaned.get("category"))
    cleaned["price"] = clean_price(cleaned.get("price"))
    cleaned["rating"] = clean_rating(cleaned.get("rating"))
    cleaned["author"] = clean_text(cleaned.get("author"))
    cleaned["tags"] = clean_tags(cleaned.get("tags"))
    cleaned["description"] = clean_text(cleaned.get("description"))
    return cleaned