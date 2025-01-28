from django.core.management.base import BaseCommand
from django.utils.timezone import timedelta

from apps.fsm.models.fsm import Player


class Command(BaseCommand):
    help = "Remove duplicate players created within a short time interval for specific FSM IDs."

    def handle(self, *args, **kwargs):
        # لیست آیدی‌های FSM که بررسی می‌شوند
        fsm_ids = [197, 198, 199, 200, 202, 204,
                   208, 205, 212, 206, 207, 209, 210, 211]

        # فاصله زمانی مجاز بین ایجاد پلیرها (مثلاً 5 ثانیه)
        time_threshold = timedelta(seconds=5)

        # پیدا کردن پلیرهای مربوط به FSMهای مشخص‌شده
        players = Player.objects.filter(fsm_id__in=fsm_ids).order_by(
            'user_id', 'fsm_id', 'started_at')

        deletions = 0

        # بررسی پلیرها برای پیدا کردن موارد تکراری
        for i in range(len(players) - 1):
            current_player = players[i]
            next_player = players[i + 1]

            # اگر دو پلیر برای یک کاربر و FSM بودند و فاصله زمانی کمتر از آستانه بود
            if (
                current_player.user_id == next_player.user_id and
                current_player.fsm_id == next_player.fsm_id and
                (next_player.started_at - current_player.started_at) <= time_threshold
            ):
                current_player.delete()
                deletions += 1

        self.stdout.write(self.style.SUCCESS(
            f'{deletions} duplicate players were successfully deleted.'))
