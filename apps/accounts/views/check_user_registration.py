from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from apps.accounts.utils.user_management import find_user_in_website

User = get_user_model()


@api_view(['GET'])
def check_user_registration(request):
    username = request.query_params.get('username', None)
    if not username:
        return Response({'error': 'Username parameter is required'}, status=400)

    website = request.headers.get("Website")
    user = find_user_in_website(
        user_data={'username': username},
        website=website,
    )

    return Response({'is_registered': bool(user)})
