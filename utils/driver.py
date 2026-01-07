from playwright.sync_api import sync_playwright

def start_browser(headless=False):
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    page = browser.new_page()
    return pw, browser, page

def close_browser(pw, browser):
    try:
        browser.close()
        pw.stop()
    except:
        pass
