from django.core.management.base import BaseCommand
from apps.fsm.models import Program


class Command(BaseCommand):

    def handle(self, *args, **options):
        for program in Program.objects.all():
            if program.cover_image:
                program.cover_image2 = program.cover_image.url
                program.save()
