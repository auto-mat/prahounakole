from rest_framework import serializers

from webmap.models import Photo, Poi


class PhotoItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = ('photo',)


class PoiSerializer(serializers.ModelSerializer):
    photos = PhotoItemSerializer(many=True, read_only=True)
    town = serializers.CharField(read_only=True)

    class Meta:
        model = Poi
        fields = (
            'address', 'created_at', 'desc', 'last_modification',
            'name', 'photos', 'town', 'url',
        )
