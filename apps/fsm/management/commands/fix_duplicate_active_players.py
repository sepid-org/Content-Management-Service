from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db import models

from apps.fsm.models.fsm import Player


class Command(BaseCommand):
    help = 'Deactivate duplicate active player records and keep the most recent one active.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning duplicate active players...")

        # پیدا کردن کاربرانی که بیش از یک رکورد فعال دارند
        duplicates = (
            Player.objects
            .filter(finished_at__isnull=True)  # فقط رکوردهای فعال بررسی شوند
            .values('user', 'fsm')
            .annotate(active_count=models.Count('id'))
            .filter(active_count__gt=1)
        )

        for duplicate in duplicates:
            user_id = duplicate['user']
            fsm_id = duplicate['fsm']

            # دریافت فقط رکوردهای فعال (finished_at = NULL) و مرتب‌سازی بر اساس جدیدترین زمان ایجاد
            active_players = Player.objects.filter(
                user_id=user_id, fsm_id=fsm_id, finished_at__isnull=True).order_by('-started_at')

            # نگه داشتن جدیدترین رکورد و غیرفعال‌سازی بقیه
            latest_player = active_players.first()
            old_active_players = active_players.exclude(id=latest_player.id)

            old_active_players.update(is_active=False, finished_at=now())

            self.stdout.write(
                f'Updated {old_active_players.count()} duplicate active records for user {user_id} in FSM {fsm_id}')

        self.stdout.write(self.style.SUCCESS(
            'Successfully cleaned duplicate active players!'))
