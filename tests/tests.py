import base64
import logging
import os
import zlib
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs, urlencode, quote

from django.test import TestCase, override_settings
from django.urls import reverse
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from sample.models import TestUser


data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')


def _file_contents(path):
    f = open(path, 'r')
    contents = f.read()
    f.close()
    return contents


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
        self.assertEqual(query['RelayState'][0], 'http://127.0.0.1/logged-out')


class TestSLS(TestCase):
    """Tests for the saml_sls view."""

    def setUp(self):
        """Initialize common resources."""
        self.user = TestUser.objects.create(username='abc1234')

    def test_sls(self):
        """Test standard logout."""
        self.client.force_login(self.user)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)
        xml = _file_contents(os.path.join(data_directory, 'logout_response.xml'))
        message = OneLogin_Saml2_Utils.deflate_and_base64_encode(xml)
        url = reverse('django_saml:sls') + '?SAMLResponse=' + quote(message)
        response = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/logged-out')
        self.assertIsNone(self.client.session.get('_auth_user_id'))

    def test_sls_invalid_decode(self):
        """Test sending garbage."""
        self.client.force_login(self.user)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)
        url = reverse('django_saml:sls') + '?SAMLResponse=adasdasdasdasdasdasd'
        response = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Invalid request - Unable to decode response")

    def test_sls_invalid_saml(self):
        """Test catching SAML exceptions."""
        # Purely so the exception logging doesn't get printed to the test console
        logging.disable(logging.CRITICAL)
        logging.disable(logging.ERROR)
        self.client.force_login(self.user)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)
        xml = _file_contents(os.path.join(data_directory, 'logout_response.xml'))
        xml = xml.replace('http://127.0.0.1/saml/sls', 'example.com')
        message = OneLogin_Saml2_Utils.deflate_and_base64_encode(xml)
        url = reverse('django_saml:sls') + '?SAMLResponse=' + quote(message)
        response = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Invalid request')
        # Put logging back the way we found it
        logging.disable(logging.NOTSET)

    def test_sls_post(self):
        """Test invalid methods."""
        response = self.client.post(reverse('django_saml:sls'))
        self.assertEqual(response.status_code, 405)
        response = self.client.put(reverse('django_saml:sls'))
        self.assertEqual(response.status_code, 405)
        response = self.client.patch(reverse('django_saml:sls'))
        self.assertEqual(response.status_code, 405)

    @patch.object(OneLogin_Saml2_Auth, 'process_slo')
    def test_unknown_exception(self, mock):
        """Test that unknown exceptions are handled gracefully."""
        logging.disable(logging.CRITICAL)
        logging.disable(logging.ERROR)
        mock.side_effect = Exception('Test exception')
        xml = _file_contents(os.path.join(data_directory, 'logout_response.xml'))
        message = OneLogin_Saml2_Utils.deflate_and_base64_encode(xml)
        url = reverse('django_saml:sls') + '?SAMLResponse=' + quote(message)
        response = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Invalid request')
        logging.disable(logging.NOTSET)


class TestACS(TestCase):
    """Test saml_acs view."""

    def test_acs(self):
        """Test a standard login response."""
        xml = _file_contents(os.path.join(data_directory, 'login_response.xml'))
        message = 'SAMLResponse=' + quote(base64.b64encode(xml.encode()))
        response = self.client.post(reverse('django_saml:acs'), data=message, HTTP_HOST='127.0.0.1', content_type='application/x-www-form-urlencoded')
        self.assertRedirects(response, '/')
        user = TestUser.objects.get()
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    @override_settings(SAML_CREATE_USER=False)
    def test_acs_no_user(self):
        """Test instance where user doesn't exist."""
        xml = _file_contents(os.path.join(data_directory, 'login_response.xml'))
        message = 'SAMLResponse=' + quote(base64.b64encode(xml.encode()))
        response = self.client.post(reverse('django_saml:acs'), data=message, HTTP_HOST='127.0.0.1',
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(TestUser.objects.count(), 0)

    def test_redirect(self):
        xml = _file_contents(os.path.join(data_directory, 'login_response.xml'))
        message = 'SAMLResponse={}&RelayState={}'.format(quote(base64.b64encode(xml.encode())), 'http://127.0.0.1/test')
        response = self.client.post(reverse('django_saml:acs'), data=message, HTTP_HOST='127.0.0.1',
                                    content_type='application/x-www-form-urlencoded')
        self.assertRedirects(response, 'http://127.0.0.1/test', fetch_redirect_response=False)

    def test_acs_get(self):
        """Test invalid methods."""
        response = self.client.get(reverse('django_saml:acs'))
        self.assertEqual(response.status_code, 405)
        response = self.client.put(reverse('django_saml:acs'))
        self.assertEqual(response.status_code, 405)
        response = self.client.patch(reverse('django_saml:acs'))
        self.assertEqual(response.status_code, 405)

    def test_exceptions(self):
        """Test handling exceptions."""
        logging.disable(logging.CRITICAL)
        logging.disable(logging.ERROR)
        message = 'SAMLResponse=asdasdasdasd'
        response = self.client.post(reverse('django_saml:acs'), data=message, HTTP_HOST='127.0.0.1',
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 400)
        logging.disable(logging.NOTSET)

    def test_saml_errors(self):
        """Test handling errors in SAML verification."""
        logging.disable(logging.CRITICAL)
        logging.disable(logging.ERROR)
        xml = _file_contents(os.path.join(data_directory, 'login_response.xml'))
        xml = xml.replace('X509Certificate>MIICQDCCAamgAwIBAgI', 'X509Certificate>MIICQDCCAamgAwZZZZ')
        message = 'SAMLResponse={}&RelayState={}'.format(quote(base64.b64encode(xml.encode())), 'http://127.0.0.1/test')
        response = self.client.post(reverse('django_saml:acs'), data=message, HTTP_HOST='127.0.0.1',
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 400)
        logging.disable(logging.NOTSET)
