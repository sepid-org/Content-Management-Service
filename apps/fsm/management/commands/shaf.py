from django.core.management.base import BaseCommand

from apps.fsm.models.content_widgets import Placeholder


class Command(BaseCommand):
    help = 'Delete all Placeholder with a specific destination_page_url.'

    def handle(self, *args, **kwargs):
        name = "dadbestan-name"
        deleted_count, _ = Placeholder.objects.filter(_object__name=name).delete()
        self.stdout.write(self.style.SUCCESS(
            f'Successfully deleted {deleted_count} Placeholder with destination_page_url="{name}"'))
