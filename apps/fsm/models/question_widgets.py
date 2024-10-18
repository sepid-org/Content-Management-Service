from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.fsm.models.response import BigAnswer, MultiChoiceAnswer, SmallAnswer, UploadFileAnswer
from apps.fsm.models.base import Widget, clone_widget
from apps.fsm.models.fsm import State
from apps.fsm.models.team import Team

PROBLEM_ANSWER_MAPPING = {
    'SmallAnswerProblem': SmallAnswer,
    'BigAnswerProblem': BigAnswer,
    'MultiChoiceProblem': MultiChoiceAnswer,
    'UploadFileProblem': UploadFileAnswer,
}


class Problem(Widget):
    text = models.TextField()
    is_required = models.BooleanField(default=False)
    solution = models.TextField(null=True, blank=True)
    be_corrected = models.BooleanField(default=False)
    correctness_threshold = models.IntegerField(default=100)

    @property
    def correct_answer(self):
        return self.answers.filter(is_correct=True).first()

    def unfinalize_older_answers(self, user):
        if isinstance(self.paper, State):
            teammates = Team.objects.get_teammates_from_widget(
                user=user, widget=self)
            older_answers = PROBLEM_ANSWER_MAPPING[self.widget_type].objects.filter(problem=self, is_final_answer=True,
                                                                                    submitted_by__in=teammates)
            for a in older_answers:
                a.is_final_answer = False
                a.save()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class SmallAnswerProblem(Problem):
    def clone(self, paper):
        return clone_widget(self, paper)


class BigAnswerProblem(Problem):
    def clone(self, paper):
        return clone_widget(self, paper)


class UploadFileProblem(Problem):
    def clone(self, paper):
        return clone_widget(self, paper)


class MultiChoiceProblem(Problem):
    min_selections = models.IntegerField(
        validators=[MinValueValidator(0)], default=1)
    max_selections = models.IntegerField(
        validators=[MinValueValidator(0)], default=1)
    lock_after_answer = models.BooleanField(default=False)

    def clone(self, paper):
        cloned_widget = clone_widget(self, paper)
        cloned_choices = [choice.clone(cloned_widget)
                          for choice in self.choices.all()]
        cloned_widget.save()

    @property
    def correct_answer(self):
        from apps.responses.serializers.answers.answer_serializers import MultiChoiceAnswerSerializer
        correct_answer_object = self.answers.filter(is_correct=True).first()
        correct_choices = self.choices.all().filter(is_correct=True)

        if not correct_answer_object:
            correct_answer_serializer = MultiChoiceAnswerSerializer(
                data={
                    'answer_type': 'MultiChoiceAnswer',
                    'problem': self,
                    'is_correct': True,
                }
            )
            correct_answer_serializer.is_valid(raise_exception=True)
            correct_answer_object = correct_answer_serializer.save()

        correct_answer_object.choices.set(correct_choices)
        correct_answer_object.save()
        return correct_answer_object


class Choice(models.Model):
    problem = models.ForeignKey(MultiChoiceProblem, on_delete=models.CASCADE,
                                related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

    def clone(self, problem):
        cloned_choice = Choice(
            problem=problem,
            text=self.text,
            is_correct=self.is_correct
        )
        cloned_choice.save()
        return cloned_choice

    @classmethod
    def create_instance(self, question: MultiChoiceProblem, choice_data) -> 'Choice':
        return Choice.objects.create(**{
            'problem': question,
            'text': choice_data.get('text'),
            'is_correct': True if choice_data.get('is_correct') else False
        })
