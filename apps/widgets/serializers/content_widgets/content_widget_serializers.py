from rest_framework import serializers
from apps.widgets.serializers.widget_serializer import WidgetSerializer

from apps.fsm.models import DetailBoxWidget, Paper, Iframe, Video, Image, TextWidget, Widget, Aparat, Audio


class ContentWidgetSerializer(WidgetSerializer):
    class Meta(WidgetSerializer.Meta):
        fields = WidgetSerializer.Meta.fields + []
        read_only_fields = WidgetSerializer.Meta.read_only_fields + []


class IframeSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.Iframe
        return super(IframeSerializer, self).create(validated_data)

    class Meta(ContentWidgetSerializer.Meta):
        model = Iframe
        fields = ContentWidgetSerializer.Meta.fields + ['link']


class VideoSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.Video
        return super(VideoSerializer, self).create(validated_data)

    class Meta(ContentWidgetSerializer.Meta):
        model = Video
        fields = ContentWidgetSerializer.Meta.fields + ['link']


class AudioSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.Audio
        return super(AudioSerializer, self).create(validated_data)

    class Meta(ContentWidgetSerializer.Meta):
        model = Audio
        fields = ContentWidgetSerializer.Meta.fields + ['link']


class AparatSerializer(ContentWidgetSerializer):
    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.Aparat
        return super(AparatSerializer, self).create(validated_data)

    class Meta(ContentWidgetSerializer.Meta):
        model = Aparat
        fields = ContentWidgetSerializer.Meta.fields + ['video_id']


class ImageSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.Image
        return super(ImageSerializer, self).create(validated_data)

    class Meta(ContentWidgetSerializer.Meta):
        model = Image
        fields = ContentWidgetSerializer.Meta.fields + ['link']


class TextWidgetSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.TextWidget
        return super(TextWidgetSerializer, self).create(validated_data)

    class Meta(ContentWidgetSerializer.Meta):
        model = TextWidget
        fields = ContentWidgetSerializer.Meta.fields + ['text']


class DetailBoxWidgetSerializer(ContentWidgetSerializer):
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        from apps.fsm.serializers.papers.paper_serializer import PaperMinimalSerializer
        return PaperMinimalSerializer(obj.details).data

    def create(self, validated_data):
        user = self.context.get('request').user
        details_instance = Paper.objects.create(**{
            'paper_type': Paper.PaperType.General,
            'creator': user,
        })
        return super(DetailBoxWidgetSerializer, self).create({
            'widget_type': Widget.WidgetTypes.DetailBoxWidget,
            'details': details_instance,
            **validated_data,
        })

    class Meta(ContentWidgetSerializer.Meta):
        model = DetailBoxWidget
        fields = ContentWidgetSerializer.Meta.fields + ['title', 'details']
        read_only_fields = ContentWidgetSerializer.Meta.read_only_fields + \
            ['details']
