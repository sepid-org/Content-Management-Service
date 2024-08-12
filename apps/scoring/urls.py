from rest_framework import routers
from apps.scoring.views.apply_scores_on_user import apply_scores_on_user_view
from apps.scoring.views.cost_view import CostViewSet
from apps.scoring.views.reward_view import RewardViewSet
from apps.scoring.views.transaction_view import TransactionViewSet
from apps.scoring.views.scoretype_view import ScoreTypeViewSet
from django.urls import path
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = []

urlpatterns += router.urls
