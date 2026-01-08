from utils.driver import start_browser, close_browser
from utils.data_loader import load_json, load_csv, load_excel
from pages.login_page import LoginPage

def run_login_test(record, page):
    username = record["username"]
    password = record["password"]
    expected = record["expected"]

    login = LoginPage(page)
    login.goto()
    login.login(username, password)

    result = login.is_login_successful()

    if expected == "pass":
        assert result, f"[FAIL] Expected PASS but FAILED for: {username}/{password}"
        print(f"[PASS] Login Passed for {username}")
    else:
        assert not result, f"[FAIL] Expected FAIL but PASSED for: {username}/{password}"
        print(f"[PASS] Login Failed as expected for {username}")

def test_datadriven():
    pw, browser, page = start_browser()

    try:
        print("\nRunning JSON dataset...")
        for record in load_json("data/logins.json"):
            run_login_test(record, page)

        print("\nRunning CSV dataset...")
        for record in load_csv("data/logins.csv"):
            run_login_test(record, page)

        print("\nRunning Excel dataset...")
        for record in load_excel("data/logins.xlsx"):
            run_login_test(record, page)

    finally:
        close_browser(pw, browser)
if __name__ == "__main__":
    test_datadriven()