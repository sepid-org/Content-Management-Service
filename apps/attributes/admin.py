from django.contrib import admin

from apps.attributes.models import IntrinsicAttribute, PerformableAction, Transition, Condition, Reward
from apps.attributes.models.performable_actions import Submission

################ INTRINSIC ATTRIBUTES ################


@admin.register(IntrinsicAttribute)
class IntrinsicAttributeCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'value']


@admin.register(Condition)
class ConditionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'value']


@admin.register(Reward)
class RewardCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'value']


################ PERFORMABLE ACTIONS ################


@admin.register(PerformableAction)
class PerformableActionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']


@admin.register(Transition)
class TransitionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'destination_state_id']


@admin.register(Submission)
class SubmissionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
