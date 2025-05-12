from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.meeting.views.meeting import MeetingViewSet

router = DefaultRouter()

router.register(r'meetings', MeetingViewSet, basename='meeting')

urlpatterns = [
    path('', include(router.urls)),
]
