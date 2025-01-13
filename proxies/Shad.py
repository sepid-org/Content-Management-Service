import uuid
from django.conf import settings
from proxies.http_request_utils import get, post

SHAD_LOGIN_USERNAME = settings.SHAD_LOGIN_USERNAME
SHAD_LOGIN_PASSWORD = settings.SHAD_LOGIN_PASSWORD
SHAD_API_URL = 'https://shadapi.noyanet.com/api/v1'


class TokenManager:
    _token = None

    @classmethod
    def set_token(cls, token):
        cls._token = token

    @classmethod
    def get_token(cls):
        return cls._token


def _login_to_shad(landing_id):
    """
    Authenticate with the Shad API and store the token.
    Returns the full response from the login endpoint.
    """
    url = f'{SHAD_API_URL}/account/login/'

    payload = {
        "landingId": landing_id,
        "username": SHAD_LOGIN_USERNAME,
        "password": SHAD_LOGIN_PASSWORD,
    }

    response = post(url, payload)

    if response.get('data'):
        TokenManager.set_token(response['data'])

    return response


def get_user_data_from_shad(user_uuid, landing_id):
    """
    Validate UUID and get user data, handling token expiration automatically.

    Args:
        user_uuid: The user's UUID to fetch data for
        landing_id: The landing ID for authentication

    Returns:
        API response with user data

    Raises:
        ValueError: If UUID is invalid, authentication fails, or response contains errors
    """
    # Format uuid as Shad uuids format
    user_uuid = _format_uuid_to_shad_format(user_uuid)

    # First ensure we have a valid UUID
    try:
        uuid.UUID(str(user_uuid))
    except ValueError:
        raise ValueError("Invalid UUID format")

    # Ensure we're logged in or try initial login
    if not TokenManager.get_token():
        login_response = _login_to_shad(landing_id)
        if not login_response.get('data'):
            raise ValueError("Initial login failed")

    # Try to get user data
    url = f'{SHAD_API_URL}/ShadEvent?UserHashId={user_uuid}'
    headers = {
        "Authorization": f"Bearer {TokenManager.get_token()}"
    }
    params = {}

    response = get(url, params, headers=headers)

    # Check for expired token and try relogin once
    if response.get('status') == 401 or response.get('error') == 'token_expired':
        login_response = _login_to_shad(landing_id)
        if not login_response.get('data'):
            raise ValueError("Failed to refresh token")

        # Retry the request with new token
        response = get(url, params, headers={
            "Authorization": f"Bearer {TokenManager.get_token()}"
        })

    status = response.get('status_code')
    error_message = response.get('data').get('error')

    if error_message or (isinstance(status, int) and status >= 400):
        raise ValueError(f"API Error: {error_message} (Status: {status})")

    return response


def _format_uuid_to_shad_format(input_uuid):
    """
    Formats a UUID string into the desired format: E7-17-70-D6-D0-37-26-FE-4F-74-A7-ED-89-23-46-FC.

    Args:
        input_uuid (str): A UUID string (with or without dashes).

    Returns:
        str: The formatted UUID string.
    """
    # Remove any existing dashes and convert to uppercase
    clean_uuid = input_uuid.replace('-', '').upper()

    # Split into groups of two characters and join with dashes
    formatted_uuid = '-'.join(clean_uuid[i:i+2]
                              for i in range(0, len(clean_uuid), 2))

    return formatted_uuid


def update_user_info_by_shad_data(user_instance, user_data):
    """
    Updates a user instance with the provided user_data dictionary.

    Args:
        user_instance: The user instance to update.
        user_data (dict): The data containing user information.

    Returns:
        The updated user instance.
    """
    # Extracting relevant data from user_data
    data = user_data.get("data", {})

    # Mapping user_data fields to the user instance fields
    user_instance.first_name = data.get("name") or user_instance.first_name
    user_instance.last_name = data.get("family") or user_instance.last_name
    user_instance.phone_number = data.get(
        "mobile") or user_instance.phone_number
    user_instance.gender = data.get("gender") or user_instance.gender
    user_instance.province = data.get("provinceName") or user_instance.province

    user_instance.save()
