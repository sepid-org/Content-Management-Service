from errors.error_codes import serialize_error
from apps.fsm.serializers.widget_serializers import WidgetSerializer
from apps.fsm.serializers.answer_serializers import AnswerSerializer
from apps.fsm.models import *
from rest_framework.exceptions import ParseError
import logging
import requests
from rest_framework_simplejwt.authentication import JWTAuthentication
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q

from apps.fsm.models import FSM, Edge


def go_next_step(player):
    pass


def go_to_state(destination):
    pass


def _get_fsm_edges(fsm: FSM) -> list[Edge]:
    return Edge.objects.filter(Q(tail__fsm=fsm) | Q(head__fsm=fsm))


def get_django_file(url: str):
    r = requests.get(url, allow_redirects=True)

    if not r.ok:
        raise Exception("fail to fetch")

    file_name = url.rsplit('/', 1)[1]
    file_type = r.headers.get('content-type')
    file_size = int(r.headers.get('content-length'))

    file_io = BytesIO(r.content)

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


def get_receipt(user, fsm):
    if fsm.registration_form and fsm.event.registration_form:
        raise ParseError(serialize_error('4077'))
    registration_form = fsm.registration_form or fsm.event.registration_form
    return RegistrationReceipt.objects.filter(user=user, answer_sheet_of=registration_form,
                                              is_participating=True).first()


def get_player(user, fsm, receipt):
    return user.players.filter(fsm=fsm, receipt=receipt, is_active=True).first()


def move_on_edge(player:Player, edge:Edge, departure_time, is_forward):
    player.current_state = edge.head if is_forward else edge.tail
    player.last_visit = departure_time
    player.save()
    try:
        last_state_history = PlayerHistory.objects.get(
            player=player, state=edge.tail if is_forward else edge.head, end_time=None)
    except:
        last_state_history = None
    if last_state_history:
        last_state_history.end_time = departure_time
        last_state_history.save()
    PlayerHistory.objects.create(player=player, state=edge.head if is_forward else edge.tail, passed_edge=edge,
                                 start_time=departure_time, is_edge_passed_in_reverse=not is_forward)
    return player


def get_a_player_from_team(team, fsm):
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


def get_player_latest_taken_edge(player: Player):
    latest_history = player.histories.filter(
        is_edge_passed_in_reverse=False, state=player.current_state).last()

    if latest_history and latest_history.passed_edge:
        last_taken_edge = latest_history.passed_edge
    else:
        # if the latest hostory is deleted, choose an inward_edges randomly
        last_taken_edge = player.current_state.inward_edges.all().first()
    return last_taken_edge
