from django.shortcuts import get_object_or_404

from .base import PerformableAction
from django.db import models


class Transition(PerformableAction):
    destination_state_id = models.IntegerField()

    def perform(self, *arg, **kwargs) -> bool:

        if not self.is_permitted(*arg, **kwargs):
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


class Buy(PerformableAction):

    def perform(self, *arg, **kwargs):
        # todo
        return True


class Submission(PerformableAction):

    def perform(self, *arg, **kwargs):

        if not self.is_permitted(*arg, **kwargs):
            return False

        self.give_reward(*arg, **kwargs)

        return True
