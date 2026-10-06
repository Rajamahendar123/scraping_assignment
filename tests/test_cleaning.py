from processing.cleaning import (
    clean_text,
    strip_quotes,
    clean_price,
    clean_rating,
    clean_tags,
    normalize_url
)

def test_clean_text():
    assert clean_text("  Extra   spaces \n\t and non-breaking\xa0space  ") == "Extra spaces and non-breaking space"
    assert clean_text("") is None
    assert clean_text(None) is None

def test_strip_quotes():
    assert strip_quotes("“The journey of a thousand miles begins with one step.”") == "The journey of a thousand miles begins with one step."
    assert strip_quotes('"Plain quotes"') == "Plain quotes"
    assert strip_quotes("‘Smart quotes’") == "Smart quotes"

def test_clean_price():
    assert clean_price("£51.77") == 51.77
    assert clean_price("1,249.99 €") == 1249.99
    assert clean_price("Free") is None
    assert clean_price(None) is None

def test_clean_rating():
    assert clean_rating("star-rating Three") == 3
    assert clean_rating("Five") == 5
    assert clean_rating("One") == 1
    assert clean_rating("Zero") is None

def test_clean_tags():
    assert clean_tags("books; inspiration; books; life") == "books;inspiration;life"
    assert clean_tags("") is None
    assert clean_tags(None) is None

def test_normalize_url():
    assert normalize_url("https://quotes.toscrape.com/author/Albert-Einstein") == "https://quotes.toscrape.com/author/Albert-Einstein"
    assert normalize_url("relative/path/page.html") is None
    assert normalize_url("") is None
