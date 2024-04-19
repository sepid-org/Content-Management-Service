from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.fsm.models import Event
from apps.fsm.serializers.fsm_serializers import EventSerializer
from apps.fsm.permissions import IsEventModifier, HasActiveRegistration


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    my_tags = ['event']
    filterset_fields = ['party', 'is_private']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'retrieve' or self.action == 'list':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'get_fsms':
            permission_classes = [HasActiveRegistration]
        else:
            permission_classes = [IsEventModifier]
        return [permission() for permission in permission_classes]

    # todo: remove duplication
    # todo: EHSAN
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
