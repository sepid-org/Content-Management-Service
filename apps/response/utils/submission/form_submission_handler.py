from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.attributes.utils import perform_posterior_actions
from apps.fsm.models.form import AnswerSheet
from apps.response.utils.submission.abstract_submission_handler import AbstractSubmissionHandler
from apps.response.serializers.answer_sheet import AnswerSheetSerializer


class FormSubmissionHandler(AbstractSubmissionHandler):
    def __init__(self, form, user):
        super().__init__(user=user)
        self.form = form

    def validate_submission(self, request, *args, **kwargs):
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

    def prepare_submission_data(self, request, *args, **kwargs):
        submission_data = {
            'user': self.user.id,
            'form': self.form.id,
            **request.data
        }
        self._validate_submission_data(submission_data)
        return submission_data

    def _validate_submission_data(self, data):
        required_fields = ['answers']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

    def save_submission(self, data, *args, **kwargs):
        serializer = AnswerSheetSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def perform_post_submission_actions(self, submission, request, *args, **kwargs):
        perform_posterior_actions(
            attributes=self.form.attributes,
            request=request,
            answer_sheet=submission
        )

    def get_response_data(self, submission):
        return AnswerSheetSerializer(submission).data
