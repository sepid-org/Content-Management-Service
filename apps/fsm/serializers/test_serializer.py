from rest_framework import serializers
from apps.fsm.models.test import Test, Participation, Entrance, RandomWidget, PlayerTest

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'name', 'description', 'cover_picture', 'start_time', 'end_time', 'time_limit', 'participation_limit', 'grading_method', 'content']

class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = ['id', 'test', 'answer_sheet', 'start_time', 'end_time', 'score']

class EntranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrance
        fields = ['id', 'participation', 'entry_time', 'device']

class RandomWidgetSerializer(serializers.ModelSerializer):
    new_question = serializers.SerializerMethodField()

    class Meta:
        model = RandomWidget
        fields = ['id', 'paper', 'player', 'new_question']

    def get_new_question(self, obj):
        return obj.get_new_question()

# Player Serializer
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerTest
        fields = ['id', 'name', 'history']
