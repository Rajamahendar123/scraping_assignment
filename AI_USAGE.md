# AI Usage Report

## 1. AI Tools Used
- Tool: Gemini / ChatGPT
- Scope: Project architecture scaffolding, regex design for currency/quote cleaning, urllib3 retry adapter configuration, and pytest test suite creation.

## 2. Representative Prompts
1. "Write a requests.Session setup with urllib3 Retry configured for status codes 429, 500, 502, 503, 504 and exponential backoff."
2. "Provide a Python regex and normalization function that generates a SHA-256 fingerprint ignoring spaces, capitalization, and punctuation for book titles and quotes."
3. "Write unit test cases using pytest for validating numeric ranges, missing fields, and URL structures on dictionary records without making internet requests."

## 3. Code Portions Assisted & Refinements Made
- Encoding Issue: Explicitly configured response.encoding = 'utf-8' to prevent currency symbol corruption.
- BeautifulSoup Attribute Type: Resolved list vs string return types when extracting star-rating class names.
- Parser Fallback: Switched from lxml to Python's built-in html.parser to ensure zero dependency on C++ build tools on Windows.
- Deduplication Enhancements: Enhanced fingerprint generation to strip unicode spaces and punctuation.

## 4. Verification & Testing
- Ran pytest test suite with 100% pass rate.
- Executed python main.py end-to-end to verify that summary_report.json matches final_dataset.csv row counts.