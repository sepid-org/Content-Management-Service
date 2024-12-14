from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.fsm.models import (
    Answer, AnswerSheet,
    SmallAnswer, BigAnswer,
    MultiChoiceAnswer, UploadFileAnswer
)

# Mapping of problem types to their corresponding answer models
ANSWER_MODELS = [
    SmallAnswer,
    BigAnswer,
    MultiChoiceAnswer,
    UploadFileAnswer
]


class Command(BaseCommand):
    help = 'Set the user of answers to match their answer sheet\'s user if the answer sheet has a user'

    def handle(self, *args, **options):
        # Track the number of updated answers
        total_updated = 0

        # Iterate through all answer models
        for answer_model in ANSWER_MODELS:
            # Find answers with an answer sheet but without a submitted_by user
            answers_to_update = answer_model.objects.filter(
                answer_sheet__isnull=False,
                submitted_by__isnull=True,
                answer_sheet__user__isnull=False
            )

            # Update the submitted_by user for each answer
            for answer in answers_to_update:
                answer.submitted_by = answer.answer_sheet.user
                answer.save()
                total_updated += 1

                self.stdout.write(self.style.SUCCESS(
                    f'Updated {answer_model.__name__} {answer.id} '
                    f'with user {answer.submitted_by.username}'
                ))

        # Final summary
        self.stdout.write(self.style.SUCCESS(
            f'Finished updating answers. Total answers updated: {total_updated}'
        ))
