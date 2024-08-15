from django.contrib import admin

from apps.attributes.models import IntrinsicAttribute, PerformableAction


@admin.register(IntrinsicAttribute)
class IntrinsicAttributeCustomAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'type', 'value']


@admin.register(PerformableAction)
class PerformableActionCustomAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'type']
