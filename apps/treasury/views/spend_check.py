from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.treasury.serializers.spend import SpendCheckSerializer
from apps.treasury.utils import has_user_spent_on_object


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def has_spent_on_object(request):
    """
    Check if the user has already spent on the specified object.

    Expected request body:
    {
        "object_id": "123"
    }
    """
    # Validate input data
    serializer = SpendCheckSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    object_id = serializer.validated_data['object_id']
    user_uuid = str(request.user.id)

    # Use utility function to check if a spend record exists
    has_spent = has_user_spent_on_object(user_uuid, object_id)

    return Response({
        "object_id": object_id,
        "has_spent": has_spent
    }, status=status.HTTP_200_OK)
