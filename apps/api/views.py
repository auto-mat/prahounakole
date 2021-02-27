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
        q = """
        SELECT
          webmap_sector.name as town, webmap_poi.id
        FROM webmap_sector INNER JOIN webmap_poi ON ST_Intersects(
          webmap_sector.geom,
          webmap_poi.geom
        ) WHERE webmap_poi.id IN (%s)
        """ % ', '.join([str(i) for i in self.queryset.values_list('id', flat=True)])
        return self.queryset.raw(q)


router = routers.DefaultRouter()
router.register(r'poi-closures', PoiViewSet)
