from rest_framework import serializers

from apps.fsm.models import Player


class PlayerMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ['id', 'current_state']
        read_only_fields = ['id', 'current_state']


class PlayerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        context = self.context
        request = context.get('request')
        fsm = validated_data.get('fsm')

        # perform fsm start actions
        from apps.attributes.models import Start
        start_attributes = fsm.attributes.instance_of(Start)
        for start_attribute in start_attributes:
            start_attribute.perform(
                request=request,
                user=request.user,
            )

        return super().create(validated_data)

    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['id']
