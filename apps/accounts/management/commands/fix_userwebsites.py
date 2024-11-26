from django.core.management.base import BaseCommand
from apps.accounts.models import UserWebsite
from django.db import transaction
import uuid


def is_username_uuid(username):
    try:
        # Try to create a UUID from the username
        uuid_obj = uuid.UUID(username)
        # If successful, check that it matches the original (to ensure valid format)
        return str(uuid_obj) == username
    except ValueError:
        # If an error occurs, it's not a valid UUID
        return False


class Command(BaseCommand):

    def handle(self, *args, **options):

        user_websites = UserWebsite.objects.exclude(website='filmbazi')

        @transaction.atomic
        def do():
            for user_website in user_websites:
                user = user_website.user
                if is_username_uuid(user.username):
                    if UserWebsite.objects.filter(user=user, website='filmbazi').exists():
                        user_website.delete()
                    else:
                        user_website.website = 'filmbazi'
                        user_website.save()

        do()
