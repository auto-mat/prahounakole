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

from django.contrib import auth, sites
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, RequestFactory, TestCase
from django.test.utils import override_settings

from django_admin_smoke_tests import tests

import feedback

from fluent_comments import compat as comments_compat

from freezegun import freeze_time

import httpproxy

from project import settings

import webmap
from webmap import views as webmap_views


class AdminFilterTests(TestCase):
    fixtures = ["webmap", "cyklomapa"]

    def setUp(self):
                # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST='testserver')
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

    def verify_views(self, views, status_code_map={}):
        for view in views:
            status_code = status_code_map[view] if view in status_code_map else 200
            if len(view) > 1:
                args = view[1]
            else:
                args = None
            address = reverse(view[0], args=args)
            response = self.client.get(address, HTTP_HOST="testing-campaign.testserver")
            self.assertEqual(response.status_code, status_code, "%s view failed with following content: \n%s" % (view, response.content.decode("utf-8")))

    def test_complementary_views(self):
        """
        test if other views load
        """
        views = [
            ("mapa_view",),
            ("mapa_view", (1, )),
            ("uzavirky_view",),
            ("uzavirky_feed",),
            ("novinky_feed",),
            ("znacky_view",),
            ("panel_mapa_view",),
            ("panel_informace_view",),
            ("panel_hledani_view",),
            ("appcache_view",),
            ("kml_view", ("l",)),
            (webmap_views.search_view, ("asdf",)),
            ("metro_view",),
        ]

        self.verify_views(views)


class ViewTest(TestCase):
    fixtures = ["webmap", "cyklomapa"]

    def setUp(self):
                # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST='testserver')
        self.user = User.objects.create_superuser(
            username='admin',
            email='test_user@test_user.com',
            password='admin',
        )
        self.user.save()
        self.client.force_login(user=self.user)

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
            '<a href="/admin/webmap/poi/1/change/" class="btn edit" title="Upravit">&#9874;</a>',
            html=True,
        )
        self.assertContains(
            response,
            '<a href="%(host)s/media/DSC00002.JPG" title="Testing photo" data-lightbox="poi-image" data-title="Testing photo">'
            '<img src="%(host)s/media/DSC00002.JPG.300x0_q85.jpg" title="Testing photo" width="300" height="225" class="foto_thumb"/></a>' %
            {'host': settings.SITE_URL},
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

    fixtures = ["webmap", "cyklomapa"]
    exclude_apps = ['constance', 'fluent_comments']


class MestoAdminTest(AdminTest):
    exclude_modeladmins = [
        auth.admin.UserAdmin,
        auth.admin.GroupAdmin,
        comments_moderation.admin.BlacklistAdmin,
        cyklomapa.admin.MarkerZnackaAdmin,
        cyklomapa.admin.MestoAdmin,
        cyklomapa.admin.MestoPoiAdmin,
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
