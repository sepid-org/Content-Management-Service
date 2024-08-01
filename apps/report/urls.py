from django.urls import path
from .views import export, export_csv,get_excel

urlpatterns = [
    path('export_json/', export, name='export_json'),
    path('export_csv/', export_csv, name='export_csv'),
    path('export_excel/', get_excel, name='export_csv'),

]
