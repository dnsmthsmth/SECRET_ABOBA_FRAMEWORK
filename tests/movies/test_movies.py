import copy

from constants import (BASE_RESPONSE_MOVIE, EXPECTED_MOVIE_GET_KEYS,
                       PATCH_VALUES)
from utils.data_generator import DataGenerator


class TestMoviesUnauthenticated:
    def test_add_movie_unauthorised(
            self,
            api_manager,
            test_film,
            unauthenticated_session
    ):
        """
        Тест на попытку создания фильма незалогиненным пользователем.
        """
        response = api_manager.movies_api.add_movie(
            film_data=test_film, expected_status=401
        )
        response_data = response.json()

        assert response_data['message'] == 'Unauthorized', (
            f'Ожидаемое сообщение: Unauthorized \n'
            f'Полученное сообщение : {response_data.get('message')}'
        )

    def test_delete_movie_unauthorised(
            self, api_manager, test_film, unauthenticated_session
    ):
        """
        Тест на удаление фильма незалогиненным пользователем.
        Проверяется захардкоженный id 566
        """
        test_id = 566
        response = api_manager.movies_api.delete_movie(
            test_id, expected_status=401
        )
        response_data = response.json()

        assert response_data.get('message') == 'Unauthorized', (
            f'Ожидаемое сообщение: Unauthorized \n'
            f'Полученное сообщение : {response_data.get('message')}'
        )

    def test_full_patch_movie_unauthorised(
            self, api_manager, test_film, unauthenticated_session
    ):
        """
        Тест на изменение фильма незалогиненным пользователем.
        Проверяется захардкоженный id 566
        """
        movie_id = 566

        patched_data = PATCH_VALUES
        patched_data['name'] = DataGenerator.generate_random_film_name()

        response = api_manager.movies_api.patch_movie(
            movie_id, patched_data, expected_status=401
        )
        response_data = response.json()

        assert response_data.get('message') == 'Unauthorized', (
            f'Ожидаемое сообщение: Unauthorized \n'
            f'Полученное сообщение: {response_data.get('message')}'
        )


