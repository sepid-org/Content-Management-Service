from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views.check_user_registration import check_user_registration
from apps.accounts.views.change_password import ChangePasswordView
from apps.accounts.views.change_phone_number import change_phone_number_view
from apps.accounts.views.check_auth import CheckAuthenticationView
from apps.accounts.views.google_login import GoogleLogin
from apps.accounts.views.logout import LogoutView
from apps.accounts.views.otp_login import OTPLoginView
from apps.accounts.views.simple_login import SimpleLogin
from apps.accounts.views.studentship_view import StudentshipViewSet
from apps.accounts.views.institute_view import InstituteViewSet, SchoolViewSet
from apps.accounts.views.profile_view import ProfileViewSet
from apps.accounts.views.user import UserViewSet
from apps.accounts.views.user_list_view import UserListAPIView
from apps.accounts.views.uuid_login import UserIDLoginView
from apps.accounts.views.verification_code import VerificationCodeView

router = DefaultRouter()
router.register(r'accounts', UserViewSet, basename='accounts')
router.register(r'institutes', InstituteViewSet, basename='institutes')
router.register(r'schools', SchoolViewSet, basename='schools')
router.register(r'profile', ProfileViewSet, basename='profiles')
router.register(r'studentship', StudentshipViewSet, basename='studentships')

urlpatterns = [
    path('accounts/check-user-registration/',
         check_user_registration,
         name='check-user-registration'),

    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/check-authentication/',
         CheckAuthenticationView.as_view(), name='check-authentication'),
    path('accounts/refresh/', TokenRefreshView.as_view(), name='refresh_token'),

    path('accounts/simple-login/', SimpleLogin.as_view(), name='simple-login'),
    path('accounts/otp-login/', OTPLoginView.as_view(), name='otp-login'),
    path("accounts/google-login/", GoogleLogin.as_view(), name="google-login"),
    path("accounts/uuid-login/", UserIDLoginView.as_view(), name="uuid-login"),

    path('accounts/verification-code/', VerificationCodeView.as_view(),
         name="send-verification-code"),
    path('accounts/change-password/',
         ChangePasswordView.as_view(), name="change-password"),
    path("accounts/change-phone-number/",
         change_phone_number_view, name="change-phone-number"),
    path('accounts/user-list/', UserListAPIView.as_view(), name='user-list'),
] + router.urls
