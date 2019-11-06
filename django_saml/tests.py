from unittest.mock import patch
from urllib.parse import urlparse, parse_qs

from django.test import TestCase
from django.urls import reverse
from onelogin.saml2.settings import OneLogin_Saml2_Settings


class TestMetadata(TestCase):
    """Tests for the metadata view."""

    def test_response(self):
        """Test metadata is returned."""
        response = self.client.get(reverse('django_saml:metadata'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertContains(response, 'entityID="http://127.0.0.1:8000/saml/metadata/"')
        self.assertContains(response, 'AuthnRequestsSigned="true"')

    @patch.object(OneLogin_Saml2_Settings, 'validate_metadata')
    def test_errors(self, mock):
        """Test errors in metadata are displayed."""
        mock.return_value = ['Test Error']
        response = self.client.get(reverse('django_saml:metadata'))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content.decode(), 'Test Error')


class TestLogin(TestCase):
    """Test for the login view."""

    def test_login(self):
        """Test redirect to IdP as expected."""
        response = self.client.get(reverse('django_saml:login'), HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response['Location'])
        self.assertEqual(parsed.netloc, 'app.onelogin.com')
        self.assertEqual(parsed.path, '/trust/saml2/http-post/sso/')
        query = parse_qs(parsed.query)
        self.assertEqual(query['RelayState'][0], 'http://127.0.0.1/')

    def test_login_next(self):
        """Test redirect to IdP as expected with next parameter."""
        response = self.client.get(reverse('django_saml:login') + "?next=/test", HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response['Location'])
        self.assertEqual(parsed.netloc, 'app.onelogin.com')
        self.assertEqual(parsed.path, '/trust/saml2/http-post/sso/')
        query = parse_qs(parsed.query)
        self.assertEqual(query['RelayState'][0], 'http://127.0.0.1/test')


class TestLogout(TestCase):
    """Tests for the logout view."""

    def test_logout(self):
        """Test redirect to the IdP for logout."""
        response = self.client.get(reverse('django_saml:logout'), HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response['Location'])
        self.assertEqual(parsed.netloc, 'app.onelogin.com')
        self.assertEqual(parsed.path, '/trust/saml2/http-redirect/slo/')
        query = parse_qs(parsed.query)
        self.assertEqual(query['RelayState'][0], '/logged-out')
