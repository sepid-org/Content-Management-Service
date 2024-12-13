from django.urls import path
from .views import get_participants, get_program_merchandises_purchases, get_answer_sheets

urlpatterns = [
    path('participants/', get_participants, name='participants-info'),
    path('answer-sheets/', get_answer_sheets, name='answer-sheets-excel-file'),
    path('program-merchandises-purchases/',
         get_program_merchandises_purchases, name='program_merchandises_purchases'),
]
