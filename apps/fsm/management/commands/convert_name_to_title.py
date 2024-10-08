from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fsm.models.base import Paper
from apps.fsm.models.fsm import State


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Get all State records
        states = State.objects.all()
        for state in states:
            self.migrate_state(state)

    @transaction.atomic
    def migrate_state(self, state: State):
        try:
            state.title = state.name
            state.save()

            self.stdout.write(self.style.SUCCESS(
                f'Successfully migrated State {state.id}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error migrating State {state.id}: {e}'))
