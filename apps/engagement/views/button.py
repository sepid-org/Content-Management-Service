from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.forms import ValidationError
from rest_framework.exceptions import PermissionDenied

from apps.fsm.models.fsm import Player, State
from apps.engagement.utils.submission.button_widget_submission_handler import ButtonWidgetSubmissionHandler
from django.shortcuts import get_object_or_404
from apps.fsm.utils.utils import transit_player_in_fsm


@api_view(["POST"])
def submit_button(request):
    """
    Submit a button
    """
    player_id = request.data.get('player_id', None)
    player = Player.get_player(player_id)
    state_id = request.data.get('state_id', None)
    button_id = request.data.get('button_id', None)
    website = request.website

    try:
        # for button widgets:
        if button_id:
            handler = ButtonWidgetSubmissionHandler(
                user=request.user,
                player=player,
                website=website,
                button_id=button_id,
            )
            response = handler.submit(request.data)
            return response
        # for edges
        elif state_id:
            state = get_object_or_404(State, id=state_id)
            transit_player_in_fsm(
                player=player,
                source_state=player.current_state,
                target_state=state,
            )
            return Response(status=status.HTTP_200_OK)

    except (PermissionDenied, ValidationError) as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
