from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.attributes.views.currency import get_currencies

router = DefaultRouter()

urlpatterns = [
    path('currencies/', get_currencies),
]

urlpatterns += router.urls
