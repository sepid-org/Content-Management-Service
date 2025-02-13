from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import exceptions
from django.http import HttpRequest

from apps.accounts.utils.set_cookies import set_cookies


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request: HttpRequest, *args, **kwargs):
        request.data.update(request.COOKIES)

        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            raise exceptions.AuthenticationFailed(
                'Refresh token not found in cookies'
            )

        request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        response = set_cookies(
            response,
            response.data['access'],
            response.data['refresh']
        )

        return response
