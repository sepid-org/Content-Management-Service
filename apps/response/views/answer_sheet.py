from rest_framework import viewsets
from rest_framework import permissions

from apps.fsm.models.form import AnswerSheet
from apps.response.serializers.answer_sheet import AnswerSheetSerializer
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.db import transaction

from apps.fsm.models.fsm import Player


class AnswerSheetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = AnswerSheet.objects.all()
    serializer_class = AnswerSheetSerializer
    my_tags = ['answer-sheets']

    @transaction.atomic
    @action(detail=False, methods=['get'], url_path='by-player')
    def by_paper(self, request, *args, **kwargs):
        player_id = request.GET.get('player_id')
        player = get_object_or_404(Player, id=player_id)
        return Response(
            data=self.get_serializer(player.answer_sheet).data,
            status=status.HTTP_200_OK,
        )
