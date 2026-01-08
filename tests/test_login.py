from utils.driver import start_browser, close_browser
from pages.login_page import LoginPage
from utils.ai_helper import analyze_failure

def test_login():
    pw, browser, page = start_browser()

    try:
        login = LoginPage(page)
        login.goto()
        login.login("tomsmith", "SuperSecretPassword!")   # intentionally wrong to see failure AI report
        
        assert login.is_login_successful()

        print("[PASS] Login Test Passed!")

    except Exception as e:
        print("[FAIL] Login Test Failed:", e)
        ss_path = "screenshots/login_failure.png"
        page.screenshot(path=ss_path)

        html_snippet = page.content()[:3000]
        # write bug report
        from utils.bug_reporter import write_bug_report
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

        # call AI analysis (already done inside write_bug_report)
        raise
    finally:
        close_browser(pw, browser)


if __name__ == "__main__":
    test_login()
