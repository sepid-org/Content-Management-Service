from django.urls import path
from .views import export, export_csv,get_user_excel,get_answer_excel

urlpatterns = [
    path('export_json/', export, name='export_json'),
    path('export_csv/', export_csv, name='export_csv'),
    path('export_user_excel/', get_user_excel, name='export_csv'),
    path('export_answer_excel/',get_answer_excel, name='export_csv'),

]
