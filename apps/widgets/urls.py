from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.widgets.views.widget_hint_view import WidgetHintViewSet
from apps.widgets.views.widget_view import WidgetViewSet


router = DefaultRouter()

router.register(r'widget-hint', WidgetHintViewSet, basename='widget-hints')
router.register(r'widget', WidgetViewSet, basename='widgets')

urlpatterns = [
    path('', include(router.urls)),
]
