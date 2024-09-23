from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.fsm.views.paper_view import PaperViewSet
from apps.fsm.views.object_view import ObjectViewSet

from .views.article_view import ArticleViewSet
from .views.program_view import ProgramViewSet
from .views.fsm_view import *
from .views.edge_view import *
from .views.registration_receipt_view import RegistrationReceiptViewSet
from .views.registration_view import RegistrationViewSet, RegistrationFormAdminViewSet
from .views.certificate_view import CertificateTemplateViewSet, FontViewSet
from .views.state_view import StateViewSet, HintViewSet
from .views.team_view import *
from .views.player_view import *

router = DefaultRouter()

router.register(r'program', ProgramViewSet, basename='programs')
router.register(r'fsm', FSMViewSet, basename='fsms')
router.register(r'article', ArticleViewSet, basename='articles')

router.register(r'form', RegistrationViewSet, basename='registration_form')
router.register(r'registration_form_admin', RegistrationFormAdminViewSet,
                basename='registration_admin_form')
router.register(r'certificate_templates',
                CertificateTemplateViewSet, basename='certificate_templates')
router.register(r'fonts', FontViewSet, basename='fonts')
router.register(r'receipts', RegistrationReceiptViewSet, basename='receipts')
router.register(r'team', TeamViewSet, basename='teams')
router.register(r'invitations', InvitationViewSet, basename='invitations')
router.register(r'state', StateViewSet, basename='states')
router.register(r'paper', PaperViewSet, basename='papers')
router.register(r'edge', EdgeViewSet, basename='edges')
router.register(r'hint', HintViewSet, basename='hints')
router.register(r'objects', ObjectViewSet, basename='objects')
router.register(r'player', PlayerViewSet, basename='players')

urlpatterns = [
    path('', include(router.urls)),
]
