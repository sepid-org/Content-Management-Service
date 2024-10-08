from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.fsm.models import State
from apps.fsm.models.base import Paper
from apps.fsm.permissions import IsStateModifier
from apps.fsm.serializers.fsm_serializers import EdgeSerializer
from apps.fsm.serializers.papers.state_serializer import StateSerializer
from apps.fsm.views.object_view import ObjectViewSet


class StateViewSet(ObjectViewSet):
    serializer_class = StateSerializer
    queryset = State.objects.all()
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
        if self.action in ['create', 'retrieve', 'list', 'outward_edges', 'inward_edges']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsStateModifier]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def outward_edges(self, request, pk=None):
        state = self.get_object()
        outward_edges = state.outward_edges.all()
        serializer = EdgeSerializer(outward_edges, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def inward_edges(self, request, pk=None):
        state = self.get_object()
        inward_edges = state.inward_edges.all()
        serializer = EdgeSerializer(inward_edges, many=True)
        return Response(serializer.data)
