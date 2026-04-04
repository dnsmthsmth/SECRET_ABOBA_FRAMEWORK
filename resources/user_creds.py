import os

from dotenv import load_dotenv

load_dotenv()


class SuperAdminCreds:
    USERNAME = os.getenv('ADMIN_EMAIL')
    PASSWORD = os.getenv('ADMIN_PASSWORD')
