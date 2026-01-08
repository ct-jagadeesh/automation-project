import requests
from utils.driver import start_browser, close_browser

USERS_API = "https://jsonplaceholder.typicode.com/users/1"
USERS_UI = "https://jsonplaceholder.typicode.com/users/1"

def test_user_api_ui_consistency():
    # 1) API
    r = requests.get(USERS_API, timeout=10)
    r.raise_for_status()
    api_user = r.json()
    api_email = api_user["email"]

    print("API email:", api_email)

    # 2) UI
    pw, browser, page = start_browser()
    try:
        page.goto(USERS_UI, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)

        body_text = page.inner_text("body")
        assert api_email in body_text

        print("[PASS] API and UI user data consistent")

    finally:
        close_browser(pw, browser)
