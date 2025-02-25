import secrets
import string


def make_random_password(length, allowed_chars=None):
    """
    Generate a secure random password using cryptographically strong randomness.

    Args:
        code_length (int): Length of the password to generate
        allowed_chars (str, optional): String containing allowed characters. 
            Defaults to ASCII letters, digits, and punctuation.

    Returns:
        str: Generated password with specified length using allowed characters

    Raises:
        ValueError: If allowed_chars is empty or code_length is less than 1
    """
    # Set default character set if not provided
    if allowed_chars is None:
        allowed_chars = string.ascii_letters + string.digits + string.punctuation

    # Validate parameters
    if not isinstance(length, int) or length < 1:
        raise ValueError("code_length must be a positive integer")

    if not allowed_chars:
        raise ValueError("allowed_chars must contain at least one character")

    # Generate password using cryptographically secure random choices
    return ''.join(secrets.choice(allowed_chars) for _ in range(length))
