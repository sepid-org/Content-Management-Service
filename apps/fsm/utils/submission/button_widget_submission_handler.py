from django.shortcuts import get_object_or_404

from apps.fsm.models.fsm import Player, State
from apps.fsm.utils.submission.abstract_submission_handler import AbstractSubmissionHandler
from apps.fsm.utils.utils import transit_player_in_fsm
from apps.widgets.models.other_widgets.button import ButtonWidget


class ButtonWidgetSubmissionHandler(AbstractSubmissionHandler):
    def __init__(self, user, state_id, button_id, player_id):
        self.state_id = state_id
        self.button_id = button_id
        player_id = player_id
        self.player = get_object_or_404(Player, id=player_id)
        self.user = user

    def validate_submission(self, *args, **kwargs):
        # Validation for button widget submission
        pass

    def prepare_submission_data(self, *args, **kwargs):
        return {
            'player': self.player,
            'state_id': self.state_id,
            'button_id': self.button_id,
            'user': self.user,
        }

    def save_submission(self, data, *args, **kwargs):
        # Handle state transition if state_id is provided
        if self.state_id:
            state = get_object_or_404(State, id=self.state_id)
            transit_player_in_fsm(
                player=self.player,
                source_state=self.player.current_state,
                target_state=state,
            )

        return data

    def perform_post_submission_actions(self, submission, request, *args, **kwargs):
        if self.button_id:
            button = get_object_or_404(ButtonWidget, id=self.button_id)
            from apps.attributes.utils import perform_posterior_actions
            perform_posterior_actions(
                attributes=button.attributes,
                player=submission['player'],
                user=self.user,
                request=request,
            )
