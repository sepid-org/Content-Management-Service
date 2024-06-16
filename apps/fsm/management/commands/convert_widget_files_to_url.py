from django.core.management.base import BaseCommand
from apps.fsm.models import Video, Image, Audio
from django.db import transaction


class Command(BaseCommand):

    def handle(self, *args, **options):

        @transaction.atomic
        def do_videos():
            for video in Video.objects.all():
                if video.file:
                    video.link = video.file.url
                    video.save()

        @transaction.atomic
        def do_images():
            for image in Image.objects.all():
                if image.file:
                    image.link = image.file.url
                    image.save()

        @transaction.atomic
        def do_audios():
            for audio in Audio.objects.all():
                if audio.file:
                    audio.link = audio.file.url
                    audio.save()

        do_videos()
        do_images()
        do_audios()
