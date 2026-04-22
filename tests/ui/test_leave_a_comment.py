import allure
import pytest
from playwright.sync_api import sync_playwright

from models.page_object_models import CinescopeLoginPage, MoviePage


@allure.epic("Тестирование UI")
@allure.feature("Тестирование страницы фильма")
@pytest.mark.ui
class TestLeaveAComment:
    @allure.title("Оставление отзыва о фильме")
    def test_leave_a_comment(
            self,
            common_user,
            creation_user_data,
            random_movie_id,
            comment_data):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            login_page = CinescopeLoginPage(page)
            login_page.open()
            login_page.login(common_user.email,
                             common_user.password)
            login_page.assert_was_redirect_to_home_page()

            movie_page = MoviePage(page=page, movie_id=random_movie_id)
            movie_page.open()

            movie_page.leave_comment(
                comment_text=comment_data['comment_text'],
                rating_option=comment_data['comment_rating'])

            movie_page.check_alert()

            movie_page.check_if_comment_exists(
                creation_user_data,
                comment_text=comment_data['comment_text'],
                rating=comment_data['comment_rating'])

            browser.close()
