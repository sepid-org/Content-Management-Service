from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.response.views.answer_view import AnswerViewSet

router = DefaultRouter()

urlpatterns = []

router.register(r'answers', AnswerViewSet, basename='answers')

urlpatterns += router.urls
