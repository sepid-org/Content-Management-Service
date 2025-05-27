# <your_app>/management/commands/update_states_dimensions.py

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fsm.models.base import Position
from apps.fsm.models.fsm import State


class Command(BaseCommand):
    help = "Ensure every State has a Position of width=1600 and height=900 (creates Position if missing)."

    def handle(self, *args, **options):
        total_updated = 0
        total_created = 0

        # Wrap the entire loop in a transaction so that if anything fails, nothing is partially written.
        with transaction.atomic():
            for state in State.objects.all():
                # Try to get the existing Position for this State
                try:
                    pos = state.position
                    # Update only if width/height differ
                    if pos.width != 1600 or pos.height != 900:
                        pos.width = 1600
                        pos.height = 900
                        pos.save(update_fields=['width', 'height'])
                        total_updated += 1
                except Position.DoesNotExist:
                    # No Position exists yet: create one with x=0, y=0
                    Position.objects.create(
                        object=state,
                        x=0,
                        y=0,
                        width=1600,
                        height=900,
                    )
                    total_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {total_created} new Position(s), updated {total_updated} existing Position(s)."
        ))
