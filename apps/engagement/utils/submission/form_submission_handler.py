from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.attributes.utils import perform_posterior_actions
from apps.fsm.models.form import AnswerSheet
from apps.engagement.utils.submission.abstract_submission_handler import AbstractSubmissionHandler
from apps.engagement.serializers.answer_sheet import AnswerSheetSerializer


class FormSubmissionHandler(AbstractSubmissionHandler):
    def __init__(self, form, **kwargs):
        super().__init__(**kwargs)
        self.form = form

    def validate_submission(self, data):
        if self.form.participant_limit > 0:
            if self.user.is_anonymous:
                raise PermissionDenied(
                    "You must be logged in to submit this form.")

            submission_count = AnswerSheet.objects.filter(
                user=self.user, form=self.form).count()
            if submission_count >= self.form.participant_limit:
                raise PermissionDenied(
                    f"You have exceeded the submission limit of {self.form.participant_limit} for this form."
                )

    def prepare_submission_data(self, data):
        submission_data = {
            'user': self.user.id,
            'form': self.form.id,
            **data
        }
        self._validate_submission_data(submission_data)
        return submission_data

    def _validate_submission_data(self, data):
        required_fields = ['answers']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

    def save_submission(self, validated_data):
        serializer = AnswerSheetSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def perform_post_submission_actions(self):
        perform_posterior_actions(
            attributes=self.form.attributes,
            user=self.user,
            player=self.player,
            website=self.website,
        )

    def get_response_data(self, submission):
        return AnswerSheetSerializer(submission).data
