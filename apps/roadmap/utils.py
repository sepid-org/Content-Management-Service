from django.utils import timezone
from apps.fsm.utils.utils import _get_fsm_edges
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
    transitions: list[PlayerTransition] = player.player_transitions.order_by(
        'time').all()
    taken_path: list[Link] = []

    for transition in transitions:
        link = Link.get_link_from_transition(transition)
        if link:
            taken_path.append(link)

    return taken_path
