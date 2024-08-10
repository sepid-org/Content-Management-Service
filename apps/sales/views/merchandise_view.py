from django.utils import timezone
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.accounts.models import Merchandise, DiscountCode
from apps.accounts.permissions import IsMerchandiseOwner
from apps.sales.serializers.merchandise import MerchandiseSerializer
from apps.sales.serializers.discount_code import DiscountCodeSerializer


class MerchandiseViewSet(ModelViewSet):
    my_tags = ['payments']
    serializer_class = MerchandiseSerializer
    queryset = Merchandise.objects.filter(is_deleted=False)
    serializer_action_classes = {
        'discount_codes': DiscountCodeSerializer
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = []
        if self.action == 'discount_codes':
            permission_classes = [IsMerchandiseOwner]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    @action(detail=True, methods=['get'], serializer_class=DiscountCodeSerializer)
    def discount_codes(self, request, pk=None):
        return Response(DiscountCodeSerializer(DiscountCode.objects.filter(merchandises__in=[self.get_object()]), many=True).data,
                        status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=False, methods=['GET'])
    def program_merchandises(self, request, pk=None):
        program_id = request.GET.get('program', None)
        merchandises = self.get_queryset().filter(program_id=program_id)
        return Response(self.serializer_class(merchandises, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def soft_delete(self, request, pk=None):
        merchandise = self.get_object()
        merchandise.is_deleted = True
        merchandise.deleted_at = timezone.now()
        merchandise.is_active = False
        merchandise.save()
        return Response()
