from django.conf import settings
import requests
from rest_framework import status
from rest_framework.response import Response

WMS_URL = settings.WMS_URL


def _get(url, params):
    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return Response(
            {"error": f"Failed to process: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_website(website_name: str):
    url = f'{WMS_URL}api/website/website-by-name/'
    params = {"website_name": website_name}

    return _get(url, params)
