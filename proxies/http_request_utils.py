import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rest_framework import status
from rest_framework.response import Response


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


def get(url, params, headers=None):
    try:
        session = get_retry_session()
        response = session.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json()
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "status_code": 500,
            "error": f"Failed to process GET request after retries: {str(e)}",
        }


def post(url, payload, headers=None):
    try:
        session = get_retry_session()
        response = session.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json()
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "status_code": 500,
            "error": f"Failed to process POST request after retries: {str(e)}",
        }
