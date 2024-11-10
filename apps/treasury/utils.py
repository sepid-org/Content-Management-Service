from .models import Spend


def has_user_spent_on_object(user_uuid, object_id):
    """
    Check if a spend record exists for the given user and object.

    Args:
        user_uuid (str): The UUID of the user.
        object_id (int): The ID of the object.

    Returns:
        bool: True if the user has spent on the object, otherwise False.
    """
    return Spend.objects.filter(user=user_uuid, object_id=object_id).exists()
