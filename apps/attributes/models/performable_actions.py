from django.shortcuts import get_object_or_404

from .base import PerformableAction
from django.db import models


class Transition(PerformableAction):
    destination_state_id = models.IntegerField()

    def perform(self, player):
        is_permitted = True

        for attribute in self.attributes.all():
            from .intrinsic_attributes import Condition

            if isinstance(attribute, Condition):
                is_permitted &= attribute.is_true(player)

        if is_permitted:
            from apps.fsm.models.fsm import State
            from apps.fsm.utils import transit_player_in_fsm

            destination_state = get_object_or_404(
                State,
                id=self.destination_state_id
            )
            transit_player_in_fsm(
                player, player.current_state, destination_state)
