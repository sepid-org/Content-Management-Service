from django.conf import settings
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rest_framework import status
from rest_framework.response import Response

BANK_URL = settings.BANK_URL


# Configure retry strategy
def get_retry_session(retries=5, backoff_factor=0.3,
                      status_forcelist=(500, 502, 503, 504)):
    """
    Create a requests session with retry capabilities.

    Args:
        retries (int): Number of total retries to allow.
        backoff_factor (float): A backoff factor to apply between attempts.
        status_forcelist (tuple): HTTP status codes to retry on.

    Returns:
        requests.Session: A configured session with retry capabilities
    """
    retry_strategy = Retry(
        total=retries,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "POST"],  # Only retry these methods
        backoff_factor=backoff_factor
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _get(url, params):
    try:
        session = get_retry_session()
        response = session.get(
            url,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return Response(
            {"error": f"Failed to process GET request after retries: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _post(url, payload):
    try:
        session = get_retry_session()
        response = session.post(
            url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return Response(
            {"error": f"Failed to process POST request after retries: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def request_transfer(sender_id: str, receiver_id: str, funds: dict):
    """
    Send a transfer request to the transfer API endpoint.

    Args:
        sender_id (str): UUID of the sender
        receiver_id (str): UUID of the receiver
        funds (dict): Dictionary of currency names and amounts

    Returns:
        dict: Response from the transfer API or Response object with error
    """
    url = f'{BANK_URL}counter/transfer/'

    payload = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "funds": funds
    }

    return _post(url, payload)


def get_user_balances(user_uuid):

    url = f'{BANK_URL}counter/user-balances/'

    payload = {
        "user_uuid": user_uuid,
    }

    return _get(url, payload)
