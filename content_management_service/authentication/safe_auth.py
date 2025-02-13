from content_management_service.authentication.cookie_jwt_authentication import CookieJWTAuthentication


class SafeTokenAuthentication(CookieJWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request=request)
        except:
            return None
