from functools import wraps
from rest_framework.response import Response
from django.core.cache import cache


class ModelViewSetCache:
    cache_timeout = 60 * 15 * 60  # 60 minutes
    lookup_field = 'pk'  # Default to 'pk', can be overridden in subclasses

    def __init__(self, model_view_set_name) -> None:
        self.model_view_set_name = model_view_set_name

    def get_list_cache_key(self, query_params=None):
        if query_params:
            query_string = "&".join(
                f"{k}={v}" for k, v in sorted(query_params.items()))
            return f"{self.model_view_set_name}:list:{query_string}"
        return f"{self.model_view_set_name}:list"

    def get_object_cache_key(self, object_id):
        return f"{self.model_view_set_name}:retrieve:{object_id}"

    def invalidate_list_cache(self):
        if hasattr(cache, 'delete_pattern'):
            # For cache backends that support pattern deletion (e.g., Redis)
            cache.delete_pattern(f"{self.model_view_set_name}:list*")
        else:
            # For cache backends that don't support pattern deletion
            cache.delete(self.get_list_cache_key())

    def invalidate_object_cache(self, lookup_field):
        cache_key_id = self.get_object_cache_key(lookup_field)
        cache.delete(cache_key_id)

    def cache_response(self, timeout=None):
        def decorator(view_func):
            @wraps(view_func)
            def wrapper(view_instance, request, *args, **kwargs):
                # Determine if it's a list or retrieve action
                if kwargs.get(view_instance.lookup_field):
                    cache_key = self.get_object_cache_key(
                        kwargs[view_instance.lookup_field])
                else:
                    cache_key = self.get_list_cache_key(request.query_params)

                # Try to get the cached response
                cached_data = cache.get(cache_key)
                if cached_data is not None:
                    return Response(cached_data)

                # If not cached, call the view function
                response = view_func(view_instance, request, *args, **kwargs)

                # Cache the response data
                cache_timeout = timeout or self.cache_timeout
                cache.set(cache_key, response.data, timeout=cache_timeout)

                return response
            return wrapper
        return decorator

    @classmethod
    def cached_view(cls, timeout=None):
        def decorator(view_func):
            @wraps(view_func)
            def wrapper(view_instance, request, *args, **kwargs):
                cache_instance = cls(view_instance.__class__.__name__)
                return cache_instance.cache_response(timeout)(view_func)(view_instance, request, *args, **kwargs)
            return wrapper
        return decorator
