# In a new file, e.g., apps/fsm/management/commands/migrate_position_data.py

from django.core.management.base import BaseCommand
# Adjust the import path as needed
from apps.fsm.models import Position, Position2


class Command(BaseCommand):
    help = 'Migrates data from Position to Position2'

    def handle(self, *args, **options):
        self.stdout.write(
            'Starting data migration from Position to Position2...')

        # Migrate data
        positions_migrated = 0
        for position in Position.objects.all():
            position2 = Position2.objects.create(
                object=position.object,
                x=position.x,
                y=position.y,
                width=position.width,
                height=position.height
            )
            positions_migrated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully migrated {positions_migrated} positions'))

        # Optionally, you can add code here to delete the old Position model data
        # Be very careful with this step and ensure you have backups
        # Position.objects.all().delete()
        # self.stdout.write(self.style.SUCCESS('Deleted old Position data'))

        self.stdout.write(self.style.SUCCESS(
            'Data migration completed successfully'))
