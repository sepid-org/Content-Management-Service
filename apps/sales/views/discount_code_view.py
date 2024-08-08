from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.accounts.models import DiscountCode
from apps.accounts.permissions import IsDiscountCodeModifier
from apps.sales.serializers.serializers import DiscountCodeSerializer


class DiscountCodeViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin, CreateModelMixin, DestroyModelMixin):
    my_tags = ['payments']
    serializer_class = DiscountCodeSerializer
    queryset = DiscountCode.objects.all()
    permission_classes = [IsDiscountCodeModifier]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context
