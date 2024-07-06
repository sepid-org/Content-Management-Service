# email api: https://smtp.sepid.org/send-email/

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import aiohttp
import json

TARGET_URL = "http://127.0.0.1:8000/send-email/"

class ProxyPostView(View):
    async def post(self, request, *args, **kwargs):
        try:
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            if 'key' not in body_data or 'value' not in body_data:
                return JsonResponse({"detail": "Invalid data"}, status=400)
            data = {
                "key": body_data['key'],
                "value": body_data['value']
            }
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=400)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(TARGET_URL, json=data) as response:
                    response.raise_for_status()
                    response_data = await response.json()
            except aiohttp.ClientResponseError as e:
                return JsonResponse({"detail": f"Request to {TARGET_URL} failed with status {e.status}"}, status=e.status)
            except Exception as e:
                return JsonResponse({"detail": str(e)}, status=500)

        return JsonResponse({"message": "Request successful", "data": response_data}, status=200)