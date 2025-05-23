# apps/fsm/management/commands/mark_backward_transitions.py

from django.core.management.base import BaseCommand
from django.db.models import F

from apps.fsm.models.fsm import PlayerTransition


class Command(BaseCommand):
    help = (
        "Bulk‐mark every PlayerTransition as is_backward=True "
        "if it goes against an existing Edge (i.e. source↔target are swapped)."
    )

    def handle(self, *args, **options):
        # Filter only those transitions where there is an Edge with
        # tail = pt.target_state and head = pt.source_state, and which aren’t already marked.
        backward_qs = PlayerTransition.objects.filter(
            target_state__outward_edges__head=F('source_state'),
            is_backward=False
        )

        # Perform a bulk update
        updated_count = backward_qs.update(is_backward=True)

        self.stdout.write(
            f"Marked {updated_count} transition(s) as is_backward.")
