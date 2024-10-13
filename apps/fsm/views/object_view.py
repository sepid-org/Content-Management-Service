from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.fsm.models import Object, Position, Paper, Widget
from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.fsm.serializers.position_serializer import PositionSerializer


class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer

    @action(detail=False, methods=['get'], url_path='by-paper/(?P<paper_id>\d+)')
    def by_paper(self, request, paper_id=None):
        paper = get_object_or_404(Paper, id=paper_id)
        positions = self.get_queryset().filter(widget__paper=paper).distinct()
        serializer = self.get_serializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='update-positions')
    @transaction.atomic
    def update_positions(self, request):
        positions_data = request.data.get('positions', [])
        self._update_positions(positions_data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update_positions(self, positions_data):
        for position_data in positions_data:
            widget_id = position_data.get('widget')
            widget = get_object_or_404(Widget, id=widget_id)
            self._update_or_create_position(widget, position_data)

    def _update_or_create_position(self, widget, position_data):
        Position.objects.update_or_create(
            object=widget.object,
            defaults={
                'x': position_data['x'],
                'y': position_data['y'],
                'width': position_data['width'],
                'height': position_data['height']
            }
        )
