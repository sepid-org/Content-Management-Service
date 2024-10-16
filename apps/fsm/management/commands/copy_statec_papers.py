from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fsm.models.base import Paper
from apps.fsm.models.fsm import Statec
from apps.fsm.views.fsm_state_view import add_paper_to_fsm_state


class Command(BaseCommand):
    help = 'Migrate State records to State2'

    def handle(self, *args, **kwargs):
        # Get all State records
        statecs = Statec.objects.filter(flag=False)
        for statec in statecs:
            self.migrate_state(statec)

    @transaction.atomic
    def migrate_state(self, statec: Statec):
        try:
            statec_paper = Paper.objects.get(id=statec.id)
            cloned_paper = Paper.objects.create()
            for widget in statec_paper.widgets.all():
                widget.clone(cloned_paper)
            for statec in statec_paper.states.all():
                add_paper_to_fsm_state(cloned_paper, statec)

            statec.flag = True
            statec.save()
            self.stdout.write(self.style.SUCCESS(
                f'Successful: {statec.id}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error migrating State {statec.id}: {e}'))
