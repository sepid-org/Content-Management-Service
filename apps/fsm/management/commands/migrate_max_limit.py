# apps/fsm/management/commands/migrate_max_limit.py
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fsm.models import Program


class Command(BaseCommand):
    help = (
        "Copy each Program.maximum_participant into its "
        "RegistrationForm.max_registrants field."
    )

    def handle(self, *args, **options):
        """
        For every Program that has a registration_form and a non‐None
        maximum_participant, set registration_form.max_registrants to
        maximum_participant and save.
        """
        total = 0

        # Wrap in a transaction so we can roll back if something goes wrong
        with transaction.atomic():
            for program in Program.objects.select_related('registration_form').all():
                max_part = program.maximum_participant
                form = getattr(program, 'registration_form', None)

                # Only migrate if both exist
                if form is not None and max_part is not None:
                    # If the form already had a value, this will override it.
                    form.max_registrants = max_part
                    form.save(update_fields=['max_registrants'])
                    self.stdout.write(
                        f"✔ Program(id={program.id}, slug='{program.slug}') → "
                        f"set RegistrationForm(id={form.id}).max_registrants={max_part}"
                    )
                    total += 1
                else:
                    # For debugging: if no form or no max_part, skip
                    reason = []
                    if form is None:
                        reason.append("no RegistrationForm")
                    if max_part is None:
                        reason.append("maximum_participant is None")
                    reason_str = " & ".join(reason)
                    self.stdout.write(
                        f"✘ Skipped Program(id={program.id}, slug='{program.slug}') → {reason_str}."
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Migration complete: {total} RegistrationForm(s) were updated."
        ))
