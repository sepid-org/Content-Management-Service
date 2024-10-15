from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Max

from apps.fsm.models import State, Paper
from apps.fsm.models.fsm import StatePaper
from apps.fsm.permissions import IsStateModifier
from apps.fsm.serializers.fsm_serializers import EdgeSerializer
from apps.fsm.serializers.papers.state_serializer import StateSerializer
from apps.fsm.views.object_view import ObjectViewSet


class StateViewSet(ObjectViewSet):
    serializer_class = StateSerializer
    queryset = State.objects.all()
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
        if self.action in ['create', 'retrieve', 'list', 'outward_edges', 'inward_edges', 'add_paper', 'remove_paper']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsStateModifier]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def outward_edges(self, request, pk=None):
        state = self.get_object()
        outward_edges = state.outward_edges.all()
        serializer = EdgeSerializer(outward_edges, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def inward_edges(self, request, pk=None):
        state = self.get_object()
        inward_edges = state.inward_edges.all()
        serializer = EdgeSerializer(inward_edges, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_paper_order(self, request, pk=None):
        state = self.get_object()
        paper_ids = request.data.get('paper_ids', [])
        if not paper_ids:
            return Response({"error": "No paper IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                for index, paper_id in enumerate(paper_ids):
                    state_paper = StatePaper.objects.get(
                        state=state, paper_id=paper_id)
                    state_paper.order = index
                    state_paper.save()
            return Response({"message": "Paper order updated successfully"}, status=status.HTTP_200_OK)
        except StatePaper.DoesNotExist:
            return Response({"error": "One or more paper IDs are invalid for this state"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def add_paper(self, request, pk=None):
        state = self.get_object()
        paper_id = request.data.get('paper_id')

        if not paper_id:
            return Response({"error": "No paper ID provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            paper = Paper.objects.get(id=paper_id)
        except Paper.DoesNotExist:
            return Response({"error": "Invalid paper ID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Get the lowest order number
                max_order = StatePaper.objects.filter(
                    state=state).aggregate(Max('order'))['order__max']
                new_order = max_order + 1 if max_order is not None else 0

                # Create new StatePaper
                StatePaper.objects.create(
                    state=state, paper=paper, order=new_order)

            return Response({"message": "Paper added successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def remove_paper(self, request, pk=None):
        state = self.get_object()
        paper_id = request.data.get('paper_id')

        if not paper_id:
            return Response({"error": "No paper ID provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            state_paper = StatePaper.objects.get(
                state=state, paper_id=paper_id)
            state_paper.delete()

            # Optionally, reorder remaining papers
            remaining_papers = StatePaper.objects.filter(
                state=state).order_by('order')
            for index, sp in enumerate(remaining_papers):
                sp.order = index
                sp.save()

            return Response({"message": "Paper removed successfully"}, status=status.HTTP_200_OK)
        except StatePaper.DoesNotExist:
            return Response({"error": "Paper not found in this state"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
