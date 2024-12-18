from django.contrib import admin

from apps.attributes.models.intrinsic_attributes import Default, Enabled, Condition, Cost, Reward
from apps.attributes.models.performable_actions import Answer, Buy, Finish, Rewarding, Start, Submission, Transition


class AttributeCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_related_attributes']
    search_fields = ['title',]
    filter_horizontal = ['attributes',]


class IntrinsicAttributeCustomAdmin(AttributeCustomAdmin):
    list_display = AttributeCustomAdmin.list_display + ['value']


class PerformableActionCustomAdmin(AttributeCustomAdmin):
    list_display = AttributeCustomAdmin.list_display + []


################ INTRINSIC ATTRIBUTES ################


@admin.register(Enabled)
class EnabledCustomAdmin(IntrinsicAttributeCustomAdmin):
    list_display = IntrinsicAttributeCustomAdmin.list_display + []


@admin.register(Default)
class DefaultCustomAdmin(IntrinsicAttributeCustomAdmin):
    list_display = IntrinsicAttributeCustomAdmin.list_display + []


@admin.register(Condition)
class ConditionCustomAdmin(IntrinsicAttributeCustomAdmin):
    list_display = IntrinsicAttributeCustomAdmin.list_display + []


@admin.register(Cost)
class CostCustomAdmin(IntrinsicAttributeCustomAdmin):
    list_display = IntrinsicAttributeCustomAdmin.list_display + []


@admin.register(Reward)
class RewardCustomAdmin(IntrinsicAttributeCustomAdmin):
    list_display = IntrinsicAttributeCustomAdmin.list_display + []


################ PERFORMABLE ACTIONS ################


@admin.register(Submission)
class SubmissionCustomAdmin(PerformableActionCustomAdmin):
    list_display = PerformableActionCustomAdmin.list_display + []


@admin.register(Start)
class StartCustomAdmin(PerformableActionCustomAdmin):
    list_display = PerformableActionCustomAdmin.list_display + []


@admin.register(Finish)
class FinishCustomAdmin(PerformableActionCustomAdmin):
    list_display = PerformableActionCustomAdmin.list_display + []


@admin.register(Rewarding)
class RewardingCustomAdmin(PerformableActionCustomAdmin):
    list_display = PerformableActionCustomAdmin.list_display + []


@admin.register(Transition)
class TransitionCustomAdmin(PerformableActionCustomAdmin):
    list_display = PerformableActionCustomAdmin.list_display + \
        ['destination_state_id']


@admin.register(Buy)
class BuyCustomAdmin(PerformableActionCustomAdmin):
    list_display = PerformableActionCustomAdmin.list_display + []


@admin.register(Answer)
class AnswerCustomAdmin(PerformableActionCustomAdmin):
    list_display = PerformableActionCustomAdmin.list_display + \
        ['question_id', 'answer_type', 'provided_answer']
