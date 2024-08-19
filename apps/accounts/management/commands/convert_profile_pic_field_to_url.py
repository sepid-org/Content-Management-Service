from django.core.management.base import BaseCommand
from apps.accounts.models import Studentship
from django.db import transaction


class Command(BaseCommand):

    def handle(self, *args, **options):

        @transaction.atomic
        def do():
            for studentship in Studentship.objects.all():
                if studentship.document:
                    studentship.document2 = studentship.document.url
                    studentship.save()

        do()
