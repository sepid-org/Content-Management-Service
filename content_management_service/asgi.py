"""
ASGI config for content_management_service project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from contextlib import asynccontextmanager
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "content_management_service.settings.production")

# Get the Django ASGI application early to ensure it's loaded properly
django_application = get_asgi_application()


@asynccontextmanager
async def lifespan(app):
    # Startup code (if needed)
    print('Starting up ASGI application...')
    yield
    # Shutdown code (if needed)
    print('Shutting down ASGI application...')


async def application(scope, receive, send):
    if scope["type"] == "lifespan":
        async with lifespan(None):
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
    else:
        await django_application(scope, receive, send)
