
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.fsm.serializers.answer_sheet_serializers import RegistrationReceiptSerializer
from apps.fsm.models import RegistrationForm, transaction, RegistrationReceipt, Invitation
from apps.fsm.permissions import IsRegistrationFormModifier
from apps.fsm.serializers.form.registration_form_serializer import RegistrationFormSerializer
from apps.fsm.serializers.team_serializer import InvitationSerializer
from apps.fsm.pagination import RegistrationReceiptSetPagination


class RegistrationViewSet(ModelViewSet):
    serializer_class = RegistrationFormSerializer
    queryset = RegistrationForm.objects.all()
    my_tags = ['registration']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update(
            {'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    def get_permissions(self):
        if self.action in ['create', 'register', 'list', 'my_invitations']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsRegistrationFormModifier]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(responses={200: RegistrationReceiptSerializer})
    @action(detail=True, methods=['get'])
    def receipts(self, request, pk=None):
        queryset = self.get_object().registration_receipts.all().order_by('-id')
        paginator = RegistrationReceiptSetPagination()
        page_queryset = paginator.paginate_queryset(queryset, request)
        if page_queryset is not None:
            serializer = RegistrationReceiptSerializer(
                page_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @swagger_auto_schema(responses={200: InvitationSerializer}, tags=['teams'])
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def my_invitations(self, request, pk=None):
        receipt = RegistrationReceipt.objects.filter(
            user=request.user,
            is_participating=True,
            form=self.get_object()
        ).first()
        invitations = Invitation.objects.filter(
            invitee=receipt,
            team__program__registration_form=self.get_object(),
            status=Invitation.InvitationStatus.Waiting,
        )
        return Response(data=InvitationSerializer(invitations, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={201: RegistrationReceiptSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        registration_form = self.get_object()

        # 1. Check the user’s permission status
        status_enum = registration_form.get_user_registration_permission_status(
            request.user)

        # 2. If not permitted, return only the enum code in the response
        if status_enum != registration_form.RegisterPermissionStatus.Permitted:
            return Response(
                {'error_code': status_enum},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Build and validate the serializer
        serializer = RegistrationReceiptSerializer(data={
            'form': registration_form.id,
            'user': request.user.id,
            **request.data,
        })
        serializer.is_valid(raise_exception=True)
        registration_receipt = serializer.save()

        # 4. Attempt to register the user into the form
        try:
            registration_receipt.register_in_form(registration_form)
        except Exception as e:
            # Return only the exception’s message as an error code
            return Response(
                {'error_code': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Return 201 Created on success
        return Response(status=status.HTTP_201_CREATED)
