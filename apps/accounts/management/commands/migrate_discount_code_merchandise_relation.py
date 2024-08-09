from django.core.management.base import BaseCommand
from apps.accounts.models import DiscountCode
from django.db import transaction


class Command(BaseCommand):

    def handle(self, *args, **options):

        @transaction.atomic
        def do():
            for discount_code in DiscountCode.objects.all():
                discount_code.merchandise2.add(discount_code.merchandise)
                discount_code.save()
        do()
