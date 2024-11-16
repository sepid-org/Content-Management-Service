import json
from typing import Dict, Union
from django.db import models
from polymorphic.models import PolymorphicModel

from apps.attributes.models.utils import get_allocated_rewards, get_net_rewards
from apps.fsm.models.form import AnswerSheet


class Answer(PolymorphicModel):
    class AnswerTypes(models.TextChoices):
        SmallAnswer = 'SmallAnswer'
        BigAnswer = 'BigAnswer'
        MultiChoiceAnswer = 'MultiChoiceAnswer'
        UploadFileAnswer = 'UploadFileAnswer'

    answer_type = models.CharField(max_length=20, choices=AnswerTypes.choices)
    answer_sheet = models.ForeignKey(AnswerSheet, related_name='answers', null=True, blank=True,
                                     on_delete=models.PROTECT)
    submitted_by = models.ForeignKey(
        'accounts.User', related_name='submitted_answers', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_final_answer = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)

    def get_allocated_rewards(self):
        assess_result_score = self.assess()['score']
        net_rewards = get_net_rewards(self.problem)
        return get_allocated_rewards(net_rewards=net_rewards, allocation_percentage=assess_result_score)

    def assess(self) -> Dict[str, Union[int, str]]:
        raise NotImplementedError("Subclasses should implement this method.")

    def __str__(self):
        return f'user: {self.submitted_by.username if self.submitted_by else "-"}'

    @property
    def string_answer(self):
        pass

    @property
    def problem(self):
        return self.problem


class SmallAnswer(Answer):
    problem = models.ForeignKey('fsm.SmallAnswerProblem', null=True,
                                blank=True, on_delete=models.PROTECT, related_name='answers')
    text = models.TextField()

    def assess(self) -> Dict[str, Union[int, str]]:
        result = 100
        if self.problem.correct_answer:
            if self.text.strip() != self.problem.correct_answer.text.strip():
                return 0
        return {
            'score': result,
            'feedback': 'empty',
        }

    @property
    def string_answer(self):
        return self.text

    def __str__(self):
        return self.text


class BigAnswer(Answer):
    problem = models.ForeignKey('fsm.BigAnswerProblem', null=True, blank=True, on_delete=models.PROTECT,
                                related_name='answers')
    text = models.TextField()

    @property
    def string_answer(self):
        return self.text


class MultiChoiceAnswer(Answer):
    problem = models.ForeignKey(
        'fsm.MultiChoiceProblem', on_delete=models.PROTECT, related_name='answers')
    choices = models.ManyToManyField('fsm.Choice')

    @property
    def string_answer(self):
        return json.dumps([choice.id for choice in self.choices.all()])

    def assess(self) -> Dict[str, Union[int, str]]:
        result: int = 100
        for choice in self.choices.all():
            if not choice.is_correct:
                result = 0
        return {
            'score': result,
            'feedback': 'empty',
        }


class UploadFileAnswer(Answer):
    problem = models.ForeignKey('fsm.UploadFileProblem', null=True, blank=True, on_delete=models.PROTECT,
                                related_name='answers')
    answer_file = models.URLField(max_length=2000, blank=True)

    @property
    def string_answer(self):
        return self.answer_file
