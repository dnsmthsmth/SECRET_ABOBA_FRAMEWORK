import os

from constants import BASE_AUTH_URL, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester


class AuthAPI(CustomRequester):
    """
    Класс для работы с аутентификацией.
    """
    def __init__(self, session):
        super().__init__(session=session, base_url=BASE_AUTH_URL)

    def super_admin_authenticate(self):
        login_data = {
            "email": os.getenv("ADMIN_EMAIL"),
            "password": os.getenv("ADMIN_PASSWORD")
        }

        response = self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=200
        )
        response_data = response.json()
        token = response_data.get("accessToken")

        if not token:
            raise KeyError("accessToken is missing")

        self._update_session_headers(**{"authorization": "Bearer " + token})
