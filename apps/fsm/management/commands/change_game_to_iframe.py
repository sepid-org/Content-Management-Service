from django.core.management.base import BaseCommand
from apps.fsm.models import Iframe, Widget


class Command(BaseCommand):

    def handle(self, *args, **options):
        for text in Iframe.objects.all():
            text.widget_type = Widget.WidgetTypes.Iframe
            text.save()
