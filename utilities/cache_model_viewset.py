from rest_framework.viewsets import ModelViewSet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.encoding import iri_to_uri


class CacheModelViewSet(ModelViewSet):
    cache_timeout = 60 * 15  # 15 minutes
    add_no_cache_headers = True
    lookup_field = 'pk'  # Default to 'pk', can be overridden in subclasses

    def get_cache_key_prefix(self):
        return f"viewset-{self.__class__.__name__}"

    def get_list_cache_key(self, request):
        key_prefix = self.get_cache_key_prefix()
        full_path = iri_to_uri(request.get_full_path())
        return f"views.decorators.cache.cache_page.{key_prefix}-list.{full_path}"

    def get_object_cache_key(self, lookup_value):
        key_prefix = self.get_cache_key_prefix()
        return f"views.decorators.cache.cache_page.{key_prefix}-object.{self.lookup_field}.{lookup_value}"

    @method_decorator(cache_page(cache_timeout, key_prefix=lambda request: request.resolver_match.func.view_class().get_cache_key_prefix() + '-list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(cache_timeout, key_prefix=lambda request: request.resolver_match.func.view_class().get_cache_key_prefix() + '-object'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def _invalidate_list_cache(self):
        cache_key = self.get_list_cache_key(self.request)
        cache.delete(cache_key)

    def _invalidate_object_cache(self, obj):
        # Invalidate cache for both pk and slug if available
        cache_key_pk = self.get_object_cache_key(obj.pk)
        cache.delete(cache_key_pk)

        if hasattr(obj, 'slug'):
            cache_key_slug = self.get_object_cache_key(obj.slug)
            cache.delete(cache_key_slug)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self._invalidate_list_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self._invalidate_list_cache()
        self._invalidate_object_cache(self.get_object())
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self._invalidate_list_cache()
        self._invalidate_object_cache(self.get_object())
        return response

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()  # Get the object before deletion
        response = super().destroy(request, *args, **kwargs)
        self._invalidate_list_cache()
        self._invalidate_object_cache(obj)
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
