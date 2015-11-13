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
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings


class AdminFilterTests(TestCase):
    fixtures=["webmap","cyklomapa"]
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

    def test_mapa_view(self):
        """
        test if main page loads
        """
        response = self.client.get(reverse("mapa_view"))
        self.assertEqual(response.status_code, 200)

    def test_popup_view(self):
        """
        test if other views load
        """
        response = self.client.get(reverse("popup_view", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_complementary_views(self):
        """
        test if other views load
        """
        response = self.client.get(reverse("uzavirky_view"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("uzavirky_view"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("znacky_view"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("panel_mapa_view"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("panel_informace_view"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("panel_hledani_view"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("appcache_view"))
        self.assertEqual(response.status_code, 200)
