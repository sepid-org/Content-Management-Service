from django.core.management.base import BaseCommand
from apps.fsm.models import FSM


class Command(BaseCommand):

    def handle(self, *args, **options):
        for fsm in FSM.objects.all():
            if fsm.cover_page:
                fsm.cover_page2 = fsm.cover_page.url
                fsm.save()
