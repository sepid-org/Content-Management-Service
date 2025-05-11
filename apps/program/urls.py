from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.fsm.views.certificate_view import CertificateTemplateViewSet, FontViewSet
from apps.fsm.views.program_view import ProgramViewSet
from apps.fsm.views.registration_admin_view import RegistrationAdminViewSet
from apps.fsm.views.registration_view import RegistrationViewSet

router = DefaultRouter()

router.register(r'fonts', FontViewSet, basename='fonts')
router.register(r'program', ProgramViewSet, basename='programs')
router.register(r'registration', RegistrationViewSet, basename='registration')
router.register(r'registration_form_admin', RegistrationAdminViewSet,
                basename='registration_admin_form')
router.register(r'certificate_templates',
                CertificateTemplateViewSet, basename='certificate_templates')

urlpatterns = [
    path('', include(router.urls)),
]
