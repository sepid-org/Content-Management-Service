from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views.accounting_view import SendVerificationCode, UserViewSet, Login, ChangePassword, change_phone_number
from apps.accounts.views.google_login import GoogleLogin
from apps.accounts.views.studentship_view import StudentshipViewSet
from apps.accounts.views.institute_view import InstituteViewSet, SchoolViewSet
from apps.accounts.views.profile_view import ProfileViewSet
from apps.accounts.views.user_list_view import UserListAPIView

urlpatterns = [
    path('accounts/verification_code/', SendVerificationCode.as_view(),
         name="send_verification_code"),
    path('accounts/login/', Login.as_view(), name='create_token'),
    path('accounts/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('accounts/change_pass/', ChangePassword.as_view(), name="change_pass"),
    path("accounts/login-with-google/",
         GoogleLogin.as_view(), name="login-with-google"),
    path("accounts/change-phone-number/",
         change_phone_number, name="change-phone-number"),
    path('accounts/user-list/', UserListAPIView.as_view(), name='user-list'),
]

router = DefaultRouter()
router.register(r'accounts', UserViewSet, basename='accounts')
router.register(r'institutes', InstituteViewSet, basename='institutes')
router.register(r'schools', SchoolViewSet, basename='schools')
router.register(r'profile', ProfileViewSet, basename='profiles')
router.register(r'studentship', StudentshipViewSet, basename='studentships')

urlpatterns += router.urls
