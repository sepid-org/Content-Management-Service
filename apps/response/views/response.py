from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from apps.fsm.models.fsm import Player, State
from apps.fsm.utils import transit_player_in_fsm
from apps.widgets.models.other_widgets.button import ButtonWidget


@api_view(["POST"])
def submit_button_widget(request):
    state_id = request.data.get('state', None)
    state = get_object_or_404(State, id=state_id)
    user = request.user
    try:
        player = Player.objects.get(
            user=user, fsm=state.fsm, finished_at__isnull=True)
    except:
        player = Player.objects.create(
            user=user,
            fsm=state.fsm,
            current_state=state,
        )

    if state:
        transit_player_in_fsm(
            player=player,
            source_state=player.current_state,
            target_state=state,
        )

    button_id = request.data.get('button', None)
    if button_id:
        button = get_object_or_404(ButtonWidget, id=button_id)

        from apps.attributes.models import PerformableAction
        performable_attributes = button.attributes.instance_of(
            PerformableAction)
        for attribute in performable_attributes:
            attribute.perform(player=player, request=request)

    return Response(status=status.HTTP_200_OK)
