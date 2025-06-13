from django.utils import timezone
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.models import Merchandise, DiscountCode
from apps.accounts.permissions import IsMerchandiseOwner
from apps.sale.serializers.merchandise import MerchandiseSerializer
from apps.sale.serializers.discount_code import DiscountCodeSerializer


class MerchandiseViewSet(ModelViewSet):
    """
    ViewSet for handling Merchandise operations, with soft-deletion and filtering support.
    """
    my_tags = ['payments']
    serializer_class = MerchandiseSerializer
    queryset = Merchandise.objects.filter(is_deleted=False)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'is_active': ['exact'],
        'program__slug': ['exact'],
    }

    serializer_action_classes = {
        'discount_codes': DiscountCodeSerializer
    }

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, self.serializer_class)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'discount_codes':
            permission_classes = [IsMerchandiseOwner]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        return [perm() for perm in permission_classes]

    @action(detail=True, methods=['get'], serializer_class=DiscountCodeSerializer)
    def discount_codes(self, request, pk=None):
        merchandise = self.get_object()
        codes = DiscountCode.objects.filter(merchandises=merchandise)
        return Response(self.get_serializer(codes, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='delete')
    def soft_delete(self, request, pk=None):
        merchandise = self.get_object()
        merchandise.is_deleted = True
        merchandise.deleted_at = timezone.now()
        merchandise.is_active = False
        merchandise.save(
            update_fields=['is_deleted', 'deleted_at', 'is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)
