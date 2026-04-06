import allure
import pytest


@pytest.mark.db
@allure.epic('Тестирование базы данных movies')
class TestMovieDbPositive:
    @pytest.mark.slow
    @allure.story('Добавление фильма в базу данных')
    def test_db_add_movie(
            self,
            super_admin,
            db_helper,
            created_test_film
    ):
        """Создает фильм в БД, после проверок фильм автоматически удаляется"""
        with allure.step(
            'Проверяем, что отправленные данные совпадают с данными в БД'
        ):
            assert created_test_film == db_helper.get_movie_by_id(
                created_test_film.id)
        with allure.step(
            'Проверяем, что фильм находится в БД по имени'
        ):
            assert db_helper.get_movie_by_name(created_test_film.name)
