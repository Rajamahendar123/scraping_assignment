import hashlib
import re

def make_fingerprint(rec: dict) -> str:
    """Builds a SHA-256 hash across normalized text to detect duplicates regardless of case/punctuation."""
    source = rec.get("source") or ""
    name = rec.get("name_or_title") or ""
    author = rec.get("author") or ""

    if source == "Books to Scrape":
        key = f"{source} {name}"
    else:
        key = f"{source} {author} {name[:50]}"

    key = re.sub(r"[^\w\s]", "", key.lower())
    key = " ".join(key.split())
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def find_duplicates(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Splits records into unique and duplicate sets."""
    seen = set()
    unique = []
    dupes = []

    for rec in records:
        fp = make_fingerprint(rec)
        if fp in seen:
            dupes.append(rec)
        else:
            seen.add(fp)
            unique.append(rec)

    return unique, dupes