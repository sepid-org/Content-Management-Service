from django.core.management import BaseCommand

from apps.accounts.models import User, UserWebsite
from apps.fsm.models import RegistrationReceipt


class Command(BaseCommand):

    def handle(self, *args, **options):
        for registration_receipt in RegistrationReceipt.objects.filter(answer_sheet_of=None):
            program = None
            for player in registration_receipt.players.all():
                program = player.fsm.program
            if program:
                registration_receipt.answer_sheet_of = program.registration_form
                registration_receipt.save()
            else:
                registration_receipt.delete()
