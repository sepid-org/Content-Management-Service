from django.core.management.base import BaseCommand

from apps.widgets.models.other_widgets.random import SeenWidget


class Command(BaseCommand):
    help = 'Copies user.id to user2 for SeenWidget records where user2 is null'

    def handle(self, *args, **kwargs):
        updated_count = 0

        widgets_to_update = SeenWidget.objects.filter(user2__isnull=True)

        for widget in widgets_to_update:
            widget.user2 = widget.user.id
            widget.save(update_fields=['user2'])
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully updated {updated_count} SeenWidget records.'
        ))
