from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.fsm.models import Hint
from apps.fsm.permissions import IsHintModifier
from apps.fsm.serializers.papers.hint_serializer import HintSerializer


class HintViewSet(viewsets.ModelViewSet):
    serializer_class = HintSerializer
    queryset = Hint.objects.all()
    my_tags = ['state']

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update(
            {'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    def get_permissions(self):
        if self.action == 'create' or self.action == 'retrieve' or self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsHintModifier]
        return [permission() for permission in permission_classes]
