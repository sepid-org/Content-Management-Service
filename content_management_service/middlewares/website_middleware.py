from django.utils.deprecation import MiddlewareMixin
from proxies.website_service.main import get_website


class WebsiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        website_name = request.headers.get("Website")
        website = get_website(website_name)
        request.website = website
