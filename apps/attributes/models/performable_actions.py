from django.shortcuts import get_object_or_404

from apps.attributes.models.utils import SumDict, get_response_allocated_rewards, sum_attribute_values
from apps.attributes.utils import does_object_have_any_reward, get_object_default_rewards
from proxies.bank_service.utils import transfer_funds_to_user

from .base import PerformableAction
from django.db import models


class Rewarding(PerformableAction):

    def perform(self, user, player, website):

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
            transfer_funds_to_user(
                website_uuid=website.uuid,
                user_uuid=str(user.id),
                funds=total_rewards,
            )


class Start(PerformableAction):

    def perform(self, user, player, website):
        if not super().perform(user, player, website):
            return False

        # perform main action:
        self.give_reward(user, player, website)

        return True


class Finish(PerformableAction):

    def perform(self, user, player, website):
        if not super().perform(user, player, website):
            return False

        from apps.attributes.utils import perform_posterior_actions
        perform_posterior_actions(
            attributes=self.attributes,
            user=user,
            player=player,
            website=website,
        )


class Submission(PerformableAction):

    def perform(self, user, player, website):
        if not super().perform(user, player, website):
            return False

        # perform main action:
        self.give_reward(user, player, website)

        from apps.attributes.utils import perform_posterior_actions
        perform_posterior_actions(
            attributes=self.attributes,
            user=user,
            player=player,
            website=website,
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

    def perform(self, user, player, website) -> bool:
        if not super().perform(user, player, website):
            return False

        from apps.engagement.utils.submission.answer_submission_handler import AnswerSubmissionHandler

        if not user:
            return False

        from apps.fsm.models.base import Widget
        question = Widget.objects.get(id=self.question_id)

        handler = AnswerSubmissionHandler(
            user=user,
            player=player,
            website=website,
            question=question,
        )
        handler.submit({
            'answer_type': self.answer_type,
            **self.provided_answer,
        })

        return True


class Transition(PerformableAction):
    destination_state_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="If NULL, this Transition transit the player to its previous state.  "
                  "If not NULL, it transit it to that state (and flags itself as a ‘backward’ transition)."
    )
    is_backward = models.BooleanField(
        default=False,
        help_text="When True, indicates this Transition should be treated as a ‘backward’‐type move."
    )

    def perform(self, user, player, website) -> bool:
        if not super().perform(user, player, website):
            return False

        from apps.fsm.models.fsm import State
        from apps.fsm.utils.utils import transit_player_in_fsm

        if self.is_backward and not self.destination_state_id:
            destination_state = player.get_previous_state()
        else:
            destination_state = get_object_or_404(
                State,
                id=self.destination_state_id
            )

        if not destination_state:
            return False

        transit_player_in_fsm(
            player=player,
            source_state=player.current_state,
            target_state=destination_state,
            is_backward=self.is_backward,
        )

        return True


class Buy(PerformableAction):

    def perform(self, user, player, website):
        if not super().perform(user, player, website):
            return False

        return True
