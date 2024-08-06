from django.db import transaction
from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.serializers.user_serializer import UserProfileSerializer, UserPublicInfoSerializer


class ProfileViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UserProfileSerializer
    my_tags = ['accounts']

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return User.objects.none()
        elif user.is_staff or user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)

    @action(detail=True, methods=['get'])
    def profile_summary(self, request, pk=None):
        user_profile = self.get_object()
        return Response(UserPublicInfoSerializer(user_profile).data)
