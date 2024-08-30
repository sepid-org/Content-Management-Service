from rest_framework.viewsets import ModelViewSet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.encoding import iri_to_uri


class CacheModelViewSet(ModelViewSet):
    cache_timeout = 60 * 15  # 15 minutes
    cache_list_only = True
    add_no_cache_headers = True

    def get_cache_key(self, request):
        return f"viewset-{self.__class__.__name__}-list-{iri_to_uri(request.get_full_path())}"

    @method_decorator(cache_page(cache_timeout))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def _invalidate_list_cache(self):
        # Instead of using delete_pattern, we'll delete the specific key
        cache_key = self.get_cache_key(self.request)
        cache.delete(cache_key)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self._invalidate_list_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self._invalidate_list_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self._invalidate_list_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self._invalidate_list_cache()
        return response

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.add_no_cache_headers:
            self._add_no_cache_headers(response)
        return response

    def _add_no_cache_headers(self, response):
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
