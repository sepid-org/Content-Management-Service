from django.core.management.base import BaseCommand
from apps.accounts.models import User
from django.db import transaction


class Command(BaseCommand):

    def handle(self, *args, **options):

        @transaction.atomic
        def do():
            for user in User.objects.all():
                if user.profile_picture:
                    user.profile_picture2 = user.profile_picture.url
                    user.save()

        do()
