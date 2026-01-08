import os
from playwright.sync_api import sync_playwright

def start_browser(headless=None):
    # Force headless in CI, allow headed locally
    if headless is None:
        headless = os.getenv("CI", "false").lower() == "true"

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    page = browser.new_page()
    return pw, browser, page

def close_browser(pw, browser):
    browser.close()
    pw.stop()
