import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_retry_session(retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504)):
    """
    Create a requests session with retry capabilities and UTF-8 encoding for responses.

    Args:
        retries (int): Number of total retries to allow.
        backoff_factor (float): A backoff factor to apply between attempts.
        status_forcelist (tuple): HTTP status codes to retry on.

    Returns:
        requests.Session: A configured session with retry capabilities and UTF-8 response encoding.
    """
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Ensure that responses use UTF-8 encoding by default
    session.headers.update({'Accept-Charset': 'utf-8'})

    return session


def get(url, params, headers=None):
    """
    Execute a GET request with retry and UTF-8 encoding.

    Args:
        url (str): URL for the GET request.
        params (dict): URL parameters.
        headers (dict, optional): HTTP headers.

    Returns:
        dict: Dictionary with the request status, HTTP status code, and data or error message.
    """
    session = get_retry_session()
    try:
        response = session.get(url, params=params, headers=headers)
        # Explicitly set encoding to UTF-8
        response.encoding = 'utf-8'
        # Raise HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
        # Try parsing JSON; fallback to raw text if JSON parsing fails.
        try:
            data = response.json()
        except ValueError:
            data = response.text
        return {
            "success": True,
            'status_code': response.status_code,
            'data': data
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            'status_code': getattr(e.response, 'status_code', 500),
            'error': str(e)
        }


def post(url, payload, headers=None):
    """
    Execute a POST request with retry and UTF-8 encoding.

    Args:
        url (str): URL for the POST request.
        payload (dict): JSON payload for the request.
        headers (dict, optional): HTTP headers.

    Returns:
        dict: Dictionary with the request status, HTTP status code, and data or error message.
    """
    try:
        # Obtain a session with retry capabilities and UTF-8 encoding support
        session = get_retry_session()
        response = session.post(url, json=payload, headers=headers)

        # Ensure the response is interpreted using UTF-8 encoding
        response.encoding = 'utf-8'

        # Raise an exception if the HTTP request returned an unsuccessful status code
        response.raise_for_status()

        # Attempt to decode the response as JSON; fallback to raw text if decoding fails
        try:
            data = response.json()
        except ValueError:
            data = response.text

        return {
            "success": True,
            'http_status': response.status_code,
            'data': data
        }
    except requests.exceptions.RequestException as e:
        # Capture HTTP status code from the response if available, else set to 500
        return {
            "success": False,
            'http_status': getattr(e.response, 'status_code', 500),
            'error': str(e)
        }
