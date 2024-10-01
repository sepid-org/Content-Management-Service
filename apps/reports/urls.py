from django.urls import path
from .views import get_form_respondents_info, get_form_respondents_answers, get_program_merchandises_purchases , get_form_id_give_answer

urlpatterns = [
    path('form-respondents-info/', get_form_respondents_info,
         name='form_respondents_info'),
    path('hi/', get_form_id_give_answer),
    path('form-respondents-answers/',
         get_form_respondents_answers, name='form_respondents_answers'),
    path('program-merchandises-purchases/',
         get_program_merchandises_purchases, name='program_merchandises_purchases'),
]
