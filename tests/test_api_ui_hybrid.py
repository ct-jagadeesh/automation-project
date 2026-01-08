# tests/test_api_ui_hybrid.py
import requests
from utils.driver import start_browser, close_browser
from utils.driver import start_browser, close_browser
import requests

API_URL = "https://jsonplaceholder.typicode.com/posts/1"
PAGE_URL = "https://jsonplaceholder.typicode.com/posts/1"

def test_api_ui_consistency():
    # 1) API call
    r = requests.get(API_URL, timeout=10)
    r.raise_for_status()
    api_json = r.json()
    api_title = api_json.get("title", "").strip()

    print("API title:", api_title)

    pw, browser, page = start_browser()
    try:
        # 2) UI validation
        page.goto(PAGE_URL, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)

        page_text = page.inner_text("body")
        page_text_norm = " ".join(page_text.split())

        print("Page text snippet:", page_text_norm[:200])

        assert api_title in page_text_norm, "API title not found in UI"
        print("[PASS] API title appears on page")

    finally:
        # ✅ CLOSE ONLY ONCE
        close_browser(pw, browser)

if __name__ == "__main__":
    test_api_ui_consistency()
