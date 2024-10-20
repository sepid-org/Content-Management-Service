import requests
from django.conf import settings
from utils.singleton_class import Singleton


class MetabaseProxy(Singleton):

    def create_session(self):
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "username": settings.METABASE_USERNAME,
            "password": settings.METABASE_PASSWORD,
        }
        response = requests.post(
            f'{settings.METABASE_URL}api/session/', headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def __init__(self) -> None:
        from django.conf import settings
        if not settings.DEBUG:
            self.session_data = self.create_session()

    def post(self, url, headers, data):
        headers = {
            "X-Metabase-Session": self.session_data.get("id"),
            **headers,
        }
        return requests.post(url=url, headers=headers, data=data)
