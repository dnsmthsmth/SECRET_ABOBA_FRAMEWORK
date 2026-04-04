import copy

import allure
import pytest

from constants import (BASE_RESPONSE_MOVIE, EXPECTED_MOVIE_GET_KEYS,
                       PATCH_VALUES)
from utils.data_generator import DataGenerator


@pytest.mark.api
@allure.epic('Тестирование movies API')
class TestMoviesUnauthenticated:
    @allure.feature('Тестирование movies API неавторизованным юзером')
    @allure.story('Добавление фильма неавторизованным юзером')
    def test_add_movie_unauthorised(
            self,
            test_film,
            unauthenticated_session
    ):
        """
        Тест на попытку создания фильма незалогиненным пользователем.
        """
        with allure.step('API-запрос на добавление фильма'):
            response = unauthenticated_session.movies_api.add_movie(
                film_data=test_film,
                expected_status=401
            )
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert response_data['message'] == 'Unauthorized', (
                f'Ожидаемое сообщение: Unauthorized \n'
                f'Полученное сообщение : {response_data.get('message')}'
            )

    @allure.story('Удаление фильма неавторизованным юзером')
    def test_delete_movie_unauthorised(
            self, test_film, unauthenticated_session
    ):
        """
        Тест на удаление фильма незалогиненным пользователем.
        Проверяется захардкоженный id 566
        """
        with allure.step('API-запрос на удаление фильма с кастомным id'):
            test_id = 566
            response = unauthenticated_session.movies_api.delete_movie(
                test_id, expected_status=401
            )
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert response_data.get('message') == 'Unauthorized', (
                f'Ожидаемое сообщение: Unauthorized \n'
                f'Полученное сообщение : {response_data.get('message')}'
            )

    @allure.story('Полный PATCH фильма неавторизованным юзером')
    def test_full_patch_movie_unauthorised(
            self, test_film, unauthenticated_session
    ):
        """
        Тест на изменение фильма незалогиненным пользователем.
        Проверяется захардкоженный id 566
        """
        with allure.step('API-запрос на изменение фильма с кастомным id'):
            movie_id = 566
            patched_data = PATCH_VALUES
            patched_data['name'] = DataGenerator.generate_random_film_name()

            response = unauthenticated_session.movies_api.patch_movie(
                movie_id, patched_data, expected_status=401
            )
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert response_data.get('message') == 'Unauthorized', (
                f'Ожидаемое сообщение: Unauthorized \n'
                f'Полученное сообщение: {response_data.get('message')}'
            )

    @allure.story('Получение всех фильмов неавторизованным юзером (GET)')
    def test_get_films_unauthorised(self, unauthenticated_session):
        """
        Тест на общий get-запрос для фильмов (без фильтров) без авторизации
        """
        with allure.step('GET-запрос на получение списка фильмов'):
            response = unauthenticated_session.movies_api.get_movies(
                expected_status=200)
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert 'movies' in response_data, (
                'Нет объекта movies в теле ответа')
            assert len(response_data.get('movies')) == 10, (
                f'Ожидаемое количество фильмов в базовом GET: 10 \n'
                f'Получено: {len(response_data.get('movies'))}'
            )

            for film in response_data.get('movies'):
                assert BASE_RESPONSE_MOVIE.issubset(film.keys()), (
                    f'GET-запрос. Неверный набор ключей. \n'
                    f'Ожидаемый: {EXPECTED_MOVIE_GET_KEYS} \n'
                    f'Полученный: {film.keys()}'
                )

            assert 'count' in response_data, 'Нет поля "count" в теле ответа'
            assert 'page' in response_data, 'Нет поля "page" в теле ответа'
            assert 'pageSize' in response_data, (
                'Нет поля "pageSize" в теле ответа')
            assert 'pageCount' in response_data, (
                'Нет поля "pageCount" в теле ответа'
            )

    @allure.story(
        'Получение фильма неавторизованным юзером с параметрами (GET)')
    @pytest.mark.parametrize('min_price,max_price,locations,genre_id', [
        (1, 100, 'MSK', 1),
        (100, 500, 'SPB', 2),
        (500, 1000, 'MSK', 3),
    ])
    def test_get_films_parametrized(self, unauthenticated_session, min_price,
                                    max_price, locations, genre_id):
        """
        Тест на общий get-запрос для фильмов с реализацией параметров.
        """
        with allure.step(
                'Генерируем фильтры из параметров и отправляем GET-запрос'):
            params = {
                'minPrice': min_price,
                'maxPrice': max_price,
                'locations': locations,
                'genreId': genre_id,
            }
            response_data = unauthenticated_session.movies_api.get_movies(
                params=params,
                expected_status=200
            ).json()

        with allure.step('Проверяем правильность ответа от API'):
            assert 'movies' in response_data, (
                'Нет объекта movies в теле ответа')
            movies = response_data['movies']
            assert len(movies) > 0, f'Нет фильмов для параметров {params}'
            assert 'count' in response_data, 'Нет поля "count" в теле ответа'
            assert response_data['page'] == 1, (
                'Выборка представлена не с первой страницы'
            )
            assert response_data['pageSize'] == 10, (
                'Размер страницы ответа отличается от значения по умолчанию'
            )
            for film in response_data.get('movies'):
                assert BASE_RESPONSE_MOVIE.issubset(film.keys()), (
                    f'GET-запрос. Неверный набор ключей в фильмах. \n'
                    f'Ожидаемый: {EXPECTED_MOVIE_GET_KEYS} \n'
                    f'Полученный: {film.keys()}'
                )
                assert min_price <= film['price'] <= max_price, (
                    'Цена фильма отличается от заданной в фильтрах'
                )
                assert locations == film['location'], (
                    'Город фильма отличается от заданного в фильтрах'
                )
                assert genre_id == film['genreId'], (
                    'Жанр фильма отличается от заданного в фильтрах'
                )


