from rest_framework import serializers
from apps.fsm.serializers.widgets.widget_serializer import WidgetSerializer

from apps.fsm.models import DetailBoxWidget, Paper, Iframe, Video, Image, TextWidget, Widget, Aparat, Audio


class ContentWidgetSerializer(WidgetSerializer):
    class Meta:
        fields = ['id', 'name', 'paper', 'widget_type',
                  'creator', 'hints', 'cost', 'reward']
        read_only_fields = ['id', 'creator']


class IframeSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        return super(IframeSerializer, self).create({'widget_type': Widget.WidgetTypes.Iframe, **validated_data})

    class Meta(ContentWidgetSerializer.Meta):
        model = Iframe
        fields = ContentWidgetSerializer.Meta.fields + ['link']


class VideoSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        return super(VideoSerializer, self).create({'widget_type': Widget.WidgetTypes.Video, **validated_data})

    class Meta(ContentWidgetSerializer.Meta):
        model = Video
        fields = ContentWidgetSerializer.Meta.fields + ['link']


class AudioSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        return super(AudioSerializer, self).create({'widget_type': Widget.WidgetTypes.Audio, **validated_data})

    class Meta(ContentWidgetSerializer.Meta):
        model = Audio
        fields = ContentWidgetSerializer.Meta.fields + ['link']


class AparatSerializer(ContentWidgetSerializer):
    def create(self, validated_data):
        return super(AparatSerializer, self).create({'widget_type': Widget.WidgetTypes.Aparat, **validated_data})

    class Meta(ContentWidgetSerializer.Meta):
        model = Aparat
        fields = ContentWidgetSerializer.Meta.fields + ['video_id']


class ImageSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        return super(ImageSerializer, self).create({'widget_type': Widget.WidgetTypes.Image, **validated_data})

    class Meta(ContentWidgetSerializer.Meta):
        model = Image
        fields = ContentWidgetSerializer.Meta.fields + ['link']


class TextWidgetSerializer(ContentWidgetSerializer):

    def create(self, validated_data):
        return super(TextWidgetSerializer, self).create(
            {'widget_type': Widget.WidgetTypes.TextWidget, **validated_data})

    class Meta(ContentWidgetSerializer.Meta):
        model = TextWidget
        fields = ContentWidgetSerializer.Meta.fields + ['text']


class DetailBoxWidgetSerializer(ContentWidgetSerializer):
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        from apps.fsm.serializers.paper_serializers import PaperMinimalSerializer
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
