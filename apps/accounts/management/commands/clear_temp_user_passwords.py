from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import UserWebsite


class Command(BaseCommand):
    help = (
        "Clears the passwords for all UserWebsite entries whose related user is temporary (is_temporary=True)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many records would be affected without making changes.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        queryset = UserWebsite.objects.filter(user__is_temporary=True)
        total = queryset.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS(
                "No UserWebsite records found for temporary users."))
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: {total} UserWebsite records would have their passwords cleared."
                )
            )
            return

        with transaction.atomic():
            # Using update to clear passwords in bulk
            updated = queryset.update(password=None)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully cleared passwords for {updated} UserWebsite records."
            )
        )
