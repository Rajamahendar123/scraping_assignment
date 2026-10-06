from processing.deduplication import find_duplicates

def test_deduplication_variations():
    records = [
        {"source": "Books to Scrape", "name_or_title": "Example Book Title", "author": None},
        {"source": "Books to Scrape", "name_or_title": "  Example Book Title ", "author": None},
        {"source": "Books to Scrape", "name_or_title": "EXAMPLE BOOK TITLE", "author": None},
        {"source": "Books to Scrape", "name_or_title": "Different Title", "author": None},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 2
    assert len(dupes) == 2
    assert unique[0]["name_or_title"] == "Example Book Title"
    assert unique[1]["name_or_title"] == "Different Title"
