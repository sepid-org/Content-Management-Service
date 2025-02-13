from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):
    def post(self, request):
        response = Response({"detail": "Successfully logged out"}, status=200)

        # پاک کردن کوکی‌ها
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        # باطل کردن توکن ریفرش (اختیاری)
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                pass

        return response
