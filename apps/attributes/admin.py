from django.contrib import admin

from apps.attributes.models import IntrinsicAttribute, PerformableAction, Transition, Condition

################ INTRINSIC ATTRIBUTES ################


@admin.register(IntrinsicAttribute)
class IntrinsicAttributeCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'value']


@admin.register(Condition)
class ConditionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'value']


################ PERFORMABLE ACTIONS ################


@admin.register(PerformableAction)
class PerformableActionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']


@admin.register(Transition)
class TransitionCustomAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'destination_state_id']
