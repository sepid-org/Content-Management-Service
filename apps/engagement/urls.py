from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.engagement.views.answer import AnswerViewSet
from apps.engagement.views.answer_sheet import AnswerSheetViewSet
from apps.engagement.views.button import submit_button_widget
from apps.engagement.views.content_log import ContentLogView

router = DefaultRouter()

urlpatterns = [
    path('submit-button/', submit_button_widget),
    path('content-log/', ContentLogView.as_view(), name='content-log'),
]

router.register(r'answers', AnswerViewSet, basename='answers')
router.register(r'answer-sheets', AnswerSheetViewSet, basename='answer-sheets')

urlpatterns += router.urls
