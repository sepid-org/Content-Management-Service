from django.urls import path
from .views import get_user_excel, get_answer_excel

urlpatterns = [
    path('registration-form-participants/', get_user_excel,
         name='registration_form_participants'),
    path('registration-form-answers/', get_answer_excel, name='export_csv'),
]
