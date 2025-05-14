import string
import random
import xml.etree.ElementTree as ET
import hashlib
import urllib.parse
import requests
from django.conf import settings

BBB_BASE_URL = settings.BBB_BASE_URL
BBB_SECRET_KEY = settings.BBB_SECRET_KEY


def generate_meeting_id(length: int = 8) -> str:
    """
    Returns a random alphanumeric string of given length.
    Adjust `length` to taste.
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def _generate_checksum(api_method: str, query_string: str) -> str:
    """Generate BBB API checksum using SHA-1 hashing.

    Args:
        api_method: BBB API method name (e.g., 'create', 'join')
        query_string: URL-encoded query parameters

    Returns:
        SHA-1 checksum as hexadecimal string
    """
    return hashlib.sha1(
        f"{api_method}{query_string}{BBB_SECRET_KEY}".encode()
    ).hexdigest()


def build_api_endpoint(api_method: str, params: dict) -> str:
    """Construct a complete BBB API URL with valid checksum.

    Args:
        api_method: BBB API method name
        params: Dictionary of API parameters

    Returns:
        Complete URL with checksum
    """
    sorted_params = dict(sorted(params.items())
                         )  # Sort parameters alphabetically
    query_string = urllib.parse.urlencode(sorted_params, doseq=True)
    checksum = _generate_checksum(api_method, query_string)
    return f"{BBB_BASE_URL}/{api_method}?{query_string}&checksum={checksum}"


def ensure_meeting_session(meeting_id: str, meeting_name: str) -> bool:
    """Create or verify a BBB meeting session by inspecting the XML returncode."""
    params = {
        'name': meeting_name,
        'meetingID': meeting_id,
        'record': True,
        'autoStartRecording': False,
        'allowStartStopRecording': True,
        'attendeePW': 'A_RANDOM_PASSWORD_FOR_ATTENDEE',
        'moderatorPW': 'A_RANDOM_PASSWORD_FOR_MODERATOR',

    }
    endpoint = build_api_endpoint('create', params)
    response = requests.get(endpoint)

    # parse the XML response
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError:
        # couldn’t even parse XML
        return False

    # grab the text of <returncode>
    returncode = root.findtext('returncode')

    if returncode == 'SUCCESS':
        return True
    else:
        # you could log root.findtext('messageKey') / root.findtext('message')
        return False


def generate_meeting_join_url(
    user_name: str,
    user_id: str,
    meeting_id: str,
    is_moderator: bool = False
) -> str:
    """Generate join URL for a BBB meeting session.

    Args:
        user_name: Display name for the joining user
        user_id: Unique identifier for the user
        meeting_id: Target meeting ID
        is_moderator: Whether user should join as moderator

    Returns:
        Complete join URL with checksum
    """
    params = {
        'fullName': user_name,
        'meetingID': meeting_id,
        'userID': user_id,
        'role': 'MODERATOR' if is_moderator else 'VIEWER',
        'redirect': 'true',
        'joinViaHtml5': 'true',
        'userdata-bbb_skip_check_audio': 'true',
        'password': 'A_RANDOM_PASSWORD_FOR_MODERATOR' if is_moderator else 'A_RANDOM_PASSWORD_FOR_ATTENDEE'
    }

    return build_api_endpoint('join', params)


def is_meeting_running(meeting_id: str) -> bool:
    """Return True iff BBB reports this meeting as running."""
    params = {'meetingID': meeting_id}
    endpoint = build_api_endpoint('getMeetingInfo', params)
    resp = requests.get(endpoint)
    try:
        root = ET.fromstring(resp.content)
        return root.findtext('running') == 'true'
    except ET.ParseError:
        return False
