# tests/test_api_ui_hybrid.py
import requests
from utils.driver import start_browser, close_browser
from utils.ai_helper import analyze_failure

API_URL = "https://jsonplaceholder.typicode.com/posts/1"
PAGE_URL = "https://jsonplaceholder.typicode.com/posts/1"  # JSON rendered as page

def test_api_ui_consistency():
    # 1) Call API
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        api_json = r.json()
        api_title = api_json.get("title", "").strip()
        print("API title:", api_title)
    except Exception as e:
        print("API call failed:", e)
        raise

    # 2) Open page with Playwright and get visible text
    pw, browser, page = start_browser(headless=False)
    try:
        page.goto(PAGE_URL, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)
        page_text = page.inner_text("body") if page.locator("body").count() > 0 else page.content()
        # normalize small whitespace differences
        page_text_norm = " ".join(page_text.split())
        print("Page text snippet:", page_text_norm[:200])

        # 3) Assert title appears in page text
        if api_title and api_title in page_text_norm:
            print("[PASS] API title appears on page")
            close_browser(pw, browser)
            return True
        else:
            error_message = f"Title mismatch. API='{api_title}'"
            print("[FAIL]", error_message)
            # save screenshot for bug report
            page.screenshot(path="screenshots/api_ui_mismatch.png")
            html_snippet = page.content()[:3000]
            ai_report = analyze_failure(error_message, html_snippet)
            print("\n--- AI Analysis ---\n", ai_report, "\n--- End AI Analysis ---\n")
            raise AssertionError(error_message)

    finally:
        close_browser(pw, browser)

if __name__ == "__main__":
    test_api_ui_consistency()
