from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets

from apps.fsm.models import Paper
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer


class PaperViewSet(viewsets.ModelViewSet):
    serializer_class = PaperSerializer
    queryset = Paper.objects.all()
    my_tags = ['paper']

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Allow anonymous access to public papers
        if not instance.is_private:
            return Response(serializer.data)

        # Check IsAuthenticated permission for private objects
        if not IsAuthenticated().has_permission(request, self):
            self.permission_denied(
                request,
                message=getattr(IsAuthenticated, 'message', None),
                code=getattr(IsAuthenticated, 'code', None)
            )
        return Response(serializer.data)
