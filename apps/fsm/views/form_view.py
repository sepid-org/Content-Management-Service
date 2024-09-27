from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction

from apps.fsm.models.form import Form
from apps.fsm.serializers.answer_sheet_serializers import AnswerSheetSerializer
from apps.fsm.serializers.form_serializer import FormSerializer


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
    @action(detail=True, methods=['post'], serializer_class=AnswerSheetSerializer)
    def submit(self, request, pk=None):
        form = self.get_object()
        serializer = AnswerSheetSerializer(
            data={
                'answer_sheet_type': 'General',
                **request.data,
            },
            context={
                'user': request.user,
                'form': form,
            }
        )
        serializer.is_valid(raise_exception=True)
        answer_sheet = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
