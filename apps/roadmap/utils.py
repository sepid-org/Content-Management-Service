from apps.fsm.utils import _get_fsm_edges
from apps.roadmap.models import Link
from apps.fsm.models import FSM, Player, PlayerHistory, State


def _get_fsm_links(fsm_id: int):
    fsm = FSM.get_fsm(fsm_id)
    edges = _get_fsm_edges(fsm)
    links = [Link.get_link_from_states(
        edge.tail, edge.head) for edge in edges]
    return links


def _get_player_taken_path(player_id: int):
    player = Player.get_player(player_id)
    player_current_state: State = player.current_state
    fsm = player_current_state.fsm
    histories: list[PlayerHistory] = player.histories.all()
    taken_path: list[Link] = []

    # 100 is consumed as maximum length in a fsm graph
    for i in range(100):
        previous_state = _get_previous_taken_state(
            player_current_state, histories)
        # if the passed_edge is deleted, it isn't possible to reach to previous state
        if not previous_state:
            break
        taken_path.append(Link.get_link_from_states(
            previous_state, player_current_state))
        player_current_state = previous_state

    taken_path.reverse()
    return taken_path


def _get_previous_taken_state(player_current_state: State, histories: list[PlayerHistory]):
    for history in histories:
        if history.is_edge_passed_in_reverse:
            continue
        # if the passed_edge is deleted:
        if not history.passed_edge:
            continue
        if history.passed_edge.head == player_current_state:
            return history.passed_edge.tail
    return None
