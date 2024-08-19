from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views.accounting_view import SendVerificationCode, UserViewSet, Login, ChangePassword, change_phone_number
from apps.accounts.views.check_authentication import CheckAuthenticationView
from apps.accounts.views.google_login import GoogleLogin
from apps.accounts.views.studentship_view import StudentshipViewSet
from apps.accounts.views.institute_view import InstituteViewSet, SchoolViewSet
from apps.accounts.views.profile_view import ProfileViewSet

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
    path('accounts/check-authentication/',
         CheckAuthenticationView.as_view(), name='check_authentication'),

    # path('registration-info/', RegistrationInfo.as_view(), name="registration_info"),
    # path('pay/', PayView.as_view(), name="pay"),
    # path('pay/verify-payment/', VerifyPayView.as_view(), name="verify-payment"),
    # # path('groupSignup/', GroupSignup.as_view(), name="group_signup"),
    # path('teamdata/', GetTeamData.as_view(), name="get_team_data"),
    # # path('changePass/', ChangePass.as_view(), name="change_password"),
    # path('changepass/', ChangePassword.as_view(), name='change_password'),
    # path('answerFile/', UploadAnswerView.as_view()),
    # re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
    #         activate, name='activate'),
    # path('userInfo/', UserInfo.as_view(), name="user_info"),
    # path('teamInfo/', TeamInfo.as_view(), name="team_info"),
    # path('teams/', Teams.as_view(), name="teams"),
    # path('verify-discount/', VerifyDiscount.as_view(), name="verify_discount"),
]

router = DefaultRouter()
router.register(r'accounts', UserViewSet, basename='accounts')
router.register(r'institutes', InstituteViewSet, basename='institutes')
router.register(r'schools', SchoolViewSet, basename='schools')
router.register(r'profile', ProfileViewSet, basename='profiles')
router.register(r'studentship', StudentshipViewSet, basename='studentships')
urlpatterns += router.urls
