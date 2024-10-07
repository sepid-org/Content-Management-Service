from django.db import transaction
from rest_framework import serializers

from apps.widgets.serializers.widget_polymorphic_serializer import WidgetPolymorphicSerializer
from apps.fsm.models import Paper


class PaperMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Paper
        fields = ['id', 'paper_type']


class PaperSerializer(serializers.ModelSerializer):
    widgets = WidgetPolymorphicSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        widgets = validated_data.pop('widgets', [])
        user = self.context.get('user', None)
        instance = super().create({'creator': user, **validated_data})
        for widget in widgets:
            widget['creator'] = user
            serializer = WidgetPolymorphicSerializer(
                data=widget, context=self.context)
            if serializer.is_valid(raise_exception=True):
                serializer.validated_data['paper'] = instance
                serializer.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('widgets'):
            representation['widgets'] = sorted(
                representation['widgets'], key=lambda x: x['id'])
        return representation

    class Meta:
        model = Paper
        fields = ['id', 'widgets', 'template', 'paper_type']
        read_only_fields = ['id', 'paper_type']

        def get_fields():
            return [field for field in PaperSerializer.Meta.fields if field != 'widgets']


class ChangeWidgetOrderSerializer(serializers.Serializer):
    order = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=True)
