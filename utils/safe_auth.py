from rest_framework_simplejwt.authentication import JWTAuthentication


class SafeTokenAuthentication(JWTAuthentication):
    keyword = 'JWT'

    def authenticate(self, request):
        try:
            return super().authenticate(request=request)
        except:
            return None
