from django.core.management import BaseCommand

from apps.accounts.models import User
from proxies.Shad import get_user_data_from_shad, update_user_info_by_shad_data


class Command(BaseCommand):

    def handle(self, *args, **options):
        for user in User.objects.filter(origin='SHAD', is_temporary=True):
            try:
                user_data = get_user_data_from_shad(
                    user_uuid=user.username,
                    landing_id=284,
                )
                update_user_info_by_shad_data(user, user_data)
                user.is_temporary = False
                user.save()
            except:
                pass

        self.stdout.write(self.style.SUCCESS('update all shad users'))
