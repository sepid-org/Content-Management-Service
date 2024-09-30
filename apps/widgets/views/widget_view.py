from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import parser_classes, action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser
from django.db import transaction
from drf_yasg import openapi

from apps.fsm.models import *
from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.widgets.serializers.mock_widget_serializer import MockWidgetSerializer
from apps.widgets.serializers.widget_polymorphic_serializer import WidgetPolymorphicSerializer


class WidgetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes([MultiPartParser])
    queryset = Widget.objects.all()
    serializer_class = WidgetPolymorphicSerializer
    my_tags = ['widgets']

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

    @swagger_auto_schema(responses={200: MockWidgetSerializer})
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = WidgetPolymorphicSerializer(
            data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        widget_instance = serializer.save()

        object_instance = widget_instance.object
        serializer = ObjectSerializer(
            object_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(WidgetPolymorphicSerializer(widget_instance).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={200: MockWidgetSerializer})
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        widget_instance = self.get_object()
        serializer = WidgetPolymorphicSerializer(
            widget_instance, data=request.data, partial=True, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()

        object_instance = widget_instance.object
        serializer = ObjectSerializer(
            object_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(WidgetPolymorphicSerializer(widget_instance).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER))
            },
            required=['ids']
        ),
        responses={200: WidgetPolymorphicSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def get_widgets_by_ids(self, request):
        ids = request.data.get('ids', [])
        widgets = self.queryset.filter(id__in=ids)
        serializer = self.get_serializer(widgets, many=True)
        return Response(serializer.data)
