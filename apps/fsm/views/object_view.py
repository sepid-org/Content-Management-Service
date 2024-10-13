from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.fsm.models import Object, Position
from apps.fsm.serializers.object_serializer import ObjectSerializer


class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer

    @action(detail=False, methods=['post'], url_path='update-positions')
    @transaction.atomic
    def update_positions(self, request):
        positions_data = request.data.get('positions', [])
        self._update_positions(positions_data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update_positions(self, positions_data):
        for position_data in positions_data:
            position_id = position_data.get('id')
            self._update_position_by_id(position_id, position_data)

    def _update_position_by_id(self, position_id, position_data):
        """
        Updates a Position based on its ID. If the Position with the given ID
        does not exist, it raises a 404 error.
        """
        position = get_object_or_404(Position, id=position_id)
        position.x = position_data['x']
        position.y = position_data['y']
        position.width = position_data['width']
        position.height = position_data['height']
        position.save()
