from functools import wraps
from rest_framework.response import Response
from django.core.cache import cache


class ModelViewSetCache:
    cache_timeout = 60 * 15  # 15 minutes
    lookup_field = 'pk'  # Default to 'pk', can be overridden in subclasses

    def get_list_cache_key(self, key_prefix):
        return f"{key_prefix}:list"

    def get_object_cache_key(self, key_prefix, lookup_value):
        return f"{key_prefix}:retrieve:{lookup_value}"

    def invalidate_list_cache(self):
        cache_key = self.get_list_cache_key(self.request)
        cache.delete(cache_key)

    def invalidate_object_cache(self, obj):
        # Invalidate cache for both pk and slug if available
        cache_key_pk = self.get_object_cache_key(obj.pk)
        cache.delete(cache_key_pk)

        if hasattr(obj, 'slug'):
            cache_key_slug = self.get_object_cache_key(obj.slug)
            cache.delete(cache_key_slug)

    def decorator(self, timeout=cache_timeout, key_prefix=''):
        def decorator(view_func):
            @wraps(view_func)
            def _wrapped_view(request, *args, **kwargs):

                # Determine if it's a retrieve or list function
                is_retrieve = view_func.__name__ == 'retrieve'
                is_list = view_func.__name__ == 'list'

                # Generate a unique cache key
                if is_retrieve:
                    # Get pk or slug
                    pk = kwargs.get('pk')
                    slug = kwargs.get('slug')
                    if pk or slug:
                        key = self.get_object_cache_key(key_prefix, pk or slug)
                    else:
                        raise Exception('no pk or slug provided')
                if is_list:
                    key = self.get_list_cache_key(key_prefix)

                cached_response = cache.get(key)

                if cached_response:
                    # If response is found in cache, return it with appropriate cache headers
                    response = Response(cached_response)
                    response['Cache-Control'] = f'max-age={timeout}, public'
                    return response

                # Call the original view function
                response = view_func(request, *args, **kwargs)

                # Cache the response data if the response is an instance of Response
                if isinstance(response, Response):
                    cache.set(key, response.data, timeout=timeout)

                    # Set cache headers in the response
                    response['Cache-Control'] = f'max-age={timeout}, public'

                return response
            return _wrapped_view
        return decorator
