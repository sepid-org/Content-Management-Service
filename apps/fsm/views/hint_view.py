from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.fsm.models import Hint
from apps.fsm.permissions import IsHintModifier
from apps.fsm.serializers.papers.hint_serializer import HintSerializer
from apps.fsm.serializers.papers.paper_serializer import ChangeWidgetOrderSerializer
from apps.fsm.serializers.papers.state_serializer import StateSerializer


class HintViewSet(viewsets.ModelViewSet):
    serializer_class = HintSerializer
    queryset = Hint.objects.all()
    my_tags = ['state']

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update(
            {'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    def get_permissions(self):
        if self.action == 'create' or self.action == 'retrieve' or self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsHintModifier]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(responses={200: HintSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=ChangeWidgetOrderSerializer)
    def change_order(self, request, pk=None):
        serializer = ChangeWidgetOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.get_object().set_widget_order(serializer.validated_data.get('order'))
        return Response(data=StateSerializer(self.get_object()).data, status=status.HTTP_200_OK)
