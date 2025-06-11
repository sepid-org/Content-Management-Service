import logging
from urllib.parse import urlparse

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from proxies.payment_service import zarinpal
from apps.accounts.models import Merchandise, Purchase, DiscountCode
from apps.accounts.permissions import IsPurchaseOwner
from apps.sale.serializers.discount_code import DiscountCodeValidationSerializer
from apps.sale.serializers.purchase import PurchaseSerializer
from errors.error_codes import serialize_error
from errors.exceptions import InternalServerError
from apps.fsm.models import RegistrationReceipt

logger = logging.getLogger(__name__)


class PaymentViewSet(GenericViewSet):
    my_tags = ['payments']
    serializer_class = DiscountCodeValidationSerializer
    serializer_action_classes = {
        'apply_discount_code': DiscountCodeValidationSerializer,
        'purchase': DiscountCodeValidationSerializer
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'apply_discount_code' or self.action == 'purchase':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'verify_payment':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsPurchaseOwner]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_queryset(self):
        if self.action == 'apply_discount_code' or self.action == 'purchase':
            return Merchandise.objects.all()
        else:
            return Purchase.objects.all()

    @transaction.atomic
    @action(detail=False, methods=['post'], serializer_class=DiscountCodeValidationSerializer)
    def apply_discount_code(self, request, pk=None):
        merchandise_id = request.data.pop('merchandise', None)
        merchandise = get_object_or_404(Merchandise, id=merchandise_id)
        serializer = DiscountCodeValidationSerializer(
            data=request.data,
            context={
                'merchandise': merchandise,
                **self.get_serializer_context(),
            }
        )
        serializer.is_valid(raise_exception=True)
        code = serializer.data.get('code', None)
        discount_code = get_object_or_404(DiscountCode, code=code)
        new_price = discount_code.calculate_discounted_price(merchandise.price)
        return Response({'new_price': new_price, **serializer.to_representation(discount_code)},
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: PurchaseSerializer})
    @transaction.atomic
    @action(detail=False, methods=['post'], serializer_class=DiscountCodeValidationSerializer)
    def purchase(self, request, pk=None):
        merchandise_id = request.data.pop('merchandise', None)
        merchandise = get_object_or_404(Merchandise, id=merchandise_id)

        serializer = DiscountCodeValidationSerializer(
            data=request.data,
            context={
                'merchandise': merchandise,
                **self.get_serializer_context(),
            }
        )
        serializer.is_valid(raise_exception=True)

        code = serializer.data.get('code', None)
        discount_code = get_object_or_404(
            DiscountCode, code=code) if code else None

        registration_form = merchandise.program.registration_form
        if not registration_form:
            raise InternalServerError(serialize_error('5004'))
        user_registration = registration_form.registration_receipts.filter(
            user=request.user).last()
        if not user_registration:
            raise ParseError(serialize_error('4044'))

        if user_registration.status != RegistrationReceipt.RegistrationStatus.Accepted:
            raise ParseError(serialize_error('4045'))

        if len(merchandise.purchases.filter(user=request.user, status=Purchase.Status.Success)) > 0:
            raise ParseError(serialize_error('4046'))

        if discount_code:
            price = discount_code.apply(merchandise)
        else:
            price = merchandise.price

        website_domain = urlparse(request.META['HTTP_ORIGIN']).netloc

        purchase = Purchase.objects.create_purchase(
            merchandise=merchandise,
            user=self.request.user,
            amount=price,
            discount_code=discount_code,
            callback_domain=website_domain,
        )

        callback_url = f'{self.reverse_action(self.verify_payment.url_name)}?purchase_id={purchase.id}'

        if price == 0:
            complete_purchase(purchase)
            is_payment_required = False
        else:
            response = zarinpal.send_request(
                amount=price,
                description=merchandise.name,
                callback_url=callback_url,
            )
            is_payment_required = True

        return Response(
            {
                'is_payment_required': is_payment_required,
                'payment_link': response if is_payment_required else None,
                **PurchaseSerializer().to_representation(purchase)
            },
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    @action(detail=False, methods=['get'])
    def verify_payment(self, request):
        purchase = get_object_or_404(
            Purchase,
            id=request.GET.get('purchase_id'),
            status=Purchase.Status.Started,
        )
        logger.warning(f'Zarinpal callback: {request.GET}')

        response = zarinpal.verify(
            status=request.GET.get('Status', None),
            authority=request.GET.get('Authority', None),
            amount=purchase.amount,
        )

        if 200 <= int(response["status"]) <= 299:
            purchase.ref_id = str(response['ref_id'])
            purchase.authority = request.GET.get('Authority', None)
            if response['status'] == 200:
                purchase.status = Purchase.Status.Success
                complete_purchase(purchase)
            else:
                purchase.status = Purchase.Status.Repetitious
                discount_code = purchase.discount_code
                if discount_code:
                    discount_code.revert_apply()
            purchase.save()

            success_payment_callback_url = zarinpal.get_payment_callback_url(
                purchase=purchase,
                status='SUCCESS',
            )
            return redirect(success_payment_callback_url)
        else:
            purchase.authority = request.GET.get('Authority')
            purchase.status = Purchase.Status.Failed
            purchase.save()
            discount_code = purchase.discount_code
            if discount_code:
                discount_code.revert_apply()
            failure_payment_callback_url = zarinpal.get_payment_callback_url(
                purchase=purchase,
                status='FAILURE',
            )
            return redirect(failure_payment_callback_url)


def complete_purchase(purchase):
    receipt = purchase.registration_receipt
    receipt.is_participating = True
    receipt.save()
