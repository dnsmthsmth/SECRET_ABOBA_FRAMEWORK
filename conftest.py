import copy
import random

import pytest
import requests
from dotenv import load_dotenv
from faker import Faker

from api.api_manager import ApiManager
from constants import (BASE_RESPONSE_MOVIE, BASE_URL, FILM_KEYS_MUTATIONS,
                       GENRES_ENDPOINT, PATCH_VALUES)
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator

faker = Faker()
load_dotenv()


@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)


@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def unauthenticated_session():
    """
    Фикстура для создания неаутентифицированной сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def super_admin_session(api_manager):
    """
    Фикстура для создания супер-админ сессии.
    """
    api_manager.auth_api.super_admin_authenticate()
    return api_manager.session


@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)


@pytest.fixture(scope="function")
def test_film(genre_ids):
    """
    Генерация случайного фильма для тестов.
    """
    random_film_name = DataGenerator.generate_random_film_name()
    random_film_price = DataGenerator.generate_random_price()
    random_description = DataGenerator.generate_random_description()
    random_film_location = DataGenerator.generate_random_location()
    random_film_published = DataGenerator.generate_random_published()
    random_film_genre_id = DataGenerator.generate_random_genre_id(genre_ids)

    # Захардкоженная рабочая ссылка на изображение
    placeholder_image_url = 'https://picsum.photos/200/300'

    return {
        "name": random_film_name,
        "imageUrl": placeholder_image_url,
        "price": random_film_price,
        "description": random_description,
        "location": random_film_location,
        "published": random_film_published,
        "genreId": random_film_genre_id
    }


@pytest.fixture(scope="function")
def test_film_with_errors(test_film):
    """
    Генерация тестового фильма с ошибкой в случайном поле.
    Создаем копию тестового фильма, случайно выбираем поле для мутации.
    Выбираем случайный вариант для этого поля.
    Возвращаем фильм с ошибкой в каком-то случайном поле.
    """
    mutated = copy.deepcopy(test_film)
    field_name = random.choice(list(FILM_KEYS_MUTATIONS.keys()))
    mutation = random.choice(FILM_KEYS_MUTATIONS[field_name])
    mutated[field_name] = mutation
    return mutated


@pytest.fixture(scope="function")
def wrong_key():
    """
    Генерация случайного поля для негативного теста.
    Генерируется случайное слово.
    Проверяется, что оно не совпало с настоящими полями.
    """
    real_keys = BASE_RESPONSE_MOVIE
    fake_key = faker.word()
    while fake_key in real_keys:
        fake_key = faker.word()
    return {
        fake_key: faker.word()
    }


@pytest.fixture(scope="session")
def genre_ids(requester):
    """
    Получение списка доступных айдишников жанров.
    Необходимо для генерации случайного существующего айдишника.
    """
    response = requester.send_request(
        method="GET",
        endpoint=GENRES_ENDPOINT,
        need_logging=False,
        expected_status=200
    )
    response_data = response.json()
    genres_ids = []
    for genre in response_data:
        genres_ids.append(genre['id'])
    return genres_ids


@pytest.fixture(scope="function")
def patched_data():
    """
    Фикстура выбирает 2 случайных поля для замены и возвращает
    словарь с ключами в качестве этих полей и значениями из константы
    """
    random_fields = random.sample(list(PATCH_VALUES.keys()), 2)

    patched_data = {
        random_fields[0]: PATCH_VALUES[random_fields[0]],
        random_fields[1]: PATCH_VALUES[random_fields[1]],
    }

    return patched_data


@pytest.fixture(scope="function")
def add_movie(test_film, api_manager):
    """
    Фикстура создает новый фильм, возвращает тело ответа.
    Удаляет созданный тестовый фильм после завершения теста.
    """
    response = api_manager.movies_api.add_movie(
        film_data=test_film,
        expected_status=201
    )
    response_data = response.json()
    assert 'id' in response_data, 'Нет id созданного фильма в теле ответа'
    movie_id = response_data.get('id')
    yield response_data

    try:
        api_manager.movies_api.delete_movie(movie_id, expected_status=200)
    except Exception as e:
        print(f"\n Не удалось удалить фильм {movie_id}: {e}")


@pytest.fixture(scope='function')
def generate_get_filters(api_manager):
    """
    Фикстура генерирует подходящие данные для фильтров GET-запроса
    """
    random_page_size = DataGenerator.generate_page_size()
    random_film_location = DataGenerator.generate_random_location()
    random_film_published = DataGenerator.generate_random_published()

    # Преобразовываем в формат для фильтров
    random_film_published = 'true' if random_film_published else 'false'
    random_created_at = DataGenerator.chose_created_at()

    return {
        "pageSize": random_page_size,
        "page": 1,
        "minPrice": 10,
        "maxPrice": 500,
        "locations": random_film_location,
        "published": random_film_published,
        "genreId": 1,
        "createdAt": random_created_at
    }
