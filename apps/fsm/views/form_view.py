from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction

from apps.fsm.models.form import AnswerSheet, Form
from apps.fsm.serializers.form_serializer import FormSerializer
from apps.response.serializers.answer_sheet import AnswerSheetSerializer


class FormViewSet(ModelViewSet):
    serializer_class = FormSerializer
    queryset = Form.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    @swagger_auto_schema(responses={201: AnswerSheetSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        form = self.get_object()
        user = request.user

        # Check if the form has a participant limit
        if form.participant_limit > 0:
            if user.is_anonymous:
                raise PermissionDenied(
                    "You must be logged in to submit this form.")
            else:
                count = AnswerSheet.objects.filter(
                    user=user, form=form).count()
                if count >= form.participant_limit:
                    raise PermissionDenied(
                        "You have exceeded the submission limit for this form.")

        # Serialize and save the submitted data
        serializer = AnswerSheetSerializer(data={
            'user': request.user.id,
            'form': form.id,
            **request.data,
        })

        serializer.is_valid(raise_exception=True)
        serializer.save()

        from apps.attributes.utils import perform_posterior_actions
        perform_posterior_actions(
            attributes=form.attributes,
            request=request,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