class TestMoviesAdminPositive:
    def test_add_movie(self, add_movie, super_admin_session):
        """
        Тест на создание фильма супер-админом.
        """
        response_data = add_movie

        assert 'id' in response_data, 'Нет id созданного фильма в теле ответа'
        assert BASE_RESPONSE_MOVIE.issubset(response_data.keys()), (
            f'Ожидаемые поля тела ответа: {BASE_RESPONSE_MOVIE} \n'
            f'Полученные поля: {response_data.keys()}'
        )

    def test_get_film(self, api_manager, add_movie, super_admin_session):
        """
        Тест на создание и получение созданного фильма по его id.
        """
        response_data = add_movie
        movie_id = response_data.get('id')

        response = api_manager.movies_api.get_movie_by_id(
            movie_id=movie_id, expected_status=200)
        response_data = response.json()

        assert movie_id == response_data.get('id'), (
            f'Ожидаемый id: {movie_id} \n'
            f'Полученный id: {response_data.get('id')}'
        )
        assert EXPECTED_MOVIE_GET_KEYS.issubset(response_data.keys()), (
            f'Ожидаемые поля тела ответа: {BASE_RESPONSE_MOVIE} \n'
            f'Полученные поля: {response_data.keys()}'
        )

    def test_get_films(self, api_manager, super_admin_session):
        """
        Тест на общий get-запрос для фильмов (без фильтров)
        """
        response = api_manager.movies_api.get_movies(expected_status=200)
        response_data = response.json()

        assert 'movies' in response_data, 'Нет объекта movies в теле ответа'
        assert len(response_data.get('movies')) == 10, (
            f'Ожидаемое количество фильмов в базовом GET: 10 \n'
            f'Получено: {len(response_data.get('movies'))}'
        )

        for film in response_data.get('movies'):
            assert BASE_RESPONSE_MOVIE.issubset(film.keys()), (
                f'GET-запрос. Неверный набор ключей в отображаемых фильмах. \n'
                f'Ожидаемый: {EXPECTED_MOVIE_GET_KEYS} \n'
                f'Полученный: {film.keys()}'
            )

        assert 'count' in response_data, 'Нет поля "count" в теле ответа'
        assert 'page' in response_data, 'Нет поля "page" в теле ответа'
        assert 'pageSize' in response_data, 'Нет поля "pageSize" в теле ответа'
        assert 'pageCount' in response_data, (
            'Нет поля "pageCount" в теле ответа'
        )

    def test_delete_movie(self, api_manager, add_movie, super_admin_session):
        """
        Тест на создание и удаление фильма супер-админом.
        """
        response_data = add_movie
        movie_id = response_data.get('id')

        response = api_manager.movies_api.delete_movie(
            movie_id, expected_status=200)

        delete_response_data = response.json()
        response = api_manager.movies_api.get_movie_by_id(
            movie_id, expected_status=404)

        get_response_data = response.json()

        assert BASE_RESPONSE_MOVIE.issubset(delete_response_data.keys()), (
            f'Ожидаемые поля тела ответа: {BASE_RESPONSE_MOVIE} \n'
            f'Полученные поля: {response_data.keys()}'
        )
        assert get_response_data.get('message') == 'Фильм не найден', (
            f'Ожидаемое сообщение об ошибке: Фильм не найден \n'
            f'Полученное сообщение: {get_response_data.get('message')}')

    def test_full_patch_movie(
            self,
            api_manager,
            add_movie,
            super_admin_session
    ):
        """
        Тест на создание и изменение всех полей в созданном фильме
        """
        response_data = add_movie
        movie_id = response_data.get('id')

        patched_data = PATCH_VALUES
        patched_data['name'] = DataGenerator.generate_random_film_name()

        response = api_manager.movies_api.patch_movie(
            movie_id, patched_data, expected_status=200)

        response_data = response.json()

        for key, value in patched_data.items():
            assert response_data[key] == value, (
                f'PATCH-запрос'
                f'Ожидаемое значения поля {key}: {value} \n'
                f'Фактическое значение: {response_data[key]}'
            )

    def test_partial_patch_movie(
            self,
            api_manager,
            add_movie,
            patched_data,
            super_admin_session
    ):
        """
        Тест на создание и изменение двух случайных полей в созданном фильме
        """
        response_data = add_movie
        movie_id = response_data.get('id')

        response = api_manager.movies_api.patch_movie(
            movie_id, patched_data, expected_status=200)

        response_data = response.json()

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

    def test_get_films_filtered(
            self,
            api_manager,
            generate_get_filters,
            super_admin_session
    ):
        """
        Тест на общий get-запрос для фильмов со случайными фильтрами
        """
        params = generate_get_filters
        response = api_manager.movies_api.get_movies(
            params=params,
            expected_status=200
        )
        response_data = response.json()

        assert 'movies' in response_data, 'Нет объекта movies в теле ответа'
        assert len(response_data.get('movies')) == params['pageSize'], (
            f'Ожидаемое количество фильмов в базовом GET: {params['pageSize']}'
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
                f'GET-запрос. Неверный набор ключей в отображаемых фильмах. \n'
                f'Ожидаемый: {EXPECTED_MOVIE_GET_KEYS} \n'
                f'Полученный: {film.keys()}'
            )
            assert params['minPrice'] <= film['price'] <= params['maxPrice'], (
                'Цена фильма отличается от заданной в фильтрах'
            )
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


