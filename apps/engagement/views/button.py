from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.forms import ValidationError
from rest_framework.exceptions import PermissionDenied

from apps.fsm.models.fsm import Player
from apps.engagement.utils.submission.button_widget_submission_handler import ButtonWidgetSubmissionHandler


@api_view(["POST"])
def submit_button_widget(request):
    """
    Submit an button widget.
    """
    player_id = request.data.get('player_id', None)
    player = Player.get_player(player_id)
    state_id = request.data.get('state_id', None)
    button_id = request.data.get('button_id', None)
    website = request.website

    try:
        handler = ButtonWidgetSubmissionHandler(
            user=request.user,
            player=player,
            website=website,
            state_id=state_id,
            button_id=button_id,
        )
        response = handler.submit(request.data)
        return response

    except (PermissionDenied, ValidationError) as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
