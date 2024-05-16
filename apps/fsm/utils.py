from django.utils import timezone
from errors.error_codes import serialize_error
from rest_framework.exceptions import ParseError
import logging
import requests
from rest_framework_simplejwt.authentication import JWTAuthentication
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q

from apps.fsm.models import FSM, Edge, Player, PlayerStateHistory, PlayerTransition, RegistrationReceipt, State


def go_next_step(player):
    pass


def go_to_state(destination):
    pass


def _get_fsm_edges(fsm: FSM) -> list[Edge]:
    return Edge.objects.filter(Q(tail__fsm=fsm) | Q(head__fsm=fsm))


def get_django_file(url: str):
    request = requests.get(url, allow_redirects=True)

    if not request.ok:
        raise Exception("fail to fetch")

    file_name = url.rsplit('/', 1)[1]
    file_type = request.headers.get('content-type')
    file_size = int(request.headers.get('content-length'))

    file_io = BytesIO(request.content)

    django_file = InMemoryUploadedFile(
        file_io, None, file_name, file_type,  file_size, None)

    return django_file


class SafeTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request=request)
        except:
            return None


logger = logging.getLogger(__name__)


def get_receipt(user, fsm) -> RegistrationReceipt:
    if fsm.registration_form and fsm.event.registration_form:
        raise ParseError(serialize_error('4077'))
    registration_form = fsm.registration_form or fsm.event.registration_form
    return RegistrationReceipt.objects.filter(user=user, answer_sheet_of=registration_form,
                                              is_participating=True).first()


def get_player(user, fsm, receipt) -> Player:
    return user.players.filter(fsm=fsm, receipt=receipt, is_active=True).first()


def transit_player_in_fsm(player: Player, source_state: State, target_state: State, edge: Edge) -> Player:
    player.current_state = target_state
    transition_time = timezone.now()

    player.last_visit = transition_time
    player.save()

    player_transition = PlayerTransition.objects.create(
        player=player,
        source_state=source_state,
        target_state=target_state,
        time=transition_time,
        transited_edge=edge
    )

    try:
        last_state_history = PlayerStateHistory.objects.filter(
            player=player, state=source_state, departure_time__lte=transition_time).last()
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


def get_player_latest_taken_edge(player: Player) -> Edge:
    latest_history = player.player_state_histories.filter(
        is_edge_transited_in_reverse=False, state=player.current_state).last()

    if latest_history and latest_history.transited_edge:
        last_taken_edge = latest_history.transited_edge
    else:
        # if the latest hostory is deleted, choose an inward_edges randomly
        last_taken_edge = player.current_state.inward_edges.all().first()
    return last_taken_edge
