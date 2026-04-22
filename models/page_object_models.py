import allure
from playwright.sync_api import Page


class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста '{text}' в поле '{locator}'")
    def enter_text_to_element(self, locator: str, text: str):
        self.page.fill(locator, text)

    @allure.step("Клик по элементу '{locator}'")
    def click_element(self, locator: str):
        self.page.click(locator)

    @allure.step("Ожидание загрузки страницы: {url}")
    def wait_redirect_for_url(self, url: str):
        self.page.wait_for_url(url)
        assert self.page.url == url, (
            "Редирект на домашнюю страницу не произошел")

    @allure.step("Получение текста элемента: {locator}")
    def get_element_text(self, locator: str) -> str:
        return self.page.locator(locator).text_content()

    @allure.step(
        "Ожидание появления или исчезновения элемента")
    def wait_for_element(self, locator: str, state: str = "visible"):
        self.page.locator(locator).wait_for(state=state)

    @allure.step("Скриншот текущей страиницы")
    def make_screenshot_and_attach_to_allure(self):
        screenshot_path = "ui_screenshots/screenshot.png"
        self.page.screenshot(path=screenshot_path,
                             full_page=True)

        with open(screenshot_path, "rb") as file:
            allure.attach(file.read(), name="Screenshot after redirect",
                          attachment_type=allure.attachment_type.PNG)

    @allure.step("Проверка всплывающего сообщения c текстом: {text}")
    def check_pop_up_element_with_text(self, text: str) -> bool:
        with allure.step("Проверка появления алерта с текстом: '{text}'"):
            notification_locator = self.page.get_by_text(text)
            notification_locator.wait_for(state="visible")
            assert notification_locator.is_visible(), (
                "Уведомление не появилось")

        with allure.step("Проверка исчезновения алерта с текстом: '{text}'"):
            notification_locator.wait_for(state="hidden")
            assert notification_locator.is_visible() is False, (
                "Уведомление не исчезло")


class BasePage(PageAction):
    def __init__(self, page: Page):
        super().__init__(page)
        self.home_url = "https://dev-cinescope.coconutqa.ru/"

        self.home_button = "a[href='/']"
        self.all_movies_button = "a[href='/movies']"

    @allure.step("Переход на главную страницу, из шапки сайта")
    def go_to_home_page(self):
        self.click_element(self.home_button)
        self.wait_redirect_for_url(self.home_url)

    @allure.step("Переход на страницу 'Все фильмы, из шапки сайта'")
    def go_to_all_movies(self):
        self.click_element(self.all_movies_button)
        self.wait_redirect_for_url(f"{self.home_url}movies")

    def reload(self):
        self.page.reload()


class CinescopeLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}login"

        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"

        self.login_button = "button[type='submit']:has-text('Войти')"
        self.register_button = "a[href='/register']:has-text('Зарегистрироваться')"

    def open(self):
        self.open_url(self.url)

    def login(self, email: str, password: str):
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.email_input, email)
        self.click_element(self.login_button)

    def assert_was_redirect_to_home_page(self):
        self.wait_redirect_for_url(self.home_url)

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Вы вошли в аккаунт")


class CinescopeRegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}register"

        # Локаторы элементов
        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"

        self.register_button = "button[type='submit']:has-text('Зарегистрироваться')"
        self.login_button = "a[href='/login']:has-text('Войти')"

    # Локальные action методы
    def open(self):
        self.open_url(self.url)

    def register(self, full_name: str, email: str, password: str,
                 confirm_password: str):
        self.enter_text_to_element(self.full_name_input, full_name)
        self.enter_text_to_element(self.email_input, email)
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.repeat_password_input,
                                   confirm_password)

        self.click_element(self.register_button)

    def wait_redirect_to_login_page(self):
        self.wait_redirect_for_url(f"{self.home_url}login")

    def check_allert(self):
        self.check_pop_up_element_with_text("Подтвердите свою почту")


class MoviePage(BasePage):
    def __init__(self, page: Page, movie_id: int = 2434):
        super().__init__(page)
        self.url = f"{self.home_url}movies/{movie_id}"

        self.comment_textarea = "textarea[placeholder='Написать отзыв']"
        self.rating_list = "button[role='combobox']"
        self.send_button = "button[type='submit']:has-text('Отправить')"

    def open(self):
        self.open_url(self.url)

    def leave_comment(
            self, comment_text: str = 'aqa test', rating_option: str = 4):
        self.enter_text_to_element(self.comment_textarea, comment_text)
        self.click_element(self.rating_list)
        self.page.get_by_role("option", name=rating_option).click()
        self.click_element(self.send_button)

    def check_alert(self):
        self.check_pop_up_element_with_text("Отзыв успешно создан")

    def check_if_comment_exists(
            self,
            user,
            comment_text: str = 'aqa test',
            rating: str = '4'
    ):
        self.page.reload()

        comment_locator = (
           self.page.locator("li")
           .filter(has=self.page.locator(f"h4:has-text('{user.fullName}')"))
           .filter(has=self.page.locator(f"p:has-text('{comment_text}')"))
           .filter(has=self.page.locator(f"span.underline:has-text('{rating}/5')"))
        )

        assert comment_locator.count() == 1, (
           f'Не найден созданный комментарий ({comment_text} '
           f'от пользователя {user.fullName}) на странице {self.url}'
        )
