from django.shortcuts import get_object_or_404

from .base import PerformableAction
from django.db import models


class Answer(PerformableAction):
    class AnswerTypes(models.TextChoices):
        SmallAnswer = 'SmallAnswer'
        BigAnswer = 'BigAnswer'
        MultiChoiceAnswer = 'MultiChoiceAnswer'
        UploadFileAnswer = 'UploadFileAnswer'

    question_id = models.PositiveIntegerField()
    answer_type = models.CharField(max_length=20, choices=AnswerTypes.choices)
    provided_answer = models.JSONField(default=dict)

    def perform(self, *args, **kwargs) -> bool:
        if not super().perform(*args, **kwargs):
            return False

        from apps.response.utils import AnswerFacade

        user = kwargs.get('user')
        player = kwargs.get('player')
        if not user:
            return False

        facade = AnswerFacade()
        facade.submit_answer(
            user=user,
            player=player,
            provided_answer={
                'answer_type': self.answer_type,
                **self.provided_answer,
            },
            question=facade.get_question(self.question_id),
        )

        return True


class Transition(PerformableAction):
    destination_state_id = models.IntegerField()

    def perform(self, *args, **kwargs) -> bool:
        if not super().perform(*args, **kwargs):
            return False

        from apps.fsm.models.fsm import State
        from apps.fsm.utils import transit_player_in_fsm
        destination_state = get_object_or_404(
            State,
            id=self.destination_state_id
        )

        player = kwargs.get('player')
        transit_player_in_fsm(
            player,
            player.current_state,
            destination_state,
        )

        return True


class Submission(PerformableAction):

    def perform(self, *args, **kwargs):
        if not super().perform(*args, **kwargs):
            return False

        # perform main action:
        self.give_reward(*args, **kwargs)

        from apps.attributes.utils import perform_posterior_actions
        perform_posterior_actions(
            attributes=self.attributes,
            *args,
            **kwargs,
        )

        return True


class Buy(PerformableAction):

    def perform(self, *args, **kwargs):
        if not super().perform(*args, **kwargs):
            return False

        return True
