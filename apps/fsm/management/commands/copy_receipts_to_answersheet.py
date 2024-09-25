from django.core.management.base import BaseCommand

from apps.fsm.models.form import AnswerSheet, RegistrationReceipt


class Command(BaseCommand):
    help = 'Copies all RegistrationReceipt fields to AnswerSheet'

    def handle(self, *args, **kwargs):
        # Get all registration receipts
        receipts = RegistrationReceipt.objects.all()

        # Iterate over each receipt and copy its values to a new AnswerSheet
        for receipt in receipts:
            answer_sheet = AnswerSheet.objects.get(id=receipt.id)

            answer_sheet.form2 = receipt.form

            # Save the AnswerSheet
            answer_sheet.save()

            # Output success message
            self.stdout.write(self.style.SUCCESS(
                f'Copied RegistrationReceipt {receipt.id} to AnswerSheet {answer_sheet.id}'))

        self.stdout.write(self.style.SUCCESS(
            'Successfully copied all RegistrationReceipts to AnswerSheets'))
