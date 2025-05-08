from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from apps.accounts.models import UserWebsite

class Command(BaseCommand):
    help = (
        "Clears the passwords for all UserWebsite entries whose related user is temporary (is_temporary=True) and have a non-null password, in configurable batches."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many records would be affected without making changes.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10000,
            help="Number of records to process per batch (default: 10000).",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        batch_size = options.get("batch_size", 10000)

        # Only include records with a non-null password
        qs = (
            UserWebsite.objects
            .filter(user__is_temporary=True)
            .exclude(Q(password__isnull=True) | Q(password=""))
            .values_list('pk', flat=True)
            .order_by('pk')
        )
        total = qs.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No UserWebsite records with passwords found for temporary users."))
            return

        self.stdout.write(
            self.style.WARNING(
                f"Found {total} UserWebsite records with passwords for temporary users."
            )
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: would clear passwords for {total} records in batches of {batch_size}."
                )
            )
            return

        updated = 0
        batch = []

        for pk in qs.iterator():
            batch.append(pk)
            if len(batch) >= batch_size:
                with transaction.atomic():
                    UserWebsite.objects.filter(pk__in=batch).update(password=None)
                updated += len(batch)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Cleared passwords for {updated}/{total} records..."
                    )
                )
                batch = []

        # Final batch
        if batch:
            with transaction.atomic():
                UserWebsite.objects.filter(pk__in=batch).update(password=None)
            updated += len(batch)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Cleared passwords for {updated}/{total} records."
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully cleared passwords for all {updated} UserWebsite records."
            )
        )
