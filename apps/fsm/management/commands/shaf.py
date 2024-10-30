from django.core.management.base import BaseCommand

from apps.widgets.models.other_widgets.button import ButtonWidget

class Command(BaseCommand):
    help = 'Delete all ButtonWidgets with a specific destination_page_url.'

    def handle(self, *args, **kwargs):
        url_to_delete = "https://ashbaria.sepid.org/program/ashbaria/"
        deleted_count, _ = ButtonWidget.objects.filter(destination_page_url=url_to_delete).delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} ButtonWidgets with destination_page_url="{url_to_delete}"'))
