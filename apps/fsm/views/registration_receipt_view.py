from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound, ParseError
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.fsm.models.form import AnswerSheet
from errors.error_codes import ErrorCodes, serialize_error
from apps.fsm.models import RegistrationReceipt
from apps.fsm.permissions import IsRegistrationReceiptOwner, IsReceiptsFormModifier
from apps.fsm.serializers.answer_sheet_serializers import RegistrationReceiptSerializer, RegistrationStatusSerializer
from apps.fsm.serializers.certificate_serializer import create_certificate
from proxies.sms_system.sms_service_proxy import SMSServiceProxy


class RegistrationReceiptViewSet(GenericViewSet, RetrieveModelMixin, DestroyModelMixin):
    serializer_class = RegistrationReceiptSerializer
    queryset = RegistrationReceipt.objects.all()
    my_tags = ['registration']

    def get_permissions(self):
        if self.action in ['destroy', 'get_certificate']:
            permission_classes = [IsRegistrationReceiptOwner]
        elif self.action == 'retrieve':
            permission_classes = [
                IsRegistrationReceiptOwner | IsReceiptsFormModifier]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return RegistrationReceipt.objects.none()
        return self.queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {'domain': self.request.build_absolute_uri('/api/'[:-5])})
        return context

    @swagger_auto_schema(responses={200: RegistrationReceiptSerializer})
    @action(detail=True, methods=['post'], serializer_class=RegistrationStatusSerializer, url_path='update-registration-status')
    @transaction.atomic
    def update_registration_status(self, request, pk=None):
        receipt = self.get_object()

        if request.user not in receipt.form.program_or_fsm.modifiers:
            raise PermissionDenied(serialize_error('4061'))

        status_serializer = RegistrationStatusSerializer(data=request.data)

        status_serializer.is_valid(raise_exception=True)

        registration_status = status_serializer.data.get('status')

        receipt.status = registration_status
        receipt.save()

        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: RegistrationReceiptSerializer})
    @action(detail=True, methods=['post'], url_path='confirm-registration')
    @transaction.atomic
    def confirm_registration(self, request, pk=None):
        receipt = self.get_object()

        if request.user not in receipt.form.program_or_fsm.modifiers:
            raise PermissionDenied(serialize_error('4061'))

        if receipt.status != RegistrationReceipt.RegistrationStatus.Accepted:
            return Response(
                {'error_code': ErrorCodes.REGISTRATION_NOT_ACCEPTED},
                status=status.HTTP_400_BAD_REQUEST
            )

        receipt.is_participating = True
        receipt.save()

        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=my_tags + ['certificates'])
    @action(detail=True, methods=['get'])
    def get_certificate(self, request, pk=None):
        receipt = self.get_object()
        if not receipt.form.has_certificate or not receipt.form.certificates_ready:
            raise ParseError(serialize_error('4098'))
        if receipt.certificate:
            receipt.certificate.storage.delete(receipt.certificate.name)
        certificate_templates = receipt.form.certificate_templates.all()
        # filter templates accordingly to user performance
        if len(certificate_templates) > 0:
            receipt.certificate = create_certificate(
                certificate_templates.first(), request.user.full_name)
            receipt.save()
        else:
            raise NotFound(serialize_error('4095'))
        return Response(RegistrationReceiptSerializer(context=self.get_serializer_context()).to_representation(receipt),
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_receipt(self, request, pk=None):
        form_id = request.GET.get('form')
        if not form_id:
            return Response({'error': 'Form ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        try:
            answer_sheet = user.answer_sheets.get(form__id=form_id)
            return Response(RegistrationReceiptSerializer(answer_sheet).data, status=status.HTTP_200_OK)
        except AnswerSheet.DoesNotExist:
            return Response({'error': 'Answer sheet not found.'}, status=status.HTTP_404_NOT_FOUND)
