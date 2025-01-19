from django.core.management.base import BaseCommand

from apps.fsm.models.form import AnswerSheet


class Command(BaseCommand):
    help = 'Remove duplicate AnswerSheets for a given form_id, keeping only the first one'

    def add_arguments(self, parser):
        parser.add_argument('--formid', type=int, help='Form ID to process')

    def handle(self, *args, **options):
        form_id = options['formid']
        if not form_id:
            self.stdout.write(self.style.ERROR(
                'Please provide a form ID using --formid'))
            return

        answer_sheets = AnswerSheet.objects.filter(
            form_id=form_id).order_by('user_id', 'created_at')
        users_processed = set()
        deleted_count = 0

        for answer_sheet in answer_sheets:
            if answer_sheet.user_id in users_processed:
                answer_sheet.delete()
                deleted_count += 1
            else:
                users_processed.add(answer_sheet.user_id)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully deleted {deleted_count} duplicate AnswerSheets for form ID {form_id}'))
