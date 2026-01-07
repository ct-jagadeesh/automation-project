# tests/test_generated_from_the_internet_herokuapp_com.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def test_generated_login_smoke(headless=False):
    url = "https://the-internet.herokuapp.com/login"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            # 1) Navigate
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # 2) Verify that the username/password inputs and login button are present
            # NOTE: selectors use the real demo site's ids
            username = page.locator("#username")
            password = page.locator("#password")
            login_btn = page.locator("button[type='submit']")

            assert username.count() > 0, "Username input not found"
            assert password.count() > 0, "Password input not found"
            assert login_btn.count() > 0, "Login button not found"

            # 3) Perform login with the valid credentials
            username.fill("tomsmith")
            password.fill("SuperSecretPassword!")
            login_btn.click()

            # 4) Wait for the flash message and assert success text
            flash = page.locator("div#flash")
            flash.wait_for(state="visible", timeout=10000)
            assert "You logged into a secure area!" in flash.inner_text(), \
                f"Expected success text not found. Flash text: {flash.inner_text()}"

            print("[PASS] Generated login smoke test passed.")
            browser.close()
            return True

    except PlaywrightTimeoutError as te:
        print("[FAIL] Playwright timeout:", te)
    except AssertionError as ae:
        print("[FAIL] Assertion error:", ae)
    except Exception as e:
        print("[FAIL] Unexpected error:", e)
    return False


if __name__ == "__main__":
    ok = test_generated_login_smoke(headless=False)
    if not ok:
        raise SystemExit(1)
