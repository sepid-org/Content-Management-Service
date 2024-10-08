from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fsm.models.base import Paper
from apps.fsm.models.fsm import State, State2


class Command(BaseCommand):
    help = 'Migrate State records to State2'

    def handle(self, *args, **kwargs):
        # Get all State records
        states = State.objects.all()
        for state in states:
            self.migrate_state(state)

    @transaction.atomic
    def migrate_state(self, state: State):
        try:
            # Create a new State2 record based on the State record
            state2 = State2.objects.create(
                title=state.title,
                name=state.name,
                is_private=state.is_private,
                creator=state.creator.id if state.creator else None,
                order=state.order,
                is_hidden=state.is_hidden,
                template=state.template,
                fsm=state.fsm,
                show_appbar=state.show_appbar,
                is_end=state.is_end
            )
            state2.save()

            # handle Paper
            state_paper = Paper.objects.get(id=state.id)
            state2.papers.add(state_paper)

            # handle FSM:
            try:
                my_fsm = state.my_fsm
                my_fsm.first_state2 = state2
                my_fsm.save()
            except:
                pass

            # handle Player
            players = state.players.all()
            for player in players:
                player.current_state2 = state2
                player.save()

            # handle Edge
            outward_edges = state.outward_edges.all()
            for outward_edge in outward_edges:
                outward_edge.tail2 = state2
                outward_edge.save()

            inward_edges = state.inward_edges.all()
            for inward_edge in inward_edges:
                inward_edge.head2 = state2
                inward_edge.save()

            # handle PlayerTransition
            player_departure_transitions = state.player_departure_transitions.all()
            for player_departure_transition in player_departure_transitions:
                player_departure_transition.source_state2 = state2
                player_departure_transition.save()

            player_arrival_transitions = state.player_arrival_transitions.all()
            for player_arrival_transition in player_arrival_transitions:
                player_arrival_transition.target_state2 = state2
                player_arrival_transition.save()

            # handle PlayerStateHistory
            player_state_histories = state.player_state_histories.all()
            for player_state_history in player_state_histories:
                player_state_history.state2 = state2
                player_state_history.save()

            # handle Hint
            hints = state.hints.all()
            for hint in hints:
                hint.reference2 = state2
                hint.save()

            self.stdout.write(self.style.SUCCESS(
                f'Successfully migrated State {state.id} to State2 {state2.id}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error migrating State {state.id}: {e}'))
