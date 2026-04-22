import copy
import datetime
import os
import random

import pytest
import requests
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy.orm import Session

from api.api_manager import ApiManager
from constants import (BASE_RESPONSE_MOVIE, BASE_URL, FILM_KEYS_MUTATIONS,
                       GENRES_ENDPOINT, MOVIES_ENDPOINT, PATCH_VALUES,
                       TEST_IMAGE_PLACEHOLDER, Roles)
from custom_requester.custom_requester import CustomRequester
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
from entities.user import User
from models.pydantic_models import TestUser
from utils.data_generator import DataGenerator

faker = Faker()
load_dotenv()


@pytest.fixture(scope='session')
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)


@pytest.fixture(scope='session')
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)


@pytest.fixture(scope='function')
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
    placeholder_image_url = TEST_IMAGE_PLACEHOLDER

    return {
        'name': random_film_name,
        'imageUrl': placeholder_image_url,
        'price': random_film_price,
        'description': random_description,
        'location': random_film_location,
        'published': random_film_published,
        'genreId': random_film_genre_id
    }


@pytest.fixture(scope='function')
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


@pytest.fixture(scope='function')
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


@pytest.fixture(scope='session')
def genre_ids(requester):
    """
    Получение списка доступных айдишников жанров.
    Необходимо для генерации случайного существующего айдишника.
    """
    response = requester.send_request(
        method='GET',
        endpoint=GENRES_ENDPOINT,
        need_logging=False,
        expected_status=200
    )
    response_data = response.json()
    genres_ids = []
    for genre in response_data:
        genres_ids.append(genre['id'])
    return genres_ids


@pytest.fixture(scope='session')
def random_movie_id(requester):
    """
    Получение псевдослучайного id фильма.
    Используется в ui тесте для выбора случайной странички фильма.
    Выборка происходит только из первых 20 фильмов с GET-запроса.
    """
    response = requester.send_request(
        method='GET',
        endpoint=MOVIES_ENDPOINT,
        params={'pageSize': 20},
        need_logging=True,
        expected_status=200
    )
    response_data = response.json()
    movies_ids = []
    for movie in response_data['movies']:
        movies_ids.append(movie['id'])
    return random.choice(movies_ids)


@pytest.fixture(scope='function')
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


@pytest.fixture(scope='function')
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
        print(f'\n Не удалось удалить фильм {movie_id}: {e}')


@pytest.fixture(scope='function')
def create_movie(super_admin):
    """
    Фикстура для создания фильма через API.
    """
    created_movies = []

    def _create_movie(user, film_data, expected_status=201):
        response = user.api.movies_api.add_movie(
            film_data=film_data,
            expected_status=expected_status)
        response_data = response.json()
        if expected_status == 201:
            assert 'id' in response_data, (
                'Нет id созданного фильма в теле ответа')
            created_movies.append(response_data["id"])
        return response_data

    yield _create_movie

    for movie_id in created_movies:
        try:
            super_admin.api.movies_api.delete_movie(
                movie_id, expected_status=200)
        except Exception as e:
            print(f'\n Не удалось удалить фильм {movie_id}: {e}')


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
        'pageSize': random_page_size,
        'page': 1,
        'minPrice': 10,
        'maxPrice': 500,
        'locations': random_film_location,
        'published': random_film_published,
        'genreId': 1,
        'createdAt': random_created_at
    }


@pytest.fixture(scope='function')
def test_user() -> TestUser:
    """
    Фикстура для генерации данных простого пользователя.
    """
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER.value]
    )


@pytest.fixture(scope='function')
def creation_user_data(test_user):
    """
    Фикстура для актуализации данных при создании пользователя админом.
    """
    return TestUser(
        email=test_user.email,
        fullName=test_user.fullName,
        password=test_user.password,
        passwordRepeat=test_user.passwordRepeat,
        roles=test_user.roles,
        verified=True,
        banned=False
    )


@pytest.fixture(scope='session')
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope='session')
def user_session():
    """
    Фикстура для организации работы сессий различных пользователей.
    """
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture(scope='session')
def unauthenticated_session(user_session):
    """
    Фикстура для создания неаутентифицированной сессии.
    """
    http_session = user_session()
    return http_session


@pytest.fixture(scope='session')
def super_admin(user_session):
    """
    Фикстура для создания сессии супер-админа.
    """
    new_session = user_session()

    super_admin = User(
        os.getenv('ADMIN_EMAIL'),
        os.getenv('ADMIN_PASSWORD'),
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    """
    Фикстура для создания сессии обычного пользователя.
    """
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user


@pytest.fixture
def admin(user_session, super_admin, creation_user_data):
    """
    Фикстура для создания сессии админа.
    """
    new_session = user_session()

    admin = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.ADMIN.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    admin.api.auth_api.authenticate(admin.creds)
    return admin


@pytest.fixture(scope='module')
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()


@pytest.fixture(scope='function')
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper


@pytest.fixture(scope='function')
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user

    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)


@pytest.fixture(scope='function')
def test_db_film(test_film):
    """
    Изменение ключей словаря тестового фильма
    для работы с БД, вместо API
    """
    test_film['image_url'] = test_film.pop('imageUrl')
    test_film['genre_id'] = test_film.pop('genreId')
    test_film['rating'] = DataGenerator.generate_random_rating()
    test_film['created_at'] = datetime.datetime.now()
    return test_film


@pytest.fixture(scope='function')
def created_test_film(db_helper, test_db_film):
    """
    Фикстура, которая создает тестовый фильм в БД
    Перед проверкой проверяется, что сгенерированный фильм уже
    не существует в БД.
    Удаляет его после завершения теста.
    """
    assert db_helper.get_movie_by_name(test_db_film['name']) is None, (
        f'Сгенерированный фильм {test_db_film['name']} уже существует в БД'
    )

    movie = db_helper.create_test_movie(test_db_film)
    yield movie

    if db_helper.get_movie_by_id(movie.id):
        db_helper.delete_movie(movie)


@pytest.fixture(scope='function')
def comment_data():
    """
    Фикстура для генерации комментария и рейтинга.
    Используется в ui-тесте.
    """
    comment_data = {
        'comment_text': DataGenerator.generate_movie_comment(),
        'comment_rating': DataGenerator.generate_movie_rating()
    }

    return comment_data
