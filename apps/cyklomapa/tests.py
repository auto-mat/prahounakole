# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
#
# Copyright (C) 2015 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import comments_moderation

import cyklomapa

from django.conf import settings
from django.contrib import auth, sites
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, RequestFactory, TestCase
from django.test.runner import DiscoverRunner
from django.test.utils import override_settings

from django_admin_smoke_tests import tests

import feedback

from fluent_comments import compat as comments_compat

from freezegun import freeze_time

import httpproxy

import webmap
from webmap import views as webmap_views


def print_response(response):
    with open("response.html", "w") as f:  # pragma: no cover
        f.write(response.content.decode())  # pragma: no cover


class CyklomapaTestSuiteRunner(DiscoverRunner):
    class InvalidStringError(str):
        def __mod__(self, other):
            raise Exception("empty string")  # pragma: no cover
            return "!!!!!empty string!!!!!"  # pragma: no cover

    def __init__(self, *args, **kwargs):
        settings.TEMPLATES[0]['OPTIONS']['string_if_invalid'] = self.InvalidStringError("%s")
        super().__init__(*args, **kwargs)


class AdminFilterTests(TestCase):
    fixtures = ["webmap", "cyklomapa"]

    def setUp(self):
                # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST='testing-sector.testserver')
        self.user = User.objects.create_superuser(
            username='admin',
            email='test_user@test_user.com',
            password='admin',
        )
        self.user.save()

    @override_settings(
        FORCE_SUBDOMAIN="testing-sector"
    )
    def run(self, *args, **kwargs):
        super(AdminFilterTests, self).run(*args, **kwargs)

    def test_admin_views(self):
        """
        test if the admin pages load
        """
        self.assertTrue(self.client.login(username='admin', password='admin'))
        response = self.client.get(reverse("admin:webmap_poi_changelist"))
        self.assertEqual(response.status_code, 200)

    @freeze_time("2016-01-04 17:10:00")
    def test_comment_post(self):
        content_type = "webmap.poi"
        object_pk = "205"
        timestamp = "1451927336"
        security_hash = comments_compat.CommentForm.generate_security_hash(None, content_type, object_pk, timestamp)
        post_data = {
            "content_type": content_type,
            "object_pk": object_pk,
            "name": "Testing name",
            "email": "test@email.com",
            "comment": "Testing comment",
            "timestamp": timestamp,
            "security_hash": security_hash,
        }
        response = self.client.post(reverse("comments-post-comment-ajax"), post_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200, response.content.decode("utf-8"))
        self.assertContains(response, '<div class=\\"comment-text\\"><p>Testing comment</p></div>')
        self.assertContains(response, 'Testing name\\n              <span class=\\"comment-date\\">poslal Led. 4, 2016, 5:10 odp.</span>')

    @freeze_time("2016-01-04 17:10:00")
    def test_comment_post_blocked(self):
        comments_moderation.admin.EmailFilter.objects.create(email="test@email.com", active=True)
        content_type = "webmap.poi"
        object_pk = "205"
        timestamp = "1451927336"
        security_hash = comments_compat.CommentForm.generate_security_hash(None, content_type, object_pk, timestamp)
        post_data = {
            "content_type": content_type,
            "object_pk": object_pk,
            "name": "Testing name",
            "email": "test@email.com",
            "comment": "Testing comment",
            "timestamp": timestamp,
            "security_hash": security_hash,
        }
        response = self.client.post(reverse("comments-post-comment-ajax"), post_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200, response.content.decode("utf-8"))
        self.assertContains(response, '<div class=\\"comment-text\\"><p>Testing comment</p></div>')
        self.assertContains(response, 'Testing name\\n              <span class=\\"comment-date\\">poslal Led. 4, 2016, 5:10 odp.</span>')
        self.assertContains(response, '<span class=\\"comment-moderated-flag\\">(moderov\\u00e1n)</span>')


class SitemapTest(TestCase):
    fixtures = ["webmap", "cyklomapa"]

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST="testing-sector.testserver")

    def test_sitemap(self):
        address = reverse("django.contrib.sitemaps.views.sitemap")
        response = self.client.get(address)
        self.assertContains(response, '<loc>http://example.com/misto/1/#misto=l_1</loc>', html=True)


class UnloggedViewTest(TestCase):
    fixtures = ["webmap", "cyklomapa"]

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST="testing-sector.testserver")

    def test_popup(self):
        address = reverse("popup_view", args=(1, ))
        response = self.client.get(address)
        self.assertContains(
            response,
            '<div class="col-md-2 col-md-offset-6 col-sm-3 col-sm-offset-0 centred">'
            '  <a href="#misto=l_1" class="sprite btn link" title="Odkaz na místo"></a>'
            '</div>',
            html=True,
        )


