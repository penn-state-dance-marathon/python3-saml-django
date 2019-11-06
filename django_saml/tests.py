from unittest.mock import patch

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
