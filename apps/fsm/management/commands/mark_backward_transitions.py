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
        # 1) Build a queryset of all relevant transitions
        backward_qs = PlayerTransition.objects.filter(
            target_state__outward_edges__head=F('source_state'),
            is_backward=False
        )

        # 2) Extract all PKs so we can chunk‐update and show progress
        all_ids = list(backward_qs.values_list('pk', flat=True))
        total = len(all_ids)
        self.stdout.write(f"Total transitions to mark: {total}")

        if total == 0:
            return

        batch_size = 10000
        updated = 0

        # 3) Iterate in batches, updating each batch and printing progress
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            batch_ids = all_ids[start:end]

            PlayerTransition.objects.filter(
                pk__in=batch_ids).update(is_backward=True)
            updated += len(batch_ids)

            self.stdout.write(f"Progress: {updated}/{total}")

        self.stdout.write(
            f"Done; marked {updated} transition(s) as is_backward.")
