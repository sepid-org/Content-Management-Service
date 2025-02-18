from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.roadmap.views import get_player_transited_path, get_fsm_roadmap

router = DefaultRouter()

urlpatterns = [
    path('get_player_transited_path/', get_player_transited_path),
    path('get_fsm_roadmap/', get_fsm_roadmap),
]

urlpatterns += router.urls
