import datetime
import random
import string

from faker import Faker

faker = Faker()


class DataGenerator:
    # Добавлены числа -> см. README
    @staticmethod
    def generate_random_film_name():
        number1 = random.randint(0, 10000)
        number2 = random.randint(0, 10000)
        return f'{faker.catch_phrase()} {number1} {number2}'

    @staticmethod
    def generate_random_price():
        return random.randint(100, 1000)

    @staticmethod
    def generate_random_description():
        return faker.text(500)

    @staticmethod
    def generate_random_location():
        locations = ('MSK', 'SPB')
        return random.choice(locations)

    @staticmethod
    def generate_random_rating():
        return round(random.uniform(1, 10), 1)

    @staticmethod
    def generate_random_published():
        return random.choice((False, True))

    @staticmethod
    def generate_random_genre_id(genre_ids):
        return random.choice(genre_ids)

    @staticmethod
    def generate_page_size():
        return random.randint(1, 20)

    @staticmethod
    def chose_created_at():
        return random.choice(['asc', 'desc'])

    @staticmethod
    def generate_random_email():
        random_string = ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_password():
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """
        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters)  # Одна буква
        digits = random.choice(string.digits)  # Одна цифра

        # Дополняем пароль случайными символами из допустимого набора
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)  # Остальная длина пароля
        remaining_chars = ''.join(
            random.choices(all_chars, k=remaining_length))

        # Перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_user_data() -> dict:
        """Генерирует данные для тестового пользователя"""
        from uuid import uuid4

        return {
            'id': f'{uuid4()}',  # генерируем UUID как строку
            'email': DataGenerator.generate_random_email(),
            'full_name': DataGenerator.generate_random_name(),
            'password': DataGenerator.generate_random_password(),
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            'verified': False,
            'banned': False,
            'roles': '{USER}'
        }

    @staticmethod
    def generate_random_int(num: int) -> int:
        return random.randint(1, num)

    @staticmethod
    def generate_movie_rating() -> str:
        return random.choice(['1', '2', '3', '4', '5'])

    @staticmethod
    def generate_movie_comment() -> str:
        return f'UI test comment #{random.randint(1, 100000)}'
