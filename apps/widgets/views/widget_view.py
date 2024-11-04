from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.db import transaction

from apps.fsm.models import *
from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.widgets.serializers.mock_widget_serializer import MockWidgetSerializer
from apps.widgets.serializers.widget_polymorphic_serializer import WidgetPolymorphicSerializer


class WidgetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Widget.objects.all()
    serializer_class = WidgetPolymorphicSerializer
    my_tags = ['widgets']

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    @swagger_auto_schema(responses={200: MockWidgetSerializer})
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        request.data['creator'] = request.user.id
        widget_serializer = WidgetPolymorphicSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        widget_serializer.is_valid(raise_exception=True)
        widget_instance = widget_serializer.save()

        object_instance = widget_instance.object
        object_serializer = ObjectSerializer(
            object_instance,
            data=request.data,
            context=self.get_serializer_context(),
            partial=True,
        )
        object_serializer.is_valid(raise_exception=True)
        object_serializer.save()

        return Response(widget_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={200: MockWidgetSerializer})
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        widget_instance = self.get_object()
        widget_serializer = WidgetPolymorphicSerializer(
            widget_instance,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        widget_serializer.is_valid(raise_exception=True)
        widget_serializer.save()

        object_instance = widget_instance.object
        object_serializer = ObjectSerializer(
            object_instance,
            data=request.data,
            context=self.get_serializer_context(),
            partial=True,
        )
        object_serializer.is_valid(raise_exception=True)
        object_serializer.save()

        return Response(widget_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def get_widgets_by_ids(self, request):
        ids = request.data.get('ids', [])
        widgets = self.queryset.filter(id__in=ids)
        serializer = self.get_serializer(widgets, many=True)
        return Response(serializer.data)
