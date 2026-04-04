import allure
import pytest


@allure.epic('Тестирование работы с юзерами')
class TestUser:
    @allure.feature('Тестирование auth API на взаимодействие '
                    'с юзерами с позиции супер-админа')
    @allure.story('Создание нового пользователя супер-админом')
    def test_create_user(self, super_admin, creation_user_data):
        with allure.step(
                'API-запрос на создание простого юзера супер-админом'):
            response = super_admin.api.user_api.create_user(
                creation_user_data).json()

        with allure.step('Проверяем правильность ответа от API'):
            assert response.get('id') and response['id'] != '', (
                'ID должен быть не пустым')
            assert response.get('email') == creation_user_data.email
            assert response.get('fullName') == creation_user_data.fullName
            assert (response.get('roles', []) == [
                role.value for role in creation_user_data.roles])
            assert response.get('verified') is True

    @allure.story('Получение данных о юзере через почту супер-админом')
    def test_get_user_by_locator(self, super_admin, creation_user_data):
        with allure.step(
                'API-запрос на создание простого юзера супер-админом'):
            created_user_response = super_admin.api.user_api.create_user(
                creation_user_data).json()
        with allure.step(
                'Забираем id и email из ответа'):
            response_by_id = super_admin.api.user_api.get_user(
                created_user_response['id']).json()
            response_by_email = super_admin.api.user_api.get_user(
                creation_user_data.email).json()

        with allure.step('Проверяем правильность ответа от API'):
            assert response_by_id == response_by_email, (
                'Содержание ответов должно быть идентичным')
            assert response_by_id.get('id') and response_by_id['id'] != '', (
                'ID должен быть не пустым')
            assert response_by_id.get('email') == creation_user_data.email

            fullname = creation_user_data.fullName
            assert response_by_id.get('fullName') == fullname
            assert response_by_id.get('roles', []) == [
                role.value for role in creation_user_data.roles]
            assert response_by_id.get('verified') is True

    @allure.story('Получение данных о юзере через id простым пользователем')
    @pytest.mark.slow
    def test_get_user_by_id_common_user(self, common_user):
        with allure.step('GET-запрос на информацию о пользователе по почте'):
            common_user.api.user_api.get_user(common_user.email,
                                              expected_status=403)
