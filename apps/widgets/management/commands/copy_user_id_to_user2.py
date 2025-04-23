from django.core.management.base import BaseCommand

from apps.widgets.models.other_widgets.random import SeenWidget


class Command(BaseCommand):
    help = 'Copies user.id to user2 for SeenWidget records where user2 is null'

    def handle(self, *args, **kwargs):
        widgets_to_update = SeenWidget.objects.filter(user2__isnull=True)
        total = widgets_to_update.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("No records to update."))
            return

        self.stdout.write(f"Updating {total} SeenWidget records...")

        updated_count = 0

        for i, widget in enumerate(widgets_to_update, start=1):
            widget.user2 = widget.user.id
            widget.save(update_fields=['user2'])
            updated_count += 1

            if i % 100 == 0 or i == total:
                print(f"{i}/{total} records processed...")

        self.stdout.write(self.style.SUCCESS(
            f"Finished. Successfully updated {updated_count} records."
        ))
