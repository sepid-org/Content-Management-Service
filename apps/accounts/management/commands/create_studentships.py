from django.core.management.base import BaseCommand

from apps.accounts.models import AcademicStudentship, SchoolStudentship, User


class Command(BaseCommand):
    help = 'Ensure all users have both school and academic studentships'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            if not hasattr(user, 'school_studentship'):
                SchoolStudentship.objects.create(user=user)
            if not hasattr(user, 'academic_studentship'):
                AcademicStudentship.objects.create(user=user)
        self.stdout.write(self.style.SUCCESS(
            'Verified all users have required studentships'))
