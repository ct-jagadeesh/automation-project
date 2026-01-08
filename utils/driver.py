import os
from playwright.sync_api import sync_playwright

def start_browser(headless=None):
    # ALWAYS headless in CI
    if os.getenv("CI") == "true":
        headless = True
    elif headless is None:
        headless = False  # visible locally

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    page = browser.new_page()
    return pw, browser, page

def close_browser(pw, browser):
    browser.close()
    pw.stop()
