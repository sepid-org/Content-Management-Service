from rest_framework_simplejwt.authentication import JWTAuthentication


class SafeTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request=request)
        except:
            return None
