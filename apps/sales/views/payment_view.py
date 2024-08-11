import logging
from urllib.parse import urlparse

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.accounts import zarinpal
from apps.accounts.models import Merchandise, Purchase, DiscountCode, User
from apps.accounts.permissions import IsPurchaseOwner
from apps.sales.serializers.discount_code import DiscountCodeValidationSerializer
from apps.sales.serializers.purchase import PurchaseSerializer
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
        if user_registration:
            if user_registration.status == RegistrationReceipt.RegistrationStatus.Accepted:
                if len(merchandise.purchases.filter(user=request.user, status=Purchase.Status.Success)) > 0:
                    raise ParseError(serialize_error('4046'))
                if discount_code:
                    price = discount_code.calculate_discounted_price(merchandise.price)
                    discount_code.remaining -= 1
                    discount_code.save()
                else:
                    price = merchandise.price

                website_domain = urlparse(
                    request.META['HTTP_ORIGIN']).netloc
                purchase = Purchase.objects.create_purchase(merchandise=merchandise, user=self.request.user,
                                                            amount=price, discount_code=discount_code, callback_domain=website_domain)
                callback_url = f'{self.reverse_action(self.verify_payment.url_name)}?id={request.user.id}&uniq_code={purchase.uniq_code}'
                response = zarinpal.send_request(amount=price, description=merchandise.name,
                                                 callback_url=callback_url)

                return Response({'payment_link': response, **PurchaseSerializer().to_representation(purchase)},
                                status=status.HTTP_200_OK)
            else:
                raise ParseError(serialize_error('4045'))
        else:
            raise ParseError(serialize_error('4044'))

    @transaction.atomic
    @action(detail=False, methods=['get'])
    def verify_payment(self, request):
        user = get_object_or_404(User, id=request.GET.get('id', None))
        purchase = get_object_or_404(Purchase, uniq_code=request.GET.get(
            'uniq_code'), status=Purchase.Status.Started)
        discount_code = purchase.discount_code
        logger.warning(f'Zarinpal callback: {request.GET}')
        res = zarinpal.verify(status=request.GET.get('Status', None),
                              authority=request.GET.get('Authority', None),
                              amount=purchase.amount)
        if 200 <= int(res["status"]) <= 299:
            purchase.ref_id = str(res['ref_id'])
            purchase.authority = request.GET.get('Authority', None)
            if res['status'] == 200:
                purchase.status = Purchase.Status.Success
                receipt = purchase.registration_receipt
                receipt.is_participating = True
                receipt.save()
            else:
                purchase.status = Purchase.Status.Repetitious
                if discount_code:
                    discount_code.remaining += 1
                    discount_code.save()
            purchase.save()

            return redirect(f'{settings.GET_PAYMENT_CALLBACK_URL(purchase.callback_domain, "success")}/{purchase.uniq_code}')
        else:
            purchase.authority = request.GET.get('Authority')
            purchase.status = Purchase.Status.Failed
            if discount_code:
                discount_code.remaining += 1
                discount_code.save()
            purchase.save()
            return redirect(f'{settings.GET_PAYMENT_CALLBACK_URL(purchase.callback_domain, "failure")}/{purchase.uniq_code}')
