import logging
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ParseError
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.models import User
from apps.fsm.models import FSM, AnswerSheet, Edge, Player, PlayerStateHistory, PlayerTransition, Program, RegistrationReceipt, State, Team
from errors.error_codes import serialize_error


def _get_fsm_edges(fsm: FSM) -> list[Edge]:
    return Edge.objects.filter(Q(tail__fsm=fsm) | Q(head__fsm=fsm)).order_by('-id')


class SafeTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request=request)
        except:
            return None


logger = logging.getLogger(__name__)


def get_receipt(user, fsm) -> RegistrationReceipt:
    registration_form = fsm.program.registration_form
    try:
        return RegistrationReceipt.objects.get(user=user, form=registration_form, is_participating=True)
    except:
        return None


def get_players(user, fsm) -> list[Player]:
    return fsm.players.filter(user=user)


def transit_team_in_fsm(team: Team, fsm: FSM, source_state: State, target_state: State, edge: Edge) -> None:
    for member in team.members.all():
        player = member.get_player_of(fsm=fsm)
        if player:
            transit_player_in_fsm(player, source_state, target_state, edge)


def transit_player_in_fsm(player: Player, source_state: State, target_state: State, edge: Edge = None) -> Player:

    if not is_transition_permitted(source_state, target_state):
        raise ParseError(serialize_error('4119'))

    player.current_state = target_state
    transition_time = timezone.now()

    player.last_visit = transition_time
    player.save()

    if edge is None:
        try:
            edge = Edge.objects.get(tail=source_state, head=target_state)
        except Edge.DoesNotExist:
            try:
                edge = Edge.objects.get(tail=target_state, head=source_state)
            except Edge.DoesNotExist:
                pass

    player_transition = PlayerTransition.objects.create(
        player=player,
        source_state=source_state,
        target_state=target_state,
        time=transition_time,
        transited_edge=edge
    )

    try:
        last_state_history = player.player_state_histories.filter(
            state=source_state, departure=None
        ).last()
        last_state_history.departure_time = transition_time
        last_state_history.departure = player_transition
        last_state_history.save()
    except:
        pass

    PlayerStateHistory.objects.create(
        player=player,
        state=target_state,
        arrival=player_transition,
    )

    return player


def is_transition_permitted(source_state: State, target_state: State):
    # if source_state.id == target_state.id:
    #     return True
    # todo
    return True


def get_a_player_from_team(team, fsm) -> Player:
    head_receipt = team.team_head
    players = Player.objects.filter(fsm=fsm, receipt__in=team.members.all())
    if len(players) <= 0:
        logger.info('no player found for any member of team')
        raise ParseError(serialize_error('4088'))
    else:
        player = players.filter(receipt=head_receipt).first()
        if not player:
            player = players.first()
        return player


def get_player_backward_edge(player: Player) -> Edge:
    # todo: it should get the desired backward edge, not mustly the first one
    return player.current_state.inward_edges.first()


def register_user_in_program(user: User, program: Program):
    registration_form = program.registration_form
    try:
        # if there is any registration_receipt, make it registered
        registration_receipt = RegistrationReceipt.objects.get(
            form=registration_form, user=user)
        registration_receipt.is_participating = True
        registration_receipt.status = RegistrationReceipt.RegistrationStatus.Accepted
        registration_receipt.save()
    except:
        # if there is no registration_receipt, create it
        RegistrationReceipt.objects.create(
            form=registration_form,
            user=user,
            answer_sheet_type=AnswerSheet.AnswerSheetType.RegistrationReceipt,
            status=RegistrationReceipt.RegistrationStatus.Accepted,
            is_participating=True)


def get_user_permission(receipt: RegistrationReceipt) -> dict:
    user = receipt.user
    if user in receipt.form.program.modifiers:
        return True
    return False
    # todo


def add_admin_to_program(user: User, program: Program):
    program.admins.add(user)
    register_user_in_program(user, program)


class AnswerSheetFacade:
    def __init__(self, answer_sheet) -> None:
        self.answer_sheet = answer_sheet

    def check_expected_choices(self, expected_choice_ids):
        try:
            # Get all multi-choice answers in one query
            from apps.fsm.models.response import MultiChoiceAnswer
            multi_choice_answers = (
                self.answer_sheet.answers
                .instance_of(MultiChoiceAnswer)
                .prefetch_related('choices')
            )

            # Create a set of all selected choice IDs for O(1) lookup
            all_choice_ids = {
                choice.id
                for answer in multi_choice_answers
                for choice in answer.choices.all()
            }

            # Check if all expected choices exist in the set
            return all(choice_id in all_choice_ids for choice_id in expected_choice_ids)
        except:
            return False

    def check_expected_choices_in_last_answer(self, expected_choice_ids):
        try:
            # Get the last multi-choice answer in a single query
            from apps.fsm.models.response import MultiChoiceAnswer
            last_answer = (
                self.answer_sheet.answers
                .instance_of(MultiChoiceAnswer)
                .prefetch_related('choices')
                .latest('id')
            )

            # Convert both sets of choices to sets for comparison
            submitted_choice_ids = {
                choice.id for choice in last_answer.choices.all()}

            expected_choice_ids = set(expected_choice_ids)

            return submitted_choice_ids == expected_choice_ids
        except:
            return False

    def check_expected_correct_choices_in_last_answer_count(self, expected_correct_choices_in_last_answer_count):
        try:
            # Get the last multi-choice answer in a single query
            from apps.fsm.models.response import MultiChoiceAnswer
            last_answer = (
                self.answer_sheet.answers
                .instance_of(MultiChoiceAnswer)
                .prefetch_related('choices')
                .latest('id')
            )

            # Count how many of the selected choices are marked as correct
            correct_choices_count = sum(
                1 for choice in last_answer.choices.all()
                if choice.is_correct
            )

            return correct_choices_count == expected_correct_choices_in_last_answer_count
        except:
            return False
