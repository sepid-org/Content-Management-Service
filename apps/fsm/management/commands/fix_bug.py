from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fsm.models.form import RegistrationForm, RegistrationForm2
from apps.fsm.models.program import Program


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(
            'Starting migration of RegistrationForm to RegistrationForm2...')

        programs = Program.objects.all()

        for program in programs:
            try:
                with transaction.atomic():
                    form1 = program.registration_form
                    form2 = program.registration_form2

                    registration_receipts1 = form1.answer_sheets.all()
                    for receipt in registration_receipts1:
                        receipt.form22 = form2
                        receipt.save()

                    certificate_templates = form1.certificate_templates.all()
                    for template in certificate_templates:
                        template.registrationForm2 = form2
                        template.save()
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Failed {program.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'job completed'))
