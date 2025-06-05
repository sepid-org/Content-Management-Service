# your_app/management/commands/add_website_super_admin.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.fsm.models.fsm import FSM
from apps.fsm.models.program import Program


User = get_user_model()


class Command(BaseCommand):
    help = (
        "Usage:\n"
        "  python manage.py add_website_super_admin <username> <website>\n\n"
        "Finds the User with the given <username> and:\n"
        "  1) Adds them as an admin to every Program with website=<website>.\n"
        "  2) Adds them as a mentor (role='manager') to every FSM whose Program has website=<website>."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            type=str,
            help="The username of the User to add as admin/mentor."
        )
        parser.add_argument(
            "website",
            type=str,
            help="The website string to filter Program objects (e.g. 'kamva')."
        )

    def handle(self, *args, **options):
        username = options["username"]
        website = options["website"]

        # 1) Lookup the User
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                f"User with username='{username}' does not exist."
            ))
            return

        # 2) Add as admin on all Program where website=<website>
        website_programs = Program.objects.filter(website=website)
        if not website_programs.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"No Program instances found with website='{website}'.")
            )
        else:
            for prog in website_programs:
                prog.admins.add(user)  # M2M .add() is idempotent
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added '{username}' as admin to Program(id={prog.id}, name='{prog.name}')."
                    )
                )

        # 3) Add as mentor on all FSM whose Program has website=<website>
        website_fsms = FSM.objects.filter(program__website=website)
        if not website_fsms.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"No FSM instances found whose Program has website='{website}'.")
            )
        else:
            for fsm in website_fsms:
                added = fsm.add_mentor(user_id=user.id, role="manager")
                if added:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Added '{username}' as mentor to FSM(id={fsm.id}, name='{fsm.name}')."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"'{username}' was already a mentor on FSM(id={fsm.id}, name='{fsm.name}')."
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Operation complete."))
