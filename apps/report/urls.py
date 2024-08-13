from django.urls import path
from .views import get_form_respondents_info, get_form_respondents_answers , get_form_respondents_bilit

urlpatterns = [
    path('form-respondents-info/', get_form_respondents_info,
         name='form_respondents_info'),
    path('form-respondents-answers/',
         get_form_respondents_answers, name='form_respondents_answers'),
    path('form-respondents-bilit/',
         get_form_respondents_bilit, name='form_respondents_answers'),
]
