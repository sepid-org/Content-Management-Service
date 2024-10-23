from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.response.views.answer_view import AnswerViewSet
from apps.response.views.response import submit_button_widget

router = DefaultRouter()

urlpatterns = [
    path('submit-button/', submit_button_widget),
]

router.register(r'answers', AnswerViewSet, basename='answers')

urlpatterns += router.urls