@pytest.mark.api
@allure.epic('Тестирование movies API')
class TestMoviesAdminPositive:
    @allure.feature(
        'Позитивное тестирование movies API с позиции супер-админа')
    @allure.story('Добавление фильма супер-админом')
    def test_add_movie(self, create_movie, test_film, super_admin):
        """
        Тест на создание фильма супер-админом.
        """
        with allure.step('API-запрос на добавление фильма'):
            response_data = create_movie(user=super_admin, film_data=test_film)

        with allure.step('Проверяем правильность ответа от API'):
            assert 'id' in response_data, (
                'Нет id созданного фильма в теле ответа')
            assert BASE_RESPONSE_MOVIE.issubset(response_data.keys()), (
                f'Ожидаемые поля тела ответа: {BASE_RESPONSE_MOVIE} \n'
                f'Полученные поля: {response_data.keys()}'
            )

    @allure.story('Получение конкретного фильма супер-админом')
    def test_get_film(self, api_manager, create_movie, test_film, super_admin):
        """
        Тест на создание и получение созданного фильма по его id.
        """
        with allure.step('API-запрос на добавление фильма'):
            response_data = create_movie(user=super_admin, film_data=test_film)
            movie_id = response_data.get('id')

        with allure.step('GET-запрос на получения фильма по id'):
            response = api_manager.movies_api.get_movie_by_id(
                movie_id=movie_id, expected_status=200)
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert movie_id == response_data.get('id'), (
                f'Ожидаемый id: {movie_id} \n'
                f'Полученный id: {response_data.get('id')}'
            )
            assert EXPECTED_MOVIE_GET_KEYS.issubset(response_data.keys()), (
                f'Ожидаемые поля тела ответа: {BASE_RESPONSE_MOVIE} \n'
                f'Полученные поля: {response_data.keys()}'
            )

    @allure.story('Получение всех фильмов супер-админом')
    def test_get_films(self, super_admin):
        """
        Тест на общий get-запрос для фильмов (без фильтров) супер-админом
        """
        with allure.step('Общий GET-запрос на получения фильмов'):
            response = super_admin.api.movies_api.get_movies(
                expected_status=200)
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert 'movies' in response_data, (
                'Нет объекта movies в теле ответа')
            assert len(response_data.get('movies')) == 10, (
                f'Ожидаемое количество фильмов в базовом GET: 10 \n'
                f'Получено: {len(response_data.get('movies'))}'
            )

            for film in response_data.get('movies'):
                assert BASE_RESPONSE_MOVIE.issubset(film.keys()), (
                    f'GET-запрос. Неверный набор ключей в фильмах. \n'
                    f'Ожидаемый: {EXPECTED_MOVIE_GET_KEYS} \n'
                    f'Полученный: {film.keys()}'
                )

            assert 'count' in response_data, 'Нет поля "count" в теле ответа'
            assert 'page' in response_data, 'Нет поля "page" в теле ответа'
            assert 'pageSize' in response_data, (
                'Нет поля "pageSize" в теле ответа')
            assert 'pageCount' in response_data, (
                'Нет поля "pageCount" в теле ответа'
            )

    @allure.story('Получение фильмов с параметрами супер-админом')
    def test_get_films_filtered(
            self,
            generate_get_filters,
            super_admin
    ):
        """
        Тест на общий get-запрос для фильмов со случайными фильтрами.
        """
        with allure.step(
                'Генерируем случайные фильтры фикстурой {generate_get_filters}'
        ):
            params = generate_get_filters

        with allure.step(
                'GET-запрос на получение фильмов с созданными параметрами'):
            response = super_admin.api.movies_api.get_movies(
                params=params,
                expected_status=200
            )
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert 'movies' in response_data, (
                'Нет объекта movies в теле ответа')
            page_size = params['pageSize']
            assert len(response_data.get('movies')) == page_size, (
                f'Ожидаемое количество фильмов в базовом GET: {page_size}'
                f'\n Получено: {len(response_data.get('movies'))}'
            )
            assert 'count' in response_data, 'Нет поля "count" в теле ответа'
            assert response_data['page'] == params['page'], (
                'Страница ответа отличается от указанной в фильтре'
            )
            assert response_data['pageSize'] == params['pageSize'], (
                'Размер страницы ответа отличается от указанной в фильтре'
            )
            for film in response_data.get('movies'):
                assert BASE_RESPONSE_MOVIE.issubset(film.keys()), (
                    f'GET-запрос. Неверный набор ключей в фильмах. \n'
                    f'Ожидаемый: {EXPECTED_MOVIE_GET_KEYS} \n'
                    f'Полученный: {film.keys()}'
                )
                movie_price_in_range = (
                        (params['minPrice'] <= film['price']) and
                        (film['price'] <= params['maxPrice'])
                )
                assert movie_price_in_range, (
                    'Цена фильма отличается от заданной в фильтрах')
                assert params['locations'] == film['location'], (
                    'Город фильма отличается от заданного в фильтрах'
                )

                # Для сравнивания bool значений, а не 'true' == True
                expected_published = params['published'] == 'true'
                assert expected_published == film['published'], (
                    'Статус публикации отличается от заданного в фильтрах'
                )
                assert params['genreId'] == film['genreId'], (
                    'Жанр фильма отличается от заданного в фильтрах'
                )

    @allure.story('Удаление фильма супер-админом')
    def test_delete_movie(self, create_movie, test_film, super_admin):
        """
        Тест на создание и удаление фильма супер-админом.
        """
        with allure.step('API-запрос на добавление фильма'):
            response_data = create_movie(user=super_admin, film_data=test_film)
            movie_id = response_data.get('id')

        with allure.step('API-запрос на удаление фильма'):
            response = super_admin.api.movies_api.delete_movie(
                movie_id, expected_status=200)
            delete_response_data = response.json()

            response = super_admin.api.movies_api.get_movie_by_id(
                movie_id, expected_status=404)
            get_response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert BASE_RESPONSE_MOVIE.issubset(delete_response_data.keys()), (
                f'Ожидаемые поля тела ответа: {BASE_RESPONSE_MOVIE} \n'
                f'Полученные поля: {response_data.keys()}'
            )
            assert get_response_data.get('message') == 'Фильм не найден', (
                f'Ожидаемое сообщение об ошибке: Фильм не найден \n'
                f'Полученное сообщение: {get_response_data.get('message')}')

    @allure.story('Полное изменение фильма супер-админом')
    def test_full_patch_movie(
            self,
            create_movie, test_film, super_admin
    ):
        """
        Тест на создание и изменение всех полей в созданном фильме
        """
        with allure.step('API-запрос на добавление фильма'):
            response_data = create_movie(user=super_admin, film_data=test_film)
            movie_id = response_data.get('id')

        with allure.step('Подтягиваем данные из constants для PATCH-запроса'):
            patched_data = PATCH_VALUES
            patched_data['name'] = DataGenerator.generate_random_film_name()

        with allure.step('PATCH-запрос на изменение фильма'):
            response = super_admin.api.movies_api.patch_movie(
                movie_id, patched_data, expected_status=200)
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            for key, value in patched_data.items():
                assert response_data[key] == value, (
                    f'PATCH-запрос'
                    f'Ожидаемое значения поля {key}: {value} \n'
                    f'Фактическое значение: {response_data[key]}'
                )

    @allure.story('Частичное изменение фильма супер-админом')
    def test_partial_patch_movie(
            self,
            create_movie,
            test_film,
            super_admin,
            patched_data
    ):
        """
        Тест на создание и изменение двух случайных полей в созданном фильме
        """
        with allure.step('API-запрос на добавление фильма'):
            response_data = create_movie(user=super_admin, film_data=test_film)
            movie_id = response_data.get('id')

        with allure.step(
                'PATCH-запрос с изменением 2 случайных полей'
                'посредством фикстуры {patched_data}'):
            response = super_admin.api.movies_api.patch_movie(
                movie_id, patched_data, expected_status=200)
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert BASE_RESPONSE_MOVIE.issubset(response_data.keys()), (
                f'Ожидаемые поля тела ответа: {BASE_RESPONSE_MOVIE} \n'
                f'Полученные поля: {response_data.keys()}'
            )
            field1 = list(patched_data.keys())[0]
            field2 = list(patched_data.keys())[1]
            assert response_data[field1] == patched_data[field1], (
                f'PATCH-запрос'
                f'Ожидаемое значения поля {field1}: {patched_data[field1]} \n'
                f'Фактическое значение: {response_data[field1]}'
            )
            assert response_data[field2] == patched_data[field2], (
                f'PATCH-запрос'
                f'Ожидаемое значения поля {field2}: {patched_data[field2]} \n'
                f'Фактическое значение: {response_data[field2]}'
            )


