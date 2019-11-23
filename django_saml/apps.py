from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
from onelogin.saml2.settings import OneLogin_Saml2_Settings


class DjangoSamlConfig(AppConfig):
    """App configuration for django_saml."""

    name = 'django_saml'

    def ready(self):
        """Pull settings from Django and defaults and configure SAML settings for use."""
        from . import settings as defaults
        from django.conf import settings
        from django.core.cache import cache
        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))

        settings.SAML_SETTINGS = {
            'strict': settings.SAML_STRICT,
            'debug': settings.SAML_DEBUG
        }

        if settings.SAML_SP is None:
            raise ImproperlyConfigured("SAML_SP must be defined")

        settings.SAML_SETTINGS['sp'] = settings.SAML_SP

        if settings.SAML_IDP is None and settings.SAML_IDP_URL is None and settings.SAML_IDP_FILE is None:
            raise ImproperlyConfigured("One must be defined: SAML_IDP, SAML_IDP_URL, SAML_IDP_FILE")

        if settings.SAML_IDP is not None:
            settings.SAML_SETTINGS['idp'] = settings.SAML_IDP
        elif settings.SAML_IDP_URL is not None:
            idp_data = cache.get('SAML_IDP_INFO', None)
            if idp_data is None:
                idp_data = OneLogin_Saml2_IdPMetadataParser.parse_remote(settings.SAML_IDP_URL)
                cache.set('SAML_IDP_INFO', idp_data, settings.SAML_IDP_METADATA_TIMEOUT)
            settings.SAML_SETTINGS['idp'] = idp_data['idp']
        elif settings.SAML_IDP_FILE is not None:
            f = open(settings.SAML_IDP_FILE, 'r')
            idp_data = OneLogin_Saml2_IdPMetadataParser.parse(f.read())
            f.close()
            settings.SAML_SETTINGS['idp'] = idp_data['idp']

        settings.SAML_SETTINGS['security'] = settings.SAML_SECURITY
        if settings.SAML_CONTACT is not None:
            settings.SAML_SETTINGS['contactPerson'] = settings.SAML_CONTACT
        if settings.SAML_ORGANIZATION is not None:
            settings.SAML_SETTINGS['organization'] = settings.SAML_ORGANIZATION

        settings.ONELOGIN_SAML_SETTINGS = OneLogin_Saml2_Settings(settings.SAML_SETTINGS, settings.SAML_BASE_DIRECTORY)