class ViewTest(TestCase):
    fixtures = ["webmap", "cyklomapa"]

    def setUp(self):
                # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST="testing-sector.testserver")
        self.user = User.objects.create_superuser(
            username='admin',
            email='test_user@test_user.com',
            password='admin',
        )
        self.user.save()
        try:
            self.client.force_login(user=self.user)
        except AttributeError:  # Django<=1.8
            self.client.login(username='admin', password='admin')

    def test_uzavirky_view(self):
        address = reverse("uzavirky_view")
        response = self.client.get(address)
        self.assertContains(response, '<a href="http://mapa.prahounakole.cz/misto/1" target="_top" title="Description">Testing poi</a>', html=True)

    def test_uzavirky_feed(self):
        address = reverse("uzavirky_feed")
        response = self.client.get(address)
        self.assertContains(response, '<title>Testing poi</title><link>http://example.com#misto=l_1/</link>')

    def test_novinky_feed(self):
        address = reverse("novinky_feed")
        response = self.client.get(address)
        self.assertContains(response, '<title>Testing poi</title><link>http://example.com#misto=l_1/</link>')

    def test_panel_mapa_view(self):
        address = reverse("panel_mapa_view")
        response = self.client.get(address)
        self.assertContains(response, '<div> Lorem ipsum </div>', html=True)

    def test_panel_hledani_view(self):
        address = reverse("panel_hledani_view")
        response = self.client.get(address)
        self.assertContains(response, '<div id="jpPlanMessage">Čekání na server</div>', html=True)

    def test_appcache_view(self):
        address = reverse("appcache_view")
        response = self.client.get(address)
        self.assertContains(response, '/kml/l/')

    def test_kml_view(self):
        address = reverse("kml_view", args=("l",))
        response = self.client.get(address)
        self.assertContains(response, '<ikona>http://example.com/media/DSC00002.JPG</ikona>', html=True)

    def test_search_view(self):
        address = reverse(webmap_views.search_view, args=("poi",))
        response = self.client.get(address)
        self.assertContains(response, '<name>Testing poi</name>', html=True)

    def test_metro_view(self):
        address = reverse("metro_view")
        response = self.client.get(address)
        self.assertContains(response, '<b>Testing poi 1</b>', html=True)

    def test_popup_list_view(self):
        address = reverse("popup-list")
        response = self.client.get(address)
        self.assertContains(response, '<a href="http://www.test.cz">Místo 1</a>', html=True)

    def test_panel_informace_view(self):
        address = reverse("panel_informace_view")
        response = self.client.get(address)
        self.assertContains(
            response,
            '<p class="desc_vlastnosti">'
            '<img src="/media/DSC00002.JPG" alt="Testing legend item 1"> &nbsp; Testing legend item 1<br/>'
            '</p>',
            html=True,
        )

    def test_znacky_view(self):
        address = reverse("znacky_view")
        response = self.client.get(address)
        self.assertContains(response, '<dt><a name="tli"></a> <b>Testing legend item</b></dt>', html=True)
        self.assertContains(response, '<dd>Legend item description</dd>', html=True)
        self.assertContains(
            response,
            '<dt><a name="tli1"></a><img src="/media/DSC00002.JPG" alt="Testing legend item 1"> <b>Testing legend item 1</b></dt>',
            html=True,
        )
        self.assertContains(response, '<dt><a name="vyluka_akt"></a><img src="/media/DSC00002.JPG" alt="Testing marker"/> <b>Testing marker</b></dt>', html=True)
        self.assertContains(response, '<dd>Marker description</dd>', html=True)

    def test_mapa_view(self):
        address = reverse("mapa_view")
        response = self.client.get(address)
        self.assertContains(response, 'mapconfig[\'address_search_area\'] = "14.288920739775005,49.99501600356955,14.656276086402867,50.16553949570296";')
        self.assertContains(response, 'mapconfig[\'vrstvy\'].push(["Testing layer", "/kml/l/", enabled, "l"]);')
        self.assertContains(response, '<a href="javascript:void(0)" data-dismiss="modal"><img src="/media/DSC00002.JPG" class=""/>Preset name</a>', html=True)

    def test_mapa_view_nonexistent_misto(self):
        address = reverse("mapa_view", args=(123, ))
        response = self.client.get(address)
        self.assertContains(response, 'mapconfig[\'address_search_area\'] = "14.288920739775005,49.99501600356955,14.656276086402867,50.16553949570296";')
        self.assertNotContains(response, 'mapconfig[\'center_feature\']')

    def test_mapa_view_misto(self):
        address = reverse("mapa_view", args=(1, ))
        response = self.client.get(address)
        self.assertContains(response, 'mapconfig[\'address_search_area\'] = "14.288920739775005,49.99501600356955,14.656276086402867,50.16553949570296";')
        self.assertContains(response, 'mapconfig[\'center_feature\'] = 1;')
        self.assertContains(response, 'enabled = "False";\n            \n            mapconfig[\'vrstvy\'].push(["Disabled layer", "/kml/d/", enabled, "d"]);')
        self.assertContains(response, '<a href="javascript:void(0)" data-dismiss="modal"><img src="/media/DSC00002.JPG" class=""/>Preset name</a>', html=True)

    def test_mapa_view_misto_enabled_layer(self):
        address = reverse("mapa_view", args=(2, ))
        response = self.client.get(address)
        self.assertContains(response, 'mapconfig[\'address_search_area\'] = "14.288920739775005,49.99501600356955,14.656276086402867,50.16553949570296";')
        self.assertContains(response, 'mapconfig[\'center_feature\'] = 2;')
        self.assertContains(response, 'enabled = "True";\n            \n            mapconfig[\'vrstvy\'].push(["Disabled layer", "/kml/d/", enabled, "d"]);')
        self.assertContains(response, '<a href="javascript:void(0)" data-dismiss="modal"><img src="/media/DSC00002.JPG" class=""/>Preset name</a>', html=True)

    def test_popup(self):
        address = reverse("popup_view", args=(1, ))
        response = self.client.get(address)
        self.assertContains(
            response,
            '<a href="http://maps.google.com/?q=Testing%20poi@50.08740475519474,14.422134381874203&amp;z=18&amp;t=h"'
            ' target="pnk_gmap" title="Zobrazit v Google Maps" class="sprite btn gmap"></a>',
            html=True,
        )
        self.assertContains(
            response,
            '<p>Description</p>',
            html=True,
        )
        self.assertContains(
            response,
            '<a href="%s" class="btn edit" title="Upravit">&#9874;</a>' % reverse("admin:webmap_poi_change", args=(1,)),
            html=True,
        )
        self.assertContains(
            response,
            '<a href="/media/DSC00002.JPG" title="Testing photo" data-lightbox="poi-image" data-title="Testing photo">'
            '<img src="/media/DSC00002.JPG.300x0_q85.jpg" title="Testing photo" width="300" height="225" class="foto_thumb"/></a>',
            html=True,
        )
        self.assertContains(
            response,
            '<h4>Testing user<span class="comment-date">poslal Lis. 12, 2015, 6:53 odp.</span></h4>',
            html=True,
        )

    def test_popup_poi_without_desc(self):
        address = reverse("popup_view", args=(205, ))
        response = self.client.get(address)
        self.assertContains(
            response,
            '<p>Metro A</p>',
            html=True,
        )


