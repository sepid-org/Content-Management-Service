from django.core.management import BaseCommand

from apps.accounts.models import User, UserWebsite
from apps.fsm.models import RegistrationReceipt


class Command(BaseCommand):

    def handle(self, *args, **options):
        for registration_receipt in RegistrationReceipt.objects.all():
            website = registration_receipt.form.program.website
            user = registration_receipt.user
            try:
                UserWebsite.objects.create(
                    user=user,
                    website=website,
                    password=user.password,
                )
            except:
                pass
