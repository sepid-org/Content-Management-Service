from rest_framework.viewsets import ModelViewSet
from django.core.cache import cache
from django.utils.functional import classproperty


class CacheModelViewSet(ModelViewSet):
    # Configuration options with defaults
    cache_timeout = 60 * 15  # 15 minutes
    add_no_cache_headers = True

    @classproperty
    def cache_key_prefix(cls):
        return f'{cls.__name__.lower()}'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.add_no_cache_headers:
            self._add_no_cache_headers(response)
        return response

    def _cached_list(self, request, *args, **kwargs):
        cache_key = f"{self.cache_key_prefix}:list:{request.get_full_path()}"
        cached_response = cache.get(cache_key)

        if cached_response is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response, self.cache_timeout)
            return response

        return cached_response

    def list(self, request, *args, **kwargs):
        return self._cached_list(request, *args, **kwargs)

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

    def _add_no_cache_headers(self, response):
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

    def _invalidate_list_cache(self):
        cache.delete_pattern(f'{self.cache_key_prefix}:list:*')
