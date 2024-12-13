from django.forms import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema

from apps.fsm.models.form import Form
from apps.fsm.serializers.form.form_polymorphic_serializer import FormPolymorphicSerializer
from apps.fsm.utils.submission.form_submission_handler import FormSubmissionHandler
from apps.response.serializers.answer_sheet import AnswerSheetSerializer


class FormViewSet(ModelViewSet):
    serializer_class = FormPolymorphicSerializer
    queryset = Form.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    @swagger_auto_schema(responses={201: AnswerSheetSerializer})
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit an answer sheet for a specific form.
        """
        form = self.get_object()

        try:
            handler = FormSubmissionHandler(form=form, user=request.user)
            response = handler.submit(request)
            return response

        except (PermissionDenied, ValidationError) as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
