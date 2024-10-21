from django.contrib import admin

from apps.attributes.models import IntrinsicAttribute, PerformableAction, Transition, Condition


@admin.register(IntrinsicAttribute)
class IntrinsicAttributeCustomAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'value']


@admin.register(Condition)
class ConditionCustomAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'value']


#########################

@admin.register(PerformableAction)
class PerformableActionCustomAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


@admin.register(Transition)
class TransitionCustomAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'destination_state_id']
