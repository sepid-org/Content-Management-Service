from apps.fsm.models.form import Form
from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer


class FormSerializer(PaperSerializer):

    class Meta(PaperSerializer.Meta):
        model = Form
        ref_name = 'registration_form'
        fields = [field for field in PaperSerializer.Meta.fields if field != 'widgets'] +\
            ['audience_type', 'start_date', 'end_date', 'background_image']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []

    def to_representation(self, instance):
        # add object fields to representation
        representation = super().to_representation(instance)
        object_instance = instance.object
        representation = {
            **ObjectSerializer(object_instance, context=self.context).data,
            **representation,
        }

        return representation
