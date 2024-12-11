from django.shortcuts import get_object_or_404

from apps.attributes.models.utils import SumDict, get_response_allocated_rewards, sum_attribute_values
from apps.attributes.utils import does_object_have_any_reward, get_object_default_rewards
from proxies.bank_service.utils import transfer_funds_to_user

from .base import PerformableAction
from django.db import models


class Rewarding(PerformableAction):

    def perform(self, *args, **kwargs):
        player = kwargs.get('player')

        if player:
            total_rewards = SumDict({})
            fsm = player.fsm

            for answer in player.answer_sheet.answers.filter(is_final_answer=True):
                if does_object_have_any_reward(answer.problem):
                    total_rewards += SumDict(answer.get_allocated_rewards())
                else:
                    answer_assessment_score = answer.assess()['score']
                    fsm_net_reward = sum_attribute_values(
                        get_object_default_rewards(fsm))
                    total_rewards += SumDict(
                        get_response_allocated_rewards(
                            response_net_rewards=fsm_net_reward,
                            allocation_percentage=answer_assessment_score,
                        )
                    )

            if total_rewards.is_zero():
                return

            # Process the transfer
            request = kwargs.get('request')
            website_name = request.headers.get('Website')
            transfer_funds_to_user(
                website_name=website_name,
                user_uuid=str(request.user.id),
                funds=total_rewards,
            )


class Start(PerformableAction):

    def perform(self, *args, **kwargs):
        if not super().perform(*args, **kwargs):
            return False

        # perform main action:
        self.give_reward(*args, **kwargs)

        return True


class Finish(PerformableAction):

    def perform(self, *args, **kwargs):
        if not super().perform(*args, **kwargs):
            return False

        from apps.attributes.utils import perform_posterior_actions
        perform_posterior_actions(
            attributes=self.attributes,
            *args,
            **kwargs,
        )


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
        from apps.fsm.utils.utils import transit_player_in_fsm
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


class Buy(PerformableAction):

    def perform(self, *args, **kwargs):
        if not super().perform(*args, **kwargs):
            return False

        return True
