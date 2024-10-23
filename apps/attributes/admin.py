from django.contrib import admin

from apps.attributes.models.intrinsic_attributes import Enabled, Condition, Cost, Reward
from apps.attributes.models.performable_actions import Buy, Submission, Transition

################ INTRINSIC ATTRIBUTES ################


@admin.register(Enabled)
class EnabledCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'value']


@admin.register(Condition)
class ConditionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'value']


@admin.register(Cost)
class CostCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'value']


@admin.register(Reward)
class RewardCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'value']


################ PERFORMABLE ACTIONS ################


@admin.register(Transition)
class TransitionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'destination_state_id']


@admin.register(Buy)
class BuyCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']


@admin.register(Submission)
class SubmissionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
