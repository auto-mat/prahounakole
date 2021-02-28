from rest_framework import serializers

from webmap.models import Photo, Poi


class PhotoItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = ('photo',)


class PoiSerializer(serializers.ModelSerializer):
    photos = PhotoItemSerializer(many=True, read_only=True)
    region = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_url(self, obj):
        scheme = self.request.scheme
        host = self.request.get_host()
        return f"{scheme}://{host}#misto={obj.marker.layer.slug}_{obj.id}/"

    class Meta:
        model = Poi
        fields = (
            'name', 'desc', 'url', 'last_modification', 'region',
            'photos',
        )
