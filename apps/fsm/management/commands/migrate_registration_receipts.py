from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fsm.models.form import AnswerSheet, RegistrationReceipt


class Command(BaseCommand):
    help = 'Migrates RegistrationForm instances to RegistrationForm2'

    def handle(self, *args, **options):
        self.stdout.write(
            'Starting migration of RegistrationForm to RegistrationForm2...')

        registration_receipts = RegistrationReceipt.objects.all()
        total_receipts = registration_receipts.count()
        migrated_receipts = 0

        for receipt in registration_receipts:
            try:
                with transaction.atomic():
                    answer_sheet = AnswerSheet.objects.get(id=receipt.id)
                    answer_sheet.user2 = receipt.user
                    answer_sheet.created_at2 = receipt.created_at
                    answer_sheet.save()

                    migrated_receipts += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully migrated receipt {receipt.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Failed to migrate receipt {receipt.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'Migration completed. {migrated_receipts} out of {total_receipts} receipts migrated successfully.'))
