from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.attributes.utils import perform_posterior_actions
from apps.fsm.utils.submission.abstract_submission_handler import AbstractSubmissionHandler
from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer
from errors.error_codes import serialize_error
from rest_framework.exceptions import ParseError


class AnswerSubmissionHandler(AbstractSubmissionHandler):
    def __init__(self, question, user, player=None):
        super().__init__(user=user)
        self.question = question
        self.player = player

    def validate_submission(self, request, *args, **kwargs):
        # Check if user is authenticated
        if self.user.is_anonymous:
            raise PermissionDenied(
                "You must be logged in to submit an answer."
            )

        # Validate player eligibility if player exists
        if self.player:
            self._validate_player_eligibility()

        # Validate question submission rules (including checking for previous correct answers)
        self._validate_question_submission_rules()

    def _validate_player_eligibility(self):
        # Ensure the player belongs to the current user
        if self.player.user != self.user:
            raise PermissionDenied(
                "You are not authorized to submit for this player."
            )

    def _validate_question_submission_rules(self):
        from apps.fsm.models.response import Answer

        # Check if user has already answered this question correctly
        if self.question.correct_answer:
            user_correctly_answered_problems = Answer.objects.filter(
                submitted_by=self.user, is_correct=True)
            for answer in user_correctly_answered_problems:
                if answer.problem == self.question:
                    raise ParseError(serialize_error('6000'))

    def prepare_submission_data(self, request, *args, **kwargs):
        # Prepare submission data with user, problem, and player information
        submission_data = {
            'is_final_answer': False,
            'problem': self.question.id,
            'submitted_by': self.user.id,
            **request.data
        }

        # Validate the submission data
        self._validate_submission_data(submission_data)
        return submission_data

    def _validate_submission_data(self, data):
        # Validate required fields (customize based on question type)
        required_fields = []  # Add required fields based on question type
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(
                    f"Missing or empty required field: {field}"
                )

    def save_submission(self, data, *args, **kwargs):
        # Use AnswerPolymorphicSerializer to save the answer
        serializer = AnswerPolymorphicSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()

        # Save answer in the player's answer sheet if player exists
        if self.player:
            answer_sheet = self.player.answer_sheet
            answer.answer_sheet = answer_sheet
            answer.save()

        return answer

    def perform_post_submission_actions(self, submission, request, *args, **kwargs):
        # Perform posterior actions after answer submission
        perform_posterior_actions(
            attributes=self.question.attributes,
            question=self.question,
            answer=submission,
            player=self.player,
            user=self.user,
            request=request
        )

    def get_response_data(self, submission):
        # Serialize the submission for response
        return AnswerPolymorphicSerializer(submission).data
