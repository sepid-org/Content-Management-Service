from django.core.management.base import BaseCommand
from apps.accounts.models import UserWebsite
from django.db import transaction
import uuid


def is_valid_uuid(value):
    try:
        uuid_obj = uuid.UUID(value)
        return str(uuid_obj).upper() == value.upper()
    except ValueError:
        return False


class Command(BaseCommand):

    def handle(self, *args, **options):

        user_websites = UserWebsite.objects.exclude(website='filmbazi')

        @transaction.atomic
        def do():
            for user_website in user_websites:
                user = user_website.user
                if is_valid_uuid(user.username):
                    if UserWebsite.objects.filter(user=user, website='filmbazi').exists():
                        user_website.delete()
                    else:
                        user_website.website = 'filmbazi'
                        user_website.save()

        do()
