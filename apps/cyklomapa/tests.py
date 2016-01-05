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
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from webmap import views as webmap_views
from django_admin_smoke_tests import tests
from freezegun import freeze_time


class AdminFilterTests(TestCase):
    fixtures = ["webmap", "cyklomapa"]

    def setUp(self):
                # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST='testserver')
        self.user = User.objects.create_superuser(
            username='admin', email='test_user@test_user.com', password='admin')
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


    @freeze_time("2016-01-04 18:00:00")
    def test_comment_post(self):
        post_data = {
            "content_type": "webmap.poi",
            "object_pk": 205,
            "name": "Testing name",
            "email": "test@email.com",
            "comment": "Testing comment",
            "timestamp": "1451927336",
            "security_hash": "88b496a272609f9be0fcd0992e6f1dfecc0344d3",
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
            ("popup_view", (1, )),
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


@override_settings(
    FORCE_SUBDOMAIN="testing-sector"
)
class AdminTest(tests.AdminSiteSmokeTest):
    def get_request(self):
        request = super().get_request()
        request.subdomain = "testing-sector"
        return request

    fixtures = ["webmap", "cyklomapa"]
    exclude_apps = ['constance', 'fluent_comments']
