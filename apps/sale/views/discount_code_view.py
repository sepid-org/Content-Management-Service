from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.accounts.models import DiscountCode
from apps.accounts.permissions import IsDiscountCodeModifier
from apps.sale.serializers.discount_code import DiscountCodeSerializer
from apps.sale.services.discount_code_service import (
    create_discount_code,
    get_program_discount_codes,
)


class DiscountCodeViewSet(ModelViewSet):
    my_tags = ["payments"]
    serializer_class = DiscountCodeSerializer
    queryset = DiscountCode.objects.order_by("-id")
    permission_classes = [IsDiscountCodeModifier]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    @action(detail=False, methods=["GET"])
    def program_discount_codes(self, request, pk=None):
        """
        Retrieve discount codes for a specific program.
        """
        program_slug = request.GET.get(
            "program", None
        )  # TODO: hashem; put this in URL
        discount_codes = get_program_discount_codes(
            program_slug
        )
        return Response(
            self.serializer_class(discount_codes, many=True).data,
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        username = request.data.pop("user", None)
        merchandises = request.data.pop("merchandises", [])

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        website = request.headers.get("Website")
        create_discount_code(
            data=serializer.validated_data,
            merchandise_ids=merchandises,
            username=username,
            website=website,
        )

        return Response(status=status.HTTP_201_CREATED)
