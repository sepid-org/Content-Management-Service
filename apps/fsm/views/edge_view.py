from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from apps.fsm.views.object_view import ObjectViewSet
from errors.error_codes import serialize_error
from apps.fsm.models import Edge, Team
from apps.fsm.permissions import IsEdgeModifier
from apps.fsm.serializers.fsm_serializers import EdgeSerializer, TeamGetSerializer
from apps.fsm.serializers.player_serializer import PlayerSerializer
from apps.fsm.utils.utils import transit_team_in_fsm


class EdgeViewSet(ObjectViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
    my_tags = ['edge']

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'list']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsEdgeModifier]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        head = request.data.get('head')
        tail = request.data.get('tail')
        if Edge.objects.filter(head=head, tail=tail).exists():
            raise ParseError(serialize_error('4118'))
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=TeamGetSerializer)
    def mentor_move_forward(self, request, pk):
        edge = self.get_object()
        fsm = edge.tail.fsm
        serializer = TeamGetSerializer(
            data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        team: Team = serializer.validated_data['team']
        transit_team_in_fsm(team, fsm, edge.tail, edge.head)

        return Response(status=status.HTTP_202_ACCEPTED)
