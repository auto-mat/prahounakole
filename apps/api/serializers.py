from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers

from webmap.models import Photo, Poi


class PhotoItemSerializer(serializers.ModelSerializer):
    img_thumb_80x80 = serializers.SerializerMethodField()
    img_thumb_200x200 = serializers.SerializerMethodField()

    def get_img_thumb_80x80(self, obj):
        options = {"size": (80, 80)}
        thumb_url = get_thumbnailer(obj.photo).get_thumbnail(options).url
        return thumb_url

    def get_img_thumb_200x200(self, obj):
        options = {"size": (200, 200)}
        thumb_url = get_thumbnailer(obj.photo).get_thumbnail(options).url
        return thumb_url

    class Meta:
        model = Photo
        fields = ("img_thumb_80x80", "img_thumb_200x200")


class PoiSerializer(serializers.ModelSerializer):
    photos = PhotoItemSerializer(many=True, read_only=True)
    region = serializers.CharField(read_only=True)
    region_url = serializers.SerializerMethodField()
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

    def get_region_url(self, obj):
        scheme = self.request.scheme
        host = self.request.get_host()
        region = Poi.objects.get(name=obj.region)
        return f"{scheme}://{host}#misto={region.marker.layer.slug}_{region.id}/"

    class Meta:
        model = Poi
        fields = (
            'name', 'desc', 'url', 'last_modification', 'region',
            'region_url', 'photos',
        )
