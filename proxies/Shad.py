from django.conf import settings

from proxies.http_request_utils import post

SHAD_LOGIN_USERNAME = settings.SHAD_LOGIN_USERNAME
SHAD_LOGIN_PASSWORD = settings.SHAD_LOGIN_PASSWORD


SHAD_API_URL = 'https://shadapi.noyanet.com/api/v1'


def login_to_Shad(landing_id=284):

    url = f'{SHAD_API_URL}/account/login/'

    payload = {
        "landingId": landing_id,
        "username": SHAD_LOGIN_USERNAME,
        "password": SHAD_LOGIN_PASSWORD,
    }

    return post(url, payload)


def get_user_data(token, user_uuid):
    url = f'{SHAD_API_URL}/ShadEvent?UserHashId={user_uuid}'

    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {}
    return post(url, payload, headers=headers)
