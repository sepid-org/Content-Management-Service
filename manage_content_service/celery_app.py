import os
from celery import Celery
# import celeryconfig

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage_content_service.settings.development')
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manage_content_service.settings.base")
print(os.environ.get('DJANGO_SETTINGS_MODULE'))
print("hi")
# print(celeryconfig)
app = Celery()
print('hii')
app.config_from_object('django.conf:settings', namespace="CELERY")
print('hijjj')
app.autodiscover_tasks()