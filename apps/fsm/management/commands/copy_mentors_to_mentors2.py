from django.core.management.base import BaseCommand

from apps.fsm.models.fsm import FSM


class Command(BaseCommand):
    help = 'Copies mentors user ids to mentors2 with manager role'

    def handle(self, *args, **kwargs):
        fsms = FSM.objects.all()
        updated_count = 0

        for i, fsm in enumerate(fsms, start=1):
            mentors = fsm.mentors.all()
            if mentors:
                # ایجاد mentors2 جدید با role "manager"
                formatted_mentors = [
                    {"id": str(m.id), "role": "manager"} for m in mentors
                ]
                fsm.mentors2 = formatted_mentors
                fsm.save(update_fields=['mentors2'])
                updated_count += 1

            if i % 50 == 0:
                print(f"{i}/{fsms.count()} FSMs processed...")

        self.stdout.write(self.style.SUCCESS(
            f"Successfully updated mentors2 in {updated_count} FSM records."
        ))
