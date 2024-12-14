from django.core.management.base import BaseCommand
from django.db.models import Max
from apps.fsm.models import (
    SmallAnswer, BigAnswer, MultiChoiceAnswer,
    UploadFileAnswer, Problem
)

# Mapping of problem types to their corresponding answer models
PROBLEM_ANSWER_MAPPING = {
    'SmallAnswerProblem': SmallAnswer,
    'BigAnswerProblem': BigAnswer,
    'MultiChoiceProblem': MultiChoiceAnswer,
    'UploadFileProblem': UploadFileAnswer,
}


class Command(BaseCommand):
    help = 'Set the last answer for each user-problem combination as final if no final answer exists'

    def handle(self, *args, **options):
        # Iterate through all problem types
        for problem_type, answer_model in PROBLEM_ANSWER_MAPPING.items():
            # Find problems of this type
            problems = Problem.objects.filter(widget_type=problem_type)

            for problem in problems:
                # Find answers for this problem
                answers = answer_model.objects.filter(problem=problem)

                # Group answers by user
                user_answers = answers.values('submitted_by').annotate(
                    last_answer_id=Max('id')
                )

                for user_answer in user_answers:
                    user = user_answer['submitted_by']
                    last_answer_id = user_answer['last_answer_id']

                    if user is None:
                        continue

                    # Check if there's already a final answer for this user and problem
                    existing_final_answer = answer_model.objects.filter(
                        problem=problem,
                        submitted_by=user,
                        is_final_answer=True
                    ).exists()

                    # If no final answer exists, set the last answer as final
                    if not existing_final_answer:
                        last_answer = answer_model.objects.get(
                            id=last_answer_id)
                        last_answer.is_final_answer = True
                        last_answer.save()

                        self.stdout.write(self.style.SUCCESS(
                            f'Set final answer for user {user} on {problem_type} problem {problem.id}'
                        ))

        self.stdout.write(self.style.SUCCESS('Finished setting final answers'))
