from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction

from apps.fsm.models.form import Form
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
        serializer = AnswerSheetSerializer(data={
            'user': request.user.id,
            'form': form,
            **request.data,
        })

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
