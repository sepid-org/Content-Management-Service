from django.shortcuts import get_object_or_404

from apps.engagement.utils.submission.abstract_submission_handler import AbstractSubmissionHandler
from apps.widgets.models.other_widgets.button import ButtonWidget


class ButtonWidgetSubmissionHandler(AbstractSubmissionHandler):
    def __init__(self, button_id,  **kwargs):
        super().__init__(**kwargs)
        self.button = get_object_or_404(ButtonWidget, id=button_id)

    def perform_post_submission_actions(self):
        from apps.attributes.utils import perform_posterior_actions
        perform_posterior_actions(
            attributes=self.button.attributes,
            user=self.user,
            player=self.player,
            website=self.website,
        )
