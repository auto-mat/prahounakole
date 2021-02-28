from django.contrib.gis.db.models.functions import Intersection
from django.db.models import (
    F, OuterRef, Subquery,
)

from oauth2_provider.contrib.rest_framework import (
    IsAuthenticatedOrTokenHasScope, OAuth2Authentication,
)
from rest_framework import routers, viewsets
from rest_framework.authentication import SessionAuthentication

from cyklomapa.models import Poi

from .serializers import PoiSerializer

# Create your views here.


class PoiViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [SessionAuthentication, OAuth2Authentication]
    permission_classes = [IsAuthenticatedOrTokenHasScope]
    required_scopes = ['can_read_poi_closures']

    queryset = Poi.objects.filter(
        status__show=True, marker__slug='vyluka_akt',
    )
    serializer_class = PoiSerializer

    def get_queryset(self):
        return self.queryset.raw(
            """
            SELECT
                cyklomapa_czechiaregions.nazev as region, webmap_poi.id
            FROM cyklomapa_czechiaregions INNER JOIN webmap_poi ON ST_Intersects(
                cyklomapa_czechiaregions.geom,
                webmap_poi.geom
            ) WHERE webmap_poi.id IN %s
            """, [tuple(self.queryset.values_list('id', flat=True))]
        )


router = routers.DefaultRouter()
router.register(r'poi-closures', PoiViewSet)
