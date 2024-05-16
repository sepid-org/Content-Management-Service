from django.utils import timezone
from apps.fsm.utils import _get_fsm_edges
from apps.roadmap.models import Link
from apps.fsm.models import FSM, Player, State, PlayerTransition


def _get_fsm_links(fsm_id: int):
    fsm = FSM.get_fsm(fsm_id)
    edges = _get_fsm_edges(fsm)
    links = [Link.get_link_from_states(
        edge.tail, edge.head) for edge in edges]
    return links


def _get_player_transited_path(player_id: int):
    player: Player = Player.get_player(player_id)
    transitions: list[PlayerTransition] = player.player_transitions.all()
    player_current_state: State = player.current_state
    current_time = timezone.now()
    taken_path: list[Link] = []

    # 100 is consumed as maximum length in a fsm graph
    for i in range(100):
        previous_transition = _get_player_previous_transition(
            player_current_state, current_time, transitions)
        # if the transited_edge is deleted, it isn't possible to reach to previous state
        if not previous_transition:
            break
        taken_path.append(Link.get_link_from_transition(previous_transition))

        player_current_state = previous_transition.source_state
        current_time = previous_transition.time

    taken_path.reverse()
    return taken_path


def _get_player_previous_transition(player_state: State, time, transitions: list[PlayerTransition]) -> PlayerTransition:
    try:
        last_transition = transitions.filter(
            target_state=player_state, time__lte=time).last()
        return last_transition
    except:
        return None


def _get_player_previous_state(player_current_state: State, time, transitions: list[PlayerTransition]) -> State:
    try:
        _get_player_previous_transition(
            player_current_state, time, transitions).source_state
    except:
        return None
