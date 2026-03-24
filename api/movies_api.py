from constants import BASE_URL, MOVIES_ENDPOINT
from custom_requester.custom_requester import CustomRequester


class MoviesAPI(CustomRequester):
    """
    Класс для работы с фильмами.
    """
    def __init__(self, session):
        super().__init__(session=session, base_url=BASE_URL)

    def add_movie(self, film_data, expected_status=201):
        """
        Добавление нового пользователя нового фильма.
        :param film_data: Данные фильма.
        :param expected_status: Ожидаемый статус-код.
        """

        return self.send_request(
            method='POST',
            endpoint=MOVIES_ENDPOINT,
            data=film_data,
            expected_status=expected_status
        )

    def get_movie_by_id(self, movie_id, expected_status=200):
        """
        Получение фильма по его id.
        :param movie_id: id фильма.
        :param expected_status: Ожидаемый статус-код.
        """

        return self.send_request(
            method='GET',
            endpoint=MOVIES_ENDPOINT + f'/{movie_id}',
            expected_status=expected_status
        )

    def get_movies(self, params=None, expected_status=200):
        """
        Получение списка фильмов с фильтрацией.
        :param params: Словарь с параметрами фильтрации.
        :param expected_status: Ожидаемый статус-код.
        """
        if params is None:
            params = {}

        # Очищаем None значения
        params = {k: v for k, v in params.items() if v is not None}

        return self.send_request(
            method='GET',
            endpoint=MOVIES_ENDPOINT,
            params=params,
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        """
        Удаление фильма по его id.
        :param movie_id: id фильма.
        :param expected_status: Ожидаемый статус-код.
        """

        return self.send_request(
            method='DELETE',
            endpoint=MOVIES_ENDPOINT + f'/{movie_id}',
            expected_status=expected_status
        )

    def patch_movie(self, movie_id, patched_data, expected_status=200):
        """
        Изменение данных о фильме по его id.
        :param movie_id: id фильма.
        :param patched_data: Коллекция с новыми данными.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method='PATCH',
            endpoint=MOVIES_ENDPOINT + f'/{movie_id}',
            data=patched_data,
            expected_status=expected_status
        )
