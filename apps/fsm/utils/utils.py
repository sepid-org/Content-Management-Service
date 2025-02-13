import logging
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ParseError
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.models import User
from apps.fsm.models import FSM, AnswerSheet, Edge, Player, PlayerStateHistory, PlayerTransition, Program, RegistrationReceipt, State, Team
from errors.error_codes import serialize_error


def _get_fsm_edges(fsm: FSM) -> list[Edge]:
    return Edge.objects.filter(Q(tail__fsm=fsm) | Q(head__fsm=fsm)).order_by('-id')


logger = logging.getLogger(__name__)


def get_receipt(user, fsm) -> RegistrationReceipt:
    registration_form = fsm.program.registration_form
    try:
        return RegistrationReceipt.objects.get(user=user, form=registration_form, is_participating=True)
    except:
        return None


def get_players(user, fsm) -> list[Player]:
    return fsm.players.filter(user=user)


def transit_team_in_fsm(team: Team, fsm: FSM, source_state: State, target_state: State, edge: Edge) -> None:
    for member in team.members.all():
        player = member.get_player_of(fsm=fsm)
        if player:
            transit_player_in_fsm(player, source_state, target_state, edge)


def transit_player_in_fsm(player: Player, source_state: State, target_state: State, edge: Edge = None) -> Player:

    if not is_transition_permitted(source_state, target_state):
        raise ParseError(serialize_error('4119'))

    player.current_state = target_state
    transition_time = timezone.now()

    player.last_visit = transition_time
    player.save()

    if edge is None:
        try:
            edge = Edge.objects.get(tail=source_state, head=target_state)
        except Edge.DoesNotExist:
            try:
                edge = Edge.objects.get(tail=target_state, head=source_state)
            except Edge.DoesNotExist:
                pass

    player_transition = PlayerTransition.objects.create(
        player=player,
        source_state=source_state,
        target_state=target_state,
        time=transition_time,
        transited_edge=edge
    )

    try:
        last_state_history = player.player_state_histories.filter(
            state=source_state, departure=None
        ).last()
        last_state_history.departure_time = transition_time
        last_state_history.departure = player_transition
        last_state_history.save()
    except:
        pass

    PlayerStateHistory.objects.create(
        player=player,
        state=target_state,
        arrival=player_transition,
    )

    return player


def is_transition_permitted(source_state: State, target_state: State):
    # if source_state.id == target_state.id:
    #     return True
    # todo
    return True


def get_a_player_from_team(team, fsm) -> Player:
    head_receipt = team.team_head
    players = Player.objects.filter(fsm=fsm, receipt__in=team.members.all())
    if len(players) <= 0:
        logger.info('no player found for any member of team')
        raise ParseError(serialize_error('4088'))
    else:
        player = players.filter(receipt=head_receipt).first()
        if not player:
            player = players.first()
        return player


def get_player_backward_edge(player: Player) -> Edge:
    # todo: it should get the desired backward edge, not mustly the first one
    return player.current_state.inward_edges.first()


def register_user_in_program(user: User, program: Program):
    registration_form = program.registration_form
    try:
        # if there is any registration_receipt, make it registered
        registration_receipt = RegistrationReceipt.objects.get(
            form=registration_form, user=user)
        registration_receipt.is_participating = True
        registration_receipt.status = RegistrationReceipt.RegistrationStatus.Accepted
        registration_receipt.save()
    except:
        # if there is no registration_receipt, create it
        RegistrationReceipt.objects.create(
            form=registration_form,
            user=user,
            answer_sheet_type=AnswerSheet.AnswerSheetType.RegistrationReceipt,
            status=RegistrationReceipt.RegistrationStatus.Accepted,
            is_participating=True)


def get_user_permission(receipt: RegistrationReceipt) -> dict:
    user = receipt.user
    if user in receipt.form.program.modifiers:
        return True
    return False
    # todo


def add_admin_to_program(user: User, program: Program):
    program.admins.add(user)
    register_user_in_program(user, program)
