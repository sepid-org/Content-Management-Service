from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.serializers.user_serializer import UserProfileSerializer, UserPublicInfoSerializer


class ProfileViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return User.objects.none()
        elif user.is_staff or user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        """
        GET /profile/current/ 
        این متد فقط پروفایل کاربری را برمی‌گرداند که توکنش را ارسال کرده است.
        اگر کاربر ناشناس باشد، وضعیت 401 (Unauthorized) برمی‌گردد.
        """
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def profile_summary(self, request, pk=None):
        user_profile = self.get_object()
        return Response(UserPublicInfoSerializer(user_profile).data)
