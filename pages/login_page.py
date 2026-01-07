class LoginPage:
    URL = "https://the-internet.herokuapp.com/login"

    def __init__(self, page):
        self.page = page
        self.username = "#username"
        self.password = "#password"
        self.login_button = "button[type='submit']"
        self.success_message = "text=You logged into a secure area!"

    def goto(self):
        self.page.goto(self.URL)

    def login(self, user, pwd):
        self.page.fill(self.username, user)
        self.page.fill(self.password, pwd)
        self.page.click(self.login_button)

    def is_login_successful(self):
        return self.page.locator(self.success_message).count() > 0
