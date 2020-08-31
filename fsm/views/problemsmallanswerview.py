from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes

from fsm.models import *
from rest_framework import permissions
from fsm.views import permissions as customPermissions
from fsm.serializers import ProblemSmallAnswerSerializer

import sys

class SmallView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission, ]

    queryset = ProblemSmallAnswer.objects.all()
    serializer_class = ProblemSmallAnswerSerializer