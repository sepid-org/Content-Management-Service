from threading import Thread
from apps.fsm.models import PlayerStateHistory, PlayerTransition
from django.db import transaction

from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        def long_task():
            playerStateHistories = PlayerStateHistory.objects.all()
            for playerStateHistory in playerStateHistories:

                @transaction.atomic
                def do():
                    if not playerStateHistory.is_processed:

                        playerStateHistory.is_processed = True

                        if playerStateHistory.transited_edge and playerStateHistory.is_edge_transited_in_reverse is None:
                            edge = playerStateHistory.transited_edge
                            player = playerStateHistory.player
                            is_reverse = playerStateHistory.is_edge_transited_in_reverse
                            source_state = edge.head if is_reverse else edge.tail
                            target_state = edge.tail if is_reverse else edge.head
                            transition_time = playerStateHistory.arrival_time
                            departure_time = playerStateHistory.departure_time

                            # last player transition
                            last_player_transition = PlayerTransition.objects.create(
                                player=player,
                                source_state=source_state,
                                target_state=target_state,
                                time=transition_time,
                                transited_edge=edge
                            )

                            # previous player state history
                            try:
                                previous_state_history = PlayerStateHistory.objects.filter(
                                    player=player, state=source_state, departure_time__lte=transition_time).last()
                                # previous_state_history.departure_time = transition_time
                                previous_state_history.departure = last_player_transition
                                previous_state_history.save()
                            except:
                                pass

                            # current player state history
                            playerStateHistory.arrival = last_player_transition

                        playerStateHistory.save()

                    if not playerStateHistory.is_processed2:
                        playerStateHistory.is_processed2 = True
                        playerStateHistory.save()

                        player = playerStateHistory.player

                        arrival_transtion = playerStateHistory.arrival
                        if arrival_transtion:
                            arrival_transtion.player = player
                            arrival_transtion.save()

                        departure_transition = playerStateHistory.departure
                        if departure_transition:
                            departure_transition.player = player
                            departure_transition.save()

                do()

        thread = Thread(target=long_task)
        thread.start()
