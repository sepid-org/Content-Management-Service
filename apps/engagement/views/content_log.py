from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.engagement.serializers.content_log import ContentLogSerializer


class ContentLogView(APIView):
    def post(self, request, format=None):
        request.data['user_id'] = request.user.id
        serializer = ContentLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