class TestMoviesAdminNegative:
    def test_add_movie_with_wrong_field(
            self,
            api_manager,
            test_film,
            wrong_key,
            super_admin_session
    ):
        """
        Тест на создание фильма с несуществующим полем.
        """
        test_film.update(wrong_key)
        response = api_manager.movies_api.add_movie(
            film_data=test_film, expected_status=400)

        response_data = response.json()

        assert response_data.get('message') == "Некорректные данные", (
            f'Ожидаемое сообщение: "Некорректные данные" \n'
            f'Полученное: {response_data.get('message')}'
        )

    def test_add_movie_with_errors(
            self,
            api_manager,
            test_film_with_errors,
            super_admin_session
    ):
        """
        Тест на создание фильма с неверными данными в случайном поле.
        """
        response = api_manager.movies_api.add_movie(
            film_data=test_film_with_errors, expected_status=400)

        response_data = response.json()

        assert response_data.get('error') == "Bad Request", (
            f'Ожидаемое сообщение: "Bad Request" \n'
            f'Полученное: {response_data.get('error')}'
        )
        assert "message" in response_data, (
            "Нет сообщения с информацией об ошибке в поле"
        )

    def test_add_existing_movie(
            self,
            api_manager,
            add_movie,
            super_admin_session
    ):
        """
        Тест на добавление фильма с существующим названием.
        """
        # Добавили сгенерированный фильм
        response_data = add_movie

        # Изменили 2 поля
        changed_film = copy.deepcopy(response_data)
        changed_film['description'] = 'New description'
        changed_film['price'] = 123

        # Добавили измененный фильм
        response = api_manager.movies_api.add_movie(
            film_data=changed_film, expected_status=409)
        response_data = response.json()

        assert response_data.get(
            'message') == "Фильм с таким названием уже существует", (
            f'Ожидаемое сообщение: "Фильм с таким названием уже существует" \n'
            f'Полученное: {response_data.get('message')}'
        )
        assert response_data.get('error') == "Conflict", (
            f'Ожидаемая ошибка: "Conflict" \n'
            f'Полученное: {response_data.get('error')}'
        )

    def test_get_wrong_id_film(self, api_manager, super_admin_session):
        """
        Тест на GET-запрос фильма с несуществующим id.
        """
        wrong_movie_id = 999999999
        response = api_manager.movies_api.get_movie_by_id(
            movie_id=wrong_movie_id,
            expected_status=404
        )
        response_data = response.json()

        assert "message" in response_data, 'Нет поля "message" в теле ответа'
        assert response_data.get('message') == 'Фильм не найден', (
            f'Ожидаемое сообщение: Фильм не найден \n'
            f'Полученное сообщение: {response_data.get('message')}')

    def test_delete_wrong_id(self, api_manager, super_admin_session):
        """
        Тест на удаление фильма с несуществующим id.
        """
        wrong_movie_id = 999999999
        response = api_manager.movies_api.delete_movie(
            movie_id=wrong_movie_id,
            expected_status=404
        )
        response_data = response.json()

        assert response_data.get('message') == 'Фильм не найден', (
            f'Ожидаемое сообщение: Фильм не найден \n'
            f'Полученное сообщение: {response_data.get('message')}')

    def test_patch_wrong_id(self, api_manager, super_admin_session):
        """
        Тест на PATCH-запрос фильма с несуществующим id.
        """
        wrong_movie_id = 999999999
        patched_data = PATCH_VALUES
        patched_data['name'] = DataGenerator.generate_random_film_name()

        response = api_manager.movies_api.patch_movie(
            movie_id=wrong_movie_id,
            patched_data=patched_data,
            expected_status=404
        )
        response_data = response.json()

        assert "message" in response_data, 'Нет поля "message" в теле ответа'
        assert response_data.get('message') == 'Фильм не найден', (
            f'Ожидаемое сообщение: Фильм не найден \n'
            f'Полученное сообщение: {response_data.get('message')}')

    def test_patch_movie_with_wrong_field(
            self,
            api_manager,
            add_movie,
            super_admin_session,
            test_film_with_errors
    ):
        """
        Тест на создание и последующее изменение несуществующего поля фильма.
        """
        response_data = add_movie
        movie_id = response_data.get('id')

        wrong_data = {'fake': 'Some data'}
        # Ожидаемый статус 404, а не 400 -> см. README
        response = api_manager.movies_api.patch_movie(
            movie_id=movie_id,
            patched_data=wrong_data,
            expected_status=404
        )
        response_data = response.json()

        assert response_data.get('message') == "Фильм не найден", (
            f'Ожидаемое сообщение: "Фильм не найден"'
            f' Полученное: {response_data.get('message')}'
        )

    def test_patch_movie_with_errors(
            self,
            api_manager,
            add_movie,
            test_film_with_errors,
            super_admin_session
    ):
        """
        Создание и изменение фильма с неверными данными в случайном поле.
        """
        response_data = add_movie
        movie_id = response_data.get('id')

        #
        response = api_manager.movies_api.patch_movie(
            movie_id=movie_id,
            patched_data=test_film_with_errors,
            expected_status=400
        )
        response_data = response.json()

        assert response_data.get('error') == "Bad Request", (
            f'Ожидаемое сообщение: "Bad Request" \n'
            f'Полученное: {response_data.get('error')}'
        )
        assert "message" in response_data, (
            "Нет сообщения с информацией об ошибке в поле"
        )

    def test_get_movies_wrong_filters(
            self,
            api_manager,
            generate_get_filters
    ):
        """
        Тест на общий get-запрос для фильмов с хардкод ошибками в фильтрах
        """
        params = generate_get_filters
        params['maxPrice'] = -1
        params['locations'] = 'Paris'
        response = api_manager.movies_api.get_movies(
            params=params,
            expected_status=400
        )
        response_data = response.json()

        assert 'message' in response_data, (
            'Нет сообщения с информаций об ошибке '
        )
