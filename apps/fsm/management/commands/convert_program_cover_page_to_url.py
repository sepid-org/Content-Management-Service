from django.core.management.base import BaseCommand
from apps.fsm.models import Program


class Command(BaseCommand):

    def handle(self, *args, **options):
        for program in Program.objects.all():
            if program.cover_page:
                program.cover_page2 = program.cover_page.url
                program.save()
