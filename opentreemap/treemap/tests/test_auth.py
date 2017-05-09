# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import mock
from django.test.utils import override_settings

from treemap.tests import (RequestTestCase, make_instance,
                           make_user)


class LogoutTests(RequestTestCase):

    @override_settings(LANDING_PAGE_DEFAULT_INSTANCE='warszawa')
    def test_logout(self):
        make_instance(name='warszawa', is_public=True, url_name='warszawa')
        res = self.client.get('/accounts/logout/')
        self.assertRedirects(res, '/warszawa/map/')


class LoginTests(RequestTestCase):

    def setUp(self):
        self.client.get('/accounts/logout/')
        self.username = 'testo'
        self.password = '1337'
        self.instance = make_instance()
        self.user = make_user(username=self.username, password=self.password)

    def test_password_correct(self):
        res = self.client.post('/accounts/login/',
                               {'username': self.username,
                                'password': self.password})
        self.assertRedirects(res, '/', target_status_code=301)

    def test_successful_login_redirect(self):
        self.client.post('/accounts/login/',
                         {'username': self.username,
                          'password': self.password})
        res = self.client.get('/accounts/profile/')
        expected_url = '/users/%s/' % self.username
        self.assertRedirects(res, expected_url)

    def test_password_incorrect(self):
        res = self.client.post('/accounts/login/',
                               {'username': self.username,
                                'password': 'WRONG!'})
        # If your login is invalid, the POST returns 200 and the user
        # stays on the login form page.
        self.assertOk(res)

    # This yields 404 for some reason.
    # def test_profile_redirect_when_no_current_user(self):
    #     res = self.client.get('/accounts/profile/')
    #     self.assertRedirects(res, '/accounts/profile/login/')

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='1', SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='2')
    @mock.patch('social_core.backends.oauth.OAuthAuth.state_token', return_value='zz')
    def test_google_auth_redirect(self, *args):
        response = self.client.get('/oauth/login/google-oauth2/')
        self.assertRedirects(
            response,
            'https://accounts.google.com/o/oauth2/auth?scope=openid+email+profile&state=zz&'
            'redirect_uri=http://testserver/oauth/complete/google-oauth2/&response_type=code&'
            'client_id=1',
            status_code=302,
            target_status_code=404)


class PublicInstanceTests(RequestTestCase):

    def setUp(self):
        self.instance = make_instance()

        self.user = make_user(username='user')

        self.instance_user = make_user(self.instance, 'instance_user')
        self.client.get('/accounts/logout/')

    def make_instance_private(self):
        self.instance.is_public = False
        self.instance.save()

    def make_instance_public(self):
        self.instance.is_public = True
        self.instance.save()

    def test_public_instance_is_accessible_without_login(self):
        self.make_instance_public()
        res = self.client.get('/%s/map/' % self.instance.url_name)
        self.assertOk(res)

    def test_private_instance_is_not_accessible_without_login(self):
        self.make_instance_private()
        res = self.client.get('/%s/map/' % self.instance.url_name)
        self.assertRedirects(res,
                             'http://testserver/accounts/login?next=/%s/map/'
                             % self.instance.url_name)

    def test_private_instance_is_not_accessible_by_non_instance_user(self):
        self.make_instance_private()
        self.client.post('/accounts/login/',
                         {'username': 'user',
                          'password': 'password'})
        res = self.client.get('/%s/map/' % self.instance.url_name)
        self.assertRedirects(res, 'http://testserver/not-available')

    def test_private_instance_accessible_by_instance_user(self):
        self.make_instance_private()
        self.client.post('/accounts/login/',
                         {'username': 'instance_user',
                          'password': 'password'})
        res = self.client.get('/%s/map/' % self.instance.url_name)
        self.assertOk(res)
