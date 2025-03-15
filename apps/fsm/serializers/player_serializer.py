from rest_framework import serializers

from apps.fsm.models import Player


class PlayerMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ['id', 'current_state', 'started_at', 'finished_at']


class PlayerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        context = self.context
        request = context.get('request')
        fsm = validated_data.get('fsm')
        player = super().create(validated_data)
        website = request.headers.get("Website")

        # perform fsm start actions
        from apps.attributes.models import Start
        start_attributes = fsm.attributes.instance_of(Start)
        for start_attribute in start_attributes:
            start_attribute.perform(
                user=request.user,
                player=player,
                website=website,
            )

        return player

    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['id']
