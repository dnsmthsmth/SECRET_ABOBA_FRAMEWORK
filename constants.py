from enum import Enum


# Доступные роли пользователей
class Roles(Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'
    SUPER_ADMIN = 'SUPER_ADMIN'


BASE_AUTH_URL = 'https://auth.dev-cinescope.coconutqa.ru/'
BASE_URL = 'https://api.dev-cinescope.coconutqa.ru/'
LOGIN_ENDPOINT = '/login'
REGISTER_ENDPOINT = '/register'
MOVIES_ENDPOINT = '/movies'
GENRES_ENDPOINT = '/genres'
TEST_IMAGE_PLACEHOLDER = 'https://picsum.photos/200/300'

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Базовые поля в ответе о фильмах
BASE_RESPONSE_MOVIE = {
    'id', 'name', 'price',
    'description', 'location',
    'published', 'rating', 'genreId',
    'createdAt', 'genre'
}

# Поля в ответе о КОНКРЕТНОМ фильме
EXPECTED_MOVIE_GET_KEYS = {
    'id', 'name', 'price',
    'description', 'location',
    'published', 'rating', 'genreId',
    'createdAt', 'genre', 'reviews'
}

# Подходящие значения для обновления данных
PATCH_VALUES = {
    'name': 'Patched name',
    'description': 'Patched description',
    'price': 100,
    'location': 'MSK',
    'published': True,
    'genreId': 1
}

# См. README для информации о константах с неверными данными
FILM_KEYS_MUTATIONS = {
        # 'name': ['', None, 123, True],
        'price': ['not a number', False],
        'description': [True, False, 15],
        'location': ['Paris', '', 'msk', True],
        'published': ['True', 'False', 1, 0],
        'genreId': [0, -1, True, 'Something', 'Драма'],
    }

# Раскомментировать константу ниже для проверки багов с README
"""FILM_KEYS_MUTATIONS = {
        'name': ['', None, 123, True],
        'price': [-100, 0, 'not a number', False, None],
        'description': [True, False, 15, None],
        'location': ['Paris', '', 'msk', True, None],
        'published': ['True', 'False', 1, 0, None],
        'genreId': [0, -1, True, 'Something', 'Драма', None],
    }"""

# Цвета для логов
GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'