@pytest.mark.api
@allure.epic('Тестирование movies API')
class TestMoviesAdminNegative:
    @allure.feature(
        'Негативное тестирование movies API с позиции супер-админа')
    @allure.story('Получение фильма с несуществующим id')
    def test_get_wrong_id_film(self, super_admin):
        """
        Тест на GET-запрос фильма с несуществующим id.
        """
        with allure.step('GET-запрос с хардкод несуществующим id'):
            wrong_movie_id = 999999999
            response = super_admin.api.movies_api.get_movie_by_id(
                movie_id=wrong_movie_id,
                expected_status=404
            )
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert "message" in response_data, (
                'Нет поля "message" в теле ответа')
            assert response_data.get('message') == 'Фильм не найден', (
                f'Ожидаемое сообщение: Фильм не найден \n'
                f'Полученное сообщение: {response_data.get('message')}')

    @allure.story('Получение фильмов с неверными параметрами')
    def test_get_movies_wrong_filters(
            self,
            super_admin,
            generate_get_filters
    ):
        """
        Тест на общий get-запрос для фильмов с хардкод ошибками в фильтрах
        """
        with allure.step('Генерируем фильтры и добавляем в них ошибки'):
            params = generate_get_filters
            params['maxPrice'] = -1
            params['locations'] = 'Paris'

        with allure.step('GET-запрос с сгенерированными фильтрами'):
            response = super_admin.api.movies_api.get_movies(
                params=params,
                expected_status=400
            )
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert 'message' in response_data, (
                'Нет сообщения с информаций об ошибке '
            )

    @allure.story('Добавление фильма с несуществующим полем')
    def test_add_movie_with_wrong_field(
            self,
            create_movie,
            test_film,
            super_admin,
            wrong_key,
    ):
        """
        Тест на создание фильма с несуществующим полем.
        """
        with allure.step(
                'Генерируем несуществующее поле, выполняем POST-запрос'):
            test_film.update(wrong_key)
            response_data = create_movie(
                user=super_admin,
                film_data=test_film,
                expected_status=400
            )

        with allure.step('Проверяем правильность ответа от API'):
            assert response_data.get('message') == 'Некорректные данные', (
                f'Ожидаемое сообщение: "Некорректные данные" \n'
                f'Полученное: {response_data.get('message')}'
            )

    @allure.story('Получение фильма с ошибкой в поле')
    def test_add_movie_with_errors(
            self,
            test_film_with_errors,
            super_admin
    ):
        """
        Тест на создание фильма с неверными данными в случайном поле.
        """
        with allure.step(
                'API-запрос на добавление фильма с ошибкой в поле'
                '(фикстура {test_film_with_errors})'
        ):
            response = super_admin.api.movies_api.add_movie(
                film_data=test_film_with_errors, expected_status=400)

            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert response_data.get('error') == 'Bad Request', (
                f'Ожидаемое сообщение: "Bad Request" \n'
                f'Полученное: {response_data.get('error')}'
            )
            assert 'message' in response_data, (
                'Нет сообщения с информацией об ошибке в поле'
            )

    @allure.story('Добавление существующего фильма')
    def test_add_existing_movie(
            self,
            create_movie,
            test_film,
            super_admin
    ):
        """
        Тест на добавление фильма с существующим названием.
        """
        with allure.step('API-запрос на добавление фильма test_film'):
            response_data = create_movie(user=super_admin, film_data=test_film)

        with allure.step('Меняем 2 поля в данных test_film'):
            changed_film = copy.deepcopy(response_data)
            changed_film['description'] = 'New description'
            changed_film['price'] = 123

        with allure.step(
                'API-запрос на добавление фильма test_film с изменениями'):
            response_data = super_admin.api.movies_api.add_movie(
                film_data=changed_film, expected_status=409).json()

        with allure.step('Проверяем правильность ответа от API'):
            message = 'Фильм с таким названием уже существует'
            assert response_data.get(
                'message') == message, (
                f'Ожидаемое сообщение: {message}\n'
                f'Полученное: {response_data.get('message')}'
            )
            assert response_data.get('error') == 'Conflict', (
                f'Ожидаемая ошибка: "Conflict" \n'
                f'Полученное: {response_data.get('error')}'
            )

    @allure.story('Удаление фильма с несуществующим id')
    def test_delete_wrong_id(self, super_admin):
        """
        Тест на удаление фильма с несуществующим id.
        """
        with allure.step('DELETE-запрос с несуществующим хардкод id фильма'):
            wrong_movie_id = 999999999
            response = super_admin.api.movies_api.delete_movie(
                movie_id=wrong_movie_id,
                expected_status=404
            )
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert response_data.get('message') == 'Фильм не найден', (
                f'Ожидаемое сообщение: Фильм не найден \n'
                f'Полученное сообщение: {response_data.get('message')}')

    @allure.story('Изменение фильма с несуществующим id')
    def test_patch_wrong_id(self, super_admin):
        """
        Тест на PATCH-запрос фильма с несуществующим id.
        """
        with allure.step('PATCH-запрос с несуществующим хардкод id фильма'):
            wrong_movie_id = 999999999
            patched_data = PATCH_VALUES
            patched_data['name'] = DataGenerator.generate_random_film_name()

            response_data = super_admin.api.movies_api.patch_movie(
                movie_id=wrong_movie_id,
                patched_data=patched_data,
                expected_status=404
            ).json()

        with allure.step('Проверяем правильность ответа от API'):
            assert 'message' in response_data, (
                'Нет поля "message" в теле ответа')
            assert response_data.get('message') == 'Фильм не найден', (
                f'Ожидаемое сообщение: Фильм не найден \n'
                f'Полученное сообщение: {response_data.get('message')}')

    @allure.story('Изменение фильма с несуществующим полем')
    def test_patch_movie_with_wrong_field(
            self,
            create_movie,
            test_film,
            super_admin,
            test_film_with_errors
    ):
        """
        Тест на создание и последующее изменение несуществующего поля фильма.
        """
        with allure.step('API-запрос на добавление фильма'):
            response_data = create_movie(user=super_admin, film_data=test_film)
            movie_id = response_data.get('id')

        with allure.step(
                'Создаем несуществующее поле и пытаемся обновить его'
                'в ранее созданном фильме'):
            wrong_data = {'fake': 'Some data'}
            # Ожидаемый статус 404, а не 400 -> см. README
            response = super_admin.api.movies_api.patch_movie(
                movie_id=movie_id,
                patched_data=wrong_data,
                expected_status=404
            )
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert response_data.get('message') == 'Фильм не найден', (
                f'Ожидаемое сообщение: "Фильм не найден"'
                f' Полученное: {response_data.get('message')}'
            )

    @allure.story('Изменение фильма с ошибками в полях')
    def test_patch_movie_with_errors(
            self,
            create_movie,
            test_film,
            super_admin,
            test_film_with_errors
    ):
        """
        Создание и изменение фильма с неверными данными в случайном поле.
        """
        with allure.step('API-запрос на добавление фильма'):
            response_data = create_movie(user=super_admin, film_data=test_film)
            movie_id = response_data.get('id')

        with allure.step(
                'Фикстура {test_film_with_errors} изменяет одно поле '
                'и создает в нем ошибку. Отправляем PATCH-запрос'
                'с неверными данными'):
            response = super_admin.api.movies_api.patch_movie(
                movie_id=movie_id,
                patched_data=test_film_with_errors,
                expected_status=400
            )
            response_data = response.json()

        with allure.step('Проверяем правильность ответа от API'):
            assert response_data.get('error') == 'Bad Request', (
                f'Ожидаемое сообщение: "Bad Request" \n'
                f'Полученное: {response_data.get('error')}'
            )
            assert 'message' in response_data, (
                'Нет сообщения с информацией об ошибке в поле'
            )


@pytest.mark.api
@allure.epic('Тестирование movies API')
class TestMoviesCommonUserPositive:
    @allure.feature(
        'Позитивное тестирование movies API с позиции обычного юзера')
    @pytest.mark.slow
    @allure.story('Добавление фильма простым юзером')
    def test_add_movie_common_user(self, create_movie, test_film, common_user):
        """
        Тест на создание фильма обычным пользователем.
        """
        with allure.step('API-запрос на добавление фильма простым юзером'):
            response_data = create_movie(user=common_user,
                                         film_data=test_film,
                                         expected_status=403)

        with allure.step('Проверяем правильность ответа от API'):
            assert response_data.get('message') == 'Forbidden resource', (
                f'Ожидаемое сообщение: "Forbidden resource" \n'
                f'Полученное: {response_data.get('message')}'
            )
            assert response_data.get('error') == 'Forbidden', (
                f'Ожидаемое сообщение: "Forbidden" \n'
                f'Полученное: {response_data.get('error')}'
            )
