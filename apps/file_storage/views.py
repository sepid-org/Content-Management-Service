
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser

from apps.file_storage.models import File
from apps.file_storage.serializers.file_serializer import FileSerializer


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    parser_classes = [MultiPartParser]
    queryset = File.objects.all()
    my_tags = ['file-storage']
    permission_classes = [AllowAny]
