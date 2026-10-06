from processing.validation import validate_record

def test_valid_book_record():
    rec = {
        "source": "Books to Scrape",
        "name_or_title": "A Light in the Attic",
        "source_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "price": 51.77,
        "rating": 3
    }
    assert validate_record(rec) == []

def test_invalid_records():
    rec_bad_price = {
        "source": "Books to Scrape",
        "name_or_title": "Invalid Price Book",
        "source_url": "https://books.toscrape.com/book.html",
        "price": -5.0,
        "rating": 4
    }
    assert "invalid_price" in validate_record(rec_bad_price)

    rec_bad_rating = {
        "source": "Books to Scrape",
        "name_or_title": "Invalid Rating Book",
        "source_url": "https://books.toscrape.com/book.html",
        "rating": 9
    }
    assert "invalid_rating" in validate_record(rec_bad_rating)

    rec_missing_name = {
        "source": "Books to Scrape",
        "name_or_title": "",
        "source_url": "https://books.toscrape.com/book.html"
    }
    assert "missing_name" in validate_record(rec_missing_name)
