from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.fsm.models import WidgetPosition, Paper, Widget
from apps.fsm.serializers.widget_position import WidgetPositionSerializer, WidgetPositionListSerializer


class WidgetPositionViewSet(viewsets.ModelViewSet):
    queryset = WidgetPosition.objects.all()
    serializer_class = WidgetPositionSerializer

    @action(detail=False, methods=['get'], url_path='by-paper/(?P<paper_id>\d+)')
    def by_paper(self, request, paper_id=None):
        paper = get_object_or_404(Paper, id=paper_id)
        positions = self.queryset.filter(widget__paper=paper)
        serializer = self.get_serializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='save-positions')
    @transaction.atomic
    def save_positions(self, request):
        serializer = WidgetPositionListSerializer(data=request.data)
        if serializer.is_valid():
            positions = serializer.save()
            return Response(WidgetPositionSerializer(positions, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