@override_settings(
    FORCE_SUBDOMAIN="testing-sector"
)
class AdminTest(tests.AdminSiteSmokeTest):
    def get_request(self, params={}):
        request = super().get_request(params)
        request.subdomain = "testing-sector"
        return request

    def post_request(self, params={}):
        request = super().post_request(params)
        request.subdomain = "testing-sector"
        return request

    fixtures = ["webmap", "cyklomapa"]
    exclude_apps = ['constance', 'fluent_comments']


class MestoAdminTest(AdminTest):
    exclude_modeladmins = [
        auth.admin.UserAdmin,
        auth.admin.GroupAdmin,
        comments_moderation.admin.BlacklistAdmin,
        cyklomapa.admin.MarkerZnackaAdmin,
        cyklomapa.admin.MestoSectorAdmin,
        cyklomapa.admin.UserAdmin,
        feedback.admin.FeedbackAdmin,
        httpproxy.admin.RequestAdmin,
        httpproxy.admin.ResponseAdmin,
        sites.admin.SiteAdmin,
        webmap.admin.BaseLayerAdmin,
        webmap.admin.LegendAdmin,
        webmap.admin.LicenseAdmin,
        webmap.admin.MapPresetAdmin,
        webmap.admin.OverlayLayerAdmin,
        webmap.admin.PhotoAdmin,
        webmap.admin.PropertyAdmin,
        webmap.admin.StatusAdmin,
    ]

    def setUp(self):
        super().setUp()
        self.superuser = User.objects.get(pk=1)
