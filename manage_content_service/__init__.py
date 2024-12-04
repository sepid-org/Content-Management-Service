from manage_content_service.celery_app import app as celery_app
import time

__all__ = ("celery_app",)
start_time = time.time()
