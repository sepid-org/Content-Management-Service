from django.shortcuts import get_object_or_404

from apps.fsm.models.fsm import State
from apps.engagement.utils.submission.abstract_submission_handler import AbstractSubmissionHandler
from apps.fsm.utils.utils import transit_player_in_fsm
from apps.widgets.models.other_widgets.button import ButtonWidget


class ButtonWidgetSubmissionHandler(AbstractSubmissionHandler):
    def __init__(self, state_id, button_id,  **kwargs):
        super().__init__(**kwargs)
        self.state_id = state_id
        self.button_id = button_id

    def validate_submission(self, data):
        # Validation for button widget submission
        pass

    def prepare_submission_data(self, data):
        return {
            'user': self.user,
            'player': self.player,
            'state_id': self.state_id,
            'button_id': self.button_id,
        }

    def save_submission(self, validated_data):
        # Handle state transition if state_id is provided
        if self.state_id:
            state = get_object_or_404(State, id=self.state_id)
            transit_player_in_fsm(
                player=self.player,
                source_state=self.player.current_state,
                target_state=state,
            )

        return validated_data

    def perform_post_submission_actions(self, submission):
        if self.button_id:
            button = get_object_or_404(ButtonWidget, id=self.button_id)
            from apps.attributes.utils import perform_posterior_actions
            perform_posterior_actions(
                attributes=button.attributes,
                user=self.user,
                player=self.player,
                website=self.website,
            )
