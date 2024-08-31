from typing import Any
from rest_framework.viewsets import ModelViewSet

from utilities.cache_enabled_model_viewset.model_view_set_cache import ModelViewSetCache


class CacheEnabledModelViewSet(ModelViewSet):
    add_no_cache_headers = True

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.model_view_set_name = self.__class__.__name__
        self.cache = ModelViewSetCache(
            model_view_set_name=self.model_view_set_name)

    @ModelViewSetCache.cached_view()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @ModelViewSetCache.cached_view()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self.cache.invalidate_list_cache(request.headers.get('website'))
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.cache.invalidate_list_cache(request.headers.get('website'))
        self.cache.invalidate_object_cache(kwargs[self.lookup_field])
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self.cache.invalidate_list_cache(request.headers.get('website'))
        self.cache.invalidate_object_cache(self.get_object())
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self.cache.invalidate_list_cache(request.headers.get('website'))
        self.cache.invalidate_object_cache(kwargs[self.lookup_field])
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
