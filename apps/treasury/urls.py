from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.treasury.views.spend import spend_on_object
from apps.treasury.views.spend_check import has_spent_on_object

router = DefaultRouter()

urlpatterns = [
    path('spend-on-object/', spend_on_object),
    path('has-spent-on-object/', has_spent_on_object, name='has-spent-on-object'),
]

urlpatterns += router.urls
