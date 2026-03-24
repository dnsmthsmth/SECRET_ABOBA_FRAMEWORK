import random

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
