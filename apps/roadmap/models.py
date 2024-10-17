from apps.fsm.models import PlayerTransition, State


# todo: refactor: Link model should be replaced with PlayerTransition model
class Link:
    source: str
    target: str

    def __init__(self, source: State, target: State):
        self.source = source
        self.target = target

    @staticmethod
    def get_link_from_states(source_state: State, target_state: State):
        if not source_state or not target_state:
            return None
        return Link(source_state.title, target_state.title)

    @staticmethod
    def get_link_from_transition(player_transition: PlayerTransition):
        return Link.get_link_from_states(player_transition.source_state, player_transition.target_state)
