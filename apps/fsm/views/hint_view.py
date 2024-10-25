from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.fsm.models import Hint
from apps.fsm.models.base import Paper
from apps.fsm.permissions import IsHintModifier
from apps.fsm.serializers.papers.hint_serializer import HintSerializer


class HintViewSet(viewsets.ModelViewSet):
    serializer_class = HintSerializer
    queryset = Hint.objects.all()
    my_tags = ['hint']

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsHintModifier]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        request.data['paper_type'] = Paper.PaperType.Hint
        request.data['creator'] = request.user.id
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='by-fsm-state')
    def by_fsm_state(self, request):
        fsm_state_id = request.query_params.get('fsm_state_id')

        if not fsm_state_id:
            return Response(
                {"error": "fsm_state_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        hints = self.queryset.filter(reference=fsm_state_id)
        serializer = self.get_serializer(hints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
