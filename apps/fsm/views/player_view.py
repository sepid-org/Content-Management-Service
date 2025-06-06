from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from apps.fsm.models.fsm import State
from errors.error_codes import ErrorCodes
from errors.exceptions import InternalServerError
from apps.fsm.models import FSM, Player
from apps.fsm.permissions import PlayerViewerPermission
from apps.fsm.serializers.fsm_serializers import TeamGetSerializer
from apps.fsm.serializers.player_serializer import PlayerSerializer
from apps.fsm.utils.utils import get_last_forward_transition, transit_player_in_fsm, transit_team_in_fsm


class PlayerViewSet(viewsets.GenericViewSet, RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    my_tags = ['player']

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
    @action(detail=True, methods=['post'])
    def go_backward(self, request, pk):
        player = self.get_object()
        fsm = player.fsm

        player_last_transition = get_last_forward_transition(player)

        # todo check back enable
        if fsm.fsm_p_type == FSM.FSMPType.Team:
            team = player.team
            if player.current_state == player_last_transition.target_state:
                transit_team_in_fsm(
                    team,
                    fsm,
                    player_last_transition.target_state,
                    player_last_transition.source_state,
                    is_backward=True,
                )
            return Response(status=status.HTTP_202_ACCEPTED)

        elif fsm.fsm_p_type == FSM.FSMPType.Individual:
            if player.current_state == player_last_transition.target_state:
                player = transit_player_in_fsm(
                    player,
                    player_last_transition.target_state,
                    player_last_transition.source_state,
                    is_backward=True,
                )
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

        player_last_transition = get_last_forward_transition(player)

        if fsm.fsm_p_type == FSM.FSMPType.Team:
            transit_team_in_fsm(
                team,
                fsm,
                player_last_transition.target_state,
                player_last_transition.source_state,
            )
            return Response(status=status.HTTP_202_ACCEPTED)

        else:
            raise InternalServerError('Not implemented Yet😎')

    @swagger_auto_schema(responses={200: PlayerSerializer}, tags=['player'])
    @action(detail=False, methods=['post'], url_path='transit-to-state')
    def transit_to_state(self, request):
        state_id = request.data.get('state')
        state = get_object_or_404(State, id=state_id)
        user = request.user

        try:
            player = Player.objects.get(
                user=user, fsm=state.fsm, finished_at__isnull=True)
        except:
            player = Player.objects.create(
                user=user,
                fsm=state.fsm,
                current_state=state,
            )

        transit_player_in_fsm(
            player=player,
            source_state=player.current_state,
            target_state=state,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='finish-fsm')
    def finish_fsm(self, request, pk=None):
        """
        Marks the FSM as finished for the player if not already done.
        """
        player: Player = self.get_object()

        if player.finished_at:
            return Response(
                {"error_code": ErrorCodes.ALREADY_FINISHED_FSM},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fsm = player.fsm
        website = request.website
        from apps.attributes.models.performable_actions import Finish
        finish_attributes = fsm.attributes.instance_of(Finish)
        for finish_attribute in finish_attributes:
            finish_attribute.perform(
                user=request.user,
                player=player,
                website=website,
            )

        player.finished_at = timezone.now()
        player.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='performance')
    def get_player_performance(self, request, pk=None):
        player: Player = self.get_object()
        return Response(
            data=player.answer_sheet.assess(),
            status=status.HTTP_200_OK,
        )
