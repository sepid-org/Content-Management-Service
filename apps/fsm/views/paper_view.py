from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.fsm.models import Paper
from apps.fsm.serializers.paper_serializers import PaperSerializer


class PaperViewSet(viewsets.ModelViewSet):
    serializer_class = PaperSerializer
    queryset = Paper.objects.all()
    my_tags = ['paper']

    def get_permissions(self):
        if self.action == 'create' or self.action == 'retrieve' or self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
