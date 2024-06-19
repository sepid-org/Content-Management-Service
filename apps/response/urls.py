from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.answer_view import AnswerViewSet

router = DefaultRouter()

urlpatterns = []

router.register(r'answers', AnswerViewSet, basename='answers')
urlpatterns += router.urls
