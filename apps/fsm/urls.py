from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.fsm.views.edge_view import EdgeViewSet
from apps.fsm.views.form_view import FormViewSet
from apps.fsm.views.fsm_view import FSMViewSet
from apps.fsm.views.resource import ResourceViewSet, HintViewSet
from apps.fsm.views.paper_view import PaperViewSet
from apps.fsm.views.object_view import ObjectViewSet
from apps.fsm.views.player_view import PlayerViewSet

from apps.fsm.views.article_view import ArticleViewSet
from apps.fsm.views.registration_receipt_view import RegistrationReceiptViewSet
from apps.fsm.views.fsm_state_view import StateViewSet
from apps.fsm.views.team_view import InvitationViewSet, TeamViewSet

router = DefaultRouter()

router.register(r'fsm', FSMViewSet, basename='fsms')
router.register(r'article', ArticleViewSet, basename='articles')

router.register(r'form', FormViewSet, basename='form')
router.register(r'receipts', RegistrationReceiptViewSet, basename='receipts')
router.register(r'team', TeamViewSet, basename='teams')
router.register(r'invitations', InvitationViewSet, basename='invitations')
router.register(r'state', StateViewSet, basename='states')
router.register(r'paper', PaperViewSet, basename='papers')
router.register(r'edge', EdgeViewSet, basename='edges')
router.register(r'hint', HintViewSet, basename='hints')
router.register(r'resources', ResourceViewSet, basename='resources')
router.register(r'objects', ObjectViewSet, basename='objects')
router.register(r'player', PlayerViewSet, basename='players')

urlpatterns = [
    path('', include(router.urls)),
]
