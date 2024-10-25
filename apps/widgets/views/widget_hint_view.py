from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.fsm.models import WidgetHint
from apps.fsm.models.base import Paper
from apps.widgets.serializers.widget_hint_serializer import WidgetHintSerializer


class WidgetHintViewSet(viewsets.ModelViewSet):
    serializer_class = WidgetHintSerializer
    queryset = WidgetHint.objects.all()
    my_tags = ['widget-hint']

    def create(self, request, *args, **kwargs):
        request.data['paper_type'] = Paper.PaperType.WidgetHint
        request.data['creator'] = request.user.id
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='by-widget')
    def by_widget(self, request):
        widget_id = request.query_params.get('widget_id')

        if not widget_id:
            return Response(
                {"error": "widget_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        hints = self.queryset.filter(reference=widget_id)
        serializer = self.get_serializer(hints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
