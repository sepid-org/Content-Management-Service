from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions


class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # دریافت توکن از کوکی
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None  # اگر توکن وجود نداشت، احراز هویت انجام نشود

        try:
            # استفاده از JWTAuthentication برای اعتبارسنجی توکن
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(
                access_token)  # اعتبارسنجی توکن
            # دریافت کاربر مرتبط با توکن
            user = jwt_auth.get_user(validated_token)

            return (user, validated_token)  # بازگرداندن کاربر و توکن
        except (InvalidToken, TokenError) as e:
            # اگر توکن نامعتبر بود، خطای احراز هویت ایجاد کنید
            raise exceptions.AuthenticationFailed('Invalid token') from e
