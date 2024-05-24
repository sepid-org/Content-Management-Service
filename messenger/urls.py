from django.urls import path
from messenger.views import *

urlpatterns = [
    path('test/',  send_email)
]
