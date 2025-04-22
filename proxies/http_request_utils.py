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

    # Define a response hook to force UTF-8 encoding
    def force_utf8(response, *args, **kwargs):
        response.encoding = 'utf-8'
        return response

    # Add the hook to the session so that every response is processed by it
    session.hooks['response'] = [force_utf8]

    return session


def get_retry_session(retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504)):
    """
    Create a requests session with retry capabilities and set the response encoding to UTF-8.

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

    # Define a response hook to ensure the encoding is set to UTF-8
    def force_utf8(response, *args, **kwargs):
        response.encoding = 'utf-8'
        return response

    session.hooks['response'] = [force_utf8]
    return session


def extract_data(response_data):
    """
    If the response contains a 'data' key, extract and return its value.

    Args:
        response_data (dict or any): The original data returned from the request.

    Returns:
        The extracted inner data if present, otherwise the original response_data.
    """
    if isinstance(response_data, dict) and 'data' in response_data:
        return response_data['data']
    return response_data


def get(url, params, headers=None):
    """
    Execute a GET request with retry capabilities and extract nested data if present.

    Args:
        url (str): The URL for the GET request.
        params (dict): URL parameters.
        headers (dict, optional): HTTP headers.

    Returns:
        dict: A dictionary with the request status, HTTP status code, and either the data or an error message.
    """
    session = get_retry_session()
    try:
        response = session.get(url, params=params, headers=headers)
        # Raise HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
        # Try parsing JSON; fallback to raw text if JSON parsing fails.
        try:
            data = response.json()
        except ValueError:
            data = response.text

        # Extract nested data if available
        data = extract_data(data)

        return {
            "success": True,
            "status_code": response.status_code,
            "data": data
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "status_code": getattr(e.response, 'status_code', 500),
            "error": str(e)
        }


def post(url, payload, headers=None):
    """
    Execute a POST request with retry capabilities and extract nested data if present.

    Args:
        url (str): The URL for the POST request.
        payload (dict): The JSON payload to send.
        headers (dict, optional): HTTP headers.

    Returns:
        dict: A dictionary with the request status, HTTP status code, and either the data or an error message.
    """
    session = get_retry_session()
    try:
        # Obtain a session with retry capabilities
        session = get_retry_session()
        response = session.post(url, json=payload, headers=headers)

        # Raise an exception if the HTTP request returned an unsuccessful status code
        response.raise_for_status()

        # Attempt to decode the response as JSON; fallback to raw text if decoding fails
        try:
            data = response.json()
        except ValueError:
            data = response.text

        # Extract nested data if available
        data = extract_data(data)

        return {
            "success": True,
            "http_status": response.status_code,
            "data": data
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "http_status": getattr(e.response, 'status_code', 500),
            "error": str(e)
        }
