from rest_framework.viewsets import ModelViewSet
from apps.accounts.models import DiscountCode, Merchandise
from apps.accounts.permissions import IsDiscountCodeModifier
from apps.accounts.utils import find_user_in_website
from apps.sales.serializers.discount_code import DiscountCodeSerializer
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class DiscountCodeViewSet(ModelViewSet):
    my_tags = ['payments']
    serializer_class = DiscountCodeSerializer
    queryset = DiscountCode.objects.all()
    permission_classes = [IsDiscountCodeModifier]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    @transaction.atomic
    @action(detail=False, methods=['GET'])
    def program_discount_codes(self, request, pk=None):
        program_slug = request.GET.get('program', None)
        discount_codes = DiscountCode.objects.filter(
            merchandises__program__slug=program_slug).distinct()
        return Response(self.serializer_class(discount_codes, many=True).data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        username = request.data.pop('user', None)
        merchandises = request.data.pop('merchandises', [])

        # create discount code
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        discount_code = serializer.save()

        # add merchandises
        for merchandise_id in merchandises:
            merchandise = Merchandise.objects.get(id=merchandise_id)
            discount_code.merchandises.add(merchandise)

        # add user (if provided)
        if username:
            website = request.data.get('website')
            target_user = find_user_in_website(
                user_data={'username': username}, website=website)

            discount_code.user = target_user
            discount_code.save()

        return Response(status=status.HTTP_201_CREATED)
