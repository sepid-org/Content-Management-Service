from django.views.decorators.cache import cache_page
from django.utils.encoding import iri_to_uri
from functools import wraps


def custom_cache_page(timeout, *, cache_key_prefix):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Create a custom cache key
            cache_key = f"{cache_key_prefix}:{iri_to_uri(request.get_full_path())}"

            # Use Django's cache_page with our custom key
            return cache_page(timeout, key_prefix=cache_key)(view_func)(request, *args, **kwargs)
        return _wrapped_view
    return decorator
