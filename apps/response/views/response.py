from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError

from apps.fsm.models.fsm import Player, State
from apps.fsm.utils import transit_player_in_fsm
from apps.widgets.models.other_widgets.button import ButtonWidget
from apps.attributes.models import PerformableAction


class ButtonSubmissionService:
    """Service class to handle button widget submission logic"""

    def __init__(self, user, request_data):
        self.user = user
        self.request_data = request_data
        self.state = None
        self.player = None

    def process(self):
        """Main method to process button submission"""
        self._validate_input()
        self._get_or_create_player()

        if self.state_transition_required():
            self._handle_state_transition()
        else:
            self._handle_button_actions()

    def _validate_input(self):
        """Validate required input data"""
        state_id = self.request_data.get('state')
        if not state_id:
            raise ValidationError('State ID is required')

        self.state = get_object_or_404(State, id=state_id)

    def _get_or_create_player(self):
        """Get existing player or create new one"""
        self.player = Player.objects.filter(
            user=self.user,
            fsm=self.state.fsm,
            finished_at__isnull=True
        ).first()

        if not self.player:
            self.player = Player.objects.create(
                user=self.user,
                fsm=self.state.fsm,
                current_state=self.state
            )

    def state_transition_required(self):
        """Determine if state transition is needed"""
        return bool(self.state)

    def _handle_state_transition(self):
        """Handle state transition logic"""
        transit_player_in_fsm(
            player=self.player,
            source_state=self.player.current_state,
            target_state=self.state
        )

    def _handle_button_actions(self):
        """Handle button-specific actions"""
        button_id = self.request_data.get('button')
        if not button_id:
            raise ValidationError(
                'Button ID is required when no state transition is specified')

        button = get_object_or_404(ButtonWidget, id=button_id)
        self._perform_button_attributes(button)

    def _perform_button_attributes(self, button):
        """Execute all performable actions for the button"""
        performable_attributes = button.attributes.instance_of(
            PerformableAction)
        for attribute in performable_attributes:
            attribute.perform(player=self.player, request=self.request_data)


@api_view(["POST"])
def submit_button_widget(request):
    """
    Handle button widget submission

    Expects either 'state' or 'button' in request data
    Returns 200 OK on success
    """
    try:
        service = ButtonSubmissionService(request.user, request.data)
        service.process()
        return Response(status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
