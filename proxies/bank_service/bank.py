from django.conf import settings

from proxies.http_request_utils import get, post

BANK_URL = settings.BANK_URL


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

    response = post(url, payload)

    if response.get('success', False) is False:
        raise Exception(response.data['error'])

    return response


def get_user_balances(user_uuid):

    url = f'{BANK_URL}counter/user-balances/'

    payload = {
        "user_uuid": user_uuid,
    }

    return get(url, payload)
