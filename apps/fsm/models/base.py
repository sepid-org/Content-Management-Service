from django.db import models
from polymorphic.models import PolymorphicModel
from abc import abstractmethod
from apps.accounts.models import User

from apps.attributes.models import Attribute, IntrinsicAttribute, PerformableAction


def clone_paper(paper, *args, **kwargs):
    paper_type = paper.__class__
    model_fields = [
        field.name for field in paper_type._meta.get_fields() if field.name != 'id']
    dicted_model = {name: value for name, value
                    in paper.__dict__.items() if name in model_fields}
    cloned_paper = paper_type(
        **{**dicted_model,
           **kwargs,
           },
    )
    cloned_paper.save()
    return cloned_paper


class Paper(PolymorphicModel):
    class PaperType(models.TextChoices):
        RegistrationForm = 'RegistrationForm'
        State = 'State'
        Hint = 'Hint'
        WidgetHint = 'WidgetHint'
        Article = 'Article'
        General = 'General'

    paper_type = models.CharField(
        max_length=25, blank=False, choices=PaperType.choices)
    creator = models.ForeignKey('accounts.User', related_name='papers', null=True, blank=True,
                                on_delete=models.SET_NULL)
    since = models.DateTimeField(null=True, blank=True)
    till = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True, default=None)
    is_exam = models.BooleanField(default=False)

    def delete(self):
        for w in Widget.objects.filter(paper=self):
            try:
                w.delete()
            except:
                w.paper = None
                w.save()
        return super(Paper, self).delete()

    def is_user_permitted(self, user: User):
        # if self.criteria:
        #     return self.criteria.evaluate(user)
        return True

    def __str__(self):
        return f"{self.paper_type}"


class Hint(Paper):
    reference = models.ForeignKey(
        'fsm.State', on_delete=models.CASCADE, related_name='hints')

    def clone(self, paper):
        return clone_hint(self, paper)


def clone_hint(hint, reference_paper):
    cloned_hint = clone_paper(hint, reference=reference_paper)
    cloned_widgets = [widget.clone(cloned_hint)
                      for widget in hint.widgets.all()]
    return cloned_hint


class Content:

    @property
    def solve_cost(self):
        return self._get_performable_action_intrinsic_attribute_template_method('solve', 'reward')

    @property
    def submission_cost(self):
        return self._get_performable_action_intrinsic_attribute_template_method('submit', 'cost')

    @property
    def submission_cost(self):
        return self._get_performable_action_intrinsic_attribute_template_method('submit', 'cost')

    @property
    def has_transition_lock(self):
        return bool(self.transition_lock)

    @property
    def transition_lock(self):
        return self._get_performable_action_intrinsic_attribute_template_method('transit', 'password')

    @property
    def has_entrance_lock(self):
        return bool(self.entrance_lock)

    @property
    def entrance_lock(self):
        return self._get_performable_action_intrinsic_attribute_template_method('enter', 'password')

    def _get_performable_action_intrinsic_attribute_template_method(self, performable_action_type, intrinsic_attribute_type):
        for performable_action in self._get_performable_actions():
            if performable_action.type == performable_action_type:
                for intrinsic_attribute in performable_action.attributes.all():
                    if intrinsic_attribute.type == intrinsic_attribute_type:
                        return intrinsic_attribute.value
        return None

    def _get_intrinsic_attributes(self) -> list[IntrinsicAttribute]:
        result = []
        for attribute in self.attributes.all():
            if isinstance(attribute, IntrinsicAttribute):
                result.append(attribute)
        return result

    def _get_performable_actions(self) -> list[PerformableAction]:
        result = []
        for attribute in self.attributes.all():
            if isinstance(attribute, PerformableAction):
                result.append(attribute)
        return result


class Widget(PolymorphicModel, Content):
    class WidgetTypes(models.TextChoices):
        Iframe = 'Iframe'
        Video = 'Video'
        Image = 'Image'
        Aparat = 'Aparat'
        Audio = 'Audio'
        TextWidget = 'TextWidget'
        DetailBoxWidget = 'DetailBoxWidget'
        SmallAnswerProblem = 'SmallAnswerProblem'
        BigAnswerProblem = 'BigAnswerProblem'
        MultiChoiceProblem = 'MultiChoiceProblem'
        UploadFileProblem = 'UploadFileProblem'

    attributes = models.ManyToManyField(to=Attribute, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to='events/')
    paper = models.ForeignKey(
        Paper, null=True, blank=True, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=30, choices=WidgetTypes.choices)
    creator = models.ForeignKey('accounts.User', related_name='widgets', null=True, blank=True,
                                on_delete=models.SET_NULL)
    is_hidden = models.BooleanField(default=False)

    @abstractmethod
    def clone(self, paper):
        pass

    def make_file_empty(self):
        try:
            self.file.delete()
        except:
            self.file = None
            self.file.save()
            pass


def clone_widget(widget, paper, *args, **kwargs):
    widget_type = widget.__class__
    model_fields = [
        field.name for field in widget_type._meta.get_fields() if field.name != 'id']
    dicted_model = {name: value for name,
                    value in widget.__dict__.items() if name in model_fields}
    cloned_widget = widget_type(
        **{**dicted_model,
           'paper': paper,
           **kwargs,
           },
    )
    cloned_widget.save()

    cloned_widget_hints = [widget_hint.clone(
        cloned_widget) for widget_hint in widget.hints.all()]

    return cloned_widget


def clone_hint(hint, reference_paper):
    cloned_hint = clone_paper(hint, reference=reference_paper)
    cloned_widgets = [widget.clone(cloned_hint)
                      for widget in hint.widgets.all()]
    return cloned_hint


class WidgetHint(Paper):
    reference = models.ForeignKey(
        Widget, on_delete=models.CASCADE, related_name='hints')

    def clone(self, paper):
        return clone_hint(self, paper)


class WidgetPosition(models.Model):
    widget = models.OneToOneField(
        'Widget', on_delete=models.CASCADE, primary_key=True)
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    def __str__(self):
        return f"{self.widget} at ({self.x}, {self.y})"
