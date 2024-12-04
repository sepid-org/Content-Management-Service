# views.py
from django.http import JsonResponse
import time
from . import start_time


def health_check(request):
    """
    Health check for monitoring services.
    """
    # Here you can perform additional checks like database, cache, etc.

    # Assuming start_time is recorded when the app starts
    uptime = time.time() - start_time
    status = {
        "status": "ok",
        "uptime": uptime,
        "response_time": 0,  # You can calculate the response time here
        "apdex": 0,  # You can add Apdex calculation here
        "last_check": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(uptime)),
    }

    return JsonResponse(status)
