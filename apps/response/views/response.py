from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from apps.fsm.models.fsm import Player, State
from apps.fsm.utils import transit_player_in_fsm
from apps.widgets.models.other_widgets.button import ButtonWidget


@api_view(["POST"])
def submit_button_widget(request):
    player_id = request.data.get('player_id', None)
    player = get_object_or_404(Player, id=player_id)

    state_id = request.data.get('state_id', None)
    if state_id:
        state = get_object_or_404(State, id=state_id)
        transit_player_in_fsm(
            player=player,
            source_state=player.current_state,
            target_state=state,
        )

    button_id = request.data.get('button_id', None)
    if button_id:
        button = get_object_or_404(ButtonWidget, id=button_id)

        from apps.attributes.utils import perform_posterior_actions
        perform_posterior_actions(
            attributes=button.attributes,
            player=player,
            user=request.user,
            request=request
        )

    return Response(status=status.HTTP_200_OK)
