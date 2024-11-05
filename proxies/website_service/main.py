from dataclasses import dataclass
from django.conf import settings
from django.core.cache import cache
from functools import wraps
import hashlib
import json
import logging
from typing import Any, Dict, Optional, Union
import requests
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@dataclass
class WMSConfig:
    """Configuration settings for WMS client."""
    base_url: str = settings.WMS_URL
    cache_timeout: int = getattr(settings, 'WMS_CACHE_TIMEOUT', 60 * 60 * 24)
    cache_prefix: str = 'wms_website_'
    request_timeout: int = 10


class WMSException(Exception):
    """Base exception for WMS-related errors."""
    pass


class WMSRequestError(WMSException):
    """Exception for WMS request failures."""
    pass


class WMSResponse:
    """Wrapper for WMS API responses."""

    def __init__(self, data: Any, status_code: int = 200):
        self.data = data
        self.status_code = status_code
        self.success = 200 <= status_code < 300

    @property
    def is_error(self) -> bool:
        return not self.success

    def to_response(self) -> Response:
        """Convert to DRF Response."""
        return Response(self.data, status=self.status_code)


class CacheManager:
    """Handles caching operations for WMS data."""

    def __init__(self, config: WMSConfig):
        self.config = config

    def _generate_key(self, identifier: str) -> str:
        """Generate a unique cache key."""
        hash_object = hashlib.md5(identifier.encode())
        return f"{self.config.cache_prefix}{hash_object.hexdigest()}"

    def get(self, identifier: str) -> Optional[Any]:
        """Retrieve data from cache."""
        return cache.get(self._generate_key(identifier))

    def set(self, identifier: str, data: Any) -> None:
        """Store data in cache."""
        cache.set(
            self._generate_key(identifier),
            data,
            self.config.cache_timeout
        )

    def delete(self, identifier: str) -> None:
        """Remove data from cache."""
        cache.delete(self._generate_key(identifier))

    def cache_decorator(self, timeout: Optional[int] = None):
        """Decorator for caching function results."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key based on function and arguments
                cache_key = f"wms_cache_{func.__name__}_{hashlib.md5(json.dumps((args, kwargs), sort_keys=True).encode()).hexdigest()}"

                # Try cache first
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Get fresh result
                result = func(*args, **kwargs)

                # Cache successful results
                if isinstance(result, WMSResponse) and result.success:
                    cache.set(cache_key, result,
                              timeout or self.config.cache_timeout)

                return result
            return wrapper
        return decorator


class WMSClient:
    """Client for interacting with WMS API."""

    def __init__(self, config: WMSConfig = WMSConfig()):
        self.config = config
        self.cache_manager = CacheManager(config)

    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> WMSResponse:
        """Make HTTP request to WMS API."""
        try:
            url = f'{self.config.base_url}{endpoint}'
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.config.request_timeout
            )
            response.raise_for_status()
            return WMSResponse(response.json())
        except requests.RequestException as e:
            logger.error(f"WMS request failed: {str(e)}", exc_info=True)
            return WMSResponse(
                {"error": f"Failed to process: {str(e)}"},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in WMS request: {str(e)}", exc_info=True)
            return WMSResponse(
                {"error": "Internal server error"},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_website(
        self,
        website_name: str,
        skip_cache: bool = False
    ) -> Union[Dict, Response]:
        """
        Get website information with caching support.

        Args:
            website_name: Name of the website to fetch
            skip_cache: If True, bypasses the cache
        """
        if not skip_cache:
            cached_data = self.cache_manager.get(website_name)
            if cached_data is not None:
                return cached_data

        response = self._make_request(
            'api/website/website-by-name/',
            params={"website_name": website_name}
        )

        if response.success:
            self.cache_manager.set(website_name, response.data)
            return response.data

        return response.to_response()

    def invalidate_website_cache(self, website_name: str) -> None:
        """Invalidate cache for specific website."""
        self.cache_manager.delete(website_name)


# Create default client instance
default_client = WMSClient()


# Convenience functions using default client
def get_website(*args, **kwargs):
    return default_client.get_website(*args, **kwargs)


def invalidate_website_cache(*args, **kwargs):
    return default_client.invalidate_website_cache(*args, **kwargs)
