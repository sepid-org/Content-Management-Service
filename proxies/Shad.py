import logging
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

    # Assuming that on success, the token is in response["data"]
    if response.get('success'):
        TokenManager.set_token(response['data'])

    return response


logger = logging.getLogger(__name__)


def get_user_data_from_shad(user_uuid, landing_id):
    """
    Fetch user data from Shad and handle token expiration.
    Initially sends the request using the raw user_uuid.
    If the response indicates a UUID format issue, it retries with the formatted UUID.

    Args:
        user_uuid: Raw user UUID
        landing_id: Landing ID used for authentication

    Returns:
        API response with user data

    Raises:
        ValueError: If UUID is invalid, login fails, or the API returns an error
    """
    logger.info("=== Starting get_user_data_from_shad ===")
    logger.info(f"Input user_uuid: {user_uuid}, landing_id: {landing_id}")

    # Ensure we are logged in or perform initial login if needed
    token = TokenManager.get_token()
    logger.info(f"Initial token: {token}")
    if not token:
        logger.info("No token found. Attempting initial login.")
        login_response = _login_to_shad(landing_id)
        logger.info(f"Login response: {login_response}")
        if login_response.get('success') is False:
            logger.info("Initial login failed")
            raise ValueError("Initial login failed")
        token = TokenManager.get_token()
        logger.info("Login successful.")
        logger.info(f"New token: {token}")

    # First attempt: use raw UUID
    url = f'{SHAD_API_URL}/ShadEvent?UserHashId={user_uuid}'
    headers = {"Authorization": f"Bearer {token}"}
    params = {}

    logger.info("Sending initial request to Shad API")
    logger.info(f"Request URL: {url}")
    logger.info(f"Request headers: {headers}")
    logger.info(f"Request params: {params}")

    response = get(url, params, headers=headers)
    logger.info(f"Initial response: {response}")

    # Handle token expiration
    if response.get('status_code') == 401 or response.get('error') == 'token_expired':
        logger.info("Token expired. Re-attempting login.")
        login_response = _login_to_shad(landing_id)
        logger.info(f"Re-login response: {login_response}")
        if login_response.get('success') is False:
            logger.info("Failed to refresh token")
            raise ValueError("Failed to refresh token")

        token = TokenManager.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        logger.info(f"New token after refresh: {token}")
        logger.info("Retrying request to Shad API with refreshed token")
        response = get(url, params, headers=headers)
        logger.info(f"Retry response: {response}")

    error_message = response.get('error')
    status_code = response.get('status_code')

    # If user not found with previous uuid format, retry fetching user data:
    if status_code == 404:
        logger.info(
            "Initial request failed due to UUID format error. Applying formatting and retrying.")
        formatted_uuid = _format_uuid_to_shad_format(user_uuid)
        logger.info(f"Formatted user_uuid: {formatted_uuid}")
        url = f'{SHAD_API_URL}/ShadEvent?UserHashId={formatted_uuid}'
        response = get(url, params, headers=headers)
        logger.info(f"Retry with formatted UUID response: {response}")
        # Update error message
        error_message = response.get('error')

    # Final error handling
    if error_message or (isinstance(status_code, int) and status_code >= 400):
        logger.info(f"API Error: {error_message} (Status: {status_code})")
        raise ValueError(f"API Error: {error_message} (Status: {status_code})")

    logger.info("get_user_data_from_shad completed successfully")
    logger.info(f"Final response: {response}")
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
    # Extract relevant data from the response
    data = user_data.get("data", {})

    # Map user_data fields to the user instance fields
    user_instance.first_name = data.get("name") or user_instance.first_name
    user_instance.last_name = data.get("family") or user_instance.last_name
    user_instance.phone_number = data.get(
        "mobile") or user_instance.phone_number
    user_instance.gender = data.get("gender") or user_instance.gender
    user_instance.province = data.get("provinceName") or user_instance.province

    user_instance.save()
