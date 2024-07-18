from django.core.management.base import BaseCommand
from apps.fsm.models import UploadFileAnswer


class Command(BaseCommand):

    def handle(self, *args, **options):
        for answer in UploadFileAnswer.objects.all():
            answer.answer_file2 = answer.answer_file.url
            answer.save()
