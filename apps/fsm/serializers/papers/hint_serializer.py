from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import Hint


class HintSerializer(PaperSerializer):

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('user', None)
        return super(HintSerializer, self).create({'paper_type': 'Hint', 'creator': user, **validated_data})

    class Meta(PaperSerializer.Meta):
        model = Hint
        ref_name = 'hint'
        fields = PaperSerializer.Meta.get_fields() + ['reference']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
