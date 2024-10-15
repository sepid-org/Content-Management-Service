from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from apps.fsm.models.fsm import State
from errors.error_codes import serialize_error
from errors.exceptions import InternalServerError
from apps.fsm.models import FSM, Player
from apps.fsm.permissions import PlayerViewerPermission
from apps.fsm.models import FSM
from apps.fsm.serializers.fsm_serializers import KeySerializer, TeamGetSerializer
from apps.fsm.serializers.player_serializer import PlayerSerializer
from apps.fsm.utils import get_player_backward_edge, transit_player_in_fsm, transit_team_in_fsm


class PlayerViewSet(viewsets.GenericViewSet, RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    my_tags = ['fsm']

    def get_permissions(self):
        if self.action in ['retrieve', 'mentor_move_backward']:
            permission_classes = [PlayerViewerPermission]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    @swagger_auto_schema(tags=['mentor'])
    def retrieve(self, request, *args, **kwargs):
        return super(PlayerViewSet, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=KeySerializer)
    def go_backward(self, request, pk):
        player = self.get_object()
        fsm = player.fsm
        # todo: it should go back through one of this state inward links:
        edge = get_player_backward_edge(player)

        if not edge:
            raise ParseError(serialize_error('4114'))

        if player is None:
            raise ParseError(serialize_error('4082'))

        # todo check back enable
        if fsm.fsm_p_type == FSM.FSMPType.Team:
            team = player.team
            if player.receipt.id != team.team_head.id:
                raise ParseError(serialize_error('4089'))
            if player.current_state == edge.head:
                transit_team_in_fsm(team, fsm, edge.head, edge.tail, edge)
            return Response(status=status.HTTP_202_ACCEPTED)

        elif fsm.fsm_p_type == FSM.FSMPType.Individual:
            if player.current_state == edge.head:
                player = transit_player_in_fsm(
                    player, edge.head, edge.tail, edge)
            return Response(status=status.HTTP_202_ACCEPTED)

        else:
            raise InternalServerError('Not implemented Yet😎')

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['mentor'])
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=TeamGetSerializer)
    def mentor_move_backward(self, request, pk):
        serializer = TeamGetSerializer(
            data=self.request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        team = serializer.validated_data['team']
        player = self.get_object()
        fsm = player.fsm
        # todo: it should go back through one of this state inward links:
        edge = get_player_backward_edge(player)

        if fsm.fsm_p_type == FSM.FSMPType.Team:
            transit_team_in_fsm(team, fsm, edge.head, edge.tail, edge)
            return Response(status=status.HTTP_202_ACCEPTED)

        else:
            raise InternalServerError('Not implemented Yet😎')

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='transit-to-state')
    def transit_to_state(self, request):
        state_id = request.data.get('state')
        state = get_object_or_404(State, id=state_id)
        try:
            player = Player.objects.get(user=request.user, fsm=state.fsm)
        except:
            player = Player.objects.create(
                user=request.user,
                fsm=state.fsm,
                current_state=state,
            )

        if not is_transition_permitted(player.current_state, state):
            raise ParseError(serialize_error('4119'))

        transit_player_in_fsm(
            player=player,
            source_state=player.current_state,
            target_state=state,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


def is_transition_permitted(source_state: State, target_state: State):
    if source_state.id == target_state.id:
        return True
    # todo
    return True
