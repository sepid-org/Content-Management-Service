from rest_framework import serializers

from apps.file_storage.models import File


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ['id', 'file']
        read_only_fields = ['id']
