from django.core.management.base import BaseCommand
from apps.accounts.models import AcademicStudentship, SchoolStudentship, User
from django.db import transaction


class Command(BaseCommand):
    help = 'Ensure all users have both school and academic studentships'

    def handle(self, *args, **kwargs):
        batch_size = 1000  # Process users in batches of 1000
        users = User.objects.all().values_list('id', flat=True)

        for start in range(0, len(users), batch_size):
            batch = users[start:start + batch_size]

            # Create studentships for users missing them
            for user_id in batch:
                self.ensure_studentships(user_id)

        self.stdout.write(self.style.SUCCESS(
            'Verified all users have required studentships'))

    @transaction.atomic
    def ensure_studentships(self, user_id):
        # Use get_or_create for each studentship type
        SchoolStudentship.objects.get_or_create(user_id=user_id)
        AcademicStudentship.objects.get_or_create(user_id=user_id)
