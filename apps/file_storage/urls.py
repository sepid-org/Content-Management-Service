from rest_framework.routers import DefaultRouter

from .views import FileViewSet

router = DefaultRouter()

router.register(r'file', FileViewSet, basename='file')

urlpatterns = []

urlpatterns += router.urls
