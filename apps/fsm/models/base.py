from django.db import models
from polymorphic.models import PolymorphicModel
from abc import abstractmethod

from apps.attributes.models import Attribute, IntrinsicAttribute, PerformableAction


class Object(PolymorphicModel):
    title = models.CharField(max_length=200)
    name = models.CharField(max_length=200, null=True)
    creator = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attributes = models.ManyToManyField(to=Attribute, null=True, blank=True)
    is_private = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    website = models.CharField(blank=True, null=True, max_length=50)


class Position(models.Model):
    object = models.OneToOneField(
        Object, on_delete=models.CASCADE, related_name='position')
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    def __str__(self):
        return f"{self.id} at ({self.x}, {self.y})"


def generate_properties(properties):
    def decorator(cls):
        for prop in properties:
            setattr(cls, prop, property(lambda self,
                    p=prop: getattr(self.object, p, None)))
        return cls
    return decorator


@generate_properties(['created_at', 'updated_at', 'title', 'name', 'order', 'is_private', 'position', 'is_hidden'])
class ObjectMixin:
    @property
    def object(self):
        if not hasattr(self, '_object') or self._object is None:
            self._object = Object.objects.create(
                title=f'{self.__class__.__name__}-{self.id}'
            )
            self.save()
        return self._object

    @property
    def attributes(self):
        return self.object.attributes.all()

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


class Paper(PolymorphicModel, ObjectMixin):
    _object = models.OneToOneField(
        Object, on_delete=models.CASCADE, null=True, related_name='paper')

    class PaperType(models.TextChoices):
        RegistrationForm = 'RegistrationForm'
        State = 'State'
        Hint = 'Hint'
        WidgetHint = 'WidgetHint'
        Article = 'Article'
        General = 'General'

    paper_type = models.CharField(
        max_length=25, choices=PaperType.choices, default=PaperType.General)
    creator = models.ForeignKey('accounts.User', related_name='papers', null=True, blank=True,
                                on_delete=models.SET_NULL)

    def delete(self):
        for w in Widget.objects.filter(paper=self):
            try:
                w.delete()
            except:
                w.paper = None
                w.save()
        return super(Paper, self).delete()

    def __str__(self):
        return f"{self.id}: {self.paper_type}"


class Widget(PolymorphicModel, ObjectMixin):
    _object = models.OneToOneField(
        Object, on_delete=models.CASCADE, null=True, related_name='widget')

    class WidgetTypes(models.TextChoices):
        Iframe = 'Iframe'
        Video = 'Video'
        Image = 'Image'
        Aparat = 'Aparat'
        Audio = 'Audio'
        TextWidget = 'TextWidget'
        Placeholder = 'Placeholder'
        DetailBoxWidget = 'DetailBoxWidget'
        SmallAnswerProblem = 'SmallAnswerProblem'
        BigAnswerProblem = 'BigAnswerProblem'
        MultiChoiceProblem = 'MultiChoiceProblem'
        UploadFileProblem = 'UploadFileProblem'
        ButtonWidget = 'ButtonWidget'
        CustomWidget = 'CustomWidget'

    paper = models.ForeignKey(
        Paper, null=True, blank=True, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=30, choices=WidgetTypes.choices)
    creator = models.ForeignKey('accounts.User', related_name='widgets', null=True, blank=True,
                                on_delete=models.SET_NULL)

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


class Hint(Paper):
    referencec = models.ForeignKey(
        'fsm.Statec', on_delete=models.CASCADE, related_name='hints')
    reference = models.ForeignKey(
        'fsm.State', on_delete=models.SET_NULL, related_name='hints', null=True)

    def clone(self, paper):
        return clone_hint(self, paper)


class WidgetHint(Paper):
    reference = models.ForeignKey(
        Widget, on_delete=models.CASCADE, related_name='hints')

    def clone(self, paper):
        return clone_hint(self, paper)


################### HELPER METHODS ###################


def clone_hint(hint, reference_paper):
    cloned_hint = clone_paper(hint, reference=reference_paper)
    cloned_widgets = [widget.clone(cloned_hint)
                      for widget in hint.widgets.all()]
    return cloned_hint


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
