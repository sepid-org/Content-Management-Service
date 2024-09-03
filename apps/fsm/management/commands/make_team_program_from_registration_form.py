from django.core.management.base import BaseCommand
from apps.fsm.models import Team


class Command(BaseCommand):

    def handle(self, *args, **options):
        for team in Team.objects.all():
            # if team.registration_form:
            #     team.program = team.registration_form.program
            #     team.save()
            #     continue

            members = team.members.all()
            if len(members) > 0:
                first_member = members[0]
                team.program = first_member.form.program
                team.save()
                continue
