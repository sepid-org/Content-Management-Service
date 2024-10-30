from django.core.management.base import BaseCommand

from apps.fsm.models.content_widgets import Placeholder


class Command(BaseCommand):
    help = 'Delete all Placeholder with a specific destination_page_url.'

    def handle(self, *args, **kwargs):
        name = "profile-pic"
        placeholders = Placeholder.objects.filter(_object__name=name)
        for placeholder in placeholders:
            placeholder._object.name = "ashbaria-my-profile"
            placeholder._object.save()
        self.stdout.write(self.style.SUCCESS(
            f'Successfully deleted Placeholder with destination_page_url="{name}"'))
