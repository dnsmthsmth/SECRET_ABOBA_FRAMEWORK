import allure
import pytest

from api.api_manager import ApiManager
from models.pydantic_models import RegisterUserResponse


@pytest.mark.api
@allure.epic('Тестирование auth API')
class TestAuthAPI:
    @pytest.mark.slow
    @allure.story('Регистрация нового пользователя')
    def test_register_user(self, api_manager: ApiManager, creation_user_data):
        with allure.step(
                'Регистрируем юзера с данными из фикстуры {creation_user_data}'
        ):
            response = api_manager.auth_api.register_user(
                user_data=creation_user_data)
            register_user_response = RegisterUserResponse(**response.json())

        with allure.step(
                'Проверяем, что почта созданного юзера совпадает с ожидаемой'):
            assert register_user_response.email == creation_user_data.email, (
                'Email не совпадает')
