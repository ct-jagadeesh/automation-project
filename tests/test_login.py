from utils.driver import start_browser, close_browser
from pages.login_page import LoginPage
from utils.ai_reporter import analyze_failure
from utils.bug_reporter import write_bug_report


def test_login():
    pw, browser, page = start_browser()

    try:
        login = LoginPage(page)
        login.goto()

        # Use correct credentials for normal runs
        login.login("tomsmith", "SuperSecretPassword!")

        assert login.is_login_successful()
        print("[PASS] Login Test Passed!")

    except Exception as e:
        print("[FAIL] Login Test Failed:", e)

        # 1️⃣ AI FAILURE ANALYSIS (NEW – Step 2)
        analyze_failure(e)

        # 2️⃣ Screenshot
        ss_path = "screenshots/login_failure.png"
        page.screenshot(path=ss_path)

        # 3️⃣ HTML snippet
        html_snippet = page.content()[:3000]

        # 4️⃣ Bug report
        report_path = write_bug_report(
            test_name="Login Test",
            error_message=str(e),
            screenshot_path=ss_path,
            html_snippet=html_snippet,
            extra_steps=[
                "Open https://the-internet.herokuapp.com/login",
                "Enter username tomsmith",
                "Enter password <used-in-test>",
                "Click Login"
            ]
        )

        print("Bug report saved:", report_path)

        # Important: re-raise so CI fails correctly
        raise

    finally:
        close_browser(pw, browser)


if __name__ == "__main__":
    test_login()
