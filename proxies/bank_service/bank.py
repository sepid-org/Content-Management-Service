from django.conf import settings
import requests
from rest_framework import status
from rest_framework.response import Response

BANK = settings.BANK


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


def _post(url, payload):
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return Response(
            {"error": f"Failed to process: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def request_transfer(sender_id: str, receiver_id: str, funds: dict):
    """
    Send a transfer request to the transfer API endpoint.

    Args:
        sender_id (str): UUID of the receiver
        receiver_id (str): UUID of the receiver
        currency_amounts (dict): Dictionary of currency names and amounts

    Returns:
        dict: Response from the transfer API or Response object with error
    """
    url = f'{BANK}counter/transfer/'

    payload = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "currency_amounts": funds
    }

    return _post(url, payload)


def get_user_balances(user_uuid):

    url = f'{BANK}counter/user-balances/'

    payload = {
        "user_uuid": user_uuid,
    }

    return _get(url, payload)
