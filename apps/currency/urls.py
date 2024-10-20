from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.currency.views import spend_on_object

router = DefaultRouter()

urlpatterns = [
    path('spend-on-object/', spend_on_object),
]

urlpatterns += router.urls
