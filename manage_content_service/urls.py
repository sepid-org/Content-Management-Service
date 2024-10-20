from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from manage_content_service.settings.base import get_environment_var
import sentry_sdk

schema_view = get_schema_view(
    openapi.Info(
        title="Manage Content Service APIs",
        default_version='v3',
        description="APIs list of Manage Content Service",
    ),
    url=settings.SWAGGER_URL,
    public=True,
    permission_classes=(permissions.AllowAny,),
)

if not settings.DEBUG:
    sentry_sdk.init(
        get_environment_var('SENTRY_DNS', None),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/auth/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('api/fsm/', include('apps.fsm.urls')),
    path('api/roadmap/', include('apps.roadmap.urls')),
    path('api/file-storage/', include('apps.file_storage.urls')),
    path('api/contact-us/', include('apps.contact.urls')),
    path('api/report/', include('apps.report.urls')),
    path('api/response/', include('apps.response.urls')),
    path('api/sale/', include('apps.sale.urls')),
    path('api/attributes/', include('apps.attributes.urls')),
    path('api/widgets/', include('apps.widgets.urls')),
    path('api/currency/', include('apps.currency.urls')),
    # https://pypi.org/project/django-link-shortener/
    path('s/', include('shortener.urls')),
]

urlpatterns += [path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
