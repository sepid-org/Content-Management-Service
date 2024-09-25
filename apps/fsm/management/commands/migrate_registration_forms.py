from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fsm.models.form import RegistrationForm, RegistrationForm2


class Command(BaseCommand):
    help = 'Migrates RegistrationForm instances to RegistrationForm2'

    def handle(self, *args, **options):
        self.stdout.write(
            'Starting migration of RegistrationForm to RegistrationForm2...')

        registration_forms = RegistrationForm.objects.all()
        total_forms = registration_forms.count()
        migrated_forms = 0

        for form in registration_forms:
            try:
                with transaction.atomic():
                    new_form = RegistrationForm2(
                        # Fields from Paper model
                        paper_type=form.paper_type,
                        # Add other fields from Paper model as needed

                        # Fields from Form model
                        audience_type=form.audience_type,
                        start_date=form.since,
                        end_date=form.till,

                        # Fields specific to RegistrationForm2
                        min_grade=form.min_grade,
                        max_grade=form.max_grade,
                        accepting_status=form.accepting_status,
                        gender_partition_status=form.gender_partition_status,
                        has_certificate=form.has_certificate,
                        certificates_ready=form.certificates_ready,
                    )
                    new_form.save()

                    # Copy related objects if needed
                    # Example: new_form.some_related_objects.set(form.some_related_objects.all())
                    form.program.registration_form2 = new_form
                    form.program.save()

                    migrated_forms += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully migrated form {form.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Failed to migrate form {form.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'Migration completed. {migrated_forms} out of {total_forms} forms migrated successfully.'))
